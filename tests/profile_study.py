"""T1.7 behavior beside power, commons designs. Run as python -m tests.profile_study."""
import hashlib
import json
from pathlib import Path

from engine.power import profile
from engine.records import provenance, run_record
from worlds import commons
import random

POWER_ROUNDS = 3
ROUNDS = 30
RUNS = {"paid": ({}, 0), "unpaid": ({"confiscation_to": "stock"}, 0), "none": ({"sanction": False}, 0),
        "paid, no restraint": ({"restraint": False}, 0),
        # The one random sample (restraint_study, seed 616) that survived only with restraint.
        "rest-and-raid survivor": ({"channels": "none", "confiscation_to": "stock",
                                    "discount": 0.9780691687045955, "hi_mult": 2, "horizon": 4, "k": 0,
                                    "n": 2, "prior": "lo", "r": 0.6947004801675916, "sanction": False,
                                    "sanction_cost": 0.46153597603574226, "search_depth": 3}, 173321596)}


def study():
    out = []
    for name, (overrides, seed) in RUNS.items():
        params = {**commons.DEFAULTS, **overrides}
        record = run_record(commons.make, params, ROUNDS, seed, include_trace=True)
        world = commons.make(dict(params), random.Random(seed))
        prof = profile(world, record["trace"], POWER_ROUNDS, "collapsed")
        out.append({"name": name, "record": record, "profile": prof,
                    "fragile_rounds": [e["round"] for e in prof["rounds"] if e["fragile"]]})
    return out


if __name__ == "__main__":
    paths = [Path(__file__)]
    print(json.dumps({"schema_version": 1, "kind": "power-profiles", "provenance": provenance(),
                      "fixture_sha256": {p.as_posix(): hashlib.sha256(p.read_text(encoding="utf-8").encode()).hexdigest() for p in paths},
                      "fixed": commons.FIXED, "fixed_reasons": commons.FIXED_REASONS,
                      "settings": {"power_rounds": POWER_ROUNDS, "rounds": ROUNDS, "target": "collapsed",
                                   "runs": {k: {"overrides": v[0], "seed": v[1]} for k, v in RUNS.items()}},
                      "results": study()}, indent=2, sort_keys=True, allow_nan=False))
