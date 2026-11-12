"""REC-15: `--seconds` must actually bound the run.

These use a fake clock, so the bound is tested without waiting in real time.
The defect they guard (U-01) was a 30-minute budget becoming 97 minutes
because the deadline was tested only at the top of the loop.
"""

from __future__ import annotations

from pmk.cli import run_bounded, run_report_lines


class FakeClock:
    """A clock whose ticks each consume *tick_cost* seconds."""

    def __init__(self, tick_cost: float):
        self.t = 0.0
        self.tick_cost = tick_cost
        self.slept = 0.0

    def now(self) -> float:
        return self.t

    def sleep(self, seconds: float) -> None:
        self.slept += seconds
        self.t += seconds

    def tick(self) -> None:
        self.t += self.tick_cost


def test_budget_is_not_exceeded_by_more_than_one_tick():
    """The old behaviour overshot by a full tick every single time."""
    clock = FakeClock(tick_cost=100.0)
    report = run_bounded(3600.0, clock.tick, sleep=clock.sleep,
                         now=clock.now)

    overshoot = report["measured_s"] - 3600.0
    assert overshoot <= report["last_tick_s"] + 1.0, (
        f"overshot by {overshoot:.0f}s, which is more than one tick "
        f"({report['last_tick_s']:.0f}s)")


def test_a_tick_that_would_outlive_the_budget_is_not_started():
    """Budget 150s, each tick costs 100s.

    After one tick there are 50s left - not enough for another 100s tick, so
    the loop must stop rather than start one. Under the old deadline test it
    would have started that tick anyway and run to 200s.
    """
    clock = FakeClock(tick_cost=100.0)
    report = run_bounded(150.0, clock.tick, sleep=clock.sleep, now=clock.now)

    assert report["ticks"] == 1
    assert report["skipped_final_tick"] is True
    # 100s of tick plus the 1s nap; the point is that it stays INSIDE the
    # 150s budget instead of running a second tick to 200s.
    assert report["measured_s"] <= 150.0


def test_a_single_huge_tick_still_runs_exactly_once():
    """One tick may overshoot - it cannot be interrupted - but only one."""
    clock = FakeClock(tick_cost=5000.0)
    report = run_bounded(120.0, clock.tick, sleep=clock.sleep, now=clock.now)

    assert report["ticks"] == 1
    assert report["measured_s"] == 5000.0


def test_short_ticks_fill_the_budget():
    """The fix must not shorten runs that were already well-behaved."""
    clock = FakeClock(tick_cost=10.0)
    report = run_bounded(100.0, clock.tick, sleep=clock.sleep, now=clock.now)

    assert report["ticks"] >= 5
    assert report["measured_s"] <= 110.0


# --- run_report_lines --------------------------------------------------
# These exist because the reporting once lived inline in cmd_project_run,
# where a NameError survived a green test suite: run_bounded returns
# skipped_final_tick inside its dict, but the caller still referred to it as a
# local. No test called the caller, so nothing caught it. A baseline run then
# crashed after 3400s of work. Every branch below is therefore asserted.


def _report(*, ticks=1, last_tick_s=0.0, measured_s=0.0, skipped=False):
    return {"ticks": ticks, "last_tick_s": last_tick_s,
            "measured_s": measured_s, "skipped_final_tick": skipped}


def test_report_warns_when_one_tick_exceeds_the_whole_budget():
    """Exactly what happened to the baseline-2 run: 1 tick of 3399.9s."""
    lines = run_report_lines(
        _report(ticks=1, last_tick_s=3399.9, measured_s=3400.0), 1800.0)

    assert any("longer than the whole" in line for line in lines)


def test_report_warns_when_overrun_exceeds_one_tick():
    lines = run_report_lines(
        _report(ticks=3, last_tick_s=10.0, measured_s=95.0), 60.0)

    assert any("more than one tick" in line for line in lines)


def test_report_reports_the_skipped_final_tick():
    lines = run_report_lines(
        _report(ticks=1, last_tick_s=100.0, measured_s=101.0, skipped=True),
        150.0)

    assert any("would have outlived the budget" in line for line in lines)


def test_report_is_quiet_for_a_well_behaved_run():
    lines = run_report_lines(
        _report(ticks=5, last_tick_s=10.0, measured_s=55.0), 60.0)

    assert len(lines) == 1
    assert "WARNING" not in lines[0]
