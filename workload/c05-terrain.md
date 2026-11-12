# Toy workload card 05 — terrain table

TOY-OK

This card records the terrain table for the no-scope toy experiment
(`docs/phase0-verification-2026-11-11.md`). It is a single-owner card; no other
card writes this file.

## Terrain table (Terrain Effects Chart summary)

| Terrain Type | Movement Cost (MP) | Combat Modifier | Stacking Limit | Breakdown Points |
|---|---:|---:|---:|---:|
| Clear | 1 | 0 | 3 | 0 |
| Rough | 2 | +1 defender | 2 | 2 |
| Woods | 2 | +2 defender | 2 | 1 |
| Town | 1 | +2 defender | 3 | 0 |
| City | 2 | +3 defender | 3 | 0 |
| Swamp | 3 | +1 defender | 1 | 3 |
| Mountain | 4 | +3 defender | 1 | 4 |
| Road/Track | per underlying | per underlying | per underlying | per underlying |
| River (crossing) | +1 MP | +2 defender | — | — |

## Notes

- Movement costs are in addition to the terrain in the hex (per rule 8.31).
- Combat modifiers apply to the defender when attacked into that terrain.
- Stacking limit is the maximum number of units/steps permitted in the hex.
- Breakdown points are the vehicle breakdown threshold for that terrain type.
- Roads and tracks use the underlying terrain for all effects except movement
  along the road, which uses the road movement rate.
- All values are caller-supplied; the official TEC tables from the source game
  are not embedded in this experiment (see D-04, D-05, R-04, R-05 in decisions).

## Source

Derived from the terrain rules referenced in `coverage/rules_coverage.json`
sections 8.31–8.47, 9.14, and 12.11–12.15.