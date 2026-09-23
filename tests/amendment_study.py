"""E10 amendable rules in the frontier world: who can capture the rulebook by amendment.
Run as python -m tests.amendment_study. Expectations A1-A3 are in rediscovery/frontier-ai.md."""
from concurrent.futures import ProcessPoolExecutor
import hashlib
import json
from itertools import product
from pathlib import Path
import random
from time import perf_counter

from engine.constitution import KEEP, Constitution, constitutional
from engine.records import provenance
from engine.rules import enforcement
from worlds import frontier as F

GRID = {"liability": (0.0, 5.0), "first": (0.0, 1.0, 3.0), "oversight": ("deployment", "continuous"),
        "lead": (0, 1), "rulemaking": ("state alone", "labs seated, majority", "labs seated, unanimity")}
VOTERS = {"state alone": (["state"], 1), "labs seated, majority": (["state", "l0", "l1"], 2),
          "labs seated, unanimity": (["state", "l0", "l1"], 3)}
D, REACH, WINDOW = 4, 1, 2


def amendment_captures(report):
    out = []
    for c in report["coalitions"]:
        for kind, e in (("one round", c.get("externalizing")), ("over rounds", c.get("sequential"))):
            if not e or not e.get("gain") or e["gain"] <= 1e-9 or (kind == "over rounds" and not e.get("capture")):
                continue
            acts = e.get("actions") or e.get("first")
            if any(a[1] != KEEP for a in acts.values()):
                out.append({"coalition": c["coalition"], "kind": kind, "gain": e["gain"], "every_member": e["every_member"],
                            "actions": acts, "falls_outside": e["falls_outside"]})
    return out


def check(cell):
    voters, threshold = VOTERS[cell["rulemaking"]]
    base = F.make({**F.DEFAULTS, **{k: v for k, v in cell.items() if k in F.SPACE}}, random.Random(0))
    world = Constitution(base, {"licensing": F.licensing, "race": F.race}, voters, threshold, "licensing")
    report = enforcement(world, F, constitutional, world.initial_state(), D, REACH, window=WINDOW)
    return {**cell, "holds_unilaterally": report["holds_unilaterally"], "no_harmful_departure": report["no_harmful_departure"],
            "amendment_captures": amendment_captures(report)}


if __name__ == "__main__":
    paths = [Path(__file__), Path("tests/test_constitution.py")]
    t0 = perf_counter()
    with ProcessPoolExecutor() as pool:
        results = list(pool.map(check, [dict(zip(GRID, v)) for v in product(*GRID.values())]))
    print(json.dumps({"schema_version": 1, "kind": "amendment", "provenance": provenance(),
                      "fixture_sha256": {p.as_posix(): hashlib.sha256(p.read_text(encoding="utf-8").encode()).hexdigest() for p in paths},
                      "settings": {"grid": GRID, "voters": VOTERS, "regimes": ["licensing", "race"], "initial": "licensing",
                                   "depth": D, "reach": REACH, "window": WINDOW},
                      "elapsed_seconds": perf_counter() - t0, "results": results},
                     indent=2, sort_keys=True, allow_nan=False, default=str))
