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

Artifact: `evidence/coalition-power.json`, clean source `d7fcd10`, 6 min 45 s. Commons n=4
unless stated; T=3; levels p=1 and p=0.5; stock grid 6..100; hi_mult 2/4; r 0.3/0.5/0.8.
Reproduce with `python -m tests.power_study` at that revision. Every tested table was
symmetric across same-size coalitions (checked, not assumed).

| Hypothesis | Result |
|---|---|
| H1 paid sanctions add no power | holds at all 66 paid states: identical to sanctions off, values all 0 or 1 |
| H2 unpaid sanctions give denial | holds: e.g. S=20, hi 2, r 0.5, one user prevents collapse with 0.64 against the other three (paid: 0) |
| H3 one-person fragility for several rounds before collapse | contradicted at T=3: a single user can force collapse only at round 16, one round before the doomed round 17. The irreversible step came earlier and differently; see finding 2 |
| H4 motivation versus protection | holds on the grid: unpaid prevent >= paid and unpaid force <= paid at every state and size; behaviorally unpaid collapses at 7, paid at 17 |
| H5 goal-invariance | holds (`tests/test_power.py`) |

1. **The irreversible point is not the flagged transition.** Users cannot take less than
   `lo` (80% of maximum sustainable yield, split n ways). Below S* = K(1 - sqrt(0.2))/2 =
   27.64, regrowth under everyone's minimum take is below demand, so collapse is certain
   whatever anyone does, unless harvest returns to the stock. S* depends only on the fixed
   `lo_frac`, not on r or n. Twelve-round queries confirm it at S = 20, 23.6 and 26
   (unavoidable with probability 1); 27.5 needs longer than 12 rounds; 28 exceeded the work
   cap. The `collapsed` label at S_min = 5 lags the real point of no return.

2. **In the paid baseline the irreversible step was taken at round 13 by the whole group,
   the only coalition able to take it, while any one user could have blocked it.** Rounds
   11-13 (S 31-33): force threshold 4, prevent threshold 1. At round 13 all four chose the
   high take (the depletion cycle), S fell from 32.6 to 23.6 < S*, and from round 14 on the
   grand coalition cannot avoid collapse within 12 rounds. The label fires at round 17.
   The depth-2 planner never saw it: the loss lies beyond its search. A careful reader of
   the behavioral trace sees a slow decline and a collapse at 17. The power profile shows a
   unanimous, individually blockable, irreversible choice four rounds earlier. This is the
   case file's first finding a careful person would likely miss.

3. **Paid sanctions are pure deterrence.** Sanction capability changes no power value in
   the paid design (H1); the game there is a count: collapse within T iff at least k users
   take high, with force threshold k and prevent threshold n+1-k at every tested state.
   Every protection the paid design shows in behavior rests on users caring about wealth.
   A user with other goals (spite, a rival's instruction, a misaligned objective) meets no
   physical resistance. This follows from the kernel; the query makes it explicit and
   quantifies where it bites: with hi_mult 4, one user can force collapse within 3 rounds
   from any stock at or below 30 (r 0.5).

4. **The design with more denial collapses sooner in behavior.** Unpaid (stock-return)
   sanctions weakly dominate paid in power at every tested state, but its agents do not
   sanction (second-order free riding, `open-commons.md` finding 2) and collapse at round
   7 versus 17. Neither tested design provides both motivation and protection. A split
   confiscation rule is the obvious untested candidate; it is a design question for a later
   task, not a conclusion here.

5. **Menu artifact exposed by a goal-free witness.** Under unpaid sanctions at S=10, the
   whole group's best preventive first round is three users taking high and one sanctioning
   them (prevention 0.22 versus 0 for everyone low); at S=15, two and two (0.77). Being
   confiscated is the only way to harvest below `lo`. This is a wrong-world signal, not a
   behavior: the commons lacks a restraint action. T1.6.

6. **Randomization matters only where contests do.** Paid brackets are all closed. 47 of
   330 unpaid values have alpha < beta (largest gap 0.17); seven p=0.5 thresholds are upper
   bounds because a smaller coalition's bracket straddles p.

Scope: n <= 4, T <= 4 exact (12 for one grand-coalition check). Thresholds shift with T as
expected: paid S=40 needs no coalition at T=3 but 4 users at T=4. Nothing here is a claim
beyond T, about larger populations, or about real fisheries. Costs of forcing or
preventing are ignored by construction. Cost: a full 16-coalition table takes 0.2-2 s at
T=3 and up to 13 s at T=4; exact enumeration grows with menus^n per stage and with
distinct reachable states per round, so larger worlds need symmetry reduction (T8.1).

## Behavior beside power (T1.7, 2026-09-23)

`python -m engine worlds.commons --trace --profile 3 --target collapsed` prints, beside each
played round, the smallest coalitions that could force or prevent collapse within 3 rounds
from the state the round started in. `FRAGILE`: one agent could force it with certainty,
so whatever held, goals held it. `SEALED`: nobody can prevent it. Artifact
`evidence/power-profiles.json`, clean `81bece6`, 2 min; `python -m tests.profile_study`.

| Run (defaults, restraint on unless stated) | Outcome | Fragile rounds | Sealed |
|---|---|---|---|
| paid | collapse 17 | none | never |
| unpaid | collapse 7 | none | never |
| no sanction | collapse 5 | none | never |
| paid, no restraint (T1.5 world) | collapse 17 | 16, 17 | 17 |
| rest-and-raid survivor (n=2) | survived 30 | 12 of 30 (every rest round) | never |

7. **The last step to collapse was compliance.** With restraint on, the paid baseline
   collapses at round 17 with all four users taking the *low* take, the take sanctions
   enforce, from S=9.7. Three resting users would have prevented it (prevent threshold 3).
   The sanction rule targets takes above one's own, so it protects the quota, not the
   stock: at low stock the enforced norm is itself the collapse. A fixed-quota norm is a
   design choice this world hard-codes; a stock-dependent norm is untested.
8. **Survival can be fragile in every other round.** The only restraint-dependent survivor
   rests whenever the stock nears the brink; at each rest round a single user could force
   collapse within 3 rounds. Its 30-round survival is goal-held, not denied.

## Population scale by declared symmetry (E2, 2026-09-23)

Decision `DECISIONS.md` 2026-09-23 (E2). Commons users are declared exchangeable
(`commons.types`); invariance of the kernel under permuting their actions and equality of
reduced and full tables at n=3 are tested. Artifact `evidence/scale.json`, clean
`dc8a981`, 4 min; `python -m tests.scale_study`. Restraint on, no sanctions unless
stated, n from 2 to 20. Exact at n=20 and T=3 in 154 s (before: n <= 4).

| S, T | force threshold by n (2, 4, 6, 8, 10, 12, 16, 20) | prevent threshold |
|---|---|---|
| 20, 2 | 2, 3, 5, 6, 8, 9, 12, 15 | 1, 2, 2, 3, 3, 4, 5, 6 |
| 30, 3 | 2, 4, 6, 7, 9, 11, 14, 18 | 1, 1, 1, 2, 2, 2, 3, 3 |

9. **Power depends on the fraction of users, not their number.** At S=20 forcing
   collapse within 2 rounds takes three quarters of the users at every size; force and
   prevent thresholds always sum to n+1 in this deterministic game, so the preventing
   share falls from a half toward a quarter only through integer granularity. This rests
   on the declared scaling of each user's take (`lo_frac` of maximum sustainable yield,
   divided by n). A world where individual takes do not shrink with n would differ; that
   is where a size effect would have to come from, not from numbers alone.
