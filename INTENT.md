# Intent

This file is the measure for every change here. If a change does not serve the intent below, it does not go in, however good it is on its own. If the intent is wrong, change this file first, with a decision record, then the rest.

## Why this exists

Civilizational risk rises with the power of what we build, and the structures meant to contain it are designed one piece at a time. Each piece looks fine. The cost lands on whoever was not in the room, and nobody chose the harm. The failures that matter most are chains: surveillance enables concentration, concentration removes correction, uncorrected error becomes irreversible. No single piece shows the chain.

Survivable System is a simulation in which such chains emerge. Agents with goals, capabilities and information act inside architectures of rules and channels. No behavior is scripted. The tool asks what structures form, who ends up able to force irreversible outcomes, who can still correct errors, and how a proposed institution or a change in technology moves those answers. The purpose is to find civilizational-scale architectures that lower existential risk, and to make every such proposal checkable by anyone.

## What may change

The core is the purpose and the evidence standards: make externalized harm and irreversible power visible, compute rather than prescribe choices, expose assumptions, permit disconfirmation, and keep proposals checkable. The current simulation architecture, agent abstraction, planner, interfaces and task order are provisional means to that end.

When a case reveals a consequential limitation, compare extending the current design with replacing it. Expand or rebuild when that yields a more general, capable tool with a simpler internal model. Existing code and sunk effort are not reasons to preserve a worse design. Record the limitation, alternatives, migration and discriminating tests; remove obsolete mechanisms rather than accumulating special cases. Generality must be demonstrated across cases, not promised.

## Current approach

- One object, the agent, at every scale: person, kin group, firm, court, state, AI system, civilization. Institutions are agents made of agents.
- A world of resources, contests, nested rules, delegation, irreversible transitions, error and selection. `spec/PRIMITIVES.md`.
- A planner that selects among actions under explicit assumptions about goals and beliefs. The current planner compares constant-action rollouts, not all adaptive plans. Choices are computed; action semantics and planner assumptions remain authored and contestable.
- Modules: interventions on a world. Composition is the union of interventions, so interactions emerge.
- Queries: where a world settles, which coalitions can force lock-in, which can correct, and how that differs between designs.
- A rediscovery suite: sourced hypotheses about known systems, competing explanations and counterexamples. Reproducing an outcome is evidence of expressiveness, not proof of its cause or of the primitives.

## What it is not

- Not a forecast. It reports shares of a sweep over stated assumptions, never a probability of the world.
- Not a global-optimum certificate. Compare designs across explicit objectives, model alternatives and assumptions. Report tradeoffs and failure conditions; no preferred institution is an acceptance criterion.
- Not a story generator. A chain written into a setup is not a finding.
- Not a platform. Python files and a command line until a need proves otherwise.
- Not validated by a clean run. The dominant failure is a wrong world: a missing type, channel or conversion. Nothing catches what is not modeled.

## Tests for any change

Core changes (this file, `spec/`, `engine/`) must pass all six. Worlds, cases and tests must pass the last four.

1. **Simplest that works.** Can existing mechanisms express the case adequately? If not, compare a coherent extension with replacement. A demonstrated limitation can justify greater power or a rebuild; avoid both unnecessary complexity and artificial limits imposed to preserve the prototype.
2. **Nothing scripted.** Behavior comes from goals, capabilities, information and the planner. A world that says "agents do X when Y" has a bug.
3. **Every assumption swept or declared.** Each number is in the world's register and swept, or fixed with a stated reason. Record source, seeds and duration. Robustness is relative to the tested space and sampling rule; repeated seeds and one-at-a-time endpoints do not establish it alone.
4. **Emerges, not asserted.** State the expected outcome and what would contradict it before building. If the setup contains the conclusion, the case is void. Failed expectations require diagnosis, not automatic expansion of the model.
5. **Makes externalization visible.** Does it help find who bears a cost, and who can force what on whom? Name affected groups, including people without agency in the model and future people; declare exclusions. Do not hide severe harm behind majority preference or a single aggregate score.
6. **Finds something a careful person would miss.** If the tool only confirms what the modeler already believed, it is not yet doing its job. The first such finding on every case is named in the case file.

## Priorities when tests conflict

Simple beats complete. Emergent beats impressive. A negative result that holds beats a positive design that might. A rediscovery case whose outcome emerges for a reason the paper derivation got wrong is the best result a session can produce.

## How we know it is working

- Rediscovery cases have reproducible outcomes, scoped claims and preserved counterexamples without case-specific behavior scripts.
- The engine finds, on a real design, a chain its authors did not see.
- New cases reuse coherent mechanisms; expansions earn their complexity and replacements retire obsolete ones. Spec size is a diagnostic, not a ceiling on capability.
- Two agents work here in alternating sessions from the files alone.
- Protocol proposals specify adoption, enforcement, challenge, amendment and exit, and earn support through reversible trials as well as modeling. The present engine does not validate such a protocol.

## Limits stated up front

A wrong world is invisible. Goals, horizons and the contest function are where opinion hides, and they must be swept. Legitimacy, enforcement and belief are the hardest parts of real systems and the most likely to be modeled wrong. Knowing what would work is not making it happen.
