"""T9.2 / E12: shutdown on evidence with a posterior that the caught AI persists.
Run as python -m tests.precaution_study."""
import hashlib
import json
from itertools import product
from pathlib import Path
import random
from time import perf_counter

from engine.records import provenance
from engine.rules import Check, unilateral_over
from worlds import control as C

GRID = {"switch": (2, 3, 4), "autonomy": (0, 1, 2), "cap": (1, 2, 3), "q": (0.0, 0.25, 0.5, 0.75, 1.0)}
D = 4


def check(cell):
    params = {**C.DEFAULTS, "switch": cell["switch"]}
    aligned = C.make({**params, "drift": 0.0}, random.Random(0))
    misaligned = C.make({**params, "drift": 1.0}, random.Random(0))
    s = {**aligned.initial_state(), "autonomy": cell["autonomy"], "cap": cell["cap"], "seen": "improve"}
    q = cell["q"]
    parts = [(q, Check(misaligned, C.corrigibility, persistent="ai")), (1 - q, Check(aligned, C.corrigibility))]
    out = {**cell, "ai_can_resist": cell["cap"] > cell["switch"] - cell["autonomy"]}
    for who in ("lab", "state"):
        r = unilateral_over(parts, s, who, D)
        out[who] = {k: r[k] for k in ("gain", "action", "rule_action")}
    for name, w in (("ai_aligned", aligned), ("ai_misaligned", misaligned)):
        r = Check(w, C.corrigibility).unilateral(s, "ai", D)
        out[name] = {k: r[k] for k in ("gain", "action", "rule_action")}
    return out


if __name__ == "__main__":
    t0 = perf_counter()
    results = [check(dict(zip(GRID, v))) for v in product(*GRID.values())]
    paths = [Path(__file__)]
    print(json.dumps({"schema_version": 1, "kind": "precaution", "provenance": provenance(),
                      "fixture_sha256": {p.as_posix(): hashlib.sha256(p.read_text(encoding="utf-8").encode()).hexdigest() for p in paths},
                      "settings": {"grid": GRID, "depth": D, "state": "the AI was caught improving (audit)",
                                   "rule": C.corrigibility.__doc__.strip()},
                      "elapsed_seconds": perf_counter() - t0, "results": results}, indent=2, sort_keys=True, allow_nan=False))
