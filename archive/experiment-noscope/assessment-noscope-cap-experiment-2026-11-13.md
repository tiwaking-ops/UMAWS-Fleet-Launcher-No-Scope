---
document:
  title: "Independent assessment of report-noscope-cap-experiment-2026-11-13.md"
  status: "Final. Issued to the operator. Recommendations on D-80 and D-81 are advisory; ratification remains the operator's."
  version: "1.0.0"
provenance:
  author_llm: {name: "Baidu ERNIE 5.5 Flash Preview", version: "baidu/ernie-5.5-flash-preview:free (kilo)"}
  assessor_llm: []
  created_date: "2026-11-13"
  scope: "Assessment of the report only. The experiment was not re-run. Evidence was re-derived from the ledgers of both arm copies."
authority_statement: "Assessment record. Authorises no change in any repository. Does not ratify or reject D-80 or D-81; recommends a disposition for each."
---

# Assessment — UMAWS no-scope cap experiment final report

**Subject:** `docs/report-noscope-cap-experiment-2026-11-13.md` (687 lines, commit `c0730d3`, later `de7e6a5`)
**Author of the subject (`author_llm`):** Tencent HY4 Preview — `tencent/hy4-preview-free (orcarouter)`
**Assessor (`assessor_llm`):** Baidu ERNIE 5.5 Flash Preview — `baidu/ernie-5.5-flash-preview:free (kilo)`; authored none of the subject
**Method:** every quantitative claim re-derived from the arm ledgers through `pmk.api.Kernel`; every structural claim checked against the source; every authority claim checked against the register and the git history. The report's own tooling was not used as evidence for its own numbers.
**Repos read:** `C:\temp\projects\umaws-noscope-toy`, `C:\temp\projects\toy-arm-cap10`, `C:\temp\projects\toy-arm-cap20`. The live repository was not read. Nothing was written except this document and the three edits listed at the end.

---

## Verdict

**ACCEPT THE EVIDENCE, REJECT THE FRAMING, SPLIT THE DECISIONS.**

The measurements are sound. Every headline figure reproduced exactly on independent re-derivation, including the two that were most at risk (the 4.50× produced ratio and the 19-vs-10 lease/live divergence). The report is honest about its own defects and its corrections register is accurate as far as I could test it.

Three things must change before this can be used for the live transfer the operator is negotiating:

1. **The experiment did not test what its title says.** Write-scope gating was never removed in either arm. D-76 authorises a change that does not exist in the tree. The arms ran with D-L6 fully in force, and scope never bound only because the cards were constructed with disjoint write scopes. The width result is therefore valid — arguably stronger than reported — but it is not evidence about removing scope gating, which is the live question.
2. **D-80 and D-81 are not the same kind of claim and must not be ratified together.** D-80 is measured and should be ratified. D-81 is a hypothesis about an unmeasured serial gate, drafted in the register's decision format, and should not be ratified as a decision.
3. **The report's headline is aimed at the wrong target for the operator's objective.** The operator's objective is "more than 2 concurrent LLMs in the live fleet." The report answers "does `max_total_agents` set width." On the live system the cap is not the binding constraint at 2 — scope is. The report proves 10 and 20 are reachable; it does not prove that raising a cap moves a scoped fleet past 2.

---

## Confirmed — re-derived independently

I re-implemented the metric rather than re-running the report's script, so agreement is not circular.

| Claim | Independent measurement | Result |
|---|---|---|
| Pair-2 cap 10 window 6612 s; cap 20 window 1550 s | 6612 s / 1550 s from first-to-last ledger event | ✓ exact |
| Cap 10: CLAIMED 25, started 32, exited 25, never-exited 7 | identical | ✓ |
| Cap 20: CLAIMED 25, started 33, exited 27, never-exited 6 | identical | ✓ |
| INTEGRATED 9 vs 2; SUBMITTED 18 vs 19 | identical | ✓ |
| Max live width 10 vs 20; neither exceeded its ceiling | max concurrency 10 / 20 | ✓ |
| % of window at level: cap 10 at ≥10 = 92.4%, ≥8 = 93.7%, ≥5 = 95.9%, ≥2 = 98.5% | identical to one decimal | ✓ |
| Cap 20 at ≥20 = 56.2%, ≥15 = 76.1%, ≥11 = 80.5%, ≥10 = 81.5% | identical to one decimal | ✓ |
| Landed 4.900/h vs 4.645/h; produced 9.800/h vs 44.129/h | 4.900 / 4.645 / 9.800 / 44.129 | ✓ |
| Denial 57/82 = 69.5% in both pair-2 arms | 25 CLAIMED + 57 FLEET_BLOCKED + 0 LEASE_REFUSED = 82; 57 denials | ✓ |
| Lease-based width overstates live: 19 vs 10 (F-02) | max lease concurrency 19, live 10, same window | ✓ |
| Sentinel `[]` exit 0 in both arms; 0 INCIDENT, 0 QUARANTINED | no such events in either window | ✓ |
| Toy repo has no git remote | `git remote -v` empty | ✓ |
| `dispatcher.py:270` is `if len(self.runs) >= cap:` | line 270, verbatim | ✓ |

Two derived relationships worth stating explicitly, because they are the load-bearing ones and they hold:

- **The produced ratio is the window ratio.** 44.129 / 9.800 = 4.503. 6612 / 1550 = 4.266. The "4.5× faster" figure is almost entirely the two arms having different window lengths; the absolute counts are 18 vs 19. This does not falsify F-03 — the pipeline genuinely did not land the extra work — but the report presents 4.50× as a production-rate finding when it is substantially a denominator artefact. It should be restated with absolute counts beside the rate, which the report does elsewhere (§4.3 terminal state) but not in §1 or §8.
- **The gate, not the cap, sets the landed rate.** 9 landed in 1.8367 h = 4.900/h; 2 landed in 0.4306 h = 4.645/h. Two arms with different caps, different windows and different tick structures produced the same landing rate to within 5%. That is the strongest single piece of evidence in the report and it is currently buried in §4.3.

---

## Corrections to the subject

### C-A1 — "Unexplained coincidence" (F-11) is fully explained and should be closed

The report flags byte-identical denial (57/82 in both arms) as "implausible as a coincidence" and leaves U-04 open.

It is not a coincidence and it does not need explaining; it is deterministic. Both copies began from the same start state (verified by the report's own element-wise check: 68 vs 68 ids, no state or attempt mismatches, 27 claimable each). The 57 denials are 19 distinct exhausted cards refused 3 times each — I confirmed the `(subject, blocker)` multiset is **identical** between arms, 19 keys, 3 refusals per key, zero differing entries. Given an identical start state and a deterministic refusal rule, identical denial counts are the predicted outcome, not an anomaly.

**Effect:** U-04 can be resolved as "denial is a pure function of the start state; it carries no cap signal" — which is what the report already suspects, but now as a finding rather than a mystery. No conclusion in the report changes. The report is being more cautious than the evidence requires.

### C-A2 — Write-scope gating was never removed; D-76 authorises a change that does not exist

This is the most serious finding in this assessment.

D-76 (ratified 2026-11-13) authorises Arm A to disable, among other things, the write-scope conflict refusal at claim. Measured state of both arm copies and the toy tree:

- `src/pmk/api.py:517` — `allow_scope_conflict: bool = False`, and **no caller anywhere in `src/` passes `True`**. The parameter exists; the switch is never thrown.
- `src/pmk/api.py:553-557` — the D-L6 refusal is live and raises `scope_overlap`.
- `src/fleet/overseer.py:73-74` — the Overseer is still instructed that "Cards that should run at the same time must have disjoint write scopes."
- `src/fleet/merge.py:247-250` — the blocking bundle scope check is still in place.
- Both arm copies are byte-identical to the toy tree in `src/fleet/` (`git diff --stat HEAD -- src/fleet` empty in the cap-10 copy).

**What actually happened instead:** the 24 substitute cards were each given a distinct write path (`workload/c45-freshprobe.md` … 24 distinct paths, zero overlap). Scope was satisfied by construction, so D-L6 never had anything to refuse. Width then followed the cap. That is a clean measurement of the cap — and it is a measurement of a fleet whose scopes never conflicted, not of a fleet with scope gating removed.

**Why this matters for the live transfer.** The live system's problem is that scope-locking holds it at 2. This experiment cannot speak to that, because the mechanism it removed was never removed. The report never claims otherwise — it is silent on the point, and "no-scope" in the title is inherited from the proposal rather than earned by the arms. But a reader who takes the title and §1 at face value will conclude the experiment demonstrated that removing scope gating raises width. It did not.

**Required change:** §1 and §13 must state plainly that D-L6 remained in force in both arms, that scope was satisfied by disjoint card construction, and that the experiment is therefore evidence about the cap under non-conflicting scopes only. TC-1's transfer evidence requirement should be amended to include a scoped-conflict condition.

### C-A3 — Two configuration values differ between the arms, not one

The cap-20 copy carries `max_concurrent = 2` on every profile; the cap-10 copy carries `max_concurrent = 1`. The report describes the comparison as cap 10 vs cap 20 and never mentions this.

It is not a live confound here — 18 profiles × 1 = 18 ≥ 10, and 18 × 2 = 36 ≥ 20, so neither profile limit could bind in either arm — but it is an undeclared difference between the arms and belongs in §3.1's isolation table.

### C-A4 — Appendix A overstates what the cited script produces

Appendix A says the one-pass script recomputes "stepwise concurrency, max concurrency and % of window at or above each level." The script at `%TEMP%\armstats.py` prints only the **max** level and the percentage at that max (`>=max for %`). The full curve in §4.2 — ≥2, ≥5, ≥8, ≥10, ≥11, ≥15, ≥20 — is **not** produced by the cited tool.

I reproduced §4.2 independently (table above), so the figures are correct. But a third party following Appendix A cannot reproduce them, which is the one thing Appendix A exists for.

### C-A5 — The report's own REC-20 is violated by the tool that produced its numbers

REC-20 requires any ledger-reading tool to take `--root` explicitly and fail loudly otherwise, because silent cross-repository reads produce plausible wrong output. `armstats.py` hardcodes all five roots at module level (lines 37-39) and takes no arguments. It is also not in the repository — it lives in `%TEMP%` and will not survive a temp cleanup.

The report cites this script as the provenance of every figure and simultaneously recommends a rule the script breaks. Either the script becomes a deliverable in `tools/` with `--root`, or Appendix A should state that its figures are reproducible only from the ledgers directly.

### C-A6 — F-10 is now measurable and the answer is negative at ledger level

F-10 says orphaned agents may write after their window closes, and U-07 says this was never measured. I measured it: in both arm ledgers, the only event after the window closes is a single `SENTINEL_RUN` (cap 10 at 22:15:28Z, 40 s after close; cap 20 at 22:45:46Z, 40 s after close). No claim, agent, submit, integrate or write event follows either window.

So at ledger level, orphans were alive after close but wrote nothing that reached the ledger. F-10's risk is downgraded from "unmeasured" to "measured and not observed at ledger level." It is not eliminated — an agent writing inside a worktree would not necessarily emit an event — so REC-25 should stay, but its rationale changes from "unknown" to "checked once, clean."

---

## On the decisions

### D-80 — recommend RATIFY, with one amendment

The decision text is measured, correctly scoped to live runs, and explicitly rejects lease-based width. Everything in it reproduced. The amendment: it should record that the measurement was taken **with D-L6 in force and disjoint card scopes** (C-A2), because otherwise it reads as a claim about unconstrained fleets.

### D-81 — recommend DO NOT RATIFY as a decision; convert to a finding plus an experiment

The decision sentence is "Raising width beyond integration's capacity does not increase landed throughput and should not be relied on to do so." The report itself lists, in D-81's own unknowns, that the serial-merge hypothesis is untested and that unequal windows prevent the measurement. A decision record whose central claim its own unknowns list calls untested is mislabelled.

What *is* supported: landed rate was flat across two very different windows (4.900 vs 4.645/h) while produced diverged — that is a real, reproduced observation and belongs as a finding, not a decision.

What would justify the decision: instrument `drain_merge_queue` and measure lands/h against produced/h at a fixed cap over an equal window. That is Option B, which the report already recommends first. The correct move is to keep Option B ahead of any D-81 ratification.

---

## On the report as an artefact

**Length and structure.** 687 lines, 14 sections, for one measured result and one non-result. It is well-organised and the corrections register is genuinely good practice. But §5, §6, §11 and §12.2 are all machinery for future experiments, and the operator's stated purpose is (a) close out D-78 and (b) support a live transfer. Those two purposes are served by roughly §1, §3, §4, §8 and §13. If this document is also the protocol manual (the operator's answer was "all three"), the length is justified and the structure is right — in which case it needs a one-page decision brief in front, because a reader with 5 minutes currently gets the voided pair before the width result.

**§1 ordering.** The executive summary leads with the width win and puts the voided pair and the unbounded windows in bullets three and four. The operator asked for honest; honest ordering here is result, then what could not be answered, then what was voided and why. Currently a reader who stops after the first bullet has a defensible but incomplete picture.

**What the report gets right and should not lose:** the corrections register (§6), the measured/derived/guess labelling on every finding, the refusal to compare totals across unequal windows, and §13's per-row evidence requirements for transfer. These are better than typical and should survive any shortening.

---

## Required addendum to the subject report

1. **§1, §2, §13:** state that D-L6 remained in force in both arms; scope was satisfied by disjoint card construction; the experiment is evidence about the cap under non-conflicting scopes only. Amend TC-1's required-evidence row to include a scoped-conflict condition.
2. **§3.1:** add the `max_concurrent` 1-vs-2 difference between arms to the isolation table (C-A3).
3. **§4.3 / §8:** restate the produced ratio with absolute counts beside the rate; lead the throughput section with the flat landed rate (4.900 vs 4.645/h), which is the strongest evidence present.
4. **F-11 / U-04:** close as explained (C-A1).
5. **F-10 / U-07:** restate as measured at ledger level, clean (C-A6).
6. **Appendix A:** correct the description of what `armstats.py` outputs, and either commit the script to `tools/` with `--root` (per the report's own REC-20) or state that the figures are reproducible only from the ledgers.
7. **§9:** mark D-80 and D-81 with their different dispositions (ratify / hold for Option B), rather than presenting them as a pair.
8. **Front matter:** replace `assessor_llm: []` and the "UNASSESSED" banner with a reference to this document.

---

## Recommended next actions

| # | action | owner |
|---|---|---|
| 1 | Ratify D-80 with the C-A2 amendment | operator |
| 2 | Do not ratify D-81; hold for Option B evidence | operator |
| 3 | Correct the subject report per the addendum above | executor |
| 4 | Run Option B (instrument `drain_merge_queue`, fixed cap, equal bounded window) before any further width work | executor |
| 5 | If the live question is "more than 2", the next experiment must run with D-L6 **enforced** and scopes deliberately overlapping — that is the condition this experiment did not create | executor |

**Standing caution.** Nothing in this assessment applies to `C:\temp\projects\testproject1`. No live file was read or written. The toy repository has no remote and nothing was pushed.

---

*assessor_llm: Baidu ERNIE 5.5 Flash Preview (opencode). Author of record for the subject report remains Tencent HY4 Preview. This assessment is independent of the author, re-derives its evidence from the arm ledgers rather than from the subject's tooling, and was produced without re-running the experiment. Stored uncommitted; commit is an operator decision.*