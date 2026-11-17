# Link Model

Each atom of the [Output Model](../Output/Model.md) defined in terms of the [Input Model](../Input/Model.md) and the results of the [Calculation Model](../../Calculation-Model/Workflow.md). The Link Model only selects, expands, and aggregates; it calculates nothing itself. This version covers `GeneralSection/CorporateStructure` and the frame of `JurisdictionSection`, following the user guide (`../xml schema.txt`).

# Operators

| Operator | Result |
| --- | --- |
| $\operatorname{rows}(\mathbf{v})$ | $\mathbf{S}\in\{0,1\}^{k\times N}$: the rows of $\mathbf{I}_N$ at which $\mathbf{v}$ is `True` |
| $\operatorname{cells}(\mathbf{A})$ | $(\mathbf{R},\mathbf{Q})$ for the $k$ non-zero cells of $\mathbf{A}\in\mathbb{R}^{a\times b}$ in row-major order: $\mathbf{R}\in\{0,1\}^{a\times k}$ marks the row of each cell and $\mathbf{Q}\in\{0,1\}^{k\times b}$ its column |
| $\operatorname{val}(\mathbf{A})$ | The $k$ non-zero entries of $\mathbf{A}$, in the same order |

A relation with $\mathbf{P}=\mathbf{R}$ therefore has one row per non-zero cell, and $\mathbf{Q}\times\mathbf{a}$ carries an attribute $\mathbf{a}$ of the columns into its rows.

# Entity-Level Matrices

**Rules** $\mathbf{Rule}\in\{0,1\}^{N\times5}$, with columns GIR201 to GIR205:

$$
\begin{aligned}
\mathbf{r}_{201}&:=\mathbf{Entt\text{-}jur}\times(\mathbf{qiir\text{-}impl}\land\neg\mathbf{dom\text{-}iir\text{-}impl})\\
\mathbf{r}_{202}&:=\mathbf{Entt\text{-}jur}\times(\mathbf{qiir\text{-}impl}\land\mathbf{dom\text{-}iir\text{-}impl})\\
\mathbf{r}_{203}&:=\mathbf{Entt\text{-}jur}\times\mathbf{qutpr\text{-}impl}\\
\mathbf{r}_{204}&:=\mathbf{Entt\text{-}jur}\times\mathbf{qdmtt\text{-}impl}\\
\mathbf{r}_{205}&:=\neg(\mathbf{r}_{201}\lor\mathbf{r}_{202}\lor\mathbf{r}_{203}\lor\mathbf{r}_{204})
\end{aligned}
$$

**GloBE status** $\mathbf{Status}\in\{0,1\}^{N\times18}$, with columns GIR301 to GIR318:

| Column | Vector | Column | Vector | Column | Vector |
| --- | --- | --- | --- | --- | --- |
| 301 | $\mathbf{ce}$ | 307 | $\mathbf{mope}$ | 313 | $\mathbf{jv}$ |
| 302 | $\mathbf{fte\text{-}tt}$ | 308 | $\mathbf{mos}$ | 314 | $\mathbf{jvsub}$ |
| 303 | $\mathbf{reverse\text{-}hybrid}$ | 309 | $\mathbf{smoce}$ | 315 | $\mathbf{nmce}$ |
| 304 | $\mathbf{hybrid}$ | 310 | $\mathbf{ie}\land\neg\mathbf{insurance\text{-}ie}$ | 316 | $\mathbf{ee}$ |
| 305 | $\mathbf{pe}$ | 311 | $\mathbf{insurance\text{-}ie}$ | 317 | $\mathbf{art\text{-}10.3.5}$ |
| 306 | $(\mathbf{C}_0\times\mathbf{pe})>0$ | 312 | $\mathbf{securitisation}$ | 318 | $\mathbf{non\text{-}group}$ |

**Owners** $\mathbf{W}\in[0,1]^{(N+2)\times N}$: one row per individually reported owner, one for Excluded Entities in aggregate, and one for non-group members in aggregate. An interest held through Excluded Entities is reported for the Entity that holds it, not for the Excluded Entities, so ownership is first looked through them:

$$
\begin{aligned}
\tilde{\mathbf{X}}&:=\operatorname{diag}(\neg\mathbf{ee})\times\mathbf{X}_0\times(\mathbf{I}_N-\operatorname{diag}(\mathbf{ee})\times\mathbf{X}_0)^{-1}\\
\mathbf{owner}&:=\mathbf{listed}\land\neg\mathbf{ee}\\
\mathbf{W}&:=
\begin{pmatrix}
\operatorname{diag}(\mathbf{owner})\times(\tilde{\mathbf{X}}-\operatorname{diag}(\tilde{\mathbf{X}}))\\
\mathbf{ee}^{T}\times\mathbf{X}_0-\mathbf{owner}^{T}\times(\tilde{\mathbf{X}}-\mathbf{X}_0)\\
\mathbf{1}_N^{T}-\mathbf{1}_N^{T}\times\mathbf{X}_0
\end{pmatrix}
\end{aligned}
$$

The first block excludes treasury shares, and the entries of $\mathbf{W}$ are rounded to four decimal places.

# ID Block

`ID` appears under `UPE` and `CE`. For a selection matrix $\mathbf{S}$ of the Entities reported in the parent relation:

| Output | Link |
| --- | --- |
| `ID/Name` | $\mathbf{S}\times\mathbf{name}$ |
| `ID/ResCountryCode` | $(\mathbf{R},\mathbf{Q}):=\operatorname{cells}(\mathbf{S}\times(\mathbf{Entt\text{-}jur}\;\;\mathbf{stateless}))$; $\mathbf{P}=\mathbf{R}$, value $\mathbf{Q}\times(\mathbf{code},\text{X5})$ |
| `ID/TIN` | $(\mathbf{R},\mathbf{Q}):=\operatorname{cells}(\mathbf{S}\times\mathbf{Entt\text{-}tin})$; $\mathbf{P}=\mathbf{R}$, values $\mathbf{Q}\times\mathbf{tin}$, $\mathbf{Q}\times\mathbf{tin\text{-}issued}$, $\mathbf{Q}\times\mathbf{tin\text{-}type}$ |
| `ID/Rules` | $(\mathbf{R},\mathbf{Q}):=\operatorname{cells}(\mathbf{S}\times\mathbf{Rule})$; $\mathbf{P}=\mathbf{R}$, value $\mathbf{Q}\times(\text{GIR201},\ldots,\text{GIR205})$ |
| `ID/GlobeStatus` | $(\mathbf{R},\mathbf{Q}):=\operatorname{cells}(\mathbf{S}\times\mathbf{Status})$; $\mathbf{P}=\mathbf{R}$, value $\mathbf{Q}\times(\text{GIR301},\ldots,\text{GIR318})$ |

# UPE

$\mathbf{S}_{U}:=\operatorname{rows}(\mathbf{group\text{-}upe})$.

| Output | Link |
| --- | --- |
| $\mathbf{P}_{\text{UPE}}$ | $\mathbf{1}^{T}$: every row belongs to the single `GLOBEBody` row |
| $\boldsymbol{\pi}_{\text{ExcludedUPE}}$ | $\mathbf{S}_{U}\times\mathbf{ee}$ |
| $\boldsymbol{\pi}_{\text{OtherUPE}}$ | $\mathbf{S}_{U}\times\neg\mathbf{ee}$ |
| `ExcludedUPE/ExcludedUPEStatus` | $\mathbf{S}_{U}\times\mathbf{ee\text{-}type}$, as the GIR60x code of the same kind |
| `ExcludedUPE/ID`, `OtherUPE/ID` | [ID block](#id-block) with $\operatorname{diag}(\boldsymbol{\pi})\times\mathbf{S}_{U}$; an Excluded UPE reports no `ResCountryCode` and no `Rules` |

# CE

$\mathbf{S}_{C}:=\operatorname{rows}\bigl((\mathbf{ce}\lor\mathbf{jvmember})\land\neg\mathbf{group\text{-}upe}\bigr)$.

| Output | Link |
| --- | --- |
| $\mathbf{P}_{\text{CE}}$ | $\mathbf{1}^{T}$ |
| `ID` | [ID block](#id-block) with $\mathbf{S}_{C}$ |
| `Ownership` | $(\mathbf{R},\mathbf{Q}):=\operatorname{cells}\bigl((\mathbf{W}\times\mathbf{S}_{C}^{T})^{T}\bigr)$; $\mathbf{P}=\mathbf{R}$ |
| `Ownership/OwnershipPercentage` | $\operatorname{val}\bigl((\mathbf{W}\times\mathbf{S}_{C}^{T})^{T}\bigr)$ |
| `Ownership/OwnershipType` | $\mathbf{Q}\times\mathbf{owner\text{-}type}$: GIR801 for $\mathbf{group\text{-}upe}$, 803 for $\mathbf{jv}$, 804 for $\mathbf{jvsub}$, 802 otherwise; 805 and 806 for the aggregate rows |
| `Ownership/TIN` | $\mathbf{Q}\times$ the owner's first TIN; `NOTIN`, flagged `unknown` with type GIR3004, for the aggregate rows |
| $\boldsymbol{\pi}_{\text{QIIR}}$ | $\mathbf{S}_{C}\times\bigl((\mathbf{pope}\lor\mathbf{ipe})\land\mathbf{qiir}\bigr)$ |
| `QIIR/POPE-IPE` | GIR901 where $\mathbf{pope}$, GIR902 where $\mathbf{ipe}$ |
| $\boldsymbol{\pi}_{\text{Art2.1.3}}$ | $\mathbf{S}_{C}\times\bigl[\mathbf{ipe}\land\mathbf{qiir}\land\bigl((\mathbf{C}^{T}\times(\mathbf{qiir}\land(\mathbf{upe}\oplus\mathbf{ipe})))>0\bigr)\bigr]$ |
| $\boldsymbol{\pi}_{\text{Art2.1.5}}$ | $\mathbf{S}_{C}\times\bigl[\mathbf{pope}\land\mathbf{qiir}\land\bigl((\mathbf{Wholly\text{-}own}^{T}\times(\mathbf{qiir}\land\mathbf{pope}))>0\bigr)\bigr]$ |
| $\boldsymbol{\pi}_{\text{Exception}}$ | $\boldsymbol{\pi}_{\text{Art2.1.3}}+\boldsymbol{\pi}_{\text{Art2.1.5}}$ |
| `QIIR/Exception/TIN` | First TIN of the displacing Parent Entity that is not itself displaced |

# Excluded Entity

$\mathbf{S}_{E}:=\operatorname{rows}(\mathbf{ee}\land\neg\mathbf{group\text{-}upe})$.

| Output | Link |
| --- | --- |
| $\mathbf{P}_{\text{ExcludedEntity}}$ | $\mathbf{1}^{T}$ |
| `Name`, `Type`, `Change` | $\mathbf{S}_{E}\times\mathbf{name}$, $\mathbf{S}_{E}\times\mathbf{ee\text{-}type}$, $\mathbf{S}_{E}\times\mathbf{ee\text{-}change}$ |

# Jurisdiction Section

One row per jurisdiction in which the group has CEs or JV Group members, with X5 standing for Stateless Entities. Let $\mathbf{Entt\text{-}jur}^{+}:=(\mathbf{Entt\text{-}jur}\;\;\mathbf{stateless})$ and $\mathbf{code}^{+}:=(\mathbf{code},\text{X5})$.

$$
\begin{aligned}
\mathbf{S}_{J}&:=\operatorname{rows}\bigl((\mathbf{Entt\text{-}jur}^{+T}\times(\mathbf{ce}\lor\mathbf{jvmember}))>0\bigr)\\
\mathbf{Iir\text{-}rights}&:=\bigl(\mathbf{Entt\text{-}jur}^{T}\times((\mathbf{Iir\text{-}payable}\times\mathbf{Entt\text{-}jur}^{+})>0)\bigr)>0\\
\mathbf{Qdmtt\text{-}rights}&:=(\operatorname{diag}(\mathbf{qdmtt\text{-}impl})\;\;\mathbf{0})
\end{aligned}
$$

$\mathbf{Iir\text{-}rights}$ and $\mathbf{Qdmtt\text{-}rights}$ have collecting jurisdictions on rows and sections on columns. $\mathbf{Iir\text{-}rights}$ is $\mathbf{Iir\text{-}taxing\text{-}rights}$ of [Taxing Rights](<../../Calculation-Model/Taxing Rights.md#iir-taxing-rights>) with the X5 column added.

| Output | Link |
| --- | --- |
| $\mathbf{P}_{\text{JurisdictionSection}}$ | $\mathbf{1}^{T}$ |
| `Jurisdiction` | $\mathbf{S}_{J}\times\mathbf{code}^{+}$ |
| `RecJurCode` | $(\mathbf{R},\mathbf{Q}):=\operatorname{cells}(\mathbf{S}_{J}\times\mathbf{rec\text{-}jur})$; $\mathbf{P}=\mathbf{R}$, value $\mathbf{Q}\times\mathbf{code}$ |
| `JurWithTaxingRights` | $(\mathbf{R},\mathbf{Q}):=\operatorname{cells}\bigl(\mathbf{S}_{J}\times(\mathbf{Iir\text{-}rights}\lor\mathbf{Qdmtt\text{-}rights})^{T}\bigr)$; $\mathbf{P}=\mathbf{R}$ |
| `JurWithTaxingRights/JurisdictionName` | $\mathbf{Q}\times\mathbf{code}$ |
| `DocSpec` | $\mathbf{S}_{J}\times\mathbf{doc\text{-}type}$, $\mathbf{S}_{J}\times\mathbf{doc\text{-}ref}$ |

The rest of the section is left absent, which the schema allows: `Subgroup`, `ReportDifference`, `GLoBETax`, and `LowTaxJurisdiction` report amounts that the Top-up Tax and UTPR documents have yet to define. UTPR taxing rights are not included for the same reason.

# Output Equations

Substituting the links, the Output equations of `CorporateStructure` follow from the Input constraints:

| Output equation | Follows from |
| --- | --- |
| Parent, $\mathbf{P}^{T}\times\mathbf{1}=\mathbf{1}$ | $\mathbf{R}$ of $\operatorname{cells}$ has exactly one 1 per column. |
| Choice, $\boldsymbol{\pi}_{\text{ExcludedUPE}}+\boldsymbol{\pi}_{\text{OtherUPE}}=\mathbf{1}$ | $\mathbf{S}_{U}\times\mathbf{ee}+\mathbf{S}_{U}\times\neg\mathbf{ee}=\mathbf{1}$. |
| At least one `TIN` | $\mathbf{Entt\text{-}tin}\times\mathbf{1}_K\ge\mathbf{listed}$. |
| At least one `Rules` | $\mathbf{r}_{205}$ is the complement of the other four. |
| At least one `GlobeStatus` | Every reported Entity is a CE, a JV, a JV Subsidiary, or an Excluded Entity. |
| At least one `Ownership` | Each column of $\mathbf{X}_0$ sums to at most 1, so an Entity without a group owner has a non-group remainder. |
| `OwnershipPercentage` is a percentage | $\mathbf{W}$ is rounded to four decimal places. |
| At least one `ResCountryCode` | $\mathbf{Entt\text{-}jur}\times\mathbf{1}_M=\neg\mathbf{stateless}$, and a Stateless Entity reports X5. |

`check.py` applies the links to the structure of [Example](../../Calculation-Model/Example.md) and evaluates the 111 Output equations of `CorporateStructure` and the 570 of `JurisdictionSection`; all hold.

`validate.py` adds test values for the required nodes that are not linked yet (`MessageSpec`, `FilingInfo`, `GeneralSection/RecJurCode`, `DocSpec`), writes the document with `../Output/serialize.py`, and validates it against the XSD with two validators. The document, [sample.xml](sample.xml), is valid, and in six deliberately broken variants the equations and the validators reject the same thing. `fuzz.py` repeats the comparison on random documents over the whole schema; no disagreement has been found.

# Open

- **Interests held through non-group members.** Looked through only for Excluded Entities; non-group members are not Entities of the Input Model.
- **GIR309.** Assigned to Single MOCEs only, although a MOPE and a MOS are also MOCEs.
- **Several statuses per owner.** The user guide asks for a separate `ID` where owners treat a Flow-through Entity differently; one `ID` per Entity is produced here.
- **`QIIR/Exception`.** Decided per Entity here, whereas [Taxing Rights](<../../Calculation-Model/Taxing Rights.md#iir-payability>) decides displacement per low-taxed Entity.
- **`QUTPR`, `Art10.3.5`.** Not linked; `QUTPR` waits for the UTPR document.
- **`OwnershipChange`.** Not linked; it needs the [effective periods](<../../Calculation-Model/Ownership Interest.md#effective-periods>).
