"""T9.1 frontier AI: information, power, rules and who pays the evaluator.
Run as python -m tests.frontier_study. Expectations F1-F4 are in rediscovery/frontier-ai.md."""
from concurrent.futures import ProcessPoolExecutor
import hashlib
import json
from itertools import product
from pathlib import Path
import random
from time import perf_counter

from engine.power import PowerLimitExceeded, externalization, sure
from engine.records import provenance
from engine.rules import enforcement
from engine.transfers import Transfers
from worlds import frontier as F

BOTH = ("unsafe deployment", "safe progress blocked")
COALITIONS = (["state"], ["state", "evaluator"], ["state", "l0"], ["state", "l1"])
INFO = {"oversight": ("deployment", "continuous"), "margin": (0, 1, 2), "lead": (0, 1, 2),
        "capacity": (0.5, 1.0), "T": (2, 3)}
RULE_GRID = {"oversight": ("deployment", "continuous"), "margin": (0, 1), "first": (0.0, 1.0, 3.0),
             "liability": (0.0, 5.0, 10.0), "capacity": (0.5, 1.0), "lead": (0, 1)}
# evaluator_liability was added after the first run showed an evaluator with nothing at stake
# is captured without payment (recorded in the case file).
PAY_GRID = {"design": ("labs pay, private", "state pays, private channel", "state pays, public, halt payers"),
            "oversight": ("deployment", "continuous"), "first": (0.0, 3.0), "liability": (0.0, 5.0),
            "evaluator_liability": (0.0, 2.0, 10.0)}
D, REACH, AMOUNTS = 4, 1, (0.5, 1.5)


def cells(grid):
    return [dict(zip(grid, v)) for v in product(*grid.values())]


def make(cell):
    return F.make({**F.DEFAULTS, **{k: v for k, v in cell.items() if k in F.SPACE}}, random.Random(0))


def info(cell):
    w = make(cell)
    s = w.initial_state()
    both = lambda x: bool(set(BOTH) & w.harmed(x))
    unsafe = lambda x: "unsafe deployment" in w.harmed(x)
    out = {}
    for coalition in COALITIONS:
        name = ",".join(coalition)
        try:
            out[name] = {"both": sure(w, s, coalition, cell["T"], both),
                         "both_informed": sure(w, s, coalition, cell["T"], both, informed=True),
                         "unsafe": sure(w, s, coalition, cell["T"], unsafe)}
        except PowerLimitExceeded:
            out[name] = None
    return {**cell, "sure_avoid": out}


def compact(report):
    uni = {i: {**{k: r.get(k) for k in ("gain", "action", "rule_action", "at_start")},
               "harmful": None if r.get("harmful") is None else {k: r["harmful"][k] for k in ("gain", "action", "new_harms", "at_start")}}
           for i, r in report["unilateral"].items()}
    pairs = []
    for r in report["coalitions"]:
        keep = lambda e: None if e is None else e if e.get("gain") is None else \
            {k: e[k] for k in ("gain", "members", "actions", "falls_outside", "at_start", "every_member")}
        pairs.append({"coalition": r["coalition"], "gain": r["gain"], "externalizing": keep(r.get("externalizing")),
                      "externalizing_every": keep(r.get("externalizing_every"))})
    return {"holds_unilaterally": report["holds_unilaterally"], "no_harmful_departure": report["no_harmful_departure"],
            "unilateral": uni, "coalitions": pairs,
            "harms_under_rule": report["harms_under_rule"]}


def rules(cell):
    w = make(cell)
    return [{**cell, "rule": name, **compact(enforcement(w, F, rule, w.initial_state(), D, REACH))}
            for name, rule in F.RULES.items()]


def sequential(report):
    out = []
    for r in report["coalitions"]:
        q = r.get("sequential")
        if q and q.get("gain") is not None:
            out.append({"coalition": r["coalition"], **{k: q[k] for k in (
                "gain", "alone", "needs_all", "capture", "every_member", "members", "first", "new_harms", "falls_outside", "at_start")}})
    return out


def paid(cell):
    base = make(cell)
    if cell["design"].startswith("labs"):
        w = Transfers(base, [("l0", "evaluator"), ("l1", "evaluator")], AMOUNTS, "parties")
    else:
        disclosure = "public" if "public" in cell["design"] else "parties"
        w = Transfers(base, [("state", "evaluator"), ("l0", "evaluator"), ("l1", "evaluator")], AMOUNTS, disclosure)
    report = enforcement(w, F, F.licensing_paid, w.initial_state(), D, REACH, window=2)
    return {**cell, **compact(report), "sequential": sequential(report)}


def power():
    out = []
    for oversight in ("deployment", "continuous"):
        w = make({"oversight": oversight})
        out.append({"oversight": oversight, "harms": externalization(w, F, w.initial_state(), 3)})
    return out


if __name__ == "__main__":
    paths = [Path(__file__), Path("tests/test_frontier.py")]
    t0 = perf_counter()
    with ProcessPoolExecutor() as pool:
        results = {"information": list(pool.map(info, cells(INFO))),
                   "rules": [r for rows in pool.map(rules, cells(RULE_GRID)) for r in rows],
                   "payments": list(pool.map(paid, cells(PAY_GRID)))}
    results["power"] = power()
    print(json.dumps({"schema_version": 1, "kind": "frontier", "provenance": provenance(),
                      "fixture_sha256": {p.as_posix(): hashlib.sha256(p.read_text(encoding="utf-8").encode()).hexdigest() for p in paths},
                      "declarations": {"stakeholders": F.STAKEHOLDERS, "harms": F.HARMS, "excluded": F.EXCLUDED},
                      "rules": {n: (f.__doc__ or "").strip() for n, f in {**F.RULES, "licensing (paid)": F.licensing_paid}.items()},
                      "fixed": F.FIXED, "fixed_reasons": F.FIXED_REASONS, "defaults": F.DEFAULTS,
                      "settings": {"information": INFO, "coalitions": COALITIONS, "rules": RULE_GRID, "payments": PAY_GRID,
                                   "depth": D, "reach": REACH, "amounts": AMOUNTS, "power_rounds": 3,
                                   "payments_window": 2},
                      "elapsed_seconds": perf_counter() - t0, "results": results},
                     indent=2, sort_keys=True, allow_nan=False, default=str))
