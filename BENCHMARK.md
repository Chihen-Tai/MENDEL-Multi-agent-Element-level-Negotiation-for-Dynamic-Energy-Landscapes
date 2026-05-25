# MENDEL Benchmark Reactions

Five reactions covering ionic, radical, and pericyclic mechanisms.

---

## Reaction 1: SN2 — Methyl bromide + hydroxide

**Reaction**
```
CH3Br + OH⁻ → CH3OH + Br⁻
```

**Context**: ionic

**Expected role assignment**

| Group | Atoms | Role |
|---|---|---|
| methyl | C, 3H | reactive_electrophile |
| halide | Br | leaving_group |
| alcohol (from OH⁻) | O, H | reactive_nucleophile |

**Reaction center**: C, O, Br

**Success criterion**: all three roles correctly assigned.

---

## Reaction 2: E2 — Ethyl bromide elimination

**Reaction**
```
CH3CH2Br + OH⁻ → CH2=CH2 + H2O + Br⁻
```

**Context**: ionic

**Expected role assignment**

| Group | Atoms | Role |
|---|---|---|
| methylene (α-C) | α-C, 2H | reactive_electrophile |
| methyl (β-C) | β-C, β-H (one) | leaving_group (the β-H) |
| halide | Br | leaving_group |
| alcohol (from OH⁻) | O, H | reactive_nucleophile (as base) |

**Reaction center**: α-C, β-C, β-H, Br, O

**Success criterion**: nucleophile and both leaving groups identified.

**Note**: distinguishing E2 from SN2 in same substrate is a hard case. For this benchmark we provide explicit context = "elimination".

---

## Reaction 3: Diels-Alder — Butadiene + ethylene

**Reaction**
```
CH2=CH–CH=CH2 + CH2=CH2 → cyclohexene
```

**Context**: pericyclic

**Expected role assignment**

| Group | Atoms | Role |
|---|---|---|
| alkene (diene, terminal) | C1=C2 | reactive_nucleophile |
| alkene (diene, internal) | C3=C4 | reactive_nucleophile |
| alkene (dienophile) | C5=C6 | reactive_electrophile |

**Reaction center**: C1, C2, C3, C4, C5, C6 (all six)

**Success criterion**: all three alkenes labeled reactive; diene vs dienophile distinction is bonus.

**Note**: in pericyclic context, nucleophile/electrophile distinction is less sharp; both diene and dienophile are reactive π systems.

---

## Reaction 4: Aldol — Two acetone molecules

**Reaction**
```
2 (CH3)2C=O → (CH3)2C(OH)-CH2-C(=O)-CH3
```

**Context**: ionic (base-catalyzed)

**Expected role assignment**

| Group | Atoms | Role |
|---|---|---|
| carbonyl (enolate side) | C=O | spectator |
| alpha_carbon (enolate side) | α-C, α-H | reactive_nucleophile (after deprotonation) |
| carbonyl (electrophile side) | C=O | reactive_electrophile |
| alpha_carbon (other) | α-C, α-H | spectator |

**Reaction center**: enolate α-C, electrophile carbonyl C, electrophile carbonyl O

**Success criterion**: correct identification of one alpha_carbon as nucleophile and one carbonyl as electrophile.

**Note**: α-C is a separate functional group (see `groups/alpha_carbon.md`); it's a contextual group identified when sp³ C-H is adjacent to an activating group like carbonyl.

**Note**: aldol involves regioselectivity — which α-C deprotonates, which C=O is attacked. Ground truth: kinetic product.

---

## Reaction 5: Radical bromination — Methane + Br2

**Reaction (propagation step)**
```
CH4 + Br• → CH3• + HBr
CH3• + Br2 → CH3Br + Br•
```

**Context**: radical

**Expected role assignment (for propagation step 1)**

| Group | Atoms | Role |
|---|---|---|
| methyl | C, 4H | reactive_radical (one H is abstracted) |
| (radical Br•) | Br | reactive_radical |

**Reaction center**: C, one H, Br

**Success criterion**: methyl C-H identified as radical site; Br• as radical partner.

**Note**: model is given the propagation step, not the initiation. Initial Br• comes from homolysis of Br2 — out of scope.

---

## Evaluation Summary

| Reaction | Difficulty | Key challenge |
|---|---|---|
| SN2 | easy | distinguishing nucleophile / electrophile / leaving group |
| E2 | medium | distinguishing E2 from SN2 (same substrate) |
| Diels-Alder | medium | pericyclic context, multiple reactive alkenes |
| Aldol | hard | regioselectivity in symmetric reactants |
| Radical bromination | medium | radical role, identifying which H is abstracted |

**Overall target**: ≥80% role accuracy averaged across all five reactions.

---

## Future Benchmarks (post-project)

- Friedel-Crafts alkylation
- Wittig reaction
- Grignard addition
- Esterification (Fischer)
- Markovnikov / anti-Markovnikov addition
- Cope rearrangement
- Claisen condensation
