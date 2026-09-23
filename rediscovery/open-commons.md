# Rediscovery: open-access commons

**Hypothesis, evidence review pending.** Monitoring and sanction incentives may change depletion in a shared resource. The references to Hardin and Ostrom below are the original paper intuition, not a verified account of their findings. No universal necessity of sanctions, paid monitors or small groups is established here.

Competing explanation: the results may depend on constant-action planning, identical agents, the restricted action set or the chosen stock margins. Disconfirmation: survival without the proposed necessary condition, collapse with it, or an absent/reversed size effect. Preserve those outcomes rather than tuning them away.

Affected parties: modeled users receive yield and pay sanction costs. Future users, outsiders, nonhuman effects and entry/exit are excluded. A stock-survival label is not a welfare measure.

## Setup in primitives

```
types:
  user (many, n):  goals: own yield over horizon. capabilities: take x from stock; observe
                   others if a channel exists; sanction; propose an L1 body.
world:
  stock S regenerates at rate r up to a cap. Below S_min it collapses. Irreversible.
rules: none at start. Creating an L1 body is an action available to users.
channels: all observe S. Whether users observe each other's x is the swept variable.
```

## Original paper conjecture (not an empirical result)

No channels between users. Each user's best response to any belief about the others is the maximum take, because others' takes are unobserved and unpunishable. S falls below S_min. Hardin.

Channels between users, sanction capability, small n. A user considering a large take expects detection and a sanction coalition. Whether the coalition forms depends on each member's belief that the others join, and with channels that belief is grounded. A cooperative equilibrium exists when the horizon is long relative to r. Users may create an L1 body to formalize sanctions, which lowers the per-round cost of enforcing. Ostrom.

The boundary depends on n, horizon, channel noise and sanction cost. The engine maps it.

## Emerges?

The tested configurations produce collapse or survival through the run limit. They support a role for sanction incentives within this world, not a universal mechanism. The conjecture about small groups remains untested with sparse channels. See engine findings and the scope correction below.

## Gap found

Beliefs about other agents' actions must be first-class in the agent's information, not derived only from channels. A user with no channel still holds a belief, and that belief decides whether a coalition forms. Moved into `spec/PRIMITIVES.md`.

## Engine findings (v0, 2026-09-15, `worlds/commons.py`)

Baseline: 4 users, horizon 12, discount 0.9, all channels, sanction capability, cost 0.1 of the low take, double high take, level-1 beliefs, confiscation to sanctioners. Sustained in every seed. Moved one at a time (`python -m engine worlds.commons --oat`):

| Moved alone | Outcome | Reading |
|---|---|---|
| channels none | collapse | detection needed |
| sanction off | collapse | response needed |
| horizon 1 | collapse | a one-round planner cannot anticipate a response |
| beliefs level 0 | collapse | finding 1 |
| confiscation to stock | collapse | finding 2 |
| sanction cost 1.0 of the low take | collapse | boundary between 0.3 and 0.5 in separate probes |
| n = 2 or 12 | sustained | finding 3 |
| all start at the high take | sustained | finding 6 |
| all start ready | sustained | |
| high take quadruple | sustained | anticipated response scales with the coalition |
| horizon 20, discount 0.8 or 0.99, regrowth 0.3 or 0.8, cost 0 | sustained | |

The one-at-a-time run takes about three minutes; the n=12 and horizon=20 points dominate.

1. **Level-0 beliefs cannot hold a norm, established or not.** A level-0 agent expects others to repeat. Standing ready to sanction has no value to it when nobody is defecting, so it drops readiness; next round nobody expects a sanction, so defecting looks free, and everyone defects at once. With everyone at the high take there is no one above anyone to sanction. Starting from an established norm changes nothing. Level 1 holds the norm because readiness is chosen for what it deters.
2. **Second-order free riding.** With confiscated takes returned to the stock, nobody sanctions at any group size from 2 to 10, at any cost down to 0.02 of the low take. The benefit is a shared stock that only bites near collapse, beyond a 12-round horizon. With confiscated takes going to the sanctioners, sanctioning pays directly and the norm holds. The paper derivation had this wrong. Monitors who keep part of the fine are not a detail of Ostrom's cases; in this model they are the mechanism.
3. **No size effect in the tested fully observed configurations.** With every user seeing every other and paid sanctioning, ten survive through the run limit as well as four. Sparse channels are one possible explanation for a size effect, not a demonstrated or necessary one. T1.1 must permit absent and reversed effects.
4. **A run on the commons.** Under unpaid sanctioning with a triple high take, the best response to one defector is to defect too: one sanctioner at even odds cannot save the stock, so the others grab what remains.
5. **Two artifacts removed.** Harvesting before regrowth made the maximum sustainable yield a knife-edge that tipped into decline with everyone cooperating; growth now comes first and the low take sits at 80% of the maximum. Breaking sanction-target ties by id let lower ids defect for free once a higher id had; sanctioners now act against every visible defector.

6. **Cooperation restarts from total defection when sanctioning pays.** With everyone at the high take, an agent that drops to the low take is below all the others and can sanction every one of them. The bounties are worth more than the high take, so it switches; the others, now sanctioned, comply. Under unpaid sanctioning cooperation never starts from this state. So paid sanctioning is what makes a norm start, not only what keeps it.

A cosmetic artifact remains: at level 1, readiness alternates on and off each round because standing ready and not are tied in value when nobody defects, and ties go to the earlier-listed action. It does not change any outcome.

## Not yet shown

Lock-in and correction thresholds (TASKS.md stage 4). Creation of an L1 body: no rule exists in this world, only the sanction action. Sparse channels.

## Evidence audit (2026-09-19, T0.1)

The 2026-09-15 table is retained as a legacy report; its raw artifacts were not saved. "Sustained" in that report means finite survival, not a demonstrated attractor. Its statements about norms and paid sanctions apply only to tested configurations under this planner. Four seeds at a baseline do not establish robustness across the register.

A counterexample to the old label: DEFAULTS plus `horizon=1, sanction=False`, seed 0, gives `survived` after one round and `collapsed` at round five. Regression: `tests/test_records.py::test_finite_survival_is_not_convergence`. Reproduce with `python -m engine worlds.commons --trace --rounds 30 --seed 0 --fix horizon=1 sanction=false --json`.

`S0_frac`, `S_min_frac` and `lo_frac` are substantive fixed assumptions, not unit choices; FIXED_REASONS now says why they are fixed and what remains untested. New artifacts record raw seeds, parameters, duration and source provenance. Sorted channel iteration makes the assignment of stochastic contest draws stable across Python hash seeds; seed-specific trajectories from the original unordered implementation are not promised to match.

T1.0 (`planner-audit.md`) finds information leaks, a directed-observation error, and decision reversals from constant actions and mean transitions in constructed cases. The information paths are repaired; the commons declares stock, wealth, topology and utilities known, and replaces unobserved action history with its prior. Existing full/no-channel regressions remain checks of this approximation, not evidence that their conclusions survive adaptive or branch-aware planning. T1.3 must compare them.

## Replacement findings (2026-09-19, T1.3)

`planner-replacement.md` records matched runs, arithmetic references, per-agent action-value probes and cost. The current default searches only depth 2 of the desired 12 rounds; this cap is explicit. The former favorable baseline now follows high / low+sanction / low without sanction and collapses at round 17, across seeds 0..3. Old horizon 2 also collapses at 17, while old horizon 12 survives 30: this is not a same-depth disproof of the old planner's cooperation result. The prior level-0 claim is also duration-sensitive: it survives 12 in both versions but fails the 30-round regression.

At n=4, depths 1/2/3 all collapse at 17; at n=2, collapse occurs at 5/7/9. At n=10, depth 1 collapses at 17 but depths 2/3 exceed the work budget. Unresolved searches say nothing about physical survival or a population size effect. Exact branch enumeration fixes the small risk diagnostic, but currently limits deeper/larger-world conclusions. Record the limit; do not tune the world or count incomplete searches as an outcome.

The old claim that tie alternation does not change outcomes was not a general result. T1.2 must measure its effects under the replacement. Future people and excluded groups remain absent, and no institutional protocol is validated by this world.

## Power findings (2026-09-23, T1.5)

`coalition-power.md`. Goal-free: the real point of no return is S* = 0.276K (fixed by `lo_frac` and the absence of any take below `lo`), not S_min. In the paid baseline all four users took the step below S* at round 13, when any one of them could have blocked it; collapse became unavoidable then and was labeled at 17. Paid sanctions change no power value: the norm they sustain is deterrence only. Unpaid sanctions give denial the agents do not use. The menu lacks a restraint action (T1.6).

## Restraint semantics (T1.6, 2026-09-23), stated before building

Problem: the menu has no take below `lo`, so collapse is sealed at S* = 0.276K and the
only way to harvest less is to be confiscated (`coalition-power.md`, findings 1 and 5).
Real users can stop taking. The absence looks like a wrong world, not an assumption
anyone chose.

Simplest change: register option `restraint: [False, True]`. True adds one action,
`(rest, no sanction)`, taking nothing. A resting user cannot sanction: the existing rule
targets takes above the sanctioner's own, and letting a non-taker police every taker
would change who is sanctionable, a second semantic change. That alternative stays
untested and declared. `restraint=False` is the previous world exactly.

Expected, before runs:
- R1 (power, consistency): with rest, the whole group prevents collapse from any
  non-collapsed stock (regrowth is positive on (0, K)). The point of no return moves to
  S_min. Follows from the kernel.
- R2 (power): rest only helps the side avoiding collapse, so every force value can only
  fall and every prevent value only rise. Expected to matter below S*: prevention by a
  minority becomes possible where the paid design had none. Contradiction: any force value
  rises (an implementation error), or no value changes anywhere below S*.
- R3 (behavior): depth-2 agents do not rest in the baseline; resting costs yield now and
  pays beyond the search depth. Expect collapse still at round 17 with the same trace.
  Contradiction: rest chosen, or survival through 30 rounds.
- R4 (behavior, the question that matters): does restraint appear anywhere in the
  one-at-a-time neighborhood (depth 3, low stock, unpaid)? No prediction; record it.

Default: decide after runs. If R1 holds, the world with restraint is the more faithful
baseline; old results stay reproducible at `restraint=False` and at their revisions.

### Restraint findings

Artifact: `evidence/restraint.json`, clean source `4175ae0`, 3 min. Reproduce with
`python -m tests.restraint_study` at that revision. 17 one-at-a-time variants x seeds 0-2,
and 60 random register samples (seed 616), each run with restraint off and on at the same
parameters and seed; power maps at T=3 for paid and unpaid designs.

| Expectation | Result |
|---|---|
| R1 whole group can always prevent | holds: with rest, prevent(everyone) = 1 at every tested stock; no stock is sealed |
| R2 rest only helps prevention | holds at every state and coalition; paid S=20: one user could force collapse, now three are needed; paid S=30: one user prevents |
| R3 baseline agents do not rest | holds: 48 of 51 neighborhood runs have identical traces and no rest; only n=2 rests (twice, at the brink) and collapses one round later |
| R4 restraint anywhere | 1 of 60 random samples survives only with restraint; 1 becomes unresolved (larger menu, same work cap); 53 collapse either way, 4 unresolved either way, 1 survives either way |

1. **Collapse is now a choice, not a physical necessity.** With restraint the commons has
   no sealed state short of S_min, and small minorities can prevent collapse over wide
   stock ranges. The planner's agents still collapse it at the same rounds. Every
   collapse in the neighborhood is a failure of behavior under the declared goals and
   search depth, not of capability.
2. **Restraint is used only as a brink tactic.** Where agents rest, they rest when the
   stock nears S_min and then take high: at n=2, rest at S=7.7, recover to 11.2, both take
   high, collapse. The one survivor (n=2, no channels, no sanctions, unpaid, depth 3,
   horizon 4) runs a rest-and-raid cycle between S=12 and 30 for 30 rounds: finite
   survival held near the edge, not a sustained norm.
3. **Search depth is the binding behavioral assumption.** Resting pays over more rounds
   than depth 1-3 can see. The archived old planner at horizon 12 survived the baseline
   (`planner-replacement.md`). Behavioral conclusions about restraint in this world are
   conclusions about a myopic planner. T1.8.

Decision: restraint is now the default (`DEFAULTS["restraint"] = True`). The world without
it had a wrong menu (findings 1 and 5 of `coalition-power.md`). The baseline trace is
unchanged; `restraint=False` remains in the register and reproduces the earlier world, and
`tests/power_study.py` pins it so T1.5 evidence still reproduces (33 of 33 map entries
rechecked). Resting sanctioners remain untested.

## Deeper exact search (T1.8, 2026-09-23), stated before the depth-4/5 runs finished

Measured first: at the initial state a depth-4 decision needs 25,370 work entries (cap
20,000), depth 5 needs 481,531 (7 s). The cap, not the method, kept depths 4-5 out of
reach. Simplest step: search deeper exactly under a larger declared cap; no tail value.

- D1: deeper agents break the high/sanction/low depletion cycle and the baseline survives
  30 rounds (the archived horizon-12 planner did). Contradiction: collapse at 17 at
  depths 4 and 5.
- D2: with restraint, deeper agents rest at low stock. Contradiction: no rest actions.

### Depth findings

Artifact `evidence/depth.json`, clean `7c1b92d`, 10 min; `python -m tests.depth_study`
(study cap 2,000,000 entries; the world's default cap is unchanged).

| Depth | Restraint | Seeds | Outcome |
|---|---|---|---|
| 1-3 | on or off | 0-2 | collapse 17 (T1.3, T1.6) |
| 4 | on | 0, 1 | collapse 22; all four rest once (round 17), then resume the cycle |
| 4 | off | 0, 1 | collapse 18 |
| 5 | on | 0 | unresolved after round 1 (contested state exceeds 2,000,000) |
| 5 | off | 0 | collapse 17 (401 s) |

D1 contradicted at every completed depth; D2 holds only weakly (one rest round at depth
4). Deeper exact search delays collapse by at most five rounds and not monotonically
(depth 4 off: 18, depth 5 off: 17). The high / sanction / low cycle is profitable inside
any window of 1-5 rounds; its cost lies further out. The archived horizon-12 planner's
survival came from 12-round constant-action rollouts, not from anything exact search to
depth 5 reproduces. Behavioral conclusions in this world are therefore conclusions about
planners that look at most about five rounds ahead. Longer reach needs an explicit,
swept continuation-value assumption; none is adopted here (A1).

## Opponent model (A1, 2026-09-23)

`evidence/opponent-models.json`: eight neighborhood configurations under `others` react
and plan (seed 0, 30 rounds). Every configuration that collapsed under react collapses
under plan, and r=0.3 survives under both; timing moves (baseline 17 to 21, depth 3 17 to
22, n=2 8 to 7). Commons conclusions are qualitative in collapse, not in timing.

## Rules as claims (E7, 2026-09-23)

`evidence/rules.json` (clean `a40ea9d`), `python -m tests.rules_study`; one-shot departures,
states within 2 rounds, coalitions up to 2, transferable utility for coalitions.
Grid: n=3, confiscation {stock, sanctioners} x sanction cost {0.1, 0.5} x high take
{2, 4} x discount {0.8, 0.95}, depth 3.

- `quota` (low take, no sanctions) fails in 16/16: a single high take pays.
- `quota and sanction` holds in 8/16, exactly the cells with high take 2x; at 4x the
  expected third that escapes confiscation (two sanctioners) still beats the low take.
  Sanction cost and where confiscations go never matter on the path, because nobody
  defects there. Where it fails, any two users gain by taking high together and the
  depletion falls on future users and stock-dependent others (no agents).
