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
