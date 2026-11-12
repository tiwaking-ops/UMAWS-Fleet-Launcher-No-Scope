# Toy workload card 29 — ai opponent behavior

TOY-OK

This card records the AI opponent behavior for the toy workload experiment
(`docs/phase0-verification-2026-11-11.md`). It is a single-owner card; no other
card writes this file.

## Scope

Write only: `workload/c29-ai.md`. Read: `workload/README.md`.

## AI opponent behavior

- **Decision cadence.** The AI opponent evaluates the current board state at
  the start of its turn and selects actions in priority order (objective,
  survival, pressure).
- **Target selection.** Prefer reachable targets that advance scenario
  objectives; break ties by lowest expected risk to the acting unit.
- **Fallback.** If no productive action is available, the opponent takes a
  defensive posture (hold position, improve cover/visibility as applicable).

## Acceptance

- Deliverable: `workload/c29-ai.md`
- Marker: `TOY-OK`
- Oracle (run by the harness after exit): `python workload/check.py workload/c29-ai.md TOY-OK`
