# Saved evidence

`commons-collapse.json` is a trace from clean source commit `f26e7f93bc44ccb953caacce0e27f39c1f2286de`. It uses the commons defaults with horizon 1, sanction capability off, seed 0 and a 30-round limit. Collapse occurs at round five. The first round alone would be labeled `survived`; neither finite result establishes an attractor.

Generate a fresh artifact from the matching source:

```sh
python -m engine worlds.commons --trace --rounds 30 --seed 0 --fix horizon=1 sanction=false --json
```

Replay the saved trajectory from the repository root:

```python
import json
from engine.records import run_record
from worlds import commons

with open("evidence/commons-collapse.json", encoding="utf-8") as f:
    evidence = json.load(f)
saved = evidence["results"][0]
actual = run_record(commons.make, saved["params"], saved["rounds_requested"],
                    saved["seed"], include_trace=True)
assert json.loads(json.dumps(actual)) == saved
```

The artifact preserves per-user wealth, actions and stock at each round, fixed assumptions with reasons, the register, source hashes and planner limitations. This is a reporting counterexample, not empirical evidence about real commons. Historical table claims still need separate evidence review.

## Planner audit

`planner-audit-before.json` comes from clean commit `ab6b02a8a578649ce7ce4c78d24c45218369cad0`; `planner-audit-after.json` comes from clean commit `7e9bba06720218d9ce4b9a06e525417b4cc59e82`. In each checkout, reproduce with:

```sh
python -m tests.planner_cases
```

Each artifact stores source provenance, the diagnostic fixture hash, fixed constants, candidate values, chosen actions and exact arithmetic references. The information repairs change the one-way-response and hidden-bit results. Tie ordering, the investment sequence gap and the threshold-risk reversal remain unchanged; they justify the next planner replacement. See `rediscovery/planner-audit.md` for scope and `tests/test_planner_audit.py` for the contracts.

Replaying an artifact means using its recorded source revision. Later, better planners are expected to change outcomes; preserve old evidence instead of silently rewriting it.
