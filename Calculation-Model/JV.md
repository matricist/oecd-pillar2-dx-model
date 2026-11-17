# Inputs

All inputs are for the same $N$ Entities and the same [effective period](<Ownership Interest.md#effective-periods>).

| Symbol | Type | Meaning |
| --- | --- | --- |
| $\mathbf{X}_0$ | $[0,1]^{N\times N}$ | [Direct Ownership Interest matrix](<Ownership Interest.md#direct-ownership-matrix>) |
| $\mathbf{C}_0$ | $\{0,1\}^{N\times N}$ | [Direct Controlling Interest matrix](<Controlling Interest.md#direct-controlling-matrix>) |
| $\mathbf{group\text{-}upe}$ | $\{0,1\}^{N\times1}$ | The group's UPEs |
| $\mathbf{ce}$ | $\{0,1\}^{N\times1}$ | CEs |
| $\mathbf{eqt}$ | $\{0,1\}^{N\times1}$ | Entities reported under the equity method |
| $\mathbf{jv\text{-}excluded}$ | $\{0,1\}^{N\times1}$ | Entities excluded from the Joint Venture definition by Article 10.1.1(a)–(d) |

$f$ is the [Ownership Interest method](<Ownership Interest.md#direct-method>) and $w$ is [Warshall's algorithm](<Controlling Interest.md#warshalls-algorithm>). Comparisons and logical operations are element-wise.

# Validation

$$
\boxed{\mathbf{eqt}\land\mathbf{ce}=\mathbf{0}_N}
$$

# Calculation

$$
\begin{aligned}
\mathbf{Y}&:=f(\mathbf{X}_0)
&&\text{direct and indirect Ownership Interests}\\
\mathbf{C}&:=w(\mathbf{C}_0)
&&\text{direct and indirect Controlling Interests}\\[6pt]
\mathbf{upe\text{-}ownership}&:=\mathbf{Y}^{T}\times\mathbf{group\text{-}upe}
&&\text{aggregate UPE ownership}\\
\mathbf{jvc}&:=\mathbf{eqt}\land(\mathbf{upe\text{-}ownership}\ge0.5)\land\neg\mathbf{jv\text{-}excluded}
&&\text{JV candidates}\\
\mathbf{jvsub}&:=\left(\mathbf{C}^{T}\times\mathbf{jvc}\right)>0
&&\text{JV Subsidiaries}\\
\mathbf{jv}&:=\mathbf{jvc}\land\neg\mathbf{jvsub}
&&\text{top-level JVs}\\
\mathbf{J}&:=\operatorname{diag}(\mathbf{jv})\times(\mathbf{I}_N\lor\mathbf{C})
&&\text{JV Groups}
\end{aligned}
$$

$\mathbf{J}$ has top-level JVs on rows and member Entities on columns. Each Entity belongs to at most one JV Group:

$$
\mathbf{J}^{T}\times\mathbf{1}_N\le\mathbf{1}_N.
$$
