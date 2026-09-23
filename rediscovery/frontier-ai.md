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
