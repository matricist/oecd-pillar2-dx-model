# Inputs

All inputs are for the same $N$ Entities and the same [effective period](<Ownership Interest.md#effective-periods>).

| Symbol | Type | Meaning |
| --- | --- | --- |
| $\mathbf{Mosg}$ | $\{0,1\}^{N\times N}$ | Minority-Owned Subgroups, from [Subgroups](<Subgroups.md#minority-owned-subgroups>) |
| $\mathbf{smoce}$ | $\{0,1\}^{N\times1}$ | Single MOCEs, from [Subgroups](<Subgroups.md#minority-owned-subgroups>) |
| $\mathbf{jvmember}$ | $\{0,1\}^{N\times1}$ | JV Group members, from [Subgroups](<Subgroups.md#jv-groups>) |
| $\mathbf{jv\text{-}id}$ | $\{0,\ldots,N\}^{N\times1}$ | Index of each Entity's top-level JV, 0 outside every JV Group, from [Subgroups](<Subgroups.md#jv-groups>) |
| $\mathbf{Entt\text{-}jur}$ | $\{0,1\}^{N\times M}$ | Entity-to-jurisdiction matrix, from [Taxing Rights](<Taxing Rights.md#iir-payability>) |
| $\mathbf{ce}$ | $\{0,1\}^{N\times1}$ | CEs |
| $\mathbf{ie}$ | $\{0,1\}^{N\times1}$ | Investment Entities |
| $\mathbf{stateless}$ | $\{0,1\}^{N\times1}$ | Stateless Entities; their rows of $\mathbf{Entt\text{-}jur}$ are all `False` |

$\mathbf{idx}:=(1,\ldots,N)^{T}$. For a vector $\mathbf{v}$, $\operatorname{eq}(\mathbf{v}):=(\mathbf{v}\times\mathbf{1}_N^{T}=\mathbf{1}_N\times\mathbf{v}^{T})$ is the $N\times N$ Boolean matrix whose $(i,j)$ entry is `True` iff $v_i=v_j$. $\odot$ denotes element-wise multiplication; comparisons and logical operations are element-wise, and Boolean entries are treated as 1 or 0 in arithmetic.

# TCSH Group

Investment Entities and Stateless Entities are out of scope. Only JV Groups are distinguished within a jurisdiction.

$$
\begin{aligned}
\mathbf{in\text{-}scope}_{\mathrm{TCSH}}&:=(\mathbf{ce}\lor\mathbf{jvmember})\land\neg\mathbf{ie}\land\neg\mathbf{stateless}\\
\mathbf{Same}_{\mathrm{TCSH}}&:=\operatorname{eq}(\mathbf{jv\text{-}id})\land(\mathbf{Entt\text{-}jur}\times\mathbf{Entt\text{-}jur}^{T})\\
&\quad\land(\mathbf{in\text{-}scope}_{\mathrm{TCSH}}\times\mathbf{in\text{-}scope}_{\mathrm{TCSH}}^{T})
\end{aligned}
$$

$(\mathbf{Same}_{\mathrm{TCSH}})_{ij}$ is `True` iff Entities $i$ and $j$ belong to the same Tested Jurisdiction.

Let $N_{\mathrm{TCSH}}$ be the number of in-scope Entities and $M_{\mathrm{TCSH}}$ the number of distinct non-zero rows of $\mathbf{Same}_{\mathrm{TCSH}}$. $\mathbf{G}_{\mathrm{TCSH}}\in\{0,1\}^{M_{\mathrm{TCSH}}\times N_{\mathrm{TCSH}}}$ has these rows as its rows, restricted to the columns of in-scope Entities. Each in-scope Entity belongs to exactly one Tested Jurisdiction:

$$
\mathbf{G}_{\mathrm{TCSH}}^{T}\times\mathbf{1}_{M_{\mathrm{TCSH}}}=\mathbf{1}_{N_{\mathrm{TCSH}}}.
$$

# ETR Calculation Group

**Group identifier**

$$
\begin{aligned}
\mathbf{mosg\text{-}id}&:=\mathbf{Mosg}^{T}\times\mathbf{idx}+(\mathbf{smoce}\land\neg\mathbf{ie})\odot\mathbf{idx}\\
\mathbf{group\text{-}id}&:=\mathbf{stateless}\odot\mathbf{idx}\\
&\quad+\neg\mathbf{stateless}\odot\left(\mathbf{mosg\text{-}id}+(\mathbf{mosg\text{-}id}=0)\odot\mathbf{jv\text{-}id}\right)
\end{aligned}
$$

$\mathbf{group\text{-}id}$ is the index of the Entity itself for a Stateless Entity, otherwise of its top-level MOPE, otherwise of its top-level JV, and 0 otherwise. A Single MOCE is its own top-level MOPE unless it is an Investment Entity: Article 5.6.2 does not apply to a MOCE that is an Investment Entity, so it keeps the identifier of the main MNE Group or of its JV Group and, through $\operatorname{eq}(\mathbf{ie})$ below, joins the Investment Entities of its jurisdiction.

**Full Calculation Groups**

$$
\begin{aligned}
\mathbf{in\text{-}scope}&:=\mathbf{ce}\lor\mathbf{jvmember}\\
\mathbf{Same}&:=\operatorname{eq}(\mathbf{group\text{-}id})\land\operatorname{eq}(\mathbf{ie})\\
&\quad\land\left((\mathbf{Entt\text{-}jur}\times\mathbf{Entt\text{-}jur}^{T})\lor\mathbf{I}_N\right)\\
&\quad\land(\mathbf{in\text{-}scope}\times\mathbf{in\text{-}scope}^{T})
\end{aligned}
$$

$(\mathbf{Same})_{ij}$ is `True` iff Entities $i$ and $j$ belong to the same Full Calculation Group.

Let $M_{Calc}$ be the number of distinct non-zero rows of $\mathbf{Same}$. $\mathbf{Entt\text{-}group}\in\{0,1\}^{N\times M_{Calc}}$ has these rows as its columns, so that $(\mathbf{Entt\text{-}group})_{ij}$ is `True` iff Entity $i$ belongs to Full Calculation Group $j$. Each in-scope Entity belongs to exactly one group:

$$
\mathbf{Entt\text{-}group}\times\mathbf{1}_{M_{Calc}}=\mathbf{in\text{-}scope}.
$$
