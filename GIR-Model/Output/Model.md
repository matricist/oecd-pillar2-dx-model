# Output Model

The GloBE Information Return schema (`../globe-xsd`) expressed as atomic vectors and matrices together with the equations they must satisfy. A document is schema-valid iff every equation holds. The [Input Model](../Input/Model.md) and the [Link Model](../Link/Model.md) produce these atoms. `generate.py` derives everything below from the XSD.

# Atoms

| Atom | Type | One per | Count |
| --- | --- | --- | --- |
| $n_r$ | $\mathbb{N}$ | Relation $r$ | 84 |
| $\mathbf{P}_r$ | $\{0,1\}^{n_q\times n_r}$ | Relation $r$ other than the root, with parent relation $q$ | 83 |
| $\mathbf{x}_v$ | $D_t^{\,n_r}$ | Simple-typed element, attribute, or text value | 493 |
| $\boldsymbol{\pi}_v$ | $\{0,1\}^{n_r}$ | Optional node | 255 |

- **Relation.** The root element and every element that may occur more than once is a relation with $n_r$ rows. Every other node is inlined into the nearest enclosing relation.
- **Parent matrix.** $(\mathbf{P}_r)_{ij}=1$ iff row $j$ of $r$ is a child of row $i$ of its parent relation.
- **Value vector.** Entry $i$ is the value of the node in row $i$; $D_t$ is the value space of its type $t$.
- **Presence vector.** Entry $i$ is 1 iff the node is present in row $i$. Optional nodes are optional elements, optional attributes, optional sequences, and the alternatives of a choice.

A required node has no presence vector. Its presence is its context $\mathbf{c}$: the presence vector of the nearest enclosing optional node in the same relation, or $\mathbf{1}$ if there is none.

# Equations

For a relation $r$ with bounds $[\mathit{lo},\mathit{hi}]$ declared in context $\mathbf{c}$ of its parent relation:

| Kind | Equation | Count |
| --- | --- | --- |
| Root | $n_{r_1}=1$ | 1 |
| Parent | $\mathbf{P}_r^{T}\times\mathbf{1}=\mathbf{1}$ | 83 |
| Occurrence | $\mathit{lo}\cdot\mathbf{c}\le\mathbf{P}_r\times\mathbf{1}\le\mathit{hi}\cdot\mathbf{c}$ | 84 |
| Nesting | $\boldsymbol{\pi}_v\le\mathbf{c}$ | 113 |
| Choice | $\sum_k\mathbf{a}_k=\mathbf{c}$ | 8 |
| Type | $\tau_t(\mathbf{x}_v)\ge\mathbf{c}$ | 493 |

- **Occurrence.** $\mathbf{P}_r\times\mathbf{1}$ counts the children of each parent row. With $\mathit{hi}$ unbounded the upper bound becomes $(\mathbf{1}-\mathbf{c})\odot(\mathbf{P}_r\times\mathbf{1})=\mathbf{0}$.
- **Choice.** $\mathbf{a}_k$ is the presence of alternative $k$: its presence vector, or $(\mathbf{P}_r\times\mathbf{1})>0$ for a repeated element.
- **Type.** $\tau_t$ maps a value vector to a Boolean vector, element-wise: 1 iff the value is valid for type $t$.

# Types

The 44 types in use reduce to four kinds of $\tau_t$:

| Kind | Types | $\tau_t(x)$ |
| --- | --- | --- |
| Enumeration | 35 | $x$ is one of the $m_t$ values in [Types.md](Types.md); with values encoded by position, $1\le x\le m_t$ |
| Bounded string | 4 | $\mathit{lo}_t\le\operatorname{len}(x)\le\mathit{hi}_t$ |
| Percentage | 1 | $0\le x\le1$ and $10^{4}x\in\mathbb{Z}$ |
| Built-in | 4 | $x$ is a boolean, integer, date, or dateTime |

Only $\operatorname{len}$ and the built-in lexical forms are not arithmetic. The types in use have no pattern, list, or union.

# Example

The relation `UPE` (`r004`) is a choice between `ExcludedUPE` and `OtherUPE`, each with a repeated `TIN`:

$$
\begin{aligned}
\boldsymbol{\pi}_{\text{ExcludedUPE}}+\boldsymbol{\pi}_{\text{OtherUPE}}&=\mathbf{1}\\
\mathbf{P}_{\text{TIN}}^{T}\times\mathbf{1}&=\mathbf{1}\\
\mathbf{P}_{\text{TIN}}\times\mathbf{1}&\ge\boldsymbol{\pi}_{\text{ExcludedUPE}}\\
(\mathbf{1}-\boldsymbol{\pi}_{\text{ExcludedUPE}})\odot(\mathbf{P}_{\text{TIN}}\times\mathbf{1})&=\mathbf{0}\\
\tau_{\text{ExcludedUPE\_EnumType}}(\mathbf{x}_{\text{ExcludedUPEStatus}})&\ge\boldsymbol{\pi}_{\text{ExcludedUPE}}
\end{aligned}
$$

Every UPE row is exactly one of the two; an Excluded UPE has at least one TIN and a valid status, and a row that is not an Excluded UPE has no TIN in that relation.

# Not Expressed

- **Order.** Elements are serialized in schema order, which is the order of the vectors in [Equations.md](Equations.md); rows are serialized in index order.
- **Namespaces.** An element takes the target namespace of the schema that declares it, so the children of `DocSpec` are in the `stf` namespace and every other element in `globe`. `serialize.py` applies this.
- **Atom shapes.** That $\mathbf{P}_r$ is $n_q\times n_r$, that vectors have $n_r$ entries, and that presence entries are 0 or 1 is assumed, not stated as an equation.
- **Annotations.**

# Files

| File | Content |
| --- | --- |
| [Equations.md](Equations.md) | The 782 equations, by relation, with the vectors of each relation |
| [Types.md](Types.md) | The 44 types, their predicates, and the enumeration values |
| `generate.py` | Derives both files from the XSD: `python generate.py` |
| `serialize.py` | Writes a set of atoms as GIR XML |

# Relation to `../Relations.md`

`../Relations.md` also converts the XSD into relations, with one relation per complex element (156). This model creates a relation only where an element can repeat (84) and inlines the rest. The two agree on the content: the 493 value vectors here are exactly the 493 value-bearing nodes of `../output_model.csv`, path by path.
