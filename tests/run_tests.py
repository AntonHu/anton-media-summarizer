from __future__ import annotations

import importlib
import inspect
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def main() -> int:
    failures = []
    for path in sorted(Path(__file__).parent.glob("test_*.py")):
        module = importlib.import_module(f"tests.{path.stem}")
        for name, func in inspect.getmembers(module, inspect.isfunction):
            if not name.startswith("test_"):
                continue
            try:
                func()
                print(f"PASS {path.name}::{name}")
            except Exception as exc:
                print(f"FAIL {path.name}::{name}: {exc}")
                failures.append((path.name, name, exc))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())

