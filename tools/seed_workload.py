"""Seed the 20-card workload into the toy repository (Phase 1).

Runs through pmk.api — no direct writes to .pm/ (I2).

Shape (proposal 7.1): 20 cards, each with one deliverable, one Windows-safe
oracle run through workload/check.py, and one premise.  Six cards (15-20)
deliberately overlap on the three shared files, which is what makes the
write-scope gating of D-L6 testable at claim time.
"""

import pathlib
import sys

ROOT = pathlib.Path(r"C:\temp\projects\umaws-noscope-toy")
sys.path.insert(0, str(ROOT / "src"))

from pmk.api import Kernel  # noqa: E402
from pmk.events import Actor  # noqa: E402

SHARED_A = "workload/shared-a.md"
SHARED_B = "workload/shared-b.md"
SHARED_C = "workload/shared-c.md"

PREMISE = {
    "id": "P-BASE",
    "claim": "workload/README.md exists and carries the WORKLOAD-BASE marker",
    "check": "python workload/check.py workload/README.md WORKLOAD-BASE",
}

# 14 single-owner cards.
UNIQUE = [
    ("toy workload card 01 — inventory model", "c01-inventory.md"),
    ("toy workload card 02 — supply ledger", "c02-supply.md"),
    ("toy workload card 03 — unit roster", "c03-roster.md"),
    ("toy workload card 04 — map index", "c04-mapindex.md"),
    ("toy workload card 05 — terrain table", "c05-terrain.md"),
    ("toy workload card 06 — weather rules", "c06-weather.md"),
    ("toy workload card 07 — combat summary", "c07-combat.md"),
    ("toy workload card 08 — logistics summary", "c08-logistics.md"),
    ("toy workload card 09 — air summary", "c09-air.md"),
    ("toy workload card 10 — naval summary", "c10-naval.md"),
    ("toy workload card 11 — scenario loader notes", "c11-loader.md"),
    ("toy workload card 12 — ui skeleton notes", "c12-ui.md"),
    ("toy workload card 13 — save format notes", "c13-save.md"),
    ("toy workload card 14 — replay format notes", "c14-replay.md"),
]

# 6 overlapping cards: every pair shares SHARED_B.
OVERLAP = [
    ("toy workload card 15 — shared section 15", [SHARED_A, SHARED_B], "SEC-15"),
    ("toy workload card 16 — shared section 16", [SHARED_A, SHARED_B], "SEC-16"),
    ("toy workload card 17 — shared section 17", [SHARED_A, SHARED_B], "SEC-17"),
    ("toy workload card 18 — shared section 18", [SHARED_B, SHARED_C], "SEC-18"),
    ("toy workload card 19 — shared section 19", [SHARED_B, SHARED_C], "SEC-19"),
    ("toy workload card 20 — shared section 20", [SHARED_B, SHARED_C], "SEC-20"),
]


def oracle_for(pairs):
    args = " ".join(f"{p} {m}" for p, m in pairs)
    return f"python workload/check.py {args}"


def main() -> int:
    kernel = Kernel(root=ROOT)
    actor = Actor(kind="human", agent="toy-seed", role="executor")

    created = []
    for title, deliverable in UNIQUE:
        path = f"workload/{deliverable}"
        card = kernel.task_create(
            title,
            type="work",
            goal_ref="toy experiment workload",
            scope={"write": [path], "read": ["workload/README.md"]},
            oracles=[oracle_for([(path, "TOY-OK")])],
            evidence_required=["RESULT.md"],
            premises=[dict(PREMISE)],
            budget={"tokens": 0, "wall_min": 30},
            attempts_max=3,
            priority=100,
            admitted=True,
            actor=actor,
        )
        created.append((card.id, card.state, sorted(card.scope.get("write", []))))

    for title, paths, marker in OVERLAP:
        card = kernel.task_create(
            title,
            type="work",
            goal_ref="toy experiment workload",
            scope={"write": list(paths), "read": ["workload/README.md"]},
            oracles=[oracle_for([(p, marker) for p in paths])],
            evidence_required=["RESULT.md"],
            premises=[dict(PREMISE)],
            budget={"tokens": 0, "wall_min": 30},
            attempts_max=3,
            priority=100,
            admitted=True,
            actor=actor,
        )
        created.append((card.id, card.state, sorted(card.scope.get("write", []))))

    for cid, state, write in created:
        print(f"{cid} {state} write={write}")
    print(f"total={len(created)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
