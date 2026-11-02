# Validation

## Structural Validation

- Each entry is a real number in $[0,1]$.
- Each column sum is at most 1.
- Each diagonal entry is less than 1.

## Domain Validation

- No 100% circular ownership.

# Operation

## Notation

- **Matrices:** Bold uppercase letters, e.g. $\mathbf{X}_0,\mathbf{Y},\mathbf{I}_N$.
- **Vectors:** Bold lowercase letters; column vectors unless stated otherwise, e.g. $\mathbf{v}$.
- **Scalars:** Non-bold letters, e.g. $y_{ij},i,j,N$.

## Direct Ownership Matrix

$\mathbf{X}_0$ is an $N\times N$ square matrix for $N$ Entities, with owning Entities on rows, Entities owned on columns, and Ownership Interest Ratios as entries. Diagonal entries represent treasury shares.

**Note:** Masking the direct ownership matrix before calculating indirect ownership generally differs from masking the result afterwards. Apply the mask at the stage required by the calculation.

## Iterative Method

Element-wise recurrence:

$$
(\mathbf{X}_{t+1})_{ij} = (\mathbf{X}_0)_{ij} + \sum_{k \neq i}(\mathbf{X}_t)_{ik}(\mathbf{X}_0)_{kj}
$$

**Note:** $k\ne i$ excludes self-ownership arising from treasury shares or circular ownership as an intermediate interest.

Matrix recurrence:

Here, $\operatorname{diag}$ retains only the diagonal entries of a matrix, setting all other entries to zero.

$$
\boxed{
    \mathbf{X}_{t+1} = (\mathbf{X}_t - \operatorname{diag}(\mathbf{X}_t) + \mathbf{I}_N)\mathbf{X}_0}
$$

Limit of iteration:

$$
\boxed{
    \mathbf{Y}=\lim_{t \to \infty} \mathbf{X}_t
}
$$

## Direct Method

Define

$$
\mathbf{E} := \mathbf{X}_0(\mathbf{I}_N-\mathbf{X}_0)^{-1}
$$

Starting from the recurrence relation,

$$
\mathbf{X}_{t+1} = (\mathbf{X}_t - \operatorname{diag}(\mathbf{X}_t) + \mathbf{I}_N)\mathbf{X}_0
$$

taking the limit as $t \to \infty$ gives

$$
\mathbf{Y} = (\mathbf{Y} - \operatorname{diag}(\mathbf{Y}) + \mathbf{I}_N)\mathbf{X}_0
$$

Rearranging the equation,

$$
\mathbf{Y}(\mathbf{I}_N-\mathbf{X}_0) = (\mathbf{I}_N-\operatorname{diag}(\mathbf{Y}))\mathbf{X}_0
$$

Under the validation conditions, $\mathbf{I}_N-\mathbf{X}_0$ is invertible, giving

$$
\mathbf{Y} = (\mathbf{I}_N-\operatorname{diag}(\mathbf{Y}))\mathbf{X}_0(\mathbf{I}_N-\mathbf{X}_0)^{-1}
$$

By the definition of $\mathbf{E}$,

$$
\mathbf{Y} = (\mathbf{I}_N-\operatorname{diag}(\mathbf{Y}))\mathbf{E}
$$

Since $(\mathbf{I}_N-\operatorname{diag}(\mathbf{Y}))$ is a diagonal matrix, the $(i,j)$-th element of the matrix equation satisfies

$$
y_{ij}=(1-y_{ii})e_{ij}
$$

For the diagonal elements, setting $j=i$ gives

$$
y_{ii}=\frac{e_{ii}}{1+e_{ii}}
$$

Substituting $y_{ii}$ back into the $y_{ij}$ equation,

$$
(1+e_{ii})y_{ij} = e_{ij}
$$

Since $1+e_{ii}$ depends only on the row index $i$, this element-wise relation can be written in matrix form as

$$
(\mathbf{I}_N+\operatorname{diag}(\mathbf{E}))\mathbf{Y} = \mathbf{E}
$$

Therefore,

$$
\mathbf{Y} = (\mathbf{I}_N+\operatorname{diag}(\mathbf{E}))^{-1}\mathbf{E}
$$

$\mathbf{I}_N+\operatorname{diag}(\mathbf{E})$ is invertible because $e_{ii} \ge 0$ for every $i$, and therefore every diagonal element $1+e_{ii}$ is strictly positive.

## Implementation

The full linear system can be solved directly using LU. For computational efficiency, this implementation instead decomposes the ownership graph into SCCs and applies LU only to cyclic components.

1. **Identify cycles:** Represent direct ownership as a directed graph and divide it into SCCs.
2. **Follow dependencies:** Use DFS to evaluate predecessor components first.
3. **Resolve circular ownership:** Use local LU solves within cyclic components, including treasury-share self-loops. Components without cycles require only propagation of ownership contributions.
4. **Normalize:** Divide every entry in row $i$ of $\mathbf{E}$ by $1+e_{ii}$ to obtain row $i$ of $\mathbf{Y}$:

   $$
   y_{ij}=\frac{e_{ij}}{1+e_{ii}}.
   $$
