"""T1.6 restraint: paired behavior runs and power maps. Run as python -m tests.restraint_study."""
import hashlib
import json
from pathlib import Path
import random
from time import perf_counter

from engine.records import provenance, run_record
from engine.sweep import sample_params
from tests.power_study import DESIGNS, STOCKS, summary, world_for
from worlds import commons

SAMPLES = 60
SAMPLE_SEED = 616
ROUNDS = 30
SEEDS = [0, 1, 2]
NEIGHBORHOOD = {"baseline": {}, "unpaid": {"confiscation_to": "stock"}, "no sanction": {"sanction": False},
                "depth 1": {"search_depth": 1}, "depth 3": {"search_depth": 3},
                "unpaid depth 3": {"confiscation_to": "stock", "search_depth": 3},
                "k 0": {"k": 0}, "n 2": {"n": 2}, "n 3": {"n": 3}, "hi 4": {"hi_mult": 4},
                "horizon 1": {"horizon": 1}, "no channels": {"channels": "none"},
                "r 0.3": {"r": 0.3}, "r 0.8": {"r": 0.8}, "discount 0.99": {"discount": 0.99},
                "prior hi": {"prior": "hi"}, "cost 0": {"sanction_cost": 0.0}}


def rests(record):
    return sum(1 for e in record.get("trace", []) for a in e["actions"].values() if a[0] == "rest")


def paired(params, seed):
    out = {}
    for rest in (False, True):
        start = perf_counter()
        record = run_record(commons.make, {**params, "restraint": rest}, ROUNDS, seed, include_trace=True)
        out[str(rest).lower()] = {"status": record["status"], "label": record["label"],
                                  "rounds_run": record["rounds_run"], "rest_actions": rests(record),
                                  "trace": record["trace"], "elapsed_seconds": perf_counter() - start}
    return out


def neighborhood():
    return [{"name": name, "params": {**commons.DEFAULTS, **over}, "seed": seed,
             **paired({**commons.DEFAULTS, **over}, seed)}
            for name, over in NEIGHBORHOOD.items() for seed in SEEDS]


def random_pairs():
    rng = random.Random(SAMPLE_SEED)
    # Keys added after this study are pinned so it reproduces its evidence.
    space = {k: v for k, v in commons.SPACE.items() if k not in ("restraint", "others")}
    out = []
    for _ in range(SAMPLES):
        params = {**sample_params(space, rng), "others": "react"}
        seed = rng.getrandbits(32)
        runs = paired(params, seed)
        for r in runs.values():
            r.pop("trace")
        out.append({"params": params, "seed": seed, **runs})
    return out


def power_maps():
    out = []
    for design in ("paid", "unpaid"):
        for rest in (False, True):
            world = world_for(**{**DESIGNS[design], "restraint": rest})
            for S in STOCKS:
                out.append({"design": design, "restraint": rest,
                            **summary(world, {**world.initial_state(), "S": S}, 3)})
    return out


if __name__ == "__main__":
    paths = [Path(__file__), Path("tests/power_study.py")]
    result = {"schema_version": 1, "kind": "restraint", "provenance": provenance(),
              "fixture_sha256": {p.as_posix(): hashlib.sha256(p.read_text(encoding="utf-8").encode()).hexdigest() for p in paths},
              "fixed": commons.FIXED, "fixed_reasons": commons.FIXED_REASONS,
              "settings": {"rounds": ROUNDS, "seeds": SEEDS, "samples": SAMPLES, "sample_seed": SAMPLE_SEED,
                           "neighborhood": NEIGHBORHOOD, "power_rounds": 3, "stocks": STOCKS,
                           "pairing": "Same parameters and seed with restraint off and on; different menus consume randomness differently, so shocks are not guaranteed identical."},
              "results": {"neighborhood": neighborhood(), "random_pairs": random_pairs(), "power": power_maps()}}
    print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))
