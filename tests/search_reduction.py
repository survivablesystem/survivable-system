"""T1.4 paired exact evidence. Run as python -m tests.search_reduction."""
from dataclasses import replace
import hashlib
import json
import math
from pathlib import Path
import random
from time import perf_counter
from types import MethodType

from engine.core import Search, SearchLimitExceeded, World, action_values, best, distribution
from engine.records import provenance, run_record
from engine.sweep import sample_params
from tests.planner_cases import audit
from worlds import commons


def reference(params, rng):
    world = commons.make(params, rng)
    world.reward_outcomes = MethodType(World.reward_outcomes, world)
    return world


def decision(params, after_high, reduced, budget=20_000):
    world = (commons.make if reduced else reference)(params, random.Random(0))
    state = world.initial_state()
    if after_high:
        state = world.step(state, {a.id: ("hi", False) for a in world.agents}, world.rng)
    actor = replace(world.agents[0], node_budget=budget)
    search = Search(world, actor)
    start = perf_counter()
    status, values = "complete", None
    try:
        observation, support = search.initial(state, actor)
        values = search.values(support, observation, actor, actor.depth, actor.k, False)
    except SearchLimitExceeded:
        status = "search_limit"
    return {"status": status, "values": values, "chosen": best(values)[0] if values else None,
            "nodes": search.nodes, "budget": budget, "elapsed_seconds": perf_counter() - start}


def marginal_checks():
    rng = random.Random(437)
    rows = []
    for _ in range(128):
        params = sample_params(commons.SPACE, rng)
        world = commons.make(params, random.Random(0))
        stock = rng.choice([0.0, 5.0, 10.0, 50.0, 100.0])
        state = {**world.initial_state(), "S": stock, "collapsed": stock == 0}
        joint = {a.id: rng.choice(world.actions(world.observe(state, a), a)) for a in world.agents}
        physical = distribution(world.outcomes(state, joint))
        marginal = distribution(world.reward_outcomes(state, joint))
        exact = {a.id: math.fsum(p * world.value(s, a) for p, s in physical) for a in world.agents}
        reduced = {a.id: math.fsum(p * r[a.id] for p, r in marginal) for a in world.agents}
        rows.append({"params": params, "stock": stock, "joint": joint,
                     "physical_branches": len(physical), "exact": exact, "reduced": reduced,
                     "max_absolute_error": max(abs(exact[i] - reduced[i]) for i in exact)})
    return rows


def study():
    decisions = []
    for n, depth in [(4, 2), (4, 3), (8, 2), (10, 2), (10, 3)]:
        params = {**commons.DEFAULTS, "n": n, "search_depth": depth}
        for after_high in (False, True):
            exact = decision(params, after_high, False)
            reduced = decision(params, after_high, True)
            error = None
            if exact["values"] is not None and reduced["values"] is not None:
                error = max(abs(a[1] - b[1]) for a, b in zip(exact["values"], reduced["values"]))
            decisions.append({"params": params, "after_high": after_high,
                              "full_kernel": exact, "reduced": reduced, "max_absolute_error": error})
    # Extra cap only certifies the newly covered value; it is not default coverage.
    extended_reference = decision({**commons.DEFAULTS, "n": 8}, True, False, budget=2_000_000)
    runs = []
    for name, overrides in [("baseline", {}), ("depth-3", {"search_depth": 3}),
                            ("eight-users", {"n": 8}), ("ten-users", {"n": 10}),
                            ("unpaid", {"confiscation_to": "stock"})]:
        params = {**commons.DEFAULTS, **overrides}
        for seed in (0, 1):
            row = {"case": name, "seed": seed}
            for mode, factory in [("full_kernel", reference), ("reduced", commons.make)]:
                start = perf_counter()
                row[mode] = run_record(factory, params, 30, seed, include_trace=True)
                row[mode + "_seconds"] = perf_counter() - start
            row["identical_record"] = row["full_kernel"] == row["reduced"]
            runs.append(row)
    # Retained pre-change evidence checks the physical-kernel refactor as well.
    archive = Path("evidence/planner-replacement-after.json")
    retained = []
    for group in json.loads(archive.read_text(encoding="utf-8"))["results"]:
        for saved in group["runs"]:
            actual = run_record(commons.make, saved["params"], saved["rounds_requested"],
                                saved["seed"], include_trace=True)
            retained.append({"case": group["case"], "seed": saved["seed"],
                             "identical_record": json.loads(json.dumps(actual)) == saved})
    # Every baseline round and actor, not just the symmetric initial state.
    probes = []
    saved_probes = json.loads(Path("evidence/planner-limits.json").read_text(encoding="utf-8"))["results"]["baseline_action_probes"]
    world = commons.make(commons.DEFAULTS, random.Random(0))
    state = world.initial_state()
    for saved in saved_probes:
        values = {a.id: action_values(world, state, a) for a in world.agents}
        error = max(abs(v[1] - old[1]) for i in values for v, old in zip(values[i], saved["values"][i]))
        joint = {i: best(v)[0] for i, v in values.items()}
        probes.append({"round": saved["round"], "values": values, "max_absolute_error": error,
                       "same_actions": json.loads(json.dumps(joint)) == saved["actions"]})
        state = world.step(state, joint, world.rng)
    return {"decisions": decisions, "extended_reference": extended_reference,
            "runs": runs, "kernel_checks": marginal_checks(), "diagnostics": audit(),
            "retained_trace_checks": retained, "retained_value_probes": probes}


if __name__ == "__main__":
    paths = [Path(__file__), Path("tests/planner_cases.py"), Path("tests/test_search_reduction.py"),
             Path("tests/test_search.py"), Path("evidence/planner-replacement-after.json"),
             Path("evidence/planner-limits.json")]
    result = {"schema_version": 1, "kind": "search-reduction", "provenance": provenance(),
              "fixture_sha256": {p.as_posix(): hashlib.sha256(p.read_text(encoding="utf-8").encode()).hexdigest() for p in paths},
              "fixed": commons.FIXED, "fixed_reasons": commons.FIXED_REASONS,
              "settings": {"rounds": 30, "seeds": [0, 1], "probe_seed": 0,
                           "marginal_sampling_seed": 437, "marginal_samples": 128,
                           "stock_checks": [0, 5, 10, 50, 100], "reference_budget": 2_000_000,
                           "reference_budget_reason": "Certify one n=8 value, not default-cap coverage.",
                           "reference": "Current planner using World.reward_outcomes (full physical kernel).",
                           "error": "Exact algebra; reported discrepancies are floating-point roundoff. Unfinished comparisons have null error."},
              "results": study()}
    print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))
