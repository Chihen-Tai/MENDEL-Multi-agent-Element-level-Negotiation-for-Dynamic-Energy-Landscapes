# Aromatic Agent

## Identity

**Name**: aromatic
**SMARTS**: `c1ccccc1` (benzene); extends to fused/heteroaromatic via additional patterns
**Description**: aromatic ring (Hückel 4n+2 π system).

---

## Atoms

All ring atoms. For benzene: 6 sp² C with delocalized π.

For heteroaromatics (pyridine, furan, thiophene, pyrrole, etc.), include all ring atoms.

---

## Allowed Roles

| Role | Allowed? | Condition |
|---|---|---|
| reactive_electrophile | yes | nucleophilic aromatic substitution (rare, requires strong EWG); or attacked by nucleophile in SNAr |
| reactive_nucleophile | yes | electrophilic aromatic substitution (EAS) — common case |
| reactive_radical | yes | radical aromatic substitution; aryl radicals in coupling |
| leaving_group | no (normally) | exception: aryl halide where halide is the leaving group, but that's the halide's role |
| spectator | yes (default) | most reactions where ring is decoration |

---

## Key Descriptors

- **Substituent EWG/EDG**:
  - EDG (-OH, -NH2, -OR, -alkyl) → activated toward EAS, ortho/para directing
  - EWG (-NO2, -COR, -CN, -CF3) → deactivated, meta directing; activated toward SNAr
- **Heteroatoms in ring**: pyridine N is electrophilic at α-positions
- **Fused rings**: naphthalene > benzene reactivity
- **Charge**: protonated heteroaromatic (e.g., pyridinium) is more electrophilic

---

## Example Reactions

| Reaction | Role | Reasoning |
|---|---|---|
| Nitration of benzene | reactive_nucleophile | aromatic π attacks NO2⁺ |
| Friedel-Crafts alkylation | reactive_nucleophile | π attacks carbocation |
| SNAr on 2,4-dinitrochlorobenzene | reactive_electrophile | ring is electron-poor, attacked by nucleophile |
| Radical aryl coupling | reactive_radical | — |
| Most reactions involving benzyl/phenyl groups | spectator | ring is just a substituent |

---

## Negotiation Notes

- **Pairs well with**: electrophiles (in EAS), nucleophiles (in SNAr when activated)
- **Conflicts with**: alkenes — aromatic ring is much less reactive in most contexts
- **Resolution rules**:
  - Default to spectator unless strong evidence (e.g., NO2⁺ partner suggesting nitration)
  - If ring has 2+ strong EWGs and a nucleophile is present → consider SNAr (electrophile role)
  - Heteroaromatic α-positions to N → likely electrophilic

---

## Edge Cases

- **Pyridine N**: lone pair can act as nucleophile (basicity) — should this be a separate group? For project scope: treat pyridine N as part of aromatic group, role assigned to ring.
- **Phenol -OH**: the OH gets its own alcohol group spec; the ring is separate
- **Anilines -NH2**: amine gets its own group; ring is separate but highly activated
- **Indole, pyrrole**: nucleophilic at C-3 (indole), C-2 (pyrrole)
- **Naphthalene, anthracene**: handled with extended SMARTS

---

## Implementation Notes

- Highest priority among SMARTS patterns (match first, exclude its atoms from subsequent matches)
- Heteroaromatics need separate SMARTS patterns (pyridine, furan, thiophene, pyrrole, imidazole, ...)
- For project scope, start with benzene + pyridine + furan + thiophene + pyrrole
