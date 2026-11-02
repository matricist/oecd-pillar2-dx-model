## 사전 정의(?)

Use the direct Ownership Interest matrix $\mathbf{X}_0$ from [Ownership Interest](<Ownership Interest.md#direct-ownership-matrix>), the direct Controlling Interest matrix $\mathbf{C}_0$ from [Controlling Interest](<Controlling Interest.md#direct-controlling-matrix>), and the JV Group membership matrix $\mathbf{J}$ from [JV Groups](<JV.md#constructing-jv-groups>), all for the same $N$ Entities.

Let $\mathbf{Y}=f(\mathbf{X}_0)$ be the direct and indirect Ownership Interest matrix and $\mathbf{C}=w(\mathbf{C}_0)$ the direct and indirect Controlling Interest matrix, where $f$ is the [Ownership Interest method](<Ownership Interest.md#direct-method>) and $w$ is [Warshall's algorithm](<Controlling Interest.md#warshalls-algorithm>).

$\mathbf{ce}$, $\mathbf{ie}$, and $\mathbf{group\text{-}upe}$ are $N\times1$ Boolean column vectors identifying CEs, Investment Entities, and the group's UPEs, respectively. $\mathbf{1}_N$ is the all-one column vector, $\mathbf{I}_N$ is the identity matrix, and $\odot$ denotes element-wise multiplication. Comparisons are element-wise.

Derive JV membership from $\mathbf{J}$:

$$
\begin{aligned}
\mathbf{jv}&:=\bigl((\mathbf{J})_{11},\ldots,(\mathbf{J})_{NN}\bigr)^{T},\\
\mathbf{jvmember}&:=\left(\mathbf{J}^{T}\times\mathbf{1}_N\right)>0,\\
\mathbf{jvsub}&:=\mathbf{jvmember}\land\neg\mathbf{jv}.
\end{aligned}
$$

## Identifying MOCE Candidates

An ordinary CE is tested against aggregate group UPE ownership; a JV Subsidiary is tested against ownership by its own top-level JV. The threshold is 30% or less in both cases.

**Ownership ratios**

$$
\begin{aligned}
\mathbf{upe\text{-}ownership}&:=\mathbf{Y}^{T}\times\mathbf{group\text{-}upe},\\
\mathbf{jv\text{-}ownership}&:=(\mathbf{J}\odot\mathbf{Y})^{T}\times\mathbf{1}_N.
\end{aligned}
$$

**Candidate tests**

Ordinary CEs exclude JV Group members and group UPEs:

$$
\begin{aligned}
\mathbf{moce\text{-}ce}:={}&\mathbf{ce}
\land\neg\mathbf{jvmember}
\land\neg\mathbf{group\text{-}upe}\\
&\land(\mathbf{upe\text{-}ownership}\le0.30),\\[6pt]
\mathbf{moce\text{-}jvsub}:={}&\mathbf{jvsub}
\land(\mathbf{jv\text{-}ownership}\le0.30).
\end{aligned}
$$

$$
\boxed{\mathbf{mocec}:=\mathbf{moce\text{-}ce}\lor\mathbf{moce\text{-}jvsub}}
$$

## Identifying Top-Level MOPEs

Let $\mathbf{ordinary\text{-}ce}:=\mathbf{ce}\land\neg\mathbf{jvmember}$. The Boolean matrix $\mathbf{S}$ retains only pairs within the main MNE Group or the same JV Group:

$$
\mathbf{S}
:=
(\mathbf{ordinary\text{-}ce}\times\mathbf{ordinary\text{-}ce}^{T})
\lor
(\mathbf{J}^{T}\times\mathbf{J}).
$$

Retain control relationships between MOCE candidates in the same group:

$$
\mathbf{C}_{\mathrm{moce}}
:=
\left(\operatorname{diag}(\mathbf{mocec})
\times\mathbf{C}
\times\operatorname{diag}(\mathbf{mocec})\right)
\land\mathbf{S}.
$$

Find candidates that control another MOCE candidate:

$$
\mathbf{mopec}
:=
\left(\mathbf{C}_{\mathrm{moce}}\times\mathbf{1}_N\right)>0.
$$

Exclude candidates controlled by another MOCE candidate:

$$
\mathbf{controlled\text{-}moce}
:=
\left(\mathbf{C}_{\mathrm{moce}}^{T}\times\mathbf{1}_N\right)>0,
$$

$$
\mathbf{mope}
:=
\mathbf{mopec}\land\neg\mathbf{controlled\text{-}moce}.
$$

## Constructing Minority-Owned Subgroups

$\mathbf{Mosg}$ is an $N\times N$ Boolean matrix with top-level MOPEs on rows and member MOCEs on columns. Each group includes the MOPE itself and the MOCE candidates it directly or indirectly controls within the same calculation group:

$$
\mathbf{Mosg}
:=
\left(\operatorname{diag}(\mathbf{mope})
\times(\mathbf{I}_N\lor\mathbf{C})
\times\operatorname{diag}(\mathbf{mocec})\right)
\land\mathbf{S}.
$$

$\mathbf{mos}$ identifies group members other than the MOPE:

$$
\mathbf{mos}
:=
\left[\left(\mathbf{Mosg}^{T}\times\mathbf{1}_N\right)>0\right]
\land\neg\mathbf{mope}.
$$

## Identifying Single MOCEs

A Single MOCE is a candidate outside every MOSG, including an Investment Entity:

$$
\mathbf{smoce}
:=
\mathbf{mocec}
\land\neg\mathbf{mope}
\land\neg\mathbf{mos}.
$$

For aggregation purposes only, exclude Single MOCEs that are Investment Entities; they remain in the Investment Entity calculation group. The final calculation-purpose MOCE vector is:

$$
\mathbf{moce}
:=
\mathbf{mope}\lor\mathbf{mos}\lor(\mathbf{smoce}\land\neg\mathbf{ie}).
$$
