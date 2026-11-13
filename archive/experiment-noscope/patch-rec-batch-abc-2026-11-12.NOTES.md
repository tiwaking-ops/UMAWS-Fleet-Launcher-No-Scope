---
document:
  title: "Batch A/B/C patch — reference only, and why it will not apply to the live repo"
  status: "Measured. Reference-only handover; authorises no change in either repository."
  version: "1.0.0"
provenance:
  author_llm: {name: "Tencent HY4 Preview", version: "tencent/hy4-preview-free (orcarouter)"}
  assessor_llm: []
  created_date: "2026-11-12"
  scope: "Toy repository C:\\temp\\projects\\umaws-noscope-toy only"
authority_statement: "Advisory. Authorises no change in either repository. Nothing here has been applied to the live repo."
---

# Batch A/B/C patch — reference only

Companion to `patch-rec-batch-abc-2026-11-12.patch`. Read this before trying to
apply that patch.

**Operator decision (2026-11-12): ship the patch as reference only.** No attempt
is made to apply it to `C:\temp\projects\testproject1`, and nothing has been
written there.

## 1. What the patch is

Ten files, 522 insertions, 39 deletions, covering REC-03/04/05/06/07/10/11/12/13/14/15:

| File | REC |
|---|---|
| `agents.toml` | REC-13 |
| `src/fleet/conductor.py` | REC-10 |
| `src/fleet/dispatcher.py` | REC-03 |
| `src/fleet/merge.py` | REC-10 |
| `src/fleet/overseer.py` | REC-04 |
| `src/pmk/cli.py` | REC-06, REC-15 |
| `tests/fleet/test_identity_guard.py` | REC-10 (tests) |
| `tests/pmk/test_run_bounded.py` | REC-15 (tests, new) |
| `tools/analyze_arm.py` | REC-07, REC-11, REC-12, REC-14 |
| `tools/preflight.py` | REC-05 (new) |

Verified **self-consistent**: `git apply --check` against a clean worktree at its
own base (`a12ff74`) exits 0. It is well-formed. That is the only kind of
cleanliness it has.

## 2. Why it will not apply to the live repo

Every file the patch touches that also exists in the live repo has **genuinely
diverged** from the toy base. This was checked twice, because "it must just be
line endings" was the first hypothesis and it is wrong:

- Both sides are LF-only (CR census: toy base 0 CR-terminated lines; live 0 CRLF,
  728 / 1414 / 418 bare LF for `conductor.py`, `cli.py`, `agents.toml`).
- Comparing with all CR stripped **still** differs, so the divergence is content.

| File in live | vs toy base |
|---|---|
| `agents.toml` | differs (live lacks `stall_minutes`; different cap history) |
| `src/fleet/conductor.py` | differs |
| `src/fleet/dispatcher.py` | differs |
| `src/fleet/merge.py` | differs |
| `src/fleet/overseer.py` | differs |
| `src/pmk/cli.py` | differs |
| `tests/fleet/test_identity_guard.py` | differs |

Three targets **do not exist in live at all**: `tools/analyze_arm.py`,
`tools/preflight.py`, `tests/pmk/test_run_bounded.py`.

The live working tree also carried **522 dirty entries** at the time of writing.
Anything generated "against live" is a snapshot of a moving target.

## 3. The changes are still portable

Every edit anchor exists in the live repo, so a live-based equivalent is
possible if you want one later:

| Anchor | Live occurrences |
|---|---|
| `cmd_project_run` (`src/pmk/cli.py`) | 2 |
| `deadline = time.time() + args.seconds` | 1 |
| `def cmd_dispatch_run` | 1 |
| `PIPELINE_IDENTITY` (`src/fleet/merge.py`) | 3 |
| `def commit_worktree` | 1 |
| `def integrate` | 1 |
| `def status` (`src/fleet/dispatcher.py`) | 1 |
| `slots_in_use` | 1 |
| `max_total_agents` (`src/fleet/overseer.py`) | 1 |
| `tree root` (`src/fleet/overseer.py`) | 1 |
| `def drain_merge_queue` (`src/fleet/conductor.py`) | 1 |

And none of the new identifiers are present in live yet, so there is no risk of
applying the same change twice: `_warn_dispatch_run`, `run_bounded`, `live_runs`,
`provenance_trailer`, `--requested-seconds` — all 0 hits.

## 4. Correction to the record

The patch committed earlier as `d4ce7e0` was defective and has been replaced by
`a6a172c`. Three defects, all found only by actually testing it:

1. It was written **UTF-16LE** (PowerShell's `>` operator), so `git apply`
   refused it with `No valid patches in input`. It was unusable. Now UTF-8
   without BOM.
2. It **contained itself**, because it was generated from a range that already
   included the commit adding it.
3. It carried `src/fleet/precheck.py`, a 42-line change that is **not any REC
   item**. It is excluded from the rebuilt patch.

Relatedly, commit `cb0b6b5` is **mislabelled**: it says "record sentinel runs
appended during verification", but it also carries that same 42-line
`precheck.py` change. I described it wrongly when committing it. The change
itself looks like legitimate read-only-scratch-directory cleanup, but it was not
part of Batch A/B/C and is deliberately not in this patch.
