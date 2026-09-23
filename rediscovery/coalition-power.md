# Coalition power: what can be forced, regardless of goals

T1.5. A query over an existing world, not a new world. Decision: `DECISIONS.md` 2026-09-23.

**Question.** Behavior runs say what agents with authored goals do. They cannot say whether a
good outcome holds because nobody *wants* to break it (deterrence) or because nobody *can*
(denial). The difference matters most when goals are unknown or drift: new entrants,
delegated agents, AI systems. Power is computable without goals, so the claim sheds the
register's most contested assumptions (goals, horizon, discount, belief level, search depth).

**Definition.** From a state, coalition C forces label X within T rounds with probability
`force(C)`: C maximizes, the complement minimizes as one coordinated adversary with full
state information, chance follows the world kernel. Alpha: C commits each round first
(its guarantee). Beta: the complement commits first (an upper bound). Randomized play lies
between; equal brackets are exact. `prevent(C) = 1 - force_beta(complement)`.
Force threshold at level p: the smallest |C| with `force_alpha >= p`. Prevent threshold:
the smallest |C| with `prevent >= p`.

**Scope and exclusions.** Finite horizon T only; no claim beyond T. Perfect state
information overstates both sides' knowledge relative to worlds with hidden state (commons
has none). The coordinated adversary is conservative: real complements may not coordinate.
Costs are ignored by construction: a coalition that can force collapse at ruinous cost to
itself still counts. That is the point (goal-free), and also a limit: power without
willingness is not a forecast. Affected parties are modeled users only; future users and
the stock's non-user dependents are excluded, as in `open-commons.md`.

## Hypotheses, stated before the runs

A feasibility probe (commons n=4, stock mode, S in {50, 20, 10}, T 2..4) ran before these
were written, to check cost. It showed one thing already: at S=10 even all four users
together cannot surely avoid collapse, but their best joint play is not "everyone low".
That observation is recorded as finding 1 below, not as a hypothesis.

H1. Deterrence, not denial. In the paid-sanction baseline (`confiscation_to=sanctioners`),
sanctions move wealth between users but never return resource to the stock. Expected:
sanction capability changes no force or prevent value. This follows from reading the
kernel, so it is a consistency check of the query, not a finding.

H2. Unpaid (stock-return) sanctions give denial. Expected: with `confiscation_to=stock`,
some coalition prevents collapse at states where, with sanctions off, it cannot.
Contradiction: identical prevent values with sanctions on and off.

H3. One-person fragility precedes collapse. Along the baseline behavioral trajectory
(collapse at round 17), expected: a single user can force collapse within T=3 with
probability 1 for several rounds before the collapse, while the other three cannot surely
prevent it. Contradiction: the force threshold stays above 1 until the collapse round.

H4. Designs trade motivation against protection. Behavior runs found that paid sanctions
motivate enforcement and unpaid ones do not (`open-commons.md`, finding 2). Expected under
H1/H2: the paid design, which motivates, gives no denial; the unpaid design gives denial
that the planner's agents do not use. Contradiction: some state where the paid design's
prevent threshold is lower than the unpaid design's.

H5. Goal-invariance. Power values are identical across horizon, discount, k, prior,
search_depth and sanction_cost. A difference is an implementation bug.

## Engine findings
