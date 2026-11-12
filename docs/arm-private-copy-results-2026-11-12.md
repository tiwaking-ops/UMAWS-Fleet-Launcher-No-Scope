---
document:
  title: "Private-copy arm results: cap 10 vs cap 20"
  status: "Control measured. Arm pending."
  version: "1.0.0"
provenance:
  author_llm: {name: "Tencent HY4 Preview", version: "tencent/hy4-preview-free (orcarouter)"}
  assessor_llm: []
  created_date: "2026-11-12"
  scope: "Toy experiment only. Nothing here applies to the live repository."
authority_statement: "Evidence record. Authorises no change in either repository."
---

# Private-copy arm results

Each arm runs in its own repository copy, so its ledger can only be written by
its own conductor (`docs/arm-isolation-private-copy-2026-11-12.md`). Windows are
reconstructed from each copy's own event log, never from a clock guess.

## 1. Control arm - cap 10

Root `C:\temp\projects\toy-arm-cap10`. Start marker **11:38:58Z**, last ledger
event **12:02:43Z**; window **1425 s**, confirmed against the run's own report of
1424 s measured. The run stopped **early** at 0.79 of the requested 1800 s
budget, because REC-15 refused to start a further tick that would outlive the
budget - the guard working as designed, after 59 ticks.

```
CLAIMED            : 3
AGENT_STARTED      : 3
AGENT_EXITED       : 3
INTEGRATED         : 2
tasks DONE         : 2   (T-0019, T-0043)
LIVE peak          : 2
LIVE sustained     : 2
throughput         : 5.053 DONE/h
denial             : 95.1%  (58 / 61 attempts)
INCIDENT           : 0
QUARANTINED        : 0
sentinel findings  : []   (exit 0)
```

**The headline of this run is not its throughput.** It is that the cap was never
approached: live width peaked at **2 against a ceiling of 10**. This arm
therefore does not reproduce the earlier "reaches 10" result, and it cannot by
itself settle whether raising the cap changes anything - a fleet that never
exceeds 2 cannot test the difference between 10 and 20.

The reason is visible in the denial breakdown rather than in the cap:

```
attempts_exhausted                       48
already satisfied on main (c21, c22)      6
uncommitted changes (workload/c42)        3
scope_overlap                             1
                                         58
```

### 1.1 What the 48 `attempts_exhausted` blocks actually are - corrected

~~Cards are failing on their own merits~~ — **this was wrong when first written
and is corrected below with cause.** `attempts_exhausted` is the **L4 rung** of
the recovery ladder (`src/fleet/recover.py:121`): it fires when
`attempt >= attempts_max` (3), and that counter **accumulates across runs** — it
lives on the task, not on the run. So the blocker reports a budget spent
*earlier*, not a failure happening now.

All 48 blocks are **16 cards × exactly 3 blocks each**, and none of those 16 got
a single `AGENT_STARTED` in this window. Their whole-history evidence:

```
never exited (started but no AGENT_EXITED)   20
AGENT_FAILED   -> UNKNOWN 9, NO_CHANGES 1     10
INFRASTRUCTURE_FAILED (integration)            6
reached the oracle gate at all                 4
ever INTEGRATED                                0
```

**So: the models are not failing, and neither are the cards on merit.**

- **No model-side failure class exists anywhere in the ledger.** Every
  `AGENT_FAILED` in the entire history is `UNKNOWN` (22) or `NO_CHANGES` (4).
  There is not one `QUOTA`, `AUTH`, `MODEL_GONE` or `CRASH`. Nothing shows the
  model refusing, being unavailable, or erroring.
- **The dominant signature is agents that started and never exited** — 20 of them
  across these 16 cards, and 38 across the whole ledger (115 started vs 77
  exited). That is the same pathology already documented twice: runs overrunning
  their budget, a single tick eating 3399.9 s, and the REC-15 `NameError` crash
  that killed five agents mid-flight. The agents were **cut off when their parent
  run ended**, not defeated by the work.
- Where a class was recorded it is `UNKNOWN` ("unrecognised failure") or
  `NO_CHANGES` (the agent ran and produced no edits) — i.e. uninformative, and
  consistent with being killed rather than with a reasoned refusal.

**Consequence, and it changes the reading of this arm.** The attempt counters
were consumed by *aborted runs*, then the private copy inherited them, so the
fleet refused those cards 3× each and produced 48 blocks that read like failures
but are inherited exhaustion. Section 1's claim that "supply of tractable cards"
limited the run is therefore **not established**: the low width is largely an
artifact of a poisoned card pool, not evidence that a cap of 10 is not binding.
Resetting the attempt counters and re-running would be needed to test that — and
that is a further intervention beyond the single requeue D-79 permits per arm, so
it is left to the operator.

Throughput (5.053 DONE/h) is computed from **2 completed tasks** and should be
read as noise-dominated; it is reported because REC-16 requires the measured
denominator, not because two samples carry much information.

## 2. Known confounds, both checked rather than assumed

- **Untracked `workload/c42-fog-of-war.md`.** Both copies inherited this file
  from the original tree, and it is named by 3 blocked claims. It is present
  identically in both copies, so it costs each arm roughly equally and does not
  bias the comparison. It does suppress claims in absolute terms.
- **`agents.toml` differs only in the cap-10 copy**, where it was deliberately
  restored to the pre-D-78 value, leaving that copy's tree staged-dirty. Nothing
  blocks on that file, but it is the one asymmetry between the two copies.
- **21 of 22 remaining cards recycled repeatedly** (61 attempts produced 3
  claims), so the arms are partly measuring retry behaviour rather than fresh
  dispatch.

## 3. Arm A - cap 20

Root `C:\temp\projects\toy-arm-cap20`. Launched **12:08:29Z**, identical
protocol (`--seconds 1800`). Isolation verified at launch: exactly one conductor
(PID 6504) plus its `pmk.exe` shim child, both bound to that copy, nothing bound
to the cap-10 copy.

Result pending.
