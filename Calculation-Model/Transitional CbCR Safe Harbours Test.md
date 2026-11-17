# TCSH Data Matrix

## Entity Inputs

Receive the following adjusted values as inputs for each of the $N_{\mathrm{TCSH}}$ Entities in scope of the [TCSH Group](<Group.md#tcsh-group>):

$$
\mathbf{Data}_{\mathrm{TCSH}}^{\text{Entity}}
\in\mathbb{R}^{N_{\mathrm{TCSH}}\times4}.
$$

Columns, in order:

1. Adjusted CbCR Revenue
2. Adjusted CbCR PBT
3. Adjusted Tax Expense
4. SBIE

Each adjusted value is the reported amount plus signed adjustments; a positive adjustment increases the value and a negative adjustment decreases it:

| Value | Reported amount | Adjustments |
| --- | --- | --- |
| Adjusted CbCR Revenue | CbCR Revenue | Investment Entity |
| Adjusted CbCR PBT | CbCR PBT | Net Unrealised Fair Value Loss, hybrid arbitrage, Investment Entity, other required adjustments |
| Adjusted Tax Expense | Income tax expense | Non-Covered Taxes, uncertain tax positions, hybrid arbitrage, Investment Entity, disallowed deferred tax expense, other required adjustments |
| SBIE | — | Derived from Eligible Payroll Costs and the carrying value of Eligible Tangible Assets, both non-negative |

The Net Unrealised Fair Value Loss is given as a non-negative amount: the net loss from fair-value changes in Ownership Interests other than Portfolio Shareholdings, including impairment losses and reversals.

## Tested Jurisdiction Aggregation

$\mathbf{G}_{\mathrm{TCSH}}\in\{0,1\}^{M_{\mathrm{TCSH}}\times N_{\mathrm{TCSH}}}$ is the membership matrix for $M_{\mathrm{TCSH}}$ Tested Jurisdictions: rows represent Tested Jurisdictions, columns represent Entities, and an entry is 1 when the Entity belongs to that Tested Jurisdiction, and 0 otherwise.

$\mathbf{G}_{\mathrm{TCSH}}$ is constructed in [TCSH Group](<Group.md#tcsh-group>).

$$
\boxed{
\displaystyle
\mathbf{Data}_{\mathrm{TCSH}}^{\text{TJ}}
=
\mathbf{G}_{\mathrm{TCSH}}\times\mathbf{Data}_{\mathrm{TCSH}}^{\text{Entity}}
}
$$

The result is an $M_{\mathrm{TCSH}}\times4$ matrix containing the four aggregate values for each Tested Jurisdiction, in the same column order.

## Tests

For each row of $\mathbf{Data}_{\mathrm{TCSH}}^{\text{TJ}}$, let $r,p,t,s$ denote the four values, respectively, with SBIE $s\ge0$. The DM thresholds $d_R,d_P$ and SETR threshold $\tau$ are given.

1. **PBT check:** If $p\le0$, pass under RP; otherwise continue to step 2.
2. **DM:** If $(r<d_R)\land(p<d_P)$, pass; otherwise continue to step 3.
3. **SETR or RP:** If $(t\ge\tau p)\lor(p-s\le0)$, pass; otherwise fail.

$$
\boxed{\text{pass}=\text{DM}\lor\text{SETR}\lor\text{RP}}
$$

## Application

Passing a test is not sufficient for the safe harbour to apply. For each Tested Jurisdiction and Fiscal Year $y$:

$$
\boxed{\text{applied}_y=\text{elected}_y\land\text{preconditions-met}_y\land\text{pass}_y}
$$

- $\text{elected}$: the MNE Group elects the safe harbour for the Tested Jurisdiction.
- $\text{preconditions-met}$ is `False` when the Tested Jurisdiction's CbC Report is not a Qualified CbC Report or $\text{once-out}_{y-1}$ is `True`.

**Once out, always out:**

$$
\text{once-out}_y=\text{once-out}_{y-1}\lor(\text{existed}_y\land\neg\text{applied}_y)
$$

where $\text{existed}_y$ is `True` when the Tested Jurisdiction existed in Fiscal Year $y$.
