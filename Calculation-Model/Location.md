Every Entity is given the jurisdiction where it is located, or for a Flow-through Entity or a Permanent Establishment described in paragraph (d) of its definition, the jurisdiction where it was created. Such an Entity starts stateless and moves to its jurisdiction of creation once it is required to apply an IIR (Article 10.3.2).

# Inputs

| Symbol | Type | Meaning |
| --- | --- | --- |
| $\mathbf{Entt\text{-}cjur}$ | $\{0,1\}^{N\times M}$ | The jurisdiction where each Entity is located, or for a Flow-through Entity or a PE of paragraph (d), the jurisdiction where it was created |
| $\mathbf{fte\text{-}tt},\mathbf{reverse\text{-}hybrid}$ | $\{0,1\}^{N\times1}$ | Tax Transparent Entities and Reverse Hybrid Entities |
| $\mathbf{pe\text{-}d}$ | $\{0,1\}^{N\times1}$ | PEs described in paragraph (d) of the definition |
| $\mathbf{group\text{-}upe}$ | $\{0,1\}^{N\times1}$ | The group's UPEs |

# Validation

$$
\boxed{\mathbf{Entt\text{-}cjur}\times\mathbf{1}_M\le\mathbf{1}_N,\qquad\mathbf{Entt\text{-}cjur}\times\mathbf{1}_M\ge\neg\mathbf{pe\text{-}d}}
$$

Each Entity has at most one jurisdiction, and only a PE of paragraph (d) may have none.

# Location State

A location state is a vector $\mathbf{s}\in\{0,1\}^{N\times1}$ of Stateless Entities. It places every other Entity in its given jurisdiction:

$$
\boxed{
\mathbf{Entt\text{-}jur}(\mathbf{s}):=\operatorname{diag}(\mathbf{1}_N-\mathbf{s})\times\mathbf{Entt\text{-}cjur}
}
$$

The Flow-through Entities, and the Entities that start stateless, are

$$
\begin{aligned}
\mathbf{fte}&:=\mathbf{fte\text{-}tt}\lor\mathbf{reverse\text{-}hybrid}\\
\mathbf{s}_0&:=(\mathbf{fte}\land\neg\mathbf{group\text{-}upe})\lor\mathbf{pe\text{-}d}
\end{aligned}
$$

A Flow-through Entity that is the UPE is located where it was created from the start (Article 10.3.2(a)).

# Required to Apply an IIR

An Entity is required to apply an IIR when, located in its jurisdiction of creation, it would be payable for an Entity that has Top-up Tax after the QDMTT. Payability is tested with every Flow-through Entity at its jurisdiction of creation:

$$
\mathbf{Iir\text{-}payable}^{c}:=\text{the }\mathbf{Iir\text{-}payable}\text{ of [Taxing Rights](<Taxing Rights.md#iir-payability>) with }\mathbf{Entt\text{-}jur}(\mathbf{s}_0\land\neg\mathbf{fte})
$$

$\mathbf{Iir\text{-}payable}^{c}$ does not depend on the location state, so it is calculated once.

For a location state $\mathbf{s}$, let $\mathbf{tt\text{-}entt}(\mathbf{s})$ be the Top-up Tax of each Entity from [Top-up Tax Calculation](<Top-up Tax Calculation.md>), with the [ETR Calculation Groups](<Group.md#etr-calculation-group>) built from $\mathbf{Entt\text{-}jur}(\mathbf{s})$ and $\mathbf{s}$. Then

$$
\boxed{
\mathbf{required}(\mathbf{s}):=\mathbf{s}\land\left[\left(\mathbf{Iir\text{-}payable}^{c}\times\mathbf{tt\text{-}entt}(\mathbf{s})\right)>0\right]
}
$$

# Fixed Point

$$
\boxed{
\mathbf{s}_{k+1}:=\mathbf{s}_k\land\neg\mathbf{required}(\mathbf{s}_k),
\qquad
\mathbf{stateless}:=\mathbf{s}_K\ \text{ where }\ \mathbf{s}_{K+1}=\mathbf{s}_K
}
$$

An Entity that has moved stays located, so $\mathbf{s}_k$ only loses entries and the iteration stops after at most $\mathbf{s}_0^{T}\mathbf{1}_N+1$ evaluations of $\mathbf{tt\text{-}entt}$. The final location is

$$
\boxed{
\mathbf{Entt\text{-}jur}:=\mathbf{Entt\text{-}jur}(\mathbf{stateless})
}
$$

and every other document uses $\mathbf{Entt\text{-}jur}$ and $\mathbf{stateless}$ from here.

**One pass.** A Flow-through Entity whose GloBE Income or Loss, Adjusted Covered Taxes and Substance-based Income Exclusion are all zero, because Article 3.5 allocates them to its owners, changes no group amount when it moves: it only leaves its own stateless group for the group of its jurisdiction of creation. If every Flow-through Entity in $\mathbf{s}_0$ is of that kind, $\mathbf{tt\text{-}entt}(\mathbf{s}_1)=\mathbf{tt\text{-}entt}(\mathbf{s}_0)$ and $K\le1$.

**Group inputs.** The group inputs of Top-up Tax Calculation are given for each Full Calculation Group by its jurisdiction (or Stateless Entity), $\mathbf{group\text{-}id}$ and $\mathbf{ie}$. An Entity that moves takes the inputs of the group it joins.

# Not Covered

- How a Flow-through Entity that moves affects the [Transitional CbCR Safe Harbour](<Transitional CbCR Safe Harbours Test.md>); the TCSH Group uses $\mathbf{s}_0$.
