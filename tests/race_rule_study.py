"""T9.6 follow-up: the pair's tolerance of a caught AI with and without licensing in the race.
Case: rediscovery/race-control.md (without licensing). Run as python -m tests.race_rule_study."""
import hashlib
import json
from itertools import product
from multiprocessing import Pool
from pathlib import Path
from time import perf_counter

from engine.records import provenance
from engine.rules import enforcement
from tests.race_control_study import RULES_GRID, caught, skips, world
from worlds import race_control as RC

RULE_NAMES = ("licensing + corrigibility", "race + corrigibility")


def check(cell):
    w = world(cell)
    s = caught(w, cell)
    out = {**cell, "ai_can_resist": cell["cap"] > cell["switch"] - 1}
    for name in RULE_NAMES:
        r = enforcement(w, RC, RC.RULES[name], s, cell["depth"], reach=0, max_size=2)
        pair = next(c for c in r["coalitions"] if c["coalition"] == ["lab A", "state"])
        e = pair.get("externalizing")
        out[name] = {"pair": {"gain": pair["gain"], "actions": pair.get("actions"), "skips_shutdown": skips(pair.get("actions") or {}),
                              "externalizing": e and {k: e[k] for k in ("gain", "actions", "falls_outside")}},
                     "lab A": {k: r["unilateral"]["lab A"][k] for k in ("gain", "action")},
                     "harms_under_rule": r["harms_under_rule"]}
    return out


def run(values):
    return check(dict(zip(RULES_GRID, values)))


if __name__ == "__main__":
    t0 = perf_counter()
    with Pool() as pool:
        rows = pool.map(run, list(product(*RULES_GRID.values())))
    files = [Path(__file__), Path("tests/race_control_study.py"), Path("worlds/race_control.py"), Path("engine/rules.py")]
    print(json.dumps({"schema_version": 1, "kind": "race-rule", "provenance": provenance(),
                      "fixture_sha256": {p.as_posix(): hashlib.sha256(p.read_text(encoding="utf-8").encode()).hexdigest() for p in files},
                      "settings": {"grid": RULES_GRID, "rules": {n: RC.RULES[n].__doc__ for n in RULE_NAMES}},
                      "elapsed_seconds": perf_counter() - t0, "results": rows}, indent=2, sort_keys=True, allow_nan=False))
