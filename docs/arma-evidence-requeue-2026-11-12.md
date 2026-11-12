---
document:
  title: "Arm A evidence - pre-launch intervention and starting state"
  status: "Pre-launch record. Result pending."
  version: "1.0.0"
provenance:
  author_llm: {name: "Tencent HY4 Preview", version: "tencent/hy4-preview-free (orcarouter)"}
  assessor_llm: []
  created_date: "2026-11-12"
  scope: "Toy repository C:\\temp\\projects\\umaws-noscope-toy only"
authority_statement: "Evidence record. Authorises no change in either repository."
---

# Arm A - pre-launch intervention record

This documents everything done to the toy repository between the end of the
baseline-2 run and the launch of Arm A, so that the difference between the two
arms is auditable. Written because D-79 requires each arm's requeue to be
logged as an operator intervention rather than absorbed silently.

## 1. What was changed before launch

Two interventions, deliberately distinguished because they are different in
kind. Only the second counts against D-79's "one matched requeue per arm".

**Recovery (not a requeue).** The baseline-2 run ended with 8 cards still
`LEASED`, because their agents were in flight when the budget ran out and never
exited. Those leases were released with `pmk revoke`:

```
T-0019,81  T-0035,82  T-0037,83  T-0038,84
T-0039,85  T-0040,86  T-0041,87  T-0042,88
```

`REVOKED` written 2026-11-12T11:06:22Z - 11:06:28Z. This is crash/end-of-run
recovery of dead agents, not replenishment of workload, so it is not the D-79
requeue. It is recorded anyway because it moves cards between states.

*Note on tooling:* `pmk revoke` performs the release and then reports
`{"error": "no_lease"}` with exit 2. Every one of the 8 appeared to fail and all
8 succeeded. Verification here is by the `REVOKED` events, not the exit code.

**The D-79 requeue for Arm A.** After recovery, 2 cards sat `BLOCKED`
(`T-0032`, `T-0035` - the latter having gone to `BLOCKED` when its lease was
revoked). Both were returned to `READY` via `Kernel.task_ready()`. This is the
single requeue D-79 allows for this arm.

## 2. Starting state at launch

```
task states   : DONE 22, READY 22
active leases : 0
fleet_cap     : 20        (agents.toml reinstated to the D-78 value)
```

Launch marker written to `tmp/arma_start.txt`.

Alongside the baseline for comparison:

| | baseline-2 re-run | Arm A |
|---|---|---|
| cap | 10 | 20 |
| READY at launch | 25 | 22 |
| supply / cap ratio | 2.5x | 1.1x |
| active leases at launch | 0 | 0 |

**Supply caveat, stated before the result is known.** The baseline launched with
2.5x more ready cards than its cap could admit; Arm A launches with only 1.1x.
22 is the maximum available - the frozen workload has 44 cards and 22 are
already `DONE`, so the ratio cannot be matched by adding work. If Arm A fails to
reach or sustain width 20, that may be supply starvation rather than the cap
failing to permit it, and the two must not be confused. Cards do recycle during
a run (21 claims arose from 56 attempts in the baseline), so the shortage is
less severe than the raw ratio suggests, but it is real and it is a confound
in Arm A's favour specifically when it does *not* reach 20.

## 3. Standing result for comparison

Baseline-2 re-run (cap 10), window 2026-11-12T09:48:04Z - 10:48:10Z:

```
window (measured) : 3606 s  (requested 1800, OVERRAN x2.00)
ticks             : 21
AGENT_EXITED      : 15
LIVE sustained    : 10
DONE              : 3
throughput        : 2.995 DONE/h
denial rate       : 62.5%
QUARANTINED       : 0
```

Full analysis in `docs/incident-arm0-measurement-2026-11-12.md` section 9.3,
including the unresolved discrepancy against Arm-0b's 6.143 DONE/h.
