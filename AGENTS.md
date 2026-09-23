# Working here (Fable, Astra, anyone)

Read `INTENT.md` first, every session. Then `TASKS.md` and the last three entries of `LOG.md`.

## Order of authority

1. `INTENT.md`: why, and the tests every change must pass.
2. `spec/PRIMITIVES.md`: the model.
3. `engine/`: implements the spec. Never extends it silently.
4. `worlds/`, `tests/`, `rediscovery/`: the library and its evidence.
5. `DECISIONS.md`, `TASKS.md`, `LOG.md`: record, plan, history.

A lower layer never changes the meaning of a higher one. A world that needs something the spec cannot express is a proposal against the spec, not a workaround in the world.

The implementation and current model are replaceable. When a limitation matters, compare extending with rebuilding; choose the simplest architecture that addresses the demonstrated cases. Preserve the intent and revisioned evidence, not obsolete internals. Record the decision before changing core code, migrate tests deliberately, and remove superseded mechanisms instead of layering exceptions. Owner authorization for this evolution is standing; ASK items still apply to changes in values or real-world scenario scope, not routine architecture choices.

## The session loop

1. Read the three files above. Run `python -m pytest -q`. If red, fixing it is the task.
2. Take the first unclaimed task in `TASKS.md` whose dependencies are done. Claim it by writing your name and the date on its line.
3. Before building, write down the simplest thing that could satisfy the acceptance line and the result that would contradict the hypothesis. Build that. A negative result can complete a research task.
4. Core changes get a `DECISIONS.md` entry before the code.
5. Green tests. Update the task line (done, or what remains). Append a `LOG.md` entry: what changed, what was learned, what the next agent must know.
6. One task per session unless the next is trivial. Leave the tree green.

## Two agents, one tree

- Claim before editing. Never touch a task another agent has claimed.
- `LOG.md` is append-only. Never rewrite another agent's entry.
- Commit at the end of every session with the task id in the message. Pull before claiming.
- Owner standing authorization (2026-09-19): publish completed, validated project work to the existing origin, including fast-forwarding and pushing main, without asking again. Check remote changes before pushing and verify CI afterward.
- To reverse a decision, add a `DECISIONS.md` entry proposing it. Never revert silently.
- Long studies run from a clean worktree so evidence provenance stays clean while work continues: commit first, `git worktree add <scratch>/run HEAD`, run `python -m tests.<name>_study` there with output outside the repo, copy the JSON into `evidence/`, then `git worktree remove`. Evidence whose `source.dirty` is true is not evidence.
- Studies are the modules in `tests/*_study.py`; each case file names its study, evidence file and clean revision. Re-run evidence after any engine change that could move it, and record the new revision in the case file and `TASKS.md`.

## Adding a world

- One file in `worlds/`, exposing `SPACE` (this world's assumptions register, all swept), `FIXED`, `FIXED_REASONS` (a reason per fixed value), `DEFAULTS` (a declared baseline for `--oat` and tests), `STAKEHOLDERS`, `HARMS`, `EXCLUDED` (who outcomes fall on, agents or not; what harms; what is left out and why), `make(params, rng)` and `describe(joint, state)`. Implement `stakeholders()` and `harmed(state)`. Declare `types()` for agents that are truly exchangeable (same menus, channels and role); test the invariance, never assume it. Name the people a harm falls on even when they have no agent: the report shows them as unrepresented, which is the point. States, observations, actions and parameters must be finite JSON-compatible data with string dictionary keys.
- Implement `observe`, finite `beliefs` and `outcomes` explicitly; the engine samples `step` from that kernel. Menus use observations. Keep private facts in state; test that indistinguishable truths give equal action values and future choices cannot distinguish hidden branches. Nested beliefs must not recover truth through attributes. Use `engine.core.action_values` for probes. Declare history/learning, depth caps and work limits; unresolved search is neither survival nor collapse.
- The paper case in `rediscovery/` comes first, with expected outcomes and interventions.
- Separate implementation regressions from research hypotheses. Existing outcome tests describe their tested configurations, not historical laws. Use several seeds and parameter settings, preserve counterexamples, and record why any expected outcome changes. Random seeds alone do not vary assumptions.
- Add a competing explanation and a source before treating a paper case as empirical evidence. "Unverified" is an acceptable status. Diagnose a failed expectation before changing primitives or tuning parameters.
- Save JSON evidence with source provenance, parameters, seeds and duration. Iteration over sets must not assign random draws to different actors across processes. Finite survival must not be called an attractor.
- When the engine disagrees with the paper case, probe before changing anything: print each agent's action values per round. The commons collapsed for three different reasons in one session, and each needed a different fix. Two were artifacts, one was a finding.
- The first surprise goes into the case file under "Engine findings", with the one-at-a-time table.

## Things agents get wrong here

- Scripting behavior. "Agents sanction defectors" is a bug. Give them the sanction action and the goal, and let the planner decide.
- Adding a primitive because the world would be clearer, or refusing a needed replacement to protect old code. A consequential, reproducible limitation is the test; compare both extension and replacement.
- A number outside `SPACE` or `FIXED`.
- Tuning until a test passes. If the expected outcome only appears at a corner, say so in the case file. That is a finding.
- Making the planner cleverer before a case needs it. Level-0 beliefs stayed until the commons showed they cannot hold a norm.
- Analysing a part alone. Harm is externalized at the boundaries between parts. If a world touches another (a shared resource, the same actors), compose them and report the whole; declare every coupling and carry or cover every exclusion.
- Reporting a good outcome without asking who could still force it away. Run the power query: survival that rests on goals is deterrence, not denial.
- Treating a green suite as a validated model. It means the known outcomes emerge. It says nothing about unknown ones.
- Long prose. Files are read by the next agent deciding what to trust.

## Style

Terse. No hype. Files lowercase with hyphens, Python snake_case. Ids stable once a test uses them. Stdlib only unless a decision record says otherwise.

## Commands

```
python -m pytest -q
python -m engine worlds.commons --oat                 one parameter at a time from DEFAULTS
python -m engine worlds.commons --samples 100         random sweep of the register
python -m engine worlds.commons --trace --fix n=4     one world, round by round
python -m engine worlds.commons --power 3             goal-free: what each coalition can force or prevent
python -m engine worlds.commons --trace --profile 3   a run, with who could force or prevent collapse each round
python -m engine worlds.commons --externalities 3 --state S=20   per declared harm: force, impose, prevent, end
python -m engine worlds.control --assess 3 --rule corrigibility   one screen: power, rule, capture, exclusions
python -m engine worlds.frontier --enforce 4 --rule licensing --size 2 --window 2   rule as a claim: who breaks it, who captures it
python -m engine worlds.authority --externalities 2 --lock 3     who can force a harm, then keep it 3 rounds against everyone
```

Rule checks: use `window=2` (two-round coordinated departures) when asking about capture; one-round checks missed the frontier capture. `precaution=q` values acting on revealed departures. Modules that wrap any world (`engine/transfers.py`, `history.py`, `constitution.py`, `delegation.py`) never change power; worlds expose `PAID_RULES` / `RECORD_RULES` for them.
