# Inputs

All inputs are for the same $N$ Entities, the same $M$ jurisdictions, and the same [effective period](<Ownership Interest.md#effective-periods>).

| Symbol | Type | Meaning |
| --- | --- | --- |
| $\mathbf{Y}$ | $[0,1]^{N\times N}$ | Direct and indirect Ownership Interest matrix, from [Ownership Interest](<Ownership Interest.md#model-matrices>) |
| $\mathbf{C}$ | $\{0,1\}^{N\times N}$ | Direct and indirect Controlling Interest matrix, from [Ownership Interest](<Ownership Interest.md#model-matrices>) |
| $\mathbf{jv},\mathbf{jvsub}$ | $\{0,1\}^{N\times1}$ | Top-level JVs and JV Subsidiaries, from [Subgroups](<Subgroups.md#jv-groups>) |
| $\mathbf{X}_0^{\mathrm{profit}}$ | $[0,1]^{N\times N}$ | [Direct Profit Ownership Interest matrix](<Ownership Interest.md#direct-ownership-matrix>) |
| $\mathbf{group\text{-}upe},\mathbf{ce},\mathbf{ee},\mathbf{pe},\mathbf{ie}$ | $\{0,1\}^{N\times1}$ | The group's UPEs, CEs, Excluded Entities, PEs, and Investment Entities |
| $\mathbf{Entt\text{-}jur}$ | $\{0,1\}^{N\times M}$ | Entity-to-jurisdiction matrix, from [Location](<Location.md#fixed-point>); the row of a Stateless Entity is all `False`. [Location](<Location.md#required-to-apply-an-iir>) also evaluates this document once with every Flow-through Entity at its jurisdiction of creation |
| $\mathbf{iir\text{-}impl}$ | $\{0,1\}^{M\times1}$ | The jurisdiction has implemented an IIR |
| $\mathbf{qiir\text{-}impl}$ | $\{0,1\}^{M\times1}$ | Its IIR has qualified status |
| $\mathbf{dom\text{-}iir\text{-}impl}$ | $\{0,1\}^{M\times1}$ | Its IIR also applies to low-taxed Entities in the jurisdiction itself |
| $\mathbf{self\text{-}iir\text{-}impl}$ | $\{0,1\}^{M\times1}$ | Its domestic IIR lets a Parent Entity pay its own Top-up Tax |

$f$ is the [Ownership Interest method](<Ownership Interest.md#direct-method>). $\operatorname{diag}(\mathbf{v})$ is the diagonal matrix of a vector, so that $\operatorname{diag}(\mathbf{v})\times\mathbf{A}$ keeps the rows of $\mathbf{A}$ at which $\mathbf{v}$ is `True` and $\mathbf{A}\times\operatorname{diag}(\mathbf{v})$ keeps the columns. Comparisons and logical operations are element-wise, and Boolean entries are treated as 1 or 0 in matrix multiplication.

# Validation

$$
\mathbf{self\text{-}iir\text{-}impl}\le\mathbf{dom\text{-}iir\text{-}impl}\le\mathbf{iir\text{-}impl},\qquad
\mathbf{qiir\text{-}impl}\le\mathbf{iir\text{-}impl}
$$

# Identification of Parent Entities

$$
\begin{aligned}
\mathbf{upe}&:=\mathbf{group\text{-}upe}\land\neg\mathbf{ee}\\
\mathbf{Own}&:=(\mathbf{Y}>0)\land\neg\mathbf{I}_N\\
\mathbf{parent}&:=\mathbf{ce}\land\left((\mathbf{Own}\times\mathbf{ce})>0\right)\\
&\quad\land\neg(\mathbf{upe}\lor\mathbf{pe}\lor\mathbf{ie}\lor\mathbf{ee}\lor\mathbf{jv}\lor\mathbf{jvsub})\\
\mathbf{Y}^{\mathrm{profit,ce}}&:=f\left(\operatorname{diag}(\mathbf{ce})\times\mathbf{X}_0^{\mathrm{profit}}\times\operatorname{diag}(\mathbf{ce})\right)\\
\mathbf{external}&:=\mathbf{1}_N-(\mathbf{Y}^{\mathrm{profit,ce}})^{T}\times\mathbf{upe}\\
\mathbf{pope}&:=\mathbf{parent}\land(\mathbf{external}>0.2)\\
\mathbf{ipe}&:=\mathbf{parent}\land\neg\mathbf{pope}
\end{aligned}
$$

- $\mathbf{Own}$ marks the Entities in which each Entity holds a direct or indirect Ownership Interest, on the full ownership graph, including paths through Excluded Entities.
- $\mathbf{parent}$ identifies the CEs that own another CE and can therefore be a POPE or an IPE.
- $\mathbf{external}$ is the share of each Entity's profits not held by the UPEs through CEs. A parent with more than 20% is a POPE; every other parent is an IPE.

# IIR Payability

**Jurisdiction status of each Entity**

$$
\begin{aligned}
\mathbf{iir}&:=\mathbf{Entt\text{-}jur}\times\mathbf{iir\text{-}impl}\\
\mathbf{qiir}&:=\mathbf{Entt\text{-}jur}\times\mathbf{qiir\text{-}impl}\\
\mathbf{dom\text{-}iir}&:=\mathbf{Entt\text{-}jur}\times\mathbf{dom\text{-}iir\text{-}impl}\\
\mathbf{self\text{-}iir}&:=\mathbf{Entt\text{-}jur}\times\mathbf{self\text{-}iir\text{-}impl}\\
\mathbf{Diff\text{-}jur}&:=\neg(\mathbf{Entt\text{-}jur}\times\mathbf{Entt\text{-}jur}^{T})
\end{aligned}
$$

$(\mathbf{Diff\text{-}jur})_{ij}$ is `True` when Entities $i$ and $j$ are not located in the same jurisdiction.

**Candidates**

A Parent Entity is a candidate for an Entity in which it holds an Ownership Interest if its jurisdiction has an IIR and the Entity is located elsewhere, or the IIR also applies domestically. The Entities that can be low-taxed are CEs, JVs, and JV Subsidiaries.

$$
\begin{aligned}
\mathbf{member}&:=\mathbf{ce}\lor\mathbf{jv}\lor\mathbf{jvsub}\\
\mathbf{Candidate}&:=\operatorname{diag}(\mathbf{iir})\times\left(\mathbf{Diff\text{-}jur}\lor(\mathbf{dom\text{-}iir}\times\mathbf{1}_N^{T})\right)\times\operatorname{diag}(\mathbf{member})\\
&\quad\land\mathbf{Own}
\end{aligned}
$$

**Top-down rule**

A UPE or IPE is displaced by a UPE or IPE that controls it and is a candidate under a Qualified IIR.

$$
\begin{aligned}
\mathbf{Top}&:=\operatorname{diag}(\mathbf{upe}\lor\mathbf{ipe})\times\mathbf{Candidate}\\
\mathbf{Upe\text{-}ipe\text{-}payable}&:=\mathbf{Top}\land\neg\left[\left(\mathbf{C}^{T}\times\operatorname{diag}(\mathbf{qiir})\times\mathbf{Top}\right)>0\right]
\end{aligned}
$$

**Split-ownership rule**

A POPE is displaced only by a POPE that wholly owns it and is a candidate under a Qualified IIR.

$$
\begin{aligned}
\mathbf{Split}&:=\operatorname{diag}(\mathbf{pope})\times\mathbf{Candidate}\\
\mathbf{Wholly\text{-}own}&:=(\mathbf{Y}=1)\\
\mathbf{Pope\text{-}payable}&:=\mathbf{Split}\land\neg\left[\left(\mathbf{Wholly\text{-}own}^{T}\times\operatorname{diag}(\mathbf{qiir})\times\mathbf{Split}\right)>0\right]
\end{aligned}
$$

**Result**

$$
\boxed{\mathbf{Iir\text{-}payable}:=\mathbf{Upe\text{-}ipe\text{-}payable}\lor\mathbf{Pope\text{-}payable}}
$$

$(\mathbf{Iir\text{-}payable})_{ij}$ identifies Parent Entity $i$ as IIR-payable for Entity $j$. Whether Entity $j$ is low-taxed, and the Parent Entity's Income Inclusion Ratio, are determined in [IIR](IIR.md).

## Domestic IIR on the Parent Entity Itself

Where the domestic IIR of its jurisdiction allows it, a Parent Entity pays 100% of its own Top-up Tax if no other Parent Entity is positioned to do so:

- a POPE, if no Parent Entity in its own jurisdiction is payable for it;
- an IPE, if in addition no UPE is payable for it and no IPE in another jurisdiction controls it.

$$
\begin{aligned}
\mathbf{covered\text{-}same}&:=\left[\left(\mathbf{Iir\text{-}payable}\land\neg\mathbf{Diff\text{-}jur}\right)^{T}\times\mathbf{1}_N\right]>0\\
\mathbf{covered\text{-}upe}&:=\left[\mathbf{Iir\text{-}payable}^{T}\times\mathbf{upe}\right]>0\\
\mathbf{upper\text{-}ipe}&:=\left[\left(\mathbf{C}\land\mathbf{Diff\text{-}jur}\right)^{T}\times\mathbf{ipe}\right]>0\\
\mathbf{self\text{-}payable}&:=\mathbf{self\text{-}iir}\land\neg\mathbf{covered\text{-}same}\\
&\quad\land\left(\mathbf{pope}\lor(\mathbf{ipe}\land\neg\mathbf{covered\text{-}upe}\land\neg\mathbf{upper\text{-}ipe})\right)
\end{aligned}
$$

$\mathbf{self\text{-}payable}$ is kept apart from $\mathbf{Iir\text{-}payable}$, whose diagonal stays `False`. The allocation in [IIR](IIR.md) does not use it yet.

# Jurisdiction-Level Taxing Rights

## IIR Taxing Rights

$$
\begin{aligned}
\mathbf{Parent\text{-}jur}&:=\left[\left(\mathbf{Iir\text{-}payable}\lor\operatorname{diag}(\mathbf{self\text{-}payable})\right)\times\mathbf{Entt\text{-}jur}\right]>0\\
\mathbf{Iir\text{-}taxing\text{-}rights}&:=\left(\mathbf{Entt\text{-}jur}^{T}\times\mathbf{Parent\text{-}jur}\right)>0\\
\mathbf{iir\text{-}right\text{-}jur}&:=\left(\mathbf{Iir\text{-}taxing\text{-}rights}\times\mathbf{1}_M\right)>0
\end{aligned}
$$

$(\mathbf{Iir\text{-}taxing\text{-}rights})_{kl}$ is `True` iff a Parent Entity in jurisdiction $k$ is IIR-payable for an Entity in jurisdiction $l$, and $\mathbf{iir\text{-}right\text{-}jur}$ identifies the jurisdictions that collect under an IIR.

## UTPR Taxing Rights

Decided by legislation alone: a jurisdiction that has implemented a UTPR has UTPR taxing rights. The safe harbours and the allocation among UTPR jurisdictions are applied in [UTPR](UTPR.md). Investment Entities are excluded from UTPR collection and from the allocation key ([Model Rules, Articles 2.4.3 and 2.6.2(a)](https://www.oecd.org/content/dam/oecd/en/publications/reports/2021/12/tax-challenges-arising-from-digitalisation-of-the-economy-global-anti-base-erosion-model-rules-pillar-two_eed81a23/782bac33-en.pdf)).

## QDMTT Taxing Rights

Decided by legislation alone: a jurisdiction that has implemented a QDMTT has taxing rights over the Entities located in it.
