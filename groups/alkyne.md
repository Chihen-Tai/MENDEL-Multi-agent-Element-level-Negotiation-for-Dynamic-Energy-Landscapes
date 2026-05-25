# Alkyne Agent

## Identity

**Name**: alkyne
**SMARTS**: `[CX2]#[CX2]`
**Description**: C≡C triple bond, sp carbons.

---

## Atoms

| Index | Element | Role within group |
|---|---|---|
| 0 | C | sp carbon |
| 1 | C | sp carbon |

---

## Allowed Roles

| Role | Allowed? | Condition |
|---|---|---|
| reactive_electrophile | yes | conjugated to EWG; or as Michael acceptor analogue |
| reactive_nucleophile | yes | electrophilic addition; π donation to electrophile |
| reactive_radical | yes | radical addition |
| leaving_group | no | — |
| spectator | yes (default) | isolated, no reactive partner |

Note: terminal alkyne -C≡C-H also has acidic H (pKa ~25), so the H can be a leaving group (deprotonation by strong base), but this is typically handled as a separate transformation, not within the alkyne group spec.

---

## Key Descriptors

- **Terminal vs internal**: terminal alkynes have acidic C-H
- **Conjugation**: extended π → more reactive
- **Substituent EWG/EDG**: similar logic to alkenes but more pronounced
- **Hybridization-induced acidity**: sp C-H is much more acidic than sp³ or sp²

---

## Example Reactions

| Reaction | Role | Reasoning |
|---|---|---|
| HBr addition to alkyne | reactive_nucleophile | π donates |
| Sonogashira coupling (terminal alkyne + Ar-X) | reactive_nucleophile (after deprotonation) | acetylide attacks electrophile |
| Click chemistry (alkyne + azide) | reactive_electrophile (in CuAAC) | metal-mediated |
| Radical hydroboration | reactive_radical | — |
| Alkyne metathesis | reactive_nucleophile / electrophile pair | depends on context |

---

## Negotiation Notes

- **Pairs well with**: halides (HX addition), azides (click), metal catalysts
- **Conflicts with**: nearby alkenes (which alkene/alkyne is more reactive?). Alkyne > alkene for radical and electrophilic addition in most contexts.
- **Resolution rules**:
  - Terminal alkyne with strong base present → C-H acts as leaving group, C becomes nucleophilic
  - Conjugated to EWG → electrophilic at β-C

---

## Edge Cases

- **Cumulenes** (C=C=C=C): out of scope
- **Aromatic-fused alkynes** (e.g., benzyne): out of scope, would need separate treatment
- **Metal acetylides**: not handled (organometallic out of scope)

---

## Implementation Notes

- Priority: same level as alkene
- If terminal alkyne, generate two sub-features: π-system and acidic C-H
