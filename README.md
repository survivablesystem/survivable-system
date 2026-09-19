# Survivable System

A research prototype for comparing institutions under explicit assumptions, with the long-term aim of reducing civilizational risk. Agents choose actions from goals and beliefs. The tool asks who bears costs, who can force irreversible outcomes, and who can correct errors.

Implemented: one commons world, a limited planner, finite simulations and parameter sweeps. Coalition queries, nested institutions and a civilizational protocol are not implemented or validated. The historical briefs are hypotheses awaiting source and counterexample review.

Read [`INTENT.md`](INTENT.md) first. It is the measure for every change.

## Quick start

Requires Python 3.10 or newer; CI tests Python 3.12 on Windows and Linux. The engine uses only the standard library; pytest is a development dependency.

```sh
python -m pip install -r requirements.txt
python -m pytest -q
python -m engine worlds.commons --trace --rounds 10 --fix n=4 horizon=1
```

On Windows, use `py` instead of `python` if that is how your installation is exposed. A short horizon makes this first example fast.

```sh
python -m engine worlds.commons --oat --rounds 30
python -m engine worlds.commons --samples 20 --rounds 30 --seed 42 --json > run.json
python -m engine worlds.commons --oat --seeds 4 --fix n=4 --json > oat.json
python -m engine worlds.commons --trace --rounds 30 --seed 7 --json > trace.json
```

The full one-at-a-time run can take several minutes. It starts from a favorable baseline and varies categorical values or numeric endpoints. `--fix` holds a parameter fixed throughout every mode. Overrides must belong to the declared register; unknown names and invalid values fail early. `--trace` and `--oat` are mutually exclusive.

## Reproducing a result

All modes support `--json` (schema version 1). Artifacts contain the world, source hashes, Git revision and dirty status, Python version, register, fixed assumptions with reasons, settings and raw runs. Each run includes parameters, an integer seed, requested/executed rounds, terminal status and final state; trace mode also records actions and states. Keep the artifact with the matching source revision. A dirty revision cannot be recovered from the commit alone; hashes identify it but do not archive it.

To replay a saved sweep record using the matching source:

```python
import importlib, json
from engine.records import run_record

with open("run.json", encoding="utf-8-sig") as f:
    evidence = json.load(f)
world = importlib.import_module(evidence["world"])
saved = evidence["results"][0]
replayed = run_record(world.make, saved["params"], saved["rounds_requested"], saved["seed"])
assert json.loads(json.dumps(replayed)) == saved
```

For one-at-a-time artifacts the records are inside each result's `runs` list; trace replay also needs `include_trace=True`. Source hashes cover local engine/world code, spec and intent, with line endings normalized. External data and dependencies require separate provenance. The old JSON `rows` pairs are replaced by versioned records.

## Layout

| Path | What |
|---|---|
| `INTENT.md` | Why this exists and the six tests every change must pass |
| `AGENTS.md` | How to work here, for people and AI agents |
| `TASKS.md` | Ordered build plan with acceptance lines. Claim, build, mark done |
| `LOG.md` | One entry per session. Append-only |
| `DECISIONS.md` | Core changes and why they passed the tests |
| `spec/PRIMITIVES.md` | The model: one object, the agent, at every scale |
| `engine/` | Planner, run loop, sweeps, CLI. Stdlib only |
| `worlds/` | One file per world: the assumptions register and the dynamics |
| `tests/` | Implementation, reproducibility and scoped outcome regressions |
| `rediscovery/` | Paper hypotheses, counterexamples and engine findings |

## What a result means

A `survived` label means only that the run did not collapse before its time limit. `terminal: null` means no absorbing outcome was detected. These are not attractors or probabilities of real-world survival. `sustained` was the earlier, overstated label.

Random sweeps sample parameter values independently and uniformly within the declared register. Outcome shares change when that register or sampling rule changes. Dependence tables show marginal associations; one-at-a-time endpoints miss interactions. Neither establishes global robustness.

Each world explicitly supplies the agent's hypothetical planning state from permitted information and point priors. Action menus and rollouts use that state; actual execution uses truth. Level-1 responses follow directed observation, so an observer can react even when the actor cannot see it. World methods must respect this information contract; they are not sandboxed.

The planner still compares repeating each available action and uses expected transitions. The audit demonstrates rejected profitable action sequences, reversed rankings at irreversible thresholds, and order-dependent ties. Goals, priors, known-model assumptions and action semantics remain authored. A green suite establishes the tested behavior, not a validated model of civilization.

Run the small diagnostics, including candidate action values and exact reference calculations:

```sh
python -m tests.planner_cases
```

See [`rediscovery/planner-audit.md`](rediscovery/planner-audit.md). `engine.core.action_values` exposes the same candidate values used by the planner. New worlds must implement `belief_state(state, agent)`; there is no silent full-information default.

## Next evidence gates

Replace the planner/transition approximation coherently using the audit's exact small cases, then investigate sparse channels without prescribing the result and compare auditor arrangements with matched assumptions. Separate design choices from uncertain conditions before ranking institutions. A real use case must identify affected groups, rival explanations and a decision someone can actually change. See [`TASKS.md`](TASKS.md).

The purpose and evidence standards are durable; the model and implementation are replaceable. Expand or rebuild when demonstrated limitations justify it, retiring obsolete mechanisms instead of accumulating exceptions. Generality must be shown across cases.

Any eventual protocol must specify adoption, enforcement, challenge, amendment and exit, and survive reversible trials. This repository currently supports investigation, not a claim that such a protocol works.

## License

MIT.
