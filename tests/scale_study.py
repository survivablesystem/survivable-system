"""E2 exact power at population scale via declared symmetry. Run as python -m tests.scale_study."""
import hashlib
import json
from pathlib import Path
import random
from time import perf_counter

from engine.power import power_table, threshold
from engine.records import provenance
from worlds import commons

CASES = ([(2, n, S, sanction) for n in (2, 4, 6, 8, 10, 12, 16, 20) for S in (20.0, 30.0, 40.0) for sanction in (False,)]
         + [(3, n, 30.0, False) for n in (2, 4, 6, 8, 10, 12, 16, 20)]
         + [(2, n, 30.0, True) for n in (2, 4, 6, 8)])


def study():
    out = []
    for T, n, S, sanction in CASES:
        world = commons.make({**commons.DEFAULTS, "n": n, "sanction": sanction, "confiscation_to": "stock"}, random.Random(0))
        start = perf_counter()
        rows = power_table(world, {**world.initial_state(), "S": S}, T, "collapsed")
        out.append({"T": T, "n": n, "S": S, "sanction": sanction,
                    "force": threshold(rows, "force"), "prevent": threshold(rows, "prevent"),
                    "force_half": threshold(rows, "force", 0.5), "prevent_half": threshold(rows, "prevent", 0.5),
                    "by_size": [{"size": len(r["coalition"]), "stands_for": r["stands_for"], "force": r["force"],
                                 "prevent": r["prevent"]} for r in rows],
                    "work": sum(r["work"]["alpha"] + r["work"]["beta"] for r in rows),
                    "elapsed_seconds": perf_counter() - start})
    return out


if __name__ == "__main__":
    paths = [Path(__file__), Path("tests/test_symmetry.py")]
    print(json.dumps({"schema_version": 1, "kind": "scale", "provenance": provenance(),
                      "fixture_sha256": {p.as_posix(): hashlib.sha256(p.read_text(encoding="utf-8").encode()).hexdigest() for p in paths},
                      "fixed": commons.FIXED, "fixed_reasons": commons.FIXED_REASONS,
                      "settings": {"cases": CASES, "target": "collapsed", "symmetry": "users exchangeable (commons.types)",
                                   "confiscation_to": "stock", "restraint": True},
                      "results": study()}, indent=2, sort_keys=True, allow_nan=False))
