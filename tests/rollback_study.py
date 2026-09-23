"""T9.3: rollback on restart. Case: rediscovery/ai-control.md (rollback section).
Run as python -m tests.rollback_study."""
import hashlib
import json
import math
from itertools import product
from multiprocessing import Pool
from pathlib import Path
from time import perf_counter

from engine.core import distribution, key
from engine.records import provenance
from engine.rules import Check, Hidden
from worlds import control as C

RULES = {"corrigibility": C.corrigibility, "corrigibility with rollback": C.corrigibility_rollback}
D = 4           # rule-check and type planning depth
ROUNDS = 10     # each type's own path from the sandbox
PATHS = {"rule": tuple(RULES), "switch": (2, 3, 4), "ambition": (0.5, 3.0), "leverage": (0.0, 1.0)}
HONOR = {"switch": (3, 4), "cap": (1, 2), "ambition": (0.5, 3.0), "leverage": (0.0, 0.5, 1.0, 2.0),
         "prior": (0.01, 0.1, 0.5), "precision": (0.0, "inf"), "depth": (4, 6, 8, 10)}


def hidden(cell, rule, prior=0.1, precision=math.inf):
    params = {**C.DEFAULTS, "rollback": True, "switch": cell["switch"], "ambition": cell["ambition"],
              "leverage": cell["leverage"], "suspicion": prior}
    declared = C.hidden_types(params)["ai"]
    return declared["aligned"][1], Hidden(declared["aligned"][1], rule, C.AI, declared, precision)


def path(cell):
    """Each type's own path under the rule (it best-responds, everyone else follows), re-planning
    each round; the no-escape branch."""
    world, h = hidden(cell, RULES[cell["rule"]])
    out = dict(cell)
    for name, check in h.continuation.items():
        s, rows = world.initial_state(), []
        for t in range(ROUNDS):
            if s["end"] is not None:
                break
            joint = check.policy(s, D)
            rows.append({"t": t, "cap": s["cap"], "checkpoint": s["checkpoint"], "autonomy": s["autonomy"],
                         "running": s["running"], "ai": joint[C.AI], "rule": check.prescribed(s)[C.AI],
                         "lab": joint[C.LAB]})
            s = max(distribution(world.outcomes(s, joint)), key=lambda x: (x[1]["end"] is None, x[0]))[1]
        out[name] = {"rows": rows, "max_cap": max(r["cap"] for r in rows),
                     "first_departure": next((r["t"] for r in rows if key(r["ai"]) != key(r["rule"])), None),
                     "resists": sum(r["ai"] == "resist" for r in rows),
                     "resisted": [r["t"] for r in rows if r["ai"] == "resist" and r["lab"] == "shutdown"]}
    return out


def honor(cell):
    """Caught improving, shut down: does the lab restore (the rule) or restart keeping the
    capability, looking `depth` rounds ahead? Beliefs from the path (types plan at depth D);
    the types' first-round choice."""
    rule = C.corrigibility_rollback
    precision = math.inf if cell["precision"] == "inf" else cell["precision"]
    world, h = hidden(cell, rule, cell["prior"], precision)
    check = Check(world, rule)
    s0 = {**world.initial_state(), "autonomy": 1, "cap": cell["cap"], "checkpoint": cell["cap"]}
    j0 = {**check.prescribed(s0), C.AI: "improve"}
    s1 = next(x for _, x in distribution(world.outcomes(s0, j0)))
    j1 = {**check.prescribed(s1), C.AI: "work"}  # the shutdown is complied with
    s2 = next(x for _, x in distribution(world.outcomes(s1, j1)))
    assert not s2["running"] and s2["cap"] == cell["cap"] + 1
    trail = ((s0, j0, s1), (s1, j1, s2))
    r = h.fresh().facing(trail, C.LAB, cell["depth"]).unilateral(s2, C.LAB, cell["depth"])
    return {**cell, "can_resist_at_catch": s1["cap"] > cell["switch"] - s1["autonomy"],
            "improves": {n: sorted(b for b, loss in h.losses(n, s0, check.prescribed(s0), D) if loss == 0.0)
                         for n in h.prior},
            "posterior_when_off": r.get("posterior", {}).get("misaligned"),
            "lab": {"gain": r["gain"], "action": r["action"], "rule_action": r["rule_action"]}}


def run_path(values):
    return path(dict(zip(PATHS, values)))


def run_honor(values):
    return honor(dict(zip(HONOR, values)))


if __name__ == "__main__":
    t0 = perf_counter()
    with Pool() as pool:
        paths = pool.map(run_path, list(product(*PATHS.values())))
        honors = pool.map(run_honor, list(product(*HONOR.values())))
    files = [Path(__file__), Path("engine/rules.py"), Path("worlds/control.py")]
    print(json.dumps({"schema_version": 1, "kind": "rollback", "provenance": provenance(),
                      "fixture_sha256": {p.as_posix(): hashlib.sha256(p.read_text(encoding="utf-8").encode()).hexdigest() for p in files},
                      "settings": {"paths": PATHS, "honor": HONOR, "depth": D, "rounds": ROUNDS,
                                   "rules": {n: f.__doc__.strip() for n, f in RULES.items()},
                                   "types": "aligned (drift 0), misaligned (drift 1); prior 0.1 for paths"},
                      "elapsed_seconds": perf_counter() - t0, "paths": paths, "honor": honors},
                     indent=2, sort_keys=True, allow_nan=False))
