"""Windows-safe oracle checker for the no-scope experiment workload.

Usage:  python workload/check.py <file> <marker> [<file> <marker> ...]

Exits 0 when every named file exists and contains its marker, 1 otherwise.
Used as the per-card acceptance oracle so no card depends on POSIX builtins
(the failure mode that voided T-0003).
"""

import pathlib
import sys


def main(argv: list[str]) -> int:
    args = argv[1:]
    if not args or len(args) % 2 != 0:
        print("usage: check.py <file> <marker> [<file> <marker> ...]")
        return 2
    pairs = list(zip(args[0::2], args[1::2]))
    ok = True
    for path_str, marker in pairs:
        path = pathlib.Path(path_str)
        present = path.exists()
        hit = present and marker in path.read_text(encoding="utf-8")
        print(f"check {path_str} marker={marker} -> {'PASS' if hit else 'FAIL'}")
        ok = ok and hit
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
