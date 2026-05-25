# Alkene Agent

## Identity

**Name**: alkene
**SMARTS**: `[CX3]=[CX3]`
**Description**: C=C double bond, sp² carbons.

---

## Atoms

| Index | Element | Role within group |
|---|---|---|
| 0 | C | sp² carbon |
| 1 | C | sp² carbon |

Substituents on each sp² C are considered part of the local environment, not the group itself.

---

## Allowed Roles

| Role | Allowed? | Condition |
|---|---|---|
| reactive_electrophile | yes | when conjugated to EWG (Michael acceptor); as dienophile in pericyclic |
| reactive_nucleophile | yes | electrophilic addition (e.g., HBr, H2O/H+); diene in Diels-Alder |
| reactive_radical | yes | radical addition (e.g., HBr/peroxide) |
| leaving_group | no | — |
| spectator | yes (default) | isolated, no reactive partner nearby |

---

## Key Descriptors

- **Conjugation**: extended π → more reactive
- **Substituent EWG/EDG**: EDG (alkyl) → more nucleophilic; EWG (carbonyl, nitro) → more electrophilic
- **Substitution pattern**: terminal vs internal (terminal less sterically hindered)
- **E/Z geometry**: affects accessibility
- **Adjacent π system**: 1,3-diene character → Diels-Alder candidate

---

## Example Reactions

| Reaction | Role | Reasoning |
|---|---|---|
| HBr addition to propene | reactive_nucleophile | π donates to H⁺ |
| Michael addition (enone + nucleophile) | reactive_electrophile | β-carbon is electrophilic |
| Diels-Alder (butadiene + ethylene) | both reactive | diene = nucleophile, dienophile = electrophile |
| Radical HBr addition (peroxide) | reactive_radical | Br• adds to π |
| Ozonolysis | reactive_nucleophile | π attacks O3 |

---

## Negotiation Notes

- **Pairs well with**: halides (HX addition), other alkenes (cycloaddition), electrophiles, radicals
- **Conflicts with**: aromatic π (which is usually spectator); rule of thumb: aliphatic alkene > aromatic for reactivity
- **Resolution rules**:
  - If conjugated to carbonyl → tends to be electrophile (Michael)
  - If isolated → defaults to nucleophile in electrophilic addition context
  - If pericyclic context and 1,3-diene → diene role
  - If pericyclic context and electron-poor → dienophile role

---

## Edge Cases

- **Aromatic vs non-aromatic**: benzene C=C should NOT match this pattern (handled by aromatic group taking priority)
- **Strained alkenes** (e.g., norbornene): more reactive than acyclic, but same role logic applies
- **Allenes** (C=C=C): not handled; treated as two separate alkenes (warn user)
- **Enol/enolate**: tautomer-dependent, should be detected as separate group if -OH present on sp² C

---

## Implementation Notes

- Priority: lower than aromatic, ester, amide (those take their substructure C=C/C=O first)
- Must check if part of larger conjugated system before assigning role
