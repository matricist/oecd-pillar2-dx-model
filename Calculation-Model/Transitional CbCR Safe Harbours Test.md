# Inputs

All vectors are indexed by the $N_{\mathrm{TCSH}}$ Entities or the $M_{\mathrm{TCSH}}$ Tested Jurisdictions of the [TCSH Group](<Group.md#tcsh-group>).

| Symbol | Type | Meaning |
| --- | --- | --- |
| $\mathbf{G}_{\mathrm{TCSH}}$ | $\{0,1\}^{M_{\mathrm{TCSH}}\times N_{\mathrm{TCSH}}}$ | Tested Jurisdictions on rows, Entities on columns, from [TCSH Group](<Group.md#tcsh-group>) |
| $\mathbf{rev},\mathbf{pbt},\mathbf{tax}$ | $\mathbb{R}^{N_{\mathrm{TCSH}}}$ | Adjusted CbCR Revenue, Adjusted CbCR PBT, and Adjusted Tax Expense |
| $\mathbf{sbie}$ | $\mathbb{R}_{\ge0}^{N_{\mathrm{TCSH}}}$ | Substance-based Income Exclusion |
| $d_{R},d_{P}$ | $\mathbb{R}$ | De minimis thresholds for revenue and PBT |
| $\tau$ | $[0,1]$ | Simplified ETR threshold of the Fiscal Year |
| $\mathbf{elected},\mathbf{qualified\text{-}cbcr},\mathbf{existed}$ | $\{0,1\}^{M_{\mathrm{TCSH}}}$ | Election made, Qualified CbC Report available, Tested Jurisdiction exists |

# Calculation

**Tested Jurisdiction aggregation**

$$
(\mathbf{r}\;\;\mathbf{p}\;\;\mathbf{t}\;\;\mathbf{s}):=\mathbf{G}_{\mathrm{TCSH}}\times(\mathbf{rev}\;\;\mathbf{pbt}\;\;\mathbf{tax}\;\;\mathbf{sbie})
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

$\mathbf{applied}$ identifies the Tested Jurisdictions to which the safe harbour applies. A Tested Jurisdiction that existed but did not apply it can never apply it again. $\mathbf{once\text{-}out}_{y-1}$ is carried to year $y$ by [Dynamics](<Dynamics.md#carry-forward>) on $\mathbf{tcsh\text{-}key}$.
