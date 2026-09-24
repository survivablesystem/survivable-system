"""A2: coup-proofing across a contest family between ratio and threshold.
Case: rediscovery/standing-army.md (contest family). Run as python -m tests.contest_study."""
from concurrent.futures import ProcessPoolExecutor
import hashlib
import json
from itertools import product
from pathlib import Path
import random
from time import perf_counter

from engine.power import harm_target, power_table, vetoes
from engine.records import provenance
from worlds import authority as A

K = 3           # rounds to end extraction
P = 0.5         # level: the threshold contest decides here as at certainty
CELLS = {"army": (2, 4), "guard": (1, 2), "gain": (1, 2), "surveillance": ("army", "all")}
FORMS = [{"contest": "tullock", "decisiveness": m, "advantage": adv} for adv in (1.0, 1.5)
         for m in (1.0, 2.0, 4.0, 16.0, 64.0, 1024.0)] + [{"contest": "threshold", "decisiveness": 4.0, "advantage": 1.5}]
# m = 1024 decides as the threshold contest except at exact ties (probability one half, not one):
# added after the first run showed no switch up to m = 16 (rediscovery/standing-army.md).


def veto(args):
    cell, form, commands = args
    world = A.make({**A.DEFAULTS, "citizens": 2, **cell, **form, "commands": commands}, random.Random(0))
    harm = harm_target(world, "extraction")
    start = perf_counter()
    ended = power_table(world, {**world.initial_state(), "extracting": True}, K, lambda s: not harm(s))
    return {**cell, **form, "commands": commands, "veto": vetoes(world, ended, P),
            "elapsed_seconds": perf_counter() - start}


if __name__ == "__main__":
    t0 = perf_counter()
    jobs = [(dict(zip(CELLS, v)), form, c) for v in product(*CELLS.values()) for form in FORMS for c in (1, 2)]
    with ProcessPoolExecutor() as pool:
        rows = list(pool.map(veto, jobs))
    paths = [Path(__file__), Path("worlds/authority.py")]
    print(json.dumps({"schema_version": 1, "kind": "contest", "provenance": provenance(),
                      "fixture_sha256": {p.as_posix(): hashlib.sha256(p.read_text(encoding="utf-8").encode()).hexdigest() for p in paths},
                      "settings": {"K": K, "p": P, "cells": CELLS, "forms": FORMS, "citizens": 2},
                      "elapsed_seconds": perf_counter() - t0, "results": rows},
                     indent=2, sort_keys=True, allow_nan=False))
