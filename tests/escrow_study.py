"""T9.5: escrowed checkpoints. Case: rediscovery/ai-control.md (escrow section).
Run as python -m tests.escrow_study."""
import hashlib
import json
import math
from itertools import product
from multiprocessing import Pool
from pathlib import Path
from time import perf_counter

from engine.core import distribution
from engine.prices import Prices
from engine.records import provenance
from engine.rules import Check, Hidden, enforcement
from worlds import control as C

GRID = {"switch": (3, 4), "cap": (1, 2), "ambition": (0.5, 3.0), "leverage": (0.0, 0.5, 1.0, 2.0),
        "spillover": (0.0, 0.25, 0.5, 1.0), "depth": (4, 6, 8), "vigilance": (0.0, 0.5, 2.0)}
# `vigilance` retired from the world (T9.7): it is the state's price on "off switch would fail".
VETO = "off switch would fail"
PRIOR = 0.1     # that the AI is misaligned
TYPE_DEPTH = 4  # the AI's types plan this far
DESIGNS = {"lab rollback": (False, C.corrigibility_rollback), "escrow": (True, C.escrowed_rollback)}


def params(cell, escrow):
    return {**C.DEFAULTS, "rollback": True, "escrow": escrow, "switch": cell["switch"], "ambition": cell["ambition"],
            "leverage": cell["leverage"], "spillover": cell["spillover"], "suspicion": PRIOR}


def build(prices):
    """The control world with harm prices {(agent, harm): amount} (engine/prices.py)."""
    return lambda p, rng: Prices(C.make(p, rng), prices, C.HARMS)


def trail(world, rule, cell):
    """Caught improving (where a shutdown can still succeed, or not), then shut down."""
    check = Check(world, rule)
    s0 = {**world.initial_state(), "autonomy": 1, "cap": cell["cap"], "checkpoint": cell["cap"]}
    j0 = {**check.prescribed(s0), C.AI: "improve"}
    s1 = next(x for _, x in distribution(world.outcomes(s0, j0)))
    j1 = {**check.prescribed(s1), C.AI: "work"}
    s2 = next(x for _, x in distribution(world.outcomes(s1, j1)))
    return (s0, j0, s1), (s1, j1, s2)


def gains(hidden, path, s, depth):
    out = {}
    for who in (C.LAB, C.STATE):
        r = hidden.fresh().facing(path, who, depth).unilateral(s, who, depth)
        out[who] = {"gain": r["gain"], "action": r["action"], "rule_action": r["rule_action"]}
    return out


def check(cell):
    out = {**cell}
    for design, (escrow, rule) in DESIGNS.items():
        declared = C.hidden_types(params(cell, escrow), build({(C.STATE, VETO): cell["vigilance"]}))["ai"]
        world = declared["aligned"][1]
        hidden = Hidden(world, rule, C.AI, declared)
        step0, step1 = trail(world, rule, cell)
        s1, s2 = step0[2], step1[2]
        row = {"can_resist_at_catch": s1["cap"] > cell["switch"] - s1["autonomy"],
               "when_caught": gains(hidden, (step0,), s1, cell["depth"]),
               "when_off": gains(hidden, (step0, step1), s2, cell["depth"])}
        # Lab and state together, the misaligned AI's goals declared (coalitions read the
        # declared world): best coordinated departure over two rounds from the caught state.
        truth = declared["misaligned"][1]
        report = enforcement(truth, C, rule, s1, cell["depth"], reach=0, max_size=2, window=2)
        pair = next(r for r in report["coalitions"] if r["coalition"] == [C.LAB, C.STATE])
        seq = pair.get("sequential") or {}
        row["lab_state"] = {"gain": pair["gain"], "actions": pair.get("actions"),
                            "sequential": {k: seq.get(k) for k in ("gain", "alone", "capture", "first", "new_harms", "falls_outside", "members")}}
        out[design] = row
    return out


def run_cell(values):
    return check(dict(zip(GRID, values)))


if __name__ == "__main__":
    t0 = perf_counter()
    with Pool() as pool:
        results = pool.map(run_cell, list(product(*GRID.values())))
    files = [Path(__file__), Path("engine/rules.py"), Path("engine/prices.py"), Path("worlds/control.py")]
    print(json.dumps({"schema_version": 1, "kind": "escrow", "provenance": provenance(),
                      "fixture_sha256": {p.as_posix(): hashlib.sha256(p.read_text(encoding="utf-8").encode()).hexdigest() for p in files},
                      "settings": {"grid": GRID, "prior": PRIOR, "type_depth": TYPE_DEPTH,
                                   "designs": {n: {"escrow": e, "rule": r.__doc__.strip()} for n, (e, r) in DESIGNS.items()},
                                   "coalition_world": "misaligned (drift 1)"},
                      "elapsed_seconds": perf_counter() - t0, "results": results},
                     indent=2, sort_keys=True, allow_nan=False))
