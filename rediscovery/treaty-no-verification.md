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
