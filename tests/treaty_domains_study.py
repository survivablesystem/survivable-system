"""T3.3 hidden choice: two capability domains. Run as python -m tests.treaty_domains_study."""
import hashlib
import json
from pathlib import Path
import random
from time import perf_counter

from engine.power import PowerLimitExceeded, sure
from engine.records import provenance
from engine.sweep import sample_params
from tests.treaty_study import paired
from worlds import treaty

BUDGETS = (("free", 2), ("scarce", 2))
ADVANTAGE = (1.5, 2.0, 3.0)
LEADS = (0, 1, 2)
RETURNS = (0.0, 0.25)
T_VALUES = (1, 2, 4, 6, 8)
SAMPLES = 120
SAMPLE_SEED = 3033


def power_grid():
    out = []
    for domains in (1, 2):
        for budget, reserve in BUDGETS:
            for adv in ADVANTAGE:
                for lead in LEADS:
                    for ret in RETURNS:
                        for T in T_VALUES:
                            params = {**treaty.DEFAULTS, "domains": domains, "contest": "threshold", "budget": budget,
                                      "reserve": reserve, "advantage": adv, "lead": lead, "returns": ret}
                            verified = treaty.make(params, random.Random(0))
                            blind = treaty.make({**params, "verification": "none"}, random.Random(0))
                            s = verified.initial_state()
                            cell = {"domains": domains, "budget": budget, "reserve": reserve, "advantage": adv,
                                    "lead": lead, "returns": ret, "T": T}
                            start = perf_counter()
                            for name, w, informed in (("blind", blind, False), ("verified", verified, False),
                                                      ("informed", verified, True)):
                                try:
                                    cell[f"sure_prevent_b_{name}"] = sure(w, s, ["b"], T, "b_disarmed", informed=informed)
                                except PowerLimitExceeded:
                                    cell[f"sure_prevent_b_{name}"] = None
                            cell["elapsed_seconds"] = perf_counter() - start
                            out.append(cell)
    return out


def behavior():
    rng = random.Random(SAMPLE_SEED)
    space = {k: v for k, v in treaty.SPACE.items() if k not in ("verification", "domains")}
    rows = []
    for _ in range(SAMPLES):
        params = {**sample_params(space, rng), "domains": 2}
        seed = rng.getrandbits(32)
        rows.append({"params": params, "seed": seed, **paired(params, seed)})
    return rows


if __name__ == "__main__":
    paths = [Path(__file__), Path("tests/treaty_study.py"), Path("tests/test_treaty.py")]
    print(json.dumps({"schema_version": 1, "kind": "treaty-domains", "provenance": provenance(),
                      "fixture_sha256": {p.as_posix(): hashlib.sha256(p.read_text(encoding="utf-8").encode()).hexdigest() for p in paths},
                      "fixed": treaty.FIXED, "fixed_reasons": treaty.FIXED_REASONS,
                      "settings": {"budgets": BUDGETS, "advantage": ADVANTAGE, "leads": LEADS, "returns": RETURNS,
                                   "T": T_VALUES, "contest": "threshold", "samples": SAMPLES, "sample_seed": SAMPLE_SEED,
                                   "behavior": "domains=2; rest of the register sampled; verification none and exact paired by parameters and seed."},
                      "results": {"power": power_grid(), "behavior": behavior()}},
                     indent=2, sort_keys=True, allow_nan=False))
