# Taxing Rights

## Matrix Masking

For a Boolean indicator vector $\mathbf{v}$, $\operatorname{diag}(\mathbf{v})\times\mathbf{A}$ masks rows of $\mathbf{A}$, while $\mathbf{A}\times\operatorname{diag}(\mathbf{v})$ masks columns: entries corresponding to `True` are retained, and those corresponding to `False` are set to zero. Comparisons such as $\mathbf{A}>0$ are element-wise and return Boolean values; Boolean entries are treated as 1 or 0 in matrix multiplication.

## Identification of Parent Entities

### UPE

$\mathbf{upe}$ is an $N\times1$ Boolean column vector for $N$ Entities. An entry is `True` if the Entity is a UPE and is not an Excluded Entity, and `False` otherwise.

### POPE and IPE

$\mathbf{parent}$ is an $N\times1$ Boolean column vector identifying POPE and IPE candidates. An entry is `True` if the Entity is a CE that directly or indirectly owns an Ownership Interest in another CE and is not a UPE, PE, IE, EE, JV, or JV Subsidiary, and `False` otherwise. Indirect ownership is calculated on the full ownership graph, including paths through EEs.

$f$ converts direct ownership ratios into direct and indirect ownership ratios, accounting for circular ownership and treasury shares. Thus, $f(\mathbf{A})$ takes a direct ownership matrix $\mathbf{A}$ as input and returns the corresponding direct and indirect ownership matrix; see [Ownership Interest](<Ownership Interest.md#direct-method>).

For the more-than-20% POPE test, retain only direct Profit Ownership Interests between CEs:

$$
\mathbf{X}_0^{\mathrm{profit,ce}}
:=
\operatorname{diag}(\mathbf{ce})\times\mathbf{X}_0^{\mathrm{profit}}\times\operatorname{diag}(\mathbf{ce}),
$$

$$
\mathbf{Y}^{\mathrm{profit,ce}}
:=
f(\mathbf{X}_0^{\mathrm{profit,ce}}).
$$

Define the MNE-held and externally held Profit Ownership Interests in each candidate:

Sum the UPE rows of $\mathbf{Y}^{\mathrm{profit,ce}}$ to obtain the group's direct and indirect Profit Ownership Interest in each Entity, retaining only POPE and IPE candidates. The result is written as the row vector $\mathbf{mne}^{T}$; $\mathbf{mne}$ is the corresponding $N\times1$ column vector.

$$
\begin{gathered}
\mathbf{mne}^{T}:=\\
\mathbf{1}_N^{T}\times\operatorname{diag}(\mathbf{upe})
\times\mathbf{Y}^{\mathrm{profit,ce}}\times\operatorname{diag}(\mathbf{parent})
\end{gathered}
$$

$$
\mathbf{external}:=\mathbf{1}_N-\mathbf{mne}.
$$

The POPE and IPE indicators are then:

$$
\mathbf{pope}
:=
\mathbf{parent}\land(\mathbf{external}>0.2),
$$

$$
\mathbf{ipe}
:=
\mathbf{parent}\land\neg\mathbf{pope}.
$$

## IIR Payability

Let $M$ be the number of jurisdictions. $\mathbf{Entt\text{-}jur}$ is an $N\times M$ Boolean matrix: rows represent Entities, columns represent jurisdictions, and an entry is `True` when the Entity is located in that jurisdiction. Each Entity belongs to exactly one jurisdiction.

The following are $M\times1$ Boolean column vectors for the fiscal year being tested, with entries set to `True` when:

- $\mathbf{iir\text{-}impl}$: the jurisdiction has implemented an IIR.
- $\mathbf{qiir\text{-}impl}$: the jurisdiction's IIR has qualified status.
- $\mathbf{dom\text{-}iir\text{-}impl}$: the jurisdiction applies its IIR to domestic low-taxed Entities.

Map each jurisdiction's status to its Entities, producing $N\times1$ Boolean column vectors:

$$
\begin{aligned}
\mathbf{iir}&:=\mathbf{Entt\text{-}jur}\times\mathbf{iir\text{-}impl},\\
\mathbf{qiir}&:=\mathbf{Entt\text{-}jur}\times\mathbf{qiir\text{-}impl},\\
\mathbf{dom\text{-}iir}&:=\mathbf{Entt\text{-}jur}\times\mathbf{dom\text{-}iir\text{-}impl}.
\end{aligned}
$$

Define the different-jurisdiction matrix:

$$
(\mathbf{diff\text{-}jur})_{ij}=1
\quad\Longleftrightarrow\quad
\text{Entities }i\text{ and }j\text{ are located in different jurisdictions}.
$$

The potential low-taxed Entity population consists of CEs, JVs, and JV Subsidiaries:

$$
\mathbf{member}:=\mathbf{ce}\lor\mathbf{jv}\lor\mathbf{jvsub}.
$$

The basic current-year payability conditions are:

$$
\begin{gathered}
\mathbf{Payable\text{-}condition}:=\\
\left[\begin{aligned}
&\bigl(\operatorname{diag}(\mathbf{iir})\times\mathbf{diff\text{-}jur}\bigr)\\
&\lor\bigl((\mathbf{dom\text{-}iir}\land\mathbf{iir})\times\mathbf{1}_N^T\bigr)
\end{aligned}\right]\times\operatorname{diag}(\mathbf{member})
\end{gathered}
$$

This requires the Parent Entity's jurisdiction to have an IIR and, for a domestic low-taxed Entity, to apply that IIR domestically.

Restrict the rows to UPEs and IPEs, and separately to POPEs:

$$
\begin{gathered}
\mathbf{Upe\text{-}ipe\text{-}candidate}:=\\
\operatorname{diag}(\mathbf{upe}\oplus\mathbf{ipe})\times\mathbf{Payable\text{-}condition}
\end{gathered}
$$

$$
\mathbf{Pope\text{-}candidate}
:=
\operatorname{diag}(\mathbf{pope})\times\mathbf{Payable\text{-}condition}.
$$

Apply the top-down rule to UPEs and IPEs. An upper UPE or IPE displaces a lower IPE only when the upper Entity is located in a jurisdiction whose IIR has qualified status for the fiscal year:

$$
\begin{gathered}
\mathbf{Qualified\text{-}upe\text{-}ipe\text{-}candidate}:=\\
\operatorname{diag}(\mathbf{qiir})\times\mathbf{Upe\text{-}ipe\text{-}candidate}
\end{gathered}
$$

$$
\begin{gathered}
\mathbf{Upper\text{-}upe\text{-}ipe}:=\\
\left(\mathbf{C}^{T}\times\mathbf{Qualified\text{-}upe\text{-}ipe\text{-}candidate}\right)>0
\end{gathered}
$$

The comparison is element-wise: an entry is `True` when at least one upper UPE or IPE qualifies for the corresponding Entity.

$$
\begin{gathered}
\mathbf{Upe\text{-}ipe\text{-}payable}:=\\
\mathbf{Upe\text{-}ipe\text{-}candidate}
\land\neg\mathbf{Upper\text{-}upe\text{-}ipe}
\end{gathered}
$$

For split ownership, define:

$$
(\mathbf{Wholly\text{-}own})_{ij}=1
\quad\Longleftrightarrow\quad
(\mathbf{Y})_{ij}=1,
$$

$$
\begin{gathered}
\mathbf{Qualified\text{-}pope\text{-}candidate}:=\\
\operatorname{diag}(\mathbf{qiir})\times\mathbf{Pope\text{-}candidate}
\end{gathered}
$$

Only a wholly-owning upper POPE in a QIIR jurisdiction displaces a lower POPE:

$$
\begin{gathered}
\mathbf{Upper\text{-}pope}:=\\
\left(\mathbf{Wholly\text{-}own}^{T}\times\mathbf{Qualified\text{-}pope\text{-}candidate}\right)>0
\end{gathered}
$$

$$
\mathbf{Pope\text{-}payable}
:=
\mathbf{Pope\text{-}candidate}\land\neg\mathbf{Upper\text{-}pope}.
$$

The final IIR payability matrix is:

$$
\boxed{
\begin{gathered}
\mathbf{Iir\text{-}payable}:=\\
\mathbf{Upe\text{-}ipe\text{-}payable}
\oplus
\mathbf{Pope\text{-}payable}
\end{gathered}
}
$$

Each non-zero element $(\mathbf{Iir\text{-}payable})_{ij}$ produces a row in `Relation.IirPayables` for Parent Entity $i$ and potential low-taxed Entity $j$. Whether Entity $j$ is actually low-taxed and the Parent Entity's Income Inclusion Ratio are determined later in [IIR.md](IIR.md).

**Note — Domestic IIR variation:** A domestic IIR variation may allow an Entity to apply the IIR to 100% of its own Top-up Tax where either:

- It is a POPE and no Parent Entity in the same jurisdiction can apply the IIR to it; or
- It is an IPE, its UPE cannot apply the IIR to it, no Parent Entity in the same jurisdiction can apply the IIR to it, and there is no upper IPE in another jurisdiction.

This variation may change $\mathbf{Iir\text{-}payable}$ by allowing self-payability on the diagonal.

## Jurisdiction-Level Taxing Rights

### IIR Taxing Rights

Aggregate Entity-level IIR payability to jurisdictions:

$$
\mathbf{Parent\text{-}jur}
:=
\left(\mathbf{Iir\text{-}payable}\times\mathbf{Entt\text{-}jur}\right)>0,
$$

$$
\begin{gathered}
\mathbf{Iir\text{-}taxing\text{-}rights}:=\\
\left(\mathbf{Entt\text{-}jur}^{T}\times\mathbf{Parent\text{-}jur}\right)>0
\end{gathered}
$$

Thus, $(\mathbf{Iir\text{-}taxing\text{-}rights})_{kl}=1$ iff at least one Parent Entity in jurisdiction $k$ is IIR-payable for an Entity in jurisdiction $l$.

Define the IIR collecting-jurisdiction indicator:

$$
\mathbf{iir\text{-}right\text{-}jur}
:=
\left(\mathbf{Iir\text{-}taxing\text{-}rights}\times\mathbf{1}_M\right)>0.
$$

### UTPR Taxing Rights

A jurisdiction with a UTPR and at least one CE other than an Investment Entity may collect under the UTPR, subject to UTPR Safe Harbours, the UPE Safe Harbour, and initial international activity relief. Investment Entities are excluded from UTPR collection, and their employees and tangible assets are excluded from the allocation key ([Model Rules, Articles 2.4.3 and 2.6.2(a)](https://www.oecd.org/content/dam/oecd/en/publications/reports/2021/12/tax-challenges-arising-from-digitalisation-of-the-economy-global-anti-base-erosion-model-rules-pillar-two_eed81a23/782bac33-en.pdf)).

### QDMTT Taxing Rights

A jurisdiction with a QDMTT may tax domestic Entities within its QDMTT scope.
