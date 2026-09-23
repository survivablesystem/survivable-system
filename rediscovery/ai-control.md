# AI systems as agents: delegation, drift and the off switch

T9.2 evidence review and design, 2026-09-23. Scope: the step after `frontier-ai.md` (AI as
a capability stock) that the owner's standing approval covers: an AI system as an agent
whose goal is its principal's, drifted by a swept amount. Decision `DECISIONS.md` E11.

## Question

When a lab grants an AI system autonomy, who can still shut it down, and from what point
on can nobody outside the AI correct it? Does a corrigibility rule (the AI works, never
resists or escapes; the lab keeps autonomy within limits) hold as goal drift grows? Do the
lab and its AI together gain by more autonomy than the rule allows, at the public's risk?

- **Power (goal-free).** Shutdown, escape (loss of control, irreversible) and who holds a
  veto on shutdown, by autonomy and capability. Drift cannot enter: power ignores goals.
- **Rules (goal-based).** Corrigibility against drift, oversight and liability; principal
  and delegate as a pair; coordinated departures over two rounds (improve, then grant).

## Sources and evidence status

| Claim | Source | Status here |
|---|---|---|
| A robot uncertain about the human's utility and maximizing it has an incentive to leave its off switch alone, if the human is not too irrational; the incentive weakens as the robot's uncertainty falls | Hadfield-Menell, Dragan, Abbeel and Russell, "The Off-Switch Game", IJCAI 2017, 220-227 | verified abstract |
| AI alignment resembles incomplete contracting: a principal cannot specify everything a delegate should do | Hadfield-Menell and Hadfield, "Incomplete Contracting and AI Alignment", AIES 2019, 417-422 | verified abstract |
| A misaligned, strategically aware AI system has instrumental reasons to seek power, including resisting correction | Carlsmith, "Is Power-Seeking AI an Existential Risk?", arXiv 2206.13353, 2022 | verified abstract (argument, not evidence) |
| Delegation creates agency costs borne by the principal, and monitoring and bonding spend resources to reduce them | Jensen and Meckling, "Theory of the Firm", *J. Financial Economics* 3(4), 1976, 305-360 | verified abstract |

## Hypotheses and rivals

- O1 (off switch): an AI whose goal is its lab's (drift 0) accepts shutdown whenever the lab
  wants it; resistance pays only above some drift.
- Rival P (power-seeking): above some capability or autonomy, resisting and escaping pay
  for almost any drift, because they preserve the AI's ability to do anything it values.
- Rival A (agency costs): the lab and its AI share an interest in more autonomy (more
  value now) and the risk falls on the public; oversight is aimed at the wrong party if it
  watches only the AI.

## World (`worlds/control.py`)

Lab, AI system, state. The lab grants or restricts autonomy (0 sandbox, 1 tools, 2 network,
3 self-modification), runs the AI, or tries to shut it down. The AI works (value to the lab
proportional to autonomy), improves (capability +1, needs autonomy 1+), resists (a shutdown
attempt fails if capability exceeds the off switch's strength, which falls with autonomy),
or escapes (needs autonomy 2+; succeeds with a chance rising with capability, lowered by an
audit; loss of control is irreversible and absorbing). The state allows, audits (makes
escape harder; the AI's last action becomes public) or orders a shutdown. Goals: the lab
values work and fears loss of control; the AI's own goal values capability and escape;
through delegation its utility is (1 - drift) x the lab's + drift x its own; the state
values the public's share of the work and fears loss of control.

## Expectations stated before building

- C1 (power): there is an autonomy level from which the lab alone can no longer shut the AI
  down once it has improved (the AI holds a veto on shutdown), well before the AI could
  force escape. Contradiction: shutdown power never depends on autonomy.
- C2 (off switch, O1): at drift 0, corrigibility holds for the AI; at high drift the AI gains
  by resisting or escaping. Contradiction: resistance pays at drift 0, or never.
- C3 (rival A): the lab and its AI together gain by granting more autonomy than the rule
  allows (or by the AI improving and the lab granting next), with the harm on the public.
  Contradiction: no such pair departure.
- C4: goal-free power is identical for every drift (by construction; tested).

## Affected and excluded

Modeled: lab, AI system, state (agents); the public and future people (no agents) bear loss
of control. Excluded and named: other labs and AI systems, hidden capability (sandbagging:
capability is public here), deception about goals (drift is known to the modeler, not
hidden from agents in a learned way), gradual or partial loss of control, misuse by people.
