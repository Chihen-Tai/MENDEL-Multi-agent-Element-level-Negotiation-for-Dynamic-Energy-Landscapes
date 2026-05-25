# Carbonyl Agent

Covers aldehyde and ketone (C=O bonded to C/H, not -OR, -NR2, -OH).

## Identity

**Name**: carbonyl
**SMARTS**: `[CX3]=[OX1]` with neighbors restricted to C or H (excludes acid, ester, amide)
- Aldehyde: `[CX3H1](=O)[#6]`
- Ketone: `[CX3](=O)([#6])[#6]`

**Description**: C=O where C is sp², bonded to carbon and/or hydrogen.

---

## Atoms

| Index | Element | Role within group |
|---|---|---|
| 0 | C | sp² carbonyl carbon (electrophilic) |
| 1 | O | carbonyl oxygen (nucleophilic via lone pair) |

α-carbons (neighbors of C) are part of local environment but separately classified.

---

## Allowed Roles

| Role | Allowed? | Condition |
|---|---|---|
| reactive_electrophile | yes | C is highly electrophilic — most common role |
| reactive_nucleophile | yes | O lone pair can act as nucleophile (weak; e.g., protonation) |
| reactive_radical | yes | radical addition to C=O (rare); α-H abstraction more common |
| leaving_group | no | not in itself; but reduction creates leaving capability |
| spectator | yes | when no nucleophile nearby |

Note: the α-carbon adjacent to carbonyl (acidic C-H, pKa ~20) often acts as nucleophile after deprotonation (enolate). This is handled by the methyl/methylene group spec, not the carbonyl group itself.

---

## Key Descriptors

- **Aldehyde vs ketone**: aldehydes more electrophilic (less steric, more polar)
- **Conjugation**: α,β-unsaturated → Michael acceptor (β-C also electrophilic)
- **EWG/EDG on C**: EWG amplifies electrophilicity
- **Steric environment**: bulky α-substituents → less accessible
- **Protonation state**: protonated C=OH⁺ is hyper-electrophilic
- **Solvent**: polar protic stabilizes the partial charges

---

## Example Reactions

| Reaction | Role | Reasoning |
|---|---|---|
| Nucleophilic addition (NaBH4, RMgX, RNH2) | reactive_electrophile | C is attacked |
| Aldol (as electrophile side) | reactive_electrophile | C attacked by enolate |
| Aldol (as enolate source) | spectator (within carbonyl); α-C becomes nucleophile | α-H is acidic |
| Michael addition to enone | reactive_electrophile at β-C | conjugated system |
| Norrish type II (photochemistry) | reactive_radical | out of project scope |
| Acetal formation | reactive_electrophile | nucleophilic addition by alcohol |

---

## Negotiation Notes

- **Pairs well with**: alcohol, amine, organometallics, hydride donors, enolates
- **Conflicts with**: ester, amide, acid (all contain C=O but their O-X bond changes electronics). These take priority in SMARTS matching.
- **Resolution rules**:
  - Default to electrophile when nucleophile present
  - Spectator when no nucleophile in system
  - α-C nucleophilicity handled by the α-C's own group (methyl/methylene), not carbonyl itself

---

## Edge Cases

- **α,β-Unsaturated carbonyl** (enone): the alkene is also reactive. Both groups may be flagged; β-C electrophilic by conjugation. Need to handle hand-off between alkene group and carbonyl group.
- **1,2- vs 1,4-addition**: ambiguous in enones; for project, accept either as correct if one of them is identified.
- **Carbonyl O acting as nucleophile** (rare, e.g., in cation stabilization): treat as edge case, default to spectator
- **Cyclic carbonyl** (cyclohexanone, etc.): same logic as acyclic
- **Aldehyde C-H**: the aldehyde H is relatively acidic and can be removed in some metal-catalyzed reactions (e.g., Tishchenko); out of project scope.

---

## Implementation Notes

- Priority: lower than carboxylic acid, ester, amide. They match their pattern first to exclude their C=O from being matched as plain carbonyl.
- Detect conjugation with adjacent alkene to enable Michael acceptor logic
