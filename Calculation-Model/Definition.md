# Definitions

This document defines terminology, notation, and model objects that are shared across the Calculation Model. Calculation-specific documents should refer to these definitions rather than redefining them locally.

Functions exported by calculation-specific documents are defined in those source documents; references here use those exports.

## Terminology and Abbreviations

- **MNE** means Multinational Enterprise.
- **UPE** means Ultimate Parent Entity.
- **CE** means Constituent Entity.
- **PE** means Permanent Establishment.
- **IE** means Investment Entity.
- **EE** means Excluded Entity.
- **JV** means Joint Venture.
- **JV Subsidiary** means a member of a JV Group other than the JV itself.
- **IPE** means Intermediate Parent Entity.
- **POPE** means Partially-Owned Parent Entity.
- **IIR** means Income Inclusion Rule.
- **UTPR** means Undertaxed Profits Rule.
- **QDMTT** means Qualified Domestic Minimum Top-up Tax.
- **ETR** means Effective Tax Rate.
- **OI** means Ownership Interest.

## Mathematical Notation

Let $N$ be the number of Entities in the modelling universe. Unless otherwise stated, vectors are $N\times1$ and matrices are $N\times N$.

- $I$ is the $N\times N$ identity matrix.
- $\mathbf{1}_N$ and $\mathbf{0}_N$ are the all-one and all-zero vectors.
- $\mathbf{1}^{N\times N}$ and $\mathbf{0}^{N\times N}$ are the corresponding all-one and all-zero matrices.
- $\operatorname{diag}(v)$ places vector $v$ on the diagonal of a square matrix.
- $\operatorname{diag}(A)$ means the diagonal matrix containing the diagonal elements of square matrix $A$.
- $\odot$ denotes element-wise multiplication.
- $\lor$, $\land$, and $\neg$ denote element-wise Boolean OR, AND, and NOT.
- $\oplus$ denotes element-wise XOR and is used only where the relevant indicator sets are mutually exclusive.
- $e_j$ is the $j$-th standard basis vector.
- $\mathbf{1}_{\{\cdot\}}$ denotes an indicator obtained from the condition in braces.

For a non-negative scalar or vector element, define the positive reciprocal operator:

$$
x_j^\dagger :=
\begin{cases}
\dfrac{1}{x_j}, & x_j>0,\\
0, & x_j=0.
\end{cases}
$$

## Ownership Interest

Let

$$
X_0\in[0,1]^{N\times N}
$$

be the direct Ownership Interest matrix derived from `Relation.DirectOwnershipInterests.direct_ownership_ratio`, with investor Entities on rows and investee Entities on columns.

Let

$$
X_0^{\text{profit}}\in[0,1]^{N\times N}
$$

be the corresponding direct Profit Ownership Interest matrix derived from `Relation.DirectOwnershipInterests.direct_ownership_profit_ratio`.

Import $f$ from [Ownership Interest.md](<Ownership Interest.md#exports>). That document defines and exports the direct and indirect Ownership Interest function; $f(A)$ applies it to direct ownership matrix $A$.

Accordingly:

$$
Y:=f(X_0)
$$

is the direct-and-indirect Ownership Interest matrix.

Any calculation that requires a restricted ownership graph should apply the relevant mask explicitly. In general, masking before and after the direct-and-indirect ownership calculation are not equivalent:

$$
\operatorname{diag}(v)f(X_0)\operatorname{diag}(v)
\neq
f\bigl(\operatorname{diag}(v)X_0\operatorname{diag}(v)\bigr).
$$

The appropriate timing of a mask therefore depends on the rule being modelled.

## Controlling Interest

Let

$$
C\in\{0,1\}^{N\times N}
$$

be the direct-and-indirect Controlling Interest matrix exported by [Controlling Interest.md](<Controlling Interest.md#direct-and-indirect-controlling-interest-function>), where:

$$
C_{ij}=1
$$

iff Entity $i$ directly or indirectly controls Entity $j$.

## Common Entity Indicator Vectors

Unless a calculation document specifies otherwise, the following indicator vectors are derived from the corresponding Relations for the relevant fiscal year:

- $\text{group-upe}_i=1$ iff Entity $i$ has a matching row in `Relation.ConstituentEntities` with `is_upe == true` for the relevant fiscal year; otherwise it is 0.
- $\text{ce}_i=1$ iff Entity $i$ has a row in `Relation.ConstituentEntities` for the relevant fiscal year.
- $\text{pe}_i=1$ iff Entity $i$ has a row in `Relation.PermanentEstablishments` for the relevant fiscal year.
- $\text{ee}_i=1$ iff Entity $i$ has a row in `Relation.ExcludedEntities` for the relevant fiscal year.
- $\text{fte}_i=1$ iff Entity $i$ has a row in `Relation.FlowThroughEntities` for the relevant fiscal year.
- $\text{ie}_i=1$ iff Entity $i$ has a row in `Relation.InvestmentEntities` for the relevant fiscal year.
- $\text{jv}_i=1$ iff `Relation.JvEntities.is_jv` is true for Entity $i$.
- $\text{jvsub}_i=1$ iff `Relation.JvEntities.is_jv_sub` is true for Entity $i$.

These vectors describe Entity characteristics independently of whether a particular calculation subsequently includes or excludes those Entities from its calculation group.

Construct each indicator over the full Entity ordering in `Relation.CompanyEntities`. For classification relations, match on both `fiscal_year` and `entity_id`; absence of a matching row gives an indicator value of 0. Classification indicators may overlap where applicable, such as an Entity that is both a CE and a PE. CE and EE indicators must not overlap.
