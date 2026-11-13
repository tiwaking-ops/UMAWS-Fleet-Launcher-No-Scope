# Toy workload card 32 — terrain combat effects

TOY-OK

## Scope

Single-owner card. Writes only `workload/c32-terrain-effects.md`. No other card writes this file.

## Content

This card records the terrain combat-effects notes for the no-scope toy workload experiment (`docs/phase0-verification-2026-11-11.md`). It is card 32, slug `terrain-effects`, acceptance marker `TOY-OK`.

## Terrain combat effects

Each terrain cell carries a fixed set of combat modifiers applied when a unit attacks into, defends in, or moves through that cell:

- `open` — movement cost 1, cover modifier +0, line of sight unblocked.
- `rough` — movement cost 2, cover modifier +1, line of sight unblocked.
- `woods` — movement cost 2, cover modifier +2, line of sight blocked beyond 2 cells.
- `urban` — movement cost 1, cover modifier +3, line of sight blocked beyond 1 cell.
- `water` — movement cost 3, cover modifier +0, line of sight unblocked, no entrenchment.

Combat resolution applies the defender's terrain cover modifier to the attack roll, and the attacker's movement cost is deducted from the entering unit's remaining movement. Cover modifiers stack with entrenchment but are capped at +5 total.

Terrain effects are evaluated at the start of each combat round from the current cell of each unit; terrain changes mid-round (for example from destruction) do not retroactively alter rolls already resolved.

## Notes

- This is a toy experiment card: the values above are placeholders for the no-scope workload, not a balance commit.
- The checker (`workload/check.py`) verifies only the presence of the `TOY-OK` marker; the format above is the contract for downstream consumers.