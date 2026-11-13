# PDD: UMAWS Fleet Launcher No-Scope System — version: 1 — status: baseline (this document)

## 1. Purpose

The UMAWS Fleet Launcher No-Scope System is the permanent project folder for a
Kernel-lite multi-agent coordination system: a Fleet Dispatcher that runs CLI
agents unattended, a browser Console to watch it, and a hierarchical quota
engine. It is the system that was exercised by the no-scope experiment and is
now promoted to a standing project (operator: Tiwa Pene; see
`docs/promotion-no-scope-system-2026-11-13.md`).

This PDD is the baseline design record for that standing system. It states what
the system is for, what "done" means for the current baseline, what is
deliberately out of scope, and what remains open.

## 2. Goals

Each goal is a verifiable property of the standing system. Goals G-001…G-006
describe the baseline that is built and tested; G-007 records the one open
obligation carried from the promotion.

### G-001 Kernel integrity and single-writer discipline

acceptance:
- the event log is append-only with a hash chain that verifies (`I1`);
- `pmk sentinel` reports clean across all invariants;
- agents never write `.pm/` directly (I2).

oracle: `pmk sentinel`

### G-002 Task, lease, and oracle model

acceptance:
- a task cannot reach DONE without a passing `gate_cmd` and an evidence bundle;
- leases are fenced and stale-fence submissions are quarantined, never merged;
- the oracles decide, not the agent's claim.

oracle: `pmk task list --state DONE --json`

### G-003 Fleet dispatch and recovery

acceptance:
- the Dispatcher assigns tasks to profiles and fills slots up to the cap;
- the recovery ladder (L0–L4) re-dispatches failures with backoff and cooldown;
- the merge queue integrates verified work through the serial gate.

oracle: `pytest -q tests/fleet`

### G-004 Console observability

acceptance:
- the Console binds to 127.0.0.1 only;
- the seven tabs (Projects, Fleet, Tasks, Queue, Overseer, Manual launcher, Metrics) render from Kernel state.

manual-check: operator opens http://127.0.0.1:8765 and confirms the seven tabs render from live state

### G-005 QuotaGate engine

acceptance:
- hierarchical quota accounting (RPM, TPM, RPD) with timezone-aware resets;
- the engine is exercised by its unit tests.

oracle: `pytest -q tests/quotagate`

### G-006 Test suite green

acceptance:
- the full suite passes on the standard library plus declared deps;
- the Kernel, Fleet, Console and QuotaGate suites are all collected and pass.

oracle: `pytest -q`

### G-007 Close the promotion's residual obligation

acceptance:
- the toy-experiment cards are retired (done: 15 VOID, 2026-11-13);
- the operator records whether any further width/capacity work is wanted.

manual-check: operator confirms the ledger is clean (READY = 0) and states whether capacity work is in scope

## 3. Non-goals

- A strong or "historical" game AI (that belonged to the archived CNA workload).
- Network play, multi-tenant hosting, or a public multi-user service.
- Linux/macOS support (Windows-native is a constraint, not a gap).
- Delegating operator authority to agents: privileged acts (task void, class-K
  decisions, profile state, dispatch run) remain human-only by design.
- Any change to the archived experiment record (`archive/experiment-noscope/`).

## 4. Constraints

- Windows 10 native; no WSL. Path length and `cmd.exe` argument mangling are handled in `src/pmk/plat.py`.
- Python 3.12 in `.venv`; the Kernel (`src/pmk/`) is standard library only; additional deps are declared in `pyproject.toml` / `requirements.lock`.
- The Kernel (`pmk`) is the only writer of coordination state; nothing edits `.pm/` directly.
- Oracles must be Windows-safe and non-interactive.
- The constitution and policy under `.pm/` are pinned (class K); changes require two-key (human) approval.
- Free-tier providers first; no quota hammering (backoff + cooldown).

## 5. Architecture sketch

```
Operator ── browser ─► Console (FastAPI, 127.0.0.1 only)
                        │
                        ▼
                  umaws app process
                    Conductor   lifecycle, wakes the Overseer
                    Dispatcher  selects a profile, claims a task
                    Adapters    hermes | kilo | cline | pi | opencode | fake
                    Harness     worktree, order file, oracles, evidence
                    pmk.api     the Kernel: the only writer of state
```

- `src/pmk/` — Kernel: events (hash chain), tasks, leases (fencing), views,
  briefing, sentinel, PDD lint, authority gate, context sync, the API and CLI.
- `src/fleet/` — profiles, adapters, selection, harness, recovery ladder,
  Dispatcher, Conductor, merge queue, Overseer runner, project lifecycle,
  scratch/worktree lifecycle, manual-launcher port.
- `src/console/` — FastAPI Console and its single HTML page.
- `src/quotagate/` — hierarchical quota engine (QuotaGate M0–M2 core).
- `tests/` — the full suite (Kernel, Fleet, QuotaGate) run against a scriptable fake CLI.
- `.pm/` — coordination state: event log, views, task cards, evidence, pinned constitution and policy.

## 6. Definition of done

gate_cmd: `pytest -q`

The baseline is "done" when the gate command passes, `pmk sentinel` is clean,
and every goal above is either oracle-green or operator-confirmed.

## 7. Open questions

None blocking the baseline. Recorded for the operator:

- Whether any further width/capacity work is wanted now that the cap experiment
  is closed (G-007 manual check).
- Whether the live GitHub repo's description ("Unscoped Task Ledger Edition")
  should be updated to match the standing project (cosmetic; no code impact).