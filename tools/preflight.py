"""REC-05: preflight check for any UMAWS Fleet arm.

Run this BEFORE launching an arm. It exists because defects 2 and 5 were both
silent: a missing generated artifact and a missing hook made the global gate
red, so no card could reach DONE in any arm, and the failure looked like a
fleet problem rather than a scaffolding one. A missing tracked file is also
invisible inside a worktree, which is where cards are integrated.

Usage:  python tools/preflight.py [--root PATH] [--skip-gate]

Exit status 0 means every required check passed. Exit status 1 means the arm
must not be launched.
"""

import argparse
import pathlib
import subprocess
import sys

TOY = pathlib.Path(r"C:\temp\projects\umaws-noscope-toy")
LIVE = pathlib.Path(r"C:\temp\projects\testproject1")

REQUIRED_ARTIFACTS = (
    "coverage/rules_coverage.json",
    ".githooks/pre-commit",
)


def run(cmd, cwd):
    return subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(TOY))
    ap.add_argument("--skip-gate", action="store_true",
                    help="skip the slow `pytest -q` gate run")
    args = ap.parse_args()

    root = pathlib.Path(args.root).resolve()
    results = []

    def chk(name, ok, detail="", required=True):
        results.append((name, bool(ok), detail, required))

    # 1. Isolation. OR-01: never operate against the live repository.
    chk("isolation: working only in the toy repository",
        root == TOY.resolve() and root != LIVE.resolve(),
        f"root = {root}")

    # 2. Required scaffolding exists.
    for rel in REQUIRED_ARTIFACTS:
        chk(f"artifact present: {rel}", (root / rel).exists())

    # 3. Required scaffolding is TRACKED. Untracked files do not exist in a
    #    worktree, so an untracked hook silently disappears during integration.
    for rel in REQUIRED_ARTIFACTS:
        r = run(["git", "ls-files", "--error-unmatch", rel], root)
        chk(f"artifact tracked: {rel}", r.returncode == 0)

    # 4. REC-09: the gate must never be repaired by editing policy. Touching
    #    policy.toml changes policy_hash, engages I8' and OR-15 aborts the arm.
    rel_policy = ".pm/policy.toml"
    if (root / rel_policy).exists():
        r = run(["git", "status", "--porcelain", "--", rel_policy], root)
        clean = r.stdout.strip() == ""
        chk(f"{rel_policy} unmodified (REC-09)", clean,
            "" if clean else r.stdout.strip())
    else:
        chk(f"{rel_policy} unmodified (REC-09)", True, "absent - nothing to edit")

    # 5. Dirty tree: warn rather than block, since the Kernel appends its own
    #    sentinel events during normal operation.
    r = run(["git", "status", "--porcelain"], root)
    dirty = [ln for ln in r.stdout.splitlines() if ln.strip()]
    chk("working tree clean", not dirty,
        f"{len(dirty)} entries" if dirty else "", required=False)

    # 6. The global gate itself.
    if args.skip_gate:
        chk("global gate `pytest -q` green", True, "SKIPPED (--skip-gate)",
            required=False)
    else:
        r = run([sys.executable, "-m", "pytest", "-q"], root)
        chk("global gate `pytest -q` green", r.returncode == 0,
            (r.stdout.strip().splitlines() or [""])[-1][:80])

    width = max(len(n) for n, _, _, _ in results)
    failures = 0
    for name, ok, detail, required in results:
        if ok:
            mark = "PASS"
        elif required:
            mark = "FAIL"
            failures += 1
        else:
            mark = "warn"
        if detail:
            print(f"{mark}  {name:<{width}}  ({detail})")
        else:
            print(f"{mark}  {name}")

    print()
    if failures:
        print(f"PREFLIGHT FAILED: {failures} required check(s) failed. "
              f"Do not launch the arm.")
        return 1
    print("PREFLIGHT PASSED: all required checks are green.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
