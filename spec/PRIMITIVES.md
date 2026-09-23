# Primitives, v0.4

The current model, not an immutable ontology. Adopted 2026-09-15 and revised through `DECISIONS.md`. Replace abstractions when discriminating cases support a simpler or more capable account consistent with INTENT. The status table distinguishes implemented mechanisms from proposals.

The tool simulates a world of agents and asks what structures emerge. Mechanisms and available actions are authored; action choices are computed. `rediscovery/` tests explicit hypotheses and competing explanations. Reproducing an outcome does not validate its historical cause.

## One object: the agent

The same object at every scale. A person, a firm, a court, a state, an AI system, a civilization. An institution is an agent made of agents.

```
agent:
  goals:        per-round cardinal utility, discounted over the horizon. Utilities need not
                be comparable across agents. Utility form is an assumption, not just rank.
  capabilities: actions available. Base set: convert, open/close channel, contest,
                delegate, propose rule, act on the world.
  information:  channels into this agent (whom it observes), noise per channel,
                and beliefs about what other agents will do. Beliefs exist with or
                without a channel; they decide whether coalitions form. Beliefs are
                level-k (engine/core.py): level 0 expects repetition; level 1 models
                direct observers as level-0 planners at future nodes. Observation is directed.
                Their effects on norms are case-dependent findings.
  resources:    vector over resource kinds.
  horizon:      how far ahead it plans and how it discounts. A parameter, not a behavior.
```

No behavior is scripted. Each round an agent plans from its goals, capabilities, information and horizon, and acts. The planner belongs to the engine, not the model. Its rationality is a swept assumption.

Planning information: worlds implement pure `observe(state, agent)` and `beliefs(observation, agent)`. Observations contain only permitted information, including any modeled memory. Beliefs are finite `(probability, hypothetical state)` supports consistent with that observation; full information uses a singleton. Menus receive observations. Nested plans receive the parent's hypothetical state, never original hidden truth. Indistinguishable states must yield identical root beliefs, menus and values. Methods and attributes must not bypass this contract. This is a modeling interface, not a security sandbox. Observations must include channel-permitted action history used by `observed_last`; authors declare any additional public information.

Search: enumerate candidate actions, integrate immediate utility over `outcomes(state, joint)`, then group nonterminal successors by the actor's observation. Each group forms a conditional belief; choose one future action for that group. Different hidden truths cannot receive different actions unless observations distinguish them. Histories are retained along separate tree paths. No automatic belief memory persists between real rounds: a world must include sufficient history in its observations and reconstruct its beliefs. World states/actions/observations use finite JSON-compatible data with string dictionary keys. Goals must be finite.

Level 1 assumes known topology and utilities. Its opponent model is a swept assumption, `Agent.others` (decision 2026-09-23, A1). "plan": every other agent is a level-0 planner at every node, root included, from the hypothetical state and its own observations. "react" (default, the rule of all earlier evidence): at every future search node, direct observers of the actor replan at level 0, even if the actor cannot observe them. Their depth is bounded by their own effective depth and the remaining parent depth. At the root everyone else repeats observed last actions or declared priors; simulated responses begin after one transition. Non-observers continue repetition/priors. This is a subjective direct-response approximation, not simultaneous equilibrium, theory-of-mind inference from arbitrary effects, or higher-level belief reasoning. Only levels 0 and 1 are supported.

Computation: effective depth is `min(horizon, search_depth)` when a cap is supplied, otherwise horizon. There is no tail estimate. First-listed ties within absolute tolerance `1e-12` remain substantive. Search integrates all supplied branches; `node_budget` counts emitted belief, transition and leaf reward entries, including zero-weight entries and nested plans. A cap overrun aborts the decision and run as `search_limit`; it never chooses a partially evaluated winner. The cap bounds enumeration work, not runtime of arbitrary Python world code. Execution samples one outcome from the same kernel; deterministic execution needs no RNG, stochastic execution requires one. Kernel weights are nonnegative, finite and sum to one within `1e-12` (only floating-point normalization is applied). Terminal rewards count on entry, never again.

Exact leaf reduction: `reward_outcomes(state, joint)` returns a finite distribution of immediate per-agent utility maps. Its expectation must equal applying `value` to every branch of `outcomes`; the default does exactly that. A world may override it with a tested exact marginal (commons uses linearity of confiscation payoffs). Only depth-1 search uses this reduction. Interior search and execution retain the physical kernel, observations, posteriors and terminal distinctions. Nonlinear utility must be integrated before reduction, never applied to mean state. Changes to goals or the physical kernel require revalidating an override. Each emitted marginal entry consumes one work unit; earlier revisions counted full leaf branches instead. Source revisions identify the computational accounting. See `rediscovery/search-reduction.md` for coverage and remaining limits.

Commons declares depth choices 1/2/3 and a fixed work cap. Large populations or deeper trees may be unresolved; they cannot be counted as survival or collapse. Exactness means agreement with this finite subjective model and depth, not an optimal institutional design. The investment, nonlinear-risk and hidden-branch diagnostics justify this replacement; see `rediscovery/planner-replacement.md` for measured cost and changed conclusions.

## The world

```
resources:       kinds, conversion rates between kinds, returns to scale per conversion.
                 Money, coercive capability, information and authority are kinds, not special cases.
contests:        when actions conflict, the outcome is a function of capability, information
                 advantage and coalition size. The function form is swept over a family.
rules:           nested levels. L0 operational: which actions are allowed. L1 collective: who
                 changes L0. L2 constitutional: who changes L1. A rule is a claim, not a
                 constraint. Violating it is an action; it succeeds or fails in a contest against
                 whoever chooses to enforce, and the enforcing coalition depends on agents'
                 beliefs about each other. (Forced by rediscovery/standing-army.)
                 Levels are a module (decision 2026-09-23, E10): `engine/constitution.py` makes
                 the regime in force a public fact that declared voters can amend by a threshold;
                 the conduct checked is "follow the regime in force". Who votes and the threshold
                 are the L1 rule; L2 is the module nested.
                 Implemented as declared conduct (decision 2026-09-23, E7): a world's RULES map
                 each agent's observation to an action; the kernel never enforces them. Queries
                 ask whether following pays (one-shot departures, on and off the path) and which
                 coalitions gain by departing together, naming harms that land outside them.
                 Hypothesis, untested: rules, money and legitimacy are one primitive, the
                 claim, worth what others are believed to honor. rediscovery/money-issuance.
delegation:      an agent may create a sub-agent, granting capability and setting its goal.
                 The set goal drifts from the intended one by a swept amount.
                 Implemented as a goal module (decision 2026-09-23, E11): a delegate's utility is
                 (1 - drift) x its principal's plus drift x its own; capability is granted by the
                 world's mechanics; the agent set is fixed.
irreversibility: flagged transitions that cannot be undone, and harms that a coalition can
                 keep against everyone else (computed by the lock query, E5). A case declares
                 catastrophic harms, affected groups and exclusions; majority utility is not a
                 definition.
harms:           declared per world (STAKEHOLDERS, HARMS, EXCLUDED; decision 2026-09-23, E1):
                 predicates on physical state, irreversible or not, each naming the
                 stakeholders it falls on, agents or not. Every artifact carries them.
error:           beliefs can be wrong. A correction moves the world back after an error. It
                 needs a detector with a channel, an actor with capability, and an erring agent
                 that cannot win the contest to block it.
selection:       agents whose resources reach zero exit. New agents enter by delegation.
                 Populations evolve. (Forced by rediscovery/captured-auditor.)
time:            discrete rounds.
```

## Scale

Worlds may declare groups of exchangeable agents (`World.types()`, decision 2026-09-23, E2): permuting their actions leaves successor physical states, menus and harms unchanged. Power queries then enumerate action multisets per group and coalitions up to permutation, exactly; rows carry `stands_for`. Symmetry is a declared, tested claim, not a detected one. The planner still expands individuals.

The engine otherwise expands individual agents. Types with populations and nested institutions are proposed abstractions, not demonstrated equivalences across scale. Use mean field only after a case and comparison justify what it preserves and loses (T8.1).

## Modules

A module is an intervention on the world or on a set of types: change a conversion rate, add or remove a channel, add a rule at a level, add an amendment rule, restrict an action set, flag a transition irreversible, create a type. Composition is the union of interventions on one world. Interactions emerge because everything acts on the same dynamics.

Worlds compose (`engine/compose.py`, decision 2026-09-23, E4): parts keep their kernels; actors map across parts and act in each; a declared coupling carries flows between parts; outsiders see only a part's public facts. Harms, stakeholders and exclusions of the parts become the whole's, with every part exclusion carried or covered. The whole is the unit of analysis: harms one part imposes on another, and forced choices between harms in different parts (`joint_prevention`), appear only there.

Two modules apply to any world (decisions 2026-09-23, E8 and E9). `engine/transfers.py`: declared payers may pay declared recipients (one agent or a group) declared amounts of utility each round, unconditional and unlimited by wealth, seen by the parties or by everyone. `engine/history.py`: worlds declare `public(state)`; the last k records join every observation. Neither touches the kernel, physical state or harms, so goal-free power is unchanged by construction; both change which rules can hold. They nest.

AI advancement is a module: a new type whose capability grows per round, plus shifts in conversion rates (information to capability becomes cheap; capability gains returns to scale).

## Queries

For a composed world, under a sweep over the assumptions register:

- **lock-in threshold**: smallest coalition that can force an irreversible transition regardless of others. Want high.
- **prevention threshold**: smallest coalition that can keep an irreversible transition from happening regardless of others. Want low.
- **correction threshold**: smallest coalition that can reverse a detected error regardless of others. Want low. Bounded form implemented for realized harms (E1), with `keep` (smallest coalition that can keep the harm against everyone) and `veto` (agents without whom nobody can end it) (E5).
- **lock**: smallest coalition that can force a harm and then keep it for T' rounds against everyone (`engine.power.lock_in`, decision 2026-09-23, E5). Irreversibility is computed, not only declared: a harm some coalition can lock is irreversible for everyone outside it within T', whatever its flag; for a terminal harm lock equals force. A realized harm declared irreversible that some coalition can end is a declaration error and fails loudly. Keeping is with certainty by default; below certainty the pure-strategy value is a lower bound. At p = 1 every alpha value is exact (a mixture guarantees certainty only if each action in it does).
- **externalization**: per declared harm, the thresholds above plus the smallest coalition that can force it without any affected agent, whether the affected can prevent it, and which affected stakeholders have no agent (`engine.power.externalization`).

Power is goal-free (`engine/power.py`, bounded form implemented). Within T rounds, a coalition maximizes the probability of entering a flagged terminal label; the complement minimizes it as one coordinated adversary; both see the full state; chance follows `outcomes`. Stage orders bracket the value: alpha (coalition commits first) is its guarantee, beta an upper bound; randomized play lies between. Prevention is the dual. Goals, horizons, beliefs and planner limits do not enter, so a power claim does not depend on them. What agents do (planner) and what coalitions could force (power) are separate reports; protection that rests on the gap between them is deterrence, not denial. Worlds may declare `physical(state)`, the part fixing menus, kernel and terminal status, as a memo key; the default is the whole state. Thresholds with an unresolved or straddling smaller coalition are upper bounds. Exact enumeration is exponential in agents and T; no claim extends beyond T.
- **assessment** (`engine/assess.py`, `--assess T`): one screen for any world and proposed rule, robust results first (power over declared harms), then goal-dependent ones (does the rule hold, harmful departures, capture over one or two rounds), then exclusions.
- **enforcement** (goal-based, `engine.rules.enforcement`, CLI `--enforce D --rule NAME`): does a declared rule hold within D rounds? Per agent, the best one-shot departure (its own information) at the start and at every state within `reach` rounds with at most one departure per round, so punishments off the path are checked; per coalition, the best one-shot joint departure (full information, summed value: an upper bound, side payments assumed), and separately the best departure that newly reaches a declared harm on stakeholders outside it (capture). With a window of W rounds, also coordinated departures spread over rounds (a report, then an act on it), counted as capture only if they beat what any one member achieves alone. Value beyond D is not counted. What coalitions could force (power) ignores goals; whether a rule holds depends on them.
- **finite outcomes**: labels and terminal status at a stated duration, plus shares over the sampled assumptions. Survival to the time limit is not an attractor or a probability of real-world survival. Attractor detection is not implemented.
- **coalition power**: can coalition C force outcome X. Answered per sample, reported as a fraction across samples.
- **diff**: any of the above for world A minus world B, or one world under two scenarios.

## Assumptions register

Everything that must be swept, because it is where modeling opinion hides: goals per type; horizon and discount per type; conversion rates and returns to scale; contest function form; channel noise; delegation drift; planner rationality. A finding is robust if it holds across the sweep. Otherwise it is reported with the assumption it depends on.

Fixed values require reasons, including substantive assumptions held fixed for a scoped experiment. Schema-2 run records include parameters, seed, requested/executed rounds, final state, status, per-agent effective planning limits and source provenance. Unresolved records have `label: null`; partial traces contain only completed physical rounds. Shares retain unresolved records in the denominator and label them separately. One-at-a-time results are local diagnostics; random-sweep dependence tables are associations, not causal estimates. Design choices and uncertain conditions still share SPACE; separating them for paired comparisons is pending.

## Not in the model

Individual psychology beyond goals and horizon. Physical detail of the world beyond resource stocks and flagged transitions. Language. Anything a rediscovery case has not yet forced in.

## Status

| Primitive | Engine v0 | Waits for |
|---|---|---|
| goals, capabilities, channels, horizon, discount | implemented | |
| beliefs, level 0 and 1 | implemented | level 2 or learned: A1 |
| contests, ratio form | implemented in the commons | second form: A2 |
| resources with conversion | per-world only; utility transfers as a module (E8) | T2.2 |
| rules as claims | declared conduct, tested (E7); amendment by declared voters (E10) | L2 nesting when a case needs it |
| delegation with drift | goal module (E11), `worlds/control.py` | agents created mid-run |
| irreversibility | declared (terminal labels, harm flags) and computed (lock, E5) | |
| error and correction | bounded: end, keep, veto and lock of declared harms (E5) | errors in beliefs |
| selection | not yet | captured auditor |
| types with populations, mean field | not yet | T8.1 |
| modules and composition | not yet | T7.1 |
| queries: finite outcomes, one-at-a-time | implemented | |
| queries: attractor detection | not yet | evidence of convergence on a case |
| queries: goal-free force/prevent thresholds over terminal labels, bounded T | implemented | |
| queries: lock-in and correction over declared harms, including authority (`worlds/authority.py`) | implemented, bounded T and T' | |
| rules as claims: self-enforcement, coalition and externalizing departures | implemented, one-shot, bounded depth | learned beliefs |
| side payments, public records, amendment (modules over any world) | implemented (E8, E9, E10) | budgets, contracts, private memory |
| first real scenario (frontier AI, owner's scope) | `worlds/frontier.py` | AI systems as agents |
| queries: diff | not yet | T7.2 |

The static linter that preceded this model was removed on adoption; `DECISIONS.md` records where each of its checks went.
