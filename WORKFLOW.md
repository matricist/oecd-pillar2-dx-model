# GloBE Calculation Workflow

This document describes the high-level orchestration flow of the GloBE model.

The key architectural distinction is that **local QDMTT computation** and the **GloBE IIR/UTPR computation** should be treated as parallel branches. A Side-by-Side Safe Harbour election may switch off the GloBE IIR/UTPR branch, but it does not switch off local QDMTT obligations.

## High-Level Flow

```text
                 MNE Group
                     │
            ┌────────┴────────┐
            │                 │
      Local QDMTT         GloBE Rules
            │                 │
        Calculate          SbS SH?
                              │
                     ┌────────┴────────┐
                    YES               NO
                     │                 │
                IIR/UTPR = 0       TCSH
                                      ↓
                                    SESH
                                      ↓
                                 Art. 5.5
                                      ↓
                                 QDMTT SH
                                      ↓
                                Full GloBE
                                      ↓
                                     IIR
                                      ↓
                                    UTPR
```

## 0. Parallel Local QDMTT Branch

Where a jurisdiction has implemented a QDMTT, the local QDMTT is calculated under that jurisdiction's domestic QDMTT rules.

This branch is separate from the GloBE IIR/UTPR branch.

- Side-by-Side Safe Harbour does not eliminate a local QDMTT liability.
- A local QDMTT calculation is not the same thing as the QDMTT Safe Harbour.
- QDMTT Safe Harbour is relevant to whether a separate GloBE jurisdictional computation is required for IIR/UTPR purposes.

## 1. Side-by-Side Safe Harbour Gate

The first gate in the GloBE branch should determine whether the MNE Group is eligible for, and has made, the Side-by-Side Safe Harbour election.

If the Side-by-Side Safe Harbour applies:

- IIR and UTPR are switched off for the relevant GloBE computation.
- Steps 2 through 6 below do not need to be performed for IIR/UTPR purposes.
- Their status should be treated as **Not Applicable / Not Computed**, rather than as having passed a Safe Harbour.
- Local QDMTT calculations remain in the parallel QDMTT branch.

If the Side-by-Side Safe Harbour does not apply, proceed with the normal GloBE flow below.

## 2. Transitional CbCR Safe Harbour

Apply the Transitional CbCR Safe Harbour tests.

If the jurisdiction qualifies, the GloBE Top-up Tax for the relevant jurisdiction is treated as zero for the fiscal year and no further jurisdictional GloBE computation is required, subject to the applicable Safe Harbour rules and elections.

## 3. Simplified ETR Safe Harbour

If the Transitional CbCR Safe Harbour does not apply, test the Simplified ETR Safe Harbour.

If the jurisdiction qualifies, the GloBE Top-up Tax is treated as zero and the full GloBE jurisdictional computation can be avoided.

## 4. Article 5.5 De Minimis Exclusion

If no preceding Safe Harbour applies, test the Article 5.5 De Minimis Exclusion.

If the conditions are met, the Top-up Tax for the relevant jurisdiction is treated as zero.

## 5. QDMTT Safe Harbour

If the jurisdiction is covered by a qualifying QDMTT Safe Harbour, a separate full GloBE jurisdictional Top-up Tax computation may be avoided for IIR/UTPR purposes in accordance with the applicable QDMTT Safe Harbour rules.

This step must be distinguished from the local QDMTT calculation itself.

## 6. Full GloBE Top-up Tax Calculation

If none of the preceding Safe Harbours or exclusions applies, perform the full GloBE computation.

The high-level calculation includes:

1. GloBE Income or Loss
2. Adjusted Covered Taxes
   - including any applicable SBTI Safe Harbour treatment
3. Jurisdictional ETR
4. Top-up Tax Percentage
5. Substance-based Income Exclusion
6. Jurisdictional Top-up Tax

The SBTI Safe Harbour is treated within the Covered Taxes / ETR computation rather than as a separate post-computation zeroing rule.

## 7. IIR

After determining the jurisdictional Top-up Tax, apply the IIR allocation rules to determine the amount chargeable to the relevant Parent Entity or Parent Entities.

## 8. UTPR

To the extent that Top-up Tax remains after application of the IIR, apply the UTPR rules.

At this stage, consider the applicable UTPR-level Safe Harbour or relief rules, including:

- Transitional UTPR Safe Harbour, where applicable for the relevant fiscal year; and
- UPE Safe Harbour, where applicable.

These rules should be treated according to their applicable fiscal-year regimes rather than simply as sequential fallback tests.

## Architecture Summary

Conceptually, the model should therefore be orchestrated as:

```text
QDMTT Engine ────────────────┐
                             │
                             ├─ MNE Group
                             │
GloBE Engine                 │
  ├─ SbS SH gate             │
  ├─ TCSH                    │
  ├─ SESH                    │
  ├─ Article 5.5             │
  ├─ QDMTT SH                │
  ├─ Full GloBE              │
  │    └─ SBTI SH within ETR │
  ├─ IIR                     │
  └─ UTPR                    │
```

This separation avoids unnecessary GloBE calculations for Side-by-Side Safe Harbour groups while preserving local QDMTT calculations where required.
