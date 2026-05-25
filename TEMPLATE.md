# [Group Name] Agent

Template for defining a new functional group in MENDEL. Copy this file to `groups/<name>.md` and fill in.

---

## Identity

**Name**: [e.g., alkene]

**SMARTS**: [e.g., `[CX3]=[CX3]`]

**Description**: [one-line description]

---

## Atoms

Which atoms belong to this group. Use SMARTS atom indices.

| Index | Element | Role within group |
|---|---|---|
| 0 | C | sp² carbon |
| 1 | C | sp² carbon |

---

## Allowed Roles

Tick which roles this group can take, and under what condition.

| Role | Allowed? | Condition |
|---|---|---|
| reactive_electrophile | yes / no | (when applicable) |
| reactive_nucleophile | yes / no | (when applicable) |
| reactive_radical | yes / no | (when applicable) |
| leaving_group | yes / no | (when applicable) |
| spectator | yes (default) | otherwise |

---

## Key Descriptors

Features that strongly influence role prediction for this group.

- [Descriptor 1: e.g., neighboring EWG → more electrophilic]
- [Descriptor 2: e.g., conjugation extent]
- [Descriptor 3: e.g., steric hindrance]

---

## Example Reactions

Cases where this group appears, and what role it takes.

| Reaction | Role | Reasoning |
|---|---|---|
| [reaction name] | [role] | [why] |

---

## Negotiation Notes

How this group interacts with other groups during negotiation:

- **Pairs well with**: [list of partner roles/groups]
- **Conflicts with**: [list of groups that may compete for same role]
- **Resolution rules**: [how to break ties]

---

## Edge Cases

- [Edge case 1]
- [Edge case 2]

---

## Implementation Notes

- SMARTS pattern priority: [where this group sits in conflict resolution]
- Special handling: [any group-specific logic]
