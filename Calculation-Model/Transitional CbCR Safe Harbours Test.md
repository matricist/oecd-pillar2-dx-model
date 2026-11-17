# Inputs

All vectors are indexed by the $N_{\mathrm{TCSH}}$ Entities or the $M_{\mathrm{TCSH}}$ Tested Jurisdictions of the [TCSH Group](<Group.md#tcsh-group>).

| Symbol | Type | Meaning |
| --- | --- | --- |
| $\mathbf{G}_{\mathrm{TCSH}}$ | $\{0,1\}^{M_{\mathrm{TCSH}}\times N_{\mathrm{TCSH}}}$ | Tested Jurisdictions on rows, Entities on columns, from [TCSH Group](<Group.md#tcsh-group>) |
| $\mathbf{rev},\mathbf{pbt},\mathbf{tax}$ | $\mathbb{R}^{N_{\mathrm{TCSH}}}$ | CbCR Revenue, CbCR PBT, and income tax expense |
| $\mathbf{Adj}_{R},\mathbf{Adj}_{P},\mathbf{Adj}_{T}$ | $\mathbb{R}^{N_{\mathrm{TCSH}}\times K}$ | Signed adjustments to the three amounts, one column per adjustment |
| $\mathbf{payroll},\mathbf{tangible}$ | $\mathbb{R}_{\ge0}^{N_{\mathrm{TCSH}}}$ | Eligible Payroll Costs and carrying value of Eligible Tangible Assets |
| $\rho_{P},\rho_{A}$ | $[0,1]$ | Substance-based Income Exclusion rates of the Fiscal Year |
| $d_{R},d_{P}$ | $\mathbb{R}$ | De minimis thresholds for revenue and PBT |
| $\tau$ | $[0,1]$ | Simplified ETR threshold of the Fiscal Year |
| $\mathbf{elected},\mathbf{qualified\text{-}cbcr},\mathbf{existed}$ | $\{0,1\}^{M_{\mathrm{TCSH}}}$ | Election made, Qualified CbC Report available, Tested Jurisdiction exists |

The adjustment columns are:

| Matrix | Columns |
| --- | --- |
| $\mathbf{Adj}_{R}$ | Investment Entity |
| $\mathbf{Adj}_{P}$ | Net Unrealised Fair Value Loss, hybrid arbitrage, Investment Entity, other |
| $\mathbf{Adj}_{T}$ | Non-Covered Taxes, uncertain tax positions, hybrid arbitrage, Investment Entity, disallowed deferred tax expense, other |

A positive entry increases the amount. The Net Unrealised Fair Value Loss is entered as a non-negative amount.

# Calculation

**Entity data**

$$
\mathbf{Data}_{\mathrm{TCSH}}^{\text{Entity}}:=
\begin{pmatrix}
\mathbf{rev}+\mathbf{Adj}_{R}\times\mathbf{1}&
\mathbf{pbt}+\mathbf{Adj}_{P}\times\mathbf{1}&
\mathbf{tax}+\mathbf{Adj}_{T}\times\mathbf{1}&
\rho_{P}\,\mathbf{payroll}+\rho_{A}\,\mathbf{tangible}
\end{pmatrix}
$$

The four columns are Adjusted CbCR Revenue, Adjusted CbCR PBT, Adjusted Tax Expense, and SBIE.

**Tested Jurisdiction aggregation**

$$
\begin{pmatrix}\mathbf{r}&\mathbf{p}&\mathbf{t}&\mathbf{s}\end{pmatrix}
:=\mathbf{G}_{\mathrm{TCSH}}\times\mathbf{Data}_{\mathrm{TCSH}}^{\text{Entity}}
$$

**Tests**

$$
\begin{aligned}
\mathbf{dm}&:=(\mathbf{r}<d_{R})\land(\mathbf{p}<d_{P})\\
\mathbf{setr}&:=(\mathbf{p}>0)\land(\mathbf{t}\ge\tau\,\mathbf{p})\\
\mathbf{rp}&:=\mathbf{p}\le\mathbf{s}\\
\mathbf{pass}&:=\mathbf{dm}\lor\mathbf{setr}\lor\mathbf{rp}
\end{aligned}
$$

$\mathbf{dm}$ is the de minimis test, $\mathbf{setr}$ the Simplified ETR test, and $\mathbf{rp}$ the routine profits test. A Tested Jurisdiction with $\mathbf{p}\le0$ passes under $\mathbf{rp}$, since $\mathbf{s}\ge0$.

**Application**

For Fiscal Year $y$:

$$
\begin{aligned}
\mathbf{preconditions\text{-}met}_{y}&:=\mathbf{qualified\text{-}cbcr}_{y}\land\neg\mathbf{once\text{-}out}_{y-1}\\
\mathbf{applied}_{y}&:=\mathbf{elected}_{y}\land\mathbf{preconditions\text{-}met}_{y}\land\mathbf{pass}_{y}\\
\mathbf{once\text{-}out}_{y}&:=\mathbf{once\text{-}out}_{y-1}\lor(\mathbf{existed}_{y}\land\neg\mathbf{applied}_{y})
\end{aligned}
$$

$\mathbf{applied}$ identifies the Tested Jurisdictions to which the safe harbour applies. A Tested Jurisdiction that existed but did not apply it can never apply it again.
