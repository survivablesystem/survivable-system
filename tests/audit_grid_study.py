"""E16: the audit rule findings (E7) across the parameters their study held at defaults.
Case: rediscovery/captured-auditor.md. Run as python -m tests.audit_grid_study."""
import hashlib
import json
from pathlib import Path
from time import perf_counter

from engine.grid import Setup, cells, compare, parse_grid, run, summarize
from engine.records import provenance
from worlds import audit

ORIGINAL = ["state.weak=true", "exposure=0.0,0.2,0.5,1.0", "regulator=none,revokes", "assignment=firm,fixed",
            "premium=0.0,1.0,2.0", "auditors=1,2"]  # evidence/rules.json, depth 4, reach 2
HELD = ["penalty=0.5,3.0", "fee=0.5,2.0", "credibility=1,3", "weak=0.1,0.5", "harm=0.5,3.0"]  # were DEFAULTS
QUERY = {"mode": "enforce", "rounds": 4, "rule": "independence", "reach": 2, "size": 2, "window": 1}


def grid_run(items):
    grid = parse_grid(items, audit.SPACE)
    results = run(Setup("worlds.audit"), QUERY, cells(audit, {}, grid))
    return {"grid": grid,
            "cells": [{"grid": r["grid"], "measures": r["measures"]} for r in results],
            "summary": summarize(results, audit),
            "compare": {k: compare(results, k) for k in ("assignment", "premium", "credibility")
                        if k in grid and len(grid[k]) > 1}}


if __name__ == "__main__":
    t0 = perf_counter()
    out = {"original": grid_run(ORIGINAL), "held": grid_run(ORIGINAL + HELD)}
    files = [Path(__file__), Path("engine/grid.py"), Path("worlds/audit.py"), Path("engine/rules.py")]
    print(json.dumps({"schema_version": 1, "kind": "audit-grid", "provenance": provenance(),
                      "fixture_sha256": {p.as_posix(): hashlib.sha256(p.read_text(encoding="utf-8").encode()).hexdigest() for p in files},
                      "settings": {"query": QUERY, "defaults": audit.DEFAULTS, "original": ORIGINAL, "held": HELD},
                      "elapsed_seconds": perf_counter() - t0, "results": out}, indent=1, sort_keys=True, allow_nan=False))
