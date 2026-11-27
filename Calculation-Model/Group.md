# Inputs

All inputs are for the same $N$ Entities and the same [effective period](<Ownership Interest.md#effective-periods>).

| Symbol | Type | Meaning |
| --- | --- | --- |
| $\mathbf{Mosg}$ | $\{0,1\}^{N\times N}$ | Minority-Owned Subgroups, from [Subgroups](<Subgroups.md#minority-owned-subgroups>) |
| $\mathbf{smoce}$ | $\{0,1\}^{N\times1}$ | Single MOCEs, from [Subgroups](<Subgroups.md#minority-owned-subgroups>) |
| $\mathbf{jvmember}$ | $\{0,1\}^{N\times1}$ | JV Group members, from [Subgroups](<Subgroups.md#jv-groups>) |
| $\mathbf{jv\text{-}id}$ | $\{0,\ldots,N\}^{N\times1}$ | Index of each Entity's top-level JV, 0 outside every JV Group, from [Subgroups](<Subgroups.md#jv-groups>) |
| $\mathbf{Entt\text{-}jur}$ | $\{0,1\}^{N\times M}$ | Entity-to-jurisdiction matrix of a location state, from [Location](<Location.md#location-state>) |
| $\mathbf{ce}$ | $\{0,1\}^{N\times1}$ | CEs |
| $\mathbf{ie}$ | $\{0,1\}^{N\times1}$ | Investment Entities |
| $\mathbf{stateless}$ | $\{0,1\}^{N\times1}$ | Stateless Entities of the same location state, from [Location](<Location.md#location-state>); their rows of $\mathbf{Entt\text{-}jur}$ are all `False` |

$\mathbf{idx}:=(1,\ldots,N)^{T}$, and $\mathbf{jur}:=\mathbf{Entt\text{-}jur}\times(1,\ldots,M)^{T}$ is the index of each Entity's jurisdiction, 0 for a Stateless Entity. For a key $\mathbf{k}$, a vector of tuples, and an indicator $\mathbf{u}$, $\operatorname{part}(\mathbf{k};\mathbf{u})\in\{0,1\}^{N\times M'}$ has one column for each of the $M'$ distinct keys among the Entities with $\mathbf{u}=1$, and its $(i,g)$ entry is 1 iff $u_i=1$ and $\mathbf{k}_i$ is the $g$-th key. It is built by sorting or hashing the keys. $\odot$ denotes element-wise multiplication; comparisons and logical operations are element-wise, and Boolean entries are treated as 1 or 0 in arithmetic.

# TCSH Group

The TCSH Group uses the initial location state $\mathbf{s}_0$ of [Location](<Location.md#location-state>). The ETR Calculation Group is built for each location state that Location evaluates, and finally for $\mathbf{stateless}$.

Investment Entities and Stateless Entities are out of scope. Only JV Groups are distinguished within a jurisdiction.

A Tested Jurisdiction is a jurisdiction, or a JV Group within it:

$$
\begin{aligned}
\mathbf{in\text{-}scope}_{\mathrm{TCSH}}&:=(\mathbf{ce}\lor\mathbf{jvmember})\land\neg\mathbf{ie}\land\neg\mathbf{stateless}\\
\mathbf{G}_{\mathrm{TCSH}}&:=\operatorname{part}\bigl((\mathbf{jur},\mathbf{jv\text{-}id});\mathbf{in\text{-}scope}_{\mathrm{TCSH}}\bigr)^{T}
\end{aligned}
$$

restricted to the $N_{\mathrm{TCSH}}$ columns of in-scope Entities, with $M_{\mathrm{TCSH}}$ rows. Each in-scope Entity belongs to exactly one Tested Jurisdiction:

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

$\mathbf{group\text{-}id}$ is the index of the Entity itself for a Stateless Entity, otherwise of its top-level MOPE, otherwise of its top-level JV, and 0 otherwise. A Single MOCE is its own top-level MOPE unless it is an Investment Entity: Article 5.6.2 does not apply to a MOCE that is an Investment Entity, so it keeps the identifier of the main MNE Group or of its JV Group and joins the Investment Entities of its jurisdiction through $\mathbf{ie}$ in the key below.

**Full Calculation Groups**

A Full Calculation Group is identified by its key: jurisdiction, group identifier, and whether its Entities are Investment Entities. A Stateless Entity has jurisdiction 0 and its own index as group identifier, so it forms a group of its own.

$$
\begin{aligned}
\mathbf{in\text{-}scope}&:=\mathbf{ce}\lor\mathbf{jvmember}\\
\mathbf{group\text{-}key}&:=(\mathbf{jur},\mathbf{group\text{-}id},\mathbf{ie})\\
\mathbf{Entt\text{-}group}&:=\operatorname{part}(\mathbf{group\text{-}key};\mathbf{in\text{-}scope})
\end{aligned}
$$

$\mathbf{Entt\text{-}group}\in\{0,1\}^{N\times M_{Calc}}$ has Entities on rows and the $M_{Calc}$ Full Calculation Groups on columns. Each in-scope Entity belongs to exactly one group:

$$
\mathbf{Entt\text{-}group}\times\mathbf{1}_{M_{Calc}}=\mathbf{in\text{-}scope}.
$$
