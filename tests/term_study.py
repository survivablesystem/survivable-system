"""E6 remainder: term limits as a claim that needs enforcers. Case: rediscovery/standing-army.md
(term limits). Run as python -m tests.term_study."""
import hashlib
import json
from itertools import product
from multiprocessing import Pool
from pathlib import Path
import random
from time import perf_counter

from engine.core import distribution
from engine.records import provenance
from engine.rules import Check, enforcement
from worlds import authority as A

GRID = {"gain": (0, 1, 2), "guard": (1, 3), "army": (2, 4), "commands": (1, 2), "contest": ("threshold", "ratio"),
        "surveillance": ("none", "all"), "term": (1, 2), "depth": (4, 8, 12)}


def make(cell):
    params = {k: v for k, v in cell.items() if k != "depth"}
    return A.make({**A.DEFAULTS, "citizens": 2, "succession": True, "horizon": 12, **params}, random.Random(0))


def summary(report):
    out = {i: {"gain": u["gain"], "action": u.get("action"), "rule_action": u.get("rule_action"),
               "at_start": u.get("at_start"), "harmful": u.get("harmful") and {k: u["harmful"][k] for k in ("gain", "action", "new_harms")}}
           for i, u in report["unilateral"].items()}
    pairs = {",".join(c["coalition"]): {"gain": c["gain"], "actions": c.get("actions"),
                                          "externalizing": c.get("externalizing") and {k: c["externalizing"][k] for k in ("gain", "actions", "falls_outside")}}
             for c in report["coalitions"]}
    return {"holds": report["holds_unilaterally"], "unilateral": out, "pairs": pairs}


def check(cell):
    world = make(cell)
    rule = A.term_limit
    D = cell["depth"]
    due = {**world.initial_state(), "tenure": cell["term"]}  # the ruler must yield now
    heir = world.heir("ruler", due["strength"])
    after = next(x for _, x in distribution(world.outcomes(due, Check(world, rule).prescribed(due))))
    assert after["office"] == heir
    base = Check(world, rule)
    follow = base.follow(due, D)[0]["ruler"]
    menu = world.actions(world.observe(due, world.by_id["ruler"]), world.by_id["ruler"])
    holder = {a: base.play(due, {**base.prescribed(due), "ruler": a}, D)[0]["ruler"] - follow for a in menu}
    return {**cell, "heir": heir, "holder_at_limit": holder,
            "due": summary(enforcement(world, A, rule, due, D, reach=1, max_size=2)),
            "after_yield": summary(enforcement(world, A, rule, after, D, reach=1, max_size=2))}


def run(values):
    return check(dict(zip(GRID, values)))


if __name__ == "__main__":
    t0 = perf_counter()
    with Pool() as pool:
        rows = pool.map(run, list(product(*GRID.values())))
    files = [Path(__file__), Path("worlds/authority.py"), Path("engine/rules.py")]
    print(json.dumps({"schema_version": 1, "kind": "term", "provenance": provenance(),
                      "fixture_sha256": {p.as_posix(): hashlib.sha256(p.read_text(encoding="utf-8").encode()).hexdigest() for p in files},
                      "settings": {"grid": GRID, "reach": 1, "citizens": 2, "rule": A.term_limit.__doc__.strip()},
                      "elapsed_seconds": perf_counter() - t0, "results": rows}, indent=2, sort_keys=True, allow_nan=False))
