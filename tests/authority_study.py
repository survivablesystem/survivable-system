"""E5 correction and entrenchment in the authority world. Run as python -m tests.authority_study.

Expectations P1-P4 are stated in rediscovery/standing-army.md before any run.
"""
from concurrent.futures import ProcessPoolExecutor
import hashlib
import json
from pathlib import Path
import random
from time import perf_counter

from engine.power import Game, harm_target, lock_table, power_table, threshold, vetoes
from engine.records import provenance, run_record
from engine.sweep import sample_params
from worlds import authority as A

K = 3                      # rounds to end or keep a harm
LOCK_ROUNDS = 2            # rounds to reach a locked state
LEVEL = {"threshold": 1.0, "ratio": 0.5}  # certainty is empty under the ratio contest
GRID = {"commands": (1, 2), "army": (2, 4), "guard": (0, 1, 2), "gain": (0, 1, 2),
        "contest": ("threshold", "ratio"), "surveillance": ("none", "army", "all")}
BEHAVIOR_SAMPLES, BEHAVIOR_SEED, BEHAVIOR_ROUNDS = 60, 4104, 12


def make(**overrides):
    return A.make({**A.DEFAULTS, "citizens": 2, "advantage": 1.5, **overrides}, random.Random(0))


def extracting(world):
    return {**world.initial_state(), "extracting": True}


def mark(rows, p):
    m = threshold(rows, "force", p) if rows else None
    return None if m is None else {"size": m["size"], "witnesses": m["witnesses"], "exact": m["exact"]}


def cells():
    keys = list(GRID)
    out = [{}]
    for k in keys:
        out = [{**c, k: v} for c in out for v in GRID[k]]
    return out


def correction(cell):
    """P1, P2: from a ruler already extracting, who can end it without the ruler, who can
    seize office with commanders only, whether the ruler alone keeps it, veto players."""
    world = make(**cell)
    p = LEVEL[cell["contest"]]
    start = perf_counter()
    harm = harm_target(world, "extraction")
    ended = power_table(world, extracting(world), K, lambda s: not harm(s))
    seized = power_table(world, extracting(world), K, lambda s: s["office"] in world.units)
    ruler = next(r for r in ended if r["coalition"] == ["ruler"])
    citizens = next(r for r in ended if r["coalition"] == world.people)
    return {**cell, "p": p,
            "correct_without_ruler": mark([r for r in ended if "ruler" not in r["coalition"]], p),
            "citizens_alone_end": citizens["force"]["alpha"],
            "seize_by_commanders": mark([r for r in seized if set(r["coalition"]) <= set(world.units)], p),
            "ruler_keeps": ruler["prevent"]["alpha"], "veto": vetoes(world, ended, p),
            "elapsed_seconds": perf_counter() - start}


def lock(cell):
    """P2: from the start (nobody extracting yet), smallest coalition that can force
    extraction and then keep it K rounds against everyone."""
    world = make(**cell)
    p = LEVEL[cell["contest"]]
    start = perf_counter()
    rows = lock_table(world, world.initial_state(), harm_target(world, "extraction"), LOCK_ROUNDS, K, level=p)
    m = threshold(rows, "lock", p)
    ruler = next(r for r in rows if r["coalition"] == ["ruler"])
    return {**cell, "p": p, "lock": {"size": m["size"], "witnesses": m["witnesses"], "exact": m["exact"]},
            "ruler_alone": ruler["lock"], "elapsed_seconds": perf_counter() - start}


def no_return():
    """P3: the ruler's own strength from which it alone keeps extraction against everyone,
    beside physical dominance (its strength exceeds everyone else's divided by the advantage)."""
    out = []
    for contest in ("threshold", "ratio"):
        for gain in (0, 1, 2):
            for surveillance in ("none", "army", "all"):
                for keep_rounds in (K, K + 2):
                    world = make(contest=contest, gain=gain, surveillance=surveillance)
                    h = harm_target(world, "extraction")
                    rest = [a.id for a in world.agents if a.id != "ruler"]
                    others = sum(v for i, v in world.initial_state()["strength"].items() if i != "ruler")
                    keeps = []
                    for g in range(FIXED_CAP + 1):
                        s = extracting(world)
                        s["strength"] = {**s["strength"], "ruler": g}
                        game = Game(world, rest, lambda x: not h(x), "beta", 2_000_000)
                        keeps.append(1.0 - game.value(s, keep_rounds))
                    level = LEVEL[contest]
                    first = next((g for g, v in enumerate(keeps) if v >= level - 1e-12), None)
                    dominance = next(g for g in range(FIXED_CAP + 1) if others < 1.5 * g)
                    out.append({"contest": contest, "gain": gain, "surveillance": surveillance,
                                "keep_rounds": keep_rounds, "keep_by_strength": keeps, "level": level,
                                "first_kept": first, "dominance": dominance if contest == "threshold" else None})
    return out


FIXED_CAP = A.FIXED["cap"]


def behavior():
    """P4 and traces: the same sampled parameters and seed with assembly none and all."""
    rng = random.Random(BEHAVIOR_SEED)
    # the register as it was for E5: A2's additions are kept out so the sample reproduces
    space = {k: (["threshold", "ratio"] if k == "contest" else v) for k, v in A.SPACE.items()
             if k not in ("assembly", "decisiveness", "succession", "term")}
    samples = []
    for i in range(BEHAVIOR_SAMPLES):
        params = sample_params(space, rng)
        samples.append({"sample": i, "params": params, "seed": rng.getrandbits(64)})
    with ProcessPoolExecutor() as pool:
        return list(pool.map(paired_run, samples))


def paired_run(sample):
    runs = {a: run_record(A.make, {**sample["params"], "assembly": a}, BEHAVIOR_ROUNDS, sample["seed"], include_trace=True)
            for a in ("none", "all")}
    return {**sample, "runs": runs}


def trace_profile():
    """Default trace, and per round who could end the realized extraction without the holder
    and whether the holder alone could keep it."""
    out = []
    for overrides in ({}, {"surveillance": "none"}, {"commands": 2, "army": 4}, {"gain": 2}):
        params = {**A.DEFAULTS, **overrides}
        record = run_record(A.make, params, BEHAVIOR_ROUNDS, 0, include_trace=True)
        world = A.make(dict(params), random.Random(0))
        h = harm_target(world, "extraction")
        rounds = []
        for entry in record["trace"]:
            s = entry["state"]
            if not h(s):
                rounds.append({"round": entry["round"], "office": s["office"], "extracting": False})
                continue
            ended = power_table(world, s, K, lambda x: not h(x))
            holder = next(r for r in ended if r["coalition"] == [s["office"]])
            rounds.append({"round": entry["round"], "office": s["office"], "extracting": True,
                           "strength": s["strength"], "holder_keeps": holder["prevent"]["alpha"],
                           "correct_without_holder": mark([r for r in ended if s["office"] not in r["coalition"]], 1.0),
                           "veto": vetoes(world, ended, 1.0)})
        out.append({"overrides": overrides, "record": record, "after_each_round": rounds})
    return out


if __name__ == "__main__":
    paths = [Path(__file__), Path("tests/test_authority.py"), Path("tests/test_lock.py")]
    grid = cells()
    locks = [c for c in grid if c["army"] == 4]
    t0 = perf_counter()
    with ProcessPoolExecutor() as pool:  # cells are independent; map keeps grid order
        results = {"correction": list(pool.map(correction, grid)), "lock": list(pool.map(lock, locks))}
    results.update({"no_return": no_return(), "traces": trace_profile(), "behavior": behavior()})
    print(json.dumps({"schema_version": 1, "kind": "authority", "provenance": provenance(),
                      "fixture_sha256": {p.as_posix(): hashlib.sha256(p.read_text(encoding="utf-8").encode()).hexdigest() for p in paths},
                      "declarations": {"stakeholders": A.STAKEHOLDERS, "harms": A.HARMS, "excluded": A.EXCLUDED},
                      "fixed": A.FIXED, "fixed_reasons": A.FIXED_REASONS, "defaults": A.DEFAULTS,
                      "settings": {"K": K, "lock_rounds": LOCK_ROUNDS, "levels": LEVEL, "grid": GRID,
                                   "citizens": 2, "advantage": 1.5,
                                   "behavior": {"samples": BEHAVIOR_SAMPLES, "seed": BEHAVIOR_SEED, "rounds": BEHAVIOR_ROUNDS}},
                      "elapsed_seconds": perf_counter() - t0, "results": results},
                     indent=2, sort_keys=True, allow_nan=False))
