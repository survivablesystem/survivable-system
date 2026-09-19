# Decisions

Log of changes to the core (`INTENT.md`, `spec/`, `engine/`). Newest first. Each entry names the intent tests it serves and the case that motivated it.

```
## YYYY-MM-DD  short title
Change / Motivated by / Intent tests / Alternatives rejected
```

## 2026-09-19  T0.1: evidence before expansion

Change: propose and adopt replacing mandatory historical outcomes with falsifiable hypotheses. A failed expectation can expose a wrong hypothesis, setup, implementation, planner or primitive; it does not identify which. State that the current planner compares constant-action rollouts, uses cardinal per-round utility and expected transitions, and does not establish global optimality. Finite survival becomes `survived`, not an attractor. Keep dynamics and planner choices otherwise unchanged.

Motivated by: the owner's review and request to improve and publish. The commons with horizon 1 and no sanction is labeled sustained after one round but collapses at round five. The rediscovery guide treated every failed expectation as a missing primitive. This reverses that validation rule explicitly; prior findings remain in history and gain scope notes.

Implementation: JSON records for sweep, one-at-a-time and trace, with schema version, normalized source hashes, Git revision/dirty status, Python version, register, fixed reasons, parameters, integer seeds, requested/executed rounds, terminal status and final state. Canonical target iteration prevents Python hash order assigning random draws to different targets. Fixed CLI overrides remain fixed in one-at-a-time experiments. Validate overrides instead of silently accepting misspellings. Add CI on Windows and Linux.

Intent tests: 1 reuses existing simulation with no new primitive; 2 does not prescribe agent choices; 3 records assumptions and limitations; 4 permits disconfirmation; 5 retains per-agent wealth in evidence and requires excluded harms to be declared; 6 preserves the finite-duration counterexample and tests for artifacts. No validated institutional or civilizational protocol is claimed.

Alternatives rejected: adding worlds before correcting the evidence contract; implementing a stronger planner without a discriminating case; reporting sample shares as probabilities; using only a Git SHA when the working tree may differ.

## 2026-09-15  one-at-a-time sweep mode
Change: `engine/sweep.py` gains `one_at_a_time`; CLI `--oat`.
Motivated by: the commons. Sustained needs six conditions at once; a random sweep found it in 2% of samples with no parameter above the dependence threshold. Moving one parameter from a favorable baseline shows each necessary condition.
Intent tests: 3, 6. Alternatives rejected: raising the sample count (does not fix a conjunctive outcome); a smarter dependence statistic (premature).

## 2026-09-15  where confiscated takes go is a design parameter
Change: `worlds/commons.py` register gains `confiscation_to: stock | sanctioners`.
Motivated by: second-order free riding. With takes returned to the stock nobody sanctions at any size or cost; with takes paid to sanctioners the norm holds and restarts. This is an institutional design choice, so it is swept, not fixed.
Intent tests: 1 (a world-level parameter, no engine change), 5, 6.

## 2026-09-15  planner: level-k beliefs, k in the register
Change: `Agent.k`. Level 0: others repeat their last observed action, unobserved take the prior. Level 1: observed others are level-0 planners who respond once, at the first rollout step where the agent's action is visible, then hold. Modeled others use their own horizon.
Motivated by: the commons. Level 0 cannot hold a norm, established or not: readiness has no value to an agent that expects only repetition.
Intent tests: 2, 3. Strains 1: the engine grew. Alternatives rejected: full re-planning of modeled others every rollout step (six times the cost, same qualitative result expected; add when a case needs it, A1); sticky or conditional belief heuristics (scripting by another name).

## 2026-09-15  contest function: ratio of capabilities
Change: success probability for m equal sanctioners against one target is m/(m+1).
Motivated by: the commons needs a contest; this is the simplest member of the ratio family.
Intent tests: 1. Open: A2, add a second form only when a case's outcome depends on the form.

## 2026-09-15  worlds are Python modules
Change: a world is a Python file exposing SPACE, FIXED, DEFAULTS, make, describe. No YAML, no DSL.
Motivated by: goal functions and dynamics are code. A declarative layer would be a second language to maintain before any world repeats boilerplate.
Intent tests: 1. Revisit when three worlds share structure that could be declared.

## 2026-09-15  adoption of PRIMITIVES.md; removal of the static linter
Change: `spec/PRIMITIVES.md` is the model. Removed `analyzer/`, `components/`, `cases/`, `spec/SPEC.md`, `spec/actors.yaml`, `.github/`, `CONTRIBUTING.md`. INTENT.md rewritten; the six tests now lead with simplicity and non-scripting.
Motivated by: the owner's goal. Where the linter's ideas went: sinks and net-losers become attractor and coalition queries over agents whose goals include the cost; concentration and capture become the lock-in threshold (T4.2); adoption becomes what the planner chooses; the sweep survives as the register; the disclosure channel and compute attestation return as modules in the frontier scenario (T9.1); actors become types.
Intent tests: all six re-derived. Alternatives rejected: keeping the linter as a time-zero snapshot (two models to maintain).

## 2026-09-14  capture restricted to connected actors
Change to the removed linter; kept for history. Capture considered only actors with a flow to the component. Motivated by the lab-oversight case ranking unconnected actors highest.

## Open questions

- **Claims as one primitive.** Rules, money and legitimacy may be one thing: a claim, worth what others are believed to honor, backed by the contest enforcing it would win. The money brief will test this. ASK the owner before changing the spec.
- **Readiness tie.** Standing ready and not are tied in value when nobody defects; ties go to the earlier action, so readiness alternates each round. Cosmetic so far. T1.2.
- **Horizon of modeled others.** Level-1 rollouts give modeled others their full horizon, which dominates runtime. A shorter modeled horizon would be a new parameter. Not until T8.2 shows it matters.
- **Sanction targeting.** Sanctioners act against every visible defector. A case that needs selective targeting would reintroduce a choice, and the id tie-break showed how a targeting rule can leak asymmetry.
