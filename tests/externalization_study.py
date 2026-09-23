"""E1 externalization reports for both worlds. Run as python -m tests.externalization_study."""
import hashlib
import json
from pathlib import Path
import random

from engine.power import externalization
from engine.records import provenance
from worlds import commons, treaty

COMMONS = [({"n": 3}, S) for S in (8.0, 20.0, 30.0, 50.0)] + [({"n": 3, "restraint": False}, S) for S in (20.0, 30.0)]
TREATY = [{"lead": lead, "domains": d, "verification": v} for lead in (0, 2) for d in (1, 2) for v in ("none", "exact")]
ROUNDS = 3


def study():
    out = {"commons": [], "treaty": []}
    for over, S in COMMONS:
        w = commons.make({**commons.DEFAULTS, **over}, random.Random(0))
        out["commons"].append({"params": over, "S": S,
                               "report": externalization(w, commons, {**w.initial_state(), "S": S}, ROUNDS)})
    for over in TREATY:
        w = treaty.make({**treaty.DEFAULTS, **over}, random.Random(0))
        out["treaty"].append({"params": over, "report": externalization(w, treaty, w.initial_state(), ROUNDS)})
    return out


if __name__ == "__main__":
    paths = [Path(__file__)]
    print(json.dumps({"schema_version": 1, "kind": "externalization", "provenance": provenance(),
                      "fixture_sha256": {p.as_posix(): hashlib.sha256(p.read_text(encoding="utf-8").encode()).hexdigest() for p in paths},
                      "settings": {"rounds": ROUNDS, "p": 1.0},
                      "declarations": {m.__name__: {"stakeholders": m.STAKEHOLDERS, "harms": m.HARMS, "excluded": m.EXCLUDED}
                                       for m in (commons, treaty)},
                      "results": study()}, indent=2, sort_keys=True, allow_nan=False))
