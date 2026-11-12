"""REC-15: `--seconds` must actually bound the run.

These use a fake clock, so the bound is tested without waiting in real time.
The defect they guard (U-01) was a 30-minute budget becoming 97 minutes
because the deadline was tested only at the top of the loop.
"""

from __future__ import annotations

from pmk.cli import run_bounded


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
