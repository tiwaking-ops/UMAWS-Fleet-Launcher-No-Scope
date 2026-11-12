---
document:
  title: "Incident and repair report — Arm-0 measurement failure and its remediation"
  status: "Comprehensive incident report. Authoritative for what went wrong and what must change before further arms run. Authorises no further change by itself."
  version: "1.3.1"
  date: "2026-11-12"
  amended: "2026-11-12 - v1.1.0 resolves U-01 (cause established), adds REC-15, fixes the throughput denominator convention and the requeue decision (D-79). v1.2.0 adds §9.1 implementation status for every REC, verified by measurement, and states REC-15's partial scope explicitly. v1.3.0 records the independent assessment: corrects the merge-conflict, anomaly-count and cap-binding claims, and adds §14. v1.3.1 adds §14.4: §9.3's baseline-2 window includes the next run's first claims, so its 2.995 DONE/h is replaced by 4.024 DONE/h in the correct window."
Author: "Tencent HY4 Preview, version tencent/hy4-preview-free (orcarouter)"
provenance:
  author_llm: {name: "Tencent HY4 Preview", version: "tencent/hy4-preview-free (orcarouter)"}
  assessor_llm: [{name: "opencode", version: "baidu/ernie-5.5-flash-preview:free"}]
  created_date: "2026-11-12"
  scope: "Toy repository C:\\temp\\projects\\umaws-noscope-toy only"
authority_statement: "Analysis and recommendation record. It ratifies nothing and changes nothing. It was unassessed at v1.2.0; v1.3.0 records an independent assessment (opencode, baidu/ernie-5.5-flash-preview:free) in §14 and corrects three factual claims. It is written for integration into the final overall report once all testing is complete."
---

# Incident and repair report — Arm-0 measurement failure

## 0. Why this report exists

The purpose is **prevention**. Across one baseline attempt, four separate
classes of defect each independently produced numbers that looked like findings
and were not. None of them breached integrity — the sentinel never fired and no
invariant was violated — but three of them would have corrupted the experiment's
primary comparison if they had gone uncaught. This document records what
happened, what was measured after repair, and what must change so it does not
recur.

Classification chosen: **measurement and method failure**, with scaffolding and
system defects as contributing causes. No integrity breach occurred. This is
recorded as a **document, not a ledger `INCIDENT`**, deliberately: an `INCIDENT`
event would land inside the log that Arm A is compared against and would corrupt
metric 3 (conflict and incident rate) for every future arm.

---

## 1. Summary of what went wrong

| # | Defect class | Specific defect | Consequence | Withdrawn or repaired |
|---|---|---|---|---|
| 1 | Method (mine) | Ran `pmk dispatch run` instead of `pmk project run` | Dispatcher alone cannot reach `DONE`; throughput reported as 0 | Two numbers **withdrawn** |
| 2 | Scaffolding (mine) | Toy copy missing `coverage/rules_coverage.json` and `.githooks/pre-commit` | Global gate `pytest -q` failed on 4 pre-existing tests; **no card could reach `DONE` in any arm** | Repaired, commit `e8d278a` |
| 3 | System (launcher) | `Kernel.task_ready()` exists but has **zero callers in `src`** | `REWORK` cards never return to `READY`; width stalled at 3 | Repaired by operator requeue; fix recommended (REC-01) |
| 4 | Measurement (mine) | Width counted from leases, which outlive their agents | Reported 16 concurrency where 10 agents were live | Measured correctly; analyzer fixed, `8becbe1` |
| 5 | Measurement (mine) | `--start/--end` filtered only lease intervals, not the counters | Headline counts described the whole log, not the window | Analyzer fixed, `8becbe1` |
| 6 | Measurement (mine) | `TASK_DONE` treated as terminal; pipeline emits `INTEGRATED` | Printed `throughput 0.000` for a run that completed 3 cards | Analyzer fixed, `8becbe1` |

---

## 2. Defect 1 — the wrong supervision loop (withdrawn numbers)

The baseline was run three times as `pmk dispatch run --seconds N`. That
constructs and ticks **only the Dispatcher**. `cli.py:815` shows what runs all
three components:

```python
dispatcher = Dispatcher(kernel, fleet_state, ...)
overseer   = OverseerRunner(kernel, fleet_state)
conductor  = Conductor(kernel, dispatcher, overseer)
while time.time() < deadline:
    conductor.tick()
    dispatcher.tick()
```

The Conductor owns everything downstream of `SUBMITTED` (`conductor.py:673`):
`drain_merge_queue()`, `reap_expired_leases()`, `advance()`. None exists on the
Dispatcher-only path.

**Two numbers were published from those runs and are withdrawn:**

- "Throughput = 0 `DONE` per wall-hour" — an artefact of never running the merge
  queue, not a property of the baseline.
- "The fleet wedges permanently" — real, but self-inflicted: `reap_expired_leases()`
  clears it, and I was running without the component that reaps.

Full record: `docs/arm0-method-error-dispatch-vs-project-2026-11-12.md`.

## 3. Defect 2 — the gate was red, so nothing could finish

Cards are judged by the **global policy command**, `.pm/policy.toml:67` →
`cmd = "pytest -q"`, not by the per-card `check.py` oracle. `pytest -q` failed on
4 pre-existing tests, so every verified card came back `ORACLE_FAILED`.

Two genuine scaffold defects, both absent from the toy copy and both tracked in
the live repo:

1. `coverage/rules_coverage.json` — a build artifact produced by
   `python -m cna.tools.coverage`. Generating it fixed both
   `test_rules_baseline` failures **and** `test_release_status`.
2. `.githooks/pre-commit` — missing entirely, so `test_identity_guard` exited
   127 (`No such file or directory`). Copied from the live repo.

After repair, full `pytest -q` exits **0**. Committed as `e8d278a`, with both
files tracked — matching the live repo's treatment — so they exist inside
worktrees and merge directories.

> **This defect blocked every card in every arm.** Throughput was unmeasurable
> across the entire experiment until it was fixed.

**Deliberately not done:** editing `.pm/policy.toml` to point the gate at the
per-card oracle. That changes `policy_hash` and engages **I8'**, which under
OR-15 aborts the arm immediately. The safe repair was to fix the artifacts.

## 4. Defect 3 — recovery is implemented and never called

Established in code, not inferred:

- `Kernel.task_ready()` at `api.py:391` appends `TASK_READY`.
- **Grep across `src` finds zero callers.** No fleet component, no CLI
  subcommand ever moves a card back.
- `models.py:46` permits `REWORK → READY`, and `api.py:401` describes REWORK as
  returning a task "to READY for re-dispatch". The capability is implemented,
  legal, documented — and dead.
- `dispatcher.py:233` dispatches only `state.ready_tasks()`, so a `REWORK` card
  is invisible until something requeues it. `recover.py:120` (L4) moves an
  attempts-exhausted card to `BLOCKED`.

**Measured effect.** Same configuration, operator action only, 8 `REWORK` cards
returned to `READY` through the Kernel:

| Metric | Arm-0 | Arm-0b (requeued) |
|---|---|---|
| tasks DONE | 3 | **10** |
| Live sustained concurrency | 3 | **10** |
| Throughput DONE/h | 5.55 | 6.14 |
| Denial rate | 73.3 % | 38.9 % |
| INCIDENT | 0 | 0 |

**This is the single most important finding: throughput was bounded by failure
recovery, upstream of anything the arm relaxations change.** Neither arm can be
measured for width until this is fixed (REC-01).

## 5. Defect 4 — width must be counted from live runs, not leases

Lease concurrency for Arm-0b reports **16**. Live agent concurrency for the same
window reports **10**:

```
peak concurrent    : 16        <- leases
LIVE peak concurrent: 10       <- agents actually running
LIVE sustained      : 10
```

Cause: a kernel lease outlives its agent. The run object leaves
`dispatcher.self.runs` on exit (`:207`) while the lease survives, so leases count
agents that have already exited. The overstatement here was **6**.

Reporting 16 would have placed Arm-0 **inside OR-04's 12–20 target band** and
wrongly implied the relaxations buy nothing. This also resolves an apparent
contradiction in earlier records: the observation "15 leases under a cap of 10"
is lease-based and true; it does **not** mean the cap is loose for live agents.

### 5.1 Consequence: `max_total_agents` may bind (corrected v1.3.0)

Sustained live concurrency is **exactly 10**, equal to `max_total_agents = 10`.
The ceiling therefore appears to bind, and OR-04's 12–20 would be unreachable
without raising it.

> **Correction (v1.3.0, independent assessment).** The equality of observed live
> width and the configured cap is not evidence that the cap *binds*. In Arm-0b
> the live series reaches 10 only in a 16 min 20 s burst (02:26:20–02:42:40)
> immediately after the requeue released eight cards, then sits at **8 for
> 4,428 s — 75.5% of the 5,860 s window** — and never returns to 10. No
> `FLEET_BLOCKED` event names a fleet cap. The defensible statement is: *the cap
> was reached once, in a requeue burst; steady-state width was 8, so the cap's
> bindingness is not established.* Baseline-2 shows the same shape (level 3 for
> 66% of its window, level 10 for 25%). D-78's premise should be re-tested with a
> cap-refusal measurement before the next arm relies on it.

An earlier speculation of mine — that the cap might not bind and no amendment
would be needed — **is withdrawn**; it relied on the lease-based figure.

Correction to a still-earlier claim: I said `max_total_agents` "is named nowhere
in §7.2". It **is** named there (line 198), in the warning "Do **not** rely on
`max_total_agents` alone — profile `max_concurrent` is a second limiter". The
precise gap is that the row instructs raising `max_concurrent` but never the
ceiling itself.

**Decision D-78 ratified by the operator 2026-11-12** (toy register, committed
`b95fabb`): raise **both** — `max_total_agents` 10 → 20 and per-profile
`max_concurrent` — revertible, toy-only, no `.pm/policy.toml` change so no I8'
exposure; width verified by counting simultaneous live runs, per R-A4.

## 6. Defect 5 and 6 — analyzer windowing and terminal event

With `--start/--end` set, the counters still read the whole log:

```
window             : 85 of 539 events
CLAIMED events     : 40      <- window actually contains 4
FLEET_BLOCKED      : 55      <- window actually contains 11
```

Two fixes plus a denominator fix, committed `8becbe1`:

1. The window is applied **once** to a filtered list that every counter reads.
   Post-fix the counters reconcile exactly with a hand count of the window.
2. Terminal is `INTEGRATED`, not `TASK_DONE` — this pipeline never emits
   `TASK_DONE`. Counted as **distinct subjects** so a card emitting both is not
   double-counted.
3. Throughput divides by **arm wall time** when a window is given, not by an
   implicit lease span inflated with idle time.

---

## 7. Additional measured findings

### 7.1 Denials are not `LEASE_REFUSED`

`LEASE_REFUSED` is **0** across the entire log, yet D-L6 demonstrably refuses
claims. Denials are recorded as **`FLEET_BLOCKED` with
`payload {"blocker": "scope_overlap"}`**. Using `LEASE_REFUSED` reports zero
denials for a run full of them. In Arm-0b: 14 `FLEET_BLOCKED` — 12
`scope_overlap` and 2 `already satisfied on main`.

### 7.2 No merge conflicts observed (corrected v1.3.0)

3 `QUARANTINED` events (T-0008, T-0009, T-0011), class `UNKNOWN`. **These are
not merge conflicts.** Each carries `reason: "attempts exhausted (3/3)"` and is
an L4 worktree quarantine from `harness._give_up` (`harness.py:851-864`), on
single-owner cards with no scope overlap. The path is
`.pm/quarantine/<task>-<fence>`, not a conflicting source path.

> **Correction (v1.3.0, independent assessment).** Arm-0b therefore recorded
> **zero merge conflicts**; the conflict baseline is 0/36 attempts, not 3. §8
> U-06 and REC-11 must be read with this correction: counting all `QUARANTINED`
> events as conflicts would count attempt-exhaustions, not overlaps.

### 7.3 Workload drift: 20 → 34 cards

All 14 new cards were created during the run by the Overseer under agent id
`overseer-gap-fill`; 4 of them reached `DONE` (T-0021, T-0022, T-0025, T-0026).
Throughput is therefore measured over an **expanding workload**, so Arm-0 and
Arm-0b are not strictly the same workload. Must be frozen for a valid comparison
(REC-04).

### 7.4 Identity anomaly

10 `IDENTITY_ANOMALY` events in Arm-0b (3 in the Arm-0 window; the 8 are
pre-window `dispatch run` events). Each worker commit was
auto-pinned at stage `commit` from the effective identity
`Tiwa Pene <tiwaking@gmail.com>` to the expected `umaws-pilot <umaws-pilot@localhost>`.
Every card carries the pipeline identity, so **commits do not currently carry
per-agent identity** — directly relevant to Arm A's worker-commit identity and
provenance-trailer requirement (§7.2, D-76). Consistent with **D-67**: past
attribution stays recorded and is not rewritten; the future-facing session that
produced them remains **unknown**.

### 7.5 Integrity held throughout

`pmk sentinel` → `{"ok": true, "findings": []}`; `pmk pins check` →
`{"ok": true, "mismatches": []}`. No **I1 / I8' / I13** violation, so **OR-15
never fired**. For accuracy on naming: the sentinel prints `I8'`, which is **not
a typo for I8** — `policy.py:131` defines `I8'` as "pinned files match their
recorded hashes" and `sentinel.py:33` enforces it via `STOP_INVARIANTS`. OR-15's
"I8" is the invariant the sentinel actually checks. My earlier suspicion of a
missing check is withdrawn.

### 7.6 Operator effort (metric 4)

**0 interventions inside the Arm-0 window**; **1** (the requeue) before Arm-0b.
Getting to that point cost roughly seven further actions — stopping the wrong
loop, a `sweep`, diagnosing the gate, generating the coverage artifact,
restoring the hook, committing, repairing the analyzer. All scaffolding repair,
none of it coordination. Reporting effort without this qualifier would mislead.

---

## 8. Unresolved issues

Each is stated with its evidence status; none is guessed at.

| ID | Issue | Status |
|---|---|---|
| U-01 | A `--seconds 1800` run spanned **~97 minutes** (02:20:33Z → 03:58:13Z) | **RESOLVED v1.1.0.** Cause established at `cli.py:832-836`: the deadline is tested only at the top of each iteration, and one iteration runs a full `conductor.tick()` (merge drain, integration, per-card `pytest -q`) plus `dispatcher.tick()` plus `sleep(1)`, so the run overshoots by up to **one entire tick**. Corroborated by lease T-0005 held **1882 s (31.4 min)**, longer than the whole requested budget. `--seconds` therefore bounds nothing usefully. See REC-15. |
| U-02 | Whether `max_total_agents` still binds above width 10 once raised, or a third limiter appears | Must be measured in Phase 3 (recorded in D-78 as untested) |
| U-03 | Whether the loose cap semantics admit more *leases* without admitting more *live agents* | Recorded in D-78 as untested; see REC-03 |
| U-04 | Whether gap-fill cards are representative of the seeded workload | Unknown; drives REC-04 |
| U-05 | Attribution of the commits behind `IDENTITY_ANOMALY` | **Unknown** session; D-67 stands |
| U-06 | `QUARANTINED` conflicts classified `UNKNOWN` with root paths | Classification not diagnosed |
| U-07 | Throughput rests on 10 completions over ~1 h (G-02) | Small sample; treat as indicative |
| U-08 | No `SENTINEL_RUN` event occurs inside either window | "Clean during the run" is inferred from a post-run check, not in-run evidence |

---

## 9. Recommendations

Tracked IDs for closure in the final overall report.

| ID | Recommendation | Type | Prevents |
|---|---|---|---|
| **REC-01** | **Wire the requeue path**: have the Conductor call `Kernel.task_ready()` for `REWORK` cards (legal per `models.py:46`) and expose a CLI path (`pmk task ready`). The capability exists and is unused. | Code | Width stalling at 3; unmeasurable arms (defect 3) |
| **REC-02** | **Measure width from `AGENT_STARTED`→`AGENT_EXITED`, never from leases.** Report lease and live figures side by side, and label which is authoritative. | Process | Reporting 16 for 10; false OR-04 pass (defect 4) |
| **REC-03** | **Make the lease/live distinction visible in the product** — expose a live-run count in `pmk fleet status`, or emit an event when a lease outlives its agent, so the distinction cannot be rediscovered by accident. | Code | Silent width overstatement (U-03) |
| **REC-04** | **Freeze the workload** for any comparative run: disable Overseer gap-fill, or count completions only against the seeded set. Record card count before and after every run. | Process | 20 → 34 drift; incomparable arms (defect 7.3) |
| **REC-05** | **Preflight every arm on a clean base**: full gate green, and assert the presence of generated artifacts (`coverage/rules_coverage.json`) and tracked hooks (`.githooks/pre-commit`). Ship it as a runnable script. | Code + process | A red global gate silently blocking every card (defect 2) |
| **REC-06** | **Use `pmk project run`, never `pmk dispatch run`**, for any run that must reach `DONE`. Add an explicit warning where `dispatch run` is offered. | Code + process | Throughput of 0 being read as a finding (defect 1) |
| **REC-07** | **Window all metric analysis, and assert it**: the analyzer must verify that windowed counts reconcile with a raw count of the same window. Add that as a regression check. | Code | Counters reading the whole log (defect 5) |
| **REC-08** | **Document that denial is `FLEET_BLOCKED{"blocker":"scope_overlap"}`**, not `LEASE_REFUSED`, which is always 0. Never report `LEASE_REFUSED` as a denial metric. | Process | A conflict metric with no denominator |
| **REC-09** | **Never repair a failing gate by editing `.pm/policy.toml`.** Fix artifacts instead; a `policy_hash` change engages I8' and OR-15 aborts the arm. Codify as a standing warning. | Process | Self-inflicted integrity abort |
| **REC-10** | **Give worker commits the acting agent's identity plus a provenance trailer** before Arm A runs — today every commit is pinned to the pipeline identity. | Code | Arm A's identity requirement being untestable (defect 7.4) |
| **REC-11** | **Count `QUARANTINED` events into metric 3 explicitly**, with the exclusion of any deliberate `INCIDENT` record documented (as done here). | Process | Conflict rate being silently wrong |
| **REC-12** | **Verify bounded runs actually bounded**: compare measured span against `--seconds` before quoting any per-hour figure. | Process | U-01 corrupting throughput denominators |
| **REC-13** | **Apply D-78 and verify by counting**, not by assuming the configured value took effect (per R-A4). | Process | Raising a knob that was never the limiter |
| **REC-14** | **Keep the terminal-event vocabulary correct**: this pipeline emits `INTEGRATED`; `TASK_DONE` is not emitted. Assert it where completions are counted. | Code | `throughput 0.000` for a run with 10 completions (defect 6) |
| **REC-15** | **Make `--seconds` actually bound the run.** Test the deadline inside the tick loop, or bound the work a single `conductor.tick()` may perform, and warn when a run overruns its budget by more than a tick. As written the flag bounds only *when the next tick starts* (`cli.py:832-836`). | Code | A 30-minute budget becoming 97 minutes (U-01) |
| **REC-16** | **Throughput divides by the measured window, never the configured budget.** Adopted by operator decision 2026-11-12 (D-79): 6.14 DONE/h, not 20.0 DONE/h. Apply to **every** arm without exception, and record the window bounds alongside every throughput figure. | Process | Two defensible denominators differing by 3.3x |
| **REC-17** | **Requeue protocol for the duration of the experiment:** perform exactly **one** manual requeue per arm, at the same point (before launch), for **both** arms, and log it as an operator intervention. Do **not** enable automatic requeue until all arms are finished. | Process | Recovery becoming an unmatched confound between arms (see D-79) |

### 9.1 Implementation status

Every status below is **measured**, not assumed; each was verified by running
the gate and a check designed to fail if the change were absent.

| REC | Status | Commit | Verification |
|---|---|---|---|
| REC-01 | **Deferred** — toy-only D-79 holds it until all arms finish | — | Operator decision 2026-11-12; not overridden |
| REC-02 | Implemented in the analyzer | analyzer commits, see `arm0b-evidence` output | Lease and live figures printed side by side: 22 leases vs 10 live |
| REC-03 | Implemented | `7ba2f8c` | Injection test: 2 slots tracked → `live_runs` 1, `stale_slots` 1, `slots_in_use` 2 |
| REC-04 | Implemented | `a9c9a34` | Contract strings `12-20`, `max_total_agents`, `tree root` all still present |
| REC-05 | Implemented | `ac6f729` | Exit 0 clean; non-zero when pointed at the live repo |
| REC-06 | Implemented | `a71b6c5` | Warning prints 5 lines; carried in `pmk dispatch --help`; cannot fire on `project run` |
| REC-07 | Implemented | `a42f88b` | Reconciliation prints CLAIMED 22 window vs 62 whole log |
| REC-10 | Implemented | `f250a16` | Real ledger: T-0007 → `hermes-solar-mini4`, T-0012 → `cline-solar-mini4` |
| REC-11 | Implemented | `53d62fe` | Metric 3 went 0.0% → **13.6%** (3 QUARANTINED / 22 claims) |
| REC-12 | Implemented | `0711799` | Arm-0b 5860 s measured vs 1800 s requested → ×3.26 OVERRAN |
| REC-13 | **Applied, then reverted for the baseline** | `f1b2e7f` / `a7da80c` | Ceiling min(20,37)=20 when applied; restored to cap 10 so the new baseline is a true control |
| REC-14 | Implemented | `4b16a0d` | Injected `TASK_DONE` raises AssertionError — guard is non-vacuous |
| REC-15 | Implemented, then repaired | `2c5568e`, `ca442c8` | Fake clock: old loop 202 s vs new 101 s on a 150 s budget. **`2c5568e` alone was not sufficient** — see 9.2 |
| REC-16 | Adopted as convention | D-79 | Throughput divides by measured window: 6.14 DONE/h, not 20.0 |
| REC-17 | Adopted as protocol | D-79 | One matched requeue before each arm; baseline-2 requeue logged |

**REC-15 is deliberately partial.** It makes `--seconds` bound the run by
refusing to start a tick that would outlive the budget, and by not sleeping past
the deadline. It does **not** bound the work a single `conductor.tick()` may
perform — the deeper remedy the recommendation also names. That is a conductor
redesign, not a loop change. The consequence is visible in the evidence: with
coarse ticks a run can finish **early**, because budget too small for another
tick is left unused (1800 s budget, 600 s ticks → stopped at 1202 s). That is
the honest cost of not overrunning, and anyone sizing a future run needs it.

**The unimplemented half is not theoretical; it destroyed a measurement.** See
9.2 for the run in which one tick alone consumed 3399.9 s of an 1800 s budget.

### 9.2 The baseline-2 run: one tick, and a verification claim that was not earned

The re-baseline run launched 2026-11-12T08:33:22Z with `--seconds 1800` and
ended 09:30:02Z. Its own report line read:

```
run budget : requested 1800s, measured 3400s, 1 ticks (last tick 3399.9s)
```

Exactly **one** tick. The event log shows why that tick could not fit in any
sane budget: `drain_merge_queue()` integrates every SUBMITTED/VERIFYING task
serially, each running the full gate (~9 min), and the run inherited six
leftover SUBMITTED cards. Roughly 53 minutes of serial gate work preceded
`advance()`, which then dispatched five agents in the final 30 seconds
(`AGENT_STARTED T-0035` 09:29:26Z, `T-0036` 09:30:02Z). The budget was gone, so
every one of those agents died without exiting.

| | Arm-0b (reference) | baseline-2 (crashed) |
|---|---|---|
| ticks | several, each overrunning | **1** |
| AGENT_EXITED | present | **0** |
| live sustained | 10 | **0** |
| DONE | 10 | 6 — leftover backlog integrated in tick 1, not window work |

**This run is void as a baseline.** Its six DONE are stock inherited from
earlier work, not throughput produced in the window, and with zero
`AGENT_EXITED` no width was ever sustained. It is reported here because a
number that looks plausible (6.353 DONE/h) would otherwise enter the record.

Two further faults, recorded separately because they are different in kind:

1. **My verification claim was not earned.** I reported REC-15 as verified by a
   green full gate. The suite was genuinely green and genuinely tested
   `run_bounded` — and was worthless for the command that actually runs an arm.
   The caller, `cmd_project_run`, referred to `skipped_final_tick` as a local
   after the extraction had moved it into the returned dict, raising
   `NameError` *after* 3400 s of completed work. Every test called the unit;
   none called the caller. Fixed in `ca442c8` by moving the reporting into
   `run_report_lines()` and asserting all four branches, including the exact
   3399.9 s case, which now prints a warning naming the true cause instead of
   raising. **The lesson generalises past this fix: a green suite over a unit
   is not evidence about its caller.**
2. **`pmk revoke` reports failure for work it performed.** Revoking the five
   orphaned leases recorded `REVOKED` for all five (09:45:56Z–09:46:02Z) and
   did release them, yet each returned `{"error": "no_lease"}` and exit 2. The
   command appears to release the lease and then fail to read it back for its
   own output. An operator trusting the exit code would conclude the revoke
   failed and the slot was still occupied. Not one of the REC items; logged
   here because it was hit in the course of this work and is unfixed.

Integrity was intact throughout: `pmk sentinel` returned `findings: []`, exit 0,
so **no OR-15 abort** applied.

---

### 9.3 The baseline-2 re-run: valid, and it disagrees with Arm-0b

> **CORRECTED per §14.4 (v1.3.1).** The figures originally published in this
> section were wrong. I analysed window `09:48:04 → 10:48:10`, but the baseline
> process exited at **10:32:50**; events from **10:44:42** onward belong to a
> *different* `pmk project run` — a foreign conductor started by another task's
> agent working in the same toy repository. It contributed 8 `CLAIMED` and 11
> `FLEET_BLOCKED` (13 + 8 = 21 and 24 + 11 = 35, which were this section's
> original pair). The cause of my error: I derived `--end` as *start plus a
> guessed duration*, so the analyzer's "measured window" was echoing my own
> input back to me rather than being read from the ledger. The values below are
> recomputed against the true process window and independently reproduced.
> **The 2.995 DONE/h figure in the original version is withdrawn.**

Voiding the first attempt was the right call, because the replacement produced
usable data. Launched 2026-11-12T09:48:04Z from `DONE 19 / READY 25 / 0 active
leases` — no inherited SUBMITTED backlog, which was the single cause of the
first run's collapse. It exited 0, and the new REC-15 warning fired as designed
(`one tick alone took 2675s, longer than the whole 1800s budget`).

| | Arm-0b (reference) | baseline-2 re-run (corrected) |
|---|---|---|
| window (measured) | 5860 s | **2684 s** (requested 1800, **OVERRAN ×1.49**) |
| CLAIMED | 22 | **13** |
| AGENT_STARTED / EXITED | — | **15 / 12** |
| LIVE peak ≥60 s | 10 | **10** |
| DONE | 10 | **3** |
| throughput | 6.143 DONE/h | **4.024 DONE/h** |
| denial | 38.9% | **64.9%** (24/37) |
| QUARANTINED | 3 | **0** |

Three things this settles, and one it unsettles.

**Settled: both arms reach live width 10.** Reproduced independently. The
lease-based figure in the same window was 12, so §5 is corroborated again:
leases overstate width. **Qualified by §14.1:** "reach" is not "bind". Live
level sat at 3 for 66% of this window and 10 for 25%; no `FLEET_BLOCKED` event
names a fleet cap. Neither arm *sustained* 10 as a steady state.

**Settled, and it is a process finding rather than a fleet one: another task's
agent was running `pmk project run` in this repository during my measurement.**
Isolation for these arms is `PYTHONPATH` + `--root` only, which does nothing
about a second process writing to the same `.pm` log. Every window computed
here must therefore be reconstructed from the log and checked for foreign
activity, not taken from wall-clock guesses.

**Unsettled: still not a replicate of Arm-0b — 4.024 vs 6.143 DONE/h and 64.9%
vs 38.9% denial.** The likely cause remains that **Arm-0b's headline number is
contaminated by the inherited-stock effect that voided the first baseline
run.** This run is the only measurement that began with a genuinely empty merge
queue, so **4.024 DONE/h is the cleanest throughput figure available** and 6.143
remains an upper bound pending re-derivation.

A secondary signal supports "the remaining cards are harder": 24 `FLEET_BLOCKED`
in this window, of which **16 were `attempts_exhausted`** — agents repeatedly
failing to complete their cards, which suppresses throughput independently of
width. Note that only 4 were `scope_overlap`, so §14.2's caution applies: this
headline is not the D-L6 scope-denial rate, which is 4/37 = 10.8%.

**Comparability caveat, stated because the analyzer raised it unprompted:**
these two runs overran their budgets by different factors (×3.26 vs ×2.00).
REC-16 normalises by the measured window, which is why both figures are given
per hour, but the tick structures differed and the comparison should carry that
qualification. It does **not** affect the Arm-A comparison, where both arms run
the same protocol against this baseline.

Integrity: `pmk sentinel` returned `findings: []`, exit 0 — **no OR-15 abort**.

---

## 10. Agent preflight checklist

An agent must satisfy every line before running any future arm. Each traces to a
recommendation.

1. **Isolation verified** — every call uses `--root <toy>` and `PYTHONPATH=<toy>\src`; nothing written to the live repository. (OR-01)
2. **Gate green on a clean base** — full `pytest -q` exits 0, assertions of REC-05 pass. (REC-05)
3. **Command correct** — the run that must reach `DONE` is `pmk project run`. (REC-06)
4. **Workload frozen** — gap-fill disabled or completion counted against the seeded set; card count recorded before and after. (REC-04)
5. **Width definition fixed** — live runs authoritative, lease figure reported alongside. (REC-02, REC-03)
6. **Requeue protocol fixed** — exactly **one** manual requeue before launch, at the matched point, for this arm and every arm it will be compared against; logged as an operator intervention. Automatic requeue stays **off** until all arms finish. (REC-17, D-79)
7. **Denial metric known** — `FLEET_BLOCKED` count, not `LEASE_REFUSED`. (REC-08)
8. **Terminal event known** — `INTEGRATED`. (REC-14)
9. **No `.pm/policy.toml` edit** — and if a policy change is ever considered, stop and escalate rather than proceed. (REC-09)
10. **Bounded-run span measured** — the actual window is taken from the log, compared with `--seconds`, and **throughput is divided by the measured window** at 6.14 DONE/h convention, never by the configured budget. An overrun is recorded, not silently absorbed. (REC-12, REC-15, REC-16)
11. **Analysis windowed and reconciled** — windowed counts asserted against a raw count. (REC-07)
12. **Operator interventions logged** — every manual action recorded, so metric 4 is honest. (§7.6)
13. **Abort condition live** — any I1 / I8' / I13 violation ends the arm immediately; sentinel checked before and after. (OR-15)

---

## 11. Conclusion

**The experiment remains valid, but only with fixes applied first.** The premise
survives: unrelaxed Arm-0 reaches sustained **10** live concurrent agents, below
OR-04's 12–20 band, so there is headroom for Arm A to demonstrate a difference
and the test retains discriminating power. But that conclusion is only reachable
after REC-01 (requeue), REC-02/03 (width measurement) and REC-04 (workload
freeze) are in place. Without them an arm measures recovery behaviour and lease
bookkeeping rather than the effect of removing write-scope gating — which is what
the first Arm-0 attempt actually did.

Nothing here ratifies a further change by itself. The one decision taken from
this analysis, **D-78**, is separately ratified by the operator and recorded in
the toy register.

## 12. Referenced evidence

- `docs/phase0-verification-2026-11-11.md` — D-01, D-02, O-01
- `docs/phase1-workload-2026-11-11.md` — workload shape, oracle proof, D-L6 probe
- `docs/baseline-correction-max-total-agents-2026-11-12.md` — `max_total_agents = 10` correction
- `docs/arm0-method-error-dispatch-vs-project-2026-11-12.md` — defect 1; withdrawn numbers
- `docs/arm0-evidence-green-run-2026-11-12.md` — defect 2 repair; Arm-0 metrics
- `docs/arm0b-evidence-requeue-2026-11-12.md` — defects 3 and 4; Arm-0b metrics
- `docs/baseline2-evidence-rederive-2026-11-12.md` — baseline-2 re-derived metrics, width distribution, cohort split, cleanup
- `pilot/decisions.md` — D-75, D-76, D-77, **D-78**, **D-79** (toy-only)
- Commits: `49ff873`, `534560d`, `e8d278a` (gate green), `8becbe1` (analyzer), `847bf41` (Arm-0b), `b95fabb` (D-78), `d135607` (this report v1.0.0)

---

## 13. Decisions taken arising from this report

Recorded in the toy register as **D-79** (2026-11-12, ratified by the operator),
following the options analysis above.

**13.1 Requeue — option A adopted.** For the duration of the experiment the
requeue stays **manual and matched**: exactly one requeue per arm, applied before
launch, applied to **every** arm that will be compared, and logged as an operator
intervention. Automatic requeue (wiring `Kernel.task_ready()` into the Conductor,
REC-01) is **deferred until all arms are finished**.

Reason: recovery was measured to be the dominant variable — one manual requeue
moved live width 3 → 10 and completions 3 → 10 with no configuration change. A
continuous automatic requeue in one arm and a single manual requeue in the other
would confound the comparison, and any width gain would be attributable to
recovery rather than to removing write-scope gating. The product fix and the
experimental control therefore pull in opposite directions, and the experiment
wins until the measurement is complete. Tracked as REC-17.

**13.2 Throughput denominator — measured window adopted.** Throughput is
**6.14 DONE/h** for Arm-0b, computed from the measured window (02:20:33Z →
03:58:13Z, 1.6278 h). The configured-budget alternative of 0.5 h would give
20.0 DONE/h and is **rejected as the reporting convention**; the two differ by
3.3×. This convention applies to every arm without exception, and window bounds
are recorded alongside every throughput figure. Tracked as REC-16.

Note the convention does not by itself make arms comparable: if a later arm
overruns by a materially different factor, the shared convention does not rescue
the comparison. REC-12 therefore remains mandatory.

**13.3 Still unresolved after these decisions.** U-02 through U-08 stand as
listed in §8. U-01 is resolved as to cause but its *remedy* (REC-15) is not yet
implemented, so every future run must still measure its own window rather than
trust `--seconds`.

---

## 14. Independent assessment (v1.3.0)

**Assessor:** opencode (`baidu/ernie-5.5-flash-preview:free`), 2026-11-12.
**Material assessed:** this report at v1.2.0, the five cited evidence records, the
toy decision register, the proposal, and the source and ledger they rest on.
**Method:** independent ledger recount (858 events at the time of review; 1,100
after baseline-2), source-line verification of every citation, and a full
`pytest -q` run (1,302 collected: 1,301 passed, 1 skipped, 0 failed, 18 m 50 s).

### 14.1 Corrections applied in this version

1. **§5.1 — cap binding.** The report said the 10 ceiling "binds" because
   observed live width equals it. The live series reaches 10 only in a 16 min
   20 s requeue burst, then sits at 8 for 75.5% of the window. No `FLEET_BLOCKED`
   event names a fleet cap. The claim is downgraded to "reached once; bindingness
   not established". Baseline-2 repeats the pattern (level 3 for 66%).
2. **§7.2 — merge conflicts.** The three `QUARANTINED` events are
   `attempts exhausted (3/3)` L4 worktree quarantines, not merge conflicts.
   Arm-0b's conflict baseline is **0/36**, not 3. U-06 and REC-11 are corrected
   accordingly.
3. **§7.4 — anomaly count.** The Arm-0 window holds 3 `IDENTITY_ANOMALY` events,
   not 8. The 8 are pre-window `dispatch run` events.

### 14.2 Further findings (recorded, not yet applied)

- **Code citations drift by 1–22 lines.** `cli.py:815` is `cmd_project_run` at
  **816**; the deadline loop is **838–842**, not 832–836. `conductor.py:673` is
  `tick()` at **674** (calls at 678, 682, 686). `models.py:46` is `INTEGRATING`;
  `REWORK → READY` is **47**. The toy `cli.py`/`conductor.py` have only the
  scaffold commit, so these were not shifted by a later edit; they appear to be
  copied from the live repository's files.
- **U-01's "resolved" is stronger than the evidence.** The mechanism is a code
  reading; the 1,882 s T-0005 lease is shorter than the 884 s overrun it is meant
  to explain. The stronger corroboration is already in the ledger: the
  `FLEET_BLOCKED` retry bursts are **74 min 45 s apart** (02:43:02 → 03:57:47),
  i.e. one full `conductor.tick()` + `dispatcher.tick()` cycle.
- **G-02 is mis-cited.** U-07 cites G-02 for "small sample"; proposal G-02 is
  "the merge queue can absorb overlap-driven conflicts". The small-sample caveat
  has no register ID.
- **The denial-rate definition is ambiguous.** Arm-0b's 14 `FLEET_BLOCKED` are
  7 distinct (task, blocker) pairs; 2 are `already satisfied on main`, not scope
  denials. Baseline-2's 24 are 16 `attempts_exhausted`, 4 `scope_overlap`, 4
  precheck. The 64.9% headline is not the D-L6 denial rate; the scope-denial
  rate is 4/37 = 10.8%.
- **`FLEET_BLOCKED` does not match its D-A1 text.** `dispatcher.py:106-114` says
  "once per (task, blocker) change", but `_start_backoff` resets `emitted` on
  every failed start, so it re-emits per retry round.
- **The Kernel-level scope refusal is silent.** `api.py:529` says every refusal
  is recorded as `LEASE_REFUSED` (N-15), but the `scope_overlap` path at
  `:553-557` raises without appending. The dispatcher's `FLEET_BLOCKED` is the
  only record.
- **OR-15's I13 limb is not enforced by the sentinel.** `STOP_INVARIANTS` is
  `("I1", "I3", "I6", "I8'")`; I13 is checked but reported as a non-stopping
  finding.
- **REC-01 is listed as active in §9 and deferred in §13.1.** The REC table has
  no status column. The §10 checklist also omits REC-10, REC-11 and REC-13;
  REC-10 is the one Arm A needs to test OR-07/D-76.
- **The merge queue is the proximate throughput limiter.** `drain_merge_queue`
  is serial; Arm-0b's eight integrations took ~75 min (~9.3 min/card), and
  baseline-2's three took ~44 min (~14.7 min/card). Raising `max_total_agents`
  may raise width without raising throughput.
- **Baseline-2 is not a seeded-only baseline.** 3 completions: 1 seeded
  (`T-0018`), 2 gap-fill (`T-0031`, `T-0036`). The workload is 44 (20 seeded + 24
  gap-fill). The freeze held for new cards (0 `TASK_CREATED`) but the gap-fill
  backlog is still being worked.
- **Baseline-2 had no requeue.** 0 `TASK_READY` in its window, so it is not
  matched to Arm-0b under REC-17/D-79. Recorded as a deviation.
- **The requeue has a cost.** Three of the eight requeued cards (T-0008, T-0009,
  T-0011) were on attempt 3 of 3 and exhausted; the requeue burned their last
  attempt. REC-17 should filter to cards with attempts remaining.

### 14.3 Verdict

The defect analysis in §1–§6 is sound and the six defect classes are real. The
measurement claims are not yet authoritative: the three corrections above change
the conflict baseline, the anomaly count and the cap-binding premise, and the
denial-rate and width definitions need to be fixed before any arm is compared.

**Conditions for a valid next arm**

1. D-79 recorded (done, `pilot/decisions.md:812-816`).
2. Conflict baseline corrected to 0/36 (done in §7.2).
3. Width definition fixed: report the live-level distribution, not only the
   max-held-≥60 s figure.
4. Denial definition fixed: `scope_overlap` only; report `attempts_exhausted`
   and precheck separately.
5. Workload frozen and the seeded subset counted separately (REC-04).
6. REC-10 implemented before Arm A (worker commit identity + provenance).
7. Clean base: 0 active leases, sentinel and pins clean, card count recorded.
8. Full gate green (1,301 passed, 1 skipped, 0 failed; 18 m 50 s).
9. Exactly one matched requeue per arm, with attempts-remaining filter (REC-17).
10. Throughput divided by the measured window, with the overrun factor recorded
    (REC-16/REC-12).

**Assessor's note on the gate.** The full `pytest -q` run at the time of this
assessment: **1,302 collected, 1,301 passed, 1 skipped, 0 failed** (18 m 50 s).
The gate is green; it is the measurement definitions, not the code, that block a
valid arm.

### 14.4 Baseline-2 window correction (v1.3.1)

§9.3 reports baseline-2 as **3,606 s, 21 CLAIMED, 35 `FLEET_BLOCKED`, 2.995
DONE/h, 62.5% denial**. That window is **contaminated by the next run**.

- The baseline-2 process started at **09:48:06Z** and exited at **10:32:50Z**
  (2,684 s; the REC-15 warning fired because one tick alone exceeded the 1,800 s
  budget).
- §9.3's 3,606 s window ends at **10:48:10Z**, which is 15 min 20 s **after** the
  process exited. The events from **10:44:42Z to 10:48:10Z** are the **next
  run's** first claims — 8 `CLAIMED` and 11 `FLEET_BLOCKED` — not baseline-2.
  13 + 8 = 21 and 24 + 11 = 35, which is exactly §9.3's pair.
- In the correct baseline-2 window (**09:48:06Z → 10:32:50Z**): **13 `CLAIMED`,
  24 `FLEET_BLOCKED`, 3 `DONE`, 4.024 DONE/h, 64.9% denial (24/37), 0
  `QUARANTINED`**. See `docs/baseline2-evidence-rederive-2026-11-12.md`.
- §9.3's "OVERRAN ×2.00" is really **×1.49** (2,684 / 1,800).
- The "21 ticks / one tick 2,675 s" pair is not independently verifiable from the
  ledger; the process ran 2,684 s. The tick count should come from the run's own
  `run_bounded` report, not from a ledger reconstruction.

The **clean-start** claim in §9.3 survives: the 09:48 run began with no
`SUBMITTED` backlog (the seven cards were returned to `READY` by the pre-run
cleanup), so its three completions were produced in-window. The error is the
window end, not the start.

The **width** claim needs the §14.1 qualification: "LIVE sustained 10" is the
max-held-≥60 s figure. Baseline-2's live level is **3 for 1,778 s (66% of the
window)** and **10 for 671 s (25%)**. Both runs reached 10, but neither sustained
10 as its steady state.
