# Alcohol Agent

## Identity

**Name**: alcohol
**SMARTS**: `[CX4][OX2H]`
**Description**: sp³ C-OH (excludes phenol, which is aromatic-OH, handled separately if needed).

---

## Atoms

| Index | Element | Role within group |
|---|---|---|
| 0 | C | sp³ carbon bonded to O |
| 1 | O | hydroxyl oxygen |
| 2 | H | hydroxyl hydrogen |

---

## Allowed Roles

| Role | Allowed? | Condition |
|---|---|---|
| reactive_electrophile | yes | when -OH is protonated (-OH2⁺), C becomes electrophilic (SN1/SN2 with H+) |
| reactive_nucleophile | yes | O lone pair attacks electrophile (most common case) |
| reactive_radical | rare | mostly via H-abstraction from C-H or O-H |
| leaving_group | yes | as water (after protonation) |
| spectator | yes (default) | when not involved |

---

## Key Descriptors

- **Substitution pattern of C**: 1°, 2°, 3° (affects SN1 vs SN2 propensity)
- **Acidic conditions present?**: protonation enables OH as leaving group
- **Steric environment**: bulky 3° OH harder to access
- **H-bond donor/acceptor**: in protic solvents the OH is partially solvated
- **pKa context**: alkoxide (deprotonated alcohol) is a stronger nucleophile

---

## Example Reactions

| Reaction | Role | Reasoning |
|---|---|---|
| Williamson ether synthesis (RO⁻ + R'X) | reactive_nucleophile | O attacks electrophilic C |
| Acid-catalyzed dehydration | leaving_group | -OH → -OH2⁺ → leaves as water |
| Fischer esterification | reactive_nucleophile | alcohol O attacks carbonyl C |
| Oxidation to ketone/aldehyde | spectator (within alcohol) | C-H is the reactive site |
| SN1 on tertiary alcohol with HBr | leaving_group | water leaves, Br⁻ enters |

---

## Negotiation Notes

- **Pairs well with**: electrophiles (carbonyls, alkyl halides), acid (for becoming leaving group)
- **Conflicts with**: amines (more nucleophilic), thiols (more nucleophilic). When competing, amine/thiol usually wins as nucleophile.
- **Resolution rules**:
  - Acidic context + 2°/3° C → likely leaving group
  - Basic context with electrophile present → nucleophile
  - Neutral with no clear partner → spectator

---

## Edge Cases

- **Phenol** (aromatic -OH): pKa ~10, much more acidic. Distinct chemistry. Treated separately (could be a `phenol.md` group or handled by aromatic + alcohol overlap).
- **Diols, polyols**: each -OH is a separate alcohol group; nearby -OHs affect each other's pKa
- **Hemiacetal / hemiketal**: -OH on C bearing -OR. Often spectator (unstable).
- **Hydrate of aldehyde** (gem-diol): out of scope for project

---

## Implementation Notes

- Priority: lower than carboxylic acid, ester, hemiacetal (those match first if -OH is part of them)
- Detect protonation state from input; if -OH2⁺ present, mark as activated leaving group
