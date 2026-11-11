---
document:
  title: "Phase 0 verification — UMAWS no-scope experiment (toy ground)"
  status: "Executed Phase 0 verification. Phase 0 gate NOT passed — blocked on operator re-confirmation of OR-01…OR-15 and authorisation of the D-series decisions."
  version: "1.0.0"
provenance:
  author_llm: {name: "Tencent HY4 Preview", version: "tencent/hy4-preview-free (orcarouter)"}
  assessor_llm: []
  created_date: "2026-11-11"
  scope: "Toy repository C:\\temp\\projects\\umaws-noscope-toy; live repository C:\\temp\\projects\\testproject1 read-only"
authority_statement: "Evidence record only. Authorises nothing in either repository. Class-K items remain operator actions per proposal §9."
---

# Phase 0 verification

**Executor:** Tencent HY4 Preview (`tencent/hy4-preview-free`), OpenCode session, 2026-11-11.
**Specification:** `docs/plans/proposal-UMAWS-Fleet-Launcher-No-Scope-v1.md` in the live repo (read-only reference).
**Working root:** `C:\temp\projects\umaws-noscope-toy`. Every `pmk` invocation below used `--root <toy>` **and** `PYTHONPATH=<toy>\src`.

## 1. Verification of the scaffold (claimed done, re-measured)

| Claim | Measured | Verdict |
|---|---|---|
| Toy repo exists | yes | verified |
| `git init` on `main` | `main`, HEAD `64ddfd1` | verified |
| Two commits | `e244a9f`, `64ddfd1` | verified |
| Clean tree | `git status --porcelain` count = 0 | verified |
| Own `.pm/` | present: `events evidence tasks views conflicts quarantine registry fleet memory briefings nohooks` | verified |
| Ledger at 1 event | **5 events** | **DISCREPANCY — see D-01** |
| `constitution.md` present | yes | verified |
| `policy.toml` present | yes | verified |
| `pins.sha256` re-recorded | `pins check` → `{"ok": true, "mismatches": [], "checked": 2}` | verified |
| 0 worktrees | `pmk status` → `worktrees: {count: 0, bytes: 0}` | verified |
| No remote | `git remote -v` count = 0 | verified |
| `import pmk` resolves to toy `src/` | `C:\temp\projects\umaws-noscope-toy\src\pmk\__init__.py` | verified — closes G-07 |
| Sentinel clean | `pmk sentinel` → `{"ok": true, "findings": []}`, checks `I1 I3 I4 I5 I6 I7 I8' I13 I14 I15 I16 I17` | verified |
| I1 chain verifies | `pmk status` → `I1 chain verifies (5 events)` | verified |

### D-01 — ledger is at 5 events, not 1

The scaffold left the ledger at 1 event (`BOOTSTRAP_IMPORTED`). It is now 5:

```
1 BOOTSTRAP_IMPORTED  actor=kernel
2 PINS_CHECKED        actor=human
3 PINS_CHECKED        actor=kernel
4 PINS_CHECKED        actor=kernel
5 SENTINEL_RUN        actor=kernel
```

Cause: my own Phase 0 verification. `pmk pins record`, `pmk pins check` and `pmk sentinel` **append events** — reads in this kernel are not uniformly read-only.

**Consequence for instrumentation (must carry into Phases 2/4/7):** the ledger's event count cannot be used as a progress or comparison signal, because the observer perturbs it. Arm start/stop markers must be explicit recorded decisions, and the four §10.1 metrics must be derived from `DONE` timestamps and lease pairs, not from raw sequence numbers.

No I1, I8 or I13 violation is present; this is a counting artefact, not an integrity failure. Recorded for the report rather than corrected.

### D-02 — first Phase 0 commit was a partial add (corrected)

`32b3a1c` staged only the two `docs/` paths, so the kernel-generated changes already on disk (events 4–5 and the re-rendered `.pm/views/status.md`, whose policy version moved `p-unset` → `p-2026-10-23`) were left out and showed as modified. Investigated as a possible background writer: **no** — there are no active git hooks in the toy repo (only `*.sample`), no `core.hooksPath` local or global, and the event count stayed at 5 across repeated reads. Cause was my own staging scope. Committed as kernel output in the next commit; I2 is unaffected because `.pm/` was never hand-edited.

## 2. Protective capture of the live repository (read-only)

Captured before any phase runs, per Phase 0:

- HEAD: `afcc0ba1046a74a1e8407c0b47deda3b8c72ae6b`, branch `main`
- Uncommitted-diff patch written to this repo: `docs/live-protective-patch-2026-11-11.patch` (644 124 bytes)
- Dirty paths at capture: 520
- Live `pmk status` at capture:

```json
{"root":"C:\\temp\\projects\\testproject1","project_state":"PAUSED",
 "tasks":{"VOID":156,"DONE":43,"READY":13},"task_total":212,
 "active_leases":0,"open_queue_items":0,"incidents":104,"stopped":false,
 "chain":"I1 chain verifies (3639 events)",
 "worktrees":{"count":21,"bytes":330795045,"dirty":null}}
```

No write, no commit and no `pmk` state change was made against the live repository. Only `git rev-parse`, `git status`, `git diff` and `pmk status` were run there.

### O-01 — the live repository is moving during this session

Across three observations today the live repo changed on its own:

| Signal | Earlier today | At Phase 0 capture |
|---|---|---|
| Events | 3 634 (authoring) → 3 637 | 3 639 |
| Worktrees | 35 (485 323 582 B) | 21 (330 795 045 B) |
| Active leases | 2 | 0 |
| READY | 12 → 11 | 13 |
| Dirty paths | 513 | 520 |

Something outside this experiment is mutating the live tree. None of it is attributable to these commands (the toy root was used for every state-changing call), but it means: (a) the protective patch is a point-in-time snapshot that decays, and (b) the proposal §4 baseline table is stale and must not be quoted as current. Flagged for the operator to confirm whether a cleanup or another agent is running.

## 3. Blocking items — operator only

Phase 0 cannot gate green until these are resolved. None is self-grantable.

1. **Re-confirm OR-01…OR-15.** They exist only in the authoring conversation, not in any file in either repository.
2. **Authorise one decision record per arm** (D-series) in this toy repo.
3. **Approve the Arm A authorising order text (proposal §7.4) and the `OVERSEER_PROMPT` relaxations** before Phase 3, key taken before the change (§9).
4. **Approve the H1 exception** for main-tree leases before Phase 6 — toy-only, Arm B only, recorded as an exception.
5. **Decide on G-08** — only `src/`, `tests/`, `docs/`, `agents.toml`, `pyproject.toml`, `pytest.ini`, `AGENTS.md`, `CLAUDE.md`, `README.md` were copied. `gateway/`, `pilot/`, `tools/` are absent and Phase 1 may need them.

## 4. Gate status

**Phase 0 gate: NOT PASSED — scaffold OK, operator items outstanding.**

Verified at the end of Phase 0: tree clean (`dirty=0`), HEAD `eacee26`, `pmk sentinel` clean with no findings across `I1 I3 I4 I5 I6 I7 I8' I13 I14 I15 I16 I17`, `I1 chain verifies (5 events)`, 0 tasks, 0 worktrees, 0 incidents, no remote.

No integration violation occurred. No phase beyond Phase 0 has been started; no configuration in the toy repo has been altered since the scaffold commits. The gate is held open only by the operator items in §3.
