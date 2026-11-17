# Inputs

Entity vectors are indexed by the $N$ Entities and group vectors by the $M_{Calc}$ Full Calculation Groups of [ETR Calculation Group](<Group.md#etr-calculation-group>).

| Symbol | Type | Meaning |
| --- | --- | --- |
| $\mathbf{Entt\text{-}group}$ | $\{0,1\}^{N\times M_{Calc}}$ | Entities on rows, Full Calculation Groups on columns, from [ETR Calculation Group](<Group.md#etr-calculation-group>) |
| $\mathbf{globe\text{-}income}$ | $\mathbb{R}^{N}$ | GloBE Income or Loss of each Entity |
| $\mathbf{act}$ | $\mathbb{R}^{N}$ | Adjusted Covered Taxes of each Entity |
| $\mathbf{sbie}$ | $\mathbb{R}_{\ge0}^{N}$ | Substance-based Income Exclusion of each Entity |
| $\mathbf{actt\text{-}prior}$ | $\mathbb{R}_{\ge0}^{N}$ | Additional Current Top-up Tax from recalculations of prior Fiscal Years (Article 5.4.1), already allocated to Entities on the income of those years (Article 5.2.5) |
| $\mathbf{income\text{-}adj},\mathbf{act\text{-}adj}$ | $\mathbb{R}^{M_{Calc}}$ | Adjustments to GloBE Income and to Adjusted Covered Taxes that are determined only for the group as a whole |
| $\mathbf{qdmtt}$ | $\mathbb{R}_{\ge0}^{M_{Calc}}$ | Qualified Domestic Minimum Top-up Tax payable for the Fiscal Year |
| $\mathbf{ente\text{-}prior}$ | $\mathbb{R}_{\ge0}^{M_{Calc}}$ | Excess Negative Tax Expense brought forward |
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

**Effective Tax Rate and Top-up Tax Percentage** (Articles 5.1.1, 5.2.1)

The Effective Tax Rate exists only where there is Net GloBE Income. Negative Adjusted Covered Taxes do not enter it; they become Excess Negative Tax Expense. A balance brought forward reduces positive Adjusted Covered Taxes, but not below zero.

$$
\begin{aligned}
\mathbf{ente\text{-}used}&:=\mathbf{positive}\odot\min\left(\mathbf{ente\text{-}prior},[\mathbf{tax}]^{+}\right)\\
\mathbf{etr}&:=\mathbf{positive}\odot\left([\mathbf{tax}]^{+}-\mathbf{ente\text{-}used}\right)\odot\left([\mathbf{income}]^{+}\right)^{\dagger}\\
\mathbf{tt\text{-}percent}&:=\mathbf{positive}\odot[r-\mathbf{etr}]^{+}
\end{aligned}
$$

$\mathbf{etr}$ is meaningful only where $\mathbf{positive}$ is `True`; elsewhere it is 0 and $\mathbf{tt\text{-}percent}$ is 0.

**Excess Profit** (Article 5.2.2)

$$
\mathbf{excess\text{-}profit}:=\left[\mathbf{income}-\mathbf{Entt\text{-}group}^{T}\times\mathbf{sbie}\right]^{+}
$$

**Article 4.1.5**

A group without Net GloBE Income whose Adjusted Covered Taxes are below zero and below the expected amount owes the difference as Additional Current Top-up Tax, unless it elects to carry the difference forward as Excess Negative Tax Expense.

$$
\begin{aligned}
\mathbf{art\text{-}4.1.5}&:=\neg\mathbf{positive}\land(\mathbf{tax}<0)\land(\mathbf{tax}<\mathbf{expected})\\
\mathbf{actt\text{-}4.1.5}&:=(\mathbf{art\text{-}4.1.5}\land\neg\mathbf{ente\text{-}elected})\odot(\mathbf{expected}-\mathbf{tax})
\end{aligned}
$$

**Excess Negative Tax Expense carried forward**

$$
\begin{aligned}
\mathbf{ente\text{-}generated}&:=\mathbf{positive}\odot[-\mathbf{tax}]^{+}+(\mathbf{art\text{-}4.1.5}\land\mathbf{ente\text{-}elected})\odot(\mathbf{expected}-\mathbf{tax})\\
\mathbf{ente\text{-}next}&:=\mathbf{ente\text{-}prior}-\mathbf{ente\text{-}used}+\mathbf{ente\text{-}generated}
\end{aligned}
$$

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
\mathbf{key\text{-}4.1.5}&:=\left[(\mathbf{act}<0)\land(\mathbf{act}<r\cdot\mathbf{globe\text{-}income})\right]\odot(r\cdot\mathbf{globe\text{-}income}-\mathbf{act})\\
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

$\mathbf{tt\text{-}entt}$ is the Top-up Tax of each Entity used in [IIR](IIR.md).

# Not Covered

- Top-up Tax under Article 7.6.2(c).
- The calculation of Additional Current Top-up Tax from its causes (Articles 5.4.1, 7.3.5, 7.3.7); it is an input here.
- The De Minimis Exclusion (Article 5.5).
- Whether Excess Negative Tax Expense is tracked for a group under the QDMTT Safe Harbour.
