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
