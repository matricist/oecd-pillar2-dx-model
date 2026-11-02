# Operation

Use the direct Ownership Interest matrix $\mathbf{X}_0$ defined in [Ownership Interest](<Ownership Interest.md#direct-ownership-matrix>) and the direct Controlling Interest matrix $\mathbf{C}_0$ defined in [Controlling Interest](<Controlling Interest.md#direct-controlling-matrix>), both for the same $N$ Entities.

## JV Exclusion Mask

$\mathbf{jv\text{-}excluded}$ is an $N\times1$ Boolean column vector. An entry is `True` if the Entity is any of the following, and `False` otherwise:

- A UPE of another MNE Group subject to the GloBE Rules.
- An Excluded Entity under Article 1.5.1.
- An Entity whose interests held by the MNE Group are held directly through an Article 1.5.1 Excluded Entity, satisfying the applicable asset-holding, ancillary-activity, or excluded-income condition.
- An Entity held by an MNE Group composed exclusively of Excluded Entities.

## Identifying JV Candidates

An Entity is a JV candidate when all of the following conditions are satisfied:

1. its financial results are reported under the equity method; and
2. the UPE or UPEs of the relevant MNE Group hold, in aggregate, at least 50% of its Ownership Interests, directly or indirectly; and
3. it is not identified by $\mathbf{jv\text{-}excluded}$.

Let $\mathbf{Y}=f(\mathbf{X}_0)$ be the $N\times N$ direct and indirect Ownership Interest matrix calculated using the [Ownership Interest method](<Ownership Interest.md#direct-method>). With $\mathbf{group\text{-}upe}$ identifying the relevant group's UPEs, the aggregate UPE ownership vector is

$$
\mathbf{upe\text{-}ownership}
:=
\mathbf{Y}^{T}\times\mathbf{group\text{-}upe}.
$$

Its scalar entry is

$$
\text{upe-ownership}_j
=
\sum_{i=1}^{N}
\text{group-upe}_i\times(\mathbf{Y})_{ij}.
$$

With $\mathbf{eqt}$ identifying equity-method Entities, the $N\times1$ Boolean JV candidate vector is

$$
\mathbf{jvc}
:=
\mathbf{eqt}
\land
(\mathbf{upe\text{-}ownership}\ge0.5)
\land
\neg\mathbf{jv\text{-}excluded},
$$

where the inequality is evaluated element-wise.

## Identifying Top-Level JVs and JV Subsidiaries

Let $w$ denote [Warshall's algorithm](<Controlling Interest.md#warshalls-algorithm>), which maps the direct Controlling Interest matrix $\mathbf{C}_0$ to the direct and indirect Controlling Interest matrix:

$$
\mathbf{C}
:=
w(\mathbf{C}_0).
$$

An Entity is a JV Subsidiary candidate if it is directly or indirectly controlled by at least one JV candidate:

$$
\mathbf{jvsub}
:=
\left(\mathbf{C}^{T}\times\mathbf{jvc}\right)>0.
$$

Thus, $\text{jvsub}_j=1$ if there exists an Entity $i$ such that $\text{jvc}_i=1$ and $(\mathbf{C})_{ij}=1$.

A top-level JV is a JV candidate that is not itself controlled by another JV candidate:

$$
\mathbf{jv}
:=
\mathbf{jvc}\land\neg\mathbf{jvsub}.
$$

This removes a JV candidate from the top level when it belongs below another JV candidate in the controlling-interest graph.

## Constructing JV Groups

$\mathbf{J}$ is the $N\times N$ Boolean JV Group membership matrix, with top-level JVs on rows and member Entities on columns. Include each JV itself and every Entity it directly or indirectly controls, where $\mathbf{I}_N$ is the identity matrix:

$$
\mathbf{J}
:=
\operatorname{diag}(\mathbf{jv})
\times(\mathbf{I}_N\lor\mathbf{C}),
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

The returned arrays can be converted to `JvEntities` rows by scanning the true elements of $\mathbf{J}$. The row index identifies `jv_group_id`, and the column index identifies `entity_id`.
