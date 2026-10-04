# Interface

## Imports

- Relations.CompanyEntities
- Relations.ConstituentEntities
- Relations.PermanentEstablishments
- Relations.DirectOwnershipInterests
- Common Entity indicator names (`ce`, `pe`, and `group-upe`) from [Definition.md](<Definition.md#common-entity-indicator-vectors>).
- $f(\mathbf{A})$ from [Ownership Interest.md](<Ownership Interest.md#exports>), used to compute direct and indirect ownership ratios for controller recommendations.

## Exports

### Direct and Indirect Controlling Interest Function

This document defines and exports `calculate_controlling_interest(C0)` for use throughout the Calculation Model.

- **Input:** A confirmed direct controlling interest matrix $\mathbf{C}_0\in\{\mathrm{False},\mathrm{True}\}^{N\times N}$, with controlling Entities on rows and controlled Entities on columns. Structural and domain validation must already be complete.
- **Output:** The direct and indirect controlling interest matrix $\mathbf{C}$, preserving the input Entity ordering. An element $(\mathbf{C})_{ij}$ is `True` if Entity $i$ directly or indirectly controls Entity $j$.
- **Runtime validation:** Raise `RuntimeValidationError` if any diagonal element of the transitive closure is `True`; do not return a result for self-control or circular control.

The implementation below specifies this exported function.

### Controller Recommendation Function

This document also exports `recommend_controller`, the controller recommendation procedure specified below.

- **Input:** A target Entity $j$, the validated direct ownership matrix $\mathbf{X}_0$, shared ownership results $\mathbf{Y}=f(\mathbf{X}_0)$ and direct shareholder lists, Entity classifications and UPE assignments, a nonnegative finite tie tolerance, and optionally the confirmed direct and indirect controlling interest matrix $\mathbf{C}$.
- **Output:** The EntityId of a recommended controller, or `null` if no candidate is selected. The candidate may be a direct shareholder or an upstream shareholder.
- **Interpretation:** A recommendation does not establish a confirmed direct controlling relationship and must not automatically be inserted into $\mathbf{C}_0$.
- **Combined validation:** Before confirming multiple recommendations as controlling relationships, validate the combined graph against all structural and domain rules, including the runtime cycle check. Recommendations made independently against the same $\mathbf{C}$ can conflict with each other.

# Validation

## Structural Validation

- If an Entity directly controls another Entity, the latter must not directly control the former.

## Domain Validation

- Apply the Entity-classification-dependent cross-table rules defined for `DirectControllingInterests` in [Relations.md](Relations.md#cross-table-validation), including the UPE, non-UPE CE, and PE/CE controller rules.

# Implementation

## Transitive Closure Using Warshall's Algorithm

Let $\mathbf{C}_0\in\{\mathrm{False},\mathrm{True}\}^{N\times N}$ denote the confirmed direct controlling interest matrix, where $(\mathbf{C}_0)_{ij}$ is `True` if Entity $i$ directly controls Entity $j$.

Compute the direct and indirect controlling interest matrix using Warshall's algorithm:

$$
\mathbf{C}^{(0)} = \mathbf{C}_0
$$
$$
(\mathbf{C}^{(k)})_{ij}
=
(\mathbf{C}^{(k-1)})_{ij}
\lor
\left(
(\mathbf{C}^{(k-1)})_{ik}
\land
(\mathbf{C}^{(k-1)})_{kj}
\right)
$$

At step $k$, Entity $k$ is added to the set of permitted intermediate Entities. After processing $k=1,\dots,N$, the final matrix $\mathbf{C}=\mathbf{C}^{(N)}$ indicates whether a direct or indirect controlling path exists between each pair of Entities.

Initialize with $\mathbf{C}_0$ only; do not add the identity matrix or automatically set diagonal elements to `True`.

### Bitset Implementation

An implementation may store each row of $\mathbf{C}$ as an array of fixed-width bitset words rather than as individual Boolean values. Let $B$ be the number of bits in one word. For Entity index $j$, define

$$
w(j)=\left\lfloor\frac{j}{B}\right\rfloor,
\qquad
b(j)=j\bmod B.
$$

Bit $b(j)$ of word $w(j)$ in row $i$ represents $(\mathbf{C})_{ij}$. Initialize the bitset rows by copying $\mathbf{C}_0$. At Warshall step $k$, test bit $b(k)$ of word $w(k)$ in each row $i$. If that bit is set, update the complete row word by word:

$$
\mathbf{C}_{i,*}\leftarrow\mathbf{C}_{i,*}\mathbin{\mathrm{OR}}\mathbf{C}_{k,*}.
$$

This is equivalent to the Boolean Warshall update because the row-wise OR is performed exactly when $(\mathbf{C})_{ik}$ is `True`. With $W=\lceil N/B\rceil$ words per row, the closure requires $O(N^2W)$ word operations and $O(NW)$ words of storage. A concrete implementation may choose a word width supported efficiently by its execution environment. The final unused bits in the last word have no semantic meaning and are ignored.

The bitset optimization does not change validation semantics. In particular, do not clear diagonal bits after computing the closure. Inspect each diagonal bit and reject the complete result if any is set.

## Runtime Validation of Circular Control

After computing the transitive closure, inspect the diagonal of $\mathbf{C}$. If any diagonal element $(\mathbf{C})_{ii}$ is `True`, Entity $i$ can reach itself through a controlling path, indicating direct self-control or a cycle involving multiple Entities.

In this case, raise a **Runtime Validation Error** and reject the result. Do not clear the diagonal elements to conceal the cycle. Return $\mathbf{C}$ only if every diagonal element is `False`.

# Controller Recommendation Algorithm

## Inputs and Notation

This document preserves the model's existing names and distinguishes types by notation: bold uppercase symbols denote matrices, bold lowercase names denote column vectors, and calligraphic symbols denote sets. Indices, scores, tolerances, and individual vector or matrix entries are scalars. `PE`, `CE`, and `UPE` remain domain abbreviations in prose.

For example, $\mathbf{pe}$ is a vector, $\text{pe}_i$ is its scalar entry, $\mathbf{Y}$ is a matrix, and $(\mathbf{Y})_{ij}$ is its scalar entry. Boldface adds type information to the existing names in Definition.md; it does not define different model objects.

| Symbol | Type and meaning |
|---|---|
| $\mathcal{V}=\{1,\ldots,N\}$ | Set of Entity indices; $N$ is the number of Entities, as in Definition.md. |
| $\mathbf{X}_0\in[0,1]^{N\times N}$ | Validated direct ownership ratio matrix, using the existing model name. |
| $\mathbf{Y}=f(\mathbf{X}_0)\in[0,1]^{N\times N}$ | Direct and indirect ownership ratio matrix, using the existing model name. |
| $\mathbf{D}\in\{0,1\}^{N\times N}$ | Declared direct ownership relation matrix. $(\mathbf{D})_{ij}=1$ when an input row for investor $i$ and investee $j$ is explicitly present, including a row whose ordinary ownership ratio is zero. |
| $\mathbf{C}\in\{0,1\}^{N\times N}$ | Optional confirmed direct and indirect controlling interest matrix; 1 and 0 correspond to `True` and `False`. |
| $j\in \mathcal{V}$ | Scalar index of the target Entity. |
| $\mathbf{ce}\in\{0,1\}^{N\times1}$ | Existing Constituent Entity indicator vector; the scalar $\text{ce}_i=1$ means Entity $i$ is a CE. |
| $\mathbf{pe}\in\{0,1\}^{N\times1}$ | Existing PE indicator vector; the scalar $\text{pe}_i=1$ means Entity $i$ is a PE. |
| $\boldsymbol{\text{group-upe-index}}\in(\mathcal{V}\cup\{\mathrm{null}\})^{N\times1}$ | Entity-index vector introduced for this procedure. The scalar $\text{group-upe-index}_i$ identifies the UPE assigned to CE $i$. It may be `null` for other Entities. |
| $\varepsilon\ge0$ | Scalar absolute tolerance for treating nearly equal ownership ratios as tied. |

Controller recommendation uses ordinary ownership interests: $\mathbf{X}_0$ and the corresponding $\mathbf{Y}=f(\mathbf{X}_0)$. It must not use profit ownership interests or their direct and indirect ownership matrix. Profit ownership may be used by other classification or allocation procedures, but it neither establishes a controller candidate nor affects the ranking in this procedure.

An explicitly recorded zero ordinary ownership relationship is treated as a declared shareholder relationship. It may be used both to associate an Entity with a single group UPE and to form a controller candidate. The ratio remains zero for ranking: an otherwise equally eligible positive-ratio shareholder defeats a zero-ratio shareholder, while a sole eligible zero-ratio shareholder may be recommended.

The vector $\boldsymbol{\text{group-upe-index}}$ records which UPE an Entity belongs to. The existing indicator vector $\boldsymbol{\text{group-upe}}\in\{0,1\}^{N\times1}$ records whether an Entity is a group UPE, while `upe` in IIR.md identifies a non-Excluded UPE for IIR purposes. Each assigned UPE index must identify an Entity whose $\text{group-upe}_i$ value is 1. This procedure retains the single-UPE-per-group assumption.

The sets $\mathcal{F}_t$, $\mathcal{M}_t$, $\mathcal{H}_t$, and $\mathcal{T}_t$ below respectively contain current candidates, tied candidates, candidates already evaluated using indirect ownership, and candidates to expand. The score $s_t(i;j)$ and maximum $m_t$ are scalars.

The procedure assumes that Constituent Entities in a group fall under a common UPE. Matching Constituent Entity status therefore takes priority over ownership ranking.

Compute $\mathbf{Y}$ on the full ownership graph. The eligibility rules below filter recommendation candidates; they do not mask ownership paths before computing $f(\mathbf{X}_0)$.

Compute $\mathbf{Y}$ and the direct shareholder lists once for a given $\mathbf{X}_0$, then reuse them for all target Entities. Rebuild both whenever $\mathbf{X}_0$ or the Entity ordering changes.

## Eligible Candidates

If $\text{pe}_j=1$, or if $\text{ce}_j=1$ and $j=\text{group-upe-index}_j$, return `null`.

Otherwise, retain Entities with the same Constituent Entity status as the target, excluding the target itself and PEs:

$$
\mathcal{E}_j
=\{i\in \mathcal{V}:\text{ce}_i=\text{ce}_j,\ i\ne j,\ \text{pe}_i=0\}.
$$

For a Constituent Entity target, additionally restrict candidates to the same UPE group:

$$
\mathcal{E}_j\leftarrow
\{i\in\mathcal{E}_j:\text{group-upe-index}_i=\text{group-upe-index}_j\}.
$$

If a confirmed direct and indirect controlling interest matrix $\mathbf{C}$ is available, exclude candidates already controlled by the target:

$$
\mathcal{E}_j\leftarrow
\mathcal{E}_j\setminus\{i:(\mathbf{C})_{ji}=\mathrm{True}\}.
$$

This prevents recommending a relationship that would create a cycle with the confirmed controlling relationships.

## Initial Candidates and Ranking

Start with the target's eligible declared direct shareholders. Explicitly declared zero-ratio relationships are included:

$$
\mathcal{F}_0=\{i\in\mathcal{E}_j:(\mathbf{D})_{ij}=1\}.
$$

Use direct ownership ratios at the initial step and direct and indirect ownership ratios at subsequent steps:

$$
s_t(i;j)=
\begin{cases}
(\mathbf{X}_0)_{ij}, & t=0,\\
(\mathbf{Y})_{ij}, & t\ge1.
\end{cases}
$$

All scores refer to the original target $j$, even when evaluating upstream shareholders.

## Select the Largest Shareholder

If $\mathcal{F}_t$ is empty, return `null`. Otherwise, find the maximum score and collect every candidate within $\varepsilon$ of it:

$$
m_t=\max_{i\in \mathcal{F}_t}s_t(i;j),\qquad
\mathcal{M}_t=\{i\in \mathcal{F}_t:m_t-s_t(i;j)\le\varepsilon\}.
$$

If $|\mathcal{M}_t|=1$, return the EntityId of the unique candidate. If multiple candidates tie, expand only those tied candidates to their upstream shareholders.

The numerical comparison tolerance defaults to $\varepsilon=10^{-12}$ in ratio units to absorb small floating-point differences. This is a configurable numerical comparison tolerance, not a minimum ownership threshold. Set it according to the model's data precision and numerical accuracy requirements; $\varepsilon=0$ requests exact comparison.

## Upstream Search and Cycle Prevention

For a set of Entities $\mathcal{S}$, define its declared direct shareholders as

$$
\operatorname{Parents}(\mathcal{S})
=\{p\in \mathcal{V}:\exists i\in \mathcal{S},\ (\mathbf{D})_{pi}=1\}.
$$

Track candidates evaluated using direct and indirect ownership ratios separately from the initial direct-ownership comparison:

$$
\mathcal{H}_0=\varnothing,\qquad
\mathcal{H}_t=\bigcup_{r=1}^{t}\mathcal{F}_r\quad(t\ge1).
$$

For Constituent Entities, the UPE may be recommended but must not be expanded to its own shareholders. Define the tied candidates eligible for expansion as

$$
\mathcal{T}_t=
\begin{cases}
\mathcal{M}_t\setminus\{\text{group-upe-index}_j\}, & \text{ce}_j=1,\\
\mathcal{M}_t, & \text{ce}_j=0.
\end{cases}
$$

The next candidate set is

$$
\mathcal{F}_{t+1}
=\left(\operatorname{Parents}(\mathcal{T}_t)\cap\mathcal{E}_j\right)
\setminus \mathcal{H}_t.
$$

An Entity evaluated at step 0 may appear again as an upstream shareholder and be evaluated using $(\mathbf{Y})_{ij}$. After that evaluation, it is not evaluated again for the same target. Set operations merge duplicates within each step. There is one initial step and at most $N$ upstream candidate evaluations, so ownership cycles cannot cause an infinite search.

The same upstream search applies to non-Constituent Entities, without a UPE boundary. Reaching the UPE terminates only that expansion branch; other tied branches may continue.

## Result and Example

Return a candidate as soon as a step has a unique largest shareholder. If a non-UPE CE has no declared direct shareholder at all, return its assigned group UPE. This fallback does not apply when a declared shareholder exists but is ineligible, and it does not apply to a non-CE. Return `null` when no new eligible candidates remain. A `null` result means that this recommendation rule could not select a candidate; it does not establish that no controller exists.

For example, assume all shareholders below are eligible:

```text
P --100%--> A --50%--> J
P --100%--> B --50%--> J
```

The initial candidates tie:

$$
\mathcal{F}_0=\mathcal{M}_0=\{A,B\}.
$$

Their common shareholder appears once in the next candidate set:

$$
\mathcal{F}_1=\{P\},\qquad (\mathbf{Y})_{PJ}=1.
$$

The procedure recommends P itself, rather than choosing between A and B.

An initial candidate can also be the upstream shareholder selected later. If A owns 100% of B and A and B each directly own 50% of J, the initial comparison is tied. A is then evaluated as B's shareholder, with $(\mathbf{Y})_{AJ}=1$, and recommended. Evaluating A at step 0 must not exclude it from this later comparison.
