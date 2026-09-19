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
