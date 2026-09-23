"""T3.1 treaty: power grid and verification-paired behavior. Run as python -m tests.treaty_study."""
import hashlib
import json
from pathlib import Path
import random
from time import perf_counter

from engine.core import action_values
from engine.power import PowerLimitExceeded, force, sure
from engine.records import provenance, run_record
from engine.sweep import sample_params
from worlds import treaty

ROUNDS = 12
SAMPLES = 120
SAMPLE_SEED = 3031
POWER_T = (2, 4, 6)
ADVANTAGE = (1.5, 2.0, 3.0)
RETURNS = (0.0, 0.25, 0.5)
LEADS = (0, 1, 2, 3)


def world(**overrides):
    return treaty.make({**treaty.DEFAULTS, **overrides}, random.Random(0))


def power_grid():
    out = []
    for contest in ("threshold", "ratio"):
        for adv in ADVANTAGE:
            for ret in RETURNS:
                for lead in LEADS:
                    for T in POWER_T:
                        cell = {"contest": contest, "advantage": adv, "returns": ret, "lead": lead, "T": T}
                        verified = world(contest=contest, advantage=adv, returns=ret, lead=lead)
                        blind = world(contest=contest, advantage=adv, returns=ret, lead=lead, verification="none")
                        s = verified.initial_state()
                        cell["force_a"] = {o: force(verified, s, ["a"], T, "b_disarmed", o) for o in ("alpha", "beta")}
                        for name, w, informed in (("blind", blind, False), ("verified", verified, False),
                                                  ("informed", verified, True)):
                            try:
                                cell[f"sure_prevent_b_{name}"] = sure(w, s, ["b"], T, "b_disarmed", informed=informed)
                            except PowerLimitExceeded:
                                cell[f"sure_prevent_b_{name}"] = None
                        out.append(cell)
    return out


def summary(record):
    trace = record["trace"]
    return {"status": record["status"], "label": record["label"], "rounds_run": record["rounds_run"],
            "builds": {i: sum(e["actions"][i] == treaty.BUILD for e in trace) for i in ("a", "b")},
            "strikes": {i: sum(e["actions"][i] == treaty.STRIKE for e in trace) for i in ("a", "b")},
            "first_build": next((e["round"] for e in trace if treaty.BUILD in e["actions"].values()), None)}


def paired(params, seed):
    out = {}
    for verification in ("none", "exact"):
        start = perf_counter()
        record = run_record(treaty.make, {**params, "verification": verification}, ROUNDS, seed, include_trace=True)
        out[verification] = {**summary(record), "elapsed_seconds": perf_counter() - start}
    return out


def behavior():
    rng = random.Random(SAMPLE_SEED)
    space = {k: v for k, v in treaty.SPACE.items() if k != "verification"}
    rows = []
    for _ in range(SAMPLES):
        params = sample_params(space, rng)
        seed = rng.getrandbits(32)
        rows.append({"params": params, "seed": seed, **paired(params, seed)})
    return rows


def defaults():
    out = []
    for opening in ("hold", "build"):
        for verification in ("none", "exact"):
            params = {**treaty.DEFAULTS, "opening": opening, "verification": verification}
            w = treaty.make(params, random.Random(0))
            probes = {a.id: action_values(w, w.initial_state(), a) for a in w.agents}
            out.append({"params": params, "record": run_record(treaty.make, params, ROUNDS, 0, include_trace=True),
                        "round1_values": probes})
    return out


if __name__ == "__main__":
    paths = [Path(__file__), Path("tests/test_treaty.py")]
    print(json.dumps({"schema_version": 1, "kind": "treaty", "provenance": provenance(),
                      "fixture_sha256": {p.as_posix(): hashlib.sha256(p.read_text(encoding="utf-8").encode()).hexdigest() for p in paths},
                      "fixed": treaty.FIXED, "fixed_reasons": treaty.FIXED_REASONS,
                      "settings": {"rounds": ROUNDS, "samples": SAMPLES, "sample_seed": SAMPLE_SEED,
                                   "power_T": POWER_T, "advantage": ADVANTAGE, "returns": RETURNS, "leads": LEADS,
                                   "pairing": "Same parameters and seed with verification none and exact."},
                      "results": {"power": power_grid(), "defaults": defaults(), "behavior": behavior()}},
                     indent=2, sort_keys=True, allow_nan=False))
