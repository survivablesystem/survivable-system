"""E17: the T9.5 escrow question with the state pricing the declared harm "shutdown resisted"
instead of `vigilance`. Case: rediscovery/ai-control.md (E17, V2-V3). Run as
python -m tests.price_study."""
import hashlib
import json
from itertools import product
from multiprocessing import Pool
from pathlib import Path
from time import perf_counter

from engine.prices import Prices
from engine.records import provenance
from engine.rules import Hidden
from tests.escrow_study import DESIGNS, PRIOR, gains, params, trail
from worlds import control as C

GRID = {"switch": (3, 4), "cap": (1, 2), "ambition": (0.5, 3.0), "leverage": (0.0, 0.5, 1.0, 2.0),
        "spillover": (0.0, 0.25, 0.5, 1.0), "depth": (4, 6, 8)}
MANDATES = {"none": (0.0, 0.0), "vigilance 0.5": (0.5, 0.0), "vigilance 2": (2.0, 0.0),
            "price 0.5": (0.0, 0.5), "price 2": (0.0, 2.0)}  # (vigilance, state's price on "shutdown resisted")


def check(cell):
    out = {**cell}
    for mandate, (vigilance, price) in MANDATES.items():
        build = lambda p, rng, price=price: Prices(C.make(p, rng), {(C.STATE, "shutdown resisted"): price}, C.HARMS)
        rows = {}
        for design, (escrow, rule) in DESIGNS.items():
            declared = C.hidden_types(params({**cell, "vigilance": vigilance}, escrow), build)["ai"]
            world = declared["aligned"][1]
            hidden = Hidden(world, rule, C.AI, declared)
            step0, step1 = trail(world, rule, cell)
            s1, s2 = step0[2], step1[2]
            rows[design] = {"can_resist_at_catch": s1["cap"] > cell["switch"] - s1["autonomy"],
                            "when_caught": gains(hidden, (step0,), s1, cell["depth"]),
                            "when_off": gains(hidden, (step0, step1), s2, cell["depth"])}
        out[mandate] = rows
    return out


def run_cell(values):
    return check(dict(zip(GRID, values)))


if __name__ == "__main__":
    t0 = perf_counter()
    with Pool() as pool:
        results = pool.map(run_cell, list(product(*GRID.values())))
    files = [Path(__file__), Path("tests/escrow_study.py"), Path("engine/prices.py"), Path("engine/rules.py"),
             Path("worlds/control.py")]
    print(json.dumps({"schema_version": 1, "kind": "price", "provenance": provenance(),
                      "fixture_sha256": {p.as_posix(): hashlib.sha256(p.read_text(encoding="utf-8").encode()).hexdigest() for p in files},
                      "settings": {"grid": GRID, "prior": PRIOR, "mandates": {k: {"vigilance": v, "price": q} for k, (v, q) in MANDATES.items()},
                                   "designs": {n: {"escrow": e, "rule": r.__doc__.strip()} for n, (e, r) in DESIGNS.items()}},
                      "elapsed_seconds": perf_counter() - t0, "results": results},
                     indent=2, sort_keys=True, allow_nan=False))
