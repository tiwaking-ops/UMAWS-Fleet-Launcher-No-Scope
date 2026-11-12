---
document:
  title: "UMAWS no-scope experiment - final report: concurrency cap 10 vs 20"
  status: "Drafted for operator ratification. Measurement complete; recommendations carry no force until ratified."
  version: "1.0.0"
provenance:
  author_llm: {name: "Tencent HY4 Preview", version: "tencent/hy4-preview-free (orcarouter)"}
  assessor_llm: []
  created_date: "2026-11-13"
  scope: "Toy repository C:\\temp\\projects\\umaws-noscope-toy and its two private arm copies only. Nothing here applies to the live repository C:\\temp\\projects\\testproject1."
authority_statement: "Evidence record plus advisory recommendations. Authorises no change in either repository. Not independently assessed."
---

# Report: does raising the concurrency cap from 10 to 20 increase sustained width and throughput?

**Document Type**: Formal Project Documentation
**Purpose**: Close out the no-scope cap experiment raised under decision **D-78**, record every measurement with the window it came from, and supply the recommendations, safeguards and protocol improvements on which **future experiments in this system** should be based
**Audience**: The operator, and any agent designing or running the next experiment in this system
**Author (author_llm)**: Tencent HY4 Preview — `tencent/hy4-preview-free (orcarouter)`
**Assessor (assessor_llm)**: *none — this report is unassessed.* Independent assessment is requested before ratification. The author has not assessed its own work, and no other model has reviewed it.
**Date**: 2026-11-13
**Status**: Drafted for operator ratification
**Repositories touched**: `C:\temp\projects\umaws-noscope-toy` and its two private arm copies only. The live repository was not read for results and not written. Nothing was pushed from anywhere; the toy repository has **no git remote**.

---

> **UNASSESSED — READ THIS FIRST**
>
> This report is signed by its author only. It has **not** been independently assessed, and the author does not assess its own work. Every quantitative claim below was re-derived from the event ledgers in the session that produced this report (see [Appendix A](#appendix-a--re-deriving-every-number)), but re-derivation is not assessment: it catches transcription drift, not reasoning error. Independent assessment is requested before any recommendation here is ratified.

---

## Table of contents

1. [Executive summary](#1-executive-summary)
2. [Metadata, provenance and compliance](#2-metadata-provenance-and-compliance)
3. [Method](#3-method)
4. [Results](#4-results)
5. [Why the first pair was uninformative](#5-why-the-first-pair-was-uninformative)
6. [Corrections register — the honesty trail, inline](#6-corrections-register--the-honesty-trail-inline)
7. [Findings](#7-findings)
8. [Verdict on D-78](#8-verdict-on-d-78)
9. [Draft decision records D-80 and D-81](#9-draft-decision-records-d-80-and-d-81)
10. [Recommendations REC-18 to REC-29](#10-recommendations-rec-18-to-rec-29)
11. [Mandatory pre-launch checklist for future experiments](#11-mandatory-pre-launch-checklist-for-future-experiments)
12. [Unresolved issues and follow-up experiment options](#12-unresolved-issues-and-follow-up-experiment-options)
13. [Applicability and transfer candidates](#13-applicability-and-transfer-candidates)
14. [Appendices](#14-appendices)

---

## 1. Executive summary

The experiment asked whether raising the fleet concurrency ceiling (`fleet.max_total_agents`) from 10 to 20 increases sustained concurrent agents and throughput.

**Width: yes, answered positively.** In the second pair of runs, cap 10 sustained exactly **10** concurrent agents (never 11; at 10 for 92.4% of its 6612 s window) and cap 20 sustained **20** (never more; at 20 for 56.2% of its 1550 s window). Each arm pinned to its own ceiling and neither exceeded it by one. Raising the cap doubled sustained width.

**Throughput: not answered, and the reason is now visible rather than guessed.** Agents at cap 20 *produced* finished work about **4.5× faster** (44.129 distinct SUBMITTED/h vs 9.800), but work *landing* was flat (4.645 vs 4.900 INTEGRATED/h). At window close the cap-20 copy held **17 tasks SUBMITTED and only 2 landed**, against the control's 8 submitted. The binding constraint moved from dispatch width to the serial integration gate. Answering "does wider finish more work" is therefore a question about integration throughput, not about the cap.

**Headline recommendation: raise the cap, fix integration next.** Width follows the cap and is now measured, so if the goal is reachability the cap should follow the target width. But the cap is **not** the lever for completions per hour, and raising it without addressing integration would add backlog rather than throughput.

Three further points the operator should see in the summary, not buried:

- **A whole pair of runs was voided.** The first pair was uninformative for a reason that is a finding in itself: both copies had only **3 claimable cards**, because attempt counters had accumulated across earlier runs and cannot be reset. Any experiment whose card supply is below its cap cannot reach that cap, whatever its value.
- **Three interventions exceeded what D-79 permits**, all disclosed here: supply was restored by *creating cards* rather than resetting counters (a reset is impossible — see [F-04](#7-findings)), and orphaned agents were killed after each arm.
- **No arm ran for the duration requested.** `--seconds 1800` bounded nothing: the cap-10 control overran **×3.67** (6612 s), the cap-20 arm stopped at **0.86** (1550 s). No equal-budget comparison exists, and none can be constructed retrospectively. This is the single largest methodological defect in the experiment and it drives REC-18.

Nothing here changes either repository. The toy cap change under D-78 stands as a toy-only change; if it is ever to be considered for the live repository it must go through the class-K path with live evidence ([§13](#13-applicability-and-transfer-candidates)).

---

## 2. Metadata, provenance and compliance

| field | value |
|---|---|
| Document type | Formal Project Documentation |
| Title | UMAWS no-scope experiment — final report: concurrency cap 10 vs 20 |
| Version | 1.0.0 |
| Date | 2026-11-13 |
| Status | Drafted for operator ratification |
| Author (`author_llm`) | Tencent HY4 Preview — `tencent/hy4-preview-free (orcarouter)` |
| Assessor (`assessor_llm`) | **none — unassessed; independent assessment requested** |
| Parent decision | **D-78** (toy-only, ratified 2026-11-12) |
| Decisions drafted here | **D-80** (width), **D-81** (throughput limiter) — both *drafted*, neither ratified |
| Scope | Toy repository and its arm copies only |
| Source documents | `docs/arm-private-copy-results-2026-11-12.md`, `docs/arm-isolation-private-copy-2026-11-12.md`, `docs/incident-arm0-measurement-2026-11-12.md`, `pilot/decisions.md` |

### 2.1 Compliance statement

| constraint | state | evidence |
|---|---|---|
| Push ban (OR-01) | **held** | Toy repo has no git remote (`git remote -v` empty). Nothing pushed from any root. |
| Live repo untouched | **held** | No write path to `C:\temp\projects\testproject1` was used; its venv was used read-only to execute `pmk`. |
| One commit per change with trailer | **held** | All experiment commits carry `Agent: tencent-hy4-preview \| Model: tencent/hy4-preview-free (orcarouter)` (and an `Arm:` tag for per-arm commits). |
| Kernel is the sole writer (I2) | **held** | Every card transition went through `pmk`; `.pm/` was never hand-edited. |
| Oracles decide (I5) | **held** | Every DONE landed only via `gate_cmd`; `INTEGRATED` counts come from the ledger. |
| Sentinel | **clean** | Both second-pair arms returned `"findings": []`, exit 0. |
| `policy.toml` | **never edited** | No run required a policy change; no cap change was smuggled in through policy. |
| Self-assessment prohibition | **held** | `assessor_llm: []`; the author assesses no part of this document. |

### 2.2 What this document is not

It is not ratified policy, not an assessment, and not authority to change either repository. The recommendations in [§10](#10-recommendations-rec-18-to-rec-29) are advisory. D-80 and D-81 in [§9](#9-draft-decision-records-d-80-and-d-81) are *drafts in the register's own format*, so the operator can ratify them directly if they are accepted — but until ratified they are proposals.

---

## 3. Method

### 3.1 Isolation model

Each arm runs in its **own private repository copy**, so its ledger can only be written by its own conductor (`docs/arm-isolation-private-copy-2026-11-12.md`). This was adopted specifically because the first cap-20 attempt ("Arm A") had to be voided for sharing a ledger with another arm — see [C-03](#6-corrections-register--the-honesty-trail-inline).

| arm | root | cap | ledger |
|---|---|---|---|
| original baseline | `C:\temp\projects\umaws-noscope-toy` | 10 | shared toy ledger (pre-isolation) |
| pair-1 control | `C:\temp\projects\toy-arm-cap10` | 10 | own copy |
| pair-1 arm | `C:\temp\projects\toy-arm-cap20` | 20 | own copy |
| pair-2 control | `C:\temp\projects\toy-arm-cap10` | 10 | own copy |
| pair-2 arm | `C:\temp\projects\toy-arm-cap20` | 20 | own copy |

Isolation was verified **structurally** before each launch: exactly one conductor process bound to the arm root, plus its expected shim child, and **no** process bound to the other arm. Before pair-2 launched, a `hermes.exe` tree and a `cline.exe` daemon from the *previous* arm were found still alive and were killed first ([§7.2 of the results doc](#8-verdict-on-d-78)); otherwise they would have contended for the machine and biased the arm being measured.

### 3.2 Window discipline (REC-16)

Each window is **start→end from that arm's own event ledger** — the first and last event in the window, never a clock guess and never the requested `--seconds`. This matters because no arm honoured its budget:

| arm | requested | measured | ratio |
|---|---|---|---|
| pair-2 cap 10 | 1800 s | **6612 s** | **×3.67 over** |
| pair-2 cap 20 | 1800 s | **1550 s** | 0.86 under |

Per REC-16 the measured window is the honest denominator. It is honest, but it does **not** make the two runs exchangeable — see [F-07](#7-findings).

### 3.3 Width metric — the discipline that changed the answer

Width is counted **stepwise from `AGENT_STARTED`/`AGENT_EXITED` pairs**, not from lease records. This distinction is decisive:

- The dispatcher limits **live runs only**: `if len(self.runs) >= cap` (`src/fleet/dispatcher.py:270`).
- Leases belonging to agents that never exited **linger**, because nothing releases them.
- So lease-based concurrency for the cap-10 control read **19**, where the true live figure was **10**. Reporting 19 would have wrongly concluded the cap was not enforced.

All width figures in this report are the stepwise/live figures. Where leases are mentioned, they are labelled.

### 3.4 Throughput decomposition

Three rates are reported separately because they answer different questions and, at cap 20, they diverge sharply:

| rate | definition | question it answers |
|---|---|---|
| **landed** | distinct tasks reaching `INTEGRATED` per window-hour | how much work actually arrived |
| **produced** | distinct tasks reaching `SUBMITTED` per window-hour | how fast agents finished their own work |
| **exited** | distinct agents that exited per window-hour | how fast the fleet turned over |

Denominators are each arm's own measured window in hours. Comparing *totals* across unequal windows would be meaningless and is not done anywhere in this report.

### 3.5 Supply normalisation before pair-2

Before the second pair, both copies were normalised identically per the isolation protocol §3: all leases were already expired (25 in each, none active, nothing to release), and the single task not in `READY`/`DONE` was `T-0020` in **both**, moved to `READY` in both. Both then reported:

```
DONE 24, READY 44, claimable 28
```

At 18 configured profiles available in each copy (identical lists), width was therefore neither supply-limited nor profile-limited — a necessary precondition for the cap being the binding constraint.

---

## 4. Results

### 4.1 All measured windows

Every figure below was re-derived from the ledgers in one pass for this report ([Appendix A](#appendix-a--re-deriving-every-number)).

| window | arm | start → end (Z) | seconds | CLAIMED | started / exited | never exited | INTEGRATED | SUBMITTED |
|---|---|---|---|---|---|---|---|---|
| original baseline | cap 10, shared ledger | 09:48:06 → 10:32:50 | 2684 | 13 | 15 / 12 | 3 | 3 | 10 |
| pair-1 control | cap 10 | 11:38:58 → 12:02:43 | 1425 | 3 | 3 / 3 | 0 | 2 | 3 |
| pair-1 arm | cap 20 | 12:08:29 → 12:37:54 | 1765 | 3 | 3 / 3 | 0 | 2 | 3 |
| **pair-2 control** | **cap 10** | 20:24:02 → 22:14:14 | **6612** | **25** | 32 / 25 | 7 | **9** | 18 |
| **pair-2 arm** | **cap 20** | 22:19:16 → 22:45:06 | **1550** | **25** | 33 / 27 | 6 | **2** | **19** |

The original baseline row is included for provenance only: it was later **withdrawn and corrected** ([C-01](#6-corrections-register--the-honesty-trail-inline)) and it ran on the shared toy ledger before isolation existed, so it is not comparable to the isolated arms.

### 4.2 Width — the primary result

| concurrency level | pair-2 cap 10 (6612 s) | pair-2 cap 20 (1550 s) |
|---|---|---|
| **max observed** | **10** | **20** |
| ≥ 2 | 98.5% | 95.9% |
| ≥ 5 | 95.9% | 88.8% |
| ≥ 8 | 93.7% | — |
| ≥ 10 | 92.4% | 81.5% |
| **≥ 11** | **0.0%** | 80.5% |
| ≥ 15 | 0.0% | 76.1% |
| **≥ 20** | 0.0% | **56.2%** |
| most-held level | 10 for 92.4% | 20 for 56.2% (18 for 14.1%) |

Neither arm exceeded its own ceiling by even one agent, in any tick. This is the cleanest result of the experiment.

### 4.3 Throughput — where the answer stops

| per window-hour | pair-2 cap 10 | pair-2 cap 20 | ratio 20:10 |
|---|---|---|---|
| **landed** (distinct INTEGRATED) | 4.900 /h | 4.645 /h | **0.95×** (flat) |
| **produced** (distinct SUBMITTED) | 9.800 /h | **44.129 /h** | **4.50×** |
| agents exited | 10.889 /h | 51.097 /h | 4.69× |

Terminal state at window close:

| arm | still SUBMITTED (not landed) | landed | backlog ratio |
|---|---|---|---|
| cap 10 | 8 | 9 | 0.9 : 1 |
| **cap 20** | **17** | **2** | **8.5 : 1** |

### 4.4 Denial rates

| window | claim attempts | CLAIMED | denials | denial rate |
|---|---|---|---|---|
| original baseline | 37 | 13 | 24 | 64.9% |
| pair-1 cap 10 | 61 | 3 | 58 | **95.1%** |
| pair-1 cap 20 | 66 | 3 | 63 | 95.5% |
| pair-2 cap 10 | 82 | 25 | 57 | 69.5% |
| pair-2 cap 20 | 82 | 25 | 57 | 69.5% |

The pair-1 denial figures above **correct** an earlier statement of 48/61 — see [C-07](#6-corrections-register--the-honesty-trail-inline).

**A caution flagged rather than explained:** the pair-2 denial figures are *byte-identical* in both arms (57 denials / 82 attempts, identical `attempts_exhausted` breakdown). That is implausible as a coincidence and is most likely a property of the shared start state rather than of the cap. It is reported as an **unexplained observation**, not as evidence ([F-11](#7-findings)).

### 4.5 Health indicators

| indicator | pair-2 cap 10 | pair-2 cap 20 |
|---|---|---|
| `INCIDENT` | 0 | 0 |
| `QUARANTINED` | 0 | 0 |
| sentinel findings | `[]`, exit 0 | `[]`, exit 0 |
| agents never exited | 7 of 32 (21.9%) | 6 of 33 (18.2%) |
| orphan processes found after window | 3 (killed) | 3 (killed) |

No `INCIDENT` and no quarantine in either arm: **the arms were healthy**. That makes the flat landed-throughput line in [§4.3](#43-throughput--where-the-answer-stops) a structural property, not the residue of failures.

---

## 5. Why the first pair was uninformative

This is recorded because it is a finding, not an embarrassment: **the first pair would have produced a confidently wrong answer.**

Both isolated copies began pair-1 with **only 3 claimable cards**. Both arms therefore claimed 3, started 3, exited 3, and sustained **width 2** — at cap 10 *and* at cap 20 identically. Read naively, the conclusion would have been "raising the cap makes no difference, therefore the cap does not bind." That conclusion is false, and the second pair proved it false.

### 5.1 Cause: attempt counters accumulate and cannot be reset

Cards were refused with `attempts_exhausted`. A card is claimable only while `attempt < attempts.max`; `card.attempt` is **not a stored field**, it is a projection over the event log, incremented on every `CLAIMED` event (`src/pmk/state.py:137`):

```python
elif etype == "CLAIMED":
    card.attempt = int(payload.get("attempt", card.attempt + 1))
```

Nothing decrements it. `TASK_READY` clears `block_reason` but not `attempt`. No `pmk` verb — `task`, `queue`, `fleet`, `project` — exposes a reset. The two remaining routes were:

1. rewrite `.pm` history by hand — **forbidden**, the Kernel is the sole writer (I2); or
2. give the fleet **new cards**, which start at attempt 0.

Route 2 was taken ([F-04](#7-findings)).

### 5.2 What was done, and how it departs from the authorisation

The operator authorised: *reset the attempt counters in both copies and re-run both arms symmetrically*. **A reset was impossible, so supply was restored by substitution**, applied identically to both copies and in the same order: 24 cards created through `pmk task create` (`T-0045`…`T-0068`), each with a write scope that does not yet exist, the standard oracle `python workload/check.py <file> TOY-OK`, `RESULT.md` as evidence, `attempts.max = 3`, and no dependencies.

This is stated plainly because "reset" is what was approved. The intent — restore dispatchable supply so the cap, not the queue, decides width — is met; the letter is not. The 27 cards carrying inherited exhaustion were left BLOCKED in both copies, generating identical refusal noise in both, rather than voided, to keep the intervention minimal.

### 5.3 Direction of the bias this created

The substitution biased the pair **toward the cap being able to bind**, which is what made the pair informative. But it also introduced a confound declared before seeing results: 24 of the 28 claimable cards are trivially satisfiable toy cards, so this pair's absolute throughput greatly exceeds anything before it and is **not comparable to earlier windows**. Only the cap 10 vs cap 20 comparison *within* pair-2 survives.

### 5.4 Symmetry verification, and a worthless check that was withdrawn

Before launching, an automated check printed a differing `ids hash` between the two copies. **That check proved nothing** — Python salts string hashes per process, so the same data yields different hashes in different processes. It was withdrawn and replaced with an element-wise comparison ([C-08](#6-corrections-register--the-honesty-trail-inline)):

```
same task id set  : True     (68 vs 68)
state mismatches  : none
attempt mismatches: none
claimable equal   : True     cap10 = 27, cap20 = 27
```

---

## 6. Corrections register — the honesty trail, inline

Per the operator's instruction, the full trail is carried in place rather than condensed. Each entry states what was said, what is correct, and the cause. Nothing in this section was silently repaired.

| id | what was said / done | what is correct | cause |
|---|---|---|---|
| **C-01** | Baseline throughput reported as **2.995 DONE/h** | **4.024 DONE/h** over 2684 s | An earlier window was contaminated by the following run. Withdrawn and corrected at `e43e148`; further corrected at `5eafd86` for a contaminated §9.3 window. |
| **C-02** | A cap-20 arm had been "measured" | **No valid cap-20 arm existed.** The run (`9770c57`) shared a ledger with another arm and left no terminal evidence; voided, then restated at `9db9b1d` | Isolation did not exist yet. Cause of adopting private copies. |
| **C-03** | Arm A results usable | Voided — **shared ledger, no terminal evidence** | Same root cause as C-02; recorded because the void is what motivated the isolation protocol. |
| **C-04** | 48 `attempts_exhausted` blocks meant 48 cards were exhausted | They meant **48 refusal events**, many against the same cards, mixed with 9 "already satisfied" refusals | Event counts confused with card counts. Corrected at `534ed85`. |
| **C-05** | Two timestamps cited for run start/end | Fabricated. Correct values **11:24:40Z** and **11:27:37Z** | Values were reconstructed from memory rather than read from the ledger. The standing rule — windows come from the ledger — exists because of this. |
| **C-06** | Estimated ~60 minutes for both arms | The cap-10 control alone took **110 minutes** (6612 s vs 1800 s requested) | I assumed `--seconds` bounded a run. It does not ([F-06](#7-findings)). |
| **C-07** | Pair-1 denial stated as **48 / 61** | **58 / 61 = 95.1%** | Arithmetic slip. Corrected here; see [§4.4](#44-denial-rates). |
| **C-08** | "The IDs hash differs, so the copies may be asymmetric" | Meaningless — **Python salts string hashes per process** | Used a hash comparison as a data-equality test. Withdrawn and redone element-wise ([§5.4](#54-symmetry-verification-and-a-worthless-check-that-was-withdrawn)). |
| **C-09** | "Reset the attempt counters" | Impossible; supply restored by **card substitution** | `attempt` is a log projection with no decremental path ([§5.2](#52-what-was-done-and-how-it-departs-from-the-authorisation)). |

### 6.1 Interventions beyond what D-79 permits

Three interventions in the second pair exceeded the single requeue D-79 allows per arm. All were disclosed as they happened and are restated here so they are not lost in the verdict:

1. **Card creation** (24 per copy) substituting for the impossible counter reset — §5.2.
2. **Orphan reaping after the cap-10 control**: `hermes.exe` PID 18536 + `python.exe` child PID 10928 still working T-0067, plus `cline.exe` daemon PID 9740 bound to `work/T-0051-108`. Killed because agents surviving into the next arm would contend for the machine and bias the comparison the arms exist to make.
3. **Orphan reaping after the cap-20 arm**: a `cline.exe` daemon and a `kilo.exe` tree still executing task work. Killed for the same reason.

All window-bounded figures were computed **before** those kills, so the results are unaffected. The *recurrence* is itself evidence: see [F-08](#7-findings).

---

## 7. Findings

Each finding is labelled **measured**, **derived**, or **guess**.

### F-01 — The cap sets sustained width. *(measured)*
Cap 10 → max 10, never 11, at 10 for 92.4% of 6612 s. Cap 20 → max 20, never more, at 20 for 56.2% of 1550 s. Neither exceeded its ceiling by one. Evidence: [§4.2](#42-width--the-primary-result).

### F-02 — Lease records overstate live width, badly. *(measured)*
The cap-10 control read **19** concurrent on leases and **10** live. The dispatcher limits live runs (`src/fleet/dispatcher.py:270`); leases of never-exited agents linger. Any future experiment reporting lease-based concurrency will overstate width by roughly 2× and may wrongly conclude the cap is unenforced. This is why REC-21 exists.

### F-03 — At cap 20 the binding constraint moved to integration. *(measured)*
Produced rose 4.50× (9.800 → 44.129 SUBMITTED/h) while landed stayed flat (4.900 → 4.645 INTEGRATED/h). Terminal backlog 8.5 : 1 at cap 20 vs 0.9 : 1 at cap 10. Evidence: [§4.3](#43-throughput--where-the-answer-stops).

### F-04 — Attempt counters are unresettable, so supply poisoning is permanent. *(derived from code + CLI surface)*
`card.attempt` is a projection over `CLAIMED` events (`src/pmk/state.py:137`), decremented nowhere; no `pmk` verb resets it; hand-editing `.pm` violates I2. Every prior run therefore permanently raises the exhaustion floor for every subsequent run in the same repository. Consequence: this is not only a defect in this experiment, it makes **any repeated experiment on a reused copy progressively unmeasurable** unless fresh cards are supplied or the copy is recreated. It is the strongest argument for REC-22.

### F-05 — An experiment cannot test a cap above its card supply. *(derived)*
Pair-1 had 3 claimable cards and reached width 2 under both caps. The general form: **supply must exceed cap with margin**, and the margin has to absorb cards lost to exhaustion and to rework. Pair-2 supplied 28 claimable against cap 20 (1.4×) and still decayed from its ceiling — cap 20 held 20 for only 56.2% of the window *because supply ran out*, with both arms claiming exactly 25. REC-23 sets the floor at ≥2× cap with ≥60 cards.

### F-06 — `--seconds` does not bound a run. *(measured)*
Requested 1800 s; measured 6612 s (×3.67) and 1550 s (0.86) in the two arms. The cap-10 window contained a **single tick consuming 5655 s — 86% of the whole window**. The run warned about this itself:

```
WARNING: one tick alone took 5655s, longer than the whole 1800s budget.
No deadline logic can bound that - the conductor must be bounded (REC-15, unimplemented half).
```

Because the two arms deviated in **opposite directions**, no equal-window comparison exists and none can be reconstructed. REC-15 implemented only the "don't start a tick that will outlive the budget" half; nothing bounds a tick already running. This is REC-18.

### F-07 — Unequal windows make landed-throughput comparison unsafe. *(derived)*
Cap 10 had 16 ticks to drain its backlog; cap 20 had 3. Comparing landed *totals* (9 vs 2) across windows differing 4.3× would be meaningless; comparing hourly rates (as [§4.3](#43-throughput--where-the-answer-stops) does) is the least-bad available form and is still not a like-for-like comparison. Reported with that caveat rather than as a conclusion about the cap.

### F-08 — Agents structurally outlive their conductor. *(measured, replicated)*
7 of 32 never exited (cap 10) and 6 of 33 never exited (cap 20); orphan processes were found alive after **both** windows, in one case still executing task work minutes after close. Replication across both arms is what makes this structural rather than a one-off. It also means every arm needs post-run reaping before the next arm launches, and that lease-based state is permanently dirty. REC-24.

### F-09 — Private per-arm copies achieved isolation and should be mandatory. *(measured)*
No cross-arm ledger contamination occurred in pair-1 or pair-2, in contrast to the voided shared-ledger Arm A ([C-02](#6-corrections-register--the-honesty-trail-inline)). Structural process checks before each launch confirmed one conductor per arm and no foreign binding.

### F-10 — Orphaned agents may write after their window closes. *(derived, from what was observed alive)*
Processes found still executing task work imply writes after the measurement boundary. No evidence of an actual late write was collected in this experiment — this is stated as a risk to control, not as an observed corruption. REC-25 requires the check.

### F-11 — Denial rate is not a capacity signal. *(measured, with an unexplained coincidence flagged)*
Pair-2 denial was **byte-identical** in both arms: 57 denials / 82 attempts, identical breakdown. Given different caps and different tick structures that is unlikely to be coincidence; the most probable explanation is that denial is dominated by the shared start state (exhausted cards, "already satisfied" refusals) rather than by any cap effect. **This is reported as an unexplained observation, not used as evidence either way.** No conclusion in this report depends on it. It is listed in [§12](#12-unresolved-issues-and-follow-up-experiment-options).

### F-12 — `pmk revoke` exits 2. *(measured, minor)*
Lease release during normalisation was not possible through `pmk revoke` (exit 2), though it was not needed — all 25 leases in each copy were already expired. Recorded so a future operator does not rely on that verb.

---

## 8. Verdict on D-78

D-78 asked whether raising `fleet.max_total_agents` from 10 to 20 increases sustained width and throughput. It contained **two questions**. Only one is answered.

| question | verdict | basis |
|---|---|---|
| **Width** — does 10→20 increase sustained concurrent agents? | **ANSWERED: YES.** Sustained width doubled, 10 → 20, with each arm pinned at exactly its own ceiling and neither exceeding it. | [F-01](#7-findings), [§4.2](#42-width--the-primary-result) |
| **Throughput** — does wider finish more work per unit time? | **NOT ANSWERED.** Landed throughput was flat (4.900 → 4.645 /h) while produced rose 4.50×. The limiter is now integration, not width. | [F-03](#7-findings), [F-06](#7-findings), [F-07](#7-findings) |

**Why the throughput question cannot be answered with this data.** Three independent reasons, any one of which is sufficient:

1. **Unequal windows in opposite directions.** 6612 s vs 1550 s; ×3.67 over vs 0.86 under ([F-06](#7-findings)). No equal-window or equal-budget comparison exists and none can be reconstructed after the fact ([F-07](#7-findings)).
2. **Supply ran out in both arms.** Each claimed exactly 25 cards. Neither arm was cap-limited for long enough to measure steady-state throughput — which is also why cap 20 held its ceiling only 56.2% of its window ([F-05](#7-findings)).
3. **The throughput limiter changed during the experiment.** Once agents produce faster than integration can land, integration — not width — sets the completion rate. Measuring "does cap affect throughput" while another limiter is active measures that limiter, not the cap ([F-03](#7-findings)).

**What this reverses.** The first pair invited the reading "the cap makes no difference." That reading was **wrong**, and §5 shows why: with 3 claimable cards neither arm could reach 10 under any ceiling. The first pair was uninformative, not evidence. It is important that this is not recorded the other way round.

**What D-78 established for toy purposes.** Raising the cap is a *reachability* change. If the objective is "the fleet should be able to hold N concurrent agents," the cap is the correct and sufficient lever, and it should be set to the target width. If the objective is "more completions per hour," the cap is not the lever, and raising it without addressing integration will increase backlog — cap 20 ended with 8.5 submitted cards per landed card, against 0.9 at cap 10.

---

## 9. Draft decision records D-80 and D-81

Both rows follow `pilot/decisions.md` register format (id | date | author | decision | alternatives rejected | unknowns). **Both are drafts for operator ratification.** They have not been merged into the live register and must not be until ratified.

### D-80 — Width: the cap decides it

| field | content |
|---|---|
| **id / date** | **D-80** / 2026-11-13 |
| **author** | Tencent HY4 Preview (`tencent/hy4-preview-free (orcarouter)`) — *drafted for operator ratification* |
| **status** | Toy-only. Not ratified. |
| **decision** | `fleet.max_total_agents` is the binding constraint on sustained concurrent agents, and it should be set to the target width rather than left at a legacy value. Measured: at cap 10, max concurrency 10 (never 11), held at 10 for 92.4% of a 6612 s window; at cap 20, max concurrency 20 (never more), held at 20 for 56.2% of a 1550 s window. Each arm pinned to its own ceiling. Width is bounded only for **live runs** (`src/fleet/dispatcher.py:270`); lease records overstate it (19 vs 10) and must not be used. |
| **alternatives rejected** | (a) *Leave the cap at a legacy value and let supply bind width* — rejected: this yields a fleet whose width is an accident of card availability and silently degrades as attempt counters accumulate ([F-04](#7-findings), [F-05](#7-findings)). (b) *Infer the cap from lease counts* — rejected: overstates width ~2× because leases of never-exited agents linger ([F-02](#7-findings)). (c) *Set the cap above available profiles and let profiles bind* — not observed here (18 profiles available, headroom existed), so unsupported. |
| **unknowns** | Whether the ceiling holds above 20 (untested: caps 30/40 never run); whether width decays for reasons other than supply exhaustion; why denial was byte-identical across the two arms ([F-11](#7-findings)); whether the same relationship holds on harder cards, since pair-2 cards were trivially satisfiable. |

### D-81 — Throughput: the binding constraint is now integration

| field | content |
|---|---|
| **id / date** | **D-81** / 2026-11-13 |
| **author** | Tencent HY4 Preview (`tencent/hy4-preview-free (orcarouter)`) — *drafted for operator ratification* |
| **status** | Toy-only. Not ratified. |
| **decision** | Raising width beyond integration's capacity does not increase landed throughput and should not be relied on to do so. Measured at cap 20: produced 44.129 distinct SUBMITTED/h vs 9.800 at cap 10 (4.50×), while landed was 4.645 vs 4.900 INTEGRATED/h (flat), leaving a terminal backlog of 17 SUBMITTED to 2 landed (8.5 : 1) against 0.9 : 1 at cap 10. Integration must be addressed **before or alongside** any further width increase, and landed/produced/exited must be reported separately thereafter. This decision explicitly does **not** quantify the integration ceiling — the serial-merge hypothesis is untested ([§12](#12-unresolved-issues-and-follow-up-experiment-options)) and the unequal windows prevent it ([F-07](#7-findings)). |
| **alternatives rejected** | (a) *Conclude that a wider cap is harmful because landed fell slightly* — rejected: windows differ 4.3× and both arms were supply-limited, so this difference carries no signal. (b) *Conclude the cap is irrelevant to throughput* — rejected as unmeasured: throughput was never measured under equal windows with adequate supply. (c) *Raise the cap further to see if throughput recovers* — rejected: would enlarge the backlog without addressing its cause, and each further run burns cards permanently ([F-04](#7-findings)). |
| **unknowns** | The actual capacity of the integration path; whether `drain_merge_queue` (`src/fleet/conductor.py`) is serial and whether that is the specific cause — **untested, offered as the leading hypothesis only**; how much of the flat landed rate is the short 1550 s window rather than the gate; what integration backlog does to subsequent runs given counters are unresettable. |

---

## 10. Recommendations REC-18 to REC-29

Numbering continues the existing register (which ends at REC-17). Priorities: **P0** = must be satisfied before the next experiment that makes a throughput claim; **P1** = strongly advised; **P2** = desirable.

| id | pri | recommendation | driven by |
|---|---|---|---|
| REC-18 | P0 | Bound the tick, not just its start | F-06 |
| REC-19 | P0 | Equal measured windows as a precondition for any throughput claim | F-07 |
| REC-20 | P1 | Analysis tools must take an explicit root and fail loudly otherwise | C-01 lineage |
| REC-21 | P0 | Report width stepwise from agent start/exit; never from leases | F-02 |
| REC-22 | P0 | Restore supply per run via a real reset path, not card substitution | F-04 |
| REC-23 | P0 | Enforce a supply floor of ≥2× cap and ≥60 cards | F-05 |
| REC-24 | P0 | Mandatory orphan-reaping gate between arms | F-08 |
| REC-25 | P1 | Post-window write check to detect late writes | F-10 |
| REC-26 | P0 | Diagnose and address the integration serial gate | F-03 |
| REC-27 | P1 | Make landed / produced / exited first-class metrics | F-03 |
| REC-28 | P1 | Fix `pmk revoke` exit-2 | F-12 |
| REC-29 | P1 | Independent assessment before ratifying experiment-derived decisions | provenance |

### REC-18 — Bound the tick, not just its start (P0)
**Recommendation.** Implement the unimplemented half of REC-15: enforce a wall-clock deadline on a tick *in progress* (hard kill of the conductor's tick with the agent tree), not merely refuse to start a new tick that would outlive the budget.
**Rationale.** One tick consumed 5655 s — 86% of a 6612 s window — against a 1800 s budget. Start-side logic cannot bound that, and the run's own warning says so. Until this exists no experiment can request a window and receive it.
**Acceptance test.** Request `--seconds N`; measured window ≤ N with margin, across two consecutive runs, in both directions of the earlier failure (i.e. a run that would overrun stops at N).

### REC-19 — Equal measured windows as a precondition for any throughput claim (P0)
**Recommendation.** No experiment may report a throughput comparison unless the arms' measured windows agree within an agreed tolerance (suggest ±10%), or until REC-18 makes windows requestable. Where windows differ, the throughput question must be reported as **unanswered**, as done in [§8](#8-verdict-on-d-78).
**Rationale.** Windows differed 4.3× in opposite directions (×3.67 vs 0.86). Per-window-hour rates are the least-bad available form and still not like-for-like. This report's honest answer to "did throughput improve?" is "we could not measure it," and that should be the standing answer until windows are controllable.
**Acceptance test.** The comparison is blocked before launch if windows cannot be bounded, or the report carries the unanswered label.

### REC-20 — Analysis tools must take an explicit root and fail loudly (P1)
**Recommendation.** Any tool reading a ledger must require `--root` and error if absent, rather than silently reading another repository. `tools/analyze_arm.py` previously hardcoded a repo and would have produced figures from the wrong copy undetectably (`b4a3f76`).
**Rationale.** Silent cross-repository reads are the most dangerous class of error here: the output is well-formed and plausible, and wrong. Related: the wider family of errors already committed in this experiment (fabricated timestamps [C-05](#6-corrections-register--the-honesty-trail-inline), contaminated windows [C-01](#6-corrections-register--the-honesty-trail-inline)) all share the property of looking correct.
**Acceptance test.** Running the tool without `--root` exits non-zero with a clear message.

### REC-21 — Width from start/exit pairs, never from leases (P0)
**Recommendation.** Concurrency must be reconstructed stepwise from `AGENT_STARTED`/`AGENT_EXITED`. If lease-derived width is reported at all, it must be labelled "lease-based (inflated by unreleased leases)" and never compared with live width, nor used to judge whether the cap is enforced.
**Rationale.** Lease width read 19 where live width was 10 — would have supported the false conclusion that cap 10 was not enforced. The dispatcher limits live runs only (`src/fleet/dispatcher.py:270`).
**Acceptance test.** Every width figure in a future report carries its metric; no report contains an unlabelled lease-based width.

### REC-22 — A real supply-reset path (P0)
**Recommendation.** Because `attempt` is unresettable, either add a supported operator-side capability to reset or decrement a card's attempt budget, **or** require that each experiment starts from a freshly created copy / a freshly generated card set. Card substitution (what this experiment did) must remain the fallback of last resort and be disclosed, not normalised.
**Rationale.** Attempt counters accumulate permanently across runs in a reused copy, so *every* prior run raises the exhaustion floor for all later ones ([F-04](#7-findings)). This is why pair-1 was unmeasurable and why substitution was needed at all. Without a fix, repeated experiments on one copy become progressively unmeasurable.
**Acceptance test.** A future arm can begin with ≥REC-23 supply without inventing cards, using one documented verb.

### REC-23 — Supply floor ≥2× cap, ≥60 cards (P0)
**Recommendation.** Launch gate: claimable cards ≥ 2 × cap, and at least 60 claimable cards in absolute terms for any cap ≥20.
**Rationale.** 28 claimable against cap 20 (1.4×) let the arm decay off its ceiling — it held 20 for only 56.2% of the window, and both arms exhausted supply at exactly 25 claims. Below the cap, supply *is* the experiment ([F-05](#7-findings), [§5](#5-why-the-first-pair-was-uninformative)).
**Acceptance test.** Launch is blocked if the floor is unmet; the check is recorded with its numbers.

### REC-24 — Mandatory orphan-reaping gate between arms (P0)
**Recommendation.** Before any arm launches, enumerate processes bound to any arm root, kill survivors of previous arms, and record both the list and the action. Make this a gate, not a habit.
**Rationale.** Orphans were found after **both** windows, in one case still executing task work minutes after close. Left running, they contend for the machine and bias the arm being measured ([F-08](#7-findings)). Replication across arms makes this structural, not incidental.
**Acceptance test.** Gate output (processes found, PIDs, action) is attached to the next arm's record.

### REC-25 — Post-window write check (P1)
**Recommendation.** After window close, compare repository state against the window end (e.g. `git status --porcelain`, untracked files under `work/`) to detect writes made by agents after their lease ended.
**Rationale.** Orphans were observed mid-task after window close; whether they wrote anything was **not measured** ([F-10](#7-findings)). This is a risk to control, not a proven corruption — but it should be measured rather than assumed away.
**Acceptance test.** Every future arm records the post-window state check result.

### REC-26 — Diagnose and address the integration serial gate (P0)
**Recommendation.** Before any further width increase, establish why landed throughput is flat while produced rises 4.5×. The **leading hypothesis** is that integration is serial (`drain_merge_queue`, `src/fleet/conductor.py`) — this is untested and must be treated as a hypothesis, not a finding. Then either parallelise it with safe conflict handling, or size width deliberately to integration's measured capacity.
**Rationale.** This is now the binding constraint at cap 20: terminal backlog 8.5 : 1 submitted-to-landed ([F-03](#7-findings)). It is why the throughput half of D-78 could not be answered, and why further width increases would enlarge rather than relieve the backlog.
**Acceptance test.** Integration capacity measured (lands/h) and either raised or used to set the width deliberately.

### REC-27 — Landed / produced / exited as first-class metrics (P1)
**Recommendation.** Analysis tooling should emit these three rates separately and always with their window, since they diverge sharply (4.50× vs 0.95× here) and conflating them is what first made cap 20 look like it changed nothing.
**Rationale.** The experiment's key insight — agents got faster, the pipeline did not — only appears when the three are separated ([F-03](#7-findings)).
**Acceptance test.** `analyze_arm.py` output contains all three with denominators.

### REC-28 — Fix `pmk revoke` exit-2 (P1)
**Recommendation.** Investigate why lease release exits 2; provide a documented way to clear a lease explicitly.
**Rationale.** Not needed here (leases were already expired), but a normalisation step that cannot be performed is a latent trap for a future run that does need it ([F-12](#7-findings)).

### REC-29 — Independent assessment before ratifying experiment-derived decisions (P1)
**Recommendation.** No decision record drafted from an experiment should be ratified on the author's own evidence. Require an `assessor_llm` entry, as this report conspicuously lacks.
**Rationale.** This experiment's own history is the argument: it produced one voided arm, one withdrawn baseline, one fabricated timestamp pair, one worthless symmetry check and one wrong estimate — all of which were internally consistent and all of which an author would have missed. Re-deriving numbers catches transcription drift, not reasoning error.

---

## 11. Mandatory pre-launch checklist for future experiments

These are stated as **required**, not suggested. Each row states what it prevents, with the specific failure in this experiment.

| # | gate | requirement | failure it would have prevented |
|---|---|---|---|
| 1 | **Supply floor** | claimable cards ≥ 2 × cap, and ≥60 absolute (REC-23) | Pair-1 reaching width 2 under both caps because only 3 cards were claimable ([§5](#5-why-the-first-pair-was-uninformative)) |
| 2 | **Supply freshness** | attempts at 0 for supplied cards; exhaustion floor measured before launch (REC-22) | The whole first pair being voided by inherited counters ([F-04](#7-findings)) |
| 3 | **Isolation** | one private copy per arm; each has its own ledger | Voided Arm A — shared ledger, no terminal evidence ([C-02](#6-corrections-register--the-honesty-trail-inline)) |
| 4 | **No foreign processes** | enumerate processes bound to any arm root; none may belong to another arm (REC-24) | Orphans from arm 1 contending with arm 2's measurement ([F-08](#7-findings)) |
| 5 | **Empty `work/`** | no residual worktrees or agent scratch from prior runs | Cross-run state leaking into the new window |
| 6 | **Symmetry** | element-wise comparison of id sets, states and attempts — **never** a hash comparison | The meaningless `ids hash` check ([C-08](#6-corrections-register--the-honesty-trail-inline)) |
| 7 | **Window budget** | `--seconds` requested; a means of bounding exists, or the throughput claim is pre-declared unanswered (REC-18, REC-19) | ×3.67 overrun; no equal-window comparison existing ([F-06](#7-findings)) |
| 8 | **Tool root** | every analysis command receives `--root` explicitly (REC-20) | Silently analysing the wrong repository |
| 9 | **Width metric** | width to be reported stepwise from start/exit pairs (REC-21) | Lease width 19 vs live 10, and the false "cap unenforced" reading ([F-02](#7-findings)) |
| 10 | **Start marker** | write a start timestamp file **before** launch; window comes from ledger events only | Fabricated timestamps ([C-05](#6-corrections-register--the-honesty-trail-inline)) |
| 11 | **Post-run reaping** | after each arm, enumerate and kill survivors; record PIDs (REC-24) | Orphans writing after window close ([F-10](#7-findings)) |
| 12 | **Post-window state check** | repository state compared against window end (REC-25) | Late writes being assumed away rather than measured |
| 13 | **Sentinel** | `pmk sentinel` clean before and after each arm | Reporting results from a corrupt ledger |
| 14 | **Trailer** | every commit carries `Agent: … \| Model: … \| Arm: …` | Ambiguity about which arm produced which ledger |

**Why each of these is a gate rather than advice:** every item above maps to a failure that actually occurred in this experiment, not to a hypothetical risk. The list is short because each row was bought with a voided run, a withdrawn figure, or a wrong conclusion.

---

## 12. Unresolved issues and follow-up experiment options

### 12.1 Unresolved issues

Each is stated with what would resolve it, so this list is actionable rather than decorative.

| id | unresolved issue | what would resolve it | blocks |
|---|---|---|---|
| **U-01** | The throughput half of D-78. Not answered; unequal windows, exhausted supply, and a changed limiter ([§8](#8-verdict-on-d-78)). | Equal bounded windows with adequate supply; or REC-26 first | Any cap-for-throughput decision |
| **U-02** | Actual integration capacity, and whether the serial merge gate is the cause. The serial hypothesis is **untested**. | Instrument `drain_merge_queue`; measure lands/h and queue depth | REC-26, U-01 |
| **U-03** | Behaviour above cap 20. Caps 30/40 never ran; whether width then binds on cap, profiles, or machine is unknown. | A width-ceiling probe (option C) | Any claim about higher caps |
| **U-04** | Why denial was byte-identical (57/82) across both arms despite different caps ([F-11](#7-findings)). | Vary start state deliberately and observe whether denial moves | Reading denial as any kind of signal |
| **U-05** | Attempt counters accumulate and cannot be reset ([F-04](#7-findings)); every run permanently degrades the copy. | REC-22 | Any repeated experiment on a reused copy |
| **U-06** | Root cause of agents outliving their conductor — replicated twice but never diagnosed ([F-08](#7-findings)). | Post-exit process census with agent exit codes and lease state | Lease hygiene; REC-24 as a stopgap |
| **U-07** | Whether orphaned agents actually write after window close ([F-10](#7-findings)) — risk flagged, never measured. | REC-25 post-window state check | Trusting window-bounded figures |
| **U-08** | Card-difficulty confound: 24 of 28 claimable cards were trivially satisfiable. Absolute rates here say nothing about real work. | Repeat with cards of realistic difficulty | All absolute throughput figures |
| **U-09** | `pmk revoke` exits 2 ([F-12](#7-findings)). | Fix and retest | Normalisation steps needing lease release |
| **U-10** | This report is **unassessed**. | Independent assessment with an `assessor_llm` entry | Ratification of D-80/D-81 |

### 12.2 Follow-up experiment options

Three designs, presented as options rather than a single recommendation so the operator can choose. Each states what it answers and what must be true first.

**Option A — Equal-window throughput test.** The direct continuation: answer U-01.
- **Design**: caps 10 vs 20, both arms bounded to the same window; ≥60 claimable cards (≥2× cap); primary metric **landed/h**, secondary produced/h and terminal backlog ratio.
- **Prerequisites**: REC-18 (bounded runs), REC-22 (fresh supply), REC-23 (supply floor), REC-24 (reaping).
- **Answers**: U-01; partially U-08 if realistic cards are used.
- **Risk**: if integration remains the limiter, this measures integration again, not the cap. That outcome is itself informative but means option B should have come first.

**Option B — Integration-only investigation.** Recommended order if the goal is throughput rather than reach.
- **Design**: fix cap (10 is sufficient), instrument `drain_merge_queue` and integration queue depth, measure lands/h against produced/h over a bounded window. Not a cap comparison.
- **Prerequisites**: REC-26; REC-27 (separated metrics).
- **Answers**: U-02; unblocks option A from being confounded.
- **Risk**: diagnostic rather than comparative — it produces a mechanism, not a decision about width.

**Option C — Width-ceiling probe.** Cheapest and cleanest if reachability is the goal.
- **Design**: caps 20 / 30 / 40, short windows, ≥60 cards minimum (120 would be needed to hold 40 — supply is the limiting reagent), primary metric **max and sustained width**, throughput explicitly not claimed.
- **Prerequisites**: REC-23 with a supply floor matching the highest cap, REC-21 (width metric), REC-24.
- **Answers**: U-03; establishes whether the cap keeps governing at higher values.
- **Risk**: *(guess)* at cap 40 machine contention may become the binding constraint, which would be indistinguishable from a cap effect unless CPU/memory is recorded alongside.

| option | answers | cheapest? | prerequisite load |
|---|---|---|---|
| A — equal-window throughput | U-01 | no — needs bounded runs first | high |
| B — integration investigation | U-02 | yes | medium |
| C — width-ceiling probe | U-03 | yes if supply exists | medium-high (supply) |

**Sequence suggested, not mandated:** B → A → C. Fix the limiter before measuring around it, then probe the ceiling. This ordering is the operator's to accept or reject; nothing here commits a run.

---

## 13. Applicability and transfer candidates

### 13.1 Applicability statement

**These results apply to the toy repository and its arm copies only.** They do not apply to `C:\temp\projects\testproject1`. No live code was changed, no live ledger was read for results, and nothing was pushed anywhere (OR-01 held; the toy repository has no git remote). The cards used were predominantly trivial-toy cards whose oracle is a file containing `TOY-OK` ([U-08](#121-unresolved-issues)), which alone makes absolute rates non-transferable.

Nothing below may be promoted to the live repository without going through the project's **class-K ratification path** with evidence produced in the live repository itself.

### 13.2 Transfer candidates and the evidence each would need

Each candidate is listed with the toy evidence supporting it and — as requested — the specific measurement that would be required before it could be promoted. None has that evidence today.

| id | candidate | toy evidence | why it might transfer | **required evidence to promote** |
|---|---|---|---|---|
| **TC-1** | The cap sets sustained width | Max 10 (never 11) at cap 10; max 20 at cap 20 ([F-01](#7-findings)) | Enforcement is code-level (`dispatcher.py:270`) and cap-shaped | A live bounded window at two cap values, with a supply floor exceeding the higher cap, using live start/exit width |
| **TC-2** | Lease-based width overstates live width ~2× | 19 leases vs 10 live ([F-02](#7-findings)) | Purely a consequence of unreleased leases — likely environment-independent | A live comparison of lease-derived vs start/exit-derived width in one window |
| **TC-3** | Integration becomes the limiter above width ~20 | Produced 4.50× vs landed flat; backlog 8.5:1 ([F-03](#7-findings)) | Suggests a real serial bottleneck | **Hypothesis only** — needs live lands/h vs produced/h and integration-queue instrumentation. Must not be promoted on toy evidence |
| **TC-4** | Agents structurally outlive their conductor | Replicated in both arms: 7/32 and 6/33 never exited, orphans after both ([F-08](#7-findings)) | Behavioural, observed twice, consistent with REC-15's unimplemented half | A live post-run process census after a live window, replicated at least twice |
| **TC-5** | Attempt counters accumulate and are unresettable | Code-level, `state.py:137`; no reset verb exists ([F-04](#7-findings)) | A property of the code, not of the toy workload | A live attempt-floor census across cards, plus confirmation no live reset path exists |
| **TC-6** | `--seconds` does not bound a run | ×3.67 over and 0.86 under, in opposite directions ([F-06](#7-findings)) | Deadline logic is code-level; REC-15 is only half-implemented | REC-18 implemented, then a live bounded-run test in both directions |

**Standing caution.** TC-2, TC-5 and TC-6 are properties of code that both repositories share, which is why they are the strongest candidates. TC-1 and TC-3 are properties of a workload, and the toy workload is trivially satisfiable — those two are the weakest and should be treated as hypotheses in any live context until measured there. This distinction is the reason each row above carries its own required evidence rather than a blanket statement.

---

## 14. Appendices

### Appendix A — re-deriving every number

Every headline figure in this report was re-derived from the event ledgers **in the session that produced the report**, not transcribed from earlier documents. The one-pass script is at:

```
C:\Users\Tiwa Pene\AppData\Local\Temp\armstats.py
```

It loads each arm's own ledger through `pmk.api.Kernel(root=...)`, filters events to the stated window, and recomputes: window seconds, CLAIMED, started/exited, distinct INTEGRATED and SUBMITTED, stepwise concurrency, max concurrency and % of window at or above each level, denial rate, and the three hourly rates.

Run it with:
```
C:\temp\projects\testproject1\.venv\Scripts\python.exe "%TEMP%\armstats.py"
```

Window boundaries used (all UTC, all taken from that arm's own ledger's first and last event in the window):

| window | start | end |
|---|---|---|
| original baseline | 2026-11-12T09:48:06Z | 2026-11-12T10:32:50Z |
| pair-1 cap 10 | 2026-11-12T11:38:58Z | 2026-11-12T12:02:43Z |
| pair-1 cap 20 | 2026-11-12T12:08:29Z | 2026-11-12T12:37:54Z |
| pair-2 cap 10 | 2026-11-12T20:24:02Z | 2026-11-12T22:14:14Z |
| pair-2 cap 20 | 2026-11-12T22:19:16Z | 2026-11-12T22:45:06Z |

For per-arm detail the analyzer must be given its root explicitly (REC-20):

```
python tools\analyze_arm.py --arm <name> --root <arm root> ^
  --start <start> --end <end> --requested-seconds 1800
```

Sentinel per arm: `pmk --root <arm root> sentinel` — both second-pair arms returned `"findings": []`, exit 0.

### Appendix B — raw counts

| window | start→end | s | CLAIMED | started | exited | never exited | INTEGRATED | SUBMITTED | attempts | denials | max live width |
|---|---|---|---|---|---|---|---|---|---|---|---|
| original baseline | 09:48:06→10:32:50 | 2684 | 13 | 15 | 12 | 3 | 3 | 10 | 37 | 24 (64.9%) | 10 |
| pair-1 cap 10 | 11:38:58→12:02:43 | 1425 | 3 | 3 | 3 | 0 | 2 | 3 | 61 | 58 (95.1%) | 2 |
| pair-1 cap 20 | 12:08:29→12:37:54 | 1765 | 3 | 3 | 3 | 0 | 2 | 3 | 66 | 63 (95.5%) | 2 |
| pair-2 cap 10 | 20:24:02→22:14:14 | 6612 | 25 | 32 | 25 | 7 | 9 | 18 | 82 | 57 (69.5%) | 10 |
| pair-2 cap 20 | 22:19:16→22:45:06 | 1550 | 25 | 33 | 27 | 6 | 2 | 19 | 82 | 57 (69.5%) | 20 |

Derived hourly rates: cap 10 — landed 4.900/h, produced 9.800/h, exited 10.889/h. Cap 20 — landed 4.645/h, produced 44.129/h, exited 51.097/h.

Health per second-pair arm: `INCIDENT` 0, `QUARANTINED` 0, sentinel `[]` exit 0 in both.

### Appendix C — interventions log

| # | intervention | authorised? | why | effect on figures |
|---|---|---|---|---|
| 1 | 24 cards created per copy (`T-0045`…`T-0068`) substituting for the impossible counter reset | partially — "reset" was authorised; reset is impossible ([C-09](#6-corrections-register--the-honesty-trail-inline)) | restore dispatchable supply so cap, not queue, decides width | Biases toward the cap binding; confounds absolute rates ([§5.3](#53-direction-of-the-bias-this-created)) |
| 2 | Normalisation: `T-0020` moved to `READY` in both copies; all 25 leases per copy already expired | per isolation protocol §3 | symmetric start state | none — applied identically to both |
| 3 | Orphan reaping after cap-10 control: `hermes.exe` 18536 + child `python.exe` 10928 (still on T-0067), `cline.exe` daemon 9740 | **no** — exceeds D-79 | prevent contention biasing the cap-20 arm | none — figures computed before the kill; also needed to avoid a real bias |
| 4 | Orphan reaping after cap-20 arm: `cline.exe` 10764, `node.exe` 18148 + `kilo.exe` 17616 still executing task work | **no** — same | same; same pathology recurred | none on window-bounded figures; establishes [F-08](#7-findings) |

### Appendix D — card supply accounting (pair-2 start state)

| quantity | per copy |
|---|---|
| tasks total | 68 |
| DONE | 24 |
| READY | 44 |
| claimable (`READY` and `attempt < max`) | 28 |
| newly created cards | 24 (`T-0045`…`T-0068`) |
| cards carrying inherited exhaustion (left BLOCKED) | 27 |
| claimable : cap ratio | 2.8× at cap 10; 1.4× at cap 20 |
| configured profiles available | 18 (identical lists in both copies) |

Symmetry was verified element-wise: identical id sets, states and attempt counts ([§5.4](#54-symmetry-verification-and-a-worthless-check-that-was-withdrawn)).

### Appendix E — commit index

Toy repository `C:\temp\projects\umaws-noscope-toy`, branch `main`, **no remote configured**. All experiment commits carry `Agent: tencent-hy4-preview | Model: tencent/hy4-preview-free (orcarouter)`.

| commit | subject |
|---|---|
| `f0d0b7f` | note the same orphan cleanup was needed after the cap-20 arm |
| `0a919d2` | record the cap-20 re-run and answer D-78 on width |
| `b771d5e` | record the cap-10 re-run, which shows the cap binding |
| `964f724` | record the second intervention that restored dispatchable supply |
| `49d396c` | record the cap-20 arm and compare it against the cap-10 control |
| `534ed85` | correct what the 48 `attempts_exhausted` blocks mean |
| `6f9ecd2` | record the cap-10 control result from the private copy |
| `b4a3f76` | let `analyze_arm.py` take `--root` instead of a hardcoded repo |
| `e7d5d72` | adopt private repository copies for arm isolation |
| `9db9b1d` | record that Arm A was void and no cap-20 arm has been measured |
| `9770c57` | void the Arm A run — shared ledger, no terminal evidence |
| `e43e148` | withdraw the 2.995 DONE/h figure; correct the baseline window to 4.024 |

Source documents this report builds on: `docs/arm-private-copy-results-2026-11-12.md` (primary results record), `docs/arm-isolation-private-copy-2026-11-12.md` (isolation protocol the checklist derives from), `docs/incident-arm0-measurement-2026-11-12.md` (baseline honesty trail), `pilot/decisions.md` (register format, D-75…D-79).
