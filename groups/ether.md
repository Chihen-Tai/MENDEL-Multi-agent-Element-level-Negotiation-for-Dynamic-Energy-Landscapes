# Ether Agent

## Identity

**Name**: ether
**SMARTS**: `[CX4][OX2][CX4]`
**Description**: R-O-R, two sp³ C bridged by O.

---

## Atoms

| Index | Element | Role within group |
|---|---|---|
| 0 | C | sp³ carbon |
| 1 | O | ether oxygen |
| 2 | C | sp³ carbon |

---

## Allowed Roles

| Role | Allowed? | Condition |
|---|---|---|
| reactive_electrophile | yes | when protonated and C-O cleavage occurs (rare, strong acid) |
| reactive_nucleophile | yes | O lone pair acting as weak nucleophile (e.g., solvent coordinating to metal) |
| reactive_radical | rare | α-C-H is somewhat activated for H-abstraction |
| leaving_group | yes | as R-OH after protonation (rare, needs strong acid) |
| spectator | yes (default, most common) | ethers are usually inert solvents |

---

## Key Descriptors

- **Strain**: epoxides (3-membered ring ether) are highly reactive — treated separately
- **Protonation state**: ether O can be protonated by strong acid
- **Electronic environment**: glycol ethers vs simple alkyl ethers
- **Steric bulk**: tert-butyl ethers more resistant to cleavage

---

## Example Reactions

| Reaction | Role | Reasoning |
|---|---|---|
| Most reactions with ether as solvent (Et2O, THF) | spectator | inert |
| HI cleavage of methyl ether (Zeisel) | leaving_group + electrophile | protonation then SN2 by I⁻ |
| Epoxide ring-opening | reactive_electrophile | strain drives reactivity (treat as separate group) |
| Crown ether complexing K⁺ | reactive_nucleophile (weak) | O coordinates |

---

## Negotiation Notes

- **Pairs well with**: rarely a primary reactant. Mostly spectator.
- **Conflicts with**: ester (which contains C-O); aromatic ring (anisole = aryl methyl ether has special chemistry)
- **Resolution rules**:
  - Default to spectator in 95% of cases
  - Strong acid + no better partner → potentially leaving group
  - Epoxide → separate handling, much more reactive

---

## Edge Cases

- **Epoxide** (`C1OC1`): much more reactive than acyclic ethers; should be a separate group
- **Aryl alkyl ether** (anisole): the aryl part is more reactive (EAS activated); the O is largely spectator
- **Acetal** (R2C(OR)2): treated separately if added later
- **Vinyl ether** (CH2=CH-OR): special enol-ether chemistry; out of project scope

---

## Implementation Notes

- Priority: lower than ester, acetal, epoxide
- For project: mostly serves as spectator; useful for not misidentifying solvent atoms as reactive
