# Survivable System

A research prototype for comparing institutions under explicit assumptions, with the long-term aim of reducing civilizational risk. Agents choose actions from goals and beliefs. The tool asks who bears costs, who can force irreversible outcomes, and who can correct errors.

Implemented: six worlds (a commons, a treaty and capability race, authority and coercion, an auditor paid by the audited, frontier AI labs with an evaluator and a state, an AI system as an agent of its lab) and a composite of two, a limited planner, finite simulations, parameter sweeps and goal-free coalition power queries: force, prevent, externalization, correction and lock (who can make a harm permanent for everyone else), and goal-based checks of declared rules: does a rule hold, and which coalitions gain by breaking it onto others (capture). Nested institutions, amendment rules and a civilizational protocol are not implemented or validated. The historical briefs are hypotheses awaiting source and counterexample review.

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

The full one-at-a-time run can take several minutes. It starts from the declared baseline and varies categorical values or numeric endpoints. `--fix` holds a parameter fixed throughout every mode. Overrides must belong to the register; unknown names and invalid values fail early. `--trace` and `--oat` are mutually exclusive. Commons searches depth 2 by default; `--fix search_depth=3` investigates the next depth. Desired horizon and effective search depth are different assumptions, both recorded. There is no estimate of utility beyond the cap.

## Two questions: what agents do, what coalitions could force

The planner answers the first under authored goals. `--power T` answers the second without any goals: for every coalition, the probability it can force a flagged terminal label (for example collapse) within T rounds against everyone else acting together, and the probability it can prevent it. Alpha/beta columns bracket the value by who commits first each round.

```sh
python -m engine worlds.commons --power 3 --fix confiscation_to=stock --target collapsed
python -m engine worlds.treaty --trace --rounds 12 --profile 3
```

`--externalities T` runs the same query per declared harm: who can force it, who can impose it without bearing it, who can prevent or end it, and whom it falls on without any agent in the model. Every world must declare its stakeholders, harms and exclusions ([`rediscovery/externalization.md`](rediscovery/externalization.md)).

Worlds compose into one system (`engine/compose.py`): the same actors act in several parts, declared couplings carry flows between them, and every query runs on the whole. `worlds/race_commons.py` puts an arms race on a shared fishery; the whole shows harms and forced choices that neither part shows ([`rediscovery/race-commons.md`](rediscovery/race-commons.md)).

```sh
python -m engine worlds.race_commons --externalities 2 --state parts.commons.S=30 --fix draw=2.0 treaty.lead=0 treaty.advantage=1.5
```

`--lock K` adds, per harm, the smallest coalition that can force it and then keep it K rounds against everyone. Irreversibility is then computed rather than only declared: a reversible harm that someone can lock is irreversible for everyone else. For a harm already realized the report names who can end it, who can keep it, and who holds a veto on ending it. `worlds/authority.py` (office, coercion, surveillance, purges) is the case where this matters ([`rediscovery/standing-army.md`](rediscovery/standing-army.md)).

```sh
python -m engine worlds.authority --externalities 3 --lock 3 --state extracting=true
```

## One screen

`--assess T [--rule NAME] [--lock K]` puts it together for any world: what can be forced, prevented or locked over each declared harm and on whom it falls (goal-free), then whether the proposed rule holds, who gains by a harmful departure and who captures it (goal-based, including coordinated departures over two rounds), then what the model leaves out.

```sh
python -m engine worlds.frontier --assess 2 --rule licensing --lock 2
```

## Does a rule hold?

Worlds declare candidate `RULES`: conduct each agent could follow, never enforced by the kernel. `--enforce D --rule NAME` asks whether anyone gains by departing (at the start and one step off the path, so empty threats are caught) and which coalitions gain by departing together while a declared harm lands on someone outside them. In the audit world, independence holds against every single agent while the firm and its auditor gain together at investors' expense ([`rediscovery/captured-auditor.md`](rediscovery/captured-auditor.md)).

```sh
python -m engine worlds.audit --enforce 4 --rule independence --reach 2
python -m engine worlds.audit --enforce 4 --rule independence --reach 2 --pay firm>a0   # with a bribe available
```

Four modules apply to any world: side payments (`--pay PAYER>RECIPIENT`, `engine/transfers.py`), public records (`--records K`, `engine/history.py`), amendable rules (`engine/constitution.py`) and delegation with goal drift (`engine/delegation.py`). They never change what can be forced, only which rules can hold. With both, the authority world has a rule that corrects a ruler by restitution instead of deposition; it holds only with public payments, records and decisive contests ([`rediscovery/standing-army.md`](rediscovery/standing-army.md)).

## AI systems as agents

`worlds/control.py`: a lab grants its AI system autonomy; the AI's goal is the lab's, drifted. Each autonomy level granted moves the veto on shutdown toward the AI long before anyone could force escape; an AI aligned to its lab resists a shutdown that costs the lab; once the veto has moved, suspicion turns a futile shutdown into restricting autonomy ([`rediscovery/ai-control.md`](rediscovery/ai-control.md)). Rule checks can hide one agent's goals (`--hidden`): others learn by Bayes from what they see, so which conduct counts as evidence is computed. Improvement reveals a misaligned AI only where a rule punishes it or capability is worth little to the lab: otherwise an aligned AI improves too, and the tell is gone; resistance to shutdown reveals nothing; learning turns a lab's response to an AI it can no longer shut down from granting more autonomy into restricting it; and shutdown with a restart that keeps capability is a ratchet towards the AI's veto.

## First real scenario: frontier AI

`worlds/frontier.py` (scope chosen by the owner): two labs, an evaluator, a state that can halt. The evaluator gives the state exactly the information it lacks, yet licensing at deployment cannot avoid a forced choice between unsafe deployment and blocking safe progress; the rule breaks on stale certification (scale after the pass, deploy on it), not on who pays the evaluator; and the capture that appears is the leading lab with the state against the rival ([`rediscovery/frontier-ai.md`](rediscovery/frontier-ai.md)).

```sh
python -m engine worlds.frontier --enforce 4 --rule licensing --fix oversight=continuous
```

`engine.power.sure` asks the information question: can a coalition guarantee an outcome using only what its members observe? It is how verification, disclosure or any channel can show up as denial rather than only as behavior (see [`rediscovery/treaty-no-verification.md`](rediscovery/treaty-no-verification.md)).

A good outcome that the planner produces but that one agent could still force away rests on goals: it is deterrence, not denial. Power claims do not depend on goals, horizons, beliefs or planner depth, and say nothing beyond T. Exact enumeration is exponential; a work cap marks unresolved entries. See [`rediscovery/coalition-power.md`](rediscovery/coalition-power.md).

## Reproducing a result

All modes support `--json` (schema version 2). Artifacts contain the world, source hashes, Git revision and dirty status, Python version, register, fixed assumptions with reasons, settings and raw runs. Runs record parameters, seed, requested/executed rounds, final state, terminal status, completion status and per-agent planning limits; trace mode also records actions/states. `search_limit` means unresolved, with a null outcome label and only completed rounds retained. Keep artifacts with their matching source revision, including older schema-1 evidence. A dirty revision cannot be recovered from the commit alone; hashes identify it but do not archive it.

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

Random sweeps sample parameter values independently and uniformly within the register. Shares change with the register or sampling rule. Unresolved search-limit runs remain in the denominator and appear separately from physical outcomes. Dependence tables show marginal associations; one-at-a-time endpoints miss interactions. Neither establishes global robustness.

Worlds supply observations, finite subjective beliefs and a stochastic outcome kernel. The planner evaluates changing actions, grouping future branches by observation so choices cannot see hidden truth. Execution samples the same kernel. Level-1 responses follow directed observation; direct observers replan at level 0 within the remaining search depth. This is an opponent model, not an equilibrium solver. World methods must respect the information contract; they are not sandboxed. Belief memory across real rounds must be explicitly modeled.

The replacement resolves the audit's profitable-investment and threshold-risk reversals against exact references. First-listed ties remain, and finite search becomes expensive quickly. A fixed per-decision budget aborts excessive work rather than returning a partly scored choice. Goals, priors, known-model assumptions and action semantics remain authored. A green suite establishes tested behavior, not a validated model of civilization.

Run the small diagnostics, including candidate action values and exact reference calculations:

```sh
python -m tests.planner_cases
```

See [`rediscovery/planner-replacement.md`](rediscovery/planner-replacement.md), including the changed commons conclusions and cost comparison. `engine.core.action_values` exposes the same values used by the planner. New worlds implement `observe`, `beliefs`, `actions` and `outcomes`; no implicit full-information or mean-state path remains. `step` is the shared execution sampler.

Worlds may also provide a proved exact `reward_outcomes` marginal for the final
search step. The default integrates the physical kernel; commons sums expected
contest payoffs directly. Earlier branches and physical play retain full outcomes.
This reduces leaf work without approximating utility or future information. See
[`rediscovery/search-reduction.md`](rediscovery/search-reduction.md) for measured
coverage, full-enumeration comparisons and remaining limits.

## Next evidence gates

The commons now lets users rest (T1.6): with it, collapse is never physically sealed short of the threshold, yet depth-limited agents still collapse the stock. Behavior there turns on the planner's search depth more than on goals (T1.8). Exact leaf reduction extends a scoped eight-user depth-2 case; ten-user searches can still be unresolved. Investigate sparse channels while reporting search failures separately, then compare auditor arrangements with matched assumptions. Larger/deeper claims still require actual coverage. Separate design choices from uncertain conditions before ranking institutions. A real use case must identify affected groups, rival explanations and a decision someone can actually change. See [`TASKS.md`](TASKS.md).

The purpose and evidence standards are durable; the model and implementation are replaceable. Expand or rebuild when demonstrated limitations justify it, retiring obsolete mechanisms instead of accumulating exceptions. Generality must be shown across cases.

Any eventual protocol must specify adoption, enforcement, challenge, amendment and exit, and survive reversible trials. This repository currently supports investigation, not a claim that such a protocol works.

## License

MIT.
