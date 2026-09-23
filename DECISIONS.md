# Decisions

Log of changes to the core (`INTENT.md`, `spec/`, `engine/`). Newest first. Each entry names the intent tests it serves and the case that motivated it.

```
## YYYY-MM-DD  short title
Change / Motivated by / Intent tests / Alternatives rejected
```

## 2026-09-23  T1.5: goal-free coalition power beside goal-driven behavior

Proposed before implementation. Every commons result so far depends on authored
goals, horizons, beliefs and planner depth, the assumptions INTENT says hide
opinion. INTENT's central questions (who can force an irreversible outcome, who
can prevent or correct it) are questions of power, answerable without goals.
Separating them distinguishes protection by deterrence (rests on the goals of
the capable) from protection by denial (holds whatever anyone wants). Unknown or
drifting goals of new agents, AI systems included, make the distinction central.

Add `engine/power.py`: finite-horizon, zero-sum reachability over the world's own
kernel. A coalition maximizes the probability of entering a flagged terminal
label within T rounds; the complement minimizes it as one coordinated adversary;
chance follows `outcomes`. Both sides see the full state and act by pure,
history-dependent strategies; menus still come from each agent's observation.
Two stage orders bracket the value: alpha (coalition commits each round first)
is what it can guarantee; beta (complement commits first) bounds it above. By
induction any randomized stage strategy lies between them, so equality is exact.
Prevention is the dual: prevent_alpha(C) = 1 - force_beta(complement of C).
Thresholds are the smallest coalition sizes reaching a stated probability, with
witnesses; unresolved sizes block a threshold claim. Work is capped per query as
in `core`; exhaustion is unresolved, never a power result.

One optional world method, `physical(state)`: the part of the state that
determines menus, kernel and terminal status. Default is the whole state. It is
only a memo key for the power query; a wrong projection is a world bug, tested
by comparing menus, successor projections and terminal status across states that
share it. Commons declares stock and collapse.

This implements the spec's lock-in and prevention queries in a bounded form
(T4.2/T4.3 remain for rule/authority worlds and correction of error states).
It is not a planner change and scripts no behavior; goals are unused.

Alternatives rejected: sampling adversaries (cannot certify a guarantee);
restricting coalitions to stationary strategies (understates power, hides
adaptive defense); a mixed-strategy LP per stage (needs a solver and is only
needed where the bracket is open); symmetry reduction by coalition size (an
assumption about the world; checked, not assumed).

Discriminating checks: hand-computed toy games (one where order matters, one
with chance), duality, monotonicity in coalition, invariance to goal/planner
parameters, projection validity, work-cap aborts.

Intent tests: 1 one query over the existing kernel, one optional projection;
2 no behavior computed or scripted; 3 query horizon, probability level and state
grid are recorded settings, and goal parameters drop out of the claim; 4
hypotheses and contradictions in `rediscovery/coalition-power.md` before runs;
5 names who can force or block an irreversible harm regardless of intent; 6
compare what agents do with what they could do.

## 2026-09-19  T1.4: exact reward integration at search leaves

Proposed before implementation. Baseline profile `2535e47` shows branch expansion,
not mostly repeated kernels: n=10/depth=2 after one all-high round exhausts 20,000
entries in 116 kernel calls (93 unique); n=4/depth=3 uses 17,589 transition entries
and 213 cached nested responses. Caching full state/joint kernels alone cannot
remove this exponential leaf cost. See `evidence/search-profile-before.json`.

Add `reward_outcomes(state, joint)`: a finite distribution of per-agent immediate
utilities whose expectation must equal `outcomes` followed by `value`. Default
derives it from that kernel. A world may supply a proved exact marginal reduction;
commons uses linearity of expected confiscation/receipts over independent contests.
Share round preparation and payoff arithmetic with the physical kernel. Use this
distribution only at depth 1, where no future action, observation or terminal test
depends on successor identity. Never evaluate nonlinear utility on mean state.
Charge every emitted reward entry, including zero weight, to the same root work cap.
Document the changed work unit; leave physical sampling and earlier branches intact.

Compare extension versus replacement: a factor-graph planner/world rewrite might
reduce interior branching but needs new conditional inference and information-set
proofs. Leaf reward integration is smaller, general across finite worlds and retains
the existing exact references. Reject mean-state planning, sampled tails, symmetry
assumptions and increasing the cap to call unresolved searches completed.

Discriminating checks: exact kernel/reward expectations across commons configurations,
threshold-crossing states and joint actions; optimized versus full-kernel planner
values/traces; nonlinear-risk and asymmetric hidden-information diagnostics; work
caps and zero-weight entries. Record measured numerical error, timings and remaining
unresolved rows. No approximation or new behavioral primitive is introduced.

Intent tests: 1 one optional exact marginal interface; 2 no behavior scripted;
3 fixed cap, source and workload explicit; 4 compare full enumeration and negative
coverage results; 5 utility losses remain branch-weighted; 6 measure which apparent
population limits were computational, without inferring institutional effects.

Outcome: adopt the reduction. The n=8/depth=2 contested decision completes in
5,241 entries versus 348,202 with full enumeration under a separate reference cap,
with equal values. Its 30-round runs now reach collapse at 17. Retained traces and
action probes agree; numerical marginal error is below 9e-16. Ten-user depth-2/3
limits remain, and some unresolved searches take longer. No population/horizon
extrapolation follows. Full evidence and boundaries: `rediscovery/search-reduction.md`.

## 2026-09-19  T1.3: finite belief-tree search and one transition kernel

Proposed before implementation. Replace constant-action rollouts and mean-state transitions with a finite stochastic kernel shared by planning and execution. Optimize future actions by observable history, integrating utility over physical branches before comparing actions. Replace the point projection with `observe(state, agent)` and `beliefs(observation, agent)`; menus receive observations. Group indistinguishable future branches into one posterior before selecting an action. This prevents future choices from acquiring hidden branch information.

Simplest implementation: enumerate finite outcomes and finite-depth action trees, with no heuristic tail or sampling inside planning. Level 0 retains repetition/priors. Level 1 recomputes direct observers' level-0 responses at future nodes, bounded by the remaining search depth and their own horizon. Known utilities/topology, explicit subjective priors, first-listed ties and receding-horizon execution remain assumptions. Belief history must be represented in observations when a world needs memory across real rounds.

Bound work before scaling: separate desired horizon from an explicit search-depth cap; commons sweeps depths 1/2/3, default 2 (the shortest resolving the motivating sequence). A declared transition-work budget aborts an incomplete decision, never selects from partial scores. Record unresolved runs separately from physical outcomes, including partial traces and planning limits. Compare short matched commons runs against both the old default horizon and horizon 2. Do not require previous survival claims to persist.

Motivated by: T1.0's investment (optimal sequence 3, repeated consume 2) and threshold case (risky expectation -4, mean-state evaluation 2). Discriminating additions: hidden versus revealed future branches, exact branch arithmetic, menu changes, terminal payoffs and budget exhaustion. This changes interfaces coherently; old artifacts remain reproducible at their source revisions, not through a second legacy planner.

Intent tests: 1 one kernel and one finite search; 2 actions and responses still computed; 3 priors, search caps and unresolved work explicit; 4 independent small references and contrary commons results retained; 5 severe branch losses no longer disappear into an average state; 6 test whether richer planning overturns the earlier norm result. Rejected: investment scripts, extra catastrophe penalties, full-state tree search with clairvoyant continuations, unbounded exhaustive search, and unvalidated sampling/aggregation to conceal cost.

T1.3 outcome: arithmetic, observation-grouping and budget checks pass. Commons' new depth-2 baseline collapses at 17, but an archived old horizon-2 control does too; old horizon 12 survives 30. Thus depth confounds the apparent reversal, and deeper-horizon conclusions remain open. Ten-user exact searches hit the cap. Adopt the coherent replacement with these limits, retire the old paths, and insert measured search reduction before population/channel claims. Details and timings: `rediscovery/planner-replacement.md`.

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
