# Validation

## Structural Validation

$$
\boxed{\mathbf{C}_0\odot\mathbf{C}_0^{\mathsf T}=\mathbf{0}}
$$

## Domain Validation

- No circular control.

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

## Controller Recommendation Algorithm

Recommend the eligible direct shareholder with the largest ordinary Ownership Interest Ratio. If tied, search upstream shareholders of the tied candidates and compare their direct and indirect Ownership Interest Ratios in the original target until a unique candidate is found; the recommendation requires confirmation.
