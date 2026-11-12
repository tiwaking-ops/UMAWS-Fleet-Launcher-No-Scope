# Toy workload card 27 — unit point costs

TOY-OK

## Scope

Single-owner card. Writes only `workload/c27-points.md`. No other card writes this file.

## Content

This card records the unit point cost table for the no-scope toy workload experiment (`docs/phase0-verification-2026-11-11.md`).

## Point costs

| Unit type | Cost (points) | Notes |
|-----------|---------------|-------|
| Infantry  | 1             | Baseline unit; occupies one slot. |
| Archer    | 2             | Ranged; same slot footprint as infantry. |
| Cavalry   | 3             | Fast movement; requires mounted capability. |
| Siege     | 5             | Heavy; limited to one per formation. |

## Rules

- Total formation cost is the sum of unit point costs for all units in the formation.
- A formation must satisfy its scenario point cap; exceeding the cap is invalid.
- Point costs are fixed for this workload card and do not vary by terrain or scenario modifiers.

## Notes

- The checker (`workload/check.py`) verifies only the presence of the `TOY-OK` marker; the table above is the contract for downstream consumers.
