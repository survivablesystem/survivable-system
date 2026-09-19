# Tasks

Ordered. Claim with `[claimed: name, date]`, finish with `[done: name, date]`. Each task names what forces it and the acceptance line. Add at the end, or insert with a reason. Owner-level design decisions are marked ASK.

## Stage 0: skeleton  [done: Fable, 2026-09-15]

- Engine v0: World interface, level-k planner, run loop, random sweep, one-at-a-time sweep, CLI.
- Commons world with tests reproducing and correcting `rediscovery/open-commons.md`.

## Stage 1: commons, finish

- T1.1 Sparse channels. `channels` gains a structured option (ring, or each user observes m random others). Forces: finding 3, the size effect must come through observability. Acceptance: with sparse channels, sustained share falls as n grows; with full channels it does not.
- T1.2 Readiness tie artifact. Decide: leave it, or break ties toward the current action. Record in DECISIONS.md either way. Low priority.

## Stage 2: captured auditor

Forces: a resource with conversion (credibility to future income), selection (exit and entry), an information channel as a swept variable.
- T2.1 World from `rediscovery/captured-auditor.md`. Firm, k auditors, regulator. Acceptance: lenient dominates with no independent channel; with one, a boundary in (exposure probability, horizon).
- T2.2 Only if T2.1 needs it: resources and conversions in `engine/core.py`. Decision record first.
- T2.3 Engine findings into the case file.

## Stage 3: treaty without verification

Forces: goals over another agent's state, channel noise, capability that accumulates.
- T3.1 World from `rediscovery/treaty-no-verification.md`. Acceptance: no channel builds; channel plus response complies; with returns to scale a lead locks in and verification alone fails.

## Stage 4: standing army

Forces: rules as claims, contests over authority, delegation with drift, the lock-in query.
- T4.1 World from `rediscovery/standing-army.md`. Acceptance: on the ruler's exit the commander holds authority in most of the space; a written rule alone changes nothing; split command and council-controlled pay raise the threshold.
- T4.2 `engine/queries.py`: lock-in threshold, smallest coalition that can force a flagged irreversible transition, brute force for n at most 8. Acceptance: 1 for the base world, higher under the interventions.
- T4.3 Correction threshold: smallest coalition that can reverse a flagged error state.

## Stage 5: kinship and trust

Forces: goals over others' outcomes, structured channels, possibly group selection.
- T5.1 World from `rediscovery/kinship-trust.md`. Acceptance: cooperation inside kin groups without sanctions at high kin weight; none across groups without a paid enforcer; the enforcer extends it as far as its channels reach.

## Stage 6: money issuance

Forces: claims as a primitive (ASK before adding: it would unify rules, money and legitimacy), issuance capability.
- T6.1 World from `rediscovery/money-issuance.md`. Acceptance: hidden supply over-issues and acceptance collapses; visible supply constrains; several issuers with readable promises select the constrained one.

## Stage 7: composition and diff

- T7.1 Modules as functions from world to world; a case composes a base world with modules. Acceptance: the commons with and without the paid-sanction module as two named cases.
- T7.2 `diff`: two cases or one under two scenarios; report which shares and thresholds moved.

## Stage 8: scale

- T8.1 Types with populations: a world declares types and counts; the engine expands them. Mean field only when exact planning is too slow on a case that needs large n. ASK before mean field.
- T8.2 Performance: profile `step` and `evaluate` before any world with more than a dozen agents. The commons one-at-a-time run takes three minutes.

## Stage 9: first real scenario

- T9.1 Frontier AI. Labs, regulator, state, AI systems as a type whose capability grows per round. Modules: disclosure channel, compute attestation. Question: which coalitions can force lock-in, and does either module change that. ASK on the scenario's boundary before building.

## Anytime

- A1 Beliefs beyond level 1 (full re-planning, level 2, learned) only when a case's known outcome fails at level 1. Record the case.
- A2 Contest function family: add a second form only when a case's outcome depends on the form.
- A3 Report format: one screen, robust first, then dependent, then not modeled.
