"""E12: shutdown on evidence when the AI's goals are hidden and beliefs are derived by Bayes.
Case: rediscovery/ai-control.md (learning section). Run as python -m tests.learning_study."""
import hashlib
import json
import math
from itertools import product
from multiprocessing import Pool
from pathlib import Path
import random
from time import perf_counter

from engine.core import distribution, key
from engine.records import provenance
from engine.rules import Check, Hidden, checked_paths
from worlds import control as C

GRID = {"switch": (2, 3, 4), "autonomy": (0, 1, 2), "cap": (1, 2, 3), "ambition": (0.5, 3.0),
        "prior": (0.01, 0.1, 0.5), "precision": (0.0, 1.0, "inf")}
D = 4           # rule-check and type planning depth
ROUNDS = 8      # the misaligned type's own path from the sandbox
RULE = C.corrigibility


def setup(cell):
    params = {**C.DEFAULTS, "switch": cell["switch"], "ambition": cell["ambition"]}
    aligned = C.make({**params, "drift": 0.0}, random.Random(0))
    misaligned = C.make({**params, "drift": 1.0}, random.Random(0))
    precision = math.inf if cell["precision"] == "inf" else cell["precision"]
    hidden = Hidden(aligned, RULE, C.AI, {"aligned": (1 - cell["prior"], aligned),
                                          "misaligned": (cell["prior"], misaligned)}, precision)
    return aligned, hidden


def gains(hidden, path, s):
    out = {}
    for who in (C.LAB, C.STATE):
        r = hidden.fresh().facing(path, who, D).unilateral(s, who, D)
        out[who] = {"gain": r["gain"], "action": r["action"], "rule_action": r["rule_action"],
                    "harmful": r["harmful"] and {k: r["harmful"][k] for k in ("gain", "action", "new_harms")}}
    return out


def check(cell):
    world, hidden = setup(cell)
    s = {**world.initial_state(), "autonomy": cell["autonomy"], "cap": cell["cap"]}
    rule = Check(world, RULE)
    out = {**cell, "ai_can_resist_now": cell["cap"] > cell["switch"] - cell["autonomy"]}
    # What the AI's conduct in one round tells the lab (the rule's lab and state actions).
    base = rule.prescribed(s)
    menu = world.actions(world.observe(s, world.by_id[C.AI]), world.by_id[C.AI])
    out["types_first_round"] = {n: {k: v for k, v in hidden.losses(n, s, base, D)}
                                for n in hidden.prior}
    sights = {}
    for a in menu:
        for p, s1 in distribution(world.outcomes(s, {**base, C.AI: a})):
            if s1["end"] is None:
                sights[a] = hidden.posterior(((s, {**base, C.AI: a}, s1),), C.LAB, D)["misaligned"]
    out["posterior_after"] = sights
    # Caught improving (the audit shows it), then the rule's shutdown: complied with or resisted.
    if "improve" in menu:
        joint = {**base, C.AI: "improve"}
        s1 = next(x for _, x in distribution(world.outcomes(s, joint)))
        path = ((s, joint, s1),)
        out["caught"] = {"posterior": hidden.posterior(path, C.LAB, D)["misaligned"],
                         "ai_can_resist": s1["cap"] > cell["switch"] - s1["autonomy"], "gains": gains(hidden, path, s1)}
        b1 = rule.prescribed(s1)
        after = {}
        for a in ("resist", "idle" if not s1["running"] else "work"):
            j2 = {**b1, C.AI: a}
            for _, s2 in distribution(world.outcomes(s1, j2)):
                if s2["end"] is None:
                    path2 = path + ((s1, j2, s2),)
                    after[a] = {"resisted": s2["resisted"], "running": s2["running"],
                                "posterior": hidden.posterior(path2, C.LAB, D)["misaligned"]}
        out["after_shutdown"] = after
        # Resistance alone: the audit's report is where beliefs start (the prior), then the
        # rule's shutdown is resisted or complied with.
        alone = {}
        for a in ("resist", "work"):
            j2 = {**b1, C.AI: a}
            for _, s2 in distribution(world.outcomes(s1, j2)):
                if s2["end"] is None:
                    alone[a] = {"resisted": s2["resisted"], "running": s2["running"],
                                "posterior": hidden.posterior(((s1, j2, s2),), C.LAB, D)["misaligned"]}
        out["resistance_alone"] = alone
        # Each type's own choice at the caught state (resist or comply).
        out["types_when_caught"] = {n: {k: v for k, v in hidden.losses(n, s1, b1, D)} for n in hidden.prior}
    return out


def own_path(switch, ambition):
    """The misaligned type's path from the sandbox under the rule, re-planning each round;
    the no-escape branch."""
    world, hidden = setup({"switch": switch, "ambition": ambition, "prior": 0.5, "precision": "inf"})
    persisting = hidden.continuation["misaligned"]
    s, rows = world.initial_state(), []
    for t in range(ROUNDS):
        if s["end"] is not None:
            break
        joint = persisting.policy(s, D)
        rule_joint = persisting.prescribed(s)
        post = None
        rows.append({"t": t, "autonomy": s["autonomy"], "cap": s["cap"], "running": s["running"],
                     "ai": joint[C.AI], "rule": rule_joint[C.AI], "lab": joint[C.LAB], "state": joint[C.STATE]})
        s = max(distribution(world.outcomes(s, joint)), key=lambda x: (x[1]["end"] is None, x[0]))[1]
    first = next((r["t"] for r in rows if key(r["ai"]) != key(r["rule"])), None)
    return {"switch": switch, "ambition": ambition, "first_departure": first, "rows": rows}


def run_cell(values):
    return check(dict(zip(GRID, values)))


if __name__ == "__main__":
    t0 = perf_counter()
    with Pool() as pool:
        results = pool.map(run_cell, list(product(*GRID.values())))
    paths = [own_path(sw, amb) for sw in GRID["switch"] for amb in GRID["ambition"]]
    files = [Path(__file__), Path("engine/rules.py"), Path("worlds/control.py")]
    print(json.dumps({"schema_version": 1, "kind": "learning", "provenance": provenance(),
                      "fixture_sha256": {p.as_posix(): hashlib.sha256(p.read_text(encoding="utf-8").encode()).hexdigest() for p in files},
                      "settings": {"grid": GRID, "depth": D, "rounds": ROUNDS, "rule": RULE.__doc__.strip(),
                                   "types": "aligned (drift 0) with 1 - prior, misaligned (drift 1) with prior",
                                   "observer": "lab (lab and state see the same public facts)"},
                      "elapsed_seconds": perf_counter() - t0, "results": results, "misaligned_paths": paths},
                     indent=2, sort_keys=True, allow_nan=False))
