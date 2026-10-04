# Entity Classification Structure

Register every Entity in `CompanyEntities` for each relevant fiscal year. Add a row to a classification relation only when that Entity belongs to the classification in that fiscal year:

| Classification               | Relation                  | Membership rule        |
| ---------------------------- | ------------------------- | ---------------------- |
| Constituent Entity (CE)      | `ConstituentEntities`     | A matching row exists. |
| Permanent Establishment (PE) | `PermanentEstablishments` | A matching row exists. |
| Investment Entity (IE)       | `InvestmentEntities`      | A matching row exists. |
| Excluded Entity (EE)         | `ExcludedEntities`        | A matching row exists. |
| Flow-through Entity (FTE)    | `FlowThroughEntities`     | A matching row exists. |

Classification rows reference the same `(fiscal_year, entity_id)` in `CompanyEntities`. Absence of a row means the classification indicator is false for that fiscal year; no row with a false membership flag is stored. Classifications are recorded independently where applicable: for example, an Entity that is both a CE and a PE has a row in both relations.

CE, PE, EE, and FTE are separated here, following the existing IE structure. UPE status is stored as `ConstituentEntities.is_upe`.

# CompanyEntities

The complete Entity register, including Entities with no row in any of the classification relations.

## Columns

| Column            | Data type              | Nullable | Source |
| ----------------- | ---------------------- | -------- | ------ |
| fiscal_year       | year                   | false    | Input  |
| entity_id         | positive integer       | false    | Input  |
| is_held_for_sale  | boolean                | false    | Input  |
| is_equity_method  | boolean                | false    | Input  |
| jurisdiction_code | ISO3166-1 alpha-2 code | true     | Input  |

## PK

- fiscal_year
- entity_id

## Constraints

- is_equity_method may be true only when the Entity has no row in ConstituentEntities for the same fiscal year.
- is_equity_method is true when the Entity is reported under the equity method in the relevant consolidated or combined Financial Statements.
- is_held_for_sale is true when the Entity is subject to a held-for-sale presentation in those Financial Statements.

# ConstituentEntities

## Columns

| Column      | Data type        | Nullable | Source |
| ----------- | ---------------- | -------- | ------ |
| fiscal_year | year             | false    | Input  |
| entity_id   | positive integer | false    | Input  |
| is_upe      | boolean          | false    | Input  |

## PK

- fiscal_year
- entity_id

## FK

- `(fiscal_year, entity_id)` references `CompanyEntities(fiscal_year, entity_id)`.

## Constraints

- An Entity is treated as a Constituent Entity if and only if it has a row in this relation for the relevant fiscal year.
- No separate `is_constituent_entity` column is stored; the `ce` indicator is derived from row existence.
- `is_upe` is required for every CE row. The `group-upe` indicator is 1 only when a matching CE row has `is_upe == true`; it is 0 otherwise.

# PermanentEstablishments

## Columns

| Column                           | Data type        | Nullable | Source |
| -------------------------------- | ---------------- | -------- | ------ |
| fiscal_year                      | year             | false    | Input  |
| entity_id                        | positive integer | false    | Input  |
| is_permanent_establishment_dtype | boolean          | false    | Input  |

## PK

- fiscal_year
- entity_id

## FK

- `(fiscal_year, entity_id)` references `CompanyEntities(fiscal_year, entity_id)`.

## Constraints

- An Entity is treated as a PE if and only if it has a row in this relation for the relevant fiscal year.
- No separate `is_permanent_establishment` column is stored; the `pe` indicator is derived from row existence.
- `is_permanent_establishment_dtype` is required for every PE row. An Entity that is not a PE has no row in this relation.
- `is_permanent_establishment_dtype` is true for a PE described in Article 10.3.3(d).

# ExcludedEntities

## Columns

| Column      | Data type        | Nullable | Source |
| ----------- | ---------------- | -------- | ------ |
| fiscal_year | year             | false    | Input  |
| entity_id   | positive integer | false    | Input  |

## PK

- fiscal_year
- entity_id

## FK

- `(fiscal_year, entity_id)` references `CompanyEntities(fiscal_year, entity_id)`.

## Constraints

- An Entity is treated as an Excluded Entity if and only if it has a row in this relation for the relevant fiscal year.
- No separate `is_excluded_entity` column is stored; the `ee` indicator is derived from row existence.
- An Entity must not have rows in both `ExcludedEntities` and `ConstituentEntities` for the same fiscal year.

# FlowThroughEntities

## Columns

| Column      | Data type        | Nullable | Source |
| ----------- | ---------------- | -------- | ------ |
| fiscal_year | year             | false    | Input  |
| entity_id   | positive integer | false    | Input  |

## PK

- fiscal_year
- entity_id

## FK

- `(fiscal_year, entity_id)` references `CompanyEntities(fiscal_year, entity_id)`.

## Constraints

- An Entity is treated as a Flow-through Entity if and only if it has a row in this relation for the relevant fiscal year.
- No separate `is_flow_through_entity` column is stored; the `fte` indicator is derived from row existence.

# InvestmentEntities

## Columns

| Column                         | Data type        | Nullable | Source |
| ------------------------------ | ---------------- | -------- | ------ |
| fiscal_year                    | year             | false    | input  |
| entity_id                      | positive integer | false    | input  |
| is_insurance_investment_entity | boolean          | false    | input  |
| eligible_for_cbcr_safeharbour  | boolean          | false    | input  |

## PK

- fiscal_year
- entity_id

## Constraints

An Entity is treated as an Investment Entity if and only if the Entity has a row in this relation for the relevant fiscal year.

- `(fiscal_year, entity_id)` must reference an existing row in `CompanyEntities`.
- `eligible_for_cbcr_safeharbour` is true only when the IE and its CE owners are located in the same jurisdiction, no Article 7.5 or 7.6 election applies, and their financial amounts are recorded in the same jurisdiction for CbCR purposes.

# JvEntities

## Columns

| Column       | Data type        | Nullable | Source     |
| ------------ | ---------------- | -------- | ---------- |
| fiscal_year  | year             | false    | calculated |
| period_start | date             | false    | calculated |
| period_end   | date             | false    | calculated |
| entity_id    | positive integer | false    | calculated |
| jv_group_id  | positive integer | false    | calculated |
| is_jv        | boolean          | false    | calculated |
| is_jv_sub    | boolean          | false    | calculated |

## PK

- fiscal_year
- period_start
- period_end
- entity_id

## Constraints

- is_jv == true iff jv_group_id == entity_id
- is_jv_sub == true iff jv_group_id != entity_id
- `period_start <= period_end`, and both dates fall within `fiscal_year`.
- Rows for the same Entity must not overlap.

An Entity is treated as a member of a JV Group if and only if the Entity has a row covering the relevant date or calculation period. The relation is recalculated whenever an effective-dated Ownership or Controlling Interest changes.

# MinorityOwnedEntities

## Columns

| Column                  | Data type        | Nullable | Source     |
| ----------------------- | ---------------- | -------- | ---------- |
| fiscal_year             | year             | false    | calculated |
| entity_id               | positive integer | false    | calculated |
| minority_owned_group_id | positive integer | false    | calculated |
| is_mope                 | boolean          | false    | calculated |
| is_mos                  | boolean          | false    | calculated |
| is_single_moce          | boolean          | false    | calculated |

## PK

- fiscal_year
- entity_id

## FK

- `(fiscal_year, entity_id)` references `CompanyEntities(fiscal_year, entity_id)`.
- `(fiscal_year, minority_owned_group_id)` references `CompanyEntities(fiscal_year, entity_id)`.

## Constraints

- Exactly one of `is_mope`, `is_mos`, and `is_single_moce` is true.
- `minority_owned_group_id == entity_id` when `is_mope == true` or `is_single_moce == true`.
- `minority_owned_group_id != entity_id` when `is_mos == true`.
- When `is_mos == true`, the row identified by `(fiscal_year, minority_owned_group_id)` exists in this relation with `is_mope == true`.
- An Entity is treated as a calculation-purpose MOCE if and only if it has a row in this relation for the relevant fiscal year.

# CompaniesTcsh

Entity-level financial data and signed adjustments used by the Transitional CbCR Safe Harbour calculation.

## Columns

| Column                                     | Data type        | Nullable | Source |
| ------------------------------------------ | ---------------- | -------- | ------ |
| fiscal_year                                | year             | false    | input  |
| period_start                               | date             | false    | input  |
| period_end                                 | date             | false    | input  |
| entity_id                                  | positive integer | false    | input  |
| cbcr_revenue                               | money            | false    | input  |
| investment_entity_revenue_adjustment       | money            | false    | input  |
| cbcr_pbt                                   | money            | false    | input  |
| unrealised_net_fair_value_loss             | money            | false    | input  |
| hybrid_arbitrage_pbt_adjustment            | money            | false    | input  |
| investment_entity_pbt_adjustment           | money            | false    | input  |
| other_required_pbt_adjustments             | money            | false    | input  |
| income_tax_expense                         | money            | false    | input  |
| non_covered_tax_adjustment                 | money            | false    | input  |
| uncertain_tax_position_adjustment          | money            | false    | input  |
| hybrid_arbitrage_tax_adjustment            | money            | false    | input  |
| investment_entity_tax_adjustment           | money            | false    | input  |
| disallowed_deferred_tax_expense_adjustment | money            | false    | input  |
| other_required_tax_adjustments             | money            | false    | input  |
| eligible_payroll_costs                     | money            | false    | input  |
| eligible_tangible_asset_carrying_value     | money            | false    | input  |

## PK

- fiscal_year
- period_start
- period_end
- entity_id

## FK

- (fiscal_year, entity_id) references CompanyEntities(fiscal_year, entity_id).

## Constraints

- All monetary values must be finite.
- `period_start <= period_end`, and both dates fall within `fiscal_year`.
- Rows for the same Entity must not overlap.
- For every calculation period in which an Entity belongs to a Tested Jurisdiction, its rows must form an exact, gap-free partition of that calculation period. A full-year row is therefore sufficient for an Entity whose Tested Jurisdiction is not split, but not for an Entity whose Tested Jurisdiction changes during the year.
- unrealised_net_fair_value_loss, eligible_payroll_costs, and eligible_tangible_asset_carrying_value must be non-negative.
- Adjustment columns are signed: a positive value increases, and a negative value decreases, the corresponding TCSH amount.
- unrealised_net_fair_value_loss records, as a positive amount, net losses arising from fair-value changes in Ownership Interests other than Portfolio Shareholdings, including impairment losses and reversals.

# TcshElections

Tested-Jurisdiction-level inputs required to determine whether the Transitional CbCR Safe Harbour may be applied.

## Columns

| Column            | Data type              | Nullable | Source |
| ----------------- | ---------------------- | -------- | ------ |
| fiscal_year       | year                   | false    | input  |
| period_start      | date                   | false    | input  |
| period_end        | date                   | false    | input  |
| jurisdiction_code | ISO3166-1 alpha-2 code | true     | input  |
| jv_group_id       | positive integer       | true     | input  |
| qualified_cbcr    | boolean                | false    | input  |
| elected           | boolean                | false    | input  |

## Logical key

- (fiscal_year, period_start, period_end, jurisdiction_code, jv_group_id), using null-safe equality.

## FK

- A non-null `(fiscal_year, period_start, period_end, jv_group_id)` must identify a JV row in `JvEntities` covering the election period.

# JurisdictionsTcsh

Tested-Jurisdiction aggregates and Transitional CbCR Safe Harbour test results.

## Columns

| Column                                 | Data type              | Nullable | Source     |
| -------------------------------------- | ---------------------- | -------- | ---------- |
| fiscal_year                            | year                   | false    | calculated |
| period_start                           | date                   | false    | calculated |
| period_end                             | date                   | false    | calculated |
| jurisdiction_code                      | ISO3166-1 alpha-2 code | true     | calculated |
| jv_group_id                            | positive integer       | true     | calculated |
| cbcr_revenue                           | money                  | false    | calculated |
| cbcr_pbt                               | money                  | false    | calculated |
| simplified_covered_taxes               | money                  | false    | calculated |
| simplified_etr                         | number                 | true     | calculated |
| eligible_payroll_costs                 | money                  | false    | calculated |
| eligible_tangible_asset_carrying_value | money                  | false    | calculated |
| substance_based_income_exclusion       | money                  | false    | calculated |
| de_minimis_passed                      | boolean                | false    | calculated |
| simplified_etr_passed                  | boolean                | false    | calculated |
| routine_profits_passed                 | boolean                | false    | calculated |
| passed                                 | boolean                | false    | calculated |
| preconditions_met                      | boolean                | false    | calculated |
| applied                                | boolean                | false    | calculated |
| once_out                               | boolean                | false    | calculated |

## Logical key

- (fiscal_year, period_start, period_end, jurisdiction_code, jv_group_id), using null-safe equality.

## FK

- A non-null `(fiscal_year, period_start, period_end, jv_group_id)` must identify a JV row in `JvEntities` covering the result period.
- The null-safe logical key must identify a row in TcshElections.

## Constraints

- `period_start <= period_end`, and both dates fall within `fiscal_year`.
- `jv_group_id` is taken from the period-specific JV classification recalculated from effective-dated Ownership and Controlling Interests.
- jv_group_id is null for a Tested Jurisdiction consisting of ordinary CEs outside a JV Group.
- simplified_etr is null when the ratio is not evaluated because cbcr_pbt <= 0.
- passed == de_minimis_passed OR simplified_etr_passed OR routine_profits_passed.
- applied == TcshElections.elected AND preconditions_met AND passed.
- preconditions_met must be false when TcshElections.qualified_cbcr is false or a prior-year once_out value is true.
- once_out for a fiscal year is true if it was true in the preceding fiscal year or the Tested Jurisdiction existed but TCSH was not applied in the current fiscal year.

# CompaniesSetr

Entity-level financial accounting starting amounts used by the Simplified ETR Safe Harbour.

## Columns

| Column                                  | Data type        | Nullable | Source |
| --------------------------------------- | ---------------- | -------- | ------ |
| fiscal_year                             | year             | false    | input  |
| entity_id                               | positive integer | false    | input  |
| financial_accounting_net_income_or_loss | money            | false    | input  |
| current_income_tax_expense              | money            | false    | input  |
| deferred_income_tax_expense             | money            | false    | input  |
| attributable_consolidated_deferred_tax  | money            | false    | input  |

## PK

- fiscal_year
- entity_id

## FK

- `(fiscal_year, entity_id)` references `CompanyEntities(fiscal_year, entity_id)`.

## Constraints

- All monetary values must be finite.
- Tax expense columns are signed: a positive value is tax expense and a negative value is tax benefit.
- `attributable_consolidated_deferred_tax` contains only consolidated-level deferred tax attributable to the Entity and not already included in `deferred_income_tax_expense`.

# SetrAdjustments

Signed Tested-Jurisdiction adjustments required after aggregation of `CompaniesSetr` amounts.

## Columns

| Column                                   | Data type              | Nullable | Source     |
| ---------------------------------------- | ---------------------- | -------- | ---------- |
| fiscal_year                              | year                   | false    | input      |
| jurisdiction_code                        | ISO3166-1 alpha-2 code | true     | input      |
| tested_group_type                        | enum                   | false    | calculated |
| tested_group_id                          | positive integer       | true     | calculated |
| basic_income_adjustment                  | money                  | false    | input      |
| industry_income_adjustment               | money                  | false    | input      |
| conditional_income_adjustment            | money                  | false    | input      |
| optional_income_adjustment               | money                  | false    | input      |
| after_year_end_income_adjustment         | money                  | false    | input      |
| cross_border_income_adjustment           | money                  | false    | input      |
| tax_neutral_income_adjustment            | money                  | false    | input      |
| integrity_income_adjustment              | money                  | false    | input      |
| policy_tax_adjustment                    | money                  | false    | input      |
| correlation_tax_adjustment               | money                  | false    | input      |
| uncertain_and_unpaid_tax_adjustment      | money                  | false    | input      |
| deferred_tax_adjustment                  | money                  | false    | input      |
| optional_tax_adjustment                  | money                  | false    | input      |
| after_year_end_tax_adjustment            | money                  | false    | input      |
| cross_border_tax_adjustment              | money                  | false    | input      |
| tax_neutral_and_integrity_tax_adjustment | money                  | false    | input      |
| negative_tax_carryforward_applied        | money                  | false    | input      |

## Logical key

- `(fiscal_year, jurisdiction_code, tested_group_type, tested_group_id)`, using null-safe equality.

## Constraints

- `tested_group_type` is one of `ordinary`, `jv`, `mosg`, `single_moce`, `investment_entity`, or `stateless`.
- `tested_group_id` is null exactly when `tested_group_type == ordinary`.
- `jurisdiction_code` is null exactly when `tested_group_type == stateless`.
- A positive adjustment increases, and a negative adjustment decreases, Simplified Income or Simplified Taxes as applicable.
- `negative_tax_carryforward_applied` is non-negative and is subtracted from Simplified Taxes.
- `deferred_tax_adjustment` includes the net effect of all required exclusions, valuation-allowance and recognition adjustments, tax-rate-change adjustments, and recasting at the Minimum Rate.

# SetrElections

Tested-Jurisdiction elections and eligibility results used by the Simplified ETR Safe Harbour.

## Columns

| Column                                   | Data type              | Nullable | Source     |
| ---------------------------------------- | ---------------------- | -------- | ---------- |
| fiscal_year                              | year                   | false    | input      |
| fiscal_year_start_date                   | date                   | false    | input      |
| jurisdiction_code                        | ISO3166-1 alpha-2 code | true     | input      |
| tested_group_type                        | enum                   | false    | calculated |
| tested_group_id                          | positive integer       | true     | calculated |
| elected                                  | boolean                | false    | input      |
| combine_same_country_investment_entities | boolean                | false    | input      |
| tested_jurisdiction_eligible             | boolean                | false    | calculated |
| entry_or_reentry_eligible                | boolean                | false    | calculated |
| integrity_requirements_met               | boolean                | false    | calculated |
| qdmtt_safe_harbour_applies               | boolean                | false    | calculated |
| tax_neutral_deemed_zero                  | boolean                | false    | calculated |
| loss_dta_adjustment_elected              | boolean                | false    | input      |

## Logical key

- `(fiscal_year, jurisdiction_code, tested_group_type, tested_group_id)`, using null-safe equality.

## Constraints

- The Tested-Jurisdiction key follows the constraints in `SetrAdjustments`.
- `combine_same_country_investment_entities` may be true only when every included Investment Entity and its CE-owners satisfy the Same-country Investment Entity conditions.
- `entry_or_reentry_eligible` is supported by complete results for every Fiscal Year beginning in the applicable preceding 24-month period.
- `tax_neutral_deemed_zero` may be true only under the tax-neutral UPE, Tax Transparent Entity, or Investment Entity tax-transparency rules described in `02.Simplified ETR Safe Harbour Test.md`.

# SetrEarlyElections

Election status under the legislation of each jurisdiction having taxing rights over a Tested Jurisdiction during the optional early-application period.

## Columns

| Column                         | Data type              | Nullable | Source     |
| ------------------------------ | ---------------------- | -------- | ---------- |
| fiscal_year                    | year                   | false    | input      |
| jurisdiction_code              | ISO3166-1 alpha-2 code | true     | input      |
| tested_group_type              | enum                   | false    | calculated |
| tested_group_id                | positive integer       | true     | calculated |
| taxing_right_jurisdiction_code | ISO3166-1 alpha-2 code | false    | calculated |
| elected                        | boolean                | false    | input      |

## Logical key

- `(fiscal_year, jurisdiction_code, tested_group_type, tested_group_id, taxing_right_jurisdiction_code)`, using null-safe equality.

## Constraints

- A row is required for every jurisdiction identified as having taxing rights over the Tested Jurisdiction when optional early application depends on adoption and election by all such jurisdictions.
- `taxing_right_jurisdiction_code` must identify a jurisdiction returned by `Taxing Rights.md` for the Tested Jurisdiction.

# JurisdictionsSetr

Calculated Simplified ETR Safe Harbour amounts and results by Tested Jurisdiction.

## Columns

| Column                              | Data type              | Nullable | Source     |
| ----------------------------------- | ---------------------- | -------- | ---------- |
| fiscal_year                         | year                   | false    | calculated |
| jurisdiction_code                   | ISO3166-1 alpha-2 code | true     | calculated |
| tested_group_type                   | enum                   | false    | calculated |
| tested_group_id                     | positive integer       | true     | calculated |
| jurisdictional_pbt                  | money                  | false    | calculated |
| jurisdictional_income_tax_expense   | money                  | false    | calculated |
| simplified_income                   | money                  | false    | calculated |
| simplified_taxes                    | money                  | false    | calculated |
| simplified_etr                      | number                 | true     | calculated |
| negative_tax_carryforward_generated | money                  | false    | calculated |
| date_available                      | boolean                | false    | calculated |
| eligible                            | boolean                | false    | calculated |
| passed                              | boolean                | false    | calculated |
| applied                             | boolean                | false    | calculated |
| topup_tax_deemed_zero               | boolean                | false    | calculated |

## Logical key

- `(fiscal_year, jurisdiction_code, tested_group_type, tested_group_id)`, using null-safe equality.

## FK

- The null-safe logical key identifies one row in `SetrAdjustments` and one row in `SetrElections`.

## Constraints

- `simplified_etr` is null when `simplified_income <= 0`.
- `negative_tax_carryforward_generated` is non-negative.
- `applied == SetrElections.elected AND eligible AND passed`.
- `topup_tax_deemed_zero == applied`.

# JurisdictionImplementations

## Columns

| Name                     | Data type              | Nullable | Source |
| ------------------------ | ---------------------- | -------- | ------ |
| fiscal_year              | year                   | false    | Input  |
| jurisdiction_code        | ISO3166-1 alpha-2 code | false    | Input  |
| iir_implemented          | boolean                | true     | Input  |
| qiir_implemented         | boolean                | true     | Input  |
| domestic_iir_implemented | boolean                | true     | Input  |
| utpr_implemented         | boolean                | true     | Input  |
| qutpr_implemented        | boolean                | true     | Input  |
| utpr_safeharbour         | boolean                | true     | Input  |
| qdmtt_implemented        | boolean                | true     | Input  |
| qdmtt_safeharbour        | boolean                | true     | Input  |
| has_setr                 | boolean                | false    | Input  |
| has_early_setr           | boolean                | false    | Input  |

## PK

- fiscal_year
- jurisdiction_code

## Constraints

- `qiir_implemented == true` implies `iir_implemented == true`.
- `domestic_iir_implemented == true` implies `iir_implemented == true`.
- `qutpr_implemented == true` implies `utpr_implemented == true`.
- `utpr_safeharbour == null` iff `utpr_implemented == null`.
- `qdmtt_safeharbour == null` iff `qdmtt_implemented == null`.
- A null implementation or qualification status means that the configured source does not establish the value; it is not equivalent to false.
- `has_early_setr == true` implies `has_setr == true`.
- `has_early_setr` identifies adoption for Fiscal Years commencing on or after 31 December 2025 and before 31 December 2026.

# DirectOwnershipInterests

## Columns

| Column                        | Data type        | Nullable | Source |
| ----------------------------- | ---------------- | -------- | ------ |
| fiscal_year                   | year             | false    | input  |
| period_start                  | date             | false    | input  |
| period_end                    | date             | false    | input  |
| investor_entity_id            | positive integer | false    | input  |
| investee_entity_id            | positive integer | false    | input  |
| direct_ownership_ratio        | number           | false    | input  |
| direct_ownership_profit_ratio | number           | true     | input  |
| article_7_4_applicable_fraction  | number           | false    | input  |

## PK

- fiscal_year
- period_start
- period_end
- investor_entity_id
- investee_entity_id

## Constraints

- 0 <= direct_ownership_ratio <= 1
- direct_ownership_profit_ratio is null or 0 <= direct_ownership_profit_ratio <= 1
- 0 <= article_7_4_applicable_fraction <= 1
- `article_7_4_applicable_fraction` is the proportion of the investor's direct Profit Ownership Interest in the investee that remains subject to Article 7.4; 1 means the entire direct Profit Ownership Interest is subject to Article 7.4 and 0 means none of it is.
- `period_start <= period_end`, and both dates fall within `fiscal_year`.
- Effective periods for the same `(investor_entity_id, investee_entity_id)` must not overlap. A missing relationship outside an expressly supplied period means that the relationship does not exist in that period.
- SUM(direct_ownership_ratio) <= 1 for every investee and every date on which the active set of relationships is unchanged.
- SUM(COALESCE(direct_ownership_profit_ratio, direct_ownership_ratio)) <= 1 for every investee and every date on which the active set of relationships is unchanged.
- article_7_4_applicable_fraction == 0 if Relation.InvestmentEntities.is_investment_entity == false

The range and per-investee aggregate constraints for ordinary ownership and profit ownership are validated independently. Passing one set of constraints does not cure a failure in the other.

# DirectControllingInterests

## Columns

| Column                | Data type        | Nullable | Source |
| --------------------- | ---------------- | -------- | ------ |
| fiscal_year           | year             | false    | input  |
| period_start          | date             | false    | input  |
| period_end            | date             | false    | input  |
| controlling_entity_id | positive integer | true     | input  |
| controlled_entity_id  | positive integer | false    | input  |

## PK

- fiscal_year
- period_start
- period_end
- controlled_entity_id

## Constraints

- `period_start <= period_end`, and both dates fall within `fiscal_year`.
- Rows for the same `controlled_entity_id` must not overlap and must collectively cover the entire Fiscal Year without gaps. A null `controlling_entity_id` expressly records that the Entity has no controller for that period.

## Cross-table Validation

Validate each direct controlling relationship against the Entity classifications for the same Fiscal Year:

- An Entity whose matching `ConstituentEntities` row has `is_upe == true` must not appear as `controlled_entity_id`. A UPE has no controller.
- Every Constituent Entity other than a UPE must appear as `controlled_entity_id` in a direct controlling relationship. In the service input representation, its `controller_id` must not be null or blank.
- If `controlling_entity_id` identifies a Constituent Entity and `controlled_entity_id` identifies a Permanent Establishment, that Permanent Establishment must also have a matching `ConstituentEntities` row. A PE that is not a CE must not have a CE as its controller.

These checks are cross-table validations because they depend on `DirectControllingInterests`, `ConstituentEntities`, and `PermanentEstablishments` together. They are applied in addition to the structural and runtime cycle validations in [Controlling Interest.md](<Controlling Interest.md>).

# IncomeInclusions

## Columns

| Column                          | Data type        | Nullable | Source     |
| ------------------------------- | ---------------- | -------- | ---------- |
| fiscal_year                     | year             | false    | calculated |
| parent_entity_id                | positive integer | false    | calculated |
| low_taxed_constituent_entity_id | positive integer | false    | calculated |
| gross_income_inclusion_ratio    | number           | false    | calculated |
| offset                          | number           | false    | calculated |
| net_income_inclusion_ratio      | number           | false    | calculated |
| top_up_tax_payables             | number           | false    | calculated |

## PK

- fiscal_year
- parent_entity_id
- low_taxed_constituent_entity_id

# IirPayables

## Columns

| Column                          | Data type        | Nullable | Source     |
| ------------------------------- | ---------------- | -------- | ---------- |
| fiscal_year                     | year             | false    | calculated |
| parent_entity_id                | positive integer | false    | calculated |
| low_taxed_constituent_entity_id | positive integer | false    | calculated |

## PK

- fiscal_year
- parent_entity_id
- low_taxed_constituent_entity_id

# TopupTaxes

## Columns

| Column      | Data type        | Nullable | Source     |
| ----------- | ---------------- | -------- | ---------- |
| fiscal_year | year             | false    | calculated |
| entity_id   | positive integer | false    | calculated |
| topup_tax   | number           | false    | calculated |

## Constraints

- `topup_tax` must be finite and non-negative.
