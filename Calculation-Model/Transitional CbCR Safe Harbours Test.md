# Interface

## Imports

- [Relations.CompanyEntities](Relations.md#companyentities): `fiscal_year`, `entity_id`, `is_held_for_sale`, and `jurisdiction_code`.
- [Relations.ConstituentEntities](Relations.md#constituententities): CE membership and `is_upe`.
- [Relations.PermanentEstablishments](Relations.md#permanentestablishments): PE membership and `is_permanent_establishment_dtype`.
- [Relations.ExcludedEntities](Relations.md#excludedentities): EE membership.
- [Relations.FlowThroughEntities](Relations.md#flowthroughentities): FTE membership.
- [Relations.InvestmentEntities](Relations.md#investmententities): IE membership and `eligible_for_cbcr_safeharbour`.
- [Relations.DirectOwnershipInterests](Relations.md#directownershipinterests): effective-dated direct Ownership Interests.
- [Relations.DirectControllingInterests](Relations.md#directcontrollinginterests): effective-dated direct Controlling Interests.
- [Relations.JvEntities](Relations.md#jventities): period-specific JV membership, `is_jv`, `is_jv_sub`, and `jv_group_id`, recalculated from the active relationships.
- [Relations.CompaniesTcsh](Relations.md#companiestcsh): Entity-level CbCR amounts and TCSH adjustments.
- [Relations.TcshElections](Relations.md#tcshelections): Qualified CbC Report status and the TCSH election for each Tested Jurisdiction.
- Earlier [Relations.JurisdictionsTcsh](Relations.md#jurisdictionstcsh) rows, where needed to apply the once-out-always-out rule.

The TCSH procedure recalculates the applicable Ownership, Controlling Interest, and JV classification for every period in which the active relationships are unchanged. It does not assume that one annual `jv_group_id` remains valid throughout the Fiscal Year.

## Exports

- [Relations.JurisdictionsTcsh](Relations.md#jurisdictionstcsh): Tested-Jurisdiction aggregates, the three test results, and the final application status.

# Validation

## Structural Validation

- All imported rows must be matched by fiscal_year and entity_id.
- Every effective period is inclusive, has `period_start <= period_end`, and lies within the common Fiscal Year.
- Effective periods for the same Ownership relationship must not overlap. Effective Controlling Interest periods for an Entity must not overlap and must cover the entire Fiscal Year without gaps; a period with no controller is represented expressly by a null controller.
- Each CompaniesTcsh row must reference an Entity in CompanyEntities.
- Each non-null jv_group_id must identify the JV heading the Entity's JV Group in JvEntities.
- An Entity may belong to at most one JV Group during any calculation period.
- Financial rows for an Entity must not overlap and must exactly cover every calculation period in which that Entity belongs to a Tested Jurisdiction.
- Each Tested Jurisdiction result is identified by the null-safe key `(fiscal_year, period_start, period_end, jurisdiction_code, jv_group_id)`.

## Domain Validation

- Ordinary CEs and members of JV Groups must be tested separately, even when they are located in the same jurisdiction.
- Each JV Group must be tested separately from every other JV Group.
- An IE may use the special TCSH treatment only when InvestmentEntities.eligible_for_cbcr_safeharbour is true.
- The transitional period, Qualified CbC Report, and once-out-always-out requirements must be satisfied before a Tested Jurisdiction can apply the safe harbour.

# Operation

## Preconditions for Applying the Transitional CbCR Safe Harbour

Before applying the Transitional CbCR Safe Harbour ("TCSH") Tests, the following conditions must be considered.

### Transitional Period

The TCSH is available only for a Fiscal Year to which the GloBE Rules apply and that begins on or before 31 December 2027, provided that the Fiscal Year does not end after 30 June 2029.

Accordingly, whether the TCSH is available must be determined before performing any of the TCSH Tests.

### Qualified CbC Report

A Qualified CbC Report ("QCbCR") is a Country-by-Country Report prepared and filed using Qualified Financial Statements ("QFS").

For this purpose, QFS may consist of any of the following:
1. Accounts used to prepare the UPE's CFS   
The accounts or reporting packages of the Constituent Entity ("CE") that are used in preparing the CFS of the UPE.
2. Separate Financial Statements of the Constituent Entity
The separate Financial Statements ("separate FS") of the CE, provided that:  
    - they are prepared in accordance with an Acceptable Financial Accounting Standard or an Authorised Financial Accounting Standard;
    - the information contained in those Financial Statements is maintained based on that accounting standard; and
    - the Financial Statements are reliable.
3. Financial accounts of an Entity excluded from consolidation solely on size or materiality grounds    
Where an Entity is not included in the UPE's CFS on a line-by-line basis solely because of size or materiality, the financial accounts of that Entity used for purposes of preparing the CbC Report may be used.

In addition, the financial information used for a Tested Jurisdiction must satisfy the applicable source-consistency requirements.

1. Entity-level consistency     
The relevant financial data of an Entity or PE used for the TCSH, including Revenue, Profit (Loss) before Income Tax, Income Tax Expense, Eligible Payroll Costs, and Eligible Tangible Assets, must generally be derived from the same QFS.    
For example, Profit (Loss) before Income Tax must not be derived from an IFRS reporting package while Income Tax Expense for the same Entity is derived from separate FS prepared under another accounting standard.
2. Tested-Jurisdiction-level consistency    
Constituent Entities within the same Tested Jurisdiction must generally use the same type of QFS.   
Accordingly, the accounts used to prepare the UPE's CFS must not generally be combined, within the same Tested Jurisdiction, with separate FS of other CEs.

Whether a CbC Report qualifies as a QCbCR is therefore determined with respect to each Tested Jurisdiction rather than solely at the level of the CbC Report as a whole.

The result is supplied by `TcshElections.qualified_cbcr` for the corresponding `(fiscal_year, period_start, period_end, jurisdiction_code, jv_group_id)`.

### Stateless CE

A PE described in Article 10.3.3(d) is treated as Stateless. An FTE is also generally treated as Stateless, except where it is the UPE or is required to apply a qualified IIR, in which case it is treated as located in its jurisdiction of creation. The UPE exception can be applied from `ConstituentEntities.is_upe`. For any other FTE, perform the TCSH initially on a Stateless basis and rerun it if the full calculation later establishes the qualified-IIR exception.

### Other Preconditions

The calculation of `preconditions_met` must also reflect the special rules for a Multi-Parented MNE Group without a single Qualified CbC Report and for a jurisdiction subject to an Article 7.3 Eligible Distribution Tax System election. The detailed calculations for these conditions remain to be specified.

### Once Out, Always Out

The "once out, always out" rule must be applied before performing the TCSH Tests.

If an MNE Group does not apply the TCSH with respect to a Tested Jurisdiction in a Fiscal Year in which it is subject to the GloBE Rules, the MNE Group may not apply the TCSH to that Tested Jurisdiction in a subsequent Fiscal Year.

For purposes of this model, a Tested Jurisdiction is identified by the ordered pair

$$
\text{jurisdiction-code},\ \text{jv-group-id}
$$

where `jv_group_id` is null for CEs that are not members of a JV Group.

Accordingly, `JurisdictionsTcsh.applied` records whether the TCSH applies, and `JurisdictionsTcsh.once_out` records whether the Tested Jurisdiction has become ineligible under the once-out-always-out rule.

Formally, let $\text{Once-out}_{TJ,FY}\in\{0,1\}$ denote whether Tested Jurisdiction $\text{TJ}$ has become ineligible for the TCSH as of Fiscal Year $\text{FY}$. Then

$$
\text{Once-out}_{TJ,FY} = \text{Once-out}_{TJ,FY-1} \lor (\text{Existed}_{TJ,FY} \land \neg \text{Applied}_{TJ,FY})
$$

The result is stored in `JurisdictionsTcsh.once_out`. `JurisdictionsTcsh.preconditions_met` is false when a prior-year `once_out` value is true.

A separate interpretative issue arises where the composition of a JV Group changes between Fiscal Years. For example, assume that JV Group 1 located in Korea fails the TCSH in 2024 and, in 2025, becomes a subsidiary of JV Group 2 located in Korea. Under the data model above, the relevant Tested Jurisdiction changes from $\mathrm{KR},1$ to $\mathrm{KR},2$.   
The once-out rule applies to a Tested Jurisdiction rather than directly to individual Entities. The treatment of such a change in JV Group composition is not resolved by this model and requires further interpretative analysis.

### In-year Ownership and Control Changes

The [OECD Safe Harbours and Penalty Relief](https://www.oecd.org/content/dam/oecd/en/topics/policy-sub-issues/global-minimum-tax/safe-harbours-and-penalty-relief-global-anti-base-erosion-rules-pillar-two.pdf) materials frame the safe harbour by Tested Jurisdiction and Fiscal Year and require JV Groups to be tested separately. They do not expressly prescribe a computational method for every in-year change in Ownership or control. The following is therefore an implementation interpretation used by this model, rather than a statement that every relationship change automatically creates a separate TCSH period.

1. An Ownership or Controlling Interest may begin or end during the Fiscal Year. The active relationships are determined independently for each day from the inclusive `period_start` and `period_end` fields.
2. Collect the Fiscal-Year start, every relationship start, the day after every relationship end, and the day after the Fiscal-Year end. Consecutive boundary dates form atomic periods in which the active relationship set is constant.
3. For each atomic period, recalculate direct and indirect Ownership Interests, Controlling Interests, JV status, JV subsidiaries, and `jv_group_id` from the active relationships.
4. Construct the Tested Jurisdiction membership for each atomic period. A membership signature consists of `jurisdiction_code`, null-safe `jv_group_id`, and the complete set of member Entities.
5. Merge adjacent atomic periods for a membership signature when its Entity set is unchanged. Consequently, an unrelated relationship change does not split the result of an unaffected Tested Jurisdiction.
6. Where the membership signature changes, test each resulting period separately and output a separate row with that period's `period_start` and `period_end`. A Tested Jurisdiction unaffected by any relevant change retains one full-Fiscal-Year result.
7. `CompaniesTcsh` amounts used by a split result must be supplied in non-overlapping rows whose periods exactly partition that result period. Amounts from those rows are summed. A full-year financial row cannot be allocated automatically to a shorter result period.

Under this interpretation, the statutory TCSH thresholds and the transition and SBIE rates determined for the common Fiscal Year are applied to each resulting Tested-Jurisdiction period without automatic day-count proration. Any different proration rule requires a separate explicit legal or policy rule and must not be inferred from the relationship dates alone.

## Relational Inputs and Outputs

The schemas for Relations.CompaniesTcsh, Relations.TcshElections, and Relations.JurisdictionsTcsh are defined in [Relations.md](Relations.md#companiestcsh), [Relations.md](Relations.md#tcshelections), and [Relations.md](Relations.md#jurisdictionstcsh), respectively.

CompaniesTcsh supplies one or more non-overlapping rows of Entity-level financial data and signed adjustments for each Entity and Fiscal Year. TcshElections supplies the Tested-Jurisdiction-period-level Qualified CbC Report status and election. JurisdictionsTcsh stores one calculated row for each Tested Jurisdiction result period.

The TCSH procedure does not store a combined Companies relation. For each calculation period, it constructs a temporary Entity view by joining CompanyEntities, the applicable classification relations, the period-specific JvEntities result, and the CompaniesTcsh rows covering the period on fiscal_year and entity_id. In that view:

- CE, PE, EE, FTE, and IE status are derived from row existence in their respective classification relations.
- is_upe, is_permanent_establishment_dtype, and eligible_for_cbcr_safeharbour are read from their classification relations.
- jv_group_id is taken from the period-specific JvEntities result and is null when no JV membership row covers the period.
- jurisdiction_code and is_held_for_sale are read from CompanyEntities.

For an Entity held for sale, cbcr_revenue contains only revenue omitted from the CbC Report because of that presentation. The remaining CompaniesTcsh amounts for that Entity are treated as zero for this calculation.

### Hybrid Arbitrage Arrangement

The rules on Hybrid Arbitrage Arrangements prevent an MNE Group from obtaining the benefit of the TCSH through arrangements that duplicate deductions, losses or taxes, or that otherwise create mismatches between the financial results used for purposes of the TCSH.

For purposes of the TCSH, the relevant arrangements generally include the following categories:
1. Deduction / Non-Inclusion Arrangement
An arrangement under which an expense or loss is recognised in the financial accounts of one CE without a corresponding increase in the revenue or taxable income of the counterparty.
2. Duplicate Loss Arrangement
An arrangement under which the same economic loss is reflected in the financial results of more than one CE or more than one jurisdiction.
3. Duplicate Tax Recognition Arrangement
An arrangement under which the same Income Tax Expense is taken into account more than once for purposes of the Simplified ETR or another relevant GLoBE computation.

The relevant adjustments are reflected separately in $\text{HybridArbitragePbtAdjustment}$ and $\text{HybridArbitrageTaxAdjustment}$.

The former adjusts Profit (Loss) before Income Tax, while the latter adjusts the amount of taxes taken into account in computing Simplified Covered Taxes.

### Investment Entity Adjustments

Where an IE qualifies for treatment under the special TCSH rule described in Section 1, the Profit (Loss) before Income Tax and associated taxes must be adjusted as necessary so that the income and associated taxes of the IE are taken into account only in the jurisdiction of its CE-owner.

Such adjustments are recorded separately as $\text{InvestmentEntityRevenueAdjustment}$, $\text{InvestmentEntityPbtAdjustment}$ and $\text{InvestmentEntityTaxAdjustment}$.

Where a portion of the Ownership Interests in the IE is held by persons that are not members of the MNE Group, the portion attributable to such owners is excluded from the relevant TCSH amounts.

### Disallowed Deferred Tax Expense Adjustment

The 2026 Commentary requires specified deferred tax expense arising from reversals of Article 9.1.2 deferred tax assets or liabilities to be excluded from Simplified Covered Taxes, subject to the applicable grace-period exception.

### Other Required Adjustments

Any additional adjustment required under the GloBE Rules, Commentary or Administrative Guidance that affects Profit (Loss) before Income Tax is recorded in $\text{OtherRequiredPbtAdjustments}$ and any such adjustment affecting Simplified Covered Taxes is recorded in $\text{OtherRequiredTaxAdjustments}$.

## Transitional CbCR Safe Harbour Calculation

Apply the in-year change procedure above and construct the temporary `TcshEntityView` for every resulting calculation period. Retain ordinary CEs and members of JV Groups that are eligible for the TCSH calculation. An IE is retained under the special TCSH treatment only when `eligible_for_cbcr_safeharbour` is true.

For each calculation period, extract the distinct combinations of

$$
(\text{jurisdiction-code},\ \text{jv-group-id})
$$

from the resulting table. Together with `period_start` and `period_end`, each such combination identifies a Tested Jurisdiction result and forms a record key of the JurisdictionsTcsh table.

### Tested Jurisdiction Membership Matrix

Define the Tested Jurisdiction membership matrix

$$
G_{TCSH} \in \{0,1\}^{M_{\mathrm{TCSH}} \times N_{\mathrm{TCSH}}}
$$

where each row represents a Tested Jurisdiction and each column represents a tested Entity.

For Tested Jurisdiction $r$ and Entity $j$,

$$
(G_{TCSH})_{rj}=\begin{cases}
1, & \text{if Entity }j\text{ belongs to Tested Jurisdiction }r\\
0, & \text{otherwise.}
\end{cases}
$$

A Tested Jurisdiction is identified by 

$$
(\text{jurisdiction-code},\ \text{jv-group-id}),
$$

where `jv_group_id` is null for CEs that are not members of a JV Group.

Accordingly, CEs located in the same jurisdiction are generally included in the same row of $G_{TCSH}$, while each JV Group is represented by a separate row even where it is located in the same jurisdiction.

### TCSH Data Matrix

For each Entity, collect the financial data required for the TCSH Tests into the matrix.

$$
Data_{TCSH}^{Entity} \in \mathbb{R}^{N_{\mathrm{TCSH}} \times 16}
$$

with columns ordered as follows:

$$
\begin{aligned}Data_{TCSH}^{Entity} = [&\text{CbcrRevenue},\\
&\text{InvestmentEntityRevenueAdjustment}, \\
&\text{CbcrPbt},\\
&\text{UnrealisedNetFairValueLoss},\\
&\text{HybridArbitragePbtAdjustment},\\
&\text{InvestmentEntityPbtAdjustment},\\
&\text{OtherRequiredPbtAdjustments},\\
&\text{IncomeTaxExpense},\\
&\text{NonCoveredTaxAdjustment},\\
&\text{UncertainTaxPositionAdjustment},\\
&\text{HybridArbitrageTaxAdjustment},\\
&\text{InvestmentEntityTaxAdjustment},\\
&\text{DisallowedDeferredTaxExpenseAdjustment},\\
&\text{OtherRequiredTaxAdjustments},\\
&\text{EligiblePayrollCosts},\\
&\text{EligibleTangibleAssetCarryingValue}.]
\end{aligned}
$$

The jurisdictional aggregates are obtained by matrix multiplication:

$$
\boxed{
\displaystyle
\boldsymbol{Data}_{TCSH}^{\text{TJ}}
=
\boldsymbol{G}_{TCSH}\times\boldsymbol{Data}_{TCSH}^{\text{Entity}}
}
$$

where

$$
Data_{TCSH}^{\text{TJ}} \in \mathbb{R}^{M_{\mathrm{TCSH}} \times 16}
$$

Thus, each row of $Data_{TCSH}^{\text{TJ}}$ contains the aggregate TCSH amounts for one Tested Jurisdiction.

For simplicity, let the corresponding columns of $Data_{TCSH}^{\text{TJ}}$ be denoted by the same names as the underlying columns of $Data_{TCSH}^{\text{Entity}}$.

### Jurisdictional Revenue

Define the TCSH Revenue of a Tested Jurisdiction:

$$
\text{Tcsh-revenue}
:=
Data_{TCSH}^{\text{TJ}}.\text{CbcrRevenue}
+
Data_{TCSH}^{\text{TJ}}.\text{InvestmentEntityRevenueAdjustment}
$$

Store this result as `JurisdictionsTcsh.cbcr_revenue`.

### Profit (Loss) before Income Tax

Define the jurisdictional TCSH Profit (Loss) before Income Tax:

$$
\text{Tcsh-pbt}
:=
Data_{TCSH}^{\text{TJ}}.\text{CbcrPbt} +\
Data_{TCSH}^{\text{TJ}}.\text{HybridArbitragePbtAdjustment} +\
Data_{TCSH}^{\text{TJ}}.\text{InvestmentEntityPbtAdjustment} +\
Data_{TCSH}^{\text{TJ}}.\text{OtherRequiredPbtAdjustments} +\
Data_{TCSH}^{\text{TJ}}.\text{UnrealisedNetFairValueLoss} \times \mathbb{1}_{Data_{TCSH}^{\text{TJ}}.\text{UnrealisedNetFairValueLoss} > 50,000,000}
$$

Store this result as `JurisdictionsTcsh.cbcr_pbt`.

The Unrealised Net Fair Value Loss adjustment is determined at the level of the Tested Jurisdiction rather than separately for each Entity. The aggregate Unrealised Net Fair Value Loss of the Tested Jurisdiction exceeds EUR 50 million, the relevant loss is excluded from Profit (Loss) before Income Tax for purposes of the TCSH Tests.

The UnrealisedNetFairValueLoss is stored as a positive amount representing the amount of the loss to be added back.

### Simplified Covered Taxes

Simplified Covered Taxes are determined from the Income Tax Expense reported in the QFS, after the adjustments required under the TCSH.

Accordingly, define:

$$
\text{Simplified-covered-taxes}
:=
Data_{TCSH}^{\text{TJ}}.\text{IncomeTaxExpense} +\
Data_{TCSH}^{\text{TJ}}.\text{NonCoveredTaxAdjustment} +\
Data_{TCSH}^{\text{TJ}}.\text{UncertainTaxPositionAdjustment} +\
Data_{TCSH}^{\text{TJ}}.\text{HybridArbitrageTaxAdjustment} +\
Data_{TCSH}^{\text{TJ}}.\text{InvestmentEntityTaxAdjustment} +\
Data_{TCSH}^{\text{TJ}}.\text{DisallowedDeferredTaxExpenseAdjustment} +\
Data_{TCSH}^{\text{TJ}}.\text{OtherRequiredTaxAdjustments}
$$

Store this result as `JurisdictionsTcsh.simplified_covered_taxes`.

The adjustment columns are signed amounts. Therefore, a positive adjustment increases Simplified Covered Taxes and a negative adjustment decreases Simplified Covered Taxes.

### Eligible Payroll Costs and Eligible Tangible Assets

The jurisdictional eligible payroll costs and tangible asset carrying values are $Data_{TCSH}^{\text{TJ}}.\text{EligiblePayrollCosts}$ and $Data_{TCSH}^{\text{TJ}}.\text{EligibleTangibleAssetCarryingValue}$.

### Substance-based Income Exclusion

For a Fiscal Year, define the applicable payroll and tangible asset carve-out percentage as $\text{carve-out}_{FY}^{payroll}$ and $\text{carve-out}_{FY}^{tangible-asset}$ respectively.

The Substance-based Income Exclusion ("SBIE") is:

$$\text{carve-out}_{FY}^{payroll} \cdot Data_{TCSH}^{\text{TJ}}.\text{EligiblePayrollCosts} + \text{carve-out}_{FY}^{tangible-asset} \cdot Data_{TCSH}^{\text{TJ}}.\text{EligibleTangibleAssetCarryingValue}
$$

Store this result as `JurisdictionsTcsh.substance_based_income_exclusion`.

The transitional percentages are:  

| Fiscal Year beginning in | Payroll carve-out | Tangible asset carve-out |
| --- | --- | --- |
| 2023 | 10.0% | 8.0% |
| 2024 | 9.8% | 7.8% |
| 2025 | 9.6% | 7.6% |
| 2026 | 9.4% | 7.4% |
| 2027 | 9.2% | 7.2% |
| 2028 | 9.0% | 7.0% |
| 2029 | 8.2% | 6.6% |
| 2030 | 7.4% | 6.2% |
| 2031 | 6.6% | 5.8% |
| 2032 | 5.8% | 5.4% |
| 2033 and thereafter | 5.0% | 5.0% |

The applicable percentage is determined by reference to the Fiscal Year to which the relevant transitional rate applies, rather than merely by the calendar year in which the Fiscal Year ends.

### De Minimis Test

Precondition: if more than one held-for-sale Entity is in the jurisdiction, when the summation of CbCR Revenue and the revenue of the held-for-sale Entity exceeds EUR 10 million, De Minimis Test is not eligible for the Jurisdiction.

A Tested Jurisdiction satisfies the De Minimis Test where its Total Revenue is less than EUR 10 million and its Profit (Loss) before Income Tax is less than EUR 1 million.

Accordingly,

$$
(\text{Tcsh-revenue}<10,000,000)
\land
(\text{Tcsh-pbt}<1,000,000)
$$

Store this result as `JurisdictionsTcsh.de_minimis_passed`.

The test is performed using the jurisdictional amounts after the adjustments required for purposes of the TCSH.

### Simplified ETR Test

The Simplified ETR is:

$$
\text{Simplified-etr}
:=
\frac{\text{Simplified-covered-taxes}}{\text{Tcsh-pbt}}
$$

and the Simplified ETR Test is satisfied where:

$$
\text{Simplified-etr} \ge ETR^{TCSH}_{FY}
$$

where $ETR^{TCSH}_{FY}$ is the applicable Transition Rate:

| Fiscal Year beginning in | Transition Rate |
| --- | --- |
| 2023 | 15% |
| 2024 | 15% |
| 2025 | 16% |
| 2026 | 17% |
| 2027 | 17% |

Store the ratio and test result as `JurisdictionsTcsh.simplified_etr` and `JurisdictionsTcsh.simplified_etr_passed`.

The test is performed using the jurisdictional amounts after the adjustments required for purposes of the TCSH.

For implementation purposes, the Simplified ETR need not be evaluated where $\text{Tcsh-pbt} \le 0$. In that case, the Routine Profits Test is necessarily satisfied because the SBIE cannot be negative.

### Routine Profits Test

A Tested Jurisdiction satisfies the Routine Profits Test where its Profit (Loss) before Income Tax is equal to or less than its SBIE.

Accordingly,

$$
\text{Tcsh-pbt}\le\text{SBIE}
$$

Store this result as `JurisdictionsTcsh.routine_profits_passed`.

### Overall Transitional CbCR Safe Harbour Result

A tested Jurisdiction qualifies for the TCSH where it satisfies at least one of the three tests.

Therefore,

$$
\boxed{
    \text{Passed}=
\text{DeMinimisPassed}\lor \text{SimplifiedEtrPassed} \lor\text{RoutineProfitsPassed}}
$$

This Boolean result is stored as `JurisdictionsTcsh.passed`. The safe harbour is stored as applied only when the tests pass, all Preconditions are met, and `TcshElections.elected` is true.
