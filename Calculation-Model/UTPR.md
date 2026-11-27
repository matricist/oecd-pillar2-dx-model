# Inputs

All inputs are for the same $N$ Entities and $M$ jurisdictions.

| Symbol | Type | Meaning |
| --- | --- | --- |
| $\mathbf{H},\mathbf{Net\text{-}iir}^{Q}$ | $[0,1]^{N\times N}$ | Ownership with the Parent Entities payable under a Qualified IIR absorbing, and its payable cells, from [IIR](<IIR.md#net-income-inclusion-ratio>) |
| $g$ | | Unit-diagonal function, $g(\mathbf{A}):=\mathbf{A}-\operatorname{diag}(\mathbf{A})+\mathbf{I}_N$, from [IIR](<IIR.md#unit-diagonal-function>) |
| $\mathbf{Iir\text{-}payable}$ | $\{0,1\}^{N\times N}$ | IIR payability, from [Taxing Rights](<Taxing Rights.md#iir-payability>) |
| $\mathbf{self\text{-}payable},\mathbf{group\text{-}upe},\mathbf{qiir}$ | $\{0,1\}^{N\times1}$ | Parent Entities paying their own Top-up Tax, UPEs (including a UPE that is an Excluded Entity), and Entities in a Qualified IIR jurisdiction, from [Taxing Rights](<Taxing Rights.md>) |
| $\mathbf{tt\text{-}entt}$ | $\mathbb{R}_{\ge0}^{N}$ | Top-up Tax of each Entity, from [Top-up Tax Calculation](<Top-up Tax Calculation.md>) |
| $\mathbf{ce},\mathbf{ie}$ | $\{0,1\}^{N\times1}$ | CEs and Investment Entities |
| $\mathbf{Entt\text{-}jur}$ | $\{0,1\}^{N\times M}$ | Entity-to-jurisdiction matrix |
| $\mathbf{emp},\mathbf{tan}$ | $\mathbb{R}_{\ge0}^{N}$ | Number of Employees and Net Book Value of Tangible Assets of each Entity |
| $\mathbf{qutpr\text{-}impl}$ | $\{0,1\}^{M\times1}$ | The jurisdiction has a Qualified UTPR in force |
| $\mathbf{utpr\text{-}zero}$ | $\{0,1\}^{M\times1}$ | An amount allocated to the jurisdiction in a prior Fiscal Year has not yet been collected (Article 2.6.3) |

$\operatorname{diag}$ retains the diagonal of a matrix or builds a diagonal matrix from a vector. $[x]^{+}:=\max(x,0)$, and $x^{\dagger}:=1/x$ for $x>0$ and $0$ for $x=0$, applied to the diagonal entries of a diagonal matrix. $\odot$ denotes element-wise multiplication; comparisons and logical operations are element-wise, and Boolean entries are treated as 1 or 0 in arithmetic.

# Top-up Tax Left for the UTPR

The Top-up Tax of a low-taxed Entity goes to the UTPR to the extent that no Qualified IIR brings it into charge (Article 2.5).

## Charge under a Qualified IIR

Only a Qualified IIR counts. With $\mathbf{Q}:=\operatorname{diag}(\mathbf{qiir})\times\mathbf{Iir\text{-}payable}$, $\mathbf{Net\text{-}iir}^{Q}$ is the share of each Entity that each Parent Entity brings into charge under a Qualified IIR, from [IIR](<IIR.md#net-income-inclusion-ratio>). A Parent Entity that pays its own Top-up Tax under a Qualified IIR is added on the diagonal:

$$
\mathbf{Charged}:=\mathbf{Net\text{-}iir}^{Q}+\operatorname{diag}(\mathbf{self\text{-}payable}\land\mathbf{qiir})
$$

$(\mathbf{Charged})_{kj}$ is the share of the Top-up Tax of Entity $j$ that Parent Entity $k$ pays under a Qualified IIR.

## UPE Residual

$\mathbf{Residual}$ is the part of each UPE's interest in an Entity that reaches the UPE without having been charged under a Qualified IIR. A UPE counts as holding all of itself. A UPE that is an Excluded Entity counts too: it applies no IIR, but Article 2.5.2 looks at the UPE's Ownership Interests whatever the UPE is.

$$
\boxed{\mathbf{Residual}:=\operatorname{diag}(\mathbf{group\text{-}upe})\times\left(g(\mathbf{H})\odot(\mathbf{1}_{N\times N}-\mathbf{Q})\right)\times\operatorname{diag}\left(\mathbf{1}_N-(\mathbf{self\text{-}payable}\land\mathbf{qiir})\right)}
$$

$\mathbf{H}$ already leaves out every path through a Parent Entity that pays under a Qualified IIR, so for a UPE $u$ and an Entity $j\ne u$, $(\mathbf{Residual})_{uj}=(\mathbf{H})_{uj}$ is the UPE's interest in $j$ that no Qualified IIR charges.

- A UPE that itself pays for $j$ under a Qualified IIR has no residual in $j$: the factor $\mathbf{1}_{N\times N}-\mathbf{Q}$.
- An Entity that pays its own Top-up Tax under a Qualified IIR leaves no residual to anyone: the right factor.
- Paths through another UPE count, as do paths through an Excluded Entity.

## UTPR Top-up Tax

$$
\begin{aligned}
\mathbf{r}&:=\mathbf{Residual}^{T}\times\mathbf{1}_N\\
\mathbf{utpr\text{-}payable}&:=\mathbf{r}>0\\
\mathbf{utpr\text{-}ratio}&:=\mathbf{utpr\text{-}payable}\odot\left[\mathbf{1}_N-\mathbf{Charged}^{T}\times\mathbf{1}_N\right]^{+}\\
\mathit{total}&:=\mathbf{utpr\text{-}ratio}^{T}\times\mathbf{tt\text{-}entt}
\end{aligned}
$$

- $\mathbf{r}=0$: every interest the UPEs hold in the Entity is held through Parent Entities charged under a Qualified IIR, and its Top-up Tax is reduced to zero (Article 2.5.2).
- $\mathbf{r}>0$: its Top-up Tax is reduced by the shares charged under a Qualified IIR (Article 2.5.3).
- $\mathit{total}$ is the Total UTPR Top-up Tax Amount (Article 2.5.1).

# Allocation to Jurisdictions

The Total UTPR Top-up Tax Amount is divided among the UTPR jurisdictions, half on Employees and half on Tangible Assets (Article 2.6). Whether a jurisdiction is a UTPR jurisdiction is decided by legislation alone, see [Taxing Rights](<Taxing Rights.md#utpr-taxing-rights>).

$$
\begin{aligned}
\mathbf{utpr\text{-}jur}&:=\mathbf{qutpr\text{-}impl}\land\left(\neg\mathbf{utpr\text{-}zero}\lor\left[\mathbf{qutpr\text{-}impl}^{T}\times\neg\mathbf{utpr\text{-}zero}=0\right]\right)\\
\mathbf{Data}&:=\operatorname{diag}(\mathbf{ce}\land\neg\mathbf{ie})\times(\mathbf{emp}\;\;\mathbf{tan})\\
\mathbf{Data\text{-}jur}&:=\operatorname{diag}(\mathbf{utpr\text{-}jur})\times\mathbf{Entt\text{-}jur}^{T}\times\mathbf{Data}\\
\mathbf{utpr\text{-}percentage}&:=\mathbf{Data\text{-}jur}\times\operatorname{diag}\left(\mathbf{Data\text{-}jur}^{T}\times\mathbf{1}_M\right)^{\dagger}\times\begin{pmatrix}0.5\\0.5\end{pmatrix}\\
\mathbf{utpr\text{-}amount}&:=\mathit{total}\cdot\mathbf{utpr\text{-}percentage}
\end{aligned}
$$

- $\mathbf{utpr\text{-}jur}$ leaves out a jurisdiction that has not yet collected a prior-year amount, unless that is true of every UTPR jurisdiction (Articles 2.6.3 and 2.6.4).
- $\mathbf{Data}$ counts CEs only, and no Investment Entities (Article 2.6.2(a)); JVs and JV Subsidiaries are not CEs.
- $\mathbf{utpr\text{-}amount}$ is the UTPR Top-up Tax Amount of each jurisdiction.

# Implementation

$\mathbf{Residual}$ is read from the UPE rows of $\mathbf{H}$, which [IIR](<IIR.md#implementation-notes>) calculates from $\mathbf{Y}$.

# Open

- **JV Group members.** $\mathit{total}$ includes the Top-up Tax of JVs and JV Subsidiaries. To be confirmed against Article 6.4.
- **Flow-through Entities.** The allocation of their Employees and Tangible Assets (Article 2.6.2(b)) is not modelled.
- **Initial phase of international activity.** Article 9.3 reduces the UTPR Top-up Tax to zero; not modelled.
- **UTPR Safe Harbours.** Not modelled.
- **Investment Entities.** The Article 7.4 adjustment of IIR is not yet carried into $\mathbf{Charged}$.
- **Deemed GloBE Income.** Where Additional Current Top-up Tax arises without Net GloBE Income, Articles 5.4.2 and 5.4.3 give each Entity a deemed GloBE Income for the IIR; not modelled.
- **Several Fiscal Years.** Ownership, Parent Entity status, and Qualified IIR status change from year to year, so $\mathbf{Net\text{-}iir}$ is a result of one Fiscal Year. Carry-forwards move between Fiscal Years as in [Continuity Across Fiscal Years](<Group.md#continuity-across-fiscal-years>).
