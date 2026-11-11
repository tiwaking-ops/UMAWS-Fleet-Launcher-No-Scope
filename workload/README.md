# Workload base — UMAWS no-scope experiment

WORKLOAD-BASE

This directory holds the 20-card workload for the experiment described in
`docs/phase0-verification-2026-11-11.md` and the D-75/76/77 records in
`pilot/decisions.md`.

- `check.py` — the Windows-safe oracle checker every card uses.
- Deliverables are `c<NN>-<slug>.md` (single-owner cards).
- `shared-a.md`, `shared-b.md`, `shared-c.md` are deliberately written by
  six cards each, to make write-scope overlap testable at claim time.
  Cards 15-17 own `a`+`b`, cards 18-20 own `b`+`c`; every pair therefore
  overlaps on `b`.
