# Interface

## Imports

- The Entity indicator vectors $\mathbf{ce}$, $\mathbf{ee}$, $\mathbf{ie}$, and $\mathbf{group\text{-}upe}$, before any calculation-specific exclusion; $\mathbf{group\text{-}upe}$ includes a UPE that is an Excluded Entity.
- The top-level JV and JV Subsidiary vectors $\mathbf{jv}$ and $\mathbf{jvsub}$ from [Subgroups.md](<Subgroups.md#jv-groups>).
- The direct Profit Ownership Interest matrix $\mathbf{X}_0^{\mathrm{profit}}$ from [Ownership Interest.md](<Ownership Interest.md#direct-ownership-matrix>).
- The Article 7.4 applicability fraction matrix $\mathbf{R}^{7.4}$.
- The Top-up Tax of each Entity, $\mathbf{tt\text{-}entt}$, from [Top-up Tax Calculation](<Top-up Tax Calculation.md>).
- The direct and indirect Ownership Interest function $f(\mathbf{A})$ from [Ownership Interest.md](<Ownership Interest.md#direct-method>).
- The cut ownership function $h(\mathbf{A};\mathbf{S})$ from [Ownership Interest.md](<Ownership Interest.md#ownership-with-absorbing-parent-entities>).
- The current-year IIR payability matrix $\mathbf{Iir\text{-}payable}$ from [Taxing Rights.md](<Taxing Rights.md#iir-payability>).
- The vector $\mathbf{qiir}\in\{0,1\}^{N\times1}$ of Entities located in a jurisdiction with a Qualified IIR in force, from [Taxing Rights.md](<Taxing Rights.md>).

## Exports

### IIR Allocation Results

This document calculates the Gross Income Inclusion Ratio, IIR Offset, Net Income Inclusion Ratio, Article 7.4-adjusted Net Income Inclusion Ratio, and IIR Top-up Tax allocated to each Parent Entity.

Each non-zero Parent-Entity-by-low-taxed-Entity cell of the result is reported as:

**IncomeInclusions**

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

- All imported vectors and matrices must use the same fiscal year and Entity ordering.

## Domain Validation

- $\mathbf{X}_0^{\mathrm{profit}}$ passes the [Ownership Interest validation](<Ownership Interest.md#validation>); in particular no Entity holds 100% of its own Profit Ownership Interests.
- $\mathbf{ce}\land\mathbf{ee}=\mathbf{0}_N$.

# Operation

$\operatorname{diag}$ retains the diagonal of a square matrix or builds a diagonal matrix from a vector. $\odot$ denotes element-wise multiplication; comparisons and logical operations are element-wise.

## Unit-Diagonal Function

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

$(\mathbf{Iir\text{-}payable})_{ij}=1$ means that Parent Entity $i$ may apply the IIR to potential low-taxed Entity $j$ for the current fiscal year. Parent Entity identification, jurisdictional implementation conditions, and the top-down and split-ownership priority rules are calculated in [Taxing Rights.md](<Taxing Rights.md#iir-payability>).

## Income Inclusion Ratio

### Ownership Graph

Retain CEs, Excluded Entities and members of a JV Group:

$$
\mathbf{member}
:=
\mathbf{ce}\lor\mathbf{ee}\lor\mathbf{jv}\lor\mathbf{jvsub}.
$$

Excluded Entities stay in the graph. They are not Parent Entities and are never payable, but they are Group Entities consolidated in the UPE's financial statements, so an interest a Parent Entity or a UPE holds through one is still its interest. Removing them would cut every chain that runs through them: a UPE that is itself an Excluded Entity would hold nothing, and the Entities below an Excluded Entity would escape the UTPR (Article 2.5.2; Commentary on Article 2.1.3 ¶18). Entities outside the group are left out.

For the ordinary IIR calculation, mask the direct Profit Ownership Interest matrix to the members:

$$
\boxed{
\mathbf{X}
:=
\operatorname{diag}(\mathbf{member})\,\mathbf{X}_0^{\mathrm{profit}}\operatorname{diag}(\mathbf{member})
}
$$

Treasury shares stay on the diagonal of $\mathbf{X}$. For example, if an Entity holds 20% of its own Profit Ownership Interests and another Entity holds the remaining 80%, $f$ treats the other holder as holding 100% of the outstanding interests.

The corresponding direct and indirect Profit Ownership Interest matrix is abbreviated as:

$$
\boxed{
\mathbf{Y}
:=
f(\mathbf{X})
}
$$

These aliases are used throughout the ordinary IIR derivation below. The aliases $\mathbf{X}$ and $\mathbf{Y}$ apply only to the ordinary IIR calculation; Article 7.4 uses separately labelled ownership matrices.

### Net Income Inclusion Ratio

Article 2.3.2 reduces a Parent Entity's Allocable Share by the part brought into charge by a lower Parent Entity **under a Qualified IIR**. A charge under an IIR that is not qualified offsets nothing. The Parent Entities payable under a Qualified IIR are therefore the absorbing Parent Entities:

$$
\mathbf{Q}:=\operatorname{diag}(\mathbf{qiir})\times\mathbf{Iir\text{-}payable}
$$

$$
\boxed{
\begin{aligned}
\mathbf{H}&:=h(\mathbf{X};\mathbf{Q})\\
\mathbf{Net\text{-}iir}^{Q}&:=\mathbf{H}\odot\mathbf{Q}\\
\mathbf{Net\text{-}iir}&:=\mathbf{H}\odot\mathbf{Iir\text{-}payable}
\end{aligned}
}
$$

$(\mathbf{H})_{ij}$ is Entity $i$'s interest in Entity $j$ that does not pass through a Parent Entity payable for $j$ under a Qualified IIR.

- A Parent Entity under a Qualified IIR is offset only by Qualified IIRs below it, and offsets the Parent Entities above it: it absorbs.
- A Parent Entity under an IIR that is not qualified is also offset only by Qualified IIRs below it, and never offsets anyone: it does not absorb.
- Where every payable Parent Entity is qualified, $\mathbf{Q}=\mathbf{Iir\text{-}payable}$ and $\mathbf{Net\text{-}iir}=\mathbf{Net\text{-}iir}^{Q}$.

**Net Income Inclusion Ratio** is a modelling term for the portion of the Inclusion Ratio remaining after the IIR Offset Mechanism. The ratio before the offset mechanism, and the offset, are:

$$
\mathbf{Gross\text{-}iir}
:=
\mathbf{Y}
\odot
\mathbf{Iir\text{-}payable},
\qquad
\mathbf{Iir\text{-}offset}
:=
\mathbf{Gross\text{-}iir}-\mathbf{Net\text{-}iir}.
$$

#### Iterative Reading

For each potential low-taxed Entity $j$, start one unit of unpaid interest at $j$ and pass it up the ownership structure one level per step. At a Parent Entity with $\mathbf{Q}_{ij}=1$ it is paid; everywhere else it moves on:

$$
\begin{aligned}
\mathbf{Iir\text{-}paid}_0&:=\mathbf{0}_{N\times N},\qquad
\mathbf{Iir\text{-}unpaid}_0:=\mathbf{I}_N\\
\mathbf{Iir\text{-}paid}_{q+1}&:=\mathbf{Iir\text{-}paid}_{q}+\left(\mathbf{X}\cdot\mathbf{Iir\text{-}unpaid}_{q}\right)\odot\mathbf{Q}\\
\mathbf{Iir\text{-}unpaid}_{q+1}&:=\left(\mathbf{X}\cdot\mathbf{Iir\text{-}unpaid}_{q}\right)\odot(\mathbf{1}_{N\times N}-\mathbf{Q})
\end{aligned}
$$

and $\lim_{q\to\infty}\mathbf{Iir\text{-}paid}_q=\mathbf{Net\text{-}iir}^{Q}$. The diagonal of $\mathbf{X}$ returns treasury shares to the unpaid interest of the same Entity, which grosses up its other holders.

#### Calculation from Y

$\mathbf{H}$ follows from $\mathbf{Y}$ by the [correction form](<Ownership Interest.md#correction-form>). For Entity $j$, let $\mathcal{S}_j$ be the Parent Entities with $(\mathbf{Q})_{kj}=1$ and $\mathbf{N}_j:=g(\mathbf{Y})_{\mathcal{S}_j\mathcal{S}_j}^{-1}\mathbf{Y}_{\mathcal{S}_j,:}$. Then

$$
\boxed{
\begin{aligned}
(\mathbf{Net\text{-}iir}^{Q})_{kj}&=(\mathbf{N}_j)_{kj}, && k\in\mathcal{S}_j,\\
(\mathbf{H})_{pj}&=\frac{(\mathbf{Y})_{pj}-\sum_{k\in\mathcal{S}_j}(\mathbf{Y})_{pk}(\mathbf{Net\text{-}iir}^{Q})_{kj}}{1-\sum_{k\in\mathcal{S}_j}(\mathbf{Y})_{pk}(\mathbf{N}_j)_{kp}}, && p\notin\mathcal{S}_j,\ p\ne j.
\end{aligned}
}
$$

The numerator is $p$'s Allocable Share less the part brought into charge by a Parent Entity in $\mathcal{S}_j$ below it. The denominator is 1 unless $p$ and a Parent Entity in $\mathcal{S}_j$ hold each other.

#### Circular Holdings Between Parent Entities

Where $p$ and a Parent Entity $k\in\mathcal{S}_j$ below it hold each other, part of what $k$ brings into charge reaches $k$ through $p$ itself. That part is $p$'s interest in itself, and the denominator grosses $p$'s remaining interest up by it.

For example, $p$ holds 60% of $k$, $k$ holds 50% of $p$, $p$ holds 100% of $j$, and $k$ pays under a Qualified IIR. $k$ holds 50% of $j$ through $p$, and $p$'s share of it through $k$ is $0.6\times0.5=30\%$. Every such path runs $p\to k\to p\to j$: it is $p$'s 30% interest in itself, not an interest in $j$ held by $k$ apart from $p$. So

$$
(\mathbf{H})_{pj}=\frac{1-0.6\times0.5}{1-0.6\times0.5}=100\%.
$$

## Investment Entity Special Rule

Article 7.4 applies to the GloBE Income or Loss remaining at the Investment Entity after any allocation required under Article 3.5.

### Article 7.4 Applicability Matrix

Let:

$$
\mathbf{R}^{7.4}\in[0,1]^{N\times N}
$$

be given as an input. For an Investment Entity $j$, the scalar $(\mathbf{R}^{7.4})_{ij}$ is the proportion of Entity $i$'s direct Profit Ownership Interest in Entity $j$ that remains subject to Article 7.4: 1 means the entire interest is subject to Article 7.4 and 0 means none of it is. For every other Entity $j$ the entry is 1, so that interests held through Entities that are not Investment Entities count in full.

For example, if the UPE holds 100% of a holding company that holds 60% of an Investment Entity, the UPE's Article 7.4 interest in the Investment Entity is 60%.

The fraction is applied to the direct Profit Ownership Interest matrix before the direct and indirect Ownership Interest function $f$ is evaluated. $g$ keeps the treasury shares on the diagonal at their full ratio. The resulting Article 7.4 ownership graphs are used only to determine the MNE Group's Allocable Share.

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
\operatorname{diag}(\mathbf{mne\text{-}member})
\left(\mathbf{X}_0^{\mathrm{profit}}\odot g(\mathbf{R}^{7.4})\right)
\operatorname{diag}(\mathbf{mne\text{-}member})
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

The group UPE indicator is used because the UPE remains the reference owner even where it is an EE and cannot itself apply the IIR.

Only the rows of the group UPEs are used, so $\mathbf{Y}^{7.4}$ is not formed in full: each row is a [Row Calculation](<Ownership Interest.md#row-calculation>) with $\mathbf{A}=\mathbf{X}^{7.4}$.

### JV Subsidiary Investment Entity

For a JV Group, let $\mathbf{jv\text{-}member}$ identify its JV and JV Subsidiaries.

Define the local Article 7.4 ownership matrices:

$$
\boxed{
\mathbf{X}^{7.4}
:=
\operatorname{diag}(\mathbf{jv\text{-}member})
\left(\mathbf{X}_0^{\mathrm{profit}}\odot g(\mathbf{R}^{7.4})\right)
\operatorname{diag}(\mathbf{jv\text{-}member})
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

This calculation is performed separately for each JV Group. Only the JV's row of $\mathbf{Y}^{7.4}$ is used, computed by [Row Calculation](<Ownership Interest.md#row-calculation>).

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

For an Article 7.4 IE, $\mathbf{tt\text{-}entt}$ is the amount already determined after applying the MNE Group's Allocable Share.

The final Parent-Entity-by-low-taxed-Entity allocation matrix is:

$$
\boxed{
\mathbf{Iir\text{-}topup\text{-}taxes}
:=
\mathbf{Adjusted\text{-}net\text{-}iir}
\cdot
\operatorname{diag}(\mathbf{tt\text{-}entt})
}
$$

$\mathbf{Adjusted\text{-}net\text{-}iir}$ equals $\mathbf{Net\text{-}iir}$ in every column to which Article 7.4 does not apply, so each Entity column uses the right ratio. Each non-zero cell supplies top_up_tax_payable for the corresponding IncomeInclusions row.

# Implementation Notes

### 1. Prepare the Profit Ownership Graph

Mask the graph to the members. Treasury shares stay on the diagonal; $f$ and $h$ handle them.

### 2. Correct $\mathbf{Y}$ for Each IIR-Payable Column

Group the potential low-taxed Entities by their set $\mathcal{S}_j$. For each group, factorize $g(\mathbf{Y})_{\mathcal{S}_j\mathcal{S}_j}$ once and read $\mathbf{Net\text{-}iir}^{Q}$ and $\mathbf{H}$ from $\mathbf{Y}$ as [above](#calculation-from-y). Columns without a Parent Entity payable under a Qualified IIR equal $\mathbf{Y}$.

### 3. Calculate the Article 7.4 Allocable Share

Solve one [row](<Ownership Interest.md#row-calculation>) of the MNE Group's Article 7.4 graph for each group UPE, and one row of each JV Group's Article 7.4 graph for its JV. Combine those results only for IEs to which the Article 7.4 adjustment applies.

### 4. Allocate Top-up Tax

Multiply each column of the Article 7.4-adjusted Net Income Inclusion Ratio by that Entity's Top-up Tax.
