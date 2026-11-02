# TCSH Data Matrix

## Entity Inputs

Receive the following adjusted values as inputs for each of the $N_{\mathrm{TCSH}}$ tested Entities:

$$
\mathbf{Data}_{\mathrm{TCSH}}^{\text{Entity}}
\in\mathbb{R}^{N_{\mathrm{TCSH}}\times4}.
$$

Columns, in order:

1. Adjusted CbCR Revenue
2. Adjusted CbCR PBT
3. Adjusted Tax Expense
4. SBIE

## Tested Jurisdiction Aggregation

$\mathbf{G}_{\mathrm{TCSH}}\in\{0,1\}^{M_{\mathrm{TCSH}}\times N_{\mathrm{TCSH}}}$ is the membership matrix for $M_{\mathrm{TCSH}}$ Tested Jurisdictions: rows represent Tested Jurisdictions, columns represent Entities, and an entry is 1 when the Entity belongs to that Tested Jurisdiction, and 0 otherwise.

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
