# Tasks

Ordered. Claim with `[claimed: name, date]`, finish with `[done: name, date]`. Each task names what forces it and the acceptance line. Add at the end, or insert with a reason. Internal architecture may evolve under the owner's standing direction; record evidence and decisions. Unresolved values and real-world scenario boundaries are marked ASK.

Research acceptance means testing the stated hypothesis and recording its boundary or counterexample. A contrary result is not a failed implementation. Do not tune a world or add primitives just to obtain an expected sign. Separate code regressions from empirical claims.

## Stage 0: skeleton  [done: Fable, 2026-09-15]

- Engine v0: World interface, level-k planner, run loop, random sweep, one-at-a-time sweep, CLI.
- Commons world with tests reproducing and correcting `rediscovery/open-commons.md`.

## Stage 1: commons, finish

- T0.1 Reliable evidence and publication. [done: Codex, 2026-09-19] Inserted before T1.1 because the owner review found confirmation-biased acceptance rules and finite survival mislabeled as an attractor. Implemented falsifiable research acceptance, finite labels, reproducible JSON in all CLI modes, stable stochastic target order, validated overrides and fixed OAT controls. 34 local tests pass; Windows/Linux CI passes. Published to `survivablesystem/survivable-system`; replayable counterexample in `evidence/`. No planner expansion or new primitive. There was no remote to pull before claiming.

- T1.0 Information and planner audit. [done: Codex, 2026-09-19] Five diagnostic cases and exact references in `rediscovery/planner-audit.md` and `tests/planner_cases.py`. Fixed response direction and implicit full-state planning with a required belief-state projection shared by menus, values and nested plans. Preserved measured tie, sequence and threshold limits; before/after artifacts in `evidence/`. 52 tests pass locally and Windows/Linux CI passes. Original commons trajectory replays unchanged; no claim it survives stronger planning. Owner's standing permission for coherent expansion/rebuilding recorded in intent and agent guidance. Next: T1.3.

- T1.3 Planner and transition replacement. Inserted before sparse-channel findings: T1.0 proves constant-action planning rejects a profitable investment and mean transitions reverse a risk ranking. Acceptance: one coherent transition/search model supports action sequences and branch-weighted utility, using the investment and threshold cases as exact references. Preserve information isolation and directed response tests; compare commons conclusions, runtime and approximations explicitly. Replace superseded internals rather than adding investment heuristics or catastrophe penalties. Exact small cases first; bound and declare search limits before large worlds. If uncertain hidden states require distributions, replace the point-belief interface coherently rather than layering contradictory paths.

- T1.1 Sparse channels. `channels` gains a structured option (ring, or each user observes m random others). Hypothesis: limited observability may produce a size effect. Acceptance: measure survival through a stated duration across sizes and channel structures with matched assumptions and several seeds; record absent or reversed effects. Test directed observation separately before relying on asymmetric graphs.
- T1.2 Readiness tie artifact. Decide: leave it, or break ties toward the current action. Record in DECISIONS.md either way. Low priority.

## Stage 2: captured auditor

Forces: a resource with conversion (credibility to future income), selection (exit and entry), an information channel as a swept variable.
- T2.0 Evidence review before another world. Acceptance: sourced, scoped auditor hypotheses, a rival explanation, a disconfirming result and affected/excluded groups. Explicitly revisit "never by the auditor" and "regardless of individual goals"; these are unverified conjectures in the existing brief.
- T2.1 World from `rediscovery/captured-auditor.md`. Firm, k auditors, regulator. Hypothesis: independent exposure and longer horizons can constrain leniency. Acceptance: map conditions for honesty and capture, including counterexamples, after T2.0. Do not make firm switching or auditor exit encode the conclusion.
- T2.2 Only if T2.1 needs it: resources and conversions in `engine/core.py`. Decision record first.
- T2.3 Engine findings into the case file.
- T7.2 Paired comparison (moved here: useful evidence should not wait for every world). Separate controllable design choices from uncertain conditions. Compare auditor arrangements on the same parameter samples and recorded seeds; report per-group costs and finite outcomes, reversals and exclusions. Shared seeds alone do not guarantee identical shocks when alternatives consume randomness differently. Coalition thresholds remain deferred to T4.

## Stage 3: treaty without verification

Forces: goals over another agent's state, channel noise, capability that accumulates.
- T3.1 World from `rediscovery/treaty-no-verification.md`. Hypothesis: verification and credible response constrain building; increasing returns may defeat them. Acceptance: scoped evidence and counterexamples, then map building/compliance and lead persistence across the stated conditions.

## Stage 4: standing army

Forces: rules as claims, contests over authority, delegation with drift, the lock-in query.
- T4.1 World from `rediscovery/standing-army.md`. Hypothesis: coercive concentration defeats succession rules; split command and independent pay may help. Acceptance: compare authority outcomes under explicit capability assumptions and competing sources of compliance; record when the proposed interventions fail.
- T4.2 `engine/queries.py`: lock-in threshold, smallest coalition that can force a flagged irreversible transition, brute force for n at most 8. Acceptance: define the time bound, adversary strategies and treatment of chance; return a witness or counterexample. Simulated success under one planner is not "regardless of others". Compare interventions without requiring a higher threshold.
- T4.3 Correction threshold: smallest coalition that can reverse a flagged error state.

## Stage 5: kinship and trust

Forces: goals over others' outcomes, structured channels, possibly group selection.
- T5.1 World from `rediscovery/kinship-trust.md`. Hypothesis: kin preference and observation structure influence cooperation boundaries. Acceptance: sourced hypotheses and comparison with alternatives such as reciprocal exchange; map cooperation within/across groups with and without an enforcer, retaining counterexamples.

## Stage 6: money issuance

Forces: claims as a candidate primitive (a decision record and discriminating cases must justify unifying rules, money and legitimacy), issuance capability.
- T6.1 World from `rediscovery/money-issuance.md`. Hypothesis: readable supply and promises improve issuer discipline. Acceptance: sourced hypotheses, rival mechanisms and failure conditions; compare hidden/visible supply and redemption information without requiring issuer selection to favor the proposed design.

## Stage 7: composition and diff

- T7.1 Modules as functions from world to world; a case composes a base world with modules. Acceptance: the commons with and without the paid-sanction module as two named cases.
- T7.2 Moved to stage 2; extend comparisons with coalition thresholds once T4 is complete.

## Stage 8: scale

- T8.1 Types with populations: a world declares types and counts; the engine expands them. Aggregation or mean field needs a case, a decision record and comparison with smaller exact populations. Demonstrate what is preserved and lost; internal architecture changes are covered by the owner's standing direction.
- T8.2 Performance: profile `step` and `evaluate` before any world with more than a dozen agents. The commons one-at-a-time run takes three minutes.

## Stage 9: first real scenario

- T9.1 Frontier AI. Labs, regulator, state, AI systems as a type whose capability grows per round. Modules: disclosure channel, compute attestation. Question: which coalitions can force lock-in, and does either module change that. ASK on the scenario's boundary before building.

## Anytime

- A1 Beliefs beyond level 1 (full re-planning, level 2, learned) only when a discriminating case exposes a consequential limitation. Record the case; disagreement with a preferred outcome alone does not justify a stronger planner.
- A2 Contest function family: add a second form only when a case's outcome depends on the form.
- A3 Report format: one screen, robust first, then dependent, then not modeled.
