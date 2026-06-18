#!/usr/bin/env python3
"""
One-shot runner for the entire data_extract test suite.

Run it from anywhere:
    python tests/backend_tests/data_extract_unit_tests/run_tests.py
    python tests/backend_tests/data_extract_unit_tests/run_tests.py -k facts   # forward pytest args (-k, -q, -x, ...)

It puts the repo root on sys.path so `backend.data_extract` imports resolve no
matter where you launch from, then runs pytest across every test_*.py in this
directory (conftest.py is auto-discovered).

No data files needed: the suite is fully self-contained — network calls are
mocked and all fixture data is synthesized in conftest.py.
"""
import sys
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
REPO_ROOT = THIS_DIR.parents[2]   # data_extract_unit_tests -> backend_tests -> tests -> repo root

# Make `backend.data_extract` importable regardless of the launch directory.
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def main() -> int:
    try:
        import pytest
    except ImportError:
        print("pytest is not installed. Run:  pip install -r requirements.txt")
        return 1
    # Run this directory; forward any extra CLI args the user passes.
    args = [str(THIS_DIR), "-v", *sys.argv[1:]]
    return pytest.main(args)


if __name__ == "__main__":
    raise SystemExit(main())
