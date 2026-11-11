"""Compute the proposal's section 10.1 metrics for one arm, from the ledger.

Nothing here is inferred from configuration: width is counted from lease
pairs (CLAIMED -> REVOKED / TASK_DONE), which is what 10.1 requires and what
the baseline correction makes mandatory (max_total_agents does not bound
held leases).

Usage:  python tools/analyze_arm.py [--arm NAME] [--start ISO] [--end ISO]
"""

import argparse
import collections
import datetime as dt
import pathlib
import sys

ROOT = pathlib.Path(r"C:\temp\projects\umaws-noscope-toy")
sys.path.insert(0, str(ROOT / "src"))

from pmk.api import Kernel  # noqa: E402


def parse_ts(value: str) -> dt.datetime:
    return dt.datetime.fromisoformat(value.replace("Z", "+00:00"))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", default="ARM-0")
    ap.add_argument("--start", default="")
    ap.add_argument("--end", default="")
    args = ap.parse_args()

    kernel = Kernel(root=ROOT)
    events = kernel.events()

    start = parse_ts(args.start) if args.start else None
    end = parse_ts(args.end) if args.end else None

    # --- lease intervals ------------------------------------------------
    opens: dict[str, dt.datetime] = {}
    intervals: list[tuple[str, dt.datetime, dt.datetime]] = []
    closes = {"REVOKED", "TASK_DONE"}
    for e in events:
        ts = parse_ts(e.ts)
        if start and ts < start:
            continue
        if end and ts > end:
            continue
        task = e.subject or ""
        if e.type == "CLAIMED":
            opens.setdefault(task, ts)
        elif e.type in closes and task in opens:
            intervals.append((task, opens.pop(task), ts))
    # Leases still open at the end of the window are counted to the window end
    # or to "now", whichever is earlier -- they were genuinely held.
    horizon = min(end or dt.datetime.now(dt.timezone.utc),
                  dt.datetime.now(dt.timezone.utc))
    for task, opened in opens.items():
        intervals.append((task, opened, horizon))

    # --- peak concurrency ----------------------------------------------
    marks = collections.Counter()
    for _, o, c in intervals:
        marks[o] += 1
        marks[c] -= 1
    running = 0
    peak = 0
    series: list[tuple[dt.datetime, int]] = []
    for ts in sorted(marks):
        running += marks[ts]
        series.append((ts, running))
        peak = max(peak, running)

    # "Sustained" = held for at least 60 s at that level.
    sustained = 0
    for i, (ts, lvl) in enumerate(series):
        nxt = series[i + 1][0] if i + 1 < len(series) else horizon
        if lvl >= sustained and (nxt - ts).total_seconds() >= 60:
            sustained = lvl

    # --- the rest -------------------------------------------------------
    types = collections.Counter(e.type for e in events)
    done = [e for e in events if e.type == "TASK_DONE"]
    incidents = types.get("INCIDENT", 0)
    refusals = types.get("LEASE_REFUSED", 0)
    claimed = types.get("CLAIMED", 0)

    if intervals:
        wall_start = min(o for _, o, _ in intervals)
        wall_end = max(c for _, _, c in intervals)
        hours = max((wall_end - wall_start).total_seconds() / 3600.0, 1e-9)
    else:
        hours = 0.0

    print(f"arm                : {args.arm}")
    print(f"leases opened      : {len(intervals)}")
    print(f"CLAIMED events     : {claimed}")
    print(f"LEASE_REFUSED      : {refusals}")
    print(f"TASK_DONE          : {len(done)}")
    print(f"INCIDENT           : {incidents}")
    print(f"peak concurrent    : {peak}")
    print(f"sustained (>=60s)  : {sustained}")
    print(f"wall hours (leases): {hours:.4f}")
    print(f"throughput DONE/h  : {len(done) / hours if hours else 0.0:.3f}")
    print(f"conflict+incident %: "
          f"{(incidents / claimed * 100.0) if claimed else 0.0:.1f}")
    print()
    print("lease intervals (task, held seconds):")
    for task, o, c in sorted(intervals, key=lambda x: x[1]):
        print(f"  {task} {(c - o).total_seconds():8.1f}s  {o.isoformat()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
