# Operation

Use the direct Ownership Interest matrix $\mathbf{X}_0$ defined in [Ownership Interest](<Ownership Interest.md#direct-ownership-matrix>) and the direct Controlling Interest matrix $\mathbf{C}_0$ defined in [Controlling Interest](<Controlling Interest.md#direct-controlling-matrix>), both for the same $N$ Entities.

## JV Exclusion Mask

$\mathbf{jv\text{-}excluded}$ is an $N\times1$ Boolean column vector. An entry is `True` if the Entity is any of the following, and `False` otherwise:

- A UPE of another MNE Group subject to the GloBE Rules.
- An Excluded Entity under Article 1.5.1.
- An Entity whose interests held by the MNE Group are held directly through an Article 1.5.1 Excluded Entity, satisfying the applicable asset-holding, ancillary-activity, or excluded-income condition.
- An Entity held by an MNE Group composed exclusively of Excluded Entities.

## Identifying JV Candidates

Let $\mathbf{Y}=f(\mathbf{X}_0)$ be the $N\times N$ direct and indirect Ownership Interest matrix calculated using the [Ownership Interest method](<Ownership Interest.md#direct-method>). Sum the interests held by the group's UPEs, identified by $\mathbf{group\text{-}upe}$:

$$
\mathbf{upe\text{-}ownership}
:=
\mathbf{Y}^{T}\times\mathbf{group\text{-}upe}.
$$

With $\mathbf{eqt}$ identifying equity-method Entities, the $N\times1$ Boolean vector $\mathbf{jvc}$ identifies Entities that use the equity method, have aggregate UPE ownership of at least 50%, and are not excluded:

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

A top-level JV is a JV candidate that is not itself controlled by another JV candidate:

$$
\mathbf{jv}
:=
\mathbf{jvc}\land\neg\mathbf{jvsub}.
$$

## Constructing JV Groups

$\mathbf{J}$ is an $N\times N$ Boolean matrix with top-level JVs on rows and member Entities on columns. Each group includes the JV itself and all Entities it directly or indirectly controls.

$$
\mathbf{J}:=\operatorname{diag}(\mathbf{jv})\times(\mathbf{I}_N\lor\mathbf{C}).
$$
