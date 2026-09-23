"""T1.8 exact search beyond depth 3, commons baseline. Run as python -m tests.depth_study."""
import hashlib
import json
from pathlib import Path
from time import perf_counter

from engine.records import provenance, run_record
from worlds import commons

# A study-level cap, recorded here; the world's declared default (FIXED) stays unchanged.
STUDY_BUDGET = 2_000_000
ROUNDS = 30
RUNS = [(depth, restraint, seed) for depth in (4, 5) for restraint in (True, False)
        for seed in ((0, 1) if depth == 4 else (0,))]


def study():
    default = commons.FIXED["node_budget"]
    commons.FIXED["node_budget"] = STUDY_BUDGET
    try:
        out = []
        for depth, restraint, seed in RUNS:
            params = {**commons.DEFAULTS, "search_depth": depth, "restraint": restraint}
            start = perf_counter()
            record = run_record(commons.make, params, ROUNDS, seed, include_trace=True)
            out.append({"record": record, "elapsed_seconds": perf_counter() - start})
        return out
    finally:
        commons.FIXED["node_budget"] = default


if __name__ == "__main__":
    paths = [Path(__file__)]
    print(json.dumps({"schema_version": 1, "kind": "depth", "provenance": provenance(),
                      "fixture_sha256": {p.as_posix(): hashlib.sha256(p.read_text(encoding="utf-8").encode()).hexdigest() for p in paths},
                      "fixed": commons.FIXED, "fixed_reasons": commons.FIXED_REASONS,
                      "settings": {"study_budget": STUDY_BUDGET, "rounds": ROUNDS, "runs": RUNS,
                                   "budget_reason": "Measured: a depth-5 initial decision needs 481,531 entries; the default 20,000 cap stops depth 4."},
                      "results": study()}, indent=2, sort_keys=True, allow_nan=False))
