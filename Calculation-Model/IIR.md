# Interface

## Imports

- Relations.CompanyEntities
- Relations.ConstituentEntities
- Relations.PermanentEstablishments
- Relations.ExcludedEntities
- Relations.InvestmentEntities
- Relations.JvEntities
- Relations.DirectOwnershipInterests
- Relations.TopupTaxes
- Common Entity indicator vectors from [Definition.md](Definition.md#common-entity-indicator-vectors).
- The direct and indirect Ownership Interest function $f(\mathbf{A})$ from [Ownership Interest.md](<Ownership Interest.md#exports>).
- The current-year IIR payability matrix $\mathbf{Iir\text{-}payable}$ from [Taxing Rights.md](<Taxing Rights.md#iir-payability>).

## Exports

### IIR Allocation Results

This document calculates the Gross Income Inclusion Ratio, IIR Offset, Net Income Inclusion Ratio, Article 7.4-adjusted Net Income Inclusion Ratio, and IIR Top-up Tax allocated to each Parent Entity.

The resulting sparse relation is:

**Relation.IncomeInclusions**

~~~text
{
  fiscal_year,
  parent_entity_id,
  low_taxed_constituent_entity_id,
  gross_income_inclusion_ratio,
  iir_offset,
  net_income_inclusion_ratio,
  top_up_tax_payable
}
~~~

For a JV or JV Subsidiary subject to the analogous Article 6.4 calculation, low_taxed_constituent_entity_id identifies the relevant low-taxed Entity even though it is not a Constituent Entity of the MNE Group.

# Validation

## Structural Validation

- All imported relations and matrices must use the same fiscal year and Entity ordering.

## Domain Validation

- No Entity may hold 100% of its own Profit Ownership Interests, because the treasury-share adjustment would be undefined.

# Operation

## Notation

Bold uppercase symbols denote matrices, bold lowercase names denote column vectors, and calligraphic symbols denote index sets. Indices, individual entries, and $N$ are scalars.

| Symbol | Type and meaning |
| --- | --- |
| $N$ | Number of Entities. |
| $\mathbf{X}_0^{\mathrm{profit}}\in[0,1]^{N\times N}$ | Direct Profit Ownership Interest matrix. |
| $\mathbf{Iir\text{-}payable}\in\{0,1\}^{N\times N}$ | Current-year IIR payability matrix; Parent Entities are on rows and potential low-taxed Entities are on columns. |
| $\mathbf{R}^{7.4}\in[0,1]^{N\times N}$ | Article 7.4 applicability fraction matrix. |
| $\mathbf{ce},\mathbf{ee},\mathbf{ie},\mathbf{jv},\mathbf{jvsub},\mathbf{group\text{-}upe}\in\{0,1\}^{N\times1}$ | Entity indicator vectors. |
| $\mathbf{I}_N$ | $N\times N$ identity matrix. |
| $\mathbf{1}_N,\mathbf{0}_N$ | All-one and all-zero column vectors. |
| $\mathbf{1}_{N\times N},\mathbf{0}_{N\times N}$ | All-one and all-zero matrices. |
| $\mathcal{S}_j$ | Indices of Parent Entities that are IIR-payable for Entity $j$. |
| $i,j,k,q,g$ | Entity indices, derivation step, or JV Group identifier. |

The operator $\operatorname{diag}$ follows [Definition.md](Definition.md#mathematical-notation): for a square matrix it retains only the diagonal entries, and for a vector it constructs a diagonal matrix.

## Local Matrix Functions

This document uses ordinary mathematical function names rather than qualified Function names.

### Masking Function

For matrix $\mathbf{A}$ and row and column indicator vectors $\mathbf{u}$ and $\mathbf{v}$, define:

$$
\boxed{
m(\mathbf{A};\mathbf{u},\mathbf{v})
:=
\operatorname{diag}(\mathbf{u})\,
\mathbf{A}\,
\operatorname{diag}(\mathbf{v})
}
$$

For the symmetric case:

$$
\boxed{
m(\mathbf{A};\mathbf{u})
:=
m(\mathbf{A};\mathbf{u},\mathbf{u})
}
$$

### Treasury-Share Removal Function

Define:

$$
\boxed{
t(\mathbf{A})
:=
\bigl(\mathbf{A}-\operatorname{diag}(\mathbf{A})\bigr)
\bigl(\mathbf{I}_N-\operatorname{diag}(\mathbf{A})\bigr)^{-1}
}
$$

The right multiplication grosses up each non-treasury interest by the reciprocal of one minus the investee's treasury-share ratio.

### Unit-Diagonal Function

Define:

$$
\boxed{
g(\mathbf{A})
:=
\mathbf{A}-\operatorname{diag}(\mathbf{A})+\mathbf{I}_N
}
$$

Thus, $g$ replaces the diagonal of a square matrix with ones and leaves all off-diagonal entries unchanged.

## Imported IIR Payability

A non-zero element

$$
(\mathbf{Iir\text{-}payable})_{ij}=1
$$

means that Parent Entity $i$ may apply the IIR to potential low-taxed Entity $j$ for the current fiscal year. Parent Entity identification, jurisdictional implementation conditions, and the top-down and split-ownership priority rules are calculated in [Taxing Rights.md](<Taxing Rights.md#iir-payability>).

## Income Inclusion Ratio

### Ownership Graph

Retain CEs and members of a JV Group:

$$
\mathbf{member}
:=
\mathbf{ce}\lor\mathbf{jv}\lor\mathbf{jvsub}.
$$

First remove treasury shares from the direct Profit Ownership Interest matrix:

$$
\boxed{
\mathbf{X}_0^{\mathrm{profit,treasury}}
:=
t(\mathbf{X}_0^{\mathrm{profit}})
}
$$

For example, if an Entity holds 20% of its own Profit Ownership Interests and another Entity holds the remaining 80%, $t$ treats the external holder as holding 100% of the outstanding interests.

Apply the member mask after the treasury-share adjustment:

$$
\mathbf{X}_0^{\mathrm{profit,treasury,member}}
:=
m\bigl(
\mathbf{X}_0^{\mathrm{profit,treasury}};
\mathbf{member}
\bigr).
$$

For the ordinary IIR calculation, abbreviate this matrix as:

$$
\boxed{
\mathbf{X}
:=
\mathbf{X}_0^{\mathrm{profit,treasury,member}}
=
m\bigl(t(\mathbf{X}_0^{\mathrm{profit}});\mathbf{member}\bigr)
}
$$

The corresponding direct and indirect Profit Ownership Interest matrix is abbreviated as:

$$
\boxed{
\mathbf{Y}
:=
f(\mathbf{X})
}
$$

These aliases are used throughout the ordinary IIR derivation below. The aliases $\mathbf{X}$ and $\mathbf{Y}$ apply only to the ordinary IIR calculation; Article 7.4 uses separately labelled ownership matrices.

### Iterative Derivation

The IIR Offset Mechanism can be expressed as an iterative process that propagates unpaid ownership interests through the ownership structure until they reach an IIR-payable Parent Entity.

Initialize:

$$
\mathbf{Iir\text{-}paid}_0:=\mathbf{0}_{N\times N},
\qquad
\mathbf{Iir\text{-}unpaid}_0:=\mathbf{I}_N,
$$

and define:

$$
\mathbf{Iir\text{-}unpayable}
:=
\mathbf{1}_{N\times N}-\mathbf{Iir\text{-}payable}.
$$

For derivation step $q$, apply:

$$
\mathbf{Iir\text{-}paid}_{q+1}
=
\mathbf{Iir\text{-}paid}_{q}
+
\left(
\mathbf{X}\cdot
\mathbf{Iir\text{-}unpaid}_{q}
\right)
\odot
\mathbf{Iir\text{-}payable},
$$

$$
\mathbf{Iir\text{-}unpaid}_{q+1}
=
\left(
\mathbf{X}\cdot
\mathbf{Iir\text{-}unpaid}_{q}
\right)
\odot
\mathbf{Iir\text{-}unpayable}.
$$

The limiting result is:

$$
\mathbf{Net\text{-}iir}
:=
\lim_{q\to\infty}\mathbf{Iir\text{-}paid}_{q}.
$$

**Net Income Inclusion Ratio** is a modelling term for the portion of the Inclusion Ratio remaining after the IIR Offset Mechanism.

The ratio before the offset mechanism is:

$$
\mathbf{Gross\text{-}iir}
:=
\mathbf{Y}
\odot
\mathbf{Iir\text{-}payable}.
$$

The IIR Offset is:

$$
\mathbf{Iir\text{-}offset}
:=
\mathbf{Gross\text{-}iir}-\mathbf{Net\text{-}iir}.
$$

### Direct Method

The Direct Method is algebraically equivalent to the iterative method above and is used for numerical implementation.

For a payable Parent Entity $i$ with $(\mathbf{Iir\text{-}payable})_{ij}=1$, component-wise:

$$
(\mathbf{Net\text{-}iir})_{ij}
=
(\mathbf{Y})_{ij}
(\mathbf{Iir\text{-}payable})_{ij}
-
\sum_{\substack{k=1\\k\ne i}}^{N}
(\mathbf{Y})_{ik}
(\mathbf{Net\text{-}iir})_{kj}.
$$

The final term removes the portion of Entity $i$'s indirect interest in Entity $j$ that is brought into charge through another Parent Entity $k$.

Move that term to the left:

$$
(\mathbf{Net\text{-}iir})_{ij}
+
\sum_{\substack{k=1\\k\ne i}}^{N}
(\mathbf{Y})_{ik}
(\mathbf{Net\text{-}iir})_{kj}
=
(\mathbf{Y})_{ij}
(\mathbf{Iir\text{-}payable})_{ij}.
$$

Without the element-wise payability restriction, the system is:

$$
g(\mathbf{Y})
\mathbf{Net\text{-}iir}
=
\mathbf{Y}
\odot
\mathbf{Iir\text{-}payable}.
$$

For each potential low-taxed Entity $j$, define:

$$
\mathcal{S}_j
:=
\left\{
i\mid(\mathbf{Iir\text{-}payable})_{ij}=1
\right\}.
$$

Solve only over the payable Parent Entities:

$$
\boxed{
(\mathbf{Net\text{-}iir})_{\mathcal{S}_j,j}
=
\left[
g(\mathbf{Y})_{\mathcal{S}_j,\mathcal{S}_j}
\right]^{-1}
\mathbf{Y}_{\mathcal{S}_j,j}
}
$$

For the complement $\overline{\mathcal{S}}_j$:

$$
(\mathbf{Net\text{-}iir})_{\overline{\mathcal{S}}_j,j}
=
\mathbf{0}.
$$

#### Equivalence of the Iterative and Direct Methods

Fix a potential low-taxed Entity $j$ and partition the Entity indices into

$$
\mathcal{S}:=\mathcal{S}_j,
\qquad
\mathcal{T}:=\overline{\mathcal{S}}_j.
$$

This is an index partition, not a change to the ownership graph. Reordering rows and columns conceptually by these two sets gives

$$
\mathbf{X}
=
\begin{bmatrix}
\mathbf{X}_{\mathcal{S},\mathcal{S}}
&
\mathbf{X}_{\mathcal{S},\mathcal{T}}
\\
\mathbf{X}_{\mathcal{T},\mathcal{S}}
&
\mathbf{X}_{\mathcal{T},\mathcal{T}}
\end{bmatrix}.
$$

Under the iterative recurrence, an ownership path is absorbed as soon as it reaches an Entity in $\mathcal{S}$; only paths that remain in $\mathcal{T}$ continue to propagate. Therefore the limiting allocation to the payable Parents is

$$
\boxed{
(\mathbf{Net\text{-}iir})_{\mathcal{S},j}
=
\mathbf{X}_{\mathcal{S},j}
+
\mathbf{X}_{\mathcal{S},\mathcal{T}}
(\mathbf{I}-\mathbf{X}_{\mathcal{T},\mathcal{T}})^{-1}
\mathbf{X}_{\mathcal{T},j}
}
$$

because

$$
(\mathbf{I}-\mathbf{X}_{\mathcal{T},\mathcal{T}})^{-1}
=
\mathbf{I}
+
\mathbf{X}_{\mathcal{T},\mathcal{T}}
+
\mathbf{X}_{\mathcal{T},\mathcal{T}}^2
+\cdots.
$$

Thus the second term collects every path that first leaves a payable Parent through $\mathcal{T}$, remains within $\mathcal{T}$ for zero or more additional steps, and then reaches Entity $j$.

The same expression follows from eliminating the $\mathcal{T}$ block of the corresponding linear system. In general, for a block system

$$
\begin{bmatrix}
\mathbf{A}&\mathbf{B}\\
\mathbf{C}&\mathbf{D}
\end{bmatrix}
\begin{bmatrix}
\mathbf{x}\\
\mathbf{y}
\end{bmatrix}
=
\begin{bmatrix}
\mathbf{p}\\
\mathbf{q}
\end{bmatrix},
$$

if $\mathbf{D}$ is invertible, then

$$
\mathbf{y}
=
\mathbf{D}^{-1}(\mathbf{q}-\mathbf{C}\mathbf{x}),
$$

and substitution into the first block equation gives

$$
\left(
\mathbf{A}-\mathbf{B}\mathbf{D}^{-1}\mathbf{C}
\right)\mathbf{x}
=
\mathbf{p}-\mathbf{B}\mathbf{D}^{-1}\mathbf{q}.
$$

The matrix

$$
\boxed{
\mathbf{A}-\mathbf{B}\mathbf{D}^{-1}\mathbf{C}
}
$$

is the Schur complement of $\mathbf{D}$. In the IIR allocation, the $\mathcal{T}$ variables can be eliminated algebraically rather than propagated step by step. Their effect is preserved in the resulting system over $\mathcal{S}$, so the ownership paths through non-payable Entities do not need to be calculated separately. The Direct Method solves this reduced system directly.

Accordingly, the iterative recurrence and the Direct Method are algebraically equivalent: the recurrence gives a constructive path-based characterization of the IIR Offset Mechanism, while the Direct Method solves the same allocation after the non-payable paths have been eliminated algebraically.

The direct method is the implementation method because it solves each constrained allocation system directly.

## Investment Entity Special Rule

Article 7.4 applies to the GloBE Income or Loss remaining at the Investment Entity after any allocation required under Article 3.5.

### Article 7.4 Applicability Matrix

Let:

$$
\mathbf{R}^{7.4}\in[0,1]^{N\times N}
$$

be derived from Relations.DirectOwnershipInterests.article_7_4_applicable_fraction. The scalar $(\mathbf{R}^{7.4})_{ij}$ is the proportion of Entity $i$'s direct Profit Ownership Interest in Entity $j$ that remains subject to Article 7.4.

The fraction is applied to the direct Profit Ownership Interest matrix before the direct and indirect Ownership Interest function $f$ is evaluated. The resulting Article 7.4 ownership graphs are used only to determine the MNE Group's Allocable Share.

### Constituent Entity Investment Entity

For an IE that is a CE, retain CEs and EEs in the MNE Group ownership graph:

$$
\mathbf{mne\text{-}member}
:=
\mathbf{ce}\lor\mathbf{ee}.
$$

Define the local Article 7.4 ownership matrices:

$$
\boxed{
\mathbf{X}^{7.4}
:=
m\bigl(
\mathbf{X}_0^{\mathrm{profit,treasury}}
\odot
\mathbf{R}^{7.4};
\mathbf{mne\text{-}member}
\bigr)
}
$$

$$
\boxed{
\mathbf{Y}^{7.4}
:=
f\bigl(\mathbf{X}^{7.4}\bigr)
}
$$

EEs remain in the ownership graph because they remain Entities of the MNE Group. JVs and JV Subsidiaries are excluded because each JV Group is treated separately under Article 6.4.

The MNE Group's Allocable Share is the aggregate Article 7.4-adjusted direct and indirect Profit Ownership Interest held by the group UPEs in each CE Investment Entity:

$$
\boxed{
\left(\mathbf{mne\text{-}allocable\text{-}share}^{ce}\right)^T
:=
\mathbf{1}_N^T
\operatorname{diag}(\mathbf{group\text{-}upe})
\mathbf{Y}^{7.4}
}
$$

For Entity $j$:

$$
(\mathbf{mne\text{-}allocable\text{-}share}^{ce})_j
=
\sum_{i=1}^{N}
(\mathbf{group\text{-}upe})_i
(\mathbf{Y}^{7.4})_{ij}.
$$

The group UPE indicator is used because the UPE remains the reference owner even where it is an EE and cannot itself apply the IIR.

### JV Subsidiary Investment Entity

For a JV Group, let

$$
\mathbf{jv\text{-}member}\in\{0,1\}^{N\times1}
$$

identify its JV and JV Subsidiaries.

Define the local Article 7.4 ownership matrices:

$$
\boxed{
\mathbf{X}^{7.4}
:=
m\bigl(
\mathbf{X}_0^{\mathrm{profit,treasury}}
\odot
\mathbf{R}^{7.4};
\mathbf{jv\text{-}member}
\bigr)
}
$$

$$
\boxed{
\mathbf{Y}^{7.4}
:=
f\bigl(\mathbf{X}^{7.4}\bigr)
}
$$

Let $\mathbf{jv}$ identify the JV of this JV Group. For each JV Subsidiary $j$ in the group, the MNE Group's Allocable Share is the Article 7.4-adjusted direct and indirect Profit Ownership Interest held by the JV in that JV Subsidiary:

$$
\boxed{
(\mathbf{mne\text{-}allocable\text{-}share}^{jv})_j
:=
\mathbf{jv}^T
\mathbf{Y}^{7.4}
\mathbf{e}_j
}
\qquad
\text{for }(\mathbf{jvsub})_j=1.
$$

This calculation is performed separately for each JV Group.

### UPE and JV Investment Entities

The Article 7.4 adjustment is not applied where the IE is itself:

- a UPE; or
- a JV rather than a JV Subsidiary.

The ordinary Net Income Inclusion Ratio applies in those cases.

### MNE Group's Allocable Share

Define:

$$
\mathbf{ie\text{-}ce}
:=
\mathbf{ie}
\odot
\mathbf{ce}
\odot
(\mathbf{1}_N-\mathbf{group\text{-}upe}),
\qquad
\mathbf{ie\text{-}jvsub}
:=
\mathbf{ie}\odot\mathbf{jvsub}.
$$

The combined allocable-share vector is:

$$
\boxed{
\mathbf{mne\text{-}allocable\text{-}share}
:=
\mathbf{ie\text{-}ce}
\odot
\mathbf{mne\text{-}allocable\text{-}share}^{ce}
+
\mathbf{ie\text{-}jvsub}
\odot
\mathbf{mne\text{-}allocable\text{-}share}^{jv}
}
$$

Define the adjustable IE indicator:

$$
\mathbf{ie\text{-}adjustable}
:=
\mathbf{ie\text{-}ce}\lor\mathbf{ie\text{-}jvsub}.
$$

For each Entity $j$, define:

$$
(\mathbf{factor}^{7.4})_j
:=
\begin{cases}
\dfrac{1}{(\mathbf{mne\text{-}allocable\text{-}share})_j},
&
(\mathbf{ie\text{-}adjustable})_j=1
\text{ and }
(\mathbf{mne\text{-}allocable\text{-}share})_j>0,
\\[8pt]
1,
&
\text{otherwise}.
\end{cases}
$$

The adjusted Net Income Inclusion Ratio is:

$$
\boxed{
\mathbf{Adjusted\text{-}net\text{-}iir}
:=
\mathbf{Net\text{-}iir}
\cdot
\operatorname{diag}(\mathbf{factor}^{7.4})
}
$$

Only CE IEs and JV Subsidiary IEs with a positive MNE Group's Allocable Share are scaled. All other columns remain unchanged.

## Allocation of Top-up Tax

Let:

$$
\mathbf{topup\text{-}tax}\in\mathbb{R}_{\ge0}^{N\times1}
$$

be derived from Relations.TopupTaxes. For this section, the Top-up Tax of an Article 7.4 IE is the amount already determined after applying the MNE Group's Allocable Share.

The final Parent-Entity-by-low-taxed-Entity allocation matrix is:

$$
\boxed{
\mathbf{Iir\text{-}topup\text{-}taxes}
:=
\left[
\mathbf{Net\text{-}iir}
\cdot
\operatorname{diag}(\mathbf{1}_N-\mathbf{ie\text{-}adjustable})
+
\mathbf{Adjusted\text{-}net\text{-}iir}
\cdot
\operatorname{diag}(\mathbf{ie\text{-}adjustable})
\right]
\cdot
\operatorname{diag}(\mathbf{topup\text{-}tax})
}
$$

Each Entity column therefore uses the ordinary Net Income Inclusion Ratio unless Article 7.4 applies, in which case it uses the adjusted ratio, before multiplying by that Entity's Top-up Tax. Each non-zero cell supplies top_up_tax_payable for the corresponding Relation.IncomeInclusions row.

# Implementation Notes

### 1. Prepare the Profit Ownership Graph

Remove treasury shares, mask the graph to the relevant member population, and call the imported ownership function to calculate direct and indirect Profit Ownership Interests.

### 2. Solve Each IIR-Payable Column

For each potential low-taxed Entity, select the payable Parent Entities and solve only the corresponding principal submatrix of $g(\mathbf{Y})$. Non-payable rows remain zero.

### 3. Calculate the Article 7.4 Allocable Share

Calculate CE IE ownership through the MNE Group graph and JV Subsidiary IE ownership through its own JV Group graph. Combine those results only for IEs to which the Article 7.4 adjustment applies.

### 4. Allocate Top-up Tax

Select the ordinary or Article 7.4-adjusted Net Income Inclusion Ratio for each Entity column, then multiply by that Entity's Top-up Tax.