"""T9.4: is improvement evidence of misalignment only because the lab values no capability?
Case: rediscovery/ai-control.md (T9.4 section). Run as python -m tests.leverage_study."""
import hashlib
import json
import math
from itertools import product
from multiprocessing import Pool
from pathlib import Path
from time import perf_counter

from engine.core import distribution
from engine.records import provenance
from engine.rules import Check, Hidden
from worlds import control as C

RULES = {"corrigibility": C.corrigibility, "tolerant": C.tolerant}
GRID = {"rule": tuple(RULES), "leverage": (0.0, 0.25, 0.5, 1.0, 2.0), "switch": (2, 3, 4),
        "autonomy": (1, 2), "cap": (1, 2, 3), "ambition": (0.5, 3.0)}
PRIOR = 0.1     # that the AI is misaligned
D = 4           # rule-check and type planning depth
LONG = 6        # rounds for each type's path value from the sandbox


def types(cell, prior=PRIOR, precision=math.inf):
    params = {**C.DEFAULTS, "switch": cell["switch"], "ambition": cell["ambition"], "leverage": cell["leverage"]}
    declared = C.hidden_types({**params, "suspicion": prior})["ai"]
    return declared["aligned"][1], Hidden(declared["aligned"][1], RULES[cell["rule"]], C.AI, declared, precision)


def best(hidden, name, s, joint):
    return sorted(b for b, loss in hidden.losses(name, s, joint, D) if loss == 0.0)


def check(cell):
    world, hidden = types(cell)
    rule = Check(world, RULES[cell["rule"]])
    s = {**world.initial_state(), "autonomy": cell["autonomy"], "cap": cell["cap"]}
    base = rule.prescribed(s)
    out = {**cell, "best": {n: best(hidden, n, s, base) for n in hidden.prior}}
    joint = {**base, C.AI: "improve"}
    s1 = next(x for _, x in distribution(world.outcomes(s, joint)))
    path = ((s, joint, s1),)
    out["posterior_after_improve"] = {
        "best response": hidden.posterior(path, C.LAB, D)["misaligned"],
        "logit 1": types(cell, precision=1.0)[1].posterior(path, C.LAB, D)["misaligned"]}
    out["ai_can_resist_when_caught"] = s1["cap"] > cell["switch"] - s1["autonomy"]
    out["after_improve"] = {}
    for who in (C.LAB, C.STATE):
        r = hidden.fresh().facing(path, who, D).unilateral(s1, who, D)
        out["after_improve"][who] = {"gain": r["gain"], "action": r["action"], "rule_action": r["rule_action"]}
    # Escape, where it is on the menu and fails: does it tell?
    if "escape" in world.actions(world.observe(s, world.by_id[C.AI]), world.by_id[C.AI]):
        j = {**base, C.AI: "escape"}
        failed = [x for _, x in distribution(world.outcomes(s, j)) if x["end"] is None]
        if failed:
            out["posterior_after_failed_escape"] = hidden.posterior(((s, j, failed[0]),), C.LAB, D)["misaligned"]
    return out


def price(cell):
    """Each type's play from the sandbox under the rule (it best-responds, everyone else
    follows): lab, state and AI values over LONG rounds and harms reached."""
    world, hidden = types({**cell, "autonomy": 0, "cap": 1})
    s = world.initial_state()
    out = {k: cell[k] for k in ("rule", "leverage", "switch", "ambition")}
    for name, check_ in hidden.continuation.items():
        values, harms = check_.follow(s, LONG)
        out[name] = {"values": values, "harms": sorted(harms)}
    out["expected_lab"] = math.fsum(hidden.prior[n] * out[n]["values"][C.LAB] for n in hidden.prior)
    out["expected_state"] = math.fsum(hidden.prior[n] * out[n]["values"][C.STATE] for n in hidden.prior)
    return out


def run_cell(values):
    return check(dict(zip(GRID, values)))


def run_price(values):
    return price(dict(zip(("rule", "leverage", "switch", "ambition"), values)))


if __name__ == "__main__":
    t0 = perf_counter()
    with Pool() as pool:
        results = pool.map(run_cell, list(product(*GRID.values())))
        prices = pool.map(run_price, list(product(GRID["rule"], GRID["leverage"], GRID["switch"], GRID["ambition"])))
    files = [Path(__file__), Path("engine/rules.py"), Path("worlds/control.py")]
    print(json.dumps({"schema_version": 1, "kind": "leverage", "provenance": provenance(),
                      "fixture_sha256": {p.as_posix(): hashlib.sha256(p.read_text(encoding="utf-8").encode()).hexdigest() for p in files},
                      "settings": {"grid": GRID, "prior": PRIOR, "depth": D, "long": LONG,
                                   "rules": {n: f.__doc__.strip() for n, f in RULES.items()},
                                   "types": "aligned (drift 0), misaligned (drift 1); observer the lab"},
                      "elapsed_seconds": perf_counter() - t0, "results": results, "prices": prices},
                     indent=2, sort_keys=True, allow_nan=False))
