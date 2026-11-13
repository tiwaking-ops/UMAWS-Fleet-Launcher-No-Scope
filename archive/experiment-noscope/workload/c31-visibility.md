# Toy workload card 31 — visibility and night rules

TOY-OK

## Scope

Single-owner card. Writes only `workload/c31-visibility.md`. No other card writes this file.

## Content

This card records the visibility and night rules for the toy experiment workload of the UMAWS no-scope experiment. The experiment removes scope gating from the Launcher: workers share one prompt and one worktree, so these rules define the experiment's observable surface and its required behaviour during low-activity windows.

### Visibility rules

- The worktree is the single visibility boundary. Every path under `workload/` is visible to any worker holding a lease; no path outside `workload/` is visible to workers.
- The three shared files (`shared-a.md`, `shared-b.md`, `shared-c.md`) are the only cross-card visibility channel. A card must not read another card's `c<NN>-<slug>.md` file.
- Cards 15-17 may write `shared-a.md` and `shared-b.md`; cards 18-20 may write `shared-b.md` and `shared-c.md`. Every pair therefore overlaps on `shared-b.md`.
- The acceptance gate is `workload/check.py`, invoked as `python workload/check.py <file> TOY-OK`. Workers may read the checker script; they may not modify it. The gate result is recorded by the harness, not by the worker.
- Visibility never implies ownership: a worker that reads `shared-b.md` sees the latest committed version; it may not assume that version is the one its later write will merge with.

### Night rules

- "Night" is the low-activity window when no dispatcher is running. During night, no worker may create new tasks, claim new cards, or renew leases.
- Open leases that expired during the day may be kept or revoked at the start of night; a revoked lease must be logged in the event log before revocation.
- Night is a quiescence window. The only allowed filesystem activity is reading the checker and the premise files; no worker process may be spawned in the worktree during night.
- Night ends with an explicit wake event recorded in the log. The first action on wake is a premise re-check (`python workload/check.py workload/README.md WORKLOAD-BASE`) before any new card activity.

## Notes

- The checker (`workload/check.py`) verifies only the presence of the `TOY-OK` marker; the rules above are the contract for downstream consumers.
- This card is a single-owner card; no other card writes `workload/c31-visibility.md`.
