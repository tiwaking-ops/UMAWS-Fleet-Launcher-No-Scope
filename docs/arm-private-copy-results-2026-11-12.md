---
document:
  title: "Private-copy arm results: cap 10 vs cap 20"
  status: "First pair voided by poisoned supply. Second pair: control running."
  version: "1.1.0"
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
to the cap-10 copy. Window reconstructed from its own ledger: start marker
**12:08:29Z**, last event **12:37:54Z** = **1765 s**, matching the run's own
report exactly.

```
CLAIMED            : 3
AGENT_STARTED      : 3
AGENT_EXITED       : 3
INTEGRATED         : 2
tasks DONE         : 2   (T-0019, T-0043)
LIVE peak          : 2
LIVE sustained     : 2
throughput         : 4.079 DONE/h
denial             : 95.5%  (63 / 66 attempts)
INCIDENT           : 0
QUARANTINED        : 0
sentinel findings  : []   (exit 0)
```

## 4. Cap 10 vs cap 20

| | cap 10 (control) | cap 20 (Arm A) |
|---|---|---|
| window (measured) | 1425 s (0.79 of budget) | 1765 s (0.98 of budget) |
| ticks | 59 | 57 |
| CLAIMED | 3 | 3 |
| AGENT_STARTED / EXITED | 3 / 3 | 3 / 3 |
| tasks DONE | 2 (T-0019, T-0043) | 2 (T-0019, T-0043) |
| LIVE peak | 2 | 2 |
| LIVE sustained | 2 | 2 |
| throughput | 5.053 DONE/h | 4.079 DONE/h |
| denial | 95.1% (48/61) | 95.5% (53/66) |
| `attempts_exhausted` | 48 | 53 |
| INCIDENT / QUARANTINED | 0 / 0 | 0 / 0 |
| sentinel | `[]` exit 0 | `[]` exit 0 |

**The two arms are the same run.** Identical claims, identical width, and even
the same two cards completed. No `FLEET_BLOCKED` in either window names a fleet
cap, and neither arm ever had more than 2 agents alive, so **the cap was not
reached at 10 or at 20**.

Throughput differs (5.053 vs 4.079) only because both completed 2 tasks in
different measured windows; on two samples each, that gap is noise, not signal.

## 5. Verdict: D-78 is not answered by this pair

The question was whether raising the cap from 10 to 20 increases sustained width
and throughput. These arms cannot answer it, and the reason is not the cap — it
is that **the card pool was already poisoned before either arm launched** (§1.1):
16 cards carried an exhausted attempt counter inherited from earlier aborted
runs, leaving only a handful of dispatchable cards. With supply limited to about
3 claims, the ceiling is irrelevant, exactly as a fleet of 2 cannot test the
difference between 10 and 20.

So this pair shows **no evidence either way**, and the tempting reading — "raising
the cap made no difference, therefore the cap does not bind" — is **not
supported**. What is supported is narrower and still useful: under this card
pool, neither cap value was approached.

**To actually test D-78**, the attempt counters must be reset in both copies and
both arms re-run, symmetrically. That is a further intervention beyond the single
requeue D-79 permits per arm, so it is not done here; it is a decision for the
operator. Note the confound that would remain even then: 22 of 44 cards are
already DONE, so a wider fleet may still starve for tractable cards rather than
reach 20.

## 6. Second operator intervention - supply restored, then re-run

The operator authorised: *reset the attempt counters in both copies and re-run
both arms symmetrically*.

### 6.1 What was actually done, and where it departs from the authorisation

**The counters cannot be reset, and this is stated plainly because "reset" is
what was approved.** `card.attempt` is not a stored field. It is a projection
over the event log, incremented on every `CLAIMED` event
(`src/pmk/state.py:137`):

```python
elif etype == "CLAIMED":
    card.attempt = int(payload.get("attempt", card.attempt + 1))
```

Nothing decrements it. `TASK_READY` clears `block_reason` but not `attempt`, and
no `pmk` verb - `task`, `queue`, `fleet`, `project` - exposes a reset. The only
remaining routes were to rewrite `.pm` history by hand (forbidden: the Kernel is
the only writer) or to give the fleet **new cards**, which start at attempt 0.

The second route was taken. In each copy, identically and in the same order, 24
cards were created through `pmk task create` (`T-0045`..`T-0068`), each with a
write scope that does not yet exist, the standard oracle
`python workload/check.py <file> TOY-OK`, `RESULT.md` as evidence, `attempts.max
= 3`, and no dependence on any other card.

So the operator's intent - restore dispatchable supply so the cap, not the
queue, decides width - is met, but by **substitution rather than reset**. The 27
cards carrying inherited exhaustion remain in the ledger, BLOCKED in both copies,
and generate the same refusal noise in both. Their presence is symmetric and is
left alone rather than voided, to keep the intervention minimal.

### 6.2 Symmetry of the re-run start state

Verified element-wise, not by comparing hash values: an earlier check printed a
differing `ids hash` between the two copies, which was meaningless because
Python salts string hashes per process. Compared directly instead:

```
same task id set  : True     (68 vs 68)
state mismatches  : none
attempt mismatches: none
claimable equal   : True     cap10 = 27, cap20 = 27
```

Normalised per `docs/arm-isolation-private-copy-2026-11-12.md` §3: all 25 leases
in each copy were already expired (no active lease to release), and the one task
not `READY`/`DONE` was `T-0020` in **both**, moved to `READY` in both. Both then
reported:

```
DONE 24, READY 44, claimable 28
```

28 claimable against a cap of 20 is a 1.4x supply ratio, and against a cap of 10
is 2.8x. Supply now exceeds the ceiling in both arms, so any observed ceiling is
the cap rather than the queue - the condition the first pair failed to meet.

### 6.3 Third confound declared in advance

24 of the 28 claimable cards are newly written toy cards whose oracle is "create
a file containing `TOY-OK`". They are trivially satisfiable, so absolute
throughput in this pair will run far above the first pair's ~4-5 DONE/h and is
**not comparable to it**. The comparison that survives is cap 10 vs cap 20
*within* this pair, where both arms face the same cards.

---

## 7. Re-run results

### 7.1 Control arm - cap 10

Root `C:\temp\projects\toy-arm-cap10`. Launched **20:24:00Z**. Window
reconstructed from its own ledger: first event **20:24:02Z**
(`OVERSEER_WOKEN`), last **22:14:14Z** = **6612 s**, agreeing with the run's own
report of 6613 s.

**This arm overran its budget by x3.67** (6612 s measured against 1800 s
requested), and one single tick consumed 5655 s of that - 86% of the entire
window in one tick. The run emitted its own warning:

```
WARNING: one tick alone took 5655s, longer than the whole 1800s budget.
No deadline logic can bound that - the conductor must be bounded
(REC-15, unimplemented half).
```

```
CLAIMED            : 25      (was 3 in the first pair)
AGENT_STARTED      : 32
AGENT_EXITED       : 25      -> 7 never exited
INTEGRATED         : 9
tasks DONE         : 9   T-0020, T-0045..T-0052
LIVE peak          : 10
LIVE sustained     : 10
throughput         : 4.900 DONE/h
denial             : 69.5%  (57 / 82 attempts)
INCIDENT           : 0
QUARANTINED        : 0
sentinel findings  : []   (exit 0)
```

**The cap bound this arm, and this time it can be said precisely.** Concurrency
was reconstructed stepwise from every `AGENT_STARTED`/`AGENT_EXITED` pair in the
window (not from lease records, which are inflated by leases that were never
released):

```
>=  2 concurrent :  98.5% of window
>=  5 concurrent :  95.9%
>=  8 concurrent :  93.7%
>= 10 concurrent :  92.4%
>= 11 concurrent :   0.0%     <- never exceeded the cap
max concurrency  :  10
```

Width **never exceeded 10 and sat at 10 for 92.4% of the window**. That is the
first clean evidence in this experiment that the cap is what sets width, and it
is why the first pair was uninformative: with only 3 claimable cards the fleet
could not reach 10 no matter what the ceiling was.

Two things qualify it. First, 7 of 32 agents never exited, so lease-based
concurrency reads 19 - the dispatcher limits *live runs* (`len(self.runs) >= cap`
in `fleet/dispatcher.py:270`), while leases of dead agents linger; the stepwise
figure above is the honest one. Second, the 4.900 DONE/h must not be read as an
improvement over the first pair's 5.053: the cards here are trivially satisfiable
and the denominators are wildly different.

### 7.2 Third operator intervention - orphaned agents killed

When the control conductor exited, **an agent tree outlived it**: `hermes.exe`
(PID 18536) with a `python.exe` child (PID 10928) still working T-0067, plus a
`cline.exe` hub daemon (PID 9740) bound to `toy-arm-cap10/work/T-0051-108`, all
started during the window and still alive afterwards. This is the
never-exited-agent pathology observed directly rather than inferred from counts.

They were killed before the cap-20 arm launched, because agents left running into
the next arm would contend for the machine and bias the throughput comparison
the arms exist to make - and because they belong to an arm whose window had
already closed. Recorded here as an intervention: it is a third one, beyond the
requeue D-79 permits and beyond the card creation authorised in §6. Their being
killed does not affect the cap-10 figures, which are window-bounded and were
computed before the kill.

### 7.3 Arm - cap 20

Launched **22:19:05Z** from the identical normalised start state (DONE 24, READY
44, claimable 28), after verifying no process was bound to either arm root.
Result pending.
