# Interface

## Imports

- The Entity indicator vectors $\mathbf{ce}$, $\mathbf{ee}$, $\mathbf{ie}$, and $\mathbf{group\text{-}upe}$.
- The top-level JV and JV Subsidiary vectors $\mathbf{jv}$ and $\mathbf{jvsub}$ from [JV.md](<JV.md#calculation>).
- The direct Profit Ownership Interest matrix $\mathbf{X}_0^{\mathrm{profit}}$ from [Ownership Interest.md](<Ownership Interest.md#direct-ownership-matrix>).
- The Article 7.4 applicability fraction matrix $\mathbf{R}^{7.4}$.
- The Entity-level Top-up Tax vector $\mathbf{topup\text{-}tax}$ from [Top-up Tax Calculation](<Top-up Tax Calculation.md>).
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

The operator $\operatorname{diag}$ retains only the diagonal entries of a square matrix, or constructs a diagonal matrix from a vector. $\odot$ denotes element-wise multiplication; comparisons and logical operations are element-wise.

The Entity indicator vectors use the same Entity ordering as the matrices:

- $\mathbf{ce}$, $\mathbf{ee}$, and $\mathbf{ie}$ identify CEs, Excluded Entities, and Investment Entities, respectively.
- $\mathbf{group\text{-}upe}$ identifies the group's UPEs, independently of later calculation exclusions.
- $\mathbf{jv}$ and $\mathbf{jvsub}$ identify top-level JVs and JV Subsidiaries, respectively.

These indicators describe Entity characteristics before calculation-specific exclusions; CE and EE indicators must not overlap. $\mathbf{X}_0^{\mathrm{profit}}$ has owning Entities on rows and Entities owned on columns.

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

No treasury-share removal is needed: $f$ and $h$ keep treasury shares on the diagonal and gross up the other holders' interests themselves.

## Imported IIR Payability

A non-zero element

$$
(\mathbf{Iir\text{-}payable})_{ij}=1
$$

means that Parent Entity $i$ may apply the IIR to potential low-taxed Entity $j$ for the current fiscal year. Parent Entity identification, jurisdictional implementation conditions, and the top-down and split-ownership priority rules are calculated in [Taxing Rights.md](<Taxing Rights.md#iir-payability>).

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
m\bigl(\mathbf{X}_0^{\mathrm{profit}};\mathbf{member}\bigr)
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

#### Circular Holdings Between Parent Entities

An earlier version computed a non-qualified Parent Entity $i$'s ratio as $\left[\mathbf{Y}_{ij}-\sum_{k\ne i}\mathbf{Y}_{ik}(\mathbf{Net\text{-}iir}^{Q})_{kj}\right]^{+}$. Without circular holdings this equals $(\mathbf{H})_{ij}$. Where $i$ and a qualified Parent Entity $k$ below it hold each other, the sum also subtracts paths that leave $i$ and return to $i$ before reaching $j$, which $\mathbf{Y}_{ij}$ never counted. For example, if $i$ holds 60% of $k$, $k$ holds 50% of $i$, and $i$ holds 100% of $j$, the earlier formula gives 70% and $\mathbf{H}_{ij}=100\%$. $\mathbf{H}$ treats $i$'s indirect holding of itself the same way $f$ does. $\mathbf{H}\ge0$, so no truncation is needed.

## Investment Entity Special Rule

Article 7.4 applies to the GloBE Income or Loss remaining at the Investment Entity after any allocation required under Article 3.5.

### Article 7.4 Applicability Matrix

Let:

$$
\mathbf{R}^{7.4}\in[0,1]^{N\times N}
$$

be given as an input. The scalar $(\mathbf{R}^{7.4})_{ij}$ is the proportion of Entity $i$'s direct Profit Ownership Interest in Entity $j$ that remains subject to Article 7.4: 1 means the entire interest is subject to Article 7.4 and 0 means none of it is. The entry is 0 unless Entity $j$ is an Investment Entity.

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
m\bigl(
\mathbf{X}_0^{\mathrm{profit}}
\odot
g(\mathbf{R}^{7.4});
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
\mathbf{X}_0^{\mathrm{profit}}
\odot
g(\mathbf{R}^{7.4});
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

be the Entity-level Top-up Tax determined in [Top-up Tax Calculation](<Top-up Tax Calculation.md>); every entry is finite and non-negative. For this section, the Top-up Tax of an Article 7.4 IE is the amount already determined after applying the MNE Group's Allocable Share.

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

Each Entity column therefore uses the ordinary Net Income Inclusion Ratio unless Article 7.4 applies, in which case it uses the adjusted ratio, before multiplying by that Entity's Top-up Tax. Each non-zero cell supplies top_up_tax_payable for the corresponding IncomeInclusions row.

# Implementation Notes

### 1. Prepare the Profit Ownership Graph

Mask the graph to the members. Treasury shares stay on the diagonal; $f$ and $h$ handle them.

### 2. Solve Each IIR-Payable Column

For each potential low-taxed Entity $j$ with a payable Parent Entity, cut the columns of the Parent Entities with $\mathbf{Q}_{ij}=1$, restrict the graph to $j$ and its direct and indirect owners, and solve column $j$ of $\mathbf{H}$ as in [Ownership Interest](<Ownership Interest.md#implementation>). Columns without a payable Parent Entity are zero.

### 3. Calculate the Article 7.4 Allocable Share

Calculate CE IE ownership through the MNE Group graph and JV Subsidiary IE ownership through its own JV Group graph. Combine those results only for IEs to which the Article 7.4 adjustment applies.

### 4. Allocate Top-up Tax

Select the ordinary or Article 7.4-adjusted Net Income Inclusion Ratio for each Entity column, then multiply by that Entity's Top-up Tax.
