---
document:
  title: "Arm-0b evidence — recovery was the bottleneck; width is 10, not 16"
  status: "Measured. Supersedes the width figure in the Arm-0 record."
  version: "1.0.0"
provenance:
  author_llm: {name: "Tencent HY4 Preview", version: "tencent/hy4-preview-free (orcarouter)"}
  assessor_llm: []
  created_date: "2026-11-12"
  scope: "Toy repository C:\\temp\\projects\\umaws-noscope-toy only"
authority_statement: "Evidence record. Authorises no change in either repository."
---

# Arm-0b — requeue run

Window **2026-11-12T02:20:33Z → 03:58:13Z**. Same configuration as Arm-0 —
**no relaxation applied**. The only difference is that the 8 cards parked in
`REWORK` were returned to `READY` by the operator through `Kernel.task_ready()`
before the run.

## 1. Result

```
arm                : ARM-0b
leases opened      : 22
CLAIMED events     : 22
FLEET_BLOCKED      : 14 {'scope_overlap': 12, 'already satisfied on main': 2}
claim attempts     : 36
tasks DONE         : 10
INCIDENT           : 0
peak concurrent    : 16        <- leases
LIVE peak concurrent: 10       <- agents actually running
LIVE sustained      : 10
wall hours         : 1.6278
throughput DONE/h  : 6.143
denial rate %      : 38.9
```

Side by side with Arm-0 (same windowing, same analyzer):

| Metric | Arm-0 | Arm-0b |
|---|---|---|
| tasks DONE | 3 | **10** (13 cumulative) |
| Throughput DONE/h | 5.55 | 6.14 |
| **Live sustained concurrency** | **3** | **10** |
| Lease concurrency (inflated) | 3 | 16 |
| Denial rate | 73.3 % | 38.9 % |
| INCIDENT | 0 | 0 |

## 2. Finding 1 — recovery, not scope gating, was the bottleneck

Live concurrency went **3 → 10** and completions **3 → 10** from one operator
action that changed no fleet configuration. Cause established in code:

- `Kernel.task_ready()` exists (`api.py:391`) but has **zero callers in `src`**
  — no fleet component and no CLI subcommand ever moves a card back.
- `models.py:46` permits `REWORK → READY`; `api.py:401` describes REWORK as
  returning a task "to READY for re-dispatch". The capability is implemented
  and never used.
- `dispatcher.py:233` dispatches only `state.ready_tasks()`, so a `REWORK` card
  is invisible to dispatch until something requeues it.

**This is upstream of everything Arm A changes.** If cards are not requeued,
neither arm can be measured for width, so Phase 3 must include an explicit
requeue step or both arms will reproduce Arm-0's misleading 3.

## 3. Finding 2 — width must be measured on live runs, not leases

Lease concurrency says 16; **live agent concurrency says 10.** A lease outlives
its agent — the kernel lease survives after the run object leaves
`dispatcher.self.runs` — so the lease figure counts agents that have already
exited. Reporting 16 as "concurrency" would have put Arm-0 inside OR-04's 12–20
target band and wrongly suggested the relaxations buy nothing. The analyzer now
prints both.

**Width for comparison purposes is the live figure: sustained 10.**

## 4. Finding 3 — `max_total_agents` is binding after all

This reverses a speculation I made after the previous run. I wrote that the cap
might not bind, because 15 leases had been observed under a cap of 10. That was
a lease-based observation and it was the wrong measure. On live runs:

- sustained live concurrency is **exactly 10**, equal to `max_total_agents = 10`.

So the cap **does** bind, and Arm A cannot reach OR-04's 12–20 without raising
it. **The `D-78` amendment request stands.** My earlier suggestion that no
amendment might be needed is withdrawn.

For accuracy on the earlier correction: `max_total_agents` *is* named in §7.2
(line 198, "Do **not** rely on `max_total_agents` alone"), which I previously
said was not the case. The precise gap is that §7.2 instructs raising
`max_concurrent` but never `max_total_agents`, so the ceiling stays at 10.

## 5. Conflicts and integrity

3 `QUARANTINED` events (T-0008, T-0009, T-0011), class `UNKNOWN`, on paths under
the repo root. These are merge conflicts and are the substance of §10.1 metric
3 — note they occur **with scope gating still on**. `INCIDENT` remains 0.

`pmk sentinel` → `{"ok": true, "findings": []}`. No I1 / I8' / I13 violation, so
**OR-15 never fired**.

## 6. Caveats carried forward

- **The workload grew mid-run: 20 → 34 cards.** All 14 new cards were created
  by the Overseer under agent id `overseer-gap-fill`, and 4 of them reached
  DONE (T-0021, T-0022, T-0025, T-0026). Throughput is therefore measured over
  an expanding workload, and **Arm-0 and Arm-0b are not strictly identical
  workloads**. Any Arm-A comparison must fix this — either disable gap-fill or
  count completions against the seeded 20 only.
- **The run spanned ~97 minutes although launched with `--seconds 1800`.**
  Cause not established; I used the measured window rather than 0.5 h. Flagged
  rather than resolved — do not assume future `--seconds` runs are 30 minutes.
- Throughput 6.14 DONE/h rests on 10 completions and 1 h of wall time; still a
  small sample (G-02).
