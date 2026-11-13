---
document:
  title: "Phase 1 — workload seeded (UMAWS no-scope experiment, toy ground)"
  status: "Phase 1 gate PASSED: 20 cards READY, sentinel clean, I1 verifies, 0 leases"
  version: "1.0.0"
provenance:
  author_llm: {name: "Tencent HY4 Preview", version: "tencent/hy4-preview-free (orcarouter)"}
  assessor_llm: []
  created_date: "2026-11-11"
  scope: "Toy repository C:\\temp\\projects\\umaws-noscope-toy only"
authority_statement: "Evidence record. Authorises no change in either repository."
---

# Phase 1 — build the ground

Executed under ratified D-75. Everything here ran with `PYTHONPATH=<toy>\src` and `--root <toy>`; the live repository was not written.

## 1. Workload shape (proposal §7.1)

Created by `tools/seed_workload.py` through `pmk.api.Kernel.task_create` — no direct `.pm/` write (I2).

- **20 cards, all `READY`:** T-0001 … T-0020.
- **14 single-owner cards** T-0001…T-0014, each writing one `workload/c<NN>-<slug>.md`, oracle `python workload/check.py <file> TOY-OK`.
- **6 deliberately overlapping cards** T-0015…T-0020: 15–17 own `shared-a.md` + `shared-b.md`; 18–20 own `shared-b.md` + `shared-c.md`. **Every pair overlaps on `shared-b.md`**, which is what makes D-L6 testable at claim time. Oracles check each card's own `SEC-<nn>` marker in both of its files.
- **One premise per card:** `P-BASE` — `workload/README.md` exists and carries `WORKLOAD-BASE`.
- **Evidence required:** `RESULT.md` per card. Budget 30 wall-min, 3 attempts, type `implement` (the first attempt used `work` and was refused with `invalid_task_type`; valid types are `implement review verify plan maintain research`).

## 2. Windows-safe oracle — proven, not assumed

`workload/check.py` takes `<file> <marker>` pairs and exits 0/1. Measured:

```
check workload\c01-inventory.md marker=TOY-OK -> FAIL      exit=1   (deliverable absent)
check workload\README.md        marker=WORKLOAD-BASE -> PASS exit=0  (premise anchor present)
```

No POSIX builtin is used anywhere, which is the defect that voided live T-0003.

## 3. First direct measurement — D-L6 binds under today's settings

Probe run against the seeded cards (leases revoked afterwards):

```
claim T-0015 (a+b)                 -> GRANTED  fence 2
claim T-0016 (a+b, overlaps T-0015) -> REFUSED  scope_overlap
claim T-0001 (disjoint)             -> GRANTED  fence 3
```

This is the first measured evidence bearing on **G-01**: write-scope disjointness *is* enforced at claim time in this build, and a disjoint card is admitted freely. It does not yet show that disjointness is the *binding* limiter on concurrency — that is what Arm-0 versus Arm A decides.

## 4. Phase 1 gate — PASSED

| Gate condition | Measured |
|---|---|
| `pmk status` green | 20 READY, 0 LEASED, 0 incidents, 0 worktrees |
| Active leases | 0 (probe leases T-0015 and T-0001 revoked; fences bumped) |
| `pmk sentinel` clean | `ok: true`, `findings: []`, checks `I1 I3 I4 I5 I6 I7 I8' I13 I14 I15 I16 I17` |
| I1 chain verifies | 53 events |

## 5. Notes carried forward

- Event counts rose 6 → 53 during Phase 1. Per D-01, this is observer effect plus seeding; **event counts are not a comparison metric**.
- The probe left two leases in place between commands before cleanup. No card was submitted or completed, no fence was violated, and both were revoked — but it is recorded here rather than left silent.
