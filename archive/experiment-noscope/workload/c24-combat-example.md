# Toy workload card 24 — combat resolution example

TOY-OK

This card records a combat resolution example for the no-scope toy experiment
(`docs/phase0-verification-2026-11-11.md`). It is a single-owner card; no other
card writes this file.

## Combat Resolution Example

### Scenario
Two units engage in melee combat:
- **Attacker**: Ironclad Vanguard (ATK 12, DEF 8, HP 45)
- **Defender**: Shadow Stalker (ATK 9, DEF 10, HP 38)

### Resolution Steps

1. **Initiative Roll**
   - Attacker rolls 1d20 + 2 (DEX) = 14
   - Defender rolls 1d20 + 3 (DEX) = 18
   - Defender acts first

2. **Defender's Turn (Shadow Stalker)**
   - Attack roll: 1d20 + 4 (proficiency) = 17 vs AC 16 → **Hit**
   - Damage: 1d8 + 3 (STR) = 7 slashing
   - Vanguard HP: 45 → 38

3. **Attacker's Turn (Ironclad Vanguard)**
   - Attack roll: 1d20 + 5 (proficiency) = 22 vs AC 14 → **Hit**
   - Damage: 1d10 + 4 (STR) = 11 bludgeoning
   - Stalker HP: 38 → 27

4. **Round 2 — Defender**
   - Attack roll: 1d20 + 4 = 12 vs AC 16 → **Miss**

5. **Round 2 — Attacker**
   - Attack roll: 1d20 + 5 = 19 vs AC 14 → **Hit**
   - Damage: 1d10 + 4 = 9 bludgeoning
   - Stalker HP: 27 → 18

6. **Round 3 — Defender**
   - Attack roll: 1d20 + 4 = 15 vs AC 16 → **Miss**

7. **Round 3 — Attacker**
   - Attack roll: 1d20 + 5 = 16 vs AC 14 → **Hit**
   - Damage: 1d10 + 4 = 10 bludgeoning
   - Stalker HP: 18 → 8

8. **Round 4 — Defender (Shadow Stalker falls)**
   - Attack roll: 1d20 + 4 = 18 vs AC 16 → **Hit**
   - Damage: 1d8 + 3 = 6 slashing
   - Vanguard HP: 38 → 32

9. **Round 4 — Attacker (finishing blow)**
   - Attack roll: 1d20 + 5 = 14 vs AC 14 → **Hit**
   - Damage: 1d10 + 4 = 8 bludgeoning
   - Stalker HP: 8 → 0 (defeated)

### Outcome
- **Victor**: Ironclad Vanguard (HP 32/45)
- **Defeated**: Shadow Stalker
- **Rounds**: 4
- **Total damage dealt by Vanguard**: 38
- **Total damage dealt by Stalker**: 13

### Notes
- The checker (`workload/check.py`) verifies only the presence of the
  `TOY-OK` marker; the format above is the contract for downstream consumers.
- This example demonstrates the turn-based resolution mechanic with
  initiative, attack rolls, damage calculation, and HP tracking.