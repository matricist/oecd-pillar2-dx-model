JV Groups (Article 6.4) and Minority-Owned Subgroups (Article 5.6) are both sets of Entities headed by a top Entity and held together by control. Both are built by one rule from a set of candidates.

# Inputs

All inputs are for the same $N$ Entities and the same [effective period](<Ownership Interest.md#effective-periods>).

| Symbol | Type | Meaning |
| --- | --- | --- |
| $\mathbf{Y}$ | $[0,1]^{N\times N}$ | Direct and indirect Ownership Interest matrix, from [Ownership Interest](<Ownership Interest.md#model-matrices>) |
| $\mathbf{C}$ | $\{0,1\}^{N\times N}$ | Direct and indirect Controlling Interest matrix, from [Ownership Interest](<Ownership Interest.md#model-matrices>) |
| $\mathbf{group\text{-}upe}$ | $\{0,1\}^{N\times1}$ | The group's UPEs |
| $\mathbf{ce}$ | $\{0,1\}^{N\times1}$ | CEs |
| $\mathbf{eqt}$ | $\{0,1\}^{N\times1}$ | Entities reported under the equity method |
| $\mathbf{jv\text{-}excluded}$ | $\{0,1\}^{N\times1}$ | Entities excluded from the Joint Venture definition by Article 10.1.1(a)–(d) |

$\mathbf{idx}:=(1,\ldots,N)^{T}$. For a vector $\mathbf{v}$, $\operatorname{eq}(\mathbf{v})$ is the $N\times N$ Boolean matrix whose $(i,j)$ entry is `True` iff $v_i=v_j$. $\odot$ denotes element-wise multiplication; comparisons and logical operations are element-wise, and Boolean entries are treated as 1 or 0 in arithmetic.

# Validation

$$
\boxed{\mathbf{eqt}\land\mathbf{ce}=\mathbf{0}_N}
$$

# Subgroup Rule

Let $\mathbf{c}$ mark the candidates, $\mathbf{u}$ the Entities that may be members, and $\mathbf{S}$ the pairs of Entities that may belong to the same subgroup. $\mathbf{S}$ is an equivalence relation on the Entities it covers.

$$
\boxed{
\begin{aligned}
\operatorname{top}(\mathbf{c};\mathbf{S})&:=\mathbf{c}\land\neg\left[\left((\mathbf{C}\land\mathbf{S})^{T}\times\mathbf{c}\right)>0\right]\\
\operatorname{sub}(\mathbf{c},\mathbf{u};\mathbf{S})&:=\left(\operatorname{diag}\bigl(\operatorname{top}(\mathbf{c};\mathbf{S})\bigr)\times(\mathbf{I}_N\lor\mathbf{C})\times\operatorname{diag}(\mathbf{u})\right)\land\mathbf{S}
\end{aligned}
}
$$

A top Entity is a candidate that no other candidate controls within the scope. Row $t$ of $\operatorname{sub}$ lists the top Entity $t$ and the members it controls directly or indirectly. Each Entity has at most one controller and control is acyclic, so the chain of controllers above an Entity is unique and each Entity appears in at most one row:

$$
\operatorname{sub}(\mathbf{c},\mathbf{u};\mathbf{S})^{T}\times\mathbf{1}_N\le\mathbf{1}_N.
$$

# JV Groups

**Candidates**

$$
\begin{aligned}
\mathbf{upe\text{-}ownership}&:=\mathbf{Y}^{T}\times\mathbf{group\text{-}upe}\\
\mathbf{jvc}&:=\mathbf{eqt}\land(\mathbf{upe\text{-}ownership}\ge0.5)\land\neg\mathbf{jv\text{-}excluded}
\end{aligned}
$$

**JV Groups**

Every Entity a JV controls belongs to its JV Group, and the scope is unrestricted:

$$
\boxed{
\begin{aligned}
\mathbf{J}&:=\operatorname{sub}(\mathbf{jvc},\mathbf{1}_N;\mathbf{1}_{N\times N})\\
\mathbf{jv}&:=\operatorname{top}(\mathbf{jvc};\mathbf{1}_{N\times N})\\
\mathbf{jvsub}&:=\left[(\mathbf{J}^{T}\times\mathbf{1}_N)>0\right]\land\neg\mathbf{jv}\\
\mathbf{jvmember}&:=\mathbf{jv}\lor\mathbf{jvsub}\\
\mathbf{jv\text{-}id}&:=\mathbf{J}^{T}\times\mathbf{idx}
\end{aligned}
}
$$

$\mathbf{J}$ has top-level JVs on rows and member Entities on columns. $\mathbf{jv\text{-}id}$ is the index of each Entity's top-level JV, and 0 for an Entity outside every JV Group.

# Minority-Owned Subgroups

**Scope**

Members of a Minority-Owned Subgroup are all in the main MNE Group or all in the same JV Group:

$$
\begin{aligned}
\mathbf{ordinary\text{-}ce}&:=\mathbf{ce}\land\neg\mathbf{jvmember}\\
\mathbf{in\text{-}scope}&:=\mathbf{ordinary\text{-}ce}\lor\mathbf{jvmember}\\
\mathbf{S}&:=\operatorname{eq}(\mathbf{jv\text{-}id})\land(\mathbf{in\text{-}scope}\times\mathbf{in\text{-}scope}^{T})
\end{aligned}
$$

**Candidates**

$$
\begin{aligned}
\mathbf{jv\text{-}ownership}&:=(\mathbf{J}\odot\mathbf{Y})^{T}\times\mathbf{1}_N\\
\mathbf{moce\text{-}ce}&:=\mathbf{ordinary\text{-}ce}\land\neg\mathbf{group\text{-}upe}\land(\mathbf{upe\text{-}ownership}\le0.3)\\
\mathbf{moce\text{-}jvsub}&:=\mathbf{jvsub}\land(\mathbf{jv\text{-}ownership}\le0.3)\\
\mathbf{mocec}&:=\mathbf{moce\text{-}ce}\lor\mathbf{moce\text{-}jvsub}
\end{aligned}
$$

**Subgroups**

Only MOCEs are members. A row with more than one member is a Minority-Owned Subgroup headed by its MOPE; a row with one member is a Single MOCE:

$$
\boxed{
\begin{aligned}
\mathbf{Sub}&:=\operatorname{sub}(\mathbf{mocec},\mathbf{mocec};\mathbf{S}),\qquad
\mathbf{size}:=\mathbf{Sub}\times\mathbf{1}_N\\
\mathbf{mope}&:=(\mathbf{size}\ge2)\\
\mathbf{Mosg}&:=\operatorname{diag}(\mathbf{mope})\times\mathbf{Sub}\\
\mathbf{mos}&:=\left[(\mathbf{Mosg}^{T}\times\mathbf{1}_N)>0\right]\land\neg\mathbf{mope}\\
\mathbf{smoce}&:=(\mathbf{size}=1)
\end{aligned}
}
$$

$\mathbf{Mosg}$ has top-level MOPEs on rows and member MOCEs on columns.

A Single MOCE that is an Investment Entity keeps $\mathbf{smoce}$ but is not computed on its own: Article 5.6.2 does not apply to it, and the [ETR Calculation Group](<Group.md#etr-calculation-group>) puts it with the Investment Entities of its jurisdiction. An Investment Entity in a Minority-Owned Subgroup stays in the subgroup, which Article 5.6.1 treats as a separate MNE Group, and is grouped with the subgroup's other Investment Entities.

# Implementation

$\mathbf{upe\text{-}ownership}$ uses only the group UPE rows of $\mathbf{Y}$, and $\mathbf{jv\text{-}ownership}$ only the top-level JV rows. Where $\mathbf{Y}$ is not otherwise needed in full, these rows can be computed by [Row Calculation](<Ownership Interest.md#row-calculation>).
