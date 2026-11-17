# Input Model

The normalized atoms from which the [Calculation Model](../../Calculation-Model/Workflow.md) and the [Link Model](../Link/Model.md) derive the [Output Model](../Output/Model.md). Nothing here repeats, and nothing here can be computed from another atom. This version covers what `GeneralSection/CorporateStructure` needs.

# Entities

$N$ Entities, indexed $1,\ldots,N$.

| Atom | Type | Meaning |
| --- | --- | --- |
| $\mathbf{name}$ | $\text{String}^{N}$ | Entity name |
| $\mathbf{X}_0$ | $[0,1]^{N\times N}$ | [Direct Ownership Interest matrix](<../../Calculation-Model/Ownership Interest.md#direct-ownership-matrix>) |
| $\mathbf{C}_0$ | $\{0,1\}^{N\times N}$ | [Direct Controlling Interest matrix](<../../Calculation-Model/Controlling Interest.md#direct-controlling-matrix>) |
| $\mathbf{Entt\text{-}jur}$ | $\{0,1\}^{N\times M}$ | Entity-to-jurisdiction matrix |
| $\mathbf{Entt\text{-}tin}$ | $\{0,1\}^{N\times K}$ | Entity-to-TIN matrix |
| $\mathbf{group\text{-}upe},\mathbf{ce},\mathbf{ee},\mathbf{pe},\mathbf{ie},\mathbf{stateless},\mathbf{eqt}$ | $\{0,1\}^{N}$ | Classifications used by the Calculation Model |
| $\mathbf{fte\text{-}tt},\mathbf{reverse\text{-}hybrid},\mathbf{hybrid},\mathbf{insurance\text{-}ie},\mathbf{securitisation},\mathbf{nmce},\mathbf{art\text{-}10.3.5},\mathbf{non\text{-}group}$ | $\{0,1\}^{N}$ | Classifications reported only in the return |
| $\mathbf{ee\text{-}type}$ | $\text{Enum}^{N}$ | Kind of Excluded Entity, where $\mathbf{ee}$ |
| $\mathbf{ee\text{-}change}$ | $\{0,1\}^{N}$ | Change of Excluded Entity status, where $\mathbf{ee}$ |

# TINs

$K$ tax identification numbers.

| Atom | Type | Meaning |
| --- | --- | --- |
| $\mathbf{tin}$ | $\text{String}^{K}$ | Number |
| $\mathbf{tin\text{-}issued}$ | $\{1,\ldots,M\}^{K}$, optional | Issuing jurisdiction |
| $\mathbf{tin\text{-}type}$ | $\text{Enum}^{K}$ | Type of TIN |

# Jurisdictions

$M$ jurisdictions.

| Atom | Type | Meaning |
| --- | --- | --- |
| $\mathbf{code}$ | $\text{CountryCode}^{M}$ | ISO code |
| $\mathbf{iir\text{-}impl},\mathbf{qiir\text{-}impl},\mathbf{dom\text{-}iir\text{-}impl}$ | $\{0,1\}^{M}$ | As in [Taxing Rights](<../../Calculation-Model/Taxing Rights.md#iir-payability>) |
| $\mathbf{qutpr\text{-}impl},\mathbf{qdmtt\text{-}impl}$ | $\{0,1\}^{M}$ | Qualified UTPR, QDMTT |

# Constraints

With $\mathbf{listed}:=\mathbf{group\text{-}upe}\lor\mathbf{ce}\lor\mathbf{jvmember}$, the Entities reported individually:

| Constraint | Reason |
| --- | --- |
| $\mathbf{Entt\text{-}tin}^{T}\times\mathbf{1}_N=\mathbf{1}_K$ | A TIN belongs to one Entity. |
| $\mathbf{Entt\text{-}tin}\times\mathbf{1}_K\ge\mathbf{listed}$ | The return requires a TIN for every reported Entity. |
| $\mathbf{Entt\text{-}jur}\times\mathbf{1}_M=\neg\mathbf{stateless}$ | An Entity has one jurisdiction unless it is stateless. |

The validations of the Calculation Model documents apply in addition.
