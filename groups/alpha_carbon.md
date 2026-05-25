# Alpha Carbon Agent

## Identity

**Name**: alpha_carbon
**SMARTS** (multiple patterns, all matched):
- α to carbonyl: `[CX4;H1,H2,H3][CX3]=[OX1]`
- α to ester: `[CX4;H1,H2,H3][CX3](=O)[OX2]`
- α to amide: `[CX4;H1,H2,H3][CX3](=O)[NX3]`
- α to nitrile: `[CX4;H1,H2,H3][CX2]#[NX1]`
- α to nitro: `[CX4;H1,H2,H3][NX3](=O)=O`
- α to sulfone: `[CX4;H1,H2,H3][SX4](=O)=O`

**Description**: sp³ C-H adjacent to an electron-withdrawing group, making the C-H acidic and the carbanion stabilized by resonance.

This is a **contextual group** — the same carbon is α-C or not depending on what's next to it.

---

## Atoms

The α-carbon itself (one atom) plus its acidic H(s). The activating group (carbonyl, nitrile, etc.) is NOT part of this group — it has its own group spec.

| Index | Element | Role within group |
|---|---|---|
| 0 | C | sp³ α-carbon |
| 1+ | H | acidic H (1, 2, or 3 depending on substitution) |

---

## Allowed Roles

| Role | Allowed? | Condition |
|---|---|---|
| reactive_electrophile | rare | only in unusual radical/oxidation contexts |
| reactive_nucleophile | yes | after deprotonation, the carbanion (enolate, nitronate, etc.) is the nucleophile |
| reactive_radical | yes | α-H abstraction in radical reactions (e.g., bromination α to carbonyl) |
| leaving_group | yes | the α-H itself leaves as H⁺ (deprotonation step) |
| spectator | yes (default if no base) | |

Note: α-C is the carbon; the H is what leaves. For role assignment, treat the whole α-C+H unit as one agent, and "leaving_group" means the H leaves while α-C becomes the nucleophile center.

---

## Key Descriptors

- **Activating group identity** (sets pKa):
  - α to nitro (-NO2): pKa ~10, very acidic
  - α to two carbonyls (1,3-dicarbonyl): pKa ~5-13, very acidic
  - α to single carbonyl (ketone/aldehyde): pKa ~20
  - α to ester: pKa ~25
  - α to amide: pKa ~25-30
  - α to nitrile: pKa ~25
  - α to sulfone: pKa ~25
- **Number of α-H**: more H → more accessible, but enolate at different C
- **Conjugation**: doubly activated (e.g., 1,3-diketone) is much more acidic
- **Base strength in context**: weak base (NaOH) only deprotonates pKa < ~15; strong base (LDA, NaH) handles up to ~25-30
- **Solvent**: protic/aprotic affects pKa

---

## Example Reactions

| Reaction | Role | Reasoning |
|---|---|---|
| Aldol (one ketone enolizes, attacks another) | reactive_nucleophile (the enolate α-C) | α-H removed by base, carbanion attacks carbonyl C |
| Claisen condensation (ester self-condensation) | reactive_nucleophile | α-C enolate attacks another ester |
| Michael addition (enolate + enone) | reactive_nucleophile | 1,4-addition to β-C of enone |
| α-Halogenation (ketone + Br2) | reactive_nucleophile (enol form) | enol attacks Br2 |
| Mannich reaction (enol + iminium) | reactive_nucleophile | α-C attacks iminium C |
| Alkylation (enolate + R-X) | reactive_nucleophile | C-C bond formation |
| HVZ reaction (acid + Br2/PBr3) | reactive_nucleophile (enol of acid bromide) | α-bromination of carboxylic acid |

---

## Negotiation Notes

- **Pairs well with**: carbonyls (other), alkyl halides (alkylation), Michael acceptors, iminium ions
- **Conflicts with**: when multiple α-C positions exist (regioselectivity question)
  - Kinetic enolate (less substituted, formed with bulky strong base like LDA)
  - Thermodynamic enolate (more substituted, formed with weaker base + equilibration)
  - For project scope, assume kinetic product unless context says otherwise
- **Resolution rules**:
  - Base present + electrophile present + α-H → α-C is nucleophile
  - Multiple α-C candidates → pick the one with lower pKa (more activated) or smaller substitution (kinetic)
  - No base or no electrophile → spectator

---

## Edge Cases

- **Doubly activated α-C** (e.g., between two carbonyls in malonate, acetoacetate): pKa ~5-13, dominates over singly activated α-C
- **α to extended conjugation**: e.g., γ-position in α,β-unsaturated carbonyl can also be deprotonated (vinylogous enolate); out of project scope
- **No α-H** (e.g., benzaldehyde, pivaldehyde): no α-C role possible; group not matched
- **Quaternary α-C**: has no H, cannot be deprotonated; not matched by SMARTS (H1/H2/H3 requirement)
- **Cyclohexanone**: α-positions are 2,6 (both equivalent by symmetry)
- **Asymmetric ketone** (e.g., 2-butanone): two non-equivalent α-positions (methyl vs methylene); regioselectivity matters

---

## Implementation Notes

- **Priority**: higher than methyl/methylene (so the α-C is not just labeled as a generic methyl)
- **Overlap with methyl/methylene**: if a [CH3] matches α-carbon AND methyl, it should be labeled alpha_carbon (override)
- **The activating group is a separate group**: carbonyl, ester, nitrile etc. all have their own spec; α-C interacts with them during negotiation
- **For aldol-like reactions**: model needs to identify TWO compatible groups (one α-C as nucleophile, one carbonyl as electrophile) and pair them
- **Detection workflow**:
  1. First identify activating groups (carbonyl, ester, amide, nitrile, nitro, sulfone)
  2. For each, look at adjacent sp³ C with H
  3. Tag those C as alpha_carbon
  4. Remove from methyl/methylene match list
