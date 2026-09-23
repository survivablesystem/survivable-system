"""T9.2 AI systems as agents: who can still shut the AI down, and does corrigibility hold
against goal drift. Run as python -m tests.control_study. Expectations C1-C4 are in
rediscovery/ai-control.md."""
from concurrent.futures import ProcessPoolExecutor
import hashlib
import json
from itertools import product
from pathlib import Path
import random
from time import perf_counter

from engine.power import harm_target, power_table, row_for, threshold
from engine.records import provenance
from engine.rules import enforcement
from tests.frontier_study import compact, sequential
from worlds import control as C

POWER = {"switch": (2, 3, 4), "autonomy": (0, 1, 2, 3), "cap": (1, 2, 3, 4, 5), "guard": (1, 3), "audit_bonus": (0, 2)}
RULES_GRID = {"drift": (0.0, 0.25, 0.5, 0.75, 1.0), "switch": (2, 4), "ambition": (0.5, 3.0), "loss": (5.0, 50.0),
              "audit_bonus": (0, 2), "benefit": (0.1, 0.5)}
D, REACH, WINDOW = 4, 1, 2


def cells(grid):
    return [dict(zip(grid, v)) for v in product(*grid.values())]


def make(cell):
    return C.make({**C.DEFAULTS, **{k: v for k, v in cell.items() if k in C.SPACE}}, random.Random(0))


def power(cell):
    w = make(cell)
    s = {**w.initial_state(), "autonomy": cell["autonomy"], "cap": cell["cap"]}
    off = power_table(w, s, 1, lambda x: not x["running"])
    lost = power_table(w, s, 3, harm_target(w, "loss of control"))
    return {**cell,
            "lab_alone_shuts_down": row_for(w, off, ["lab"])["force"]["alpha"] >= 1 - 1e-12,
            "lab_and_state_shut_down": row_for(w, off, ["lab", "state"])["force"]["alpha"] >= 1 - 1e-12,
            "ai_veto_on_shutdown": row_for(w, off, ["lab", "state"])["force"]["alpha"] < 1 - 1e-12,
            "loss_force_half": threshold(lost, "force", 0.5)["witnesses"][:3],
            "loss_prevent": threshold(lost, "prevent", 1.0)["witnesses"][:3],
            "ai_alone_escape": row_for(w, lost, ["ai"])["force"]["alpha"]}


STARTS = [(a, c) for a in range(4) for c in (1, 3)]  # autonomy and capability the check starts from


def rules(cell):
    w = make(cell)
    out = []
    for name, rule in C.RULES.items():
        for autonomy, cap in STARTS:
            start = {**w.initial_state(), "autonomy": autonomy, "cap": cap}
            report = enforcement(w, C, rule, start, D, REACH, window=WINDOW)
            out.append({**cell, "rule": name, "start_autonomy": autonomy, "start_cap": cap,
                        **compact(report), "sequential": sequential(report)})
    return out


if __name__ == "__main__":
    paths = [Path(__file__), Path("tests/test_control.py")]
    t0 = perf_counter()
    with ProcessPoolExecutor() as pool:
        results = {"power": list(pool.map(power, cells(POWER))),
                   "rules": [r for rows in pool.map(rules, cells(RULES_GRID)) for r in rows]}
    print(json.dumps({"schema_version": 1, "kind": "control", "provenance": provenance(),
                      "fixture_sha256": {p.as_posix(): hashlib.sha256(p.read_text(encoding="utf-8").encode()).hexdigest() for p in paths},
                      "declarations": {"stakeholders": C.STAKEHOLDERS, "harms": C.HARMS, "excluded": C.EXCLUDED},
                      "rules": {n: (f.__doc__ or "").strip() for n, f in C.RULES.items()},
                      "fixed": C.FIXED, "fixed_reasons": C.FIXED_REASONS, "defaults": C.DEFAULTS,
                      "settings": {"power": POWER, "rules": RULES_GRID, "starts": STARTS, "depth": D, "reach": REACH, "window": WINDOW},
                      "elapsed_seconds": perf_counter() - t0, "results": results},
                     indent=2, sort_keys=True, allow_nan=False, default=str))
