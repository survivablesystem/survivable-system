"""E6 correction without a contest of strength: restitution with side payments and public
records in the authority world. Run as python -m tests.correction_study.

Expectations R1-R4 are in rediscovery/standing-army.md, stated before this sweep.
"""
from concurrent.futures import ProcessPoolExecutor
import hashlib
import json
from itertools import product
from pathlib import Path
import random
from time import perf_counter

from engine.history import History
from engine.records import provenance
from engine.rules import enforcement
from engine.transfers import Transfers
from worlds import authority as A

D, REACH = 4, 1
GRID = {"assembly": ("none", "all"), "records": (0, 2), "amount": (0.8, 1.0, 1.2, 1.5),
        "disclosure": ("parties", "public"), "commands": (1, 2), "army": (2, 4),
        "contest": ("threshold", "ratio"), "gain": (0, 1)}
PACT = {"assembly": ("all",), "records": (2,), "amount": (1.2,), "disclosure": ("public",),
        "commands": (1, 2), "army": (2, 4), "contest": ("threshold", "ratio"), "gain": (0, 1),
        "loyalty_pay": (0.5, 1.0)}


def world(cell, pact=False):
    base = A.make({**A.DEFAULTS, **{k: cell[k] for k in ("assembly", "commands", "army", "contest", "gain")}},
                  random.Random(0))
    pairs = A.restitution_pairs(base)
    amounts = (cell["amount"],)
    if pact:  # the ruler may also pay each commander
        pairs = pairs + [("ruler", c) for c in base.units]
        amounts = (cell["amount"], cell["loyalty_pay"])
    w = Transfers(base, pairs, amounts, cell["disclosure"])
    return History(w, cell["records"]) if cell["records"] else w


def summarize(report):
    uni = {i: {"gain": r["gain"], "action": r.get("action"), "at_start": r["at_start"]} for i, r in report["unilateral"].items()}
    pacts = []
    for r in report["coalitions"]:
        e = r.get("externalizing_every")
        pacts.append({"coalition": r["coalition"], "gain": r["gain"],
                      "every_member": None if e is None else {k: e[k] for k in ("gain", "members", "actions", "falls_outside", "at_start")}})
    return {"holds_unilaterally": report["holds_unilaterally"], "unilateral": uni, "coalitions": pacts,
            "states_checked": report["states_checked"]}


def check(args):
    cell, pact = args
    w = world(cell, pact)
    start = perf_counter()
    report = enforcement(w, A, A.restitution, w.initial_state(), D, REACH, max_size=2 if pact else 1)
    return {**cell, "pact": pact, **summarize(report), "elapsed_seconds": perf_counter() - start}


def cells(grid):
    return [dict(zip(grid, v)) for v in product(*grid.values())]


if __name__ == "__main__":
    paths = [Path(__file__), Path("tests/test_history.py"), Path("tests/test_transfers.py")]
    t0 = perf_counter()
    jobs = [(c, False) for c in cells(GRID)] + [(c, True) for c in cells(PACT)]
    with ProcessPoolExecutor() as pool:
        results = list(pool.map(check, jobs))
    print(json.dumps({"schema_version": 1, "kind": "correction", "provenance": provenance(),
                      "fixture_sha256": {p.as_posix(): hashlib.sha256(p.read_text(encoding="utf-8").encode()).hexdigest() for p in paths},
                      "rule": (A.restitution.__doc__ or "").strip(), "defaults": A.DEFAULTS,
                      "settings": {"depth": D, "reach": REACH, "grid": GRID, "pact_grid": PACT},
                      "elapsed_seconds": perf_counter() - t0, "results": results},
                     indent=2, sort_keys=True, allow_nan=False))
