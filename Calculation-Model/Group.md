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
| $\mathbf{entity\text{-}id}$ | $\text{String}^{N}$ | Identifier of each Entity that stays the same across Fiscal Years |
| $\mathbf{code}$ | $\text{CountryCode}^{M}$ | ISO code of each jurisdiction |
| $\mathbf{ie}$ | $\{0,1\}^{N\times1}$ | Investment Entities |
| $\mathbf{stateless}$ | $\{0,1\}^{N\times1}$ | Stateless Entities of the same location state, from [Location](<Location.md#location-state>); their rows of $\mathbf{Entt\text{-}jur}$ are all `False` |

$\mathbf{idx}:=(1,\ldots,N)^{T}$, and $\mathbf{jur}:=\mathbf{Entt\text{-}jur}\times(1,\ldots,M)^{T}$ is the index of each Entity's jurisdiction, 0 for a Stateless Entity. Keys use identifiers that stay the same across Fiscal Years: $\mathbf{jur\text{-}code}_i$ is $\mathbf{code}_{\mathbf{jur}_i}$, or `none` for a Stateless Entity, and for a vector $\mathbf{v}$ of Entity indices, $\operatorname{id}(\mathbf{v})_i$ is $\mathbf{entity\text{-}id}_{\mathbf{v}_i}$, or `main` where $\mathbf{v}_i=0$. For a key $\mathbf{k}$, a vector of tuples, and an indicator $\mathbf{u}$, $\operatorname{part}(\mathbf{k};\mathbf{u})\in\{0,1\}^{N\times M'}$ has one column for each of the $M'$ distinct keys among the Entities with $\mathbf{u}=1$, and its $(i,g)$ entry is 1 iff $u_i=1$ and $\mathbf{k}_i$ is the $g$-th key. It is built by sorting or hashing the keys. $\odot$ denotes element-wise multiplication; comparisons and logical operations are element-wise, and Boolean entries are treated as 1 or 0 in arithmetic.

# TCSH Group

The TCSH Group uses the initial location state $\mathbf{s}_0$ of [Location](<Location.md#location-state>). The ETR Calculation Group is built for each location state that Location evaluates, and finally for $\mathbf{stateless}$.

Investment Entities and Stateless Entities are out of scope. Only JV Groups are distinguished within a jurisdiction.

A Tested Jurisdiction is a jurisdiction, or a JV Group within it:

$$
\begin{aligned}
\mathbf{in\text{-}scope}_{\mathrm{TCSH}}&:=(\mathbf{ce}\lor\mathbf{jvmember})\land\neg\mathbf{ie}\land\neg\mathbf{stateless}\\
\mathbf{tcsh\text{-}key}&:=\bigl(\mathbf{jur\text{-}code},\operatorname{id}(\mathbf{jv\text{-}id})\bigr)\\
\mathbf{G}_{\mathrm{TCSH}}&:=\operatorname{part}(\mathbf{tcsh\text{-}key};\mathbf{in\text{-}scope}_{\mathrm{TCSH}})^{T}
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

A Full Calculation Group is identified by its key: its jurisdiction, its top Entity, and whether its Entities are Investment Entities. The top Entity is the top-level MOPE, otherwise the top-level JV, otherwise `main` for the main MNE Group; an Entity in both a Minority-Owned Subgroup and a JV Group follows the Minority-Owned Subgroup. A Stateless Entity has jurisdiction `none` and is its own top Entity, so it forms a group of its own.

$$
\begin{aligned}
\mathbf{in\text{-}scope}&:=\mathbf{ce}\lor\mathbf{jvmember}\\
\mathbf{group\text{-}key}&:=\bigl(\mathbf{jur\text{-}code},\operatorname{id}(\mathbf{group\text{-}id}),\mathbf{ie}\bigr)\\
\mathbf{Entt\text{-}group}&:=\operatorname{part}(\mathbf{group\text{-}key};\mathbf{in\text{-}scope})
\end{aligned}
$$

$\mathbf{Entt\text{-}group}\in\{0,1\}^{N\times M_{Calc}}$ has Entities on rows and the $M_{Calc}$ Full Calculation Groups on columns. Each in-scope Entity belongs to exactly one group:

$$
\mathbf{Entt\text{-}group}\times\mathbf{1}_{M_{Calc}}=\mathbf{in\text{-}scope}.
$$

# Continuity Across Fiscal Years

Both keys stay the same from one Fiscal Year to the next as long as the jurisdiction and the top Entity do. A balance that belongs to a group is therefore kept for its key, not for the group of a particular year.

Let $\mathcal{U}$ be the set of keys that have appeared in any Fiscal Year, and for year $t$ let $\mathbf{E}_t\in\{0,1\}^{M_t\times|\mathcal{U}|}$ have $(\mathbf{E}_t)_{gk}=1$ iff group $g$ of year $t$ has key $k$. A group balance is kept as a vector $\mathbf{b}$ over $\mathcal{U}$ and is read and written by

$$
\boxed{
\mathbf{opening}_t:=\mathbf{E}_t\times\mathbf{b},
\qquad
\mathbf{b}:=\mathbf{E}_t^{T}\times\mathbf{closing}_t
}
$$

The write sets every key absent in year $t$ to zero. This applies to $\mathbf{group\text{-}key}$ for the Excess Negative Tax Expense of [Top-up Tax Calculation](<Top-up Tax Calculation.md>) and to $\mathbf{tcsh\text{-}key}$ for [TCSH](<Transitional CbCR Safe Harbours Test.md>).

**Limits**

- **Group that ends.** A key absent in year $t+1$ passes nothing on; its balance lapses.
- **Group that splits.** The part that keeps the top Entity keeps the whole balance; the other parts start at zero.
- **Top Entity that changes.** A group whose top Entity changes has a new key and starts at zero, even if its members are the same.
- **Articles 6.2 and 6.3.** Whether these results match the treatment of Entities joining or leaving the group, and of transfers of assets and liabilities, is not decided here.
