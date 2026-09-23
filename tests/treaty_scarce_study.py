"""T3.2 scarce responses and ratio-raising returns. Run as python -m tests.treaty_scarce_study."""
import hashlib
import json
from pathlib import Path
import random

from engine.power import PowerLimitExceeded, force, sure
from engine.records import provenance
from engine.sweep import sample_params
from tests.treaty_study import paired
from worlds import treaty

BUDGETS = (("free", 2), ("scarce", 0), ("scarce", 1), ("scarce", 2), ("scarce", 3))
ELASTICITY = (1.0, 1.5, 2.0)
RETURNS = (0.25, 0.5)
ADVANTAGE = (1.5, 2.0, 3.0)
LEADS = (0, 1, 2, 3)
T_VALUES = (1, 2, 4, 6, 8)
SAMPLES = 120
SAMPLE_SEED = 3032


def power_grid():
    out = []
    for budget, reserve in BUDGETS:
        for el in ELASTICITY:
            for ret in RETURNS:
                for adv in ADVANTAGE:
                    for lead in LEADS:
                        for T in T_VALUES:
                            params = {**treaty.DEFAULTS, "contest": "threshold", "budget": budget, "reserve": reserve,
                                      "elasticity": el, "returns": ret, "advantage": adv, "lead": lead}
                            verified = treaty.make(params, random.Random(0))
                            blind = treaty.make({**params, "verification": "none"}, random.Random(0))
                            s = verified.initial_state()
                            cell = {"budget": budget, "reserve": reserve, "elasticity": el, "returns": ret,
                                    "advantage": adv, "lead": lead, "T": T,
                                    "force_a": force(verified, s, ["a"], T, "b_disarmed")}
                            for name, w, informed in (("blind", blind, False), ("verified", verified, False),
                                                      ("informed", verified, True)):
                                try:
                                    cell[f"sure_prevent_b_{name}"] = sure(w, s, ["b"], T, "b_disarmed", informed=informed)
                                except PowerLimitExceeded:
                                    cell[f"sure_prevent_b_{name}"] = None
                            out.append(cell)
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


if __name__ == "__main__":
    paths = [Path(__file__), Path("tests/treaty_study.py"), Path("tests/test_treaty.py")]
    print(json.dumps({"schema_version": 1, "kind": "treaty-scarce", "provenance": provenance(),
                      "fixture_sha256": {p.as_posix(): hashlib.sha256(p.read_text(encoding="utf-8").encode()).hexdigest() for p in paths},
                      "fixed": treaty.FIXED, "fixed_reasons": treaty.FIXED_REASONS,
                      "settings": {"budgets": BUDGETS, "elasticity": ELASTICITY, "returns": RETURNS,
                                   "advantage": ADVANTAGE, "leads": LEADS, "T": T_VALUES, "contest": "threshold",
                                   "samples": SAMPLES, "sample_seed": SAMPLE_SEED,
                                   "behavior": "Full register sampled; verification none and exact paired by parameters and seed."},
                      "results": {"power": power_grid(), "behavior": behavior()}},
                     indent=2, sort_keys=True, allow_nan=False))
