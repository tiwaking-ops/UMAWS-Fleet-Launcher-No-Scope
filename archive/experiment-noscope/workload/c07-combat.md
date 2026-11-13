# Toy workload card 07 — combat summary

TOY-OK

## Scope

Single-owner card. Writes only `workload/c07-combat.md`.

## Content

This card records the combat-system summary for the toy workload experiment
(`docs/phase0-verification-2026-11-11.md` and `docs/phase1-workload-2026-11-11.md`).

Combat in CNA is a fixed pipeline (11.0): gun positions, secret barrage plot,
retreat before assault, force assignment, anti-armor fire, then close assault.

The canonical ordering is recorded in `src/cna/rules/sec11_combat.py`
(`COMBAT_STAGES`) so a caller cannot invent another order:

- `position`
- `barrage`
- `retreat_before_assault`
- `force_assignment`
- `anti_armor`
- `close_assault`

The combat CP costs (11.21-11.23) are:

| Stage | Phasing | Non-phasing |
|---|---|---|
| Attack | 5 | 3 |
| Probe | 2 | 2 |
| Routed | — | 1 |

The Combat Segment CP caps (11.24) are:

- phasing: 5 CP per Combat Segment
- non_phasing: 3 CP per Combat Segment

Hard cohesion thresholds:

- `COLLAPSE_AT = -26` — a unit at this Cohesion or worse may not Retreat Before Assault (13.1).
- `SURRENDER_AT = -17` — a defending unit at this Cohesion or worse surrenders (15.88).
- `PROBE_SHARE = Fraction(1, 2)` — a close assault committing less than this share is a Probe (15.25).
- `PROBE_DEFENDER_FLOOR = -3` — a Probe defended at worse than this uses no CP (15.96).
- `DISORGANIZATION_LOSS_PERCENT = 30` — losses at or above this percentage earn three Disorganization Points (15.87).
- `EMPTY_DEFENCE_HEXES = 3` — a defender that allocates nothing retreats and is disorganized (15.29).
- `COMBINED_ARMS_MAX = 4` — the ceiling on the Combined Arms reduction (15.4).

The Artillery Barrage Table (12.6), the Anti-Armor Combat Results Table
(14.6), and the Close Assault Combat Results Table with the Prisoners Captured
Table (15.79, 15.89) are deliberately not in this module: they are R-04 data and
are supplied by the caller. The caller also supplies unit ratings and TOE
Strength Points from the OA sheets (R-06).

## Acceptance

Markers recorded: `TOY-OK`.

Acceptance command:
`python workload/check.py workload/c07-combat.md TOY-OK` (orchestrated by the
harness; the file must itself contain the `TOY-OK` marker).
