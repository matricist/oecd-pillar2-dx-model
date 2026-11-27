# Calculation Model Workflow

A document index arranged in the workflow order.

The documents below calculate one Fiscal Year $t$, the map

$$
(\mathbf{x}_{t+1},\ \mathbf{out}_t):=F(\mathbf{x}_t,\ \mathbf{in}_t)
$$

from the state $\mathbf{x}_t$ carried in and the year's input $\mathbf{in}_t$ (ownership, control, amounts, legislation) to the state carried out and the year's results $\mathbf{out}_t$ (Top-up Tax, IIR and UTPR allocation, return). Within $t$, the [effective periods](<Ownership Interest.md#effective-periods>) are calculated each for itself; the state changes only from one Fiscal Year to the next.

| State | Kept for | In | Out |
| --- | --- | --- | --- |
| Excess Negative Tax Expense | $\mathbf{group\text{-}key}$ | $\mathbf{ente\text{-}prior}$ | $\mathbf{ente\text{-}next}$ of [Top-up Tax Calculation](<Top-up Tax Calculation.md>) |
| Tested Jurisdiction excluded from the TCSH | $\mathbf{tcsh\text{-}key}$ | $\mathbf{once\text{-}out}_{y-1}$ | $\mathbf{once\text{-}out}_{y}$ of [TCSH](<Transitional CbCR Safe Harbours Test.md>) |
| Filed Top-up Tax of each Entity | $\mathbf{entity\text{-}id}$ | [Recalculation](<Top-up Tax Calculation.md#recalculation-of-earlier-fiscal-years>) | $\mathbf{tt\text{-}entt}$ |

Group balances are kept for their keys as in [Continuity Across Fiscal Years](<Group.md#continuity-across-fiscal-years>).

## 1. Foundations

- [Example](Example.md)

## 2. Transitional CbCR Safe Harbours Test

1. [Ownership and Controlling Interest](<Ownership Interest.md>)
2. [Initial Location](<Location.md#location-state>)
3. [JV Groups](<Subgroups.md#jv-groups>)
4. [TCSH Group](<Group.md#tcsh-group>)
5. [Transitional CbCR Safe Harbours Test](<Transitional CbCR Safe Harbours Test.md>)

## 3. Top-up Tax Calculation

1. [Minority-Owned Subgroups](<Subgroups.md#minority-owned-subgroups>)
2. [ETR Calculation Group](<Group.md#etr-calculation-group>)
3. GloBE De Minimis — document pending
4. [Top-up Tax Calculation](<Top-up Tax Calculation.md>)

## 4. Applying IIR

1. Side by Side Safe harbour — document pending
2. [Location of Flow-through Entities](<Location.md#fixed-point>): repeat 3.2 to 3.4 until the location state no longer changes
3. [Taxing Rights](<Taxing Rights.md>)
4. [IIR](IIR.md)

## 5. Applying UTPR

1. UTPR Safe Harbour and UPE Safe Harbour — document pending
2. [UTPR](UTPR.md)
