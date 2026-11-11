---
document:
  title: "Arm-0 method error — dispatch run cannot reach DONE"
  status: "Methodological correction; two published numbers withdrawn"
  version: "1.0.0"
provenance:
  author_llm: {name: "Tencent HY4 Preview", version: "tencent/hy4-preview-free (orcarouter)"}
  assessor_llm: []
  created_date: "2026-11-12"
  scope: "Toy repository C:\\temp\\projects\\umaws-noscope-toy only"
authority_statement: "Evidence record. Authorises no change in either repository."
---

# Arm-0 ran the wrong supervision loop

On 2026-11-12 the Arm-0 baseline was run twice with `pmk dispatch run --seconds N`
(300 s, then 900 s, then 1800 s). **That is the Dispatcher alone.** Two claims I
made from those runs were wrong and are withdrawn here.

## 1. What `dispatch run` actually is

`pmk/cli.py:815` `cmd_project_run` builds all three components and ticks them:

```python
dispatcher = Dispatcher(kernel, fleet_state, ...)
overseer   = OverseerRunner(kernel, fleet_state)
conductor  = Conductor(kernel, dispatcher, overseer)
while time.time() < deadline:
    conductor.tick()
    dispatcher.tick()
```

`pmk dispatch run` constructs only `Dispatcher` and ticks only that. The
**Conductor** owns everything downstream of SUBMITTED — `conductor.py:673`:

```python
merged = self.drain_merge_queue()      # SUBMITTED -> verified -> integrated -> DONE
reaped = self.reap_expired_leases()    # clears orphaned leases
advanced = self.advance()              # project lifecycle
```

Neither exists in the Dispatcher path.

## 2. Numbers withdrawn

| Claim made | Status |
|---|---|
| "Throughput = 0 `DONE` per wall-hour" | **Withdrawn.** An artefact of never running the merge queue, not a baseline property. |
| "The fleet wedges permanently; 12 leases orphaned" | **Withdrawn as a baseline property.** `Conductor.reap_expired_leases()` clears it. The wedge was real but self-inflicted — I ran without the component that reaps. |

## 3. Numbers that stand

These were measured from lease pairs and do not depend on which loop ran:

- Peak concurrent leases **15**, sustained **>= 60 s** — above the declared
  `fleet_cap` of 10 (see the addendum in
  `docs/baseline-correction-max-total-agents-2026-11-12.md`).
- 14 of 14 disjoint cards dispatched; 1 of 6 overlapping cards (T-0015).
- 8 cards reached `SUBMITTED` under `dispatch run` before it was stopped — so
  the Dispatcher itself works; only the final transition was missing.
- Sentinel clean throughout; no I1 / I8 / I13 violation, so OR-15 never fired.

## 4. Open caveat carried into the rerun

`LEASE_REFUSED` count is **0** across the whole log despite D-L6 demonstrably
refusing a claim (Phase 1 probe returned `scope_overlap`). Either the Dispatcher
does not attempt a claim it expects to fail, or refusals are not written to the
ledger. Until resolved, **metric 3 (conflict & incident rate) may have no
denominator**, which would make the Arm-0 versus Arm-A conflict comparison
unmeasurable from the ledger alone. To be checked in code, not assumed.

## 5. What changed

Operator approved rerunning Arm-0 with `pmk project run --seconds 1800`
(Conductor + Dispatcher + Overseer), without `project init` while
`project_state` is `NEW`. Note for the report: this makes the **Overseer an
active participant**, which is directly relevant to an experiment about Overseer
scope gating, and it is what Arm A will later be compared against.
