# Ester Agent

## Identity

**Name**: ester
**SMARTS**: `[CX3](=O)[OX2][CX4]`
**Description**: R-COO-R', acyl-oxygen-alkyl linkage.

---

## Atoms

| Index | Element | Role within group |
|---|---|---|
| 0 | C | sp² carbonyl carbon |
| 1 | O | carbonyl oxygen (=O) |
| 2 | O | ester oxygen (-O-) |
| 3 | C | sp³ alkyl carbon (O-bonded) |

---

## Allowed Roles

| Role | Allowed? | Condition |
|---|---|---|
| reactive_electrophile | yes | C is electrophilic (less than acid chloride, more than amide) |
| reactive_nucleophile | yes | enolate at α-C; ester O lone pair (weak) |
| reactive_radical | rare | — |
| leaving_group | yes | -OR' leaves during nucleophilic acyl substitution |
| spectator | yes (default in many cases) | |

---

## Key Descriptors

- **Carbonyl electrophilicity**: moderate (less than aldehyde/ketone in some senses; -OR is slightly EDG)
- **α-C acidity**: pKa ~25, accessible to strong bases (LDA, NaH)
- **Steric environment**: bulky esters (e.g., tert-butyl) resist hydrolysis
- **Activated esters** (e.g., NHS ester, pentafluorophenyl ester): more electrophilic, designed to leave quickly

---

## Example Reactions

| Reaction | Role | Reasoning |
|---|---|---|
| Saponification (ester + OH⁻ → acid + alcohol) | reactive_electrophile + leaving_group | OH⁻ attacks C, -OR leaves |
| Transesterification | reactive_electrophile + leaving_group | new alcohol attacks, old -OR leaves |
| Claisen condensation | reactive_electrophile (one ester) + reactive_nucleophile (α-C of other ester) | classic enolate chemistry |
| Reduction (LiAlH4) | reactive_electrophile | hydride attacks C |
| Grignard addition | reactive_electrophile | adds twice → tertiary alcohol |

---

## Negotiation Notes

- **Pairs well with**: nucleophiles (amines, alcohols, hydroxide, hydride, organometallics), bases (for enolate formation)
- **Conflicts with**: carbonyl, ether, alcohol, acid (all have C=O and/or C-O). Ester SMARTS is specific enough to win over generic patterns.
- **Resolution rules**:
  - Strong base + α-H present → α-C becomes nucleophile (enolate)
  - Nucleophile attacking C → electrophile + leaving group roles
  - Otherwise → spectator

---

## Edge Cases

- **Cyclic ester (lactone)**: same chemistry, but ring strain matters (β-lactone vs δ-lactone)
- **Vinyl ester**: special, hydrolyzes to aldehyde; out of project scope
- **Carbonate** (R-O-CO-O-R'): two ester linkages on same C; not matched by this SMARTS
- **Thioester** (R-CO-S-R'): different chemistry (more electrophilic); separate group

---

## Implementation Notes

- Priority: higher than carbonyl, ether (claims atoms first)
- Priority: lower than carboxylic acid (acid has -OH, ester has -OR; non-overlapping by H requirement)
- Detect α-H presence to enable enolate role
