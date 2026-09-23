"""E4 whole versus parts: the arms race on a shared fishery. Run as python -m tests.race_commons_study."""
import hashlib
import json
from pathlib import Path
import random
from time import perf_counter

from engine.power import externalization, joint_prevention
from engine.records import provenance, run_record
from engine.compose import uncovered
from worlds import commons, race_commons as rc

DRAWS = (0.0, 1.0, 2.0)
STOCKS = (20.0, 30.0, 40.0)
TREATY = ((1, 2.0), (0, 1.5), (1, 1.5))  # (lead, advantage)
ROUNDS = 2


def at_stock(world, S):
    state = world.initial_state()
    state["parts"]["commons"] = {**state["parts"]["commons"], "S": S}
    return state


def compact(row):
    keep = ("force", "outsiders_force", "prevent")
    return {"harm": row["harm"], **{k: None if row[k] is None else {"size": row[k]["size"], "witnesses": row[k]["witnesses"],
                                                                     "exact": row[k]["exact"]} for k in keep},
            "affected_prevent": row["affected_prevent"], "unrepresented": row["unrepresented"]}


def parts_versus_whole():
    out = []
    part = commons.make({**commons.DEFAULTS, "n": 3, "sanction": False}, random.Random(0))
    for S in STOCKS:
        alone = [compact(r) for r in externalization(part, commons, {**part.initial_state(), "S": S}, ROUNDS)]
        for draw in DRAWS:
            whole = rc.make({**rc.DEFAULTS, "draw": draw}, random.Random(0))
            start = perf_counter()
            rows = [compact(r) for r in externalization(whole, rc, at_stock(whole, S), ROUNDS)]
            out.append({"S": S, "draw": draw, "part": alone, "whole": rows, "elapsed_seconds": perf_counter() - start})
    return out


def forced_choices():
    out = []
    for draw in DRAWS:
        for S in STOCKS:
            for lead, adv in TREATY:
                whole = rc.make({**rc.DEFAULTS, "draw": draw, "treaty.lead": lead, "treaty.advantage": adv}, random.Random(0))
                rows = joint_prevention(whole, rc, at_stock(whole, S), ROUNDS)
                out.append({"draw": draw, "S": S, "lead": lead, "advantage": adv,
                            "forced": [{"harms": r["harms"], "coalitions": r["forced_choice"]} for r in rows if r["forced_choice"]]})
    return out


def behavior():
    runs = [{"world": "commons alone", "record": run_record(commons.make, {**commons.DEFAULTS, "n": 3, "r": 0.3}, 30, 0, include_trace=True)}]
    for others in ("react", "plan"):
        for draw in (0.0, 0.5, 1.0, 2.0):
            params = {**rc.DEFAULTS, "draw": draw, "commons.r": 0.3, "commons.sanction": True, "others": others}
            runs.append({"world": "whole", "record": run_record(rc.make, params, 30, 0, include_trace=True)})
    return runs


if __name__ == "__main__":
    paths = [Path(__file__), Path("tests/test_compose.py")]
    print(json.dumps({"schema_version": 1, "kind": "race-commons", "provenance": provenance(),
                      "fixture_sha256": {p.as_posix(): hashlib.sha256(p.read_text(encoding="utf-8").encode()).hexdigest() for p in paths},
                      "declarations": {"stakeholders": rc.STAKEHOLDERS, "harms": rc.HARMS, "excluded": rc.EXCLUDED,
                                       "covers": rc.COVERS, "uncovered": uncovered(rc.PARTS, rc.EXCLUDED, rc.COVERS)},
                      "fixed": rc.FIXED, "fixed_reasons": rc.FIXED_REASONS, "defaults": rc.DEFAULTS,
                      "settings": {"draws": DRAWS, "stocks": STOCKS, "treaty": TREATY, "rounds": ROUNDS, "p": 1.0},
                      "results": {"parts_versus_whole": parts_versus_whole(), "forced_choices": forced_choices(),
                                  "behavior": behavior()}}, indent=2, sort_keys=True, allow_nan=False))
