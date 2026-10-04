# Interface

## Imports

- Relations.CompanyEntities
- Relations.ConstituentEntities
- Relations.ExcludedEntities
- Relations.DirectOwnershipInterests
- Relations.DirectControllingInterests
- The direct and indirect Ownership Interest function $f(\mathbf{A})$ from [Ownership Interest.md](<Ownership Interest.md#exports>).
- `calculate_controlling_interest(C0)` from [Controlling Interest.md](<Controlling Interest.md#exports>).
- Common Entity indicator names from [Definition.md](<Definition.md#common-entity-indicator-vectors>).

## Exports

### Joint Venture Group Identification Function

This document defines and exports `identify_joint_venture_groups` for use throughout the Calculation Model.

- **Input:** The direct Ownership Interest Ratio matrix $\mathbf{X}_0$, the confirmed direct Controlling Interest matrix $\mathbf{C}_0$, and the Entity indicators described below, including the combined JV exclusion vector $\mathbf{jv\text{-}excluded}$.
- **Output:** The JV candidate vector $\mathbf{jvc}$, top-level JV vector $\mathbf{jv}$, JV Subsidiary vector $\mathbf{jvsub}$, and JV Group membership matrix $\mathbf{J}$.
- **Relation output:** Each true element $(\mathbf{J})_{ij}$ produces a row in `Relations.JvEntities` for member Entity $j$, with Entity $i$ as its `jv_group_id`. The row records `is_jv == true` when $i=j$ and `is_jv_sub == true` otherwise.

# Validation

## Structural Validation

- All input matrices and vectors must use the same Entity ordering and fiscal year.
- $\mathbf{X}_0$ and $\mathbf{C}_0$ must be square $N\times N$ matrices.
- The Ownership Interest and Controlling Interest calculations must pass their respective validation rules before this calculation is performed.

## Domain Validation

- The calculation population must represent one MNE Group, including all UPEs of that group where it is a Multi-Parented MNE Group.
- Every Entity identified by $\mathbf{group\text{-}upe}$ must also be identified by $\mathbf{ce}$.
- An equity-method Entity must not be a CE of the same MNE Group.
- $\mathbf{jv\text{-}excluded}$ must combine all four exclusions described under the JV Exclusion Mask below. Each component must be determined for the same MNE Group, fiscal year, and Entity ordering as the other inputs.

## Runtime Validation

The current `JvEntities` relation assigns at most one `jv_group_id` to each Entity. If an Entity belongs to more than one row of $\mathbf{J}$, raise a **Runtime Validation Error** rather than selecting a JV Group arbitrarily.

# Operation

## Notation

As in Ownership Interest.md, bold uppercase symbols denote matrices, bold lowercase names denote column vectors, and calligraphic symbols denote sets. Indices and individual vector or matrix entries are scalars. Existing model names such as `group-upe`, `jvc`, `jv`, and `jvsub` are preserved.

| Symbol | Type and meaning |
|---|---|
| $\mathcal{V}=\{1,\ldots,N\}$ | Set of Entity indices. |
| $\mathbf{X}_0\in[0,1]^{N\times N}$ | Direct Ownership Interest Ratio matrix. |
| $\mathbf{Y}=f(\mathbf{X}_0)\in[0,1]^{N\times N}$ | Direct and indirect Ownership Interest Ratio matrix. |
| $\mathbf{C}_0\in\{0,1\}^{N\times N}$ | Confirmed direct Controlling Interest matrix. |
| $\mathbf{C}\in\{0,1\}^{N\times N}$ | Confirmed direct and indirect Controlling Interest matrix. |
| $\mathbf{group\text{-}upe}\in\{0,1\}^{N\times1}$ | Indicator vector for the UPE or UPEs of the relevant MNE Group. |
| $\mathbf{ce}\in\{0,1\}^{N\times1}$ | CE indicator vector. |
| $\mathbf{eqt}\in\{0,1\}^{N\times1}$ | Equity-method Entity indicator vector derived from `CompanyEntities.is_equity_method`. |
| $\mathbf{jv\text{-}excluded}\in\{0,1\}^{N\times1}$ | Combined indicator vector for Entities excluded from JV candidacy before testing JV Subsidiary status. |
| $\mathbf{jvc}\in\{0,1\}^{N\times1}$ | JV candidate indicator vector. |
| $\mathbf{jv}\in\{0,1\}^{N\times1}$ | Top-level JV indicator vector. |
| $\mathbf{jvsub}\in\{0,1\}^{N\times1}$ | JV Subsidiary indicator vector. |
| $\mathbf{J}\in\{0,1\}^{N\times N}$ | JV Group membership matrix, with JV Groups on rows and member Entities on columns. |
| $i,j,k,N$ | Scalar Entity indices or Entity count. |
| $(\mathbf{Y})_{ij},(\mathbf{C})_{ij},(\mathbf{J})_{ij}$ | Scalar matrix entries. |

All Boolean matrix operations below use logical AND for multiplication and logical OR for addition. The symbol $\odot$ denotes element-wise multiplication.

## JV Exclusion Mask

Combine the following four exclusions into one indicator vector:

1. a UPE of another MNE Group that is subject to the GloBE Rules;
2. an Excluded Entity under Article 1.5.1;
3. an Entity whose Ownership Interests held by the MNE Group are held directly through an Article 1.5.1 Excluded Entity, where the Entity satisfies the applicable asset-holding, ancillary-activity, or excluded-income condition; and
4. an Entity held by an MNE Group composed exclusively of Excluded Entities.

Define the respective indicator vectors as $\mathbf{other\text{-}upe}$, $\mathbf{article\text{-}1.5.1\text{-}ee}$, $\mathbf{excluded\text{-}entity\text{-}held}$, and $\mathbf{all\text{-}ee\text{-}group\text{-}held}$. Then

$$
\mathbf{jv\text{-}excluded}
:=
\mathbf{other\text{-}upe}
\lor
\mathbf{article\text{-}1.5.1\text{-}ee}
\lor
\mathbf{excluded\text{-}entity\text{-}held}
\lor
\mathbf{all\text{-}ee\text{-}group\text{-}held}.
$$

The name `jv-excluded` is used because the combined vector includes Entities that are ineligible for JV treatment without necessarily being Excluded Entities themselves.

## Identifying JV Candidates

An Entity is a JV candidate when all of the following conditions are satisfied:

1. its financial results are reported under the equity method; and
2. the UPE or UPEs of the relevant MNE Group hold, in aggregate, at least 50% of its Ownership Interests, directly or indirectly; and
3. it is not identified by $\mathbf{jv\text{-}excluded}$.

The aggregate UPE ownership vector is

$$
\mathbf{upe\text{-}ownership}
:=
\mathbf{Y}^{T}\mathbf{group\text{-}upe}.
$$

Its scalar entry is

$$
\text{upe-ownership}_j
=
\sum_{i\in\mathcal{V}}
\text{group-upe}_i(\mathbf{Y})_{ij}.
$$

The JV candidate vector is therefore

$$
\mathbf{jvc}
:=
\mathbf{eqt}
\odot
\mathbf{1}_{\{\mathbf{upe\text{-}ownership}\ge0.5\}}
\odot
(\mathbf{1}_N-\mathbf{jv\text{-}excluded}),
$$

where the inequality is evaluated element-wise.

## Identifying Top-Level JVs and JV Subsidiaries

Compute the direct and indirect Controlling Interest matrix using the function exported by Controlling Interest.md:

$$
\mathbf{C}
:=
\operatorname{calculate\_controlling\_interest}(\mathbf{C}_0).
$$

An Entity is a JV Subsidiary candidate if it is directly or indirectly controlled by at least one JV candidate:

$$
\mathbf{jvsub}
:=
\mathbf{1}_{\{\mathbf{C}^{T}\mathbf{jvc}>0\}}.
$$

Thus, $\text{jvsub}_j=1$ if there exists an Entity $i$ such that $\text{jvc}_i=1$ and $(\mathbf{C})_{ij}=1$.

A top-level JV is a JV candidate that is not itself controlled by another JV candidate:

$$
\mathbf{jv}
:=
\mathbf{jvc}\odot(\mathbf{1}_N-\mathbf{jvsub}).
$$

This removes a JV candidate from the top level when it belongs below another JV candidate in the controlling-interest graph.

## Constructing JV Groups

Include each top-level JV in its own group and include every Entity it directly or indirectly controls:

$$
\mathbf{J}
:=
\operatorname{diag}(\mathbf{jv})
(\mathbf{I}_N\lor\mathbf{C}),
$$

where the multiplication is evaluated over the Boolean semiring. Equivalently,

$$
(\mathbf{J})_{ij}
=
\text{jv}_i
\land
\bigl(i=j\lor(\mathbf{C})_{ij}=1\bigr).
$$

Accordingly, $(\mathbf{J})_{ij}=1$ if and only if Entity $i$ is a top-level JV and Entity $j$ is either Entity $i$ itself or an Entity directly or indirectly controlled by Entity $i$.

Before creating `JvEntities`, validate that each column of $\mathbf{J}$ contains at most one true value:

$$
\forall j\in\mathcal{V}:\qquad
\sum_{i\in\mathcal{V}}(\mathbf{J})_{ij}\le1.
$$

The returned arrays can be converted to `JvEntities` rows by scanning the true elements of $\mathbf{J}$. The row index identifies `jv_group_id`, and the column index identifies `entity_id`.
