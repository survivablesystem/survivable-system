# Decisions

Log of changes to the core (`INTENT.md`, `spec/`, `engine/`). Newest first. Each entry names the intent tests it serves and the case that motivated it.

```
## YYYY-MM-DD  short title
Change / Motivated by / Intent tests / Alternatives rejected
```

## 2026-09-19  T1.3: finite belief-tree search and one transition kernel

Proposed before implementation. Replace constant-action rollouts and mean-state transitions with a finite stochastic kernel shared by planning and execution. Optimize future actions by observable history, integrating utility over physical branches before comparing actions. Replace the point projection with `observe(state, agent)` and `beliefs(observation, agent)`; menus receive observations. Group indistinguishable future branches into one posterior before selecting an action. This prevents future choices from acquiring hidden branch information.

Simplest implementation: enumerate finite outcomes and finite-depth action trees, with no heuristic tail or sampling inside planning. Level 0 retains repetition/priors. Level 1 recomputes direct observers' level-0 responses at future nodes, bounded by the remaining search depth and their own horizon. Known utilities/topology, explicit subjective priors, first-listed ties and receding-horizon execution remain assumptions. Belief history must be represented in observations when a world needs memory across real rounds.

Bound work before scaling: separate desired horizon from an explicit search-depth cap; commons sweeps depths 1/2/3, default 2 (the shortest resolving the motivating sequence). A declared transition-work budget aborts an incomplete decision, never selects from partial scores. Record unresolved runs separately from physical outcomes, including partial traces and planning limits. Compare short matched commons runs against both the old default horizon and horizon 2. Do not require previous survival claims to persist.

Motivated by: T1.0's investment (optimal sequence 3, repeated consume 2) and threshold case (risky expectation -4, mean-state evaluation 2). Discriminating additions: hidden versus revealed future branches, exact branch arithmetic, menu changes, terminal payoffs and budget exhaustion. This changes interfaces coherently; old artifacts remain reproducible at their source revisions, not through a second legacy planner.

Intent tests: 1 one kernel and one finite search; 2 actions and responses still computed; 3 priors, search caps and unresolved work explicit; 4 independent small references and contrary commons results retained; 5 severe branch losses no longer disappear into an average state; 6 test whether richer planning overturns the earlier norm result. Rejected: investment scripts, extra catastrophe penalties, full-state tree search with clairvoyant continuations, unbounded exhaustive search, and unvalidated sampling/aggregation to conceal cost.

## 2026-09-19  T1.0: explicit planning information and directed response

Change: require each world to provide `belief_state(state, agent)`, a pure projection to a complete hypothetical state using permitted information and declared point priors. Both candidate menus and rollouts use that projection; actual execution uses the real state. Nested plans project the parent's hypothetical state, never recover the original truth. Expose `action_values` through the same path used by `plan`. At level 1, model agents that observe the acting agent, whether or not the actor can observe them. Channel topology and utility functions are treated as known; direct observation triggers one response, not arbitrary inference from public effects.

Motivated by: `rediscovery/planner-audit.md`, executable at pre-fix commit `ab6b02a`. A one-way observer should make take worth -1 rather than 2 over two rounds, but was omitted. An unrevealed hidden bit changed values and the selected guess despite identical information. The projection replaces implicit full-state planning with one explicit boundary, rather than adding private-field exceptions in every planner operation.

Limits retained: a point belief is not a belief distribution or a posterior update; world authors must enforce the projection contract and keep true private data out of planning methods/attributes. First-listed ties remain explicit. Investment and threshold counterexamples justify a subsequent shared search/transition redesign; no special-case strategy or risk penalty is inserted here. The commons' full/no-channel regressions and saved trajectory must still hold, but this audit does not validate them under stronger planning.

Intent tests: 1 one information boundary and one directed predicate; 2 responses still computed from goals; 3 point priors and known-model assumptions declared; 4 tests compare indistinguishable truths and exact toy references; 5 unilateral observation and utility-neutral side effects exposed; 6 wrong rankings arise even with adequate horizons and level-1 beliefs. Alternatives rejected: hidden-state masking in the CLI only; treating channels as symmetric; sticky tie rules without sensitivity evidence; world-specific investment/risk fixes.

## 2026-09-19  T1.0: preserve purpose, replace machinery when evidence warrants

Change: adopt the owner's explicit direction that any implementation, planner or model abstraction may be expanded or rebuilt while preserving the core purpose and evidence standards. Simplicity means few coherent mechanisms, not a fixed line count or perpetual compatibility. Compare extension with replacement; retire obsolete paths instead of stacking case-specific fixes. Preserve counterexamples and revisioned evidence across migrations. Internal ontology and aggregation changes need evidence and a decision record, not renewed permission; unresolved values and real-world scenario boundaries still need owner steering.

Motivated by: the owner's instruction to continue and not protect early prototypes at the expense of a more general, powerful tool. This relaxes the literal spec-size/shrinkage target and the assumption that the present agent ontology or planner is permanent. It does not authorize changing the purpose, scripting desired outcomes or asserting validity from passing tests.

Intent tests: 1 prefer the simplest adequate architecture, including replacement; 2 retain computed choices; 3 keep explicit assumptions and migrations; 4 compare against disconfirming cases; 5 preserve affected-party accounting; 6 let limitations force general improvements. Alternatives rejected: freezing v0; adding complexity merely for imagined future needs; rewriting without a discriminating test.

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

- **Claims as one primitive.** Rules, money and legitimacy may be one thing: a claim, worth what others are believed to honor, backed by the contest enforcing it would win. The money brief must test this against alternatives. Under the 2026-09-19 standing direction, revise the spec through evidence and a decision record; owner steering is needed if values or real-world scope change.
- **Readiness tie.** Standing ready and not are tied in value when nobody defects; ties go to the earlier action, so readiness alternates each round. Cosmetic so far. T1.2.
- **Horizon of modeled others.** Level-1 rollouts give modeled others their full horizon, which dominates runtime. A shorter modeled horizon would be a new parameter. Not until T8.2 shows it matters.
- **Sanction targeting.** Sanctioners act against every visible defector. A case that needs selective targeting would reintroduce a choice, and the id tie-break showed how a targeting rule can leak asymmetry.
