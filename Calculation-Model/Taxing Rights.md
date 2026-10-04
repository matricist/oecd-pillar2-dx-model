# Taxing Rights

## Interface

### Imports

- Entity locations and classification indicators from [Relations.md](Relations.md) and [Definition.md](Definition.md).
- Direct and indirect Ownership Interests, including the exported function $f(\mathbf{X}_0)$, from [Ownership Interest.md](<Ownership Interest.md>).
- Direct and indirect Controlling Interests from [Controlling Interest.md](<Controlling Interest.md>).
- JV and JV Subsidiary indicators from [Identifying Joint Venture Groups.md](<Identifying Joint Venture Groups.md>).
- Current-year IIR, QIIR, domestic IIR, UTPR, QUTPR, and QDMTT status from `Relation.JurisdictionImplementations`.

`Relation.JurisdictionImplementations`

```text
{
  fiscal_year,
  jurisdiction_code,
  iir_implemented,
  qiir_implemented,
  domestic_iir_implemented,
  utpr_implemented,
  qutpr_implemented,
  qdmtt_implemented
}
```

### Exports

- Parent Entity indicators $\mathbf{upe}$, $\mathbf{parent}$, $\mathbf{pope}$, and $\mathbf{ipe}$.
- The IIR payability matrix $\mathbf{Iir\text{-}payable}$ and sparse `Relation.IirPayables` rows.
- The jurisdiction-level taxing-rights matrix $\mathbf{Taxing\text{-}rights}$, Tested-Jurisdiction-specific indicator vectors $\mathbf{taxing\text{-}right\text{-}jur}^{(l)}$, and the group-wide indicator vector $\mathbf{taxing\text{-}right\text{-}jur}$.

`Relation.IirPayables`

```text
{
  fiscal_year,
  parent_entity_id,
  low_taxed_constituent_entity_id
}
```

The calculation uses only the ownership structure and jurisdiction implementation status for the fiscal year being tested; no historical ownership structure is required. This stage determines whether the IIR can apply to an Entity for that year, but does not calculate the Income Inclusion Ratio or the amount ultimately collected under the IIR.

## Notation

Bold uppercase symbols denote matrices, bold lowercase names denote column vectors, and individual entries are scalars.

| Symbol                                                                                                                                   | Meaning                                                                                   |
| ---------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------- |
| $N$                                                                                                                                      | Number of Entities.                                                                       |
| $M$                                                                                                                                      | Number of jurisdictions.                                                                  |
| $\mathbf{X}_0,\mathbf{X}_0^{\mathrm{profit}}\in[0,1]^{N\times N}$                                                                        | Validated direct ordinary and Profit Ownership Interest matrices.                         |
| $\mathbf{Y}=f(\mathbf{X}_0)$                                                                                                             | Direct and indirect ordinary Ownership Interest matrix.                                   |
| $\mathbf{C}\in\{0,1\}^{N\times N}$                                                                                                       | Direct and indirect Controlling Interest matrix.                                          |
| $\mathbf{Entt\text{-}jur}\in\{0,1\}^{N\times M}$                                                                                         | Entity-to-jurisdiction incidence matrix.                                                  |
| $\mathbf{ce},\mathbf{pe},\mathbf{ie},\mathbf{ee},\mathbf{jv},\mathbf{jvsub}\in\{0,1\}^{N\times1}$                                        | Entity classification indicators.                                                         |
| $\mathbf{group\text{-}upe}\in\{0,1\}^{N\times1}$                                                                                         | Group UPE indicator from `Relation.ConstituentEntities.is_upe`.                           |
| $\mathbf{iir\text{-}impl},\mathbf{dom\text{-}iir\text{-}impl},\mathbf{utpr\text{-}impl},\mathbf{qdmtt\text{-}impl}\in\{0,1\}^{M\times1}$ | Current-year jurisdiction implementation indicators.                                      |
| $\mathbf{qiir\text{-}impl},\mathbf{qutpr\text{-}impl}\in\{0,1\}^{M\times1}$                                                              | Current-year qualified-status indicators, kept separate from domestic-law implementation. |

For Entity $i$ and jurisdiction $k$:

$$
(\mathbf{Entt\text{-}jur})_{ik}=1
\quad\Longleftrightarrow\quad
\text{Entity }i\text{ is located in jurisdiction }k.
$$

All rows used in this calculation must belong to the same fiscal year. Each Entity must map to exactly one jurisdiction.

## Identification of Parent Entities

### UPE

For IIR purposes, the UPE indicator is:

$$
\mathbf{upe}
:=
\mathbf{group\text{-}upe}\odot(\mathbf{1}_N-\mathbf{ee}).
$$

`group-upe` identifies the UPE independently of Excluded Entity status. `upe` identifies a non-Excluded UPE that may apply the IIR.

### POPE and IPE Candidates

An Entity is a candidate if it owns, directly or indirectly, an Ownership Interest in another CE and is not a UPE, PE, IE, EE, JV, or JV Subsidiary:

$$
\mathbf{parent}
:=
\mathbf{1}_{\{\operatorname{diag}(\mathbf{ce})[\mathbf{Y}-\operatorname{diag}(\mathbf{Y})]\operatorname{diag}(\mathbf{ce})\mathbf{1}_N>0\}}
\odot(\mathbf{1}_N-\mathbf{upe})
\odot(\mathbf{1}_N-\mathbf{pe})
\odot(\mathbf{1}_N-\mathbf{ie})
\odot(\mathbf{1}_N-\mathbf{ee})
\odot(\mathbf{1}_N-\mathbf{jv})
\odot(\mathbf{1}_N-\mathbf{jvsub}).
$$

Subtracting $\operatorname{diag}(\mathbf{Y})$ enforces the requirement that the candidate own an interest in another CE. The CE mask is applied after calculating direct and indirect ownership so that an ownership chain passing through an EE is not broken.

For the more-than-20% POPE test, retain only direct Profit Ownership Interests between CEs:

$$
\mathbf{X}_0^{\mathrm{profit,ce}}
:=
\operatorname{diag}(\mathbf{ce})\mathbf{X}_0^{\mathrm{profit}}\operatorname{diag}(\mathbf{ce}),
$$

$$
\mathbf{Y}^{\mathrm{profit,ce}}
:=
f(\mathbf{X}_0^{\mathrm{profit,ce}}).
$$

Define the MNE-held and externally held Profit Ownership Interests in each candidate:

$$
\mathbf{mne}^{T}
:=
\mathbf{1}_N^{T}\operatorname{diag}(\mathbf{upe})
\mathbf{Y}^{\mathrm{profit,ce}}\operatorname{diag}(\mathbf{parent}),
$$

$$
\mathbf{external}:=\mathbf{1}_N-\mathbf{mne}.
$$

The POPE and IPE indicators are then:

$$
\mathbf{pope}
:=
\mathbf{parent}\odot\mathbf{1}_{\{\mathbf{external}>0.2\}},
$$

$$
\mathbf{ipe}
:=
\mathbf{parent}\odot(\mathbf{1}_N-\mathbf{pope}).
$$

## IIR Payability

Lift the current-year jurisdiction implementation indicators to Entity-level vectors:

$$
\mathbf{iir}:=\mathbf{Entt\text{-}jur}\,\mathbf{iir\text{-}impl},
\qquad
\mathbf{qiir}:=\mathbf{Entt\text{-}jur}\,\mathbf{qiir\text{-}impl},
\qquad
\mathbf{dom\text{-}iir}:=\mathbf{Entt\text{-}jur}\,\mathbf{dom\text{-}iir\text{-}impl}.
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
\mathbf{Payable\text{-}condition}
:=
\left[
\bigl(\operatorname{diag}(\mathbf{iir})\mathbf{diff\text{-}jur}\bigr)
\lor
\bigl((\mathbf{dom\text{-}iir}\odot\mathbf{iir})\mathbf{1}_N^T\bigr)
\right]\operatorname{diag}(\mathbf{member}).
$$

This requires the Parent Entity's jurisdiction to have an IIR and, for a domestic low-taxed Entity, to apply that IIR domestically.

Restrict the rows to UPEs and IPEs, and separately to POPEs:

$$
\mathbf{Upe\text{-}ipe\text{-}candidate}
:=
\operatorname{diag}(\mathbf{upe}\oplus\mathbf{ipe})\mathbf{Payable\text{-}condition},
$$

$$
\mathbf{Pope\text{-}candidate}
:=
\operatorname{diag}(\mathbf{pope})\mathbf{Payable\text{-}condition}.
$$

Apply the top-down rule to UPEs and IPEs. An upper UPE or IPE displaces a lower IPE only when the upper Entity is located in a jurisdiction whose IIR has qualified status for the fiscal year:

$$
\mathbf{Qualified\text{-}upe\text{-}ipe\text{-}candidate}
:=
\operatorname{diag}(\mathbf{qiir})\mathbf{Upe\text{-}ipe\text{-}candidate},
$$

$$
\mathbf{Upper\text{-}upe\text{-}ipe}
:=
\mathbf{1}_{\{\mathbf{C}^{T}\mathbf{Qualified\text{-}upe\text{-}ipe\text{-}candidate}>0\}},
$$

$$
\mathbf{Upe\text{-}ipe\text{-}payable}
:=
\mathbf{Upe\text{-}ipe\text{-}candidate}
\land\neg\mathbf{Upper\text{-}upe\text{-}ipe}.
$$

For split ownership, define:

$$
(\mathbf{Wholly\text{-}own})_{ij}=1
\quad\Longleftrightarrow\quad
(\mathbf{Y})_{ij}=1,
$$

$$
\mathbf{Qualified\text{-}pope\text{-}candidate}
:=
\operatorname{diag}(\mathbf{qiir})\mathbf{Pope\text{-}candidate},
$$

Only a wholly-owning upper POPE in a QIIR jurisdiction displaces a lower POPE:

$$
\mathbf{Upper\text{-}pope}
:=
\mathbf{1}_{\{\mathbf{Wholly\text{-}own}^{T}\mathbf{Qualified\text{-}pope\text{-}candidate}>0\}},
$$

$$
\mathbf{Pope\text{-}payable}
:=
\mathbf{Pope\text{-}candidate}\land\neg\mathbf{Upper\text{-}pope}.
$$

The final IIR payability matrix is:

$$
\boxed{
\mathbf{Iir\text{-}payable}
:=
\mathbf{Upe\text{-}ipe\text{-}payable}
\oplus
\mathbf{Pope\text{-}payable}
}
$$

Each non-zero element $(\mathbf{Iir\text{-}payable})_{ij}$ produces a row in `Relation.IirPayables` for Parent Entity $i$ and potential low-taxed Entity $j$. Whether Entity $j$ is actually low-taxed and the Parent Entity's Income Inclusion Ratio are determined later in [IIR.md](IIR.md).

## Jurisdiction-Level Taxing Rights

### IIR Taxing Rights

Aggregate Entity-level IIR payability to jurisdictions:

$$
\mathbf{Parent\text{-}jur}
:=
\mathbf{1}_{\{\mathbf{Iir\text{-}payable}\,\mathbf{Entt\text{-}jur}>0\}},
$$

$$
\mathbf{Iir\text{-}taxing\text{-}rights}
:=
\mathbf{1}_{\{\mathbf{Entt\text{-}jur}^{T}\mathbf{Parent\text{-}jur}>0\}}.
$$

Thus, $(\mathbf{Iir\text{-}taxing\text{-}rights})_{kl}=1$ iff at least one Parent Entity in jurisdiction $k$ is IIR-payable for an Entity in jurisdiction $l$.

Define the IIR collecting-jurisdiction indicator:

$$
\mathbf{iir\text{-}right\text{-}jur}
:=
\mathbf{1}_{\{\mathbf{Iir\text{-}taxing\text{-}rights}\mathbf{1}_M>0\}}.
$$

### UTPR Taxing Rights

Define the jurisdictions containing at least one CE and the jurisdictions containing at least one potential low-taxed Entity:

$$
\mathbf{ce\text{-}presence}
:=
\mathbf{1}_{\{\mathbf{Entt\text{-}jur}^{T}\mathbf{ce}>0\}},
\qquad
\mathbf{member\text{-}presence}
:=
\mathbf{1}_{\{\mathbf{Entt\text{-}jur}^{T}\mathbf{member}>0\}}.
$$

A jurisdiction is a potential UTPR collecting jurisdiction if it has implemented the UTPR and contains at least one CE:

$$
\mathbf{utpr\text{-}right\text{-}jur}
:=
\mathbf{ce\text{-}presence}\odot\mathbf{utpr\text{-}impl}.
$$

The simplified jurisdiction-pair matrix is:

$$
\mathbf{Utpr\text{-}taxing\text{-}rights}
:=
\mathbf{utpr\text{-}right\text{-}jur}\,\mathbf{member\text{-}presence}^{T}.
$$

This identifies potential UTPR taxing rights only. The UTPR percentage, allocation key, and amount collected are calculated in [05.UTPR.md](05.UTPR.md).

The separate $\mathbf{qutpr\text{-}impl}$ vector records qualified status for qualification-dependent coordination rules. It is not substituted for $\mathbf{utpr\text{-}impl}$ in this potential-right test, which asks whether domestic UTPR legislation applies.

### QDMTT Taxing Rights

A jurisdiction has potential QDMTT taxing rights over its own Entities if it has implemented a QDMTT and contains at least one potential low-taxed Entity:

$$
\mathbf{qdmtt\text{-}right\text{-}jur}
:=
\mathbf{member\text{-}presence}\odot\mathbf{qdmtt\text{-}impl},
$$

$$
\mathbf{Qdmtt\text{-}taxing\text{-}rights}
:=
\operatorname{diag}(\mathbf{qdmtt\text{-}right\text{-}jur}).
$$

### Combined Taxing Rights

The jurisdiction-pair matrix is the Boolean union of the three charging mechanisms:

$$
\boxed{
\mathbf{Taxing\text{-}rights}
:=
\mathbf{Iir\text{-}taxing\text{-}rights}
\lor
\mathbf{Utpr\text{-}taxing\text{-}rights}
\lor
\mathbf{Qdmtt\text{-}taxing\text{-}rights}
}
$$

For Tested Jurisdiction $l$, its taxing-right jurisdictions are the union in column $l$:

$$
\boxed{
\mathbf{taxing\text{-}right\text{-}jur}^{(l)}
:=
(\mathbf{Iir\text{-}taxing\text{-}rights})_{:,l}
\lor
(\mathbf{Utpr\text{-}taxing\text{-}rights})_{:,l}
\lor
(\mathbf{Qdmtt\text{-}taxing\text{-}rights})_{:,l}
=
(\mathbf{Taxing\text{-}rights})_{:,l}
}
$$

The group-wide set of jurisdictions with at least one potential taxing right is the direct Boolean union of the IIR, UTPR, and QDMTT collecting-jurisdiction indicators:

$$
\boxed{
\mathbf{taxing\text{-}right\text{-}jur}
:=
\mathbf{iir\text{-}right\text{-}jur}
\lor
\mathbf{utpr\text{-}right\text{-}jur}
\lor
\mathbf{qdmtt\text{-}right\text{-}jur}
}
$$

Equivalently, $\mathbf{taxing\text{-}right\text{-}jur}=\mathbf{1}_{\{\mathbf{Taxing\text{-}rights}\mathbf{1}_M>0\}}$.
