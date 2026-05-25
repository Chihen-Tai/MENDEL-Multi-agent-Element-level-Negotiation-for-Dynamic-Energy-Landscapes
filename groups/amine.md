# Amine Agent

Covers primary, secondary, and tertiary aliphatic amines.

## Identity

**Name**: amine
**SMARTS**:
- Primary: `[NX3H2][CX4]`
- Secondary: `[NX3H1]([CX4])[CX4]`
- Tertiary: `[NX3]([CX4])([CX4])[CX4]`

**Description**: sp³ N bonded to 1-3 alkyl groups.

---

## Atoms

For primary: N, 2H, and the C-bonded.
For secondary: N, 1H, and two C-bonded.
For tertiary: N and three C-bonded.

---

## Allowed Roles

| Role | Allowed? | Condition |
|---|---|---|
| reactive_electrophile | rare | only after acylation (becomes amide carbonyl, but then it's amide group) |
| reactive_nucleophile | yes | N lone pair attacks electrophile — most common |
| reactive_radical | rare | aminyl radical chemistry; out of project scope |
| leaving_group | yes (rare) | -NR2 can leave as amine in some retro-reactions; usually after protonation |
| spectator | yes (default if no electrophile) | |

---

## Key Descriptors

- **Basicity (pKa ~9-11)**: protonated to NR3H⁺ in acidic conditions, losing nucleophilicity
- **Substitution (1°, 2°, 3°)**: affects nucleophilicity and steric accessibility
  - 1° most accessible
  - 3° least sterically hindered for proton, but most for C-attack
- **EWG/EDG**: aniline (Ar-NH2) is less basic than alkylamine (lone pair delocalized into ring)
- **Solvent**: protic vs aprotic changes effective basicity

---

## Example Reactions

| Reaction | Role | Reasoning |
|---|---|---|
| Amide formation (RCOOH + R'NH2) | reactive_nucleophile | N attacks carbonyl C |
| SN2 (RNH2 + R'X) | reactive_nucleophile | N attacks alkyl halide |
| Imine formation (R2NH + R'CHO) | reactive_nucleophile | N attacks aldehyde C |
| Hofmann elimination (R4N⁺ + heat/base) | leaving_group (after quaternization) | -NR3 leaves as amine |
| Acid-base reaction (RNH2 + HX) | reactive_nucleophile (proton acceptor) | basic role |

---

## Negotiation Notes

- **Pairs well with**: carbonyl/ester/acid (acylation), alkyl halides (alkylation), aldehydes (imine), acids (protonation)
- **Conflicts with**: alcohol — both are nucleophiles. Amine usually wins (more nucleophilic).
- **Resolution rules**:
  - Default nucleophile in presence of electrophile
  - In acidic environment with no electrophile → spectator (protonated)
  - As Hofmann substrate (quaternary ammonium + base + heat) → leaving group

---

## Edge Cases

- **Aniline** (Ar-NH2): less nucleophilic than alkylamine; ring is activated (separate group)
- **Quaternary ammonium** (R4N⁺): not in this SMARTS (no H or different valence); becomes leaving group precursor
- **Hydrazine** (NH2-NH2): two N, special; out of project scope
- **Hydroxylamine** (NH2OH): out of scope
- **α-Amino acids**: zwitterion in water; user-specified protonation state
- **Pyridine/pyrrole**: aromatic N, handled by aromatic group

---

## Implementation Notes

- Priority: above ether (since both have lone pair on heteroatom but amine more nucleophilic)
- Three sub-patterns (1°/2°/3°); use highest-specificity match
- Detect aniline by checking N attached to aromatic C → different role probabilities
