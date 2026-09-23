"""T1.5 goal-free coalition power in the commons. Run as python -m tests.power_study."""
import hashlib
import json
import math
from pathlib import Path
import random
from time import perf_counter

from engine.core import run
from engine.power import PowerLimitExceeded, force, power_table, threshold, witness
from engine.records import provenance
from worlds import commons

DESIGNS = {"paid": {"sanction": True, "confiscation_to": "sanctioners"},
           "unpaid": {"sanction": True, "confiscation_to": "stock"},
           "none": {"sanction": False, "confiscation_to": "sanctioners"}}
TARGET = "collapsed"
LEVELS = [1.0, 0.5]
MAP_ROUNDS = 3
STOCKS = [6.0, 8.0, 10.0, 15.0, 20.0, 25.0, 30.0, 40.0, 50.0, 75.0, 100.0]
HI_MULTS = [2, 4]
REGROWTH = [0.3, 0.5, 0.8]
SEALED_ROUNDS = 12


def unavoidable(world, state):
    """Grand coalition cannot avoid the target within SEALED_ROUNDS; None if unresolved."""
    try:
        return force(world, state, [], SEALED_ROUNDS, TARGET)
    except PowerLimitExceeded:
        return None


def world_for(**overrides):
    return commons.make({**commons.DEFAULTS, **overrides}, random.Random(0))


def no_return_stock():
    # All users at the minimum take harvest lo_frac * MSY. Below the lower root of
    # r S (1 - S/K) = lo_frac * r K / 4, stock declines whatever anyone does, unless
    # something returns harvest to the stock. Independent of r and n.
    return commons.FIXED["K"] * (1 - math.sqrt(1 - commons.FIXED["lo_frac"])) / 2


def by_size(rows):
    """Per-size values; `symmetric` checks, rather than assumes, exchangeable users."""
    sizes = {}
    for r in rows:
        sizes.setdefault(len(r["coalition"]), []).append((r["force"], r["prevent"]))
    return {"symmetric": all(len({json.dumps(v, sort_keys=True) for v in group}) == 1
                             for group in sizes.values()),
            "force_alpha": [min(f["alpha"] for f, _ in sizes[k]) for k in sorted(sizes)],
            "force_beta": [max(f["beta"] for f, _ in sizes[k]) for k in sorted(sizes)],
            "prevent_alpha": [min(p["alpha"] for _, p in sizes[k]) for k in sorted(sizes)],
            "prevent_beta": [max(p["beta"] for _, p in sizes[k]) for k in sorted(sizes)]}


def summary(world, state, rounds):
    start = perf_counter()
    rows = power_table(world, state, rounds, TARGET)
    return {"S": state["S"], "rounds": rounds, **by_size(rows),
            "thresholds": [threshold(rows, kind, p) for kind in ("force", "prevent") for p in LEVELS],
            "work": sum(r["work"]["alpha"] + r["work"]["beta"] for r in rows),
            "elapsed_seconds": perf_counter() - start}


def power_map():
    out = []
    for design, overrides in DESIGNS.items():
        for hi_mult in HI_MULTS:
            for r in REGROWTH:
                world = world_for(**overrides, hi_mult=hi_mult, r=r)
                for S in STOCKS:
                    out.append({"design": design, "hi_mult": hi_mult, "r": r,
                                **summary(world, {**world.initial_state(), "S": S}, MAP_ROUNDS)})
    return out


def horizon_and_size():
    out = []
    for design in ("paid", "unpaid"):
        for rounds in (2, 3, 4):
            world = world_for(**DESIGNS[design])
            for S in (15.0, 20.0, 30.0, 40.0):
                out.append({"design": design, "n": 4, **summary(world, {**world.initial_state(), "S": S}, rounds)})
        for n in (2, 3):
            world = world_for(**DESIGNS[design], n=n)
            for S in (15.0, 20.0, 30.0, 40.0):
                out.append({"design": design, "n": n, **summary(world, {**world.initial_state(), "S": S}, MAP_ROUNDS)})
    return out


def profiles():
    """What agents did, beside what coalitions could have forced, at each pre-round state."""
    out = []
    for design, overrides in DESIGNS.items():
        world = world_for(**overrides)
        label, final, trace = run(world, 30, world.rng)
        states = [world.initial_state()] + [s for _, s in trace]
        rounds = []
        for t, (joint, after) in enumerate(trace):
            before = states[t]
            entry = {"round": t + 1, "actions": joint, "S_after": after["S"],
                     **summary(world, before, MAP_ROUNDS)}
            if design != "unpaid" and before["S"] < no_return_stock() + 10:
                start = perf_counter()
                entry["unavoidable_within_12"] = unavoidable(world, before)
                entry["unavoidable_seconds"] = perf_counter() - start
            rounds.append(entry)
        out.append({"design": design, "params": {**commons.DEFAULTS, **overrides}, "seed": 0,
                    "label": label, "rounds_run": len(trace), "rounds": rounds})
    return out


def best_prevention():
    """The grand coalition's best first-round joint: goal-free, exposes action semantics."""
    out = []
    for design in ("paid", "unpaid"):
        world = world_for(**DESIGNS[design])
        for S in (10.0, 15.0, 20.0):
            result = witness(world, {**world.initial_state(), "S": S}, [], MAP_ROUNDS, TARGET)
            out.append({"design": design, "S": S, "prevent_all": 1 - result["value"],
                        "joint": result["reply"]})
    return out


def sealed_checks():
    world = world_for(**DESIGNS["paid"])
    return [{"S": S, "rounds": SEALED_ROUNDS,
             "unavoidable": unavoidable(world, {**world.initial_state(), "S": S})}
            for S in (20.0, 23.6, 26.0, 27.5, 28.0)]


if __name__ == "__main__":
    paths = [Path(__file__), Path("tests/test_power.py")]
    result = {"schema_version": 1, "kind": "coalition-power", "provenance": provenance(),
              "fixture_sha256": {p.as_posix(): hashlib.sha256(p.read_text(encoding="utf-8").encode()).hexdigest() for p in paths},
              "fixed": commons.FIXED, "fixed_reasons": commons.FIXED_REASONS,
              "settings": {"target": TARGET, "levels": LEVELS, "map_rounds": MAP_ROUNDS,
                           "stocks": STOCKS, "hi_mults": HI_MULTS, "regrowth": REGROWTH,
                           "designs": DESIGNS, "sealed_rounds": SEALED_ROUNDS,
                           "no_return_stock": no_return_stock(),
                           "query": "Finite-horizon zero-sum reachability; coordinated full-information adversary; pure stage strategies bracketed by alpha/beta orders; chance by the kernel. Goals, horizon, discount, k, prior, search_depth and sanction_cost do not enter.",
                           "stocks_reason": "Query states, not assumptions: a grid over the stock between collapse and capacity."},
              "results": {"map": power_map(), "horizon_and_size": horizon_and_size(),
                          "profiles": profiles(), "best_prevention": best_prevention(),
                          "sealed": sealed_checks()}}
    print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))
