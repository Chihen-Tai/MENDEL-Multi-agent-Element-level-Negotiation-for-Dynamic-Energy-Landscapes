# Nitrile Agent

## Identity

**Name**: nitrile
**SMARTS**: `[CX2]#[NX1]`
**Description**: -C≡N, sp C bonded to sp N.

---

## Atoms

| Index | Element | Role within group |
|---|---|---|
| 0 | C | sp carbon |
| 1 | N | sp nitrogen |

---

## Allowed Roles

| Role | Allowed? | Condition |
|---|---|---|
| reactive_electrophile | yes | C of nitrile is electrophilic (like carbonyl C) |
| reactive_nucleophile | yes (rare) | N lone pair as weak nucleophile (e.g., metal coordination, Ritter) |
| reactive_radical | rare | — |
| leaving_group | rare | -CN can leave as cyanide in special cases |
| spectator | yes (default) | nitriles are generally unreactive at room T |

---

## Key Descriptors

- **Electrophilicity at C**: similar to carbonyl but slightly less (resonance with N lone pair)
- **α-H acidity**: α-C-H is acidic (pKa ~25, similar to ester)
- **Hydrolysis**: -CN → -CONH2 → -COOH under acidic/basic conditions
- **Reduction**: -CN → -CH2NH2 (primary amine) via LiAlH4
- **Steric**: linear C≡N is very compact

---

## Example Reactions

| Reaction | Role | Reasoning |
|---|---|---|
| Hydrolysis to amide/acid | reactive_electrophile | water attacks C |
| Reduction (LiAlH4) | reactive_electrophile | hydride attacks C |
| Grignard addition | reactive_electrophile | RMgX adds, gives ketone after hydrolysis |
| Ritter reaction (RCN + R'-OH/H+) | reactive_nucleophile (N) | N attacks carbocation |
| α-C deprotonation (nitrile-stabilized carbanion) | spectator at -CN, nucleophile at α-C | α-C carries reactivity |
| Click chemistry (alkyne + nitrile? — no, alkyne + azide); irrelevant | spectator | — |

---

## Negotiation Notes

- **Pairs well with**: strong nucleophiles (organometallics, hydride donors), water (under catalysis), carbocations (Ritter)
- **Conflicts with**: carbonyl-like behavior. Carbonyl > nitrile in most electrophilic contexts.
- **Resolution rules**:
  - Default to spectator unless strong nucleophile/electrophile present
  - α-C handles deprotonation/alkylation chemistry, not the nitrile itself

---

## Edge Cases

- **Isocyanide** (-N⁺≡C⁻): different chemistry; not matched by this SMARTS (different connectivity)
- **Cyanohydrin** (R2C(OH)CN): the -OH and -CN are separate groups; -CN often spectator
- **Cyanide ion** (CN⁻ as separate species): different — this is a free nucleophile, not a substrate group
- **Acrylonitrile** (CH2=CH-CN): both alkene and nitrile present; alkene is Michael acceptor

---

## Implementation Notes

- Priority: medium; doesn't overlap with most other groups
- α-C of nitrile is part of methyl/methylene group; that group handles enolate-like chemistry
- For project scope, often spectator
