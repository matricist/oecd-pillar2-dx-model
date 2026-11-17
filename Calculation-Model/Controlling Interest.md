# Validation

## Structural Validation

$$
\boxed{\mathbf{C}_0\odot\mathbf{C}_0^{\mathsf T}=\mathbf{0}}
$$

Each column of $\mathbf{C}_0$ contains at most one `True`.

## Domain Validation

- No circular control.

## Cross-Classification Validation

Let $\mathbf{ce}$, $\mathbf{pe}$, and $\mathbf{group\text{-}upe}$ be $N\times1$ Boolean column vectors identifying CEs, PEs, and the group's UPEs, and let $\mathbf{controllers}:=\mathbf{C}_0^{T}\times\mathbf{1}_N$ count the direct controllers of each Entity.

- **A UPE has no controller:** $\mathbf{controllers}\odot\mathbf{group\text{-}upe}=\mathbf{0}_N$.
- **Every CE other than a UPE has a controller:** $(\mathbf{controllers})_j=1$ wherever $(\mathbf{ce}\land\neg\mathbf{group\text{-}upe})_j$ is `True`.
- **A PE that is not a CE is not controlled by a CE:** $\operatorname{diag}(\mathbf{ce})\times\mathbf{C}_0\times\operatorname{diag}(\mathbf{pe}\land\neg\mathbf{ce})=\mathbf{0}$.

These checks apply in addition to the structural and domain validations above.

# Direct Controlling Matrix

$\mathbf{C}_0$ is an $N\times N$ square matrix for $N$ Entities, with controlling Entities on rows, Entities controlled on columns, and Boolean values as entries. All diagonal entries are `False`.

# Warshall's algorithm

Starting from $\mathbf{C}_0$, compute the direct and indirect controlling interest matrix:

$$
(\mathbf{C}_t)_{ij}
=
(\mathbf{C}_{t-1})_{ij}
\lor
\left(
(\mathbf{C}_{t-1})_{it}
\land
(\mathbf{C}_{t-1})_{tj}
\right)
\qquad (t=1,\ldots,N)
$$

After $t=N$, the matrix remains unchanged:

$$
\boxed{\mathbf{C}=\lim_{t\to\infty}\mathbf{C}_t}
$$

# Implementation

## Bitset Implementation

For better performance, store each matrix row as a bitset. At step $t$, if Entity $i$ controls Entity $t$, merge row $t$ into row $i$ using bitwise OR. This updates multiple Boolean entries at once and reduces memory usage without changing the Warshall result.
