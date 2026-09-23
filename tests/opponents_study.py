"""A1: behavioral findings under both level-1 opponent models. Run as python -m tests.opponents_study."""
import hashlib
import json
from pathlib import Path
import random

from engine.records import provenance, run_record
from engine.sweep import sample_params
from tests.treaty_study import summary
from worlds import commons, treaty

MODELS = ("react", "plan")
COMMONS = {"baseline": {}, "unpaid": {"confiscation_to": "stock"}, "no sanction": {"sanction": False},
           "no channels": {"channels": "none"}, "n 2": {"n": 2}, "depth 3": {"search_depth": 3},
           "r 0.3": {"r": 0.3}, "no restraint": {"restraint": False}}
SAMPLES = 120
SAMPLE_SEED = 3031  # the T3.1 sample, so the react column reproduces T3.1


def commons_runs():
    out = []
    for name, over in COMMONS.items():
        for model in MODELS:
            record = run_record(commons.make, {**commons.DEFAULTS, **over, "others": model}, 30, 0)
            out.append({"name": name, "others": model, "status": record["status"],
                        "label": record["label"], "rounds_run": record["rounds_run"]})
    return out


def treaty_pairs():
    rng = random.Random(SAMPLE_SEED)
    later = {"elasticity": 1.0, "budget": "free", "reserve": 2, "domains": 1}
    space = {k: v for k, v in treaty.SPACE.items() if k not in ("verification", "others", *later)}
    rows = []
    for _ in range(SAMPLES):
        params = {**sample_params(space, rng), **later}
        seed = rng.getrandbits(32)
        row = {"params": params, "seed": seed}
        for model in MODELS:
            for verification in ("none", "exact"):
                record = run_record(treaty.make, {**params, "others": model, "verification": verification},
                                    12, seed, include_trace=True)
                row[f"{model}/{verification}"] = summary(record)
        rows.append(row)
    return rows


if __name__ == "__main__":
    paths = [Path(__file__), Path("tests/treaty_study.py")]
    print(json.dumps({"schema_version": 1, "kind": "opponent-models", "provenance": provenance(),
                      "fixture_sha256": {p.as_posix(): hashlib.sha256(p.read_text(encoding="utf-8").encode()).hexdigest() for p in paths},
                      "settings": {"models": MODELS, "commons": COMMONS, "samples": SAMPLES, "sample_seed": SAMPLE_SEED,
                                   "treaty": "T3.1 register (later keys pinned); four runs per sample: model x verification, same seed."},
                      "results": {"commons": commons_runs(), "treaty": treaty_pairs()}},
                     indent=2, sort_keys=True, allow_nan=False))
