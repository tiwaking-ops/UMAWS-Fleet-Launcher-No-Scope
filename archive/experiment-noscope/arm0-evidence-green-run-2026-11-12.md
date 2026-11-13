---
document:
  title: "Arm-0 baseline evidence (green gate, windowed)"
  status: "Measured; Arm-0 complete. Two derived figures carried as caveated."
  version: "1.0.0"
provenance:
  author_llm: {name: "Tencent HY4 Preview", version: "tencent/hy4-preview-free (orcarouter)"}
  assessor_llm: []
  created_date: "2026-11-12"
  scope: "Toy repository C:\\temp\\projects\\umaws-noscope-toy only"
authority_statement: "Evidence record. Authorises no change in either repository."
---

# Arm-0 baseline — evidence record

Window: **2026-11-11T22:05:18Z → 22:37:44Z** (UTC), the first run after the
gate was made green in commit `e8d278a`. Command: `pmk project run --seconds
1800` (Conductor + Dispatcher + Overseer). The ledger is UTC; the commit
timestamp `2026-11-12 11:05:18 +1300` is the same instant.

Analyzer: `tools/analyze_arm.py --arm ARM-0-GREEN --start ... --end ...`

## 1. Measured output

```
window             : 85 of 539 events
leases opened      : 4
CLAIMED events     : 4
LEASE_REFUSED      : 0
FLEET_BLOCKED      : 11 {'scope_overlap': 11}
claim attempts     : 15
tasks DONE         : 3 ['T-0013', 'T-0014', 'T-0016']
INCIDENT           : 0
peak concurrent    : 3
sustained (>=60s)  : 3
wall hours (leases): 0.5406
throughput DONE/h  : 5.550
denial rate %      : 73.3
conflict+incident %: 0.0
```

## 2. Section 10.1 metrics

| Metric | Arm-0 value | Confidence |
|---|---|---|
| 1. Throughput | **3 cards DONE in 0.54 h = 5.55 DONE/h** | Measured, but see §3 — small sample |
| 2. Peak concurrent leases | **3, sustained >= 60 s** | Measured from lease pairs |
| 3. Conflict & incident rate | **INCIDENT 0; denial rate 73.3 % (11 of 15 claim attempts)** | Measured. Denials are D-L6 `scope_overlap` |
| 4. Operator effort per task | **0 interventions inside the window** | Measured — the run ran unattended |

Metric 4 needs the honest qualifier: **0 in-window**, but the *attempt* to get
here cost roughly seven operator actions (stopping the wrong loop, a `sweep`,
diagnosing the gate, generating the coverage artifact, restoring
`.githooks/pre-commit`, committing, and repairing the analyzer). All of it was
scaffolding repair, none of it coordination. Reporting "0" without that would
be misleading.

## 3. What this baseline does and does not establish

**It establishes** that cards can now reach `DONE` — three did, for the first
time in the experiment — and that D-L6 denial traffic is cleanly measurable
(11/11 `scope_overlap`; nothing else is denying claims).

**It does not establish a concurrency baseline.** Peak concurrent was **3**,
against `max_total_agents = 10` and the OR-04 target of 12–20. The fleet never
exercised width in this window, so **Arm A has no meaningful width to improve
on yet**. The cause is structural, not scope gating:

- `dispatcher.py:233` dispatches only `state.ready_tasks()`.
- Cards left in `REWORK` are therefore not re-dispatched. `recover.py:120`
  (L4) moves an attempts-exhausted card to `BLOCKED`.

End state `{BLOCKED: 5, REWORK: 8, DONE: 3, LEASED: 1, READY: 3}` fits that: the
three completions were cards already `LEASED`/`READY` at window start, and the
8 `REWORK` cards sat idle rather than being retried. **Throughput in this
system is bounded by recovery of failed cards, upstream of anything the
relaxations in Arm A change.** This is the most important finding of Arm-0 and
it is a property of the baseline, not of my harness.

Two smaller caveats, carried rather than resolved:

- **Throughput 5.55 DONE/h rests on 3 completions.** G-02.
- **No `SENTINEL_RUN` event occurs inside the window.** "Sentinel clean during
  the run" is inferred from a post-run `pmk sentinel`, not from in-run
  evidence.

## 4. Integrity

`pmk sentinel` → `{"ok": true, "findings": []}`, exit 0; `pmk pins check` →
`{"ok": true, "mismatches": []}`. No I1 / I8' / I13 violation, so **OR-15 never
fired**.

Note for the report: the sentinel's list prints `I8'`, which is **not a
typo for I8**. `policy.py:131` defines `I8'` as "pinned files match their
recorded hashes", and `sentinel.py:33` has `STOP_INVARIANTS = ("I1", "I3",
"I6", "I8'")`. So the abort condition named "I8" in OR-15 is the one the
sentinel actually enforces. (I initially suspected a missing check; that
suspicion was wrong and is withdrawn here.)

## 5. Analyzer defects found and fixed

Two bugs in `tools/analyze_arm.py` were producing wrong published numbers and
are fixed as part of this commit:

1. **Windowing was applied to lease intervals only.** With `--start/--end` the
   headline counters still read the whole 539-event log, reporting 40 `CLAIMED`
   and 55 `FLEET_BLOCKED` for a window that contains 4 and 11. The window is
   now applied once to a filtered list that every counter reads. Post-fix the
   counters reconcile exactly with a hand count of the window.
2. **`TASK_DONE` was treated as terminal.** This pipeline emits `INTEGRATED`
   and never `TASK_DONE`, so the analyzer printed `throughput DONE/h: 0.000`
   for a run that completed 3 cards. Terminal is now `INTEGRATED` (also added
   to the lease-closing set), counted as **distinct subjects** so a card
   emitting both is not double-counted.
3. Throughput is now divided by **arm wall time** when a window is given, not
   by an implicit lease span that inflates the denominator with idle time.

## 6. Still open

- **`max_total_agents` is not in Arm A's §7.2 change list**, but today's value
  is 10 and OR-04 targets 12–20. Phase 3 cannot reach 12–20 without changing
  it. Needs operator ratification.
- **`IDENTITY_ANOMALY` ×3 in-window** (T-0013, T-0014, T-0016): each worker
  commit was auto-pinned from `Tiwa Pene <tiwaking@gmail.com>` to
  `umaws-pilot <umaws-pilot@localhost>` at stage `commit`. This bears directly
  on the proposal's worker-commit identity + provenance-trailer requirement —
  commits do not currently carry per-agent identity.
