# Rediscovery: standing army, no succession rule

**Known outcome.** When the ruler exits, the army or its commander decides who rules next. Written succession rules are ignored. Praetorian Guard, Mamluks, most coups.

## Setup in primitives

```
types:
  ruler (1):        goals: retain position. capabilities: command army, pay army from treasury.
  army (1, large):  created by ruler through delegation. capabilities: coercion, larger than
                    every other type combined. goal as set: obey ruler. drift: toward obey commander.
  commander (1):    sub-agent of ruler inside army. capabilities: direct the army's coercion.
  council (1):      goals: choose ruler per rule. capabilities: deliberate, appoint. no coercion.
  population (many): goals: safety, yield. capabilities: labor; coercion small each, large in coalition.
rules:
  L2: council appoints the ruler. Amendment rule: none written.
  L0: army obeys ruler.
channels: ruler observes commander. commander observes army. council observes little.
irreversible: exit of the ruler.
```

## Derivation

Round of the ruler's exit. Who rules is now contested. Council acts under L2 and appoints. Commander acts and claims. The contest function decides by capability, and the commander's is largest by construction. The council's rule is a claim with no enforcer. The population could enforce as a coalition, but each member believes the others will not join, and without channels among them nothing grounds a different belief. The coalition does not form. The commander wins. Constitutional authority now sits with whoever commands coercion, whatever the written rule says.

Before the exit: delegation drift moves the army's goal from obey ruler toward obey commander over rounds. The ruler observes the commander, so the ruler's best response is to replace commanders often, split the army, or pay soldiers directly. Those are the interventions history found, and the ruler reaches them by planning, not by script.

## Emerges?

Yes, after one correction. With rules as hard constraints on action sets, the council's rule binds by fiat and the army cannot act; the model would say the constitution holds. With rules as claims enforced by contest, the outcome above follows.

## Gap found

Rules must be claims, not constraints. A rule binds only through the contest that enforcing it would win, and the enforcing coalition depends on agents' beliefs about each other. Both moved into `spec/PRIMITIVES.md`.

## What the engine should show

Lock-in threshold at the ruler's exit: one agent, the commander.

| Intervention | Expected effect |
|---|---|
| Split command into k armies | Threshold rises to the coalition of commanders needed to beat the rest |
| Council controls pay (money to coercion conversion) | Commander's capability decays without council; threshold rises, correction stays low |
| Written succession rule alone | No change. A claim with no enforcer |

The third row is the one careful designers get wrong. It is the first test of intent test 6.
