---
document:
  title: "Operator decision: untracked workload/c42-fog-of-war.md, and worktree reclamation"
  status: "Decided and applied. Reversible: the artifact is preserved, not deleted."
  version: "1.0.0"
provenance:
  author_llm: {name: "opencode", version: "baidu/ernie-5.5-flash-preview:free"}
  assessor_llm: []
  created_date: "2026-11-13"
  scope: "Toy repository C:\\temp\\projects\\umaws-noscope-toy only"
authority_statement: "Records an operator-authorised cleanup. Changes no gate, no policy, and no arm protocol."
---

# Untracked `workload/c42-fog-of-war.md` and worktree reclamation

Two items cleared because they were blocking dispatch. Both were authorised by
the operator on 2026-11-13 ("start: worktree reclaim and the c42 decision").

## 1. `workload/c42-fog-of-war.md` — moved out of the main tree

### What it was

An untracked file in the main tree, 3,007 bytes, mtime 2026-11-12T10:50:38Z.
It is a complete card body for card 42 and it passes its card oracle:

```
$ python workload/check.py workload/c42-fog-of-war.md TOY-OK
check workload/c42-fog-of-war.md marker=TOY-OK -> PASS
```

No evidence bundle (`EB-T-0044-*`) exists and no commit ever contained it.

### Where it came from

| Time (UTC) | Event |
|---|---|
| 2026-11-12T04:00:46Z | `TASK_CREATED` T-0044 |
| 2026-11-12T10:03:25Z | `CLAIMED` T-0044, fence 80 |
| 2026-11-12T10:34:43Z | `REVOKED` — baseline-2 orphan cleanup |
| 2026-11-12T10:44:52Z | `AGENT_EXITED` OK, then `FIX_ROUND` (c42 oracle failed) |
| 2026-11-12T10:44:55Z | `AGENT_STARTED` again, in the run later voided as Arm A's predecessor |
| 2026-11-12T10:50:38Z | file mtime — rewritten, oracle then passed |
| 2026-11-12T11:10:19Z | `SCOPE_CONFLICT` + `FLEET_BLOCKED` on this path |
| 2026-11-12T11:25:12Z | same blocker, last occurrence |

The agent wrote its deliverable into the **main tree** instead of its worktree.
Because T-0044 never integrated, the file was never committed, and from 11:10:19Z
it blocked T-0044 from being leased at all.

### Decision: preserve, do not commit

Moved to `stranded/T-0044-c42-fog-of-war.md`, with the full reconstruction in
`stranded/T-0044-c42-fog-of-war.NOTE.md`.

Not committed to `main`, for three reasons:

1. **Provenance.** The pipeline is the only legitimate path to `main`. This file
   has no author, no bundle and no commit; committing it would place unattributed
   work on `main` outside the pipeline.
2. **It came from a voided run.** The write happened inside the run voided for
   shared-ledger contamination; promoting its output would let a voided run shape
   repository state.
3. **Supply.** Committing it would make T-0044 "already satisfied on main" and
   remove it from the dispatchable pool, which is the constraint the current arms
   are short of.

Preserved rather than deleted, so it can be put back if the operator prefers.

### Effect

`workload/` is clean; T-0044 is dispatchable. The same file still exists in both
private copies (`toy-arm-cap10`, `toy-arm-cap20`). It is **left there**: it is
symmetric between the two arms and removing it would change a running arm's
start state.

## 2. Worktree reclamation

31 worktrees / 306.3 MiB → **4 worktrees / 0.0 MiB**, with the main repo at 0
active leases.

- **17 dirty trees reclaimed capture-first** to `stranded/` (REC-02):
  T-0001-19, T-0001-4, T-0002-20, T-0002-5, T-0003-21, T-0003-6, T-0004-7,
  T-0008-11, T-0009-12, T-0010-28, T-0019-81, T-0035-82, T-0037-90, T-0038-91,
  T-0039-92, T-0040-86, T-0040-93.
- **14 clean trees pruned**: T-0013-34, T-0019-89, T-0020-97, T-0035-66,
  T-0037-83, T-0038-84, T-0039-85, T-0041-87, T-0041-94, T-0042-88, T-0042-95,
  T-0043-79, T-0043-96, T-0044-80.

Four empty directory stubs remain registered (T-0013-34, T-0035-66, T-0043-79,
T-0044-80), 0 bytes each. They are harmless and left in place rather than
deleting paths the Kernel still lists.

`stranded/` now holds 94 directories, ~2 MB — the capture excludes `.git`, so the
per-tree "10.4 MiB" was almost entirely checkout, not content.

Integrity after both actions: `pmk sentinel` → `ok: true, findings: []`;
`pmk pins check` → `ok: true, mismatches: []`; active leases 0; tasks unchanged
at READY 15 / DONE 22 / REWORK 1 / BLOCKED 6 of 44.

## 3. Related: `tmp/arma.out` committed

`docs/arma-result-record-2026-11-12.md` §7 and the incident report §9.4 cite
`tmp/arma.out` as the terminal evidence for Arm A. `tmp/` is not gitignored but
was untracked, so the citation pointed at a file with no durable copy. It is
committed here alongside this record.