# Amide Agent

## Identity

**Name**: amide
**SMARTS**: `[CX3](=O)[NX3]`
**Description**: R-CO-NR'R'', acyl-N linkage. Includes 1°, 2°, 3° amides.

---

## Atoms

| Index | Element | Role within group |
|---|---|---|
| 0 | C | sp² carbonyl carbon |
| 1 | O | carbonyl oxygen |
| 2 | N | amide nitrogen (lone pair partly delocalized) |

---

## Allowed Roles

| Role | Allowed? | Condition |
|---|---|---|
| reactive_electrophile | yes | C is electrophilic (least reactive among acyl groups) |
| reactive_nucleophile | yes | α-C can be deprotonated (similar to ester but less acidic); N lone pair is mostly delocalized |
| reactive_radical | rare | — |
| leaving_group | yes (rare) | -NR2 leaves only under harsh conditions |
| spectator | yes (default in many cases — amides are inert) | |

---

## Key Descriptors

- **Resonance delocalization**: N lone pair into C=O makes amide planar, less basic on N
- **Restricted rotation**: C-N has partial double bond character
- **Hydrolysis**: amide hydrolysis is slow without strong acid/base catalysis
- **Substitution**: 1° (RCONH2), 2° (RCONHR), 3° (RCONR2)
- **α-H acidity**: pKa ~25-30, less than ester

---

## Example Reactions

| Reaction | Role | Reasoning |
|---|---|---|
| Amide hydrolysis (RCONH2 + H2O/acid or base) | reactive_electrophile + leaving_group | water/OH⁻ attacks C, -NR2 leaves |
| Hofmann rearrangement (RCONH2 + Br2/OH⁻) | reactive_nucleophile (N) then rearrangement | out of scope for project |
| Reduction (LiAlH4) → amine | reactive_electrophile | hydride attacks |
| Peptide bond chemistry (biological) | varies | out of project scope |
| Bischler-Napieralski cyclization | reactive_electrophile | activated by POCl3 |

---

## Negotiation Notes

- **Pairs well with**: strong nucleophiles (only), water (slow hydrolysis), reducing agents
- **Conflicts with**: carboxylic acid, ester (similar acyl structure but different leaving group). Amide is the most inert of the three.
- **Resolution rules**:
  - Default to spectator unless strong activator present
  - Strong nucleophile + amide → electrophile + leaving group
  - Most reactions involving amide → it's the spectator

---

## Edge Cases

- **Lactam** (cyclic amide): same chemistry, but ring strain matters (β-lactam = penicillin: highly reactive)
- **Urea** (NH2-CO-NH2): two N attached to same C; out of scope
- **Carbamate** (R-O-CO-NR'2): hybrid of ester and amide; out of scope
- **Sulfonamide** (R-SO2-NR'2): different group entirely; not matched

---

## Implementation Notes

- Priority: higher than carbonyl, amine (claims its C, O, N first)
- Priority: lower than carboxylic acid, ester (those have different X on the C)
- Default behavior: spectator. Only flag as reactive if strong evidence in context.
