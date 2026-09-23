"""E2 step 3: commons behavior across population size. Run as python -m tests.size_study."""
import hashlib
import json
from itertools import product
from multiprocessing import Pool
from pathlib import Path
from time import perf_counter

from engine.records import provenance, run_record
from worlds import commons

SIZES = (2, 3, 4, 6, 8, 12, 16, 24)
SANCTIONS = (("none", {"sanction": False}), ("paid", {"confiscation_to": "sanctioners"}),
             ("unpaid", {"confiscation_to": "stock"}))
PRIORS = ("lo", "ready")
REGROWTH = (0.3, 0.5)
HIGH = (2, 3)
SEEDS = (0, 1)
ROUNDS = 30


def compact(record):
    """Per round: count of each (take, sanction) choice and the stock."""
    rounds = []
    for entry in record.pop("trace"):
        counts = {}
        for take, sanction in entry["actions"].values():
            k = f"{take}{'+s' if sanction else ''}"
            counts[k] = counts.get(k, 0) + 1
        rounds.append({"round": entry["round"], "choices": counts, "S": entry["state"]["S"]})
    record.pop("final_state")
    record.pop("planning")
    record["rounds"] = rounds
    return record


def case(setting):
    name, extra, prior, r, hi, n, seed = setting
    params = {**commons.DEFAULTS, **extra, "prior": prior, "r": r, "hi_mult": hi, "n": n}
    start = perf_counter()
    record = compact(run_record(commons.make, params, ROUNDS, seed, include_trace=True))
    return {"sanctions": name, "elapsed_seconds": perf_counter() - start, **record}


COSTS = (0.05, 0.1, 0.2)
COST_SIZES = (4, 6, 8, 12, 16, 24)
COST_BASE = {"confiscation_to": "stock", "prior": "lo", "r": 0.3, "hi_mult": 2}


def cost_case(setting):
    """Discriminating check: the unpaid brink brake should vanish where (n-1) x cost
    crosses a fixed multiple of one's own low take."""
    cost, n, others = setting
    params = {**commons.DEFAULTS, **COST_BASE, "sanction_cost": cost, "n": n, "others": others}
    record = compact(run_record(commons.make, params, ROUNDS, 0, include_trace=True))
    return {"brake": any("lo+s" in r["choices"] for r in record["rounds"]), **record}


def cost_settings():
    return ([(c, n, "react") for c in COSTS for n in COST_SIZES]
            + [(0.1, n, "plan") for n in (6, 8, 12)])


def settings():
    grid = [(name, extra, prior, r, hi, n, seed) for (name, extra), prior, r, hi, n, seed
            in product(SANCTIONS, PRIORS, REGROWTH, HIGH, SIZES, SEEDS)]
    return sorted(grid, key=lambda s: -s[5])  # largest first


if __name__ == "__main__":
    paths = [Path(__file__), Path("tests/test_continuation.py")]
    start = perf_counter()
    with Pool(4) as pool:
        results = pool.map(case, settings(), chunksize=1)
        cost_check = pool.map(cost_case, cost_settings(), chunksize=1)
    results.sort(key=lambda r: (r["sanctions"], r["params"]["prior"], r["params"]["r"], r["params"]["hi_mult"],
                                r["params"]["n"], r["seed"]))
    print(json.dumps({"schema_version": 1, "kind": "size", "provenance": provenance(),
                      "fixture_sha256": {p.as_posix(): hashlib.sha256(p.read_text(encoding="utf-8").encode()).hexdigest() for p in paths},
                      "fixed": commons.FIXED, "fixed_reasons": commons.FIXED_REASONS, "defaults": commons.DEFAULTS,
                      "settings": {"sizes": SIZES, "sanctions": dict(SANCTIONS), "priors": PRIORS, "regrowth": REGROWTH,
                                   "high": HIGH, "seeds": SEEDS, "rounds": ROUNDS,
                                   "cost_check": {"base": COST_BASE, "costs": COSTS, "sizes": COST_SIZES, "seed": 0}},
                      "cost_check": cost_check,
                      "duration_seconds": perf_counter() - start, "results": results},
                     indent=2, sort_keys=True, allow_nan=False))
