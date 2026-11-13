# Toy workload card 34 — supply line tracing

TOY-OK

## Scope

Single-owner card. Writes only `workload/c34-supply-lines.md`. No other card writes this file.

## Content

### Supply line tracing

A supply line is traced from a supply source to a unit following these rules:

1. **Source identification**: Supply lines originate from a friendly supply source (depot, airfield, or port). The source is identified by its map coordinate.

2. **Path tracing**: The line is traced cell-by-cell from the source toward the target unit. Each step follows the shortest viable path through adjacent cells that are not blocked by enemy units, impassable terrain, or distance limits.

3. **Distance limit**: Supply lines have a maximum range of 6 cells from the source. If the unit is beyond 6 cells, the line is broken and no supply is received.

4. **Line integrity**: A supply line breaks if any of the following conditions are met:
   - An enemy unit occupies any cell along the path
   - Impassable terrain (water, extreme elevation) blocks the path
   - The cumulative path exceeds the 6-cell distance limit
   - The path must remain continuously connected (no teleporting over gaps)

5. **Unit supply status**: If the supply line is unbroken within the distance limit, the unit receives full supply. If the line is broken or the unit is beyond the limit, the unit is out of supply and suffers reduced combat effectiveness.

### Examples

- A unit 3 cells away from a depot with no obstructions has a valid supply line.
- A unit 7 cells away from a depot is beyond the distance limit and out of supply.
- A unit 4 cells away with an enemy unit blocking the direct path may have its line rerouted if an alternative path within the distance limit exists.

## Notes

- This is a toy experiment card: the values and rules above are placeholders for the no-scope workload, not a combat commit.
- The checker (`workload/check.py`) verifies only the presence of the `TOY-OK` marker; the format above is the contract for downstream consumers.