# Input Model

The normalized atoms from which the [Calculation Model](../../Calculation-Model/Workflow.md) and the [Link Model](../Link/Model.md) derive the [Output Model](../Output/Model.md). Nothing here repeats, and nothing here can be computed from another atom. It covers every part of the return.

An atom marked optional may have no value; the return then leaves the element out.

# Entities

$N$ Entities, indexed $1,\ldots,N$.

| Atom | Type | Meaning |
| --- | --- | --- |
| $\mathbf{name}$ | $\text{String}^{N}$ | Entity name |
| $\mathbf{X}_0$ | $[0,1]^{N\times N}$ | [Direct Ownership Interest matrix](<../../Calculation-Model/Ownership Interest.md#direct-ownership-matrix>) |
| $\mathbf{C}_0$ | $\{0,1\}^{N\times N}$ | [Direct Controlling Interest matrix](<../../Calculation-Model/Controlling Interest.md#direct-controlling-matrix>) |
| $\mathbf{Entt\text{-}jur}$ | $\{0,1\}^{N\times M}$ | Entity-to-jurisdiction matrix |
| $\mathbf{Entt\text{-}tin}$ | $\{0,1\}^{N\times K}$ | Entity-to-TIN matrix |
| $\mathbf{group\text{-}upe},\mathbf{ce},\mathbf{ee},\mathbf{pe},\mathbf{ie},\mathbf{stateless},\mathbf{eqt}$ | $\{0,1\}^{N}$ | Classifications used by the Calculation Model |
| $\mathbf{fte\text{-}tt},\mathbf{reverse\text{-}hybrid},\mathbf{hybrid},\mathbf{insurance\text{-}ie},\mathbf{securitisation},\mathbf{nmce},\mathbf{non\text{-}group}$ | $\{0,1\}^{N}$ | Classifications reported only in the return |
| $\mathbf{Art\text{-}10.3.5}$ | $\{0,1\}^{N\times M}$ | The jurisdiction whose IIR a Parent Entity located elsewhere must apply under Article 10.3.5; $\mathbf{art\text{-}10.3.5}:=(\mathbf{Art\text{-}10.3.5}\times\mathbf{1}_M)>0$ |
| $\mathbf{ee\text{-}type}$ | $\text{Enum}^{N}$ | Kind of Excluded Entity, where $\mathbf{ee}$ |
| $\mathbf{ee\text{-}change}$ | $\{0,1\}^{N}$ | Change of Excluded Entity status, where $\mathbf{ee}$ |
| $\mathbf{other\text{-}fas}$ | $\text{String}^{N}$, optional | Accounting standard of the Entity, where it differs from that of the consolidated statements |

# TINs

$K$ tax identification numbers.

| Atom | Type | Meaning |
| --- | --- | --- |
| $\mathbf{tin}$ | $\text{String}^{K}$ | Number |
| $\mathbf{tin\text{-}issued}$ | $\{1,\ldots,M\}^{K}$, optional | Issuing jurisdiction |
| $\mathbf{tin\text{-}type}$ | $\text{Enum}^{K}$ | Type of TIN |

# Jurisdictions

$M$ jurisdictions.

| Atom | Type | Meaning |
| --- | --- | --- |
| $\mathbf{code}$ | $\text{CountryCode}^{M}$ | ISO code |
| $\mathbf{iir\text{-}impl},\mathbf{qiir\text{-}impl},\mathbf{dom\text{-}iir\text{-}impl},\mathbf{self\text{-}iir\text{-}impl}$ | $\{0,1\}^{M}$ | As in [Taxing Rights](<../../Calculation-Model/Taxing Rights.md#iir-payability>) |
| $\mathbf{qutpr\text{-}impl},\mathbf{qdmtt\text{-}impl}$ | $\{0,1\}^{M}$ | Qualified UTPR, QDMTT |
| QDMTT terms | per jurisdiction | Accounting standard, currency, whether the SBIE and the de minimis exclusion are available; optional: minimum rate above 15%, basis for blending, currency election |
| $\mathbf{local\text{-}currency}$ | $\text{Currency}^{M}$, optional | Currency of a local filing, where it differs |

# Amounts

| Atom | Type | Meaning |
| --- | --- | --- |
| $\mathbf{fanil}$ | $\mathbb{R}^{N}$ | Financial Accounting Net Income or Loss |
| $\mathbf{income\text{-}tax}$ | $\mathbb{R}^{N}$ | Income tax expense |
| $\mathbf{defer\text{-}expense}$ | $\mathbb{R}^{N}$ | Deferred tax expense for GloBE purposes, before adjustments and recasting |
| $\mathbf{payroll},\mathbf{tangible}$ | $\mathbb{R}_{\ge0}^{N}$ | Eligible Payroll Costs and Eligible Tangible Assets |
| $\rho_{p},\rho_{t}$ | $[0,1]$ | Mark-up rates of the Fiscal Year for payroll and for tangible assets |
| $\mathbf{nm\text{-}rev}$ | $\mathbb{R}^{N\times3}$, optional | Total Revenue of a non-material Entity: the Fiscal Year and the two preceding years |
| $\mathbf{nm\text{-}simplified}$ | $\mathbb{R}^{N}$, optional | Simplified Tax of a non-material Entity |
| $\mathbf{actt\text{-}prior}$ | $\mathbb{R}_{\ge0}^{N}$ | Entity input of [Top-up Tax Calculation](<../../Calculation-Model/Top-up Tax Calculation.md>) |
| $\mathbf{rev},\mathbf{pbt},\mathbf{tax},\mathbf{sbie}$ | $\mathbb{R}^{N}$ | Entity inputs of [TCSH](<../../Calculation-Model/Transitional CbCR Safe Harbours Test.md>) |
| $\mathbf{emp},\mathbf{tan}$ | $\mathbb{R}_{\ge0}^{N}$ | Employees and Tangible Assets, for [UTPR](<../../Calculation-Model/UTPR.md>) |
| $\mathbf{qdmtt},\mathbf{ente\text{-}prior}$ | $\mathbb{R}_{\ge0}^{M_{Calc}}$ | Group inputs of Top-up Tax Calculation |
| $\mathbf{loss\text{-}dta}$ | $\mathbb{R}^{M_{Calc}}$ | GloBE Loss Deferred Tax Asset established or used (Article 4.5) |
| $\mathbf{elected},\mathbf{qsh},\mathbf{ente\text{-}elected}$ | Boolean | Elections of TCSH and Top-up Tax Calculation |
| $\mathbf{utpr\text{-}carry},\mathbf{utpr\text{-}cash}$ | $\mathbb{R}_{\ge0}^{M}$ | UTPR Top-up Tax brought forward and additional cash tax expense |

GloBE Income, Adjusted Covered Taxes and the Substance-based Income Exclusion are not atoms; [Derived Amounts](#derived-amounts) builds them.

# Items

An item matrix has Entities on rows and the items of one adjustment list on columns. Additions and reductions are kept apart, both as non-negative amounts.

| Atom | Type | Items |
| --- | --- | --- |
| $\mathbf{Inc}^{+},\mathbf{Inc}^{-}$ | $\mathbb{R}_{\ge0}^{N\times26}$ | Adjustments to accounting income, GIR2001 to GIR2026 |
| $\mathbf{Tax}^{+},\mathbf{Tax}^{-}$ | $\mathbb{R}_{\ge0}^{N\times17}$ | Adjustments to current tax, GIR2401 to GIR2417 |
| $\mathbf{Def}^{+},\mathbf{Def}^{-}$ | $\mathbb{R}_{\ge0}^{N\times16}$ | Adjustments to deferred tax expense, GIR2501 to GIR2516 |
| $\mathbf{Def}^{hi},\mathbf{Def}^{lo}$ | $\mathbb{R}^{N\times16}$ | Recast of each deferred tax item to the Minimum Rate, from a higher and from a lower rate |

Six columns are not atoms, because another part of the Input already determines them:

| Column | Value |
| --- | --- |
| GIR2013, GIR2017 | Additions and reductions of the `cross-border` rows of the Entity with basis GIR1801 and GIR1802 |
| GIR2022, GIR2023 | Reductions of the `upe-adj` rows of the Entity under Article 7.1 and under Article 7.2 |
| GIR2025 | $[\mathbf{ship}+\mathbf{anc}]^{+}$ in $\mathbf{Inc}^{-}$ and $[-(\mathbf{ship}+\mathbf{anc})]^{+}$ in $\mathbf{Inc}^{+}$ |
| GIR2416 | $[\mathbf{defer\text{-}total}]^{+}$ in $\mathbf{Tax}^{+}$ and $[-\mathbf{defer\text{-}total}]^{+}$ in $\mathbf{Tax}^{-}$ |

# International Shipping

| Atom | Type | Meaning |
| --- | --- | --- |
| $\mathbf{ship\text{-}rev},\mathbf{ship\text{-}cost}$ | $\mathbb{R}^{N}$ | Revenue and costs of International Shipping Income |
| $\mathbf{anc\text{-}rev},\mathbf{anc\text{-}cost}$ | $\mathbb{R}^{N}$ | Revenue and costs of Qualified Ancillary International Shipping Income |
| $\mathbf{Ship\text{-}cat}$ | $\{0,1\}^{N\times6}$ | Activities of Article 3.3.2, GIR2101 to GIR2106 |
| $\mathbf{anc\text{-}cat}$ | $\text{Enum}^{N}$ | Activity of Article 3.3.3, where $\mathbf{Ship\text{-}cat}$ has an entry |
| $\mathbf{ship\text{-}payroll},\mathbf{ship\text{-}tangible},\mathbf{ship\text{-}tax}$ | $\mathbb{R}^{N}$ | Payroll, tangible assets and Covered Taxes attributable to the excluded income |

$\mathbf{ship}:=\mathbf{ship\text{-}rev}-\mathbf{ship\text{-}cost}$ and $\mathbf{anc}:=\mathbf{anc\text{-}rev}-\mathbf{anc\text{-}cost}$.

# Tables

A table $t$ has $k_t$ rows. An incidence matrix $\mathbf{T}_t$ with one 1 per row says what each row belongs to: an Entity ($k_t\times N$), a [Full Calculation Group](<../../Calculation-Model/Group.md#etr-calculation-group>) ($k_t\times M_{Calc}$), or a section of the return ($k_t\times(M+1)$). The other columns are vectors of length $k_t$.

**Rows that belong to an Entity**

| Table | Further columns | Return element |
| --- | --- | --- |
| `transfer` | $\mathbf{From},\mathbf{To}\in\{0,1\}^{k\times N}$ in place of $\mathbf{T}$; basis GIR1701 to GIR1704; amount | `MainEntityPEandFTE` |
| `tax-transfer` | $\mathbf{From},\mathbf{To}$; bases $\{0,1\}^{k\times9}$, GIR2301 to GIR2309; amount | `CrossAllocation` |
| `cross-border` | Other Entity; basis GIR1801 or GIR1802; additions, reductions | `CrossBorderAdjustments` |
| `upe-adj` | Basis GIR1901 to GIR1910; amount, or an exception flag | `UPEAdjustments` |
| `change` | Date; statuses before the change $\{0,1\}^{k\times21}$, GIR701 to GIR721; owners before the change $\mathbf{W}^{pre}\in[0,1]^{k\times(N+2)}$ | `OwnershipChange` |
| `art-6.3.4` | Fiscal Year of the triggering event; option (i) or (ii) | `Elections/Art6.3.4` |
| `art-7.5` | Status, election year, revocation year; Constituent Entity-owners $\{0,1\}^{k\times N}$ | `Elections/Art7.5` |
| `art-7.6` | Status, years; distributions, creditable tax, share of undistributed income; the Investment Entity | `Elections/Art7.6` |

A `transfer` row moves an amount of income from one Entity to another, and a `tax-transfer` row an amount of Covered Taxes. The columns of $\mathbf{W}^{pre}$ are those of $\mathbf{W}$ in the [Link Model](../Link/Model.md#entity-level-matrices).

**Other rows about Entities**

| Table | Rows | Columns | Return element |
| --- | --- | --- | --- |
| `upe-owner` | Belong to a `upe-adj` row | Ownership percentage; either number, jurisdiction and tax rate of individual owners, or TIN, jurisdiction, tax rate and kind of an Entity owner | `IdentificationOfOwners` |
| `tax-group` | One per tax consolidation group | TIN of the group; members $\mathbf{Entt\text{-}taxgroup}\in\{0,1\}^{N\times k}$ | `AggregatedReporting` |

**Rows that belong to a Full Calculation Group**

| Table | Further columns | Return element |
| --- | --- | --- |
| `recalc` | Year; articles $\{0,1\}^{k\times6}$, GIR2601 to GIR2606; income, taxes, ETR, Excess Profit, Top-up Tax Percentage and Top-up Tax, as previously reported and as recalculated | `NONArt4.1.5` |
| `post-dta`, `post-refund` | Year; amount | `PostFilingAdjust` |
| `ddt` | Year; opening balance; tax of the year and of the three preceding years; closing balance | `DeemedDistTax/Election/Recapture` |
| `transition` | Year; optional: deferred tax liabilities at the start and recast; deferred tax assets in total, at the start, recast and excluded; a disposal with its jurisdiction and four amounts; alternative jurisdiction | `DeferTaxAdjustAmt/Transition` |
| `cfc` | Jurisdiction of the CFCs; top Entity of the subgroup; amount | `TransBlendCFC` |
| `sbie-pe`, `sbie-fte` | Jurisdiction of the owners, UPE, or neither; payroll in total and allocated; tangible assets in total and allocated | `PEAllocation`, `FTEAllocation` |
| `dm-prior` | Year; revenue, GloBE revenue, GloBE Income, accounting income | `Deminimis-SimplifiedNMCECalc/FinancialData` |
| `data-point` | Optional: description, amount, percentage, text, Boolean | `Summary/AdditionalDataPoint` |

**Rows that belong to a section**

| Table | Further columns | Return element |
| --- | --- | --- |
| `diff` | Jurisdiction with taxing rights $\{0,1\}^{k\times M}$; the thirteen optional amounts of `ReportDifference` as they are under that jurisdiction's law | `ReportDifference`, `DiffDomesticTut` |
| `data-point` | As above | `JurisdictionSection/AdditionalDataPoint` |

Two more `data-point` tables belong to nothing: those of the general section and of the UTPR attribution.

# Group Detail

Indexed by the $M_{Calc}$ Full Calculation Groups; all optional.

| Atom | Type | Meaning |
| --- | --- | --- |
| $\mathbf{def\text{-}diff},\mathbf{def\text{-}globe}$ | $\mathbb{R}^{M_{Calc}}$ | Deferred tax expense on assets and liabilities whose GloBE carrying value differs: at the accounting value, at the GloBE value |
| $\mathbf{Recapture}$ | $\mathbb{R}^{M_{Calc}\times9}$ | Deferred tax liabilities subject to recapture: the nine amounts of `RecaptureDeferred` |
| $\mathbf{ddt\text{-}reduction},\mathbf{ddt\text{-}increment},\mathbf{ddt\text{-}ratio}$ | $\mathbb{R}^{M_{Calc}}$ | Article 7.3: reduction of prior Adjusted Covered Taxes, incremental Top-up Tax, Disposition Recapture Ratio |
| $\mathbf{dm\text{-}basis}$ | $\text{Enum}^{M_{Calc}}$ | De minimis election (GIR2901) or simplified calculation for non-material Entities (GIR2902) |
| $\mathbf{dm\text{-}rev},\mathbf{dm\text{-}globe\text{-}rev}$ | $\mathbb{R}^{M_{Calc}}$ | Revenue and GloBE revenue of the Fiscal Year, where $\mathbf{dm\text{-}basis}$ |

# Elections

A five-year election is a triple of status, election year and revocation year.

| Atom | Indexed by | Elections |
| --- | --- | --- |
| Five-year elections of an Entity | $N$ | Articles 1.5.3, 3.2.1(b), 3.2.1(c), 4.4.7, 4.5.6 |
| Flags of an Entity | $N$ | Simplified calculations for non-material Entities; debt release (Article 3.2.1) |
| Five-year elections of a group | $M_{Calc}$ | Articles 3.2.2, 3.2.5, 3.2.8, 4.5, 3.2.1(c); no deferred tax allocation |
| Flags of a group | $M_{Calc}$ | Articles 3.2.6, 4.6.1, 5.3.1; simplified reporting. Article 4.1.5 is $\mathbf{ente\text{-}elected}$. |
| $\mathbf{qo\text{-}opening},\mathbf{qo\text{-}add},\mathbf{qo\text{-}red}$ | $M_{Calc}$ | Balance of the Article 3.2.1(c) election of a group: opening amount, additions, reductions |

# UTPR Exclusions

| Atom | Type | Meaning |
| --- | --- | --- |
| $\mathit{art\text{-}9.3}$ | Boolean | The group is in the initial phase of its international activity |
| Initial phase | | First day of the first Fiscal Year in scope; the Reference Jurisdiction; tangible assets by jurisdiction in that year, $\mathbf{tan}^{0}\in\mathbb{R}_{\ge0}^{M}$ |
| $\mathit{utpr\text{-}sh},\mathit{cit\text{-}rate}$ | Boolean, $[0,1]$ | The Transitional UTPR Safe Harbour applies; corporate income tax rate of the UPE jurisdiction |

# Filing

One row per section of the return: $M+1$ jurisdiction sections, the last for Stateless Entities.

| Atom | Type | Meaning |
| --- | --- | --- |
| $\mathbf{rec\text{-}jur}$ | $\{0,1\}^{(M+1)\times M}$ | Recipient jurisdictions of each section |
| $\mathbf{doc\text{-}type},\mathbf{doc\text{-}ref}$ | $\text{Enum}^{M+1}$, $\text{String}^{M+1}$ | Document type and reference of each section |
| $\mathbf{corr\text{-}ref}$ | $\text{String}^{M+1}$, optional | Reference of the document that the section corrects |
| Message header | | Transmitting and receiving jurisdiction, message reference, reporting period, timestamp; optional: schema version, sending Entity, contact, warning |
| Filing information | | Filing Constituent Entity and its role, accounting standard, currency, period, name of the group; optional: additional information |
| $\mathit{unreported\text{-}change}$ | Boolean, optional | Changes of the corporate structure during the year that are not in `change` |

The filing information, the general section, each summary row and the UTPR attribution have a document type, reference and optional corrected reference of their own.

# Derived Amounts

The amounts that the Calculation Model takes as inputs, built from the atoms above. With $\mathbf{G}:=\mathbf{Entt\text{-}group}$ of [Top-up Tax Calculation](<../../Calculation-Model/Top-up Tax Calculation.md>) and $[x]^{+}:=\max(x,0)$:

$$
\begin{aligned}
\mathbf{adj\text{-}fanil}&:=\mathbf{fanil}+(\mathbf{To}-\mathbf{From})^{T}\times\mathbf{amount}\\
\mathbf{globe\text{-}income}&:=\mathbf{adj\text{-}fanil}+(\mathbf{Inc}^{+}-\mathbf{Inc}^{-})\times\mathbf{1}\\
\mathbf{adj\text{-}tax}&:=\mathbf{income\text{-}tax}+(\mathbf{To}-\mathbf{From})^{T}\times\mathbf{amount}\\
\mathbf{defer\text{-}total}&:=\mathbf{defer\text{-}expense}+(\mathbf{Def}^{+}-\mathbf{Def}^{-}+\mathbf{Def}^{hi}+\mathbf{Def}^{lo})\times\mathbf{1}\\
\mathbf{act}&:=\mathbf{adj\text{-}tax}+(\mathbf{Tax}^{+}-\mathbf{Tax}^{-})\times\mathbf{1}\\
\mathbf{sbie}&:=\rho_{p}\cdot\mathbf{payroll}+\rho_{t}\cdot\mathbf{tangible}\\
\mathbf{ship\text{-}cap}&:=\tfrac{1}{2}\left[\mathbf{G}^{T}\times\mathbf{ship}\right]^{+}\\
\mathbf{income\text{-}adj}&:=\left[\mathbf{G}^{T}\times\mathbf{anc}-\mathbf{ship\text{-}cap}\right]^{+}\\
\mathbf{act\text{-}adj}&:=\mathbf{loss\text{-}dta}
\end{aligned}
$$

$\mathbf{From}$, $\mathbf{To}$ and $\mathbf{amount}$ are the columns of `transfer` in the first line and of `tax-transfer` in the third.

- **Income.** $\mathbf{adj\text{-}fanil}$ is accounting income after the allocations between Main Entity, Permanent Establishment and Flow-through Entity. The item columns then lead to GloBE Income.
- **Taxes.** $\mathbf{adj\text{-}tax}$ is current tax after cross-allocation. The Total Deferred Tax Adjustment Amount $\mathbf{defer\text{-}total}$ enters Adjusted Covered Taxes as item GIR2416.
- **Shipping.** An Entity excludes all of its shipping income as item GIR2025. Qualified Ancillary income above the cap of 50% of the group's International Shipping Income stays in GloBE Income, so the group adds it back as $\mathbf{income\text{-}adj}$.

# Constraints

With $\mathbf{listed}:=\mathbf{group\text{-}upe}\lor\mathbf{ce}\lor\mathbf{jvmember}$, the Entities reported individually:

| Constraint | Reason |
| --- | --- |
| $\mathbf{Entt\text{-}tin}^{T}\times\mathbf{1}_N=\mathbf{1}_K$ | A TIN belongs to one Entity. |
| $\mathbf{Entt\text{-}tin}\times\mathbf{1}_K\ge\mathbf{listed}$ | The return requires a TIN for every reported Entity. |
| $\mathbf{Entt\text{-}jur}\times\mathbf{1}_M=\neg\mathbf{stateless}$ | An Entity has one jurisdiction unless it is stateless. |
| $\mathbf{rec\text{-}jur}\times\mathbf{1}_M\ge\mathbf{1}_{M+1}$ | The return requires a recipient for every section. |
| $\mathbf{From}\times\mathbf{1}_N=\mathbf{To}\times\mathbf{1}_N=\mathbf{1}$ and $\mathbf{From}\odot\mathbf{To}=\mathbf{0}$ | A transfer has one source and one other destination. |
| $\mathbf{G}^{T}\times\mathbf{actt\text{-}prior}=\mathbf{T}_{\text{recalc}}^{T}\times(\text{recalculated}-\text{previous Top-up Tax})$ | The Additional Current Top-up Tax of a group is that of its recalculations. |
| $\mathbf{T}_{\text{dm-prior}}^{T}\times\mathbf{1}\le2$ | The de minimis exclusion looks at the Fiscal Year and two preceding years. |
| A row has every column that the schema requires of its element | For example a five-year election with a status has an election year, and a shipping Entity has $\mathbf{anc\text{-}cat}$. |
| $\mathbf{Def}^{hi}$ and $\mathbf{Def}^{lo}$ are zero where $\mathbf{Def}^{+}$ and $\mathbf{Def}^{-}$ are | A recast belongs to an adjustment row. |

The validations of the Calculation Model documents apply in addition.
