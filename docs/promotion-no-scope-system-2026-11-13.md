---
document:
  title: "Promotion record — UMAWS-Fleet-Launcher-No-Scope-System"
  status: "Final. Executed by the operator's agent under operator approval."
  version: "1.0.0"
provenance:
  author_llm: {name: "Baidu ERNIE 5.5 Flash Preview", version: "baidu/ernie-5.5-flash-preview:free (kilo)"}
  assessor_llm: []
  created_date: "2026-11-13"
authority_statement: "Records the operator's promotion of the no-scope toy repository into the permanent UMAWS Fleet Launcher No-Scope project folder. Authorises the archive and verification steps recorded here. Does not modify the constitution or policy."
---

# Promotion record — UMAWS-Fleet-Launcher-No-Scope-System

**Operator (approver):** Tiwa Pene (Human)
**Reason (operator's words):** "UMAWS-Fleet-Launcher-No-Scope-System project promotion"
**Date approved:** 2026-11-13

## What is being promoted

The folder `C:\temp\projects\umaws-noscope-toy` — previously the no-scope
experiment's isolated toy repository — is promoted to the **permanent project
folder** for the UMAWS Fleet Launcher No-Scope System.

The folder name `umaws-noscope-toy` is **retained** (operator decision), for
history continuity. The name is a historical label; the folder is no longer a
throwaway.

## Commits covered by this promotion

| Commit | Meaning |
|---|---|
| `8052dca` | Pre-sync checkpoint — the toy's original state (rollback point). |
| `36c48d2` | Port of testproject1 Fleet hardening (authority gate, scratch, worktree lifecycle, gate timeout, REC-03/04/06/10/15 fixes preserved). 1343 tests green. |

## Decisions applied

- **Folder name:** keep `umaws-noscope-toy`. APPROVED.
- **Step 2 (archive experiment residue):** APPROVED.
- **Step 3 (fresh project state):** option **3a** — keep the `.pm/` event log
  intact; start a new project on top of it. APPROVED.
- **Step 4 (rebuild & verify):** APPROVED.

## Provenance and constraints honoured

- Constitution rule 8 ("Never delete artifacts. Supersede or quarantine"):
  the archive uses `git mv`, so nothing is deleted and history follows.
- The `.pm/events/` append-only hash chain is **not rewritten**; the old
  experiment events remain as the audit trail (step 3a).

## Live repository

`https://github.com/tiwaking-ops/UMAWS-Fleet-Launcher-No-Scope`
(Apache-2.0; at promotion time it held only the LICENSE and a one-line
description). Syncing this folder to that remote is a separate operator step.

---

*author_llm: Baidu ERNIE 5.5 Flash Preview (opencode). Produced under the operator's written approval; not a self-assessment.*