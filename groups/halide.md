# Halide Agent

## Identity

**Name**: halide (alkyl halide)
**SMARTS**: `[CX4][F,Cl,Br,I]`
**Description**: sp³ C-X bond, X = F, Cl, Br, I.

---

## Atoms

| Index | Element | Role within group |
|---|---|---|
| 0 | C | sp³ carbon (electrophilic) |
| 1 | X | halogen (leaving group) |

---

## Allowed Roles

| Role | Allowed? | Condition |
|---|---|---|
| reactive_electrophile | yes | C is electrophilic — typical SN role |
| reactive_nucleophile | no | halide as leaving group, not nucleophile (unless free X⁻ ion, separate species) |
| reactive_radical | yes | radical chain (homolysis of C-X or X-X) |
| leaving_group | yes | X leaves as X⁻ — most common role for halide itself |
| spectator | yes (default if no nucleophile) | |

Note: when the halide is given as a free ion (e.g., Br⁻ in CH3Br + Br⁻ → CH3Br + Br⁻), the free ion acts as nucleophile. But for the C-X group in the substrate, the role of the halogen is leaving group; the C is electrophile.

---

## Key Descriptors

- **Halogen identity**: leaving group ability F << Cl < Br < I
- **C hybridization and substitution**: 1°, 2°, 3° — affects SN1 vs SN2 propensity
  - 1° → SN2 preferred
  - 3° → SN1 preferred
  - 2° → both possible, context-dependent
- **Allyl/benzyl C-X**: more reactive (resonance stabilization of cation or radical)
- **C-F bond**: very strong, F is poor leaving group (rarely reactive in this role)
- **Vinyl/aryl halide**: NOT matched by this SMARTS (different chemistry); separate group needed if added

---

## Example Reactions

| Reaction | Role | Reasoning |
|---|---|---|
| SN2 (CH3Br + OH⁻) | C = electrophile; Br = leaving group | OH⁻ attacks C, Br leaves |
| SN1 (t-BuBr + H2O) | C = electrophile; Br = leaving group | Br leaves first, water attacks cation |
| E2 (RCH2CH2Br + base) | C = electrophile (formally); Br = leaving group; β-H = leaving group | concerted |
| Wurtz coupling (RX + Na) | C = electrophile + X = leaving group | reduces to R⁻, dimerizes |
| Radical halogenation (R-H + X2) | radical on C-H and X-X | initiation/propagation |
| Grignard formation (RX + Mg) | C accepts electrons; X = leaving group | inverts polarity of C |

---

## Negotiation Notes

- **Pairs well with**: nucleophiles (amines, alcohols, hydroxide, cyanide, alkoxide), bases (for E2), metals (Mg, Li for Grignard/lithiation)
- **Conflicts with**: when multiple halides present (which leaves first?). Answer: weaker C-X bond → leaves first (I > Br > Cl > F).
- **Resolution rules**:
  - Nucleophile present → C is electrophile, X is leaving group
  - Base present + β-H available → could be E2 (X still leaves)
  - Radical initiator → radical role
  - No reactive partner → spectator

---

## Edge Cases

- **Aryl halide** (Ar-X): different chemistry (no SN2, only SNAr if activated, or via cross-coupling); not matched by this SMARTS
- **Vinyl halide** (R-CH=CH-X): generally unreactive under SN; out of scope
- **Acid chloride** (R-CO-Cl): not matched; should be a separate group due to very high reactivity
- **Geminal dihalide** (CH2X2): each X is a separate halide group
- **CF3, CCl3**: highly substituted; very unreactive at C, but F/Cl might still play role in special chemistry

---

## Implementation Notes

- Priority: above ether (independent of any C-O patterns); below acid chloride (if added)
- Detect halogen identity for prioritization in resolution rules
- Detect substitution at C (1°/2°/3°) for SN1/SN2 prediction
