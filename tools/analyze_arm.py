"""Compute the proposal's section 10.1 metrics for one arm, from the ledger.

Nothing here is inferred from configuration.  WIDTH IS COUNTED FROM LIVE
AGENT RUNS (AGENT_STARTED -> AGENT_EXITED), because a kernel lease outlives
its agent and lease concurrency overstates how many agents are actually
working.  The lease figure is still reported alongside it, labelled as
inflated, since the two disagree materially (Arm-0b: 16 leases vs 10 live).

Throughput divides by the MEASURED window (REC-16), never by the requested
budget; pass --requested-seconds to have the overrun flagged (REC-12).

Usage:  python tools/analyze_arm.py [--arm NAME] [--start ISO] [--end ISO]
                                    [--requested-seconds N]
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
    # REC-12: the value actually passed to e.g. `pmk project run --seconds N`.
    # Supplying it lets the analyzer say whether the run honoured its budget,
    # which decides whether any per-hour figure is trustworthy at all.
    ap.add_argument("--requested-seconds", type=float, default=None)
    args = ap.parse_args()

    kernel = Kernel(root=ROOT)
    all_events = kernel.events()

    start = parse_ts(args.start) if args.start else None
    end = parse_ts(args.end) if args.end else None

    # Apply the window ONCE, and read every counter below from `events`.
    # Counting from the unfiltered log makes --start/--end silently affect
    # only the lease intervals while the headline numbers still describe
    # activity outside the window (probe leases, pre-gate-fix runs).
    events = []
    for e in all_events:
        ts = parse_ts(e.ts)
        if start and ts < start:
            continue
        if end and ts > end:
            continue
        events.append(e)

    if start or end:
        print(f"window             : {len(events)} of {len(all_events)} events")

    # --- lease intervals ------------------------------------------------
    opens: dict[str, dt.datetime] = {}
    intervals: list[tuple[str, dt.datetime, dt.datetime]] = []
    # A lease ends when it is revoked or when the card integrates (DONE).
    # "TASK_DONE" is not emitted by this pipeline; INTEGRATED is terminal.
    closes = {"REVOKED", "INTEGRATED", "TASK_DONE"}
    for e in events:
        ts = parse_ts(e.ts)
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

    # --- width of LIVE agent runs, not leases ---------------------------
    # A lease outlives its agent: the kernel lease survives after the run
    # object leaves dispatcher.self.runs.  Lease concurrency therefore
    # overstates how many agents are actually working, and width must be
    # reported both ways or it is not interpretable.
    live_open: dict[str, dt.datetime] = {}
    live_pts: list[tuple[dt.datetime, int]] = []
    for e in events:
        ts = parse_ts(e.ts)
        if e.type == "AGENT_STARTED":
            if e.subject not in live_open:
                live_open[e.subject] = ts
                live_pts.append((ts, 1))
        elif e.type == "AGENT_EXITED" and e.subject in live_open:
            live_open.pop(e.subject)
            live_pts.append((ts, -1))
    live_peak = live_sustained = 0
    if live_pts:
        live_pts.sort()
        cur = 0
        lseries: list[tuple[dt.datetime, int]] = []
        for t, d in live_pts:
            cur += d
            lseries.append((t, cur))
            live_peak = max(live_peak, cur)
        for i, (t, l) in enumerate(lseries):
            nxt = lseries[i + 1][0] if i + 1 < len(lseries) else horizon
            if l >= live_sustained and (nxt - t).total_seconds() >= 60:
                live_sustained = l

    # --- the rest -------------------------------------------------------
    types = collections.Counter(e.type for e in events)
    done_events = [e for e in events
                   if e.type in ("INTEGRATED", "TASK_DONE")]
    # Count distinct cards, not events: a card that emits both must not
    # be counted twice.
    done_tasks = sorted({e.subject for e in done_events if e.subject})
    incidents = types.get("INCIDENT", 0)
    # REC-11: a merge conflict is recorded as QUARANTINED, not as INCIDENT.
    # Counting INCIDENT alone reported 0.0 for a window that held three real
    # conflicts, so metric 3 silently under-reported.  Both are counted, and
    # both are printed so the figure can never again hide its composition.
    quarantined = types.get("QUARANTINED", 0)
    conflicts = incidents + quarantined
    refusals = types.get("LEASE_REFUSED", 0)
    claimed = types.get("CLAIMED", 0)

    # D-L6 denials are recorded as FLEET_BLOCKED with
    # payload {"blocker": "scope_overlap"} -- NOT as LEASE_REFUSED.  Counting
    # only LEASE_REFUSED reports zero denials for a run full of them.
    blocked = [e for e in events if e.type == "FLEET_BLOCKED"]
    blockers = collections.Counter(
        (e.payload or {}).get("blocker", "?") for e in blocked)
    attempts = claimed + len(blocked)

    # Throughput is per unit of ARM WALL TIME.  When the operator supplies a
    # window, that window is the wall clock; otherwise fall back to the span
    # actually covered by leases.  Using the lease span silently inflates the
    # denominator with idle time and understates throughput.
    if start and end:
        wall_start, wall_end = start, end
    elif intervals:
        wall_start = min(o for _, o, _ in intervals)
        wall_end = max(c for _, _, c in intervals)
    else:
        wall_start = wall_end = None
    hours = ((wall_end - wall_start).total_seconds() / 3600.0
             if wall_start and wall_end else 0.0)

    print(f"arm                : {args.arm}")
    print(f"leases opened      : {len(intervals)}")
    print(f"CLAIMED events     : {claimed}")
    print(f"LEASE_REFUSED      : {refusals}")
    print(f"FLEET_BLOCKED      : {len(blocked)} {dict(blockers)}")
    print(f"claim attempts     : {attempts}")
    print(f"tasks DONE         : {len(done_tasks)} {done_tasks}")
    print(f"INCIDENT           : {incidents}")
    print(f"QUARANTINED        : {quarantined}")
    print(f"peak concurrent    : {peak}")
    print(f"LIVE peak concurrent: {live_peak}  (lease-based: {peak})")
    print(f"LIVE sustained      : {live_sustained}  (lease-based: {sustained})")
    print(f"wall hours (measured): {hours:.4f}"
          f"{'   <- REPORTING DENOMINATOR' if hours else ''}")
    if args.requested_seconds is not None and wall_start and wall_end:
        measured = (wall_end - wall_start).total_seconds()
        ratio = measured / args.requested_seconds
        verdict = "OK" if ratio <= 1.10 else "OVERRAN"
        print(f"requested seconds   : {args.requested_seconds:.0f}"
              f" ({args.requested_seconds / 3600.0:.4f} h)")
        print(f"measured seconds    : {measured:.0f} ({hours:.4f} h)"
              f"   -> {verdict}, x{ratio:.2f} of budget")
        if verdict == "OVERRAN":
            # cli.py:832-836 tests the deadline only once per tick, so a run
            # overshoots by up to a whole tick.  See REC-15 / U-01.
            print("  WARNING: --seconds did not bound this run.  Every per-hour")
            print("  figure below uses the MEASURED window (REC-16).  Do not")
            print("  compare it against a run that overran by a different factor.")
    print(f"throughput DONE/h  : "
          f"{(len(done_tasks) / hours) if hours else 0.0:.3f}")
    print(f"denial rate %      : "
          f"{(len(blocked) / attempts * 100.0) if attempts else 0.0:.1f}")
    print(f"conflict+incident %: "
          f"{(conflicts / claimed * 100.0) if claimed else 0.0:.1f}"
          f"   (= INCIDENT {incidents} + QUARANTINED {quarantined}"
          f" over {claimed} claims)")
    print()
    print("lease intervals (task, held seconds):")
    for task, o, c in sorted(intervals, key=lambda x: x[1]):
        print(f"  {task} {(c - o).total_seconds():8.1f}s  {o.isoformat()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
