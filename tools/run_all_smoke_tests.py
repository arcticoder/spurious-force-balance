"""
tools/run_all_smoke_tests.py
------------------------------
Finds every smoke_test.py under hardware/ and runs each with the same Python
interpreter, from the repo root. Exits non-zero if any smoke test fails. The CAD
checks need the venv that carries CadQuery (see hardware/README.md):
    ~/.venvs/lab-hw/bin/python tools/run_all_smoke_tests.py
"""

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    smoke_tests = sorted(REPO_ROOT.glob("hardware/*/smoke_test.py"))
    if not smoke_tests:
        print("No smoke_test.py files found.")
        return 1

    failures = []
    for path in smoke_tests:
        rel = path.relative_to(REPO_ROOT)
        print(f"\n=== {rel} ===")
        result = subprocess.run([sys.executable, str(path)], cwd=REPO_ROOT)
        if result.returncode != 0:
            failures.append(str(rel))

    print(f"\n{len(smoke_tests)} smoke test(s) run, {len(failures)} failed.")
    if failures:
        print("Failed:")
        for f in failures:
            print(f"  {f}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
