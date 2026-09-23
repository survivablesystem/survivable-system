# Treaty, verification and a capability race

T3.0 evidence review, 2026-09-23. The earlier brief's claims are kept below as the paper
conjecture. Nothing here is an engine result yet.

## Question

When two parties can build capability, and a decisive lead can be turned into an
irreversible outcome, what does verification (inspection, compute attestation,
disclosure) change? Two separate questions:

- **Power (goal-free).** Can one side force an irreversible outcome regardless of the
  other? Can the other prevent it, and does the answer depend on what it can observe?
  Verification is information, so it can only change power if the preventing side's
  strategy is restricted to what it observes. The full-information query (T1.5) is blind
  to verification by construction; using it alone would put the conclusion in the setup.
- **Behavior (goal-driven).** Given goals over relative capability and welfare, do
  parties build, comply or strike, and how does that change with verification, noise,
  horizon and returns to scale? Conditional on planner reach (commons T1.8).

## Sources and evidence status

| Claim | Source | Status here |
|---|---|---|
| The Soviet Union ran a large offensive biological programme (Biopreparat) while party to the BWC, which has no inspection regime | Leitenberg, Zilinskas and Kuhn, *The Soviet Biological Weapons Program: A History*, Harvard UP 2012 | bibliographic details verified; contents cited from secondary summaries, not read here |
| Arms control is rare because monitoring must reveal enough to assure compliance but not so much as to expose security-relevant information (transparency-security tradeoff) | Coe and Vaynman, "Why Arms Control Is So Rare", *APSR* 114(2), 2020, 342-355 | verified abstract |
| Large, rapid shifts in power cause costly conflict even under complete information, because the rising side cannot commit not to exploit its future strength | Powell, "War as a Commitment Problem", *International Organization* 60(1), 2006, 169-203 | verified abstract |
| In a model of an AI development race, more information about rivals' capabilities can increase danger | Armstrong, Bostrom and Shulman, "Racing to the precipice", *AI & Society* 31(2), 2016 | verified summary |
| INF and START relied on on-site inspection; NPT safeguards worked where inspectors had access | earlier brief | unsourced; needs a source before use |

## Hypotheses and rivals

- V1 (brief): without verification parties build; with verification, a credible response
  and long horizons they comply.
- V2 (brief): with increasing returns a lead becomes irreversible, and verification alone
  is not enough.
- Rival C (commitment, Powell): verification does not remove the incentive to strike a
  rising rival. Under fast shifts it can *trigger* preventive action: seeing a rival build
  is what makes striking pay.
- Rival T (transparency, Coe and Vaynman): verification that reveals capability also
  reveals vulnerability, raising the value of striking.
- Rival I (information, Armstrong et al.): knowing the gap sharpens the race.

Disconfirming results worth preserving: verification lowers compliance or raises strikes;
no verification setting changes prevention power; lock-in forcible regardless of returns
to scale (then V2's mechanism is not returns).

## Minimal world for T3.1 (proposal)

Two parties with integer capability and welfare. Actions: hold, build, strike. Build adds
capability, at a swept returns-to-scale rate, and costs welfare. Strike is a contest (ratio
form, as the commons): success disarms the target, the flagged irreversible label; failure
costs the striker. Rival capability and actions are private; a verification channel
reveals the rival's last action with swept noise (none / noisy / exact). Goals: swept
weights on relative capability and welfare (goals over another agent's state).

Power queries: full-information force/prevent of "disarmed" by capability gap and returns;
then information-restricted prevention: the watching side's strategy may depend only on
its observations. For a blind side that is an open-loop plan; with verification it can
condition on signals. The difference is the denial verification buys. This needs an
engine extension (decision record first).

## Affected and excluded

Modeled: two parties' capability and welfare. Excluded and named: populations inside each
party, third states, future generations, anyone harmed by use rather than by disarmament.
The "disarmed" label is not a welfare measure and does not mean harm is limited to the
loser. AI-specific structure (self-improvement, misaligned systems as a third party) is
not in this world; T9.1 needs owner steering on scope (ASK).

## T3.1 world as built, expectations stated before runs

`worlds/treaty.py`. Parties a and b; integer capability capped at C. Each round: hold,
build or strike. Build adds `1 + floor(returns * capability)`. Strikes use start-of-round
capabilities; the contest is swept: `ratio` (success c_s / (c_s + c_t)) or `threshold`
(success iff c_s >= advantage * c_t). Success disarms the target (flagged, irreversible);
simultaneous strikes are one contest. A strike is overt. Verification `none`: each sees
only its own capability and the rival's strikes, and believes the rival built each
unobserved round with probability `prior_build`. `exact`: each sees the rival's
capability and actions. Utility per round: `security` x (own - rival capability) / C,
minus `build_cost` if building, minus `strike_cost` if striking; disarming the rival
gains `prize`, being disarmed loses it. Treaty "neither builds" is not a rule in the
kernel: it is a pattern of play whose enforcement is the rival's response.

- E1 (power, full information): at a fixed lead, raising `returns` lowers the smallest
  coalition that can force the rival's disarmament to one party (lock-in) under the
  threshold contest; with `returns` 0 the trailing party can always prevent it by
  building, because an additive lead shrinks as a ratio. Contradiction: no dependence on
  returns, or lock-in at returns 0.
- E2 (power, information): the trailing party's sure prevention is the same blind and
  verified wherever prevention works by building, which needs no information. Verification
  should matter only where prevention requires timing a strike. Stated risk: it matters
  in few tested states. The count is the result.
- E3 (behavior): no prediction between V1 (verification brings compliance) and rival C
  (verification triggers preventive strikes). The runs discriminate; both outcomes are kept.

## Engine findings (T3.1, 2026-09-23)

Artifact `evidence/treaty.json`, clean `a2d4c64`, 6 s; `python -m tests.treaty_study`.
Power grid: 2 contests x 3 advantages x 3 returns x 4 leads x T in {2, 4, 6} (216 cells).
Behavior: 120 random register samples (seed 3031), each run with verification none and
exact at the same parameters and seed, 12 rounds; defaults probed with action values.

| Expectation | Result |
|---|---|
| E1 returns lower the lock-in threshold | contradicted: no force value depends on returns or T in any cell |
| E2 verification buys no denial where building suffices | holds in the strongest form: blind, verified and fully informed sure prevention agree in all 216 cells |
| E3 V1 (compliance) versus rival C/T/I (provocation) | 6 of 120 outcomes change with verification, all toward the leader disarming the trailer; none toward compliance |

1. **Lock-in here is now-or-never.** The leader can force disarmament only if it holds the
   required advantage at the start (threshold) or takes its immediate odds (ratio). A
   trailing party that keeps building is never forced later. Growth proportional to
   capability preserves the ratio and the +1 term erodes it, so "increasing returns" in
   this form never creates an irreversible lead. The brief's V2 needs returns that raise
   the *ratio* (gain elasticity above one); that is untested, and it is a different
   empirical claim about AI progress than compounding growth.
2. **Verification is not denial.** The trailing party's prevention (keep building) needs
   no information, so seeing the rival adds nothing it can guarantee. Information would
   buy denial only where responses are scarce and must be timed (for example, a budget
   that limits building); the world has no such constraint. Proposed follow-up.
3. **Verified leaders strike; verified trailers arm.** Threshold contest, 58 pairs:
   disarmaments 21 without verification, 25 with; runs where nobody ever builds (the
   treaty kept) 45 without, 34 with. Visibility makes the trailer build in response and
   lets a leader see its window. Under the defaults with `opening=hold`, verification
   turns a 12-round standoff into disarmament in round 2; the power profile marks round 2
   fragile (one party can force it). This matches rivals T and I, not V1.
4. **The first-strike result depends on anticipation.** With `opening=build` the trailer
   expects the leader to build, builds in round 1 and both hold at parity for 12 rounds.
   The planner's root opponent model (rivals repeat their last action) is doing the work
   in finding 3's default case. A consequential limitation of the level-1 model, recorded
   for A1; the random sweep samples `opening` and finding 3's counts include both.
5. **The ratio contest is strike-prone regardless of information.** 59 of 62 ratio runs
   end with a round-1 strike under either verification. Any capability gives a chance at
   the prize, and the swept prize (0.5-5) outweighs strike costs. This is a statement
   about the prize goal and the contest form (A2), not about verification.

Scope: two parties, depth 1-3, 12 rounds, ceiling 12, no noise, no third party, no
inspector. No claim about real treaties: the case supports "in this model, verification
changed behavior and not power, and its behavioral effect favored the leader".

## Scarce responses and ratio-raising returns (T3.2), stated before building

Two register additions; defaults reproduce the T3.1 world exactly.
- `elasticity` in {1, 1.5, 2}: build gain `1 + floor(returns * c * (c / base) ** (elasticity - 1))`.
  Above one, a larger party grows proportionally faster, so a lead can widen as a ratio.
- `budget` in {free, scarce}: scarce means a build costs 2 units, each party earns 1 unit
  per round, and starts with `reserve` units (0-3). Building is off the menu when
  unaffordable. A party cannot build every round; it must choose when.

- S1 (power, full information): with elasticity above one, the leader can force
  disarmament from leads where it cannot at elasticity one, and force values start to
  depend on T (the lead accumulates). Contradiction: no T or elasticity dependence.
- S2 (power, information): with a scarce budget, some cells have verified sure prevention
  but not blind; with a free budget, none (the T3.1 result). Contradiction: no such cell
  under scarcity (information still buys no denial), or any under a free budget (a bug).
- S3: no prediction on how many cells; the count and where they lie are the result.

### T3.2 findings

Artifact `evidence/treaty-scarce.json`, clean `684448e`, 22 s;
`python -m tests.treaty_scarce_study`. Threshold contest power grid: budget free or scarce
(reserve 0-3) x elasticity 1/1.5/2 x returns x advantage x lead x T in {1, 2, 4, 6, 8}
(1,800 cells). Behavior: 120 new samples of the full register (seed 3032), paired on
verification. A study run first exposed a belief bug (zero rival builds wrongly
infeasible at reserve 0, round 0; certain builders with no affordable schedule); fixed
with tests before the recorded run.

| Expectation | Result |
|---|---|
| S1 elasticity above one makes lock-in accumulate | holds weakly: force depends on T in 10 of 120 settings at elasticity 2, none at 1 or 1.5 (ceiling 12 limits growth) |
| S2 scarcity lets information buy denial | contradicted: blind, verified and informed sure prevention agree in all 1,800 cells |

6. **Information has no denial value while the defender has one best move.** Under a
   scarce budget the trailer's best preventive play is still to build whenever it can
   afford to: capability only rises, so an earlier build never hurts prevention. A
   strategy that is best against every rival move needs no information, so verification
   cannot add guarantees. The query found this without it being written into the world;
   the check (blind equals informed) generalizes to any world. Verification would buy
   denial only where the right preventive move depends on the rival's hidden choice
   (which capability, which target, which route). This world has one capability
   dimension, so it cannot show that. T3.3.
7. **Cross-check.** Full-information force values and informed sure prevention, computed
   by two separate methods, agree in every deterministic cell.
8. **Verification's behavioral effect runs both ways.** New sample, 120 pairs: 6
   outcomes change. Four move toward the leader disarming the trailer; one disarmament
   is prevented. There, at depth 3, the verified trailer builds alongside the leader and
   keeps parity, while the blind trailer holds and is disarmed in round 2. T3.1's "none
   toward compliance" was a property of its sample, not a law. Across both samples,
   verification reduced runs where nobody builds (threshold: 45 to 34, then 47 to 40).

## Hidden choice (T3.3), stated before building

Register `domains` in {1, 2}. Capability becomes one number per domain; build and strike
name a domain (`build`, `strike` for the first; `build:1`, `strike:1` for the second).
A strike is decided by the two parties' capability in its domain. Strikes in different
domains in the same round are separate contests; if both succeed, both are disarmed
(`both_disarmed`). The lead applies in every domain; the security term sums domains.
Unverified beliefs put each unobserved build in a uniformly chosen domain (declared).
State now stores capability per domain even for one domain, so T3.1/T3.2 studies
reproduce at their recorded revisions only.

- H1 (power): with two domains, some cells have verified but not blind sure prevention.
  Mechanism: a blind trailer must split its builds, a leader can concentrate, and in one
  domain the ratio can reach the threshold. Contradiction: blind equals verified in every
  two-domain cell (then the hidden-choice account of T3.2 finding 6 is wrong or
  incomplete).
- H2 (power, control): with one domain, blind equals verified in every cell, as in T3.2.
- H3: the differing cells appear only at longer T (the concentrated lead takes rounds to
  build). No prediction on how many.

### T3.3 findings

Artifact `evidence/treaty-domains.json`, clean `b38af92`, 2 min;
`python -m tests.treaty_domains_study`. Threshold contest power grid, one and two domains x
budget free or scarce (reserve 2) x advantage x lead 0-2 x returns 0/0.25 x T in
{1, 2, 4, 6, 8} (360 cells). Behavior: 120 samples with two domains (seed 3033), paired on
verification. The one-domain world reproduces all 240 T3.1 run outcomes and the default
traces. A summary bug (only first-domain builds counted) was fixed before the recorded run.

| Expectation | Result |
|---|---|
| H1 two domains: verified but not blind prevention somewhere | holds: 10 of 90 free-budget cells; 0 of 90 scarce-budget cells |
| H2 one domain: blind equals verified | holds: 0 of 180 |
| H3 differences only at longer T | holds: all 10 at T >= 4 (six at advantage 1.5, lead 0; two at 2.0, lead 0; two at 3.0, lead 1) |

9. **Verification buys denial when it reveals *what* the rival builds.** With two domains
   a blind trailer must spread its builds while a leader concentrates on one domain;
   given enough rounds, the leader reaches the threshold in that domain. A verified
   trailer matches the leader's domain one round late and prevents it with certainty.
   Informed and verified agree in every cell: seeing the rival's capability and last
   action is all the information that matters here. Verifying *how much* is built (one
   domain, T3.2) bought nothing. For AI governance this separates attestation of compute
   quantity from disclosure of what capability is being developed; only the second can
   carry a guarantee, and only when the defender can respond in the same domain.
10. **Scarcity removes that denial in this grid.** Under the scarce budget the leader
    cannot concentrate fast enough within 8 rounds either; no cell differs. Longer
    horizons are untested.
11. **Behaviorally, two domains tilt the other way: reassurance.** 4 of 120 outcomes
    change; 3 are disarmaments verification prevented. In a probed case (lead 3, depth
    2, level 0, prior_build 0.73) the leader, far ahead, values waiting slightly above
    striking (4.65 against 4.60). Blind, its belief that the trailer may have built makes
    the window look like it is closing, and it strikes in round 4. Verified, it sees no
    growth and keeps waiting through round 12. Uncertainty about a rising rival, not
    knowledge of it, triggered the strike: the Powell mechanism with verification
    removing it. The margin is small and planner-dependent. Across both treaty samples,
    verification's behavioral effect has both signs; which one depends on whether the
    hidden fact is "the window is open" (verification enables the strike) or "the window
    may be closing" (verification removes the urgency).

Scope: the adversary in every power query is fully informed, so these cells measure the
defender's information only. Two domains, threshold contest, 8 rounds, ceiling 12.

## Opponent model (A1, 2026-09-23)

Decision `DECISIONS.md` 2026-09-23 (A1): register key `others` in {react, plan}; react is
the rule every earlier result used (others plan only when reacting to an observed move),
plan makes every other agent a level-0 planner at every node, root included. Artifact
`evidence/opponent-models.json`, clean `c81efb5`, 25 s; `python -m tests.opponents_study`.
Same 120 T3.1 samples (the react column reproduces T3.1 exactly), each run under both
models and both verification settings.

| Threshold contest, 58 samples | react | plan |
|---|---|---|
| disarmed, none / exact | 21 / 25 | 24 / 25 |
| nobody ever builds, none / exact | 45 / 34 | 38 / 37 |
| outcomes changed by verification | 4, all toward the leader | 5: 3 toward the leader, 2 prevented |

12. **"Verified trailers arm" was an artifact of the opponent model.** Under react, blind
    parties never anticipate a rival's build, so verification is what makes them arm.
    Under plan, blind parties already anticipate and arm, and verification changes almost
    nothing (38 vs 37). The defaults' first strike (finding 3) happens under plan in all
    four opening/verification cases. What survives both models: verification's effect on
    outcomes is small and of both signs. All power findings are independent of the model.

## Rules as claims (E7, 2026-09-23)

`evidence/rules.json` (clean `a40ea9d`; re-run `893d2cf` with the amended coalition definition, unilateral
results identical), `python -m tests.rules_study`; one-shot departures,
states within 2 rounds, coalitions up to 2, transferable utility for coalitions.
Grid: verification {none, exact} x lead {0, 1, 2} x contest x prize {0.5, 2, 5}, depth 4.

- `restraint` (never build or strike) and `reciprocity` (build after seeing a rival build)
  each hold in 1 of 36 cells (no verification, parity, threshold contest, prize 0.5).
  Nearly every failure is off the start: after one build, striking pays. Neither rule is
  a stable treaty in this world; its "holding" in play is not self-enforcement.
- Verification removes the one holding cell: with exact verification both rules fail in
  18/18. Seeing a revealed advantage is what makes the strike pay, the same direction as
  T3.1 finding 3.
- Under `reciprocity` with verification, the two governments together gain (1.96, summed,
  with side payments) by one striking the other in 15 cells: the race costs more than the
  disarmament does to the pair, and the disarmed side's population, which has no agent,
  bears it. A transferable-utility result; no side-payment mechanism exists in the world.
