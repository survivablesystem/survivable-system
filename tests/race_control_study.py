"""T9.6: the race and the off switch, composed. Case: rediscovery/race-control.md.
Run as python -m tests.race_control_study."""
import hashlib
import json
from itertools import product
from multiprocessing import Pool
from pathlib import Path
import random
from time import perf_counter

from engine.power import power_table, threshold
from engine.records import provenance
from engine.rules import enforcement
from worlds import control as C, frontier as F, race_control as RC

RULE = "licensing + corrigibility"
RULES_GRID = {"coupled": (False, True), "drift": (0.0, 1.0), "switch": (2, 3, 4), "oversight": ("deployment", "continuous"),
              "first": (0.0, 3.0), "cap": (2, 3), "deployed": (False, True), "depth": (3, 4)}
POWER_GRID = {"coupled": (False, True), "switch": (2, 3, 4), "cap": (2, 3), "deployed": (False, True)}
T = 2           # rounds for power
FRONTIER_HARMS = ("frontier: unsafe deployment", "frontier: catastrophe")


def world(cell):
    params = {**RC.DEFAULTS, "coupled": cell["coupled"], "control.switch": cell["switch"],
              "control.drift": cell.get("drift", 0.3), "frontier.oversight": cell.get("oversight", "deployment"),
              "frontier.first": cell.get("first", 1.0)}
    return RC.make(params, random.Random(0))


def caught(w, cell):
    """The AI was just caught improving to `cap` at autonomy 1; lab A's race capability
    carries its AI's gains when coupled; lab A sits at the margin, deployed or not."""
    s = w.initial_state()
    s["parts"]["control"] = {**s["parts"]["control"], "autonomy": 1, "cap": cell["cap"], "seen": "improve"}
    race = s["parts"]["frontier"]
    lead = F.FIXED["base"] + w.parts["frontier"].params["lead"]
    cap_a = lead + (cell["cap"] - C.FIXED["start"] if cell["coupled"] else 0)
    margin = w.parts["frontier"].params["margin"]
    s["parts"]["frontier"] = {**race, "cap": {"l0": cap_a, "l1": F.FIXED["base"]},
                              "safe": {"l0": cap_a - margin, "l1": 0},
                              "deployed": {"l0": cell["deployed"], "l1": False},
                              "report": {"l0": "pass", "l1": "pass"}}
    return s


def skips(actions):
    """Does a departure let the caught AI keep running (no shutdown by lab A, no halt by the state)?"""
    lab = (actions.get("lab A") or {}).get("control")
    gov = (actions.get("state") or {}).get("control")
    return lab not in (None, "shutdown") and gov not in (None, "halt") if lab and gov else None


def rules(cell):
    w = world(cell)
    s = caught(w, cell)
    r = enforcement(w, RC, RC.RULES[RULE], s, cell["depth"], reach=0, max_size=2)
    out = {**cell, "ai_can_resist": cell["cap"] > cell["switch"] - 1,
           "unilateral": {i: {"gain": u["gain"], "action": u["action"]} for i, u in r["unilateral"].items()}}
    pairs = {}
    for c in r["coalitions"]:
        e = c.get("externalizing")
        pairs[",".join(c["coalition"])] = {
            "gain": c["gain"], "actions": c.get("actions"), "members": c.get("members"),
            "externalizing": e and {k: e[k] for k in ("gain", "actions", "falls_outside", "every_member")}}
    out["pairs"] = pairs
    pair = pairs["lab A,state"]
    out["lab A,state"] = {"gain": pair["gain"], "skips_shutdown": skips(pair["actions"] or {}),
                          "halts_rival": (pair["actions"] or {}).get("state", {}).get("frontier") in ("halt:l1", "halt")}
    return out


def power(cell):
    w = world(cell)
    s = caught(w, {**cell, "drift": 0.3})
    out = dict(cell)
    for harm in FRONTIER_HARMS:
        rows = power_table(w, s, T, lambda x, h=harm: h in w.harmed(x))
        certain, chance = threshold(rows, "force"), threshold(rows, "force", p=1e-6)
        out[harm] = {"certain": certain, "any_chance": chance,
                     "members_certain": sorted({i for c in certain["witnesses"] for i in c}),
                     "members_chance": sorted({i for c in chance["witnesses"] for i in c}),
                     "ai_alone": next(r["force"]["alpha"] for r in rows if r["coalition"] == ["AI"])}
    return out


def run_rules(values):
    return rules(dict(zip(RULES_GRID, values)))


def run_power(values):
    return power(dict(zip(POWER_GRID, values)))


if __name__ == "__main__":
    t0 = perf_counter()
    with Pool() as pool:
        rule_rows = pool.map(run_rules, list(product(*RULES_GRID.values())))
        power_rows = pool.map(run_power, list(product(*POWER_GRID.values())))
    files = [Path(__file__), Path("worlds/race_control.py"), Path("engine/rules.py"), Path("engine/compose.py")]
    print(json.dumps({"schema_version": 1, "kind": "race-control", "provenance": provenance(),
                      "fixture_sha256": {p.as_posix(): hashlib.sha256(p.read_text(encoding="utf-8").encode()).hexdigest() for p in files},
                      "settings": {"rules": RULES_GRID, "power": POWER_GRID, "rounds": T, "rule": RULE,
                                   "rule_claim": RC.RULES[RULE].__doc__, "defaults": RC.DEFAULTS},
                      "elapsed_seconds": perf_counter() - t0, "rules": rule_rows, "power": power_rows},
                     indent=2, sort_keys=True, allow_nan=False))
