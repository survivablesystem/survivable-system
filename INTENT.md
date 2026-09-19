# Intent

This file is the measure for every change here. If a change does not serve the intent below, it does not go in, however good it is on its own. If the intent is wrong, change this file first, with a decision record, then the rest.

## Why this exists

Civilizational risk rises with the power of what we build, and the structures meant to contain it are designed one piece at a time. Each piece looks fine. The cost lands on whoever was not in the room, and nobody chose the harm. The failures that matter most are chains: surveillance enables concentration, concentration removes correction, uncorrected error becomes irreversible. No single piece shows the chain.

Survivable System is a simulation in which such chains emerge. Agents with goals, capabilities and information act inside architectures of rules and channels. No behavior is scripted. The tool asks what structures form, who ends up able to force irreversible outcomes, who can still correct errors, and how a proposed institution or a change in technology moves those answers. The purpose is to find civilizational-scale architectures that lower existential risk, and to make every such proposal checkable by anyone.

## What it is

- One object, the agent, at every scale: person, kin group, firm, court, state, AI system, civilization. Institutions are agents made of agents.
- A world of resources, contests, nested rules, delegation, irreversible transitions, error and selection. `spec/PRIMITIVES.md`.
- A planner that gives each agent its best action from its goals and beliefs. Behavior is computed, never written.
- Modules: interventions on a world. Composition is the union of interventions, so interactions emerge.
- Queries: where a world settles, which coalitions can force lock-in, which can correct, and how that differs between designs.
- A rediscovery suite: structures whose outcomes history knows. The primitives are right when those outcomes emerge uncoded.

## What it is not

- Not a forecast. It reports shares of a sweep over stated assumptions, never a probability of the world.
- Not a story generator. A chain written into a setup is not a finding.
- Not a platform. Python files and a command line until a need proves otherwise.
- Not validated by a clean run. The dominant failure is a wrong world: a missing type, channel or conversion. Nothing catches what is not modeled.

## Tests for any change

Core changes (this file, `spec/`, `engine/`) must pass all six. Worlds, cases and tests must pass the last four.

1. **Simplest that works.** Can it be expressed with what exists? A new primitive, parameter or feature needs a rediscovery case or scenario that cannot be expressed without it. Removal is as welcome as addition.
2. **Nothing scripted.** Behavior comes from goals, capabilities, information and the planner. A world that says "agents do X when Y" has a bug.
3. **Every assumption swept or declared.** Each number is in the world's register and swept, or fixed with a stated reason. A finding is robust across the sweep or reported with what it depends on.
4. **Emerges, not asserted.** A case's known outcome must follow from its setup. If the setup contains the conclusion, the case is void.
5. **Makes externalization visible.** Does it help find who bears a cost, and who can force what on whom?
6. **Finds something a careful person would miss.** If the tool only confirms what the modeler already believed, it is not yet doing its job. The first such finding on every case is named in the case file.

## Priorities when tests conflict

Simple beats complete. Emergent beats impressive. A negative result that holds beats a positive design that might. A rediscovery case whose outcome emerges for a reason the paper derivation got wrong is the best result a session can produce.

## How we know it is working

- Every rediscovery case emerges without a case-specific mechanism.
- The engine finds, on a real design, a chain its authors did not see.
- The spec stays the same size or shrinks while the world library grows.
- Two agents work here in alternating sessions from the files alone.

## Limits stated up front

A wrong world is invisible. Goals, horizons and the contest function are where opinion hides, and they must be swept. Legitimacy, enforcement and belief are the hardest parts of real systems and the most likely to be modeled wrong. Knowing what would work is not making it happen.
