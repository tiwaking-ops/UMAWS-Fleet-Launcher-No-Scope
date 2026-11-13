---
document:
  title: "Baseline correction — max_total_agents (proposal §4)"
  status: "Correction to a recorded number; measured value now differs"
  version: "1.0.0"
provenance:
  author_llm: {name: "Tencent HY4 Preview", version: "tencent/hy4-preview-free (orcarouter)"}
  assessor_llm: []
  created_date: "2026-11-12"
  scope: "Toy repository C:\\temp\\projects\\umaws-noscope-toy (agents.toml copied verbatim from the live repo)"
authority_statement: "Evidence record. Corrects a number; authorises nothing."
---

# Correction: `max_total_agents` is 10, not 100

The proposal's §4 baseline table records:

> | `max_total_agents` | 100 (`agents.toml`, operator's D-50 edit) | `Dispatcher.max_total_agents()` |

Measured on 2026-11-12 from `agents.toml` in the toy repository — a verbatim copy of the live file:

```
line 22: max_total_agents   = 10        # Reduced from 100: free models too slow at high
                                        # concurrency. Sun Nov 01 20:49:25 NZDT 2026
                                        # Tiwa has increased this from 6 to 10
```

So the ceiling was **raised 6 → 10, not raised to 100**. The file's own comment says 100 was reduced *because* free models are slow at high concurrency — i.e. the 100 figure was historically real but deliberately lowered.

Also measured, and not in the proposal at all:

- 18 profiles are declared.
- Per-profile `max_concurrent` sums to **20** (one profile carries 3, seventeen carry 1).
- `Dispatcher` caps at `max_total_agents` (`dispatcher.py:238`, `:420`), so today's effective concurrency ceiling is **min(10, 20) = 10**.

**Why this matters to the experiment.** OR-04 targets 12–20 concurrent workers. Today's configuration cannot reach even 12 without changing `max_total_agents` — and Phase 3 (§7.2) explicitly warns that raising per-profile `max_concurrent` alone is insufficient for that same reason. So Arm A's configuration change list must include `max_total_agents`, which §7.2 currently does not name. That is an amendment to the execute order, flagged here rather than improvised.

It also sharpens G-05 and R-G1: the project has never demonstrated above six live, and the declared cap is ten; 12–20 requires a change the proposal only partially specified.

## Addendum 2026-11-12 (same day) — the "effective ceiling = 10" inference was wrong

The sentence above concludes *"today's effective concurrency ceiling is min(10, 20) = 10."* The Arm-0 validation run contradicts it and it is withdrawn.

Measured, 300-second `dispatch run`:

```
fleet_cap: 10        slots_in_use: 9        active leases: 15
```

Fifteen simultaneous leases under a cap of ten. Reading `dispatcher.py` explains why rather than excusing it: the cap is compared against `len(self.runs)` — the dispatcher's **in-memory run set** (`dispatcher.py:238` `_fill`, `:420` profile selection). An entry leaves `self.runs` when `poll()` returns a result (`dispatcher.py:207` `del self.runs[task_id]`), but the **kernel lease survives** until the task is completed or revoked. So the cap bounds *tracked runs*, not *held leases*, and leases can accumulate past it.

Consequences for the experiment:

- `max_total_agents` is **not** a reliable predictor of concurrent leases. Width must be measured from lease pairs (as §10.1 already requires), never inferred from configuration.
- The correction to the §4 baseline number itself still stands: the value is **10, not 100**. Only the inference drawn from it is withdrawn.
- This is adjacent to the risk the proposal already names as **R-A4** (`max_concurrent` per profile silently caps width) but is not the same defect; it deserves its own note rather than being folded into R-A4.
