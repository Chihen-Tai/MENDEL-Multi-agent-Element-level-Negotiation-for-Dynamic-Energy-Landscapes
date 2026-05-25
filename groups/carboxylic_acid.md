# Carboxylic Acid Agent

## Identity

**Name**: carboxylic_acid
**SMARTS**: `[CX3](=O)[OX2H]`
**Description**: -COOH, contains C=O and O-H in one functional group.

---

## Atoms

| Index | Element | Role within group |
|---|---|---|
| 0 | C | sp² carbonyl carbon |
| 1 | O | carbonyl oxygen (=O) |
| 2 | O | hydroxyl oxygen (-OH) |
| 3 | H | acidic hydrogen |

---

## Allowed Roles

| Role | Allowed? | Condition |
|---|---|---|
| reactive_electrophile | yes | C is electrophilic (especially when activated, e.g., -COCl from -COOH) |
| reactive_nucleophile | yes | carboxylate (deprotonated) O attacks electrophile |
| reactive_radical | rare | decarboxylation in some radical contexts |
| leaving_group | yes | as -OH/water during esterification; or as CO2 in decarboxylation |
| spectator | yes | when not reacting |

---

## Key Descriptors

- **pKa ~4-5**: easily deprotonated to carboxylate
- **Carboxylate is delocalized**: both O equivalent in resonance
- **Activation**: -COOH → -COCl, -CO-O-CO- (anhydride), -COR' (activated ester) all more electrophilic
- **H-bonding**: dimerizes in non-polar solvents
- **Substituent effect**: EWG α-substituents (e.g., -CF3) → lower pKa

---

## Example Reactions

| Reaction | Role | Reasoning |
|---|---|---|
| Fischer esterification (RCOOH + R'OH) | reactive_electrophile (C) + leaving_group (-OH) | C attacked by R'OH, then -OH leaves as water |
| Amide formation (RCOOH + R'NH2) | reactive_electrophile + leaving_group | similar, -OH leaves |
| Saponification (reverse esterification) | spectator? — usually the ester is the substrate | varies |
| Decarboxylation (β-keto acid) | leaving_group | -COOH → CO2 + R-H |
| Deprotonation by base | reactive_nucleophile (after deprotonation, carboxylate is nucleophile) | RCOO⁻ attacks alkyl halide → ester |

---

## Negotiation Notes

- **Pairs well with**: alcohols (esterification), amines (amidation), strong bases (deprotonation)
- **Conflicts with**: alcohol — both have -OH. Carboxylic acid takes priority in SMARTS matching.
- **Resolution rules**:
  - In presence of base → deprotonate → carboxylate as nucleophile
  - In presence of alcohol/amine + acid catalyst → C is electrophile, -OH is leaving group
  - β-keto acid + heat → decarboxylation, -COOH is leaving group (becomes CO2)

---

## Edge Cases

- **Dicarboxylic acids** (e.g., succinic acid, oxalic acid): each -COOH is a separate group; they may affect each other's pKa
- **α-Amino acids**: contains both -COOH and -NH2; zwitterion form in neutral water. For project, treat each group separately; user provides protonation state.
- **β-Keto acids**: prone to decarboxylation
- **Anhydride** (R-CO-O-CO-R): not matched by this SMARTS; separate group needed if added later

---

## Implementation Notes

- Priority: higher than alcohol, ester, carbonyl (matches first to claim its atoms)
- Detect protonation state; carboxylate vs carboxylic acid have different role probabilities
- For project, ignore intramolecular H-bonding effects
