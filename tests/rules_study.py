"""E7 rules as claims across four worlds. Run as python -m tests.rules_study.

Audit expectations Q1-Q4 are in rediscovery/captured-auditor.md; the other worlds' rule
checks are recorded in their case files. One-shot departures, depth D, reach R.
"""
import hashlib
import json
from itertools import product
from pathlib import Path
import random
from time import perf_counter

from engine.records import provenance
from engine.rules import Check, enforcement
from worlds import audit, authority, commons, treaty

D, REACH = 4, 2
GRIDS = {
    "audit": {"exposure": (0.0, 0.2, 0.5, 1.0), "regulator": ("none", "revokes"),
              "assignment": ("firm", "fixed"), "premium": (0.0, 1.0, 2.0), "auditors": (1, 2)},
    "commons": {"n": (3,), "confiscation_to": ("stock", "sanctioners"), "sanction_cost": (0.1, 0.5),
                "hi_mult": (2, 4), "discount": (0.8, 0.95)},
    "treaty": {"verification": ("none", "exact"), "lead": (0, 1, 2), "contest": ("threshold", "ratio"),
               "prize": (0.5, 2.0, 5.0)},
    "authority": {"assembly": ("none", "all"), "surveillance": ("none", "all"), "commands": (1, 2),
                  "army": (2, 4), "gain": (0, 1), "rent": (0.5, 1.5)},
}
MODULES = {"audit": audit, "commons": commons, "treaty": treaty, "authority": authority}
DEPTH = {"commons": 3}  # commons menus are larger; depth 3 keeps the grid to minutes


def compact(report):
    uni = {i: None if r["gain"] is None else {"gain": r["gain"], "action": r.get("action"),
                                               "rule_action": r.get("rule_action"), "at_start": r["at_start"]}
           for i, r in report["unilateral"].items()}
    co = []
    for r in report["coalitions"]:
        e = r.get("externalizing")
        co.append({"coalition": r["coalition"], "gain": r["gain"], "actions": r.get("actions"),
                   "externalizing": None if e is None else e if e.get("gain") is None else
                   {k: e[k] for k in ("gain", "actions", "falls_outside", "at_start", "members")}})
    return {"holds_unilaterally": report["holds_unilaterally"], "unilateral": uni, "coalitions": co,
            "harms_under_rule": report["harms_under_rule"], "states_checked": report["states_checked"]}


def run(name):
    module, grid = MODULES[name], GRIDS[name]
    depth = DEPTH.get(name, D)
    out = []
    for values in product(*grid.values()):
        cell = dict(zip(grid, values))
        world = module.make({**module.DEFAULTS, **cell}, random.Random(0))
        for rule in module.RULES:
            start = perf_counter()
            report = enforcement(world, module, module.RULES[rule], world.initial_state(), depth, REACH)
            out.append({**cell, "rule": rule, "depth": depth, **compact(report), "elapsed_seconds": perf_counter() - start})
    return out


def audit_margins():
    """Per audit cell and rule, each agent's one-shot gain at a round with weak books: the
    decision state. The whole-grid maximum hides negative margins behind start-state ties."""
    out = []
    grid = GRIDS["audit"]
    for values in product(*grid.values()):
        cell = dict(zip(grid, values))
        world = audit.make({**audit.DEFAULTS, **cell}, random.Random(0))
        state = {**world.initial_state(), "weak": True}
        for rule in audit.RULES:
            check = Check(world, audit.RULES[rule])
            out.append({**cell, "rule": rule, "gains": {a.id: check.unilateral(state, a.id, D)["gain"] for a in world.agents},
                        "pair": check.joint(state, ["firm", "a0"], D)["gain"]})
    return out


if __name__ == "__main__":
    paths = [Path(__file__), Path("tests/test_rules.py"), Path("tests/test_audit.py")]
    t0 = perf_counter()
    results = {name: run(name) for name in MODULES}
    results["audit_margins"] = audit_margins()
    print(json.dumps({"schema_version": 1, "kind": "rules", "provenance": provenance(),
                      "fixture_sha256": {p.as_posix(): hashlib.sha256(p.read_text(encoding="utf-8").encode()).hexdigest() for p in paths},
                      "rules": {n: {r: (f.__doc__ or "").strip() for r, f in m.RULES.items()} for n, m in MODULES.items()},
                      "defaults": {n: m.DEFAULTS for n, m in MODULES.items()},
                      "settings": {"depth": D, "depth_overrides": DEPTH, "reach": REACH, "grids": GRIDS, "max_size": 2},
                      "elapsed_seconds": perf_counter() - t0, "results": results},
                     indent=2, sort_keys=True, allow_nan=False))
