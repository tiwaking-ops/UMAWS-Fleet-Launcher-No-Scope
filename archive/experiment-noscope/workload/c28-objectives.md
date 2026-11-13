# Toy workload card 28 — scenario objectives

TOY-OK

This card records the scenario objectives for the toy workload experiment
(`docs/phase0-verification-2026-11-11.md`). It is a single-owner card; no other
card writes this file.

## Scenario objectives

The toy experiment workload exists to test the claim-time enforcement of
write-scope disjointness under the UMAWS fleet's lease/fence model. Its
scenario objectives are:

- **Objective 1: workload scaffold.** The `workload/` directory is a 20-card
  workload (cards T-0001…T-0020) plus deliberately overlapping shared files
  `shared-a.md`, `shared-b.md`, `shared-c.md`, so that write-scope overlap is
  real and testable at claim time.
- **Objective 2: one premise per card.** Every card carries exactly one premise,
  `P-BASE`: `workload/README.md` exists and carries the `WORKLOAD-BASE` marker.
  The premise check is `python workload/check.py workload/README.md
  WORKLOAD-BASE`, per card order/contract.
- **Objective 3: per-card oracle.** Each card's deliverable is accepted by the
  Windows-safe oracle `python workload/check.py <card-file> TOY-OK`, which
  reads files as UTF-8 text and exits 0 only when every named file exists and
  contains its marker. No POSIX builtins are used anywhere in the workflow.
- **Objective 4: overlap is detectable.** Cards 15-17 own `shared-a.md`+
  `shared-b.md`; cards 18-20 own `shared-b.md`+`shared-c.md`. Every pair
  overlaps on `shared-b.md`, so the D-L6 measurable (a claimed card that an
  overlapping peer already holds is refused with `scope_overlap`) is exercised
  by construction rather than by chance.

## Acceptance

- Deliverable: `workload/c28-objectives.md`
- Marker: `TOY-OK`
- Oracle (run by the harness after I exit): `python workload/check.py
  workload/c28-objectives.md TOY-OK`
