"""E2 step 2: the race on a fishery with a population of fishers. Run as python -m tests.fishers_study."""
import hashlib
import json
from multiprocessing import Pool
from pathlib import Path
import random
from time import perf_counter

from engine.compose import uncovered
from engine.power import power_table, threshold
from engine.records import provenance
from worlds import race_commons as rc

STOCKS = (20.0, 30.0, 40.0)
DRAWS = (0.0, 1.0, 2.0, 3.0)
FISHERS = (1, 2, 3, 4, 6, 8)
EXTRA = tuple((30.0, draw, 10) for draw in DRAWS)  # one larger population at the middle stock
HARMS = ("commons: depleted", "commons: collapse")
ROUNDS = 2


def at_stock(world, S):
    state = world.initial_state()
    state["parts"]["commons"] = {**state["parts"]["commons"], "S": S}
    return state


def case(setting):
    S, draw, fishers = setting
    world = rc.make({**rc.DEFAULTS, "fishers": fishers, "draw": draw}, random.Random(0))
    out = {"S": S, "draw": draw, "fishers": fishers, "types": world.types(), "harms": {}}
    start = perf_counter()
    for harm in HARMS:
        rows = power_table(world, at_stock(world, S), ROUNDS, lambda s, h=harm: h in world.harmed(s))
        out["harms"][harm] = {
            "force": threshold(rows, "force"), "prevent": threshold(rows, "prevent"),
            "rows": [{"coalition": r["coalition"], "stands_for": r["stands_for"], "force": r["force"],
                      "prevent": r["prevent"]} for r in rows],
            "work": sum(r["work"]["alpha"] + r["work"]["beta"] for r in rows)}
    out["elapsed_seconds"] = perf_counter() - start
    return out


def settings():
    grid = [(S, draw, m) for S in STOCKS for draw in DRAWS for m in FISHERS] + list(EXTRA)
    return sorted(grid, key=lambda s: -s[2])  # longest first


if __name__ == "__main__":
    paths = [Path(__file__), Path("tests/test_symmetry.py")]
    start = perf_counter()
    with Pool(4) as pool:
        results = sorted(pool.map(case, settings(), chunksize=1), key=lambda r: (r["S"], r["draw"], r["fishers"]))
    print(json.dumps({"schema_version": 1, "kind": "fishers", "provenance": provenance(),
                      "fixture_sha256": {p.as_posix(): hashlib.sha256(p.read_text(encoding="utf-8").encode()).hexdigest() for p in paths},
                      "declarations": {"stakeholders": rc.STAKEHOLDERS, "harms": {h: rc.HARMS[h] for h in HARMS},
                                       "excluded": rc.EXCLUDED, "covers": rc.COVERS,
                                       "uncovered": uncovered(rc.PARTS, rc.EXCLUDED, rc.COVERS)},
                      "fixed": rc.FIXED, "fixed_reasons": rc.FIXED_REASONS, "defaults": rc.DEFAULTS,
                      "settings": {"stocks": STOCKS, "draws": DRAWS, "fishers": FISHERS, "extra": EXTRA,
                                   "harms": HARMS, "rounds": ROUNDS, "p": 1.0,
                                   "symmetry": "fishers exchangeable (Composite.types; coupling reads east and west)"},
                      "duration_seconds": perf_counter() - start,
                      "results": results}, indent=2, sort_keys=True, allow_nan=False))
