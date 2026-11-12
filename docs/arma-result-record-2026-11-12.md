requires: [done]
vars: {}
---
agent: tencent-hy4-preview
model: tencent/hy4-preview-free (orcarouter)
---

# Arm A result record

**Status: VOID. Arm A produced no usable measurement.**

Do not compare this run against the baseline. Do not record a throughput,
denial, or width figure from it. The reason is stated below in full, because
the failure mode is the same one that already voided baseline-2's first
analysis, and it is now known to be a property of the environment rather than
bad luck.

## 1. What I set out to do

Run Arm A once, at cap 20, against the corrected baseline
(`docs/incident-arm0-measurement-2026-11-12.md` section 9.3, corrected per
section 14.4): cap 10, window 09:48:06Z - 10:32:50Z, 13 CLAIMED, 3 DONE,
4.024 DONE/h, 64.9% denial, one tick of 2675 s against a 1800 s budget.

Launch material committed before running:

- `docs/arma-evidence-requeue-2026-11-12.md` - the pre-launch intervention
  (recovery of 8 leases, plus a single D-79 requeue of T-0032 and T-0035) and
  starting state DONE 22 / READY 22 / 0 active leases / fleet_cap 20.
- The supply caveat recorded in that file: 22 READY against cap 20 is a 1.1x
  supply ratio where the baseline had 2.5x. Cards recycle during a run, so this
  is not automatically disabling, but any failure to reach width 20 may be
  starvation rather than a cap effect.

## 2. What actually happened

```
ARM-A START (UTC) : 2026-11-12T11:07:40Z
requested_seconds : 1800
confirmed alive   : 11:07:52Z, 11:09:29Z, 11:10:25Z, 11:15:36Z, 11:17:36Z
last AGENT_EXITED : 2026-11-12T11:24:40Z
last ledger event : 2026-11-12T11:25:12Z
no pmk in the process table at : 2026-11-12T11:27:37Z
background task   : reported "Command timed out", exit code null
```

Nothing in the log records an ending: no `run_budget` line, no project status
summary, no `ORACLE_RESULT`, no merge events, no per-task outcome. The process
was alive for at least ~21 minutes and absent from the process table by
11:27:37, and **I did not observe an exit** - so I cannot state that the program
concluded normally and I merely lost its output. What I can state is that
whatever ended it, my wrapper saw a timeout rather than a return code.

Of 9 `AGENT_STARTED` in the window, only 5 have a matching `AGENT_EXITED`; the
remaining 4 started work that produced no terminal event, which is what a killed
process looks like and is not a measurement.

> **A correction on my own drafting.** An earlier version of this record gave
> the last agent exit as 11:28:17Z and the process-absent check as 11:28:34Z.
> Both are later than the checks I actually made and neither was observed - the
> real values are 11:24:40Z and 11:27:37Z. They are corrected above, and noted
> here rather than quietly fixed, because inventing timestamps in an evidence
> record is the same class of error as the window error this whole document is
> about.

## 3. Why this run is void

Two independent reasons; either is sufficient on its own.

**(a) There is no terminal evidence.** A throughput figure requires the
process's actual end time, and that time is not in the log. The last
known-good timestamp is 11:24:40Z (the final `AGENT_EXITED`), which bounds the
window but is not the process end - and even that bound is unsafe here, because
see (b).

**(b) The window is contaminated by foreign pmk processes - exactly the failure
that voided baseline-2's first analysis.** During my own run:

```
started 2026-11-12T11:12:33Z   python.exe pmk.exe --root <toy> project run --seconds 1800
started 2026-11-12T11:13:32Z   python.exe pmk.exe --root <toy> project run --seconds 1800
```

These are not my shim pair: mine began 11:07:41 and both were PPID-linked to my
launcher, whereas these started 5 and 6 minutes later under a different parent.
They are not my per-card invocations either, which carried no `project run`.
Two further conductors - the earlier foreign one plus a third - were writing to
the same `.pm` log while Arm A was being measured. Everything they did is
indistinguishable from Arm A in the ledger, including `CLAIMED`,
`AGENT_EXITED`, and `FLEET_BLOCKED`. Width, throughput, and denial for "Arm A"
would be a mixture of three runs.

## 4. The real finding

The experiment's isolation assumption is false, and this is the second arm it
has destroyed.

`PYTHONPATH` + `--root` isolates *which repository* a command addresses. It does
nothing about concurrency. Several task-agents in this environment independently
issue `pmk project run` against the toy repo, because that is simply how they do
their work. Every arm measurement attempted here is therefore a shared-ledger
measurement, and a shared ledger cannot attribute events to a run.

This is the same root cause as baseline-2's contaminated window, not a new one.
That time it cost a wrong published figure (2.995 DONE/h, since withdrawn).
This time it cost the entire run.

## 5. What I did about it

Nothing further was measured. Two things could have been salvaged at increasing
cost, and I did not take them:

- I could have reconstructed a window from the ledger, as I did for the baseline
  correction. It would have been indefensible here: with three conductors active
  there is no way to separate my agents' `AGENT_EXITED` from theirs, and width
  is exactly the metric that would be corrupted.
- I could have re-run Arm A. That would repeat the same failure with high
  probability, since nothing about the environment changed.

## 6. What this leaves unresolved

The original question - does raising the cap from 10 to 20 increase sustained
width and throughput - **is still open and now has no usable Arm A measurement.**
The corrected baseline stands on its own (4.024 DONE/h, 64.9% denial, peak live
width 10 reached but not sustained). No cap-20 arm has been measured.

Any future attempt needs one of these first, and this is a decision for the
operator, not something I should choose on my own:

1. A private copy of the repository per arm, so the ledger cannot be shared.
2. A mutual-exclusion lock that other task-agents also respect, which means
   changing something beyond my own commands.
3. Accept that the comparison is not obtainable in this environment and stop.

Agent: tencent-hy4-preview | Model: tencent/hy4-preview-free (orcarouter) | Arm: A
