"""T9.1 binding certification: licensing where a pass certifies only the capability seen.
Run as python -m tests.binding_study. Expectations B1-B3 are in rediscovery/frontier-ai.md."""
from concurrent.futures import ProcessPoolExecutor
import hashlib
import json
from pathlib import Path
import random
from time import perf_counter

from engine.history import History
from engine.records import provenance
from engine.rules import enforcement
from tests.frontier_study import D, REACH, RULE_GRID, cells, compact, make
from worlds import frontier as F


def check(cell):
    plain = make(cell)
    bound = History(make(cell), 1)
    return {**cell,
            "plain": compact(enforcement(plain, F, F.licensing, plain.initial_state(), D, REACH)),
            "bound": compact(enforcement(bound, F, F.licensing_bound, bound.initial_state(), D, REACH))}


if __name__ == "__main__":
    paths = [Path(__file__), Path("tests/frontier_study.py"), Path("tests/test_frontier.py")]
    t0 = perf_counter()
    with ProcessPoolExecutor() as pool:
        results = list(pool.map(check, cells(RULE_GRID)))
    print(json.dumps({"schema_version": 1, "kind": "binding", "provenance": provenance(),
                      "fixture_sha256": {p.as_posix(): hashlib.sha256(p.read_text(encoding="utf-8").encode()).hexdigest() for p in paths},
                      "rules": {"licensing": F.licensing.__doc__.strip(), "licensing (bound)": F.licensing_bound.__doc__.strip()},
                      "settings": {"grid": RULE_GRID, "depth": D, "reach": REACH, "records": 1},
                      "elapsed_seconds": perf_counter() - t0, "results": results},
                     indent=2, sort_keys=True, allow_nan=False, default=str))
