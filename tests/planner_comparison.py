"""Matched finite commons probes; run as python -m tests.planner_comparison."""
import hashlib
import json
from pathlib import Path
import random
from time import perf_counter

from engine.core import action_values
from engine.records import provenance, run_record
from worlds import commons


def comparison():
    rows = []
    for name, overrides in [
        ("baseline", {}), ("horizon-2", {"horizon": 2}),
        ("no-channels", {"channels": "none"}),
        ("no-sanctions", {"sanction": False}),
        ("unpaid", {"confiscation_to": "stock"}),
        ("level-0", {"k": 0}), ("two-users", {"n": 2}),
    ]:
        params = {**commons.DEFAULTS, **overrides}
        world = commons.make(params, random.Random(0))
        start = perf_counter()
        values = action_values(world, world.initial_state(), world.agents[0])
        runs = [run_record(commons.make, params, 12, seed, include_trace=True)
                for seed in range(3)]
        rows.append({"case": name, "initial_values": values, "runs": runs,
                     "elapsed_seconds": perf_counter() - start})
    return rows


if __name__ == "__main__":
    result = {"schema_version": 1, "kind": "planner-comparison", "provenance": provenance(),
              "fixture_sha256": hashlib.sha256(Path(__file__).read_text(encoding="utf-8").encode()).hexdigest(),
              "settings": {"rounds": 12, "seeds": [0, 1, 2]}, "results": comparison()}
    print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))
