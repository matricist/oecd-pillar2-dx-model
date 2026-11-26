# Direct Ownership Matrix

$\mathbf{X}_0$ is an $N\times N$ square matrix for $N$ Entities, with owning Entities on rows, Entities owned on columns, and Ownership Interest Ratios as entries. Diagonal entries represent treasury shares.

$\mathbf{X}_0^{\mathrm{profit}}$ is the corresponding direct Profit Ownership Interest matrix. Where no separate Profit Ownership Interest Ratio is given for an entry, it equals the entry of $\mathbf{X}_0$.

**Note:** Masking the direct ownership matrix before calculating indirect ownership generally differs from masking the result afterwards. Apply the mask at the stage required by the calculation.

## Effective Periods

The matrices describe a period within the Fiscal Year during which no direct Ownership or Controlling Interest changes. Where one changes, the year is split at the change date and every validation and calculation is repeated for each period.

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

Substituting back, $y_{ij}=(l_{ij}-\delta_{ij})/l_{ii}$, which in matrix form is

$$
\mathbf{Y}=\operatorname{diag}(\mathbf{L})^{-1}(\mathbf{L}-\mathbf{I}_N)
$$

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

   - Single Entity, no self-loop: $\mathbf{L}_{:,j}=\mathbf{e}_j+\sum_{k}\mathbf{L}_{:,k}(\mathbf{X}_0)_{kj}$. No solve.
   - Single Entity with treasury shares $x_{jj}$: as above, divided by $1-x_{jj}$.
   - Cyclic component: one LU factorisation of the $|C|\times|C|$ matrix $\mathbf{I}-(\mathbf{X}_0)_{CC}$, reused for every row.
4. **Normalize:** $y_{ij}=(l_{ij}-\delta_{ij})/l_{ii}$.

**Validation comes free.** $\mathbf{I}_N-\mathbf{X}_0$ is singular exactly when some $\mathbf{I}-(\mathbf{X}_0)_{CC}$ is, so the invertibility condition is checked component by component: a singular local LU identifies the closed set of Entities that no one outside owns.

**Cost.** Dense LU costs $O(N^3)$. Here the cost is $O\bigl(\sum_C|C|^3\bigr)$ for the cyclic components plus propagation, which is linear in the number of edges times the number of ancestors per column. Column $j$ of $\mathbf{L}$ is nonzero only on $j$ and its direct and indirect owners, so $\mathbf{L}$ and $\mathbf{Y}$ stay sparse. Group structures are mostly trees with a few small cycles, so in practice this is close to linear.
