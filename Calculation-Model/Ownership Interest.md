# Interface

## Imports

- Relations.CompanyEntities
- Relations.PermanentEstablishments
- Relations.DirectOwnershipInterests

## Exports

### Direct and Indirect Ownership Interest Function: $f(\mathbf{A})$

This document defines and exports $f(\mathbf{A})$ for use throughout the Calculation Model.

- **Input:** A direct Ownership Interest Ratio matrix $\mathbf{A}\in[0,1]^{N\times N}$, with investor Entities on rows and investee Entities on columns. Each column sum must not exceed 1, and $\rho(\mathbf{A})<1$.
- **Output:** The corresponding direct and indirect Ownership Interest Ratio matrix, preserving the input Entity ordering.

$$
\mathbf{E}_{\mathbf{A}} := \mathbf{A}(\mathbf{I}_N-\mathbf{A})^{-1},\qquad
f(\mathbf{A}) := (\mathbf{I}_N+\operatorname{diag}(\mathbf{E}_{\mathbf{A}}))^{-1}\mathbf{E}_{\mathbf{A}}.
$$

In particular, $\mathbf{Y}=f(\mathbf{X}_0)$. The derivation and implementation below specify this exported function; `calculate_ownership(A)` implements $f(\mathbf{A})$ without explicitly forming the inverses. Other documents import $f$ from this document rather than defining it independently.

# Validation

## Structural Validation

- The sum of Direct Ownership Interest Ratios in any Entity must not exceed 1.
- An Entity’s Direct Ownership Interest Ratio in itself (treasury shares) must be less than 1.
- If an Entity holds a 100% Direct Ownership Interest in another Entity, the latter must not hold a 100% Direct Ownership Interest in the former.

## Domain Validation

- The ownership structure must not contain an SCC in which every Entity is wholly owned, in aggregate, by Entities within that SCC. This includes circular ownership through multiple partial interests, even when no individual interest is 100% (discussed below).
- A PE must not hold any Direct Ownership Interest in another Entity.
- Each PE must be directly and wholly owned by a single Entity.

# Operation

## Notation

As in Controlling Interest.md, bold uppercase symbols denote matrices, bold lowercase symbols denote column vectors, and calligraphic symbols denote sets. Indices and individual entries are scalars. This styling preserves the existing model names and calculation definitions.

| Symbol | Type and meaning |
|---|---|
| $\mathbf{A},\mathbf{X}_0,\mathbf{X}_t,\mathbf{Y},\mathbf{E}$ | $N\times N$ matrices; $N$ is the number of Entities. |
| $\mathbf{E}_{\mathbf{A}}$ | The $N\times N$ intermediate matrix obtained when the exported function receives $\mathbf{A}$. |
| $\mathbf{v}\in\mathbb{R}^{N\times1}$ | A column vector used in the definition of the diagonal operator. |
| $\mathcal{C},\mathcal{D}$ | Sets of Entity indices belonging to SCCs. |
| $\mathbf{B}_{\mathcal{C}}\in\mathbb{R}^{N\times\lvert\mathcal{C}\rvert}$ | The right-hand-side matrix for SCC $\mathcal{C}$. |
| $\mathbf{I}_N,\mathbf{I}_{\lvert\mathcal{C}\rvert}$ | Identity matrices for the full Entity population and an SCC block, respectively. |
| $i,j,k,t,N$ | Scalar indices, iteration index, or Entity count. |
| $p_{ij},\ y_{ij}:=(\mathbf{Y})_{ij},\ e_{ij}:=(\mathbf{E})_{ij}$ | Scalar ownership ratios or intermediate matrix entries. |

For example, $\mathbf{E}_{:,\mathcal{C}}$ is a matrix block, while $e_{ij}$ is a scalar. Block indices follow the common Entity ordering. The functions $f$, $\rho$, and $\operatorname{diag}$ retain their existing meanings. `PE` remains the domain abbreviation in prose.

## Converting the Relation to Direct Ownership Interest Ratio Matrix

From the Company Direct Ownership Interests table, define the Direct Ownership Interest Ratio Matrix $\mathbf{X}_0$ as follows:

$$
\mathbf{X}_0 \in [0,1]^{N \times N}
$$

where $N$ is the number of Entities identified by EntityId, and the row and column indices correspond to InvestorEntityId and InvesteeEntityId, respectively.

For each pair of Entities $i$ and $j$,

$$
(\mathbf{X}_0)_{ij}=\begin{cases}
p_{ij}, & \text{if Entity } i \text{ directly owns an Ownership Interest of } p_{ij} \text{ in Entity } j, \\
0, & \text{if no such direct ownership relationship exists.}
\end{cases}
$$

where $p_{ij}$ is the DirectOwnershipInterestRatio corresponding to InvestorEntityId = i and InvesteeEntityId = j.

## Derivation of Direct and Indirect Ownership Interest Ratios Using an Iterative Method

For validated inputs, $\rho(\mathbf{X}_0)<1$, where $\rho$ denotes the spectral radius, as explained under Invalid Ownership Structures below. This condition ensures convergence of both the Neumann series and the recurrence below. The recurrence is introduced solely to derive the direct solution; it is not used as a numerical implementation.

Starting with the direct ownership matrix $\mathbf{X}_0$, define:

$$
(\mathbf{X}_{t+1})_{ij} = (\mathbf{X}_0)_{ij} + \sum_{k \neq i}(\mathbf{X}_t)_{ik}(\mathbf{X}_0)_{kj}
$$

The first term on the right-hand side represents the direct ownership interest, while the second term represents the indirect ownership interest.  
The condition $k \ne i$ in the calculation of indirect ownership is required to prevent the portion of Entity $i$'s ownership in itself, arising from circular ownership structures or treasury shares, from being used as an intermediate ownership interest in the next iteration.

The recurrence relation can be expressed in matrix form as follows:

$$
\boxed{
    \mathbf{X}_{t+1} = (\mathbf{X}_t - \operatorname{diag}(\mathbf{X}_t) + \mathbf{I}_N)\mathbf{X}_0}
$$

Here, $\operatorname{diag}(\mathbf{M})$ for a square matrix $\mathbf{M}$ retains its diagonal entries and sets all other entries to zero. For a column vector $\mathbf{v}\in\mathbb{R}^{N\times1}$, $\operatorname{diag}(\mathbf{v})$ constructs an $N\times N$ diagonal matrix from its entries. The symbol $\mathbf{I}_N$ denotes the $N\times N$ identity matrix.

Let $\mathbf{Y}$ denote the matrix of direct and indirect Ownership Interest Ratios to be determined. Then:

$$
\boxed{
    \mathbf{Y}=\lim_{t \to \infty} \mathbf{X}_t
}
$$

## Derivation of Direct and Indirect Ownership Interest Ratios Using the Direct Method

The direct solution can be derived from the iterative recurrence relation defined above.

First, define

$$
\mathbf{Y} := \lim_{t \to \infty} \mathbf{X}_t
$$

$$
\mathbf{E} := \mathbf{X}_0(\mathbf{I}_N-\mathbf{X}_0)^{-1}
$$

Since $\rho(\mathbf{X}_0)<1$, the Neumann series converges and

$$
\mathbf{E} = \mathbf{X}_0 + \mathbf{X}_0^2 + \mathbf{X}_0^3 + \cdots
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

Since $\rho(\mathbf{X}_0)<1$, $\mathbf{I}_N-\mathbf{X}_0$ is invertible, giving

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

The implementation evaluates the direct solution using strongly connected component (SCC) decomposition, depth-first search (DFS), and local LU solves. The iterative recurrence above is used only to derive the direct solution; it is not executed as a numerical algorithm or used as a fallback.

### Ownership Graph and SCC Decomposition

Construct a directed graph with one vertex for each Entity and an edge from Entity $i$ to Entity $j$ whenever $(\mathbf{X}_0)_{ij}>0$.

Partition the graph into SCCs and contract each SCC into a single vertex. The resulting condensation graph is a directed acyclic graph (DAG).

An SCC requires a local solve if it contains multiple Entities or a single Entity with a self-loop representing treasury shares. A single-Entity SCC without a self-loop can be evaluated directly.

### DFS Evaluation and Local LU Solves

Rather than explicitly forming $(\mathbf{I}_N-\mathbf{X}_0)^{-1}$, compute $\mathbf{E}$ from the equivalent linear system

$$
\mathbf{E}(\mathbf{I}_N-\mathbf{X}_0)=\mathbf{X}_0.
$$

For an SCC $\mathcal{C}$, let $\operatorname{Pred}(\mathcal{C})$ denote its immediate predecessor SCCs in the condensation graph. Using $:$ to denote all row indices, the block equation is

$$
\mathbf{E}_{:,\mathcal{C}}(\mathbf{I}_{|\mathcal{C}|}-(\mathbf{X}_0)_{\mathcal{C},\mathcal{C}})
=
(\mathbf{X}_0)_{:,\mathcal{C}}
+
\sum_{\mathcal{D}\in\operatorname{Pred}(\mathcal{C})}
\mathbf{E}_{:,\mathcal{D}}(\mathbf{X}_0)_{\mathcal{D},\mathcal{C}}.
$$

Evaluate each SCC through DFS over its predecessors, caching each completed result so that every SCC is evaluated only once. Once all predecessors of $\mathcal{C}$ have been evaluated, define

$$
\mathbf{B}_{\mathcal{C}}
=
(\mathbf{X}_0)_{:,\mathcal{C}}
+
\sum_{\mathcal{D}\in\operatorname{Pred}(\mathcal{C})}
\mathbf{E}_{:,\mathcal{D}}(\mathbf{X}_0)_{\mathcal{D},\mathcal{C}}.
$$

For a single-Entity SCC without a self-loop, $(\mathbf{X}_0)_{\mathcal{C},\mathcal{C}}=0$, and therefore

$$
\mathbf{E}_{:,\mathcal{C}}=\mathbf{B}_{\mathcal{C}}.
$$

For an SCC containing a cycle, solve the local linear system

$$
\mathbf{E}_{:,\mathcal{C}}\bigl(\mathbf{I}_{|\mathcal{C}|}-(\mathbf{X}_0)_{\mathcal{C},\mathcal{C}}\bigr)=\mathbf{B}_{\mathcal{C}}.
$$

Because `lu_solve` expects the coefficient matrix to multiply the unknown from the left, transpose the equation:

$$
\bigl(\mathbf{I}_{|\mathcal{C}|}-(\mathbf{X}_0)_{\mathcal{C},\mathcal{C}}\bigr)^T \mathbf{E}_{:,\mathcal{C}}^T=\mathbf{B}_{\mathcal{C}}^T.
$$

Use `lu_factor` to factorize the transposed coefficient matrix with pivoting, then use `lu_solve` to obtain the solution. Factorize the coefficient matrix once per SCC and reuse the factorization for all right-hand sides. Transpose the solution back and store it in $\mathbf{E}_{:,\mathcal{C}}$.

Thus, DFS determines the dependency order and propagates ownership contributions between SCCs, while local LU solves account for circular ownership within each SCC. If the graph contains no cycles, the entire calculation reduces to DFS with cached results.

### Recovering the Ownership Interest Ratios

After computing $\mathbf{E}$, obtain the final direct and indirect Ownership Interest Ratios by row-wise normalization:

$$
y_{ij}=\frac{e_{ij}}{1+e_{ii}}.
$$

This implements

$$
\mathbf{Y}=(\mathbf{I}_N+\operatorname{diag}(\mathbf{E}))^{-1}\mathbf{E}
$$

without explicitly forming either inverse.

### Invalid Ownership Structures

The calculation requires $\mathbf{I}_{|\mathcal{C}|}-(\mathbf{X}_0)_{\mathcal{C},\mathcal{C}}$ to be nonsingular for every SCC $\mathcal{C}$. Under the nonnegativity and column-sum constraints on $\mathbf{X}_0$, this is equivalent to requiring

$$
\rho((\mathbf{X}_0)_{\mathcal{C},\mathcal{C}})<1
$$

for every SCC, where $\rho$ denotes the spectral radius.

Equivalently, every SCC $\mathcal{C}$ must contain at least one Entity whose total direct ownership by Entities within $\mathcal{C}$ is less than 1:

$$
\exists j\in \mathcal{C}:\quad \sum_{i\in \mathcal{C}}(\mathbf{X}_0)_{ij}<1.
$$

An SCC that violates this condition is fully internally owned: every Entity in it is owned 100% in aggregate by Entities within the same SCC. For example, three Entities each owned 50% by each of the other two form an invalid SCC, even though no individual ownership interest is 100%.

Such inputs are rejected during validation under the rule prohibiting 100% circular ownership or 100% treasury shares. Neither LU solving nor numerical iteration is used as a fallback. Since SCC decomposition puts $\mathbf{X}_0$ into block triangular form after reordering, its eigenvalues are those of its diagonal SCC blocks. Therefore, satisfying the condition for every SCC ensures $\rho(\mathbf{X}_0)<1$.

For valid inputs, the calculation requires no iteration limit or convergence stopping criterion, although ordinary floating-point rounding errors remain possible.