---
document:
  title: "Baseline-2 evidence — re-derived from the ledger after the REC-15 crash"
  status: "Measured. Re-derived from the ledger; the run itself printed no report because it exited on the REC-15 NameError. Supersedes the discarded first baseline-2 attempt."
  version: "1.0.0"
provenance:
  author_llm: {name: "opencode", version: "baidu/ernie-5.5-flash-preview:free"}
  assessor_llm: []
  derived_from: "baseline-2 run, `pmk project run --seconds 1800`, started 2026-11-12T09:48:04Z (tmp/baseline2_start.txt); run authored by Tencent HY4 Preview"
  created_date: "2026-11-12"
  scope: "Toy repository C:\\temp\\projects\\umaws-noscope-toy only"
authority_statement: "Evidence record. Authorises no change in either repository. Derived from the ledger, not from a run report (the run printed none)."
---

# Baseline-2 evidence — re-derived

## 1. What this run was

The second baseline-2 attempt, launched after the first attempt died on the
`REC-15` `NameError` fixed in `ca442c8`.

- Start marker: **2026-11-12T09:48:04Z** (`tmp/baseline2_start.txt`).
- Process window: **09:48:06Z → 10:32:50Z** (2,684 s).
- Budget: **1,800 s**. Measured: **2,684 s** — **1.49× the budget**, an
  **884 s overrun**. `REC-15` is only the loop half: it refuses to *start* a
  tick that would outlive the budget, but it cannot interrupt a tick already
  running. One tick of 884 s is the irreducible overshoot.
- No requeue: **0 `TASK_READY`** events in the window. This run therefore does
  **not** match Arm-0b's one-requeue protocol (REC-17 / D-79). Recorded as a
  deviation, not silently absorbed.

The **first** baseline-2 attempt (start 08:33:22Z) is discarded: it did ~3,400 s
of work and exited 1 on the `NameError` before printing anything. Its events
remain in the ledger but are outside the window below and are not used.

## 2. Measured metrics

Analyzer: `python tools/analyze_arm.py --arm BASELINE-2 --start 2026-11-12T09:48:06Z --end 2026-11-12T10:32:50Z --requested-seconds 1800`

```
window             : 152 of 1100 events
leases opened      : 13
CLAIMED events     : 13
LEASE_REFUSED      : 0
FLEET_BLOCKED      : 24 {'attempts_exhausted': 16, 'scope_overlap': 4,
                        'already satisfied on main (T-0023)': 2,
                        'already satisfied on main (T-0024)': 2}
claim attempts     : 37
tasks DONE         : 3 ['T-0018', 'T-0031', 'T-0036']
INCIDENT           : 0
QUARANTINED        : 0
peak concurrent    : 12        <- leases
LIVE peak concurrent: 10       <- agents actually running
LIVE sustained      : 10       <- max level held >= 60 s
wall hours (measured): 0.7456  <- REPORTING DENOMINATOR
throughput DONE/h  : 4.024
denial rate %      : 64.9      <- all blockers, see §4
conflict+incident %: 0.0
```

**Live-width distribution** (the figure the headline hides):

| Live agents | Seconds | Share of window |
|---:|---:|---:|
| 3 | 1,778 | 66.2% |
| 10 | 671 | 25.0% |
| other (1,2,4–9) | 235 | 8.8% |

So the fleet spent **two-thirds of the run at 3 live agents**, reached 10 only
for the last ~11 minutes, and never exceeded 10. "Sustained 10" is the
max-held-≥60 s definition, not the steady state.

## 3. Completions by cohort

The workload is **44 cards**, not the seeded 20: 20 seeded (`T-0001`…`T-0020`)
plus 24 gap-fill (`T-0021`+). The REC-04 freeze held for this run — **0
`TASK_CREATED`** in the window — but the existing gap-fill backlog was still
being worked.

| Cohort | Completed in this run |
|---|---|
| Seeded `T-0001`…`T-0020` | **1** (`T-0018`) |
| Gap-fill `T-0021`+ | **2** (`T-0031`, `T-0036`) |

The run is therefore **not a seeded-only baseline**. Any comparison with Arm-0b
must either count the seeded subset only (Arm-0b: 6 of 10 completions were
seeded) or state the cohort split explicitly.

## 4. Denial-rate caveat

`64.9%` is `24 / 37` and is dominated by **`attempts_exhausted` (16 of 24)** —
the eight READY-but-attempt-exhausted cards (`T-0001/2/3/8/9/10/11/15`) being
retried every tick. It is not a D-L6 scope-denial rate.

- Scope denials: **4 / 37 = 10.8%**.
- Precheck-satisfied (not denials): 4.
- Attempt-exhausted blocks (not denials): 16.

REC-08's "denial is `FLEET_BLOCKED{scope_overlap}`" is the right definition;
the 64.9% headline is not that metric.

## 5. What the run establishes, and what it does not

**Establishes**

- The pipeline can still complete cards after the `REC-15` fix: three integrated,
  zero incidents, zero quarantined conflicts. (No in-run gate result was captured;
  the full gate was verified green after the run: 1,301 passed, 1 skipped,
  0 failed, 18 m 50 s.)
- The `REC-15` loop bound is partial but observable: the run overran by 884 s,
  which the analyzer flags (`OVERRAN, x1.49 of budget`), and the measured window
  is used for every per-hour figure (REC-16).

**Does not establish**

- A width baseline. The fleet was at 3 for 66% of the window; the 10 is a
  short burst. The cap-binding claim in §5.1 of the incident report is not
  supported by this run either.
- A recovery-controlled comparison. There was no requeue, so this run is not
  matched to Arm-0b (REC-17).
- A seeded-only workload comparison. Two of the three completions are gap-fill.

## 6. Post-run cleanup (recorded)

The run exited leaving **10 open leases** and nine live agent processes. All
were reaped through the Kernel:

- `pmk agent stop` on T-0032, T-0035, T-0037…T-0044 (all already exited).
- `pmk revoke` on fences 70, 71, 73–80 → new fence 81.
- Eight dirty worktrees reclaimed to `stranded/` (T-0035-71, T-0038-74,
  T-0039-75, T-0040-76, T-0041-77, T-0042-78, T-0043-79, T-0044-80).
- Clean worktrees pruned: **61 → 12** (684 MB → 104 MB).
- Active leases: **0**.
- `pmk sentinel` → `ok: true`; `pmk pins check` → `ok: true, mismatches: []`.

**Side effect to record:** revoking the ten leases returned the **seven
`SUBMITTED` cards to `READY`**. Their work is preserved in the reclaimed
worktrees and bundles, but they are no longer `SUBMITTED`; the next run will
re-dispatch them. This is a consequence of reaping a crashed run, not a
measurement result.

## 7. Reproduce

```
pmk status
python tools/analyze_arm.py --arm BASELINE-2 \
  --start 2026-11-12T09:48:06Z --end 2026-11-12T10:32:50Z \
  --requested-seconds 1800
pmk sentinel
pmk pins check
```

## 8. Next-arm protocol (REC-16 / REC-17)

**REC-16 — measured window.** Throughput is `DONE / measured window`, never
`DONE / requested budget`. Record three numbers with every figure: the window
start/end, the measured seconds, and the overrun factor (`measured / requested`).
Baseline-2's overrun factor is **1.49**; do not compare its per-hour figure
against an arm with a materially different factor (REC-12).

**REC-17 — one matched requeue.** Exactly **one** manual requeue per arm, applied
before launch, applied to every arm that will be compared, logged as an operator
intervention (metric 4). Filter to cards with **attempts remaining**: the Arm-0b
requeue burned the last attempt of T-0008, T-0009 and T-0011, which then
terminated. Automatic requeue stays off until all arms are finished (D-79).

**Cohort rule.** Count completions against the **seeded 20** separately from the
gap-fill cards. Baseline-2 is 1 seeded + 2 gap-fill; Arm-0b is 6 seeded + 4
gap-fill. Report both, and do not present the total as a seeded-only figure.

**Clean-base rule.** Before the next arm: 0 active leases, sentinel and pins
clean, card count recorded, and the seven `SUBMITTED` cards returned to `READY`
by the baseline-2 cleanup either re-dispatched or explicitly excluded.