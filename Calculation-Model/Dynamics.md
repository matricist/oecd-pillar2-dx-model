The other documents calculate one Fiscal Year. This document chains Fiscal Years: what each year passes to the next, and how it finds its way when groups change.

# Time

The model has two time scales.

- **Fiscal Year** $t$. The state below is read at the start of $t$ and written at its end.
- **Effective period** within $t$. Where a direct Ownership or Controlling Interest changes, the year is split into [effective periods](<Ownership Interest.md#effective-periods>), each calculated for that period alone. [Period Changes](<Ownership Interest.md#period-changes>) updates $\mathbf{L}$ from one period to the next. The state does not change between periods.

One Fiscal Year is the map

$$
\boxed{(\mathbf{x}_{t+1},\ \mathbf{out}_t):=F(\mathbf{x}_t,\ \mathbf{in}_t)}
$$

where $\mathbf{in}_t$ is the year's input (ownership, control, amounts, legislation), $\mathbf{out}_t$ its results (Top-up Tax, IIR and UTPR allocation, return), and $F$ is the [workflow](Workflow.md) of the other documents.

# State

| State | Indexed by | Read by | Written by |
| --- | --- | --- | --- |
| Excess Negative Tax Expense | $\mathbf{group\text{-}key}$ of [Group](<Group.md#etr-calculation-group>) | $\mathbf{ente\text{-}prior}$ of [Top-up Tax Calculation](<Top-up Tax Calculation.md>) | $\mathbf{ente\text{-}next}$ |
| Tested Jurisdiction excluded from the TCSH | $\mathbf{tcsh\text{-}key}$ of [Group](<Group.md#tcsh-group>) | $\mathbf{once\text{-}out}_{y-1}$ of [TCSH](<Transitional CbCR Safe Harbours Test.md>) | $\mathbf{once\text{-}out}_{y}$ |
| Filed Top-up Tax of each Entity | $\mathbf{entity\text{-}id}$ | [Recalculation](#recalculation-of-earlier-fiscal-years) | $\mathbf{tt\text{-}entt}$ |

# Carry-Forward

A group of year $t+1$ continues a group of year $t$ when their keys are equal. For the $M_t$ groups of year $t$ and the $M_{t+1}$ groups of year $t+1$:

$$
\boxed{
(\mathbf{P}_t)_{gh}:=\bigl[\mathbf{group\text{-}key}_t(g)=\mathbf{group\text{-}key}_{t+1}(h)\bigr],
\qquad
\mathbf{ente\text{-}prior}_{t+1}:=\mathbf{P}_t^{T}\times\mathbf{ente\text{-}next}_t
}
$$

Keys are unique within a year, so each row and each column of $\mathbf{P}_t$ has at most one 1. The TCSH state is carried the same way, with $\mathbf{P}_t^{\mathrm{TCSH}}$ built from $\mathbf{tcsh\text{-}key}$; for year $t+1$,

$$
\mathbf{once\text{-}out}_{y-1}:=\mathbf{P}_t^{\mathrm{TCSH}\,T}\times\mathbf{once\text{-}out}_{t}.
$$

A Tested Jurisdiction of year $t+1$ with no match starts with `False`.

# Recalculation of Earlier Fiscal Years

Where a Fiscal Year $\tau<t$ is recalculated (Articles 4.6.1 and 5.4.1), $F$ is evaluated again for $\tau$ with the corrected input. Let $\mathbf{tt\text{-}entt}_\tau^{\mathrm{re}}$ and $\mathbf{tt\text{-}group}_\tau^{\mathrm{re}}$ be its results and $\mathbf{tt\text{-}entt}_\tau$, $\mathbf{tt\text{-}group}_\tau$ those filed. The increase of each group is Additional Current Top-up Tax of year $t$, already allocated to the Entities of year $\tau$:

$$
\boxed{
\mathbf{actt\text{-}prior}_t:=\sum_{\tau}\left(\mathbf{tt\text{-}entt}_\tau^{\mathrm{re}}-\mathbf{tt\text{-}entt}_\tau\right)\odot\left(\mathbf{Entt\text{-}group}_\tau\times\left[\mathbf{tt\text{-}group}_\tau^{\mathrm{re}}>\mathbf{tt\text{-}group}_\tau\right]\right)
}
$$

The sum runs over the years recalculated in $t$, and each Entity of year $\tau$ is placed in year $t$ by $\mathbf{entity\text{-}id}$.

# Limits

- **Group that ends.** A group of year $t$ whose key does not appear in year $t+1$ passes nothing on: its row of $\mathbf{P}_t$ is zero and its balance lapses.
- **Group that splits.** The part that keeps the top Entity keeps the whole balance; the other parts start at zero.
- **Top Entity that changes.** A group whose top Entity changes has a new key, so it starts at zero even if its members are the same.
- **Articles 6.2 and 6.3.** Whether these results match the treatment of Entities joining or leaving the group, and of transfers of assets and liabilities, is not decided here.
- **Decreases on recalculation.** A recalculation that lowers a group's Top-up Tax is not carried to year $t$.
- **State not yet modelled.** The deferred tax asset of the GloBE Loss Election (Article 4.5), the recapture of deferred tax liabilities by year of origin (Article 4.4.4), and the five-year elections. The recapture would add a state indexed by year of origin, aged each year by a shift matrix.
