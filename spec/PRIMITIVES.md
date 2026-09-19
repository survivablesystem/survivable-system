# Primitives, v0.1

The model. Adopted 2026-09-15 (`DECISIONS.md`). The status table at the end says which parts the engine implements and which wait for a case that forces them.

The tool simulates a world of agents and asks what structures emerge. Nothing about how the world fails is written into it. Failure chains are outputs. The test of the primitives is `rediscovery/`: outcomes history already knows must emerge without being coded.

## One object: the agent

The same object at every scale. A person, a firm, a court, a state, an AI system, a civilization. An institution is an agent made of agents.

```
agent:
  goals:        preference over world states. Ordinal. May diverge from every other agent's.
  capabilities: actions available. Base set: convert, open/close channel, contest,
                delegate, propose rule, act on the world.
  information:  channels into this agent (whom it observes), noise per channel,
                and beliefs about what other agents will do. Beliefs exist with or
                without a channel; they decide whether coalitions form. Beliefs are
                level-k (engine/core.py): level 0 expects repetition and cannot hold
                a norm; level 1 expects a response and can.
  resources:    vector over resource kinds.
  horizon:      how far ahead it plans and how it discounts. A parameter, not a behavior.
```

No behavior is scripted. Each round an agent plans from its goals, capabilities, information and horizon, and acts. The planner belongs to the engine, not the model. Its rationality is a swept assumption.

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
                 Hypothesis, untested: rules, money and legitimacy are one primitive, the
                 claim, worth what others are believed to honor. rediscovery/money-issuance.
delegation:      an agent may create a sub-agent, granting capability and setting its goal.
                 The set goal drifts from the intended one by a swept amount.
irreversibility: flagged transitions that cannot be undone. Catastrophe is an irreversible
                 transition to a state most agents' goals rank lowest.
error:           beliefs can be wrong. A correction moves the world back after an error. It
                 needs a detector with a channel, an actor with capability, and an erring agent
                 that cannot win the contest to block it.
selection:       agents whose resources reach zero exit. New agents enter by delegation.
                 Populations evolve. (Forced by rediscovery/captured-auditor.)
time:            discrete rounds.
```

## Scale

Agents are types with populations, not individuals. Many identical agents are a mean field. A civilization is a few dozen types across a few levels, and the same engine runs at every level.

## Modules

A module is an intervention on the world or on a set of types: change a conversion rate, add or remove a channel, add a rule at a level, add an amendment rule, restrict an action set, flag a transition irreversible, create a type. Composition is the union of interventions on one world. Interactions emerge because everything acts on the same dynamics.

AI advancement is a module: a new type whose capability grows per round, plus shifts in conversion rates (information to capability becomes cheap; capability gains returns to scale).

## Queries

For a composed world, under a sweep over the assumptions register:

- **lock-in threshold**: smallest coalition that can force an irreversible transition regardless of others. Want high.
- **correction threshold**: smallest coalition that can reverse a detected error regardless of others. Want low.
- **attractors**: where the world settles, and the share of sampled assumptions under which it settles in each. The share landing in a catastrophic attractor is the only probability this tool reports.
- **coalition power**: can coalition C force outcome X. Answered per sample, reported as a fraction across samples.
- **diff**: any of the above for world A minus world B, or one world under two scenarios.

## Assumptions register

Everything that must be swept, because it is where modeling opinion hides: goals per type; horizon and discount per type; conversion rates and returns to scale; contest function form; channel noise; delegation drift; planner rationality. A finding is robust if it holds across the sweep. Otherwise it is reported with the assumption it depends on.

## Not in the model

Individual psychology beyond goals and horizon. Physical detail of the world beyond resource stocks and flagged transitions. Language. Anything a rediscovery case has not yet forced in.

## Status

| Primitive | Engine v0 | Waits for |
|---|---|---|
| goals, capabilities, channels, horizon, discount | implemented | |
| beliefs, level 0 and 1 | implemented | level 2 or learned: A1 |
| contests, ratio form | implemented in the commons | second form: A2 |
| resources with conversion | per-world only | captured auditor, T2.2 |
| rules as claims, nested levels | not yet | standing army, T4.1 |
| delegation with drift | not yet | standing army |
| irreversibility | implemented (collapse) | |
| error and correction | not yet | T4.3 |
| selection | not yet | captured auditor |
| types with populations, mean field | not yet | T8.1 |
| modules and composition | not yet | T7.1 |
| queries: attractors, one-at-a-time | implemented | |
| queries: lock-in, correction, coalition power, diff | not yet | T4.2, T4.3, T7.2 |

The static linter that preceded this model was removed on adoption; `DECISIONS.md` records where each of its checks went.
