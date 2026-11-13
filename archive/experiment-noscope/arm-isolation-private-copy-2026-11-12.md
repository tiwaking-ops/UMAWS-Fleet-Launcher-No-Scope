---
document:
  title: "Arm isolation by private repository copy"
  status: "Protocol adopted 2026-11-12 after Arm A was voided. In use."
  version: "1.0.0"
provenance:
  author_llm: {name: "Tencent HY4 Preview", version: "tencent/hy4-preview-free (orcarouter)"}
  assessor_llm: []
  created_date: "2026-11-12"
  scope: "Toy experiment only. Nothing here applies to the live repository."
authority_statement: "Protocol record. Authorises no change in either repository."
---

# Arm isolation by private repository copy

Adopted after Arm A was voided (`docs/arma-result-record-2026-11-12.md`). This
is the fix for the failure that has now cost two measurements: one withdrawn
figure and one entire arm.

## 1. Why `--root` and `PYTHONPATH` were not enough

Those two isolate **which repository** a command addresses. They do nothing
about **concurrency**. Task-agents working their own cards in this environment
independently issue `pmk project run` against the toy repository, because that
is how they do their work. What was observed inside a single Arm A window:

```
started 11:12:33Z   python.exe pmk.exe --root <toy> project run --seconds 1800
started 11:13:32Z   python.exe pmk.exe --root <toy> project run --seconds 1800
```

Three conductors writing one `.pm` ledger. `CLAIMED`, `AGENT_EXITED` and
`FLEET_BLOCKED` from all three are indistinguishable in that log, so width -
precisely what the arm existed to measure - cannot be attributed.

## 2. What changed

Each arm now runs in its own full copy of the repository, so its ledger can only
be written by its own conductor.

| arm | root | cap | config source |
|---|---|---|---|
| control | `C:\temp\projects\toy-arm-cap10` | 10 | `agents.toml` at `a12ff74` (pre-D-78) |
| Arm A | `C:\temp\projects\toy-arm-cap20` | 20 | `agents.toml` at `b66c804` (D-78 reinstated) |

Copied with everything except `work/`, `coverage/`, `.pytest_cache/` and `tmp/`,
which are lease artefacts rather than state.

**`work/` must exist in the copy even when empty.** `Conductor.drain_merge_queue`
begins its per-task loop with `if not (kernel.repo.root / "work").exists():
continue`, so a copy without that directory skips *every* integration and the arm
produces no completions at all. An empty directory is created explicitly.

## 3. Matched start

Both copies were normalised to an identical state before any run, verified in
each: release every active lease via `Kernel.revoke`, then move any task not
`DONE` or `READY` into `READY` via `Kernel.task_ready`.

Both reported exactly:

```
states        : DONE 22, READY 22
active leases : 0
SUBMITTED     : 0
moved to READY: T-0019:REWORK, T-0037:BLOCKED, T-0038:BLOCKED,
                T-0039:BLOCKED, T-0040:BLOCKED, T-0041:BLOCKED, T-0042:BLOCKED
```

Identical in both, including which tasks moved. `SUBMITTED 0` matters
specifically: an inherited submit backlog is what collapsed the first baseline
run into a single 3399.9 s tick.

## 4. Ordering

The arms run **sequentially, control first.** Running them concurrently is now
technically safe - the ledgers are separate - but the two arms place different
loads on the machine by design, and adding cross-contention would bias the
throughput comparison they exist to make. Sequential costs wall-clock and avoids
that confound.

## 5. Isolation check performed before each run

Every `python` process carrying `toy-arm-cap` in its command line is listed and
checked by root and by PPID. A clean check shows exactly one conductor and its
`pmk.exe` shim child, both bound to the arm being run. Example at the launch of
the control arm:

```
PID 10792  PPID 17628  started 11:38:59Z  root=toy-arm-cap10
PID 20324  PPID 10792  started 11:38:59Z  root=toy-arm-cap10
```

Note that the shim child is expected and is not a foreign process: `pmk.exe`
re-executes itself, which is why PPID must be checked rather than process count.

## 6. What this does not fix

It does not stop other agents working the *original* repository. That noise
continues and simply no longer reaches these arms. It also does not make the two
arms' start states anything other than what section 3 produced: 22 ready cards
against cap 20 is a 1.1x supply ratio, which may still limit Arm A for reasons
unrelated to the cap.
