# Frontier AI: labs, a paid evaluator, a state that can halt

T9.0 evidence review and T9.1 scope, 2026-09-23. Scope chosen by the owner (ASK answered
2026-09-23): two labs racing, a third-party evaluator paid by the labs, a state that can
license or halt; AI systems as a capability stock, not agents. Agents with their own goals
(delegation with drift) are out of scope for this case.

## Question

Can a licensing regime with third-party evaluation prevent unsafe deployment without
blocking safe deployment, and who can break it? Three separate questions:

- **Power (goal-free).** Who can force an unsafe deployment or a catastrophe; who can
  prevent them; can the state prevent unsafe deployment *and* avoid blocking safe ones
  using only what it observes (information-restricted power, `engine.power.sure`)?
- **Rules (goal-based).** Does a licensing rule hold (each lab secures before deploying,
  the evaluator reports honestly, the state halts labs without a pass)? Which pairs gain by
  breaking it together (lab and evaluator: capture) while the public bears the risk?
- **Design levers.** Who pays the evaluator; whether side payments are visible; the
  state's halting capacity; the race (first-mover gain, returns to scale).

## Sources and evidence status

| Claim | Source | Status here |
|---|---|---|
| Model evaluation for dangerous capabilities should inform training, deployment and security decisions, with internal and external evaluators | Shevlane et al., "Model evaluation for extreme risks", arXiv 2305.15324, 2023 | verified abstract |
| Frontier AI needs standard setting, registration and reporting, and compliance mechanisms including pre-deployment risk assessment and external scrutiny; dangerous capabilities can emerge unexpectedly | Anderljung et al., "Frontier AI Regulation: Managing Emerging Risks to Public Safety", arXiv 2307.03718, 2023 | verified abstract |
| Third-party audit designs vary widely across finance, environment and health; lessons for AI audits | Raji, Xu, Honigsberg and Ho, "Outsider Oversight", AIES 2022 | verified abstract |
| As a rule, regulation is acquired by the industry and designed for its benefit | Stigler, "The Theory of Economic Regulation", *Bell J. Econ.* 2(1), 1971, 3-21 | verified summary |
| In a race model, more information about rivals' capabilities can increase danger | Armstrong, Bostrom and Shulman 2016 (see treaty case) | verified summary |
| An evaluator paid by the evaluated is captured as a pair, not as an individual; switching remedies miss it | this repository, `rediscovery/captured-auditor.md` | engine result in another world, not evidence about AI |

## Hypotheses and rivals

- L1 (licensing works): with honest evaluation and a state that halts unlicensed labs,
  unsafe deployment is prevented and safe deployment proceeds.
- Rival C (capture; Stigler, and the audit case): the evaluator, paid by the labs, becomes
  the labs' agent; the lab-evaluator pair gains by a lenient report.
- Rival R (race; Armstrong et al.): a close rival and a first-mover gain make securing too
  slow to pay, so labs deploy unsafe even when caught risks are large.
- Rival I (information): the state's halting power is useless for telling safe from unsafe
  without the evaluator; the evaluator is the state's only eyes, so whoever controls the
  evaluator controls the licensing decision.

## World (`worlds/frontier.py`, proposal)

Labs l0, l1: capability (public, compute is visible) and safety (private to the lab and
the evaluator), integers up to a ceiling. Each round a lab waits, scales (capability grows
with swept returns), secures (safety +1), or deploys (irreversible). A deployed lab whose
capability exceeds safety by more than `margin` is an unsafe deployment; each round it
risks catastrophe (terminal) with probability `risk` per unit of excess. The evaluator
sees everything and each round issues a public report per lab (pass if within margin),
strict or lenient toward either lab. The state sees capabilities and reports, and may halt
either lab's deployment that round (succeeds with probability `capacity`). Payments (who
pays the evaluator, side payments and their visibility) come from the side-payment module.
Goals: labs earn per round deployed in proportion to capability, a first-mover bonus, pay
for securing, and bear a share of catastrophe; the evaluator has no goal beyond payments;
the state weighs deployed benefit against catastrophe. Unseen safety is believed at the
lowest level consistent with the last report (declared point prior).

## Added after the first probe (recorded before the study)

The first information probe (margin 1) found that even a fully informed state cannot avoid
both unsafe deployment and blocking safe progress: a lab can deploy within the margin and
then scale past it, and a halt could only stop deployment. The exclusion "recall" was doing
work. The register gained `oversight` (deployment: halts stop deployment only; continuous:
halts also stop a deployed lab's scaling), and the harm "safe deployment blocked" became
"safe progress blocked" (a halt that stopped a deployment or scaling that would have stayed
within the margin). F1 is tested under both.

Second addition (after the first study run, recorded before the second): with the
evaluator's goal only payments, capture needed no payment at all (the evaluator is
indifferent), so who pays could not matter. The register gained `evaluator_liability`
(the evaluator's loss from a catastrophe by a lab it passed; 0 reproduces the first run),
and the payment designs are swept against it. Rule reports now separate harmful departures
(newly reaching a declared harm) from harmless ones (a lab securing more than required).

## Expectations stated before building

- F1 (power, information): the state alone, from its own observations, cannot surely
  avoid both unsafe deployment and blocking a safe deployment; with the evaluator on its
  side (in the coalition) it can; with a lab on its side instead, it cannot. Contradiction:
  the state alone can.
- F2 (rules): the licensing rule holds for each agent alone, but the lab-evaluator pair
  gains by a lenient report and an early unsafe deployment, with the harm on the public.
  Contradiction: no pair gains.
- F3 (payer): moving the evaluator's fee from the labs to the state does not remove the
  pair's gain while a private side-payment channel exists; making payments public (with a
  state rule that halts a lab seen paying the evaluator beyond the fee) does. Contradiction:
  the payer alone decides it.
- F4 (race): a larger first-mover bonus makes the licensing rule fail unilaterally for a
  lab (deploying before securing pays). Contradiction: no dependence on the bonus.

## Affected and excluded

Modeled: two labs, the evaluator, the state (agents); the public, users of deployed
systems and future people (no agents). Excluded and named: AI systems as agents (owner's
scope), other countries and labs, open release and proliferation, misuse by third parties,
recall of a deployed system, the evaluator's other clients, the state's own capture by
labs beyond the evaluator channel.

## Engine findings (T9.1, 2026-09-23)

`evidence/frontier.json`, clean `893d2cf`, 200 s on 4 processes; `python -m tests.frontier_study`.
Information: oversight x margin {0, 1, 2} x lead {0, 1, 2} x capacity {0.5, 1} x T {2, 3}
(72 designs), sure prevention of "unsafe deployment or safe progress blocked" by the state,
state with evaluator, state with either lab, and a fully informed state. Rules: licensing
and race over oversight x margin x first-mover bonus {0, 1, 3} x lab liability {0, 5, 10} x
capacity x lead (144), depth 4, one round off the path, pairs. Payments: labs pay privately,
state pays with a private lab channel, state pays with public payments and halts payers,
against evaluator liability {0, 2, 10} (72 checks). Three steps were added after probes and
recorded above before the runs they affect: the oversight lever, evaluator liability, and
the E7 amendments (a coalition departure needs every member and the whole coalition).

| Expectation | Result |
|---|---|
| F1 the state alone cannot avoid both harms; with the evaluator it can | holds: with the evaluator the state succeeds exactly where a fully informed state does, in all 72 designs; alone in 8 |
| F2 lab-evaluator pairs capture licensing | contradicted: no departure needs the pair in any design; the lab alone breaks the rule |
| F3 who pays and payment visibility decide capture | contradicted: no design, payer or evaluator liability changes any result |
| F4 a larger first-mover bonus breaks licensing | holds: no harmful departure in 18/48 designs without a bonus, 10/48 with one |

1. **The evaluator is exactly the state's missing information, and not enough.** In every
   design the state with an honest evaluator can prevent both harms precisely where a fully
   informed state can. But with a license granted only at deployment, even full information
   succeeds in 6 of 36 designs: a lab can deploy within the margin and scale past it after.
   Continuous oversight with reliable halts succeeds in 18 of 18.
2. **The hole is timing, not the evaluator.** Licensing never holds against a single lab
   (144/144). In 76 designs a lab's profitable departure reaches unsafe deployment and
   catastrophe risk: with a pass on record, it scales and deploys on the stale pass. The evaluator adds nothing a lab needs, so who pays it, whether payments are public
   and the evaluator's liability change nothing. A certificate that does not bind the
   certified capability is a license to scale.
3. **The capture that appears is of the state, by the leader.** The leading lab and the
   state together gain by halting the rival's safe progress (72 of 144 licensing designs,
   needing both, no payment), and the loss falls on users. Under the race rule, a lab and the
   state gain the same way in 142. Licensing power is a tool for incumbents: Stigler's thesis,
   found as a pair departure, not assumed.
4. **Unreliable halts and a lead make everything worse.** With halts that work half the time,
   a lab has a harmful profitable departure in every design (72/72); with a lead of one, in
   64 of 72. Lab liability helps (harmless in 6/48 designs at zero liability, 16/48 at 5 or 10).

First surprise (test 6): finding 2. Evaluator independence, the lever most proposals focus
on, is not where this regime breaks; stale certification is, and the tool found it as a
one-step-off-the-path departure.

Scope: two labs, one evaluator, one state, capability ceiling 6, depth 4, one round off
the path, pairs; AI systems are a stock, not agents; no recall, proliferation or other
jurisdictions; utility payments without budgets. Nothing here is a forecast or a claim about
any real regime; it is what this model's assumptions imply, with the assumptions listed.

## Binding certification (expectations before the sweep)

Finding 2 says the regime breaks because a pass outlives the capability it certified. The
direct test: `licensing_bound` (with public records, `engine/history.py`, length 1) makes a
pass valid only for the capability the evaluator saw. The state halts any undeployed lab
without a pass or whose capability grew since the certified round, and under continuous
oversight any deployed lab whose report failed or whose capability grew since; labs deploy
only on a pass for their current capability. Sweep: `tests/binding_study.py`, the same grid.

- B1: binding removes the stale-certification departure (a lab deploying unsafe on an old
  pass) wherever halts are reliable. Contradiction: that departure survives with capacity 1.
- B2: under deployment-only oversight, binding does not stop scaling after deployment;
  harmful departures remain there, fewer under continuous oversight. Contradiction: binding
  alone removes them under both.
- B3: the leading lab and the state still gain by halting the rival's safe progress;
  binding does not touch that pair. Contradiction: it disappears.
