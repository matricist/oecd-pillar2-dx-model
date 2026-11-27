# Inputs

Entity vectors are indexed by the $N$ Entities and group vectors by the $M_{Calc}$ Full Calculation Groups of [ETR Calculation Group](<Group.md#etr-calculation-group>). A group input belongs to the group's $\mathbf{group\text{-}key}$, so it follows an Entity that [moves](<Location.md#fixed-point>).

| Symbol | Type | Meaning |
| --- | --- | --- |
| $\mathbf{Entt\text{-}group}$ | $\{0,1\}^{N\times M_{Calc}}$ | Entities on rows, Full Calculation Groups on columns, from [ETR Calculation Group](<Group.md#etr-calculation-group>) |
| $\mathbf{globe\text{-}income}$ | $\mathbb{R}^{N}$ | GloBE Income or Loss of each Entity |
| $\mathbf{act}$ | $\mathbb{R}^{N}$ | Adjusted Covered Taxes of each Entity |
| $\mathbf{sbie}$ | $\mathbb{R}_{\ge0}^{N}$ | Substance-based Income Exclusion of each Entity |
| $\mathbf{actt\text{-}prior}$ | $\mathbb{R}_{\ge0}^{N}$ | Additional Current Top-up Tax from recalculations of prior Fiscal Years (Article 5.4.1), already allocated to Entities on the income of those years (Article 5.2.5), from [Recalculation](#recalculation-of-earlier-fiscal-years) |
| $\mathbf{income\text{-}adj},\mathbf{act\text{-}adj}$ | $\mathbb{R}^{M_{Calc}}$ | Adjustments to GloBE Income and to Adjusted Covered Taxes that are determined only for the group as a whole |
| $\mathbf{qdmtt}$ | $\mathbb{R}_{\ge0}^{M_{Calc}}$ | Qualified Domestic Minimum Top-up Tax payable for the Fiscal Year |
| $\mathbf{ente\text{-}prior}$ | $\mathbb{R}_{\ge0}^{M_{Calc}}$ | Excess Negative Tax Expense brought forward, read for $\mathbf{group\text{-}key}$ as in [Continuity Across Fiscal Years](<Group.md#continuity-across-fiscal-years>) |
| $\mathbf{qsh}$ | $\{0,1\}^{M_{Calc}}$ | The QDMTT Safe Harbour applies |
| $\mathbf{ente\text{-}elected}$ | $\{0,1\}^{M_{Calc}}$ | The Excess Negative Tax Expense procedure is elected in place of Article 4.1.5 |
| $r$ | $[0,1]$ | Minimum Rate, 0.15 |

$[x]^{+}:=\max(x,0)$, and $x^{\dagger}:=1/x$ for $x>0$ and $0$ for $x=0$; both apply element-wise, and $\dagger$ applies to the diagonal entries of a diagonal matrix. $\odot$ denotes element-wise multiplication; comparisons and logical operations are element-wise, and Boolean entries are treated as 1 or 0 in arithmetic.

# Calculation

**Group amounts**

$$
\begin{aligned}
\mathbf{income}&:=\mathbf{Entt\text{-}group}^{T}\times\mathbf{globe\text{-}income}+\mathbf{income\text{-}adj}\\
\mathbf{tax}&:=\mathbf{Entt\text{-}group}^{T}\times\mathbf{act}+\mathbf{act\text{-}adj}\\
\mathbf{positive}&:=\mathbf{income}>0\\
\mathbf{expected}&:=r\cdot\mathbf{income}
\end{aligned}
$$

$\mathbf{income}$ is the Net GloBE Income or Loss of each group, $\mathbf{tax}$ its Adjusted Covered Taxes, and $\mathbf{expected}$ its Expected Adjusted Covered Taxes Amount.

**Shortfall** (Articles 4.1.5, 5.1.1, 5.2.1)

A balance of Excess Negative Tax Expense brought forward reduces positive Adjusted Covered Taxes, but not below zero. Where there is Net GloBE Income, negative Adjusted Covered Taxes count as zero. The resulting numerator falls short of the expected amount by $\mathbf{shortfall}$:

$$
\begin{aligned}
\mathbf{ente\text{-}left}&:=\left[\mathbf{ente\text{-}prior}-\mathbf{positive}\odot[\mathbf{tax}]^{+}\right]^{+},\qquad\mathbf{ente\text{-}used}:=\mathbf{ente\text{-}prior}-\mathbf{ente\text{-}left}\\
\mathbf{numerator}&:=\mathbf{positive}\odot\left([\mathbf{tax}]^{+}-\mathbf{ente\text{-}used}\right)+\neg\mathbf{positive}\odot\mathbf{tax}\\
\mathbf{shortfall}&:=\left[\mathbf{expected}-\mathbf{numerator}\right]^{+}
\end{aligned}
$$

The shortfall becomes Top-up Tax, Additional Current Top-up Tax, or Excess Negative Tax Expense:

| | Net GloBE Income | No Net GloBE Income |
| --- | --- | --- |
| $\mathbf{tax}\ge0$ | Top-up Tax on Excess Profit | No shortfall |
| $\mathbf{tax}<0$ | Top-up Tax on Excess Profit, with $[-\mathbf{tax}]^{+}$ carried forward | Additional Current Top-up Tax under Article 4.1.5, or carried forward where elected |

Without Net GloBE Income, $\mathbf{expected}\le0$, so a shortfall implies $\mathbf{tax}<\mathbf{expected}\le0$.

**Effective Tax Rate, Top-up Tax Percentage and Excess Profit** (Articles 5.1.1, 5.2.1, 5.2.2)

$$
\begin{aligned}
\mathbf{etr}&:=\mathbf{positive}\odot\mathbf{numerator}\odot\mathbf{income}^{\dagger}\\
\mathbf{tt\text{-}percent}&:=\mathbf{positive}\odot\mathbf{shortfall}\odot\mathbf{income}^{\dagger}\\
\mathbf{excess\text{-}profit}&:=\left[\mathbf{income}-\mathbf{Entt\text{-}group}^{T}\times\mathbf{sbie}\right]^{+}
\end{aligned}
$$

$\mathbf{tt\text{-}percent}=[r-\mathbf{etr}]^{+}$ wherever $\mathbf{positive}$ is `True`; elsewhere both are 0.

**Article 4.1.5 and Excess Negative Tax Expense**

$$
\begin{aligned}
\mathbf{art\text{-}4.1.5}&:=\neg\mathbf{positive}\land(\mathbf{shortfall}>0)\\
\mathbf{actt\text{-}4.1.5}&:=(\mathbf{art\text{-}4.1.5}\land\neg\mathbf{ente\text{-}elected})\odot\mathbf{shortfall}\\
\mathbf{ente\text{-}generated}&:=\mathbf{positive}\odot[-\mathbf{tax}]^{+}+(\mathbf{art\text{-}4.1.5}\land\mathbf{ente\text{-}elected})\odot\mathbf{shortfall}\\
\mathbf{ente\text{-}next}&:=\mathbf{ente\text{-}left}+\mathbf{ente\text{-}generated}
\end{aligned}
$$

$\mathbf{ente\text{-}next}$ is written for $\mathbf{group\text{-}key}$ as in [Continuity Across Fiscal Years](<Group.md#continuity-across-fiscal-years>). From one Fiscal Year to the next the balance follows Lindley's recursion $b'=[b-a]^{+}+g$, which is linear in the max-plus algebra. Unrolled, the balance left after a year is the largest of zero and, for each earlier starting year, the amounts generated since then less those absorbed since then, with the opening balance counted from the first year.

**Jurisdictional Top-up Tax** (Article 5.2.3)

$$
\begin{aligned}
\mathbf{regular}&:=\mathbf{tt\text{-}percent}\odot\mathbf{excess\text{-}profit}\\
\mathbf{actt}&:=\mathbf{actt\text{-}4.1.5}+\mathbf{Entt\text{-}group}^{T}\times\mathbf{actt\text{-}prior}\\
\mathbf{gross}&:=\mathbf{regular}+\mathbf{actt}
\end{aligned}
$$

$$
\boxed{\mathbf{tt\text{-}group}:=\neg\mathbf{qsh}\odot\left[\mathbf{gross}-\mathbf{qdmtt}\right]^{+}}
$$

$\mathbf{regular}$ is Top-up Tax Percentage times Excess Profit, and $\mathbf{actt}$ is the Additional Current Top-up Tax of the group. Under the QDMTT Safe Harbour the Top-up Tax is zero.

**Allocation to Entities** (Articles 5.2.4, 5.2.5, 5.4.3)

Each of the three parts of $\mathbf{gross}$ has its own allocation key. The QDMTT reduces the three parts in the same proportion, $\boldsymbol{\theta}$.

$$
\begin{aligned}
\boldsymbol{\theta}&:=\mathbf{tt\text{-}group}\odot\mathbf{gross}^{\dagger}\\
\mathbf{key}&:=[\mathbf{globe\text{-}income}]^{+}\\
\mathbf{key\text{-}4.1.5}&:=(\mathbf{act}<0)\odot\left[r\cdot\mathbf{globe\text{-}income}-\mathbf{act}\right]^{+}\\
\mathbf{A}(\mathbf{k})&:=\operatorname{diag}(\mathbf{k})\times\mathbf{Entt\text{-}group}\times\operatorname{diag}\left(\mathbf{Entt\text{-}group}^{T}\times\mathbf{k}\right)^{\dagger}
\end{aligned}
$$

$\mathbf{A}(\mathbf{k})$ gives each Entity its share of the key $\mathbf{k}$ within its group. The regular part is allocated on the GloBE Income of the Entities that have GloBE Income, the Article 4.1.5 part on the shortfall of the Entities whose own Adjusted Covered Taxes are below zero and below their expected amount, and the prior-year part stays with the Entities to which it was allocated.

$$
\boxed{
\begin{aligned}
\mathbf{tt\text{-}entt}:={}&\mathbf{A}(\mathbf{key})\times(\boldsymbol{\theta}\odot\mathbf{regular})\\
&+\mathbf{A}(\mathbf{key\text{-}4.1.5})\times(\boldsymbol{\theta}\odot\mathbf{actt\text{-}4.1.5})\\
&+(\mathbf{Entt\text{-}group}\times\boldsymbol{\theta})\odot\mathbf{actt\text{-}prior}
\end{aligned}
}
$$

The allocation preserves the group amount,

$$
\mathbf{Entt\text{-}group}^{T}\times\mathbf{tt\text{-}entt}=\mathbf{tt\text{-}group},
$$

provided that a group with $\mathbf{actt\text{-}4.1.5}>0$ has at least one Entity with $\mathbf{key\text{-}4.1.5}>0$. A group with $\mathbf{regular}>0$ always has an Entity with GloBE Income.

$\mathbf{tt\text{-}entt}$ is the Top-up Tax of each Entity. It decides which Flow-through Entities are [required to apply an IIR](<Location.md#required-to-apply-an-iir>), and with the final location it is the Top-up Tax used in [IIR](IIR.md).

# Recalculation of Earlier Fiscal Years

Where a Fiscal Year $\tau$ is recalculated in year $t$ (Articles 4.6.1 and 5.4.1), the whole calculation of $\tau$ is run again with the corrected input. Let $\mathbf{tt\text{-}entt}_\tau^{\mathrm{re}}$ and $\mathbf{tt\text{-}group}_\tau^{\mathrm{re}}$ be its results and $\mathbf{tt\text{-}entt}_\tau$, $\mathbf{tt\text{-}group}_\tau$ those filed. The increase of each group is Additional Current Top-up Tax of year $t$, already allocated to the Entities of year $\tau$:

$$
\boxed{
\mathbf{actt\text{-}prior}_t:=\sum_{\tau}\left(\mathbf{tt\text{-}entt}_\tau^{\mathrm{re}}-\mathbf{tt\text{-}entt}_\tau\right)\odot\left(\mathbf{Entt\text{-}group}_\tau\times\left[\mathbf{tt\text{-}group}_\tau^{\mathrm{re}}>\mathbf{tt\text{-}group}_\tau\right]\right)
}
$$

The sum runs over the years recalculated in $t$, and each Entity of year $\tau$ is placed in year $t$ by $\mathbf{entity\text{-}id}$.

# Not Covered

- Top-up Tax under Article 7.6.2(c).
- The calculation of Additional Current Top-up Tax from its causes (Articles 5.4.1, 7.3.5, 7.3.7); it is an input here.
- The De Minimis Exclusion (Article 5.5).
- Whether Excess Negative Tax Expense is tracked for a group under the QDMTT Safe Harbour.
- A recalculation that lowers a group's Top-up Tax.
- The deferred tax asset of the GloBE Loss Election (Article 4.5), which would follow the same recursion as the Excess Negative Tax Expense.
- The recapture of deferred tax liabilities by year of origin (Article 4.4.4), which would add a balance for each year of origin, aged each year by a shift matrix, and the five-year elections.
