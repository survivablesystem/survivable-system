"""Depth/size sensitivity and per-round action probes for T1.3, not robustness."""
import hashlib
import json
from pathlib import Path
import random
from time import perf_counter

from engine.core import action_values, plan
from engine.records import provenance, run_record
from worlds import commons


def study():
    rows = []
    for size in (2, 4, 10):
        for depth in (1, 2, 3):
            params = {**commons.DEFAULTS, "n": size, "search_depth": depth}
            start = perf_counter()
            runs = [run_record(commons.make, params, 30, seed, include_trace=True) for seed in range(4)]
            rows.append({"n": size, "depth": depth, "elapsed_seconds": perf_counter() - start, "runs": runs})
    # Diagnose before revising the baseline's qualitative expectation.
    world = commons.make(commons.DEFAULTS, random.Random(0))
    state, probes = world.initial_state(), []
    for t in range(30):
        if world.terminal(state) is not None:
            break
        values = {a.id: action_values(world, state, a) for a in world.agents}
        joint = {a.id: plan(world, state, a) for a in world.agents}
        probes.append({"round": t + 1, "stock_before": state["S"], "values": values, "actions": joint})
        state = world.step(state, joint, world.rng)
    return {"sensitivity": rows, "baseline_action_probes": probes}


if __name__ == "__main__":
    print(json.dumps({"schema_version": 1, "kind": "planner-limits", "provenance": provenance(),
                      "fixture_sha256": hashlib.sha256(Path(__file__).read_text(encoding="utf-8").encode()).hexdigest(),
                      "settings": {"rounds": 30, "seeds": [0, 1, 2, 3]}, "results": study()},
                     indent=2, sort_keys=True, allow_nan=False))
