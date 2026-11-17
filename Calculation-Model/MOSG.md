# Inputs

All inputs are for the same $N$ Entities and the same [effective period](<Ownership Interest.md#effective-periods>).

| Symbol | Type | Meaning |
| --- | --- | --- |
| $\mathbf{Y}$ | $[0,1]^{N\times N}$ | Direct and indirect Ownership Interest matrix, from [JV](<JV.md#calculation>) |
| $\mathbf{C}$ | $\{0,1\}^{N\times N}$ | Direct and indirect Controlling Interest matrix, from [JV](<JV.md#calculation>) |
| $\mathbf{J}$ | $\{0,1\}^{N\times N}$ | JV Groups, from [JV](<JV.md#calculation>) |
| $\mathbf{jv},\mathbf{jvsub}$ | $\{0,1\}^{N\times1}$ | Top-level JVs and JV Subsidiaries, from [JV](<JV.md#calculation>) |
| $\mathbf{upe\text{-}ownership}$ | $[0,1]^{N\times1}$ | Aggregate UPE ownership, from [JV](<JV.md#calculation>) |
| $\mathbf{ce}$ | $\{0,1\}^{N\times1}$ | CEs |
| $\mathbf{group\text{-}upe}$ | $\{0,1\}^{N\times1}$ | The group's UPEs |

$\odot$ denotes element-wise multiplication. Comparisons and logical operations are element-wise.

# Calculation

**Group membership**

$$
\begin{aligned}
\mathbf{jvmember}&:=\mathbf{jv}\lor\mathbf{jvsub}\\
\mathbf{ordinary\text{-}ce}&:=\mathbf{ce}\land\neg\mathbf{jvmember}\\
\mathbf{S}&:=(\mathbf{ordinary\text{-}ce}\times\mathbf{ordinary\text{-}ce}^{T})\lor\left((\mathbf{J}^{T}\times\mathbf{J})>0\right)
\end{aligned}
$$

$\mathbf{S}$ retains only pairs of Entities within the main MNE Group or within the same JV Group.

**MOCE candidates**

$$
\begin{aligned}
\mathbf{jv\text{-}ownership}&:=(\mathbf{J}\odot\mathbf{Y})^{T}\times\mathbf{1}_N\\
\mathbf{moce\text{-}ce}&:=\mathbf{ordinary\text{-}ce}\land\neg\mathbf{group\text{-}upe}\land(\mathbf{upe\text{-}ownership}\le0.3)\\
\mathbf{moce\text{-}jvsub}&:=\mathbf{jvsub}\land(\mathbf{jv\text{-}ownership}\le0.3)\\
\mathbf{mocec}&:=\mathbf{moce\text{-}ce}\lor\mathbf{moce\text{-}jvsub}
\end{aligned}
$$

**Top-level MOPEs**

$$
\begin{aligned}
\mathbf{C}_{\mathrm{moce}}&:=\left(\operatorname{diag}(\mathbf{mocec})\times\mathbf{C}\times\operatorname{diag}(\mathbf{mocec})\right)\land\mathbf{S}\\
\mathbf{mope}&:=\left[(\mathbf{C}_{\mathrm{moce}}\times\mathbf{1}_N)>0\right]\land\neg\left[(\mathbf{C}_{\mathrm{moce}}^{T}\times\mathbf{1}_N)>0\right]
\end{aligned}
$$

**Minority-Owned Subgroups**

$$
\begin{aligned}
\mathbf{Mosg}&:=\left(\operatorname{diag}(\mathbf{mope})\times(\mathbf{I}_N\lor\mathbf{C})\times\operatorname{diag}(\mathbf{mocec})\right)\land\mathbf{S}\\
\mathbf{mos}&:=\left[(\mathbf{Mosg}^{T}\times\mathbf{1}_N)>0\right]\land\neg\mathbf{mope}
\end{aligned}
$$

**Single MOCEs**

$$
\mathbf{smoce}:=\mathbf{mocec}\land\neg\mathbf{mope}\land\neg\mathbf{mos}
$$

$\mathbf{Mosg}$ has top-level MOPEs on rows and member MOCEs on columns. Each Entity belongs to at most one Minority-Owned Subgroup:

$$
\mathbf{Mosg}^{T}\times\mathbf{1}_N\le\mathbf{1}_N.
$$
