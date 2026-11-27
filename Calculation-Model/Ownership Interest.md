This document defines how direct interests become direct and indirect interests: Ownership Interests over the real numbers, the same with some Parent Entities absorbing what reaches them, and Controlling Interests over the Booleans. Every other document imports its interest matrices from here.

# Direct Ownership Matrix

$\mathbf{X}_0$ is an $N\times N$ square matrix for $N$ Entities, with owning Entities on rows, Entities owned on columns, and Ownership Interest Ratios as entries. Diagonal entries represent treasury shares.

$\mathbf{X}_0^{\mathrm{profit}}$ is the corresponding direct Profit Ownership Interest matrix. Where no separate Profit Ownership Interest Ratio is given for an entry, it equals the entry of $\mathbf{X}_0$.

**Note:** Masking the direct ownership matrix before calculating indirect ownership generally differs from masking the result afterwards. Apply the mask at the stage required by the calculation.

## Effective Periods

The matrices describe a period within the Fiscal Year during which no direct Ownership or Controlling Interest changes. Where one changes, the year is split at the change date and every validation and calculation is repeated for each period. The amounts of each period are calculated for that period alone and are not combined across periods. [Period Changes](#period-changes) updates the calculation from one period to the next.

## Arithmetic

Ownership Interest Ratios and amounts are given as finite decimals, so they are rational numbers, and every result of the Calculation Model is a rational number as well: $\mathbf{Y}$ solves a linear system with rational coefficients. Every document of the Calculation Model calculates exactly, without rounding, and compares exactly with its thresholds, such as $\mathbf{Y}=1$, more than 20%, at least 50% and at most 30%. Rounding applies only when a value is reported, such as a percentage to four decimal places of the ratio in the GloBE Information Return.

# Validation

$$
\begin{aligned}
&0\le(\mathbf{X}_0)_{ij}\le1\\
&\mathbf{1}_N^{T}\times\mathbf{X}_0\le\mathbf{1}_N^{T}\\
&(\mathbf{X}_0)_{ii}<1\\
&\mathbf{I}_N-\mathbf{X}_0\text{ is invertible}
\end{aligned}
$$

Given the first three conditions, the last fails exactly when some non-empty set of Entities $C$ is wholly owned within itself: $\sum_{i\in C}(\mathbf{X}_0)_{ij}=1$ for every $j\in C$, such as two Entities holding 100% of each other. Wholly-owned chains are fine. Every chain of owners eventually reaches an Entity with a column sum below 1, such as the UPE, which is owned from outside the matrix.

$\mathbf{X}_0$ and $\mathbf{X}_0^{\mathrm{profit}}$ are validated independently. Passing the validation for one does not cure a failure in the other.

# Calculation

$\mathbf{Y}$ is the $N\times N$ direct and indirect Ownership Interest matrix: $(\mathbf{Y})_{ij}$ is the total share of Entity $j$ that Entity $i$ holds, directly and through other Entities. The diagonal entry $(\mathbf{Y})_{ii}$ is the share of Entity $i$ that it holds in itself, through treasury shares or circular ownership.

Matrices are bold uppercase, vectors bold lowercase, and scalars such as $y_{ij}$ are not bold. $\operatorname{diag}$ retains only the diagonal entries of a matrix, setting all other entries to zero.

## Iterative Method

$$
\boxed{
\begin{aligned}
\mathbf{X}_{t+1}&=(\mathbf{X}_t-\operatorname{diag}(\mathbf{X}_t)+\mathbf{I}_N)\mathbf{X}_0\\
\mathbf{Y}&=\lim_{t\to\infty}\mathbf{X}_t
\end{aligned}
}
$$

Element by element, the recurrence is

$$
(\mathbf{X}_{t+1})_{ij} = (\mathbf{X}_0)_{ij} + \sum_{k \neq i}(\mathbf{X}_t)_{ik}(\mathbf{X}_0)_{kj}
$$

where $k\ne i$ excludes self-ownership arising from treasury shares or circular ownership as an intermediate interest.

## Direct Method

$$
\boxed{
\begin{aligned}
\mathbf{L}&:=(\mathbf{I}_N-\mathbf{X}_0)^{-1}\\
\mathbf{Y}&=\operatorname{diag}(\mathbf{L})^{-1}(\mathbf{L}-\mathbf{I}_N)
\end{aligned}
}
$$

Element by element, $y_{ij}=\dfrac{l_{ij}-\delta_{ij}}{l_{ii}}$. In particular, the self-ownership is $y_{ii}=1-1/l_{ii}$.

### Derivation

Taking the limit of the recurrence as $t\to\infty$ gives

$$
\mathbf{Y} = (\mathbf{Y} - \operatorname{diag}(\mathbf{Y}) + \mathbf{I}_N)\mathbf{X}_0
$$

Rearranging, and using that $\mathbf{I}_N-\mathbf{X}_0$ is invertible under the validation conditions,

$$
\mathbf{Y} = (\mathbf{I}_N-\operatorname{diag}(\mathbf{Y}))\mathbf{X}_0\mathbf{L} = (\mathbf{I}_N-\operatorname{diag}(\mathbf{Y}))(\mathbf{L}-\mathbf{I}_N)
$$

since $\mathbf{X}_0\mathbf{L}=\mathbf{L}-\mathbf{I}_N$. The $(i,j)$-th element is

$$
y_{ij}=(1-y_{ii})(l_{ij}-\delta_{ij})
$$

Setting $j=i$ gives $y_{ii}=(1-y_{ii})(l_{ii}-1)$, so

$$
1-y_{ii}=\frac{1}{l_{ii}}
$$

Substituting back gives $y_{ij}=(l_{ij}-\delta_{ij})/l_{ii}$, the Direct Method.

$\operatorname{diag}(\mathbf{L})$ is invertible because $\mathbf{L}=\sum_{t\ge0}\mathbf{X}_0^t\ge\mathbf{I}_N$ entrywise, so every $l_{ii}\ge1$.

### Interpretation

$l_{ij}$ sums every ownership path from $i$ to $j$. Each such path splits uniquely into a loop that returns to $i$ and a path that never returns to $i$, so $l_{ij}=l_{ii}\cdot y_{ij}$ for $i\ne j$. Dividing by $l_{ii}$ removes paths that use $i$ as an intermediate holder ($k\ne i$ in the recurrence). Loops at $j$ stay in. Those are $j$'s treasury shares and circular holdings, which raise the interests of $j$'s other holders.

### Example

$P$ holds 90% of $S$, and $S$ holds 10% of itself as treasury shares.

$$
\mathbf{X}_0=\begin{pmatrix}0&0.9\\0&0.1\end{pmatrix},\quad
\mathbf{L}=\begin{pmatrix}1&1\\0&10/9\end{pmatrix},\quad
\mathbf{Y}=\begin{pmatrix}0&1\\0&0.1\end{pmatrix}
$$

$P$ holds 100% of $S$, which is 90% of the shares held outside $S$ itself. $S$ holds 10% of itself.

## Implementation

$\mathbf{L}$ is never formed as an explicit inverse. It is the unique solution of

$$
\mathbf{L}=\mathbf{I}_N+\mathbf{L}\mathbf{X}_0,
$$

whose column $j$ reads $\mathbf{L}_{:,j}=\mathbf{e}_j+\sum_k\mathbf{L}_{:,k}(\mathbf{X}_0)_{kj}$. Column $j$ depends only on the columns of $j$'s direct owners, so the columns can be filled from the top of the ownership graph down.

1. **Decompose:** Treat $(\mathbf{X}_0)_{ij}>0$ as an edge $i\to j$ and split the graph into strongly connected components (SCCs). A component is cyclic if it has more than one Entity or a treasury-share self-loop.
2. **Order:** Sort the components topologically, owners first. Every owner of a component outside it is then already solved.
3. **Solve each component $C$:** With $P$ the Entities outside $C$,

   $$
   \mathbf{L}_{:,C}(\mathbf{I}-(\mathbf{X}_0)_{CC})=\mathbf{I}_{:,C}+\mathbf{L}_{:,P}(\mathbf{X}_0)_{PC}.
   $$

   - Single Entity, no self-loop: the column formula above. No solve.
   - Single Entity with treasury shares $x_{jj}$: as above, divided by $1-x_{jj}$.
   - Cyclic component: one LU factorisation of the $|C|\times|C|$ matrix $\mathbf{I}-(\mathbf{X}_0)_{CC}$, reused for every row.
4. **Normalize:** apply the [Direct Method](#direct-method) to $\mathbf{L}$.

**Validation comes free.** $\mathbf{I}_N-\mathbf{X}_0$ is singular exactly when some $\mathbf{I}-(\mathbf{X}_0)_{CC}$ is, so the invertibility condition is checked component by component: a singular local LU identifies the closed set of Entities that no one outside owns.

**Cost.** Dense LU costs $O(N^3)$. Here the cost is $O\bigl(\sum_C|C|^3\bigr)$ for the cyclic components plus propagation, which is linear in the number of edges times the number of ancestors per column. Column $j$ of $\mathbf{L}$ is nonzero only on $j$ and its direct and indirect owners, so $\mathbf{L}$ and $\mathbf{Y}$ stay sparse. Group structures are mostly trees with a few small cycles, so in practice this is close to linear.

## Row Calculation

Row $i$ of $f(\mathbf{A})$ needs one row of $\mathbf{L}=(\mathbf{I}_N-\mathbf{A})^{-1}$. The row $\mathbf{r}_i:=\mathbf{e}_i^{T}\mathbf{L}$ is the solution of

$$
\mathbf{r}_i=\mathbf{e}_i^{T}+\mathbf{r}_i\mathbf{A},
$$

and

$$
\boxed{
f(\mathbf{A})_{i,:}=\frac{\mathbf{r}_i-\mathbf{e}_i^{T}}{(\mathbf{r}_i)_i}
}
$$

$(\mathbf{r}_i)_j$ depends only on the entries for $j$'s direct owners, so the row is filled from $i$ down through its direct and indirect subsidiaries, in the topological order of the strongly connected components, with a local solve for each cyclic component. Entities that $i$ does not hold are never visited.

## Period Changes

Between two periods usually only a few direct interests change. Let $\mathcal{K}$ be the Entities whose column of $\mathbf{X}_0$ changes, and $\mathbf{D}:=(\mathbf{X}_0'-\mathbf{X}_0)_{:,\mathcal{K}}$ the change. By the Sherman–Morrison–Woodbury identity, the next period's $\mathbf{L}'=(\mathbf{I}_N-\mathbf{X}_0')^{-1}$ is a rank-$|\mathcal{K}|$ update of $\mathbf{L}$:

$$
\boxed{
\mathbf{L}'=\mathbf{L}+\mathbf{L}\mathbf{D}\left(\mathbf{I}_{|\mathcal{K}|}-\mathbf{L}_{\mathcal{K},:}\mathbf{D}\right)^{-1}\mathbf{L}_{\mathcal{K},:}
}
$$

The $|\mathcal{K}|\times|\mathcal{K}|$ matrix is invertible exactly when $\mathbf{X}_0'$ passes the [validation](#validation). The Direct Method then gives $\mathbf{Y}'$ from $\mathbf{L}'$.

# Ownership with Absorbing Parent Entities

The IIR and the UTPR follow an interest in a low-taxed Entity $j$ up the ownership chain until it reaches a Parent Entity that brings it into charge. Such a Parent Entity absorbs the interest: nothing above it reaches $j$ through it. This is the ownership calculation above with the absorbing Parent Entities' incoming edges cut.

## Definition

Let $\mathbf{S}\in\{0,1\}^{N\times N}$ mark absorbing Parent Entities on rows and the Entities they absorb for on columns. Column $j$ of the cut ownership matrix $h(\mathbf{X};\mathbf{S})$ is column $j$ of $f$ applied to $\mathbf{X}$ with the columns of the absorbing Parent Entities of $j$ removed:

$$
\boxed{
h(\mathbf{X};\mathbf{S})_{:,j}:=f\bigl(\mathbf{X}\operatorname{diag}(\mathbf{1}_N-\mathbf{S}_{:,j})\bigr)_{:,j}
}
$$

Removing column $k$ removes every interest held in $k$, so no path to $j$ passes through $k$. A path may still start at $k$.

- For an absorbing Parent Entity $k$ of $j$, $h_{kj}$ is $k$'s interest in $j$ through Entities that are not absorbing.
- For any other Entity $i$, $h_{ij}$ is $i$'s interest in $j$ that reaches $i$ without passing through an absorbing Parent Entity.
- With no absorbing Parent Entities, $h(\mathbf{X};\mathbf{0})=f(\mathbf{X})$.

Treasury shares and circular ownership are handled inside $f$, so $\mathbf{X}$ keeps its diagonal.

## Iterative Reading

Column $j$ of $h$ is the limit of the recurrence of the iterative method run on $\mathbf{X}\operatorname{diag}(\mathbf{1}_N-\mathbf{S}_{:,j})$. Equivalently, start one unit of unpaid interest at $j$ and pass it up one ownership level per step: an absorbing Parent Entity keeps what reaches it, every other Entity passes it on. For the absorbing Parent Entities, what they keep in the limit is $h_{kj}$.

## Correction Form

$h$ needs no second solve of the ownership graph. For one column $j$, let $\mathcal{S}$ be its absorbing Parent Entities, $\mathbf{Y}:=f(\mathbf{X})$, and

$$
\mathbf{N}_{\mathcal{S}}:=g(\mathbf{Y})_{\mathcal{S}\mathcal{S}}^{-1}\,\mathbf{Y}_{\mathcal{S},:}
$$

with $g(\mathbf{A}):=\mathbf{A}-\operatorname{diag}(\mathbf{A})+\mathbf{I}_N$. Then

$$
\boxed{
h(\mathbf{X};\mathbf{S})_{ij}=
\begin{cases}
(\mathbf{N}_{\mathcal{S}})_{ij}, & i\in\mathcal{S},\\[6pt]
\dfrac{y_{ij}-\mathbf{Y}_{i\mathcal{S}}(\mathbf{N}_{\mathcal{S}})_{:,j}}{1-\mathbf{Y}_{i\mathcal{S}}(\mathbf{N}_{\mathcal{S}})_{:,i}}, & i\notin\mathcal{S},\ i\ne j.
\end{cases}
}
$$

- $(\mathbf{N}_{\mathcal{S}})_{kj}$ is $k$'s interest in $j$ that does not pass through another absorbing Parent Entity: the absorption probabilities of an absorbing Markov chain.
- The numerator is $i$'s interest in $j$ less the part that passes through an absorbing Parent Entity. Each such path is split at the last absorbing Parent Entity on it.
- $\mathbf{Y}_{i\mathcal{S}}(\mathbf{N}_{\mathcal{S}})_{:,i}$ in the denominator is $i$'s interest in itself that passes through an absorbing Parent Entity. Cutting removes it, so it grosses up $i$'s remaining interests the same way treasury shares gross up the other holders. Without such a circular holding the denominator is 1.

$g(\mathbf{Y})_{\mathcal{S}\mathcal{S}}$ is invertible and the denominator lies in $(0,1]$, because $g(\mathbf{Y})=\operatorname{diag}(\mathbf{L})^{-1}\mathbf{L}$ and every principal submatrix of $\mathbf{L}$ is invertible.

Removing a set of Entities from the graph is the same correction with $\mathcal{S}$ fixed for every column: for $i\ne j$ outside $\mathcal{S}$, $f\bigl(\operatorname{diag}(\mathbf{1}_N-\mathbf{s})\,\mathbf{X}\operatorname{diag}(\mathbf{1}_N-\mathbf{s})\bigr)_{ij}$ is given by the second case.

## Implementation

Compute $\mathbf{Y}$ once. Group the columns by their absorbing set $\mathcal{S}$. For each group, factorize the $|\mathcal{S}|\times|\mathcal{S}|$ matrix $g(\mathbf{Y})_{\mathcal{S}\mathcal{S}}$ once and compute $\mathbf{N}_{\mathcal{S}}$ for the columns of the group and the rows that need a denominator. Each remaining cell then costs $|\mathcal{S}|$ multiplications.

# Controlling Interest

The direct and indirect Controlling Interest matrix is the same path closure over the Boolean semiring: $\lor$ in place of $+$, $\land$ in place of $\times$.

## Direct Controlling Matrix

$\mathbf{C}_0$ is an $N\times N$ square matrix for $N$ Entities, with controlling Entities on rows, Entities controlled on columns, and Boolean values as entries. All diagonal entries are `False`.

## Control Validation

$$
\boxed{\mathbf{C}_0^{T}\times\mathbf{1}_N\le\mathbf{1}_N}
$$

Each Entity has at most one direct controller, and there is no circular control.

Let $\mathbf{ce}$, $\mathbf{pe}$, and $\mathbf{group\text{-}upe}$ be $N\times1$ Boolean column vectors identifying CEs, PEs, and the group's UPEs, and let $\mathbf{controllers}:=\mathbf{C}_0^{T}\times\mathbf{1}_N$ count the direct controllers of each Entity.

- **A UPE has no controller:** $\mathbf{controllers}\odot\mathbf{group\text{-}upe}=\mathbf{0}_N$.
- **Every CE other than a UPE has a controller:** $(\mathbf{controllers})_j=1$ wherever $(\mathbf{ce}\land\neg\mathbf{group\text{-}upe})_j$ is `True`.
- **A PE that is not a CE is not controlled by a CE:** $\operatorname{diag}(\mathbf{ce})\times\mathbf{C}_0\times\operatorname{diag}(\mathbf{pe}\land\neg\mathbf{ce})=\mathbf{0}$.

## Closure

Each Entity has at most one controller and control is acyclic, so between two Entities there is at most one chain of control. The Boolean closure therefore equals the same sum over the integers, and it is the Leontief inverse of $\mathbf{C}_0$:

$$
\boxed{\mathbf{C}=w(\mathbf{C}_0):=(\mathbf{I}_N-\mathbf{C}_0)^{-1}-\mathbf{I}_N=\mathbf{C}_0+\mathbf{C}_0^{2}+\cdots}
$$

Every entry is 0 or 1, and the sum is finite because $\mathbf{C}_0$ has no cycle. $\mathbf{C}$ is computed like $\mathbf{L}$ in the [implementation](#implementation) above: the control graph has no cyclic component, so every column is filled by propagation alone, and no normalization is needed.

# Model Matrices

The model evaluates $f$ and $w$ once on the group's direct matrices:

$$
\boxed{
\mathbf{Y}:=f(\mathbf{X}_0),\qquad
\mathbf{C}:=w(\mathbf{C}_0)
}
$$

These are the direct and indirect Ownership and Controlling Interest matrices imported by the other documents. Documents that need another graph, such as the Profit Ownership Interests of the members, evaluate $f$ on it themselves.
