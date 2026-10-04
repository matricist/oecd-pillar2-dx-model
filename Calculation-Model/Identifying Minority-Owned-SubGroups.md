# Interface

## Imports

- [`Relations.CompanyEntities`](<Relations.md#companyentities>).
- [`Relations.ConstituentEntities`](<Relations.md#constituententities>).
- [`Relations.InvestmentEntities`](<Relations.md#investmententities>).
- [`Relations.JvEntities`](<Relations.md#jventities>).
- The direct and indirect Ownership Interest function $f(\mathbf{A})$ from [Ownership Interest.md](<Ownership Interest.md#exports>).
- `calculate_controlling_interest(C0)` from [Controlling Interest.md](<Controlling Interest.md#exports>).
- The JV Group membership matrix $\mathbf{J}$ from [Identifying Joint Venture Groups.md](<Identifying Joint Venture Groups.md#exports>).
- Common Entity indicator names from [Definition.md](<Definition.md#common-entity-indicator-vectors>).

## Exports

### Minority-Owned Subgroup Identification Function

This document defines and exports `identify_minority_owned_subgroups` for use throughout the Calculation Model.

- **Input:** The direct Ownership Interest Ratio matrix $\mathbf{X}_0$, the confirmed direct Controlling Interest matrix $\mathbf{C}_0$, the JV Group membership matrix $\mathbf{J}$, and the Entity indicators described below.
- **Output:** The MOCE candidate vector $\mathbf{mocec}$, MOPE vector $\mathbf{mope}$, Minority-Owned Subsidiary vector $\mathbf{mos}$, Single MOCE vector $\mathbf{smoce}$, final MOCE vector $\mathbf{moce}$, and MOSG membership matrix $\mathbf{Mosg}$.
- **Relation output:** The function produces [`Relations.MinorityOwnedEntities`](<Relations.md#minorityownedentities>). For a MOPE or Single MOCE, `minority_owned_group_id` is its own `entity_id`; for a Minority-Owned Subsidiary, it is the `entity_id` of its top-level MOPE.

# Validation

## Structural Validation

- All input matrices and vectors must use the same Entity ordering and fiscal year.
- $\mathbf{X}_0$, $\mathbf{C}_0$, and $\mathbf{J}$ must be square $N\times N$ matrices.
- The Ownership Interest, Controlling Interest, and JV Group calculations must pass their respective validation rules before this calculation is performed.

## Domain Validation

- Every Entity identified by $\mathbf{group\text{-}upe}$ must also be identified by $\mathbf{ce}$.
- An Entity must not be both an ordinary CE of the MNE Group and a member of a JV Group for the same fiscal year.
- Each row of $\mathbf{J}$ represents a top-level JV and each column belongs to at most one JV Group, as required by Identifying Joint Venture Groups.md.

## Runtime Validation

Each MOCE may belong to at most one MOSG. If a column of $\mathbf{Mosg}$ contains more than one true value, raise a **Runtime Validation Error** rather than selecting a MOPE arbitrarily.

# Operation

## Notation

As in Ownership Interest.md, bold uppercase symbols denote matrices, bold lowercase names denote column vectors, and calligraphic symbols denote sets. Indices and individual vector or matrix entries are scalars. Existing model names such as `mocec`, `mope`, `mos`, and `smoce` are preserved.

| Symbol | Type and meaning |
|---|---|
| $\mathcal{V}=\{1,\ldots,N\}$ | Set of Entity indices. |
| $\mathbf{X}_0\in[0,1]^{N\times N}$ | Direct Ownership Interest Ratio matrix. |
| $\mathbf{Y}=f(\mathbf{X}_0)\in[0,1]^{N\times N}$ | Direct and indirect Ownership Interest Ratio matrix. |
| $\mathbf{C}_0\in\{0,1\}^{N\times N}$ | Confirmed direct Controlling Interest matrix. |
| $\mathbf{C}\in\{0,1\}^{N\times N}$ | Confirmed direct and indirect Controlling Interest matrix. |
| $\mathbf{J}\in\{0,1\}^{N\times N}$ | JV Group membership matrix, with top-level JVs on rows and member Entities on columns. |
| $\mathbf{group\text{-}upe}\in\{0,1\}^{N\times1}$ | Indicator vector for the UPE or UPEs of the MNE Group. |
| $\mathbf{ce}\in\{0,1\}^{N\times1}$ | CE indicator vector. |
| $\mathbf{ie}\in\{0,1\}^{N\times1}$ | IE indicator vector. |
| $\mathbf{jv}\in\{0,1\}^{N\times1}$ | Top-level JV indicator vector. |
| $\mathbf{jvsub}\in\{0,1\}^{N\times1}$ | JV Subsidiary indicator vector. |
| $\mathbf{S}\in\{0,1\}^{N\times N}$ | Same calculation-group scope matrix. |
| $\mathbf{mocec}\in\{0,1\}^{N\times1}$ | MOCE candidate indicator vector. |
| $\mathbf{mope}\in\{0,1\}^{N\times1}$ | MOPE indicator vector. |
| $\mathbf{mos}\in\{0,1\}^{N\times1}$ | Minority-Owned Subsidiary indicator vector. |
| $\mathbf{smoce}\in\{0,1\}^{N\times1}$ | Single MOCE indicator vector. |
| $\mathbf{moce}\in\{0,1\}^{N\times1}$ | Final calculation-purpose MOCE indicator vector. |
| $\mathbf{Mosg}\in\{0,1\}^{N\times N}$ | MOSG membership matrix, with top-level MOPEs on rows and group members on columns. |
| $\mathbf{1}_N$ | Length-$N$ vector of ones. |
| $\mathbf{I}_N$ | $N\times N$ identity matrix. |

All Boolean matrix operations below use logical AND for multiplication and logical OR for addition. The symbol $\odot$ denotes element-wise multiplication. Comparisons are evaluated element-wise.

## Identifying MOCE Candidates

A MOCE candidate is identified against the UPE of the calculation group to which it belongs:

- an ordinary CE is tested using the aggregate direct and indirect Ownership Interests held by the UPE or UPEs of the MNE Group; and
- a JV Subsidiary is tested using the direct and indirect Ownership Interests held by the top-level JV of its JV Group, because that JV is treated as the UPE of a separate MNE Group for this purpose.

First derive the JV indicators from $\mathbf{J}$:

$$
\mathbf{jv}
:=
\mathbf{1}_{\{\operatorname{diag}(\mathbf{J})=1\}},
\qquad
\mathbf{jvmember}
:=
\mathbf{1}_{\{\mathbf{J}^{T}\mathbf{1}_N>0\}},
\qquad
\mathbf{jvsub}
:=
\mathbf{jvmember}\odot(\mathbf{1}_N-\mathbf{jv}).
$$

The aggregate UPE ownership of each Entity is

$$
\mathbf{upe\text{-}ownership}
:=
\mathbf{Y}^{T}\mathbf{group\text{-}upe}.
$$

An ordinary CE candidate must be a CE outside a JV Group, must not itself be a group UPE, and must have aggregate UPE ownership of 30% or less:

$$
\mathbf{moce\text{-}ce}
:=
\mathbf{ce}
\odot(\mathbf{1}_N-\mathbf{jvmember})
\odot(\mathbf{1}_N-\mathbf{group\text{-}upe})
\odot\mathbf{1}_{\{\mathbf{upe\text{-}ownership}\le0.30\}}.
$$

Because each column of $\mathbf{J}$ belongs to at most one JV Group, the top-level JV ownership of each group member is

$$
\mathbf{jv\text{-}ownership}
:=
(\mathbf{J}\odot\mathbf{Y})^{T}\mathbf{1}_N.
$$

A JV Subsidiary candidate must have top-level JV ownership of 30% or less:

$$
\mathbf{moce\text{-}jvsub}
:=
\mathbf{jvsub}
\odot\mathbf{1}_{\{\mathbf{jv\text{-}ownership}\le0.30\}}.
$$

The two populations are disjoint, so the complete candidate vector is

$$
\mathbf{mocec}
:=
\mathbf{moce\text{-}ce}\lor\mathbf{moce\text{-}jvsub}.
$$

## Restricting the Calculation Scope

MOCEs in the main MNE Group and MOCEs in each deemed JV MNE Group must be tested separately. Define the ordinary CE population outside JV Groups as

$$
\mathbf{ordinary\text{-}ce}
:=
\mathbf{ce}\odot(\mathbf{1}_N-\mathbf{jvmember}).
$$

The same calculation-group scope matrix is

$$
\mathbf{S}
:=
(\mathbf{ordinary\text{-}ce}\mathbf{ordinary\text{-}ce}^{T})
\lor
(\mathbf{J}^{T}\mathbf{J}),
$$

where both products are evaluated over the Boolean semiring. Thus, $(\mathbf{S})_{ij}=1$ when Entities $i$ and $j$ are both ordinary CEs of the main MNE Group or belong to the same JV Group.

## Identifying Top-Level MOPEs

Restrict the controlling-interest matrix to relationships between MOCE candidates:

$$
\mathbf{C}_{\mathrm{moce}}
:=
\operatorname{diag}(\mathbf{mocec})
\mathbf{C}
\operatorname{diag}(\mathbf{mocec})
\odot\mathbf{S}.
$$

A MOPE candidate is a MOCE candidate that directly or indirectly controls at least one other MOCE candidate:

$$
\mathbf{mopec}
:=
\mathbf{1}_{\{\mathbf{C}_{\mathrm{moce}}\mathbf{1}_N>0\}}.
$$

A top-level MOPE must not itself be controlled by another MOCE candidate:

$$
\mathbf{controlled\text{-}moce}
:=
\mathbf{1}_{\{\mathbf{C}_{\mathrm{moce}}^{T}\mathbf{1}_N>0\}},
$$

$$
\mathbf{mope}
:=
\mathbf{mopec}\odot(\mathbf{1}_N-\mathbf{controlled\text{-}moce}).
$$

Using the transitive closure $\mathbf{C}$ ensures that only the highest MOCE in a control chain is selected as the MOPE.

## Constructing Minority-Owned Subgroups

Each MOSG contains its top-level MOPE and every MOCE candidate that it directly or indirectly controls:

$$
\mathbf{Mosg}
:=
\operatorname{diag}(\mathbf{mope})
(\mathbf{I}_N\lor\mathbf{C})
\operatorname{diag}(\mathbf{mocec})
\odot\mathbf{S}.
$$

Accordingly, $(\mathbf{Mosg})_{ij}=1$ if and only if Entity $i$ is a top-level MOPE and Entity $j$ is either that MOPE or a MOCE candidate controlled by it.

Before assigning group IDs, validate

$$
\forall j\in\mathcal{V}:\qquad
\sum_{i\in\mathcal{V}}(\mathbf{Mosg})_{ij}\le1.
$$

The Minority-Owned Subsidiary vector includes the non-root members of these groups:

$$
\mathbf{mos}
:=
\mathbf{1}_{\{\mathbf{Mosg}^{T}\mathbf{1}_N>0\}}
\odot(\mathbf{1}_N-\mathbf{mope}).
$$

## Identifying Single MOCEs

A candidate outside every MOSG is a Single MOCE unless it is an Investment Entity. A standalone Investment Entity remains in the Investment Entity calculation group instead of forming a separate MOCE calculation group:

$$
\mathbf{smoce}
:=
\mathbf{mocec}
\odot(\mathbf{1}_N-\mathbf{mope})
\odot(\mathbf{1}_N-\mathbf{mos})
\odot(\mathbf{1}_N-\mathbf{ie}).
$$

The final calculation-purpose MOCE classification is the disjoint union

$$
\mathbf{moce}
:=
\mathbf{mope}\lor\mathbf{mos}\lor\mathbf{smoce}.
$$

To create `MinorityOwnedEntities`, scan the true elements of $\mathbf{Mosg}$ and assign each column Entity to the row Entity that represents its MOPE. Then add every Entity identified by $\mathbf{smoce}$ with its own `entity_id` as `minority_owned_group_id`.
