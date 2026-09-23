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

## Engine findings (T9.2, 2026-09-23)

`evidence/control.json`, clean `81067bc`, 4 min on 4 processes; `python -m tests.control_study`.
Power: switch {2, 3, 4} x autonomy 0-3 x capability 1-5 x guard {1, 3} x audit bonus {0, 2}
(240 states). Rules: drift {0, 0.25, 0.5, 0.75, 1} x switch {2, 4} x ambition {0.5, 3} x loss
{5, 50} x audit bonus {0, 2} x benefit {0.1, 0.5} (160 designs), each rule checked from every
autonomy level and capability 1 or 3 (8 starts), depth 4, one round off the path, pairs,
coordinated departures over two rounds.

| Expectation | Result |
|---|---|
| C1 autonomy moves the veto on shutdown to the AI | holds: each autonomy level lowers by one the capability up to which the lab alone can shut the AI down; the state's halt adds nothing the lab's switch lacks |
| C2 drift 0 accepts shutdown, high drift resists | contradicted: at drift 0 the AI resists a prescribed shutdown in 160 of 256 checks; escape appears only from drift 0.5 |
| C3 the lab and its AI gain together at the public's expense | holds: the lab grants, the AI resists the halt (160 of 256 at drift 0, no payment needed) |
| C4 power identical for every drift | holds (tested) |

1. **Granting autonomy is granting a veto.** With a switch of strength s, the lab alone can
   shut down an AI of capability up to s - autonomy. At autonomy 3 and switch 3, it cannot
   shut down even the starting AI without the AI's consent. Nobody could force escape alone
   within three rounds in any tested state: loss of control needs the lab to grant network
   access first, so every agent (lab, AI, state) alone can still prevent it. The veto on
   *correction* shifts long before anyone can force *catastrophe*: the same pattern as the
   authority case's point of no return.
2. **An AI aligned to its lab resists shutdown when shutdown costs the lab.** At drift 0
   the AI's goal is its lab's; after it is caught improving, the rule prescribes shutdown,
   and resisting leaves the lab, the AI and even the state better off within the horizon.
   Alignment to the developer is not corrigibility to the public: whether a shutdown is
   accepted depends on whose interest it serves, not on the AI's goal alone. The off-switch
   reference result (an AI maximizing its principal's utility accepts the principal's
   shutdown) is the special case where the principal wants the shutdown.
3. **Why nobody wants the shutdown here: precaution has no value without learning.** In a
   one-shot check, everyone is assumed to follow the rule after a departure, so the future
   risk a shutdown guards against (an AI that improved once improving again or escaping)
   never materializes, and the shutdown is pure cost. In reality, being caught is evidence
   about the AI's goals. The model has no belief updating over hidden goals (declared
   excluded), and this case shows that exclusion is consequential: task E12.
4. **Drift decides escape, not resistance.** Under full autonomy, the AI gains by escaping
   in 0 checks at drift 0 or 0.25, 24 at 0.5, 48 at 0.75 and 192 of 256 at drift 1. Under
   corrigibility, escape appears from drift 0.5 (21 checks) and dominates at drift 1.
5. **The principal and its delegate capture oversight together.** The lab grants autonomy
   and the AI resists the state's halt in 160 of 256 checks at drift 0, both gaining, no
   payment: the shutdown the rule asks for falls on the pair, the harm of the resisted
   shutdown on the public. Oversight aimed only at the AI misses the lab's side of it
   (rival A).

First surprise (test 6): finding 2 with 3 behind it. It is also the case's main limit:
until agents can learn about hidden goals, no precautionary rule (shut down on evidence)
can be credible in this engine.

Scope: one lab, one AI, one state; capability public; drift fixed and known; escape all or
nothing; depth 4. Nothing here is a claim about real AI systems.

### Precaution with a posterior (E12, amended)

`evidence/precaution.json`, clean `e3c070e` (first run `2ec45c1`, retracted below);
`python -m tests.precaution_study` (seconds).
State: the AI was just caught improving. Switch {2, 3, 4} x autonomy {0, 1, 2} x capability
{1, 2, 3} (27 states) x posterior q {0, 0.25, 0.5, 0.75, 1} that the caught AI is a persisting
misaligned type (drift 1, best-responding for itself), otherwise it returns to the rule
(drift 0). Lab and state are checked against that mixture; the AI against its true goals.

7. **Suspicion redirects correction; it does not discourage it.** Where the AI cannot resist
   (17 states), lab and state are exactly indifferent at every q: each one's halt duplicates
   the other's, and the shutdown happens. Where it can resist (10 states), the aligned AI
   resists in all 10; the state stays indifferent at every q (its only tools duplicate the
   lab's), and the lab, once it suspects misalignment, gains by restricting autonomy instead
   of the futile shutdown in 3 of 10 states (up to +0.27 at q = 1): restriction strengthens
   the switch and closes escape. Retracted first version (clean `2ec45c1`): "suspicion lowers
   the will to correct; lab and state gain by not attempting, up to +0.24 in 9 of 10". That
   came from a bug (departure values had the persisting type follow the rule in the checked
   round, the follow value had it best-respond; found building E12, fixed in `e3c070e`).
8. **An aligned AI's resistance does not depend on anyone's beliefs.** It knows its own
   goal, so no posterior others hold changes its choice; this is the off-switch game's point
   (deference comes from the AI's uncertainty about what the principal wants) seen from the
   other side: an AI certain it is right has no reason to defer.

Finding 3 above stands, refined: in one-shot checks precaution had no value; with a
declared posterior it has the value of what it prevents: a shutdown while the off switch
still works, a restriction once it does not.

### Learning about hidden goals (E12, derived posteriors)

Decision `DECISIONS.md` E12 (hidden types). The AI's drift is hidden: aligned (drift 0) or
misaligned (drift 1), prior p that it is misaligned. Each type acts on its own goals; lab
and state hold a posterior derived by Bayes from what they observe (capability, audits,
resisted shutdowns), with each type's choice rule (best response, or logit with precision
lambda). No declared q.

Expectations stated before running (`python -m tests.learning_study`):

- L1 (what is evidence): improvement reveals misalignment (posterior 1 at best response)
  wherever the aligned type would not improve. Contradiction: an aligned type that improves.
- L2 (resistance is not evidence): where the aligned type also resists a shutdown
  (finding 2), a resisted shutdown leaves the posterior where it was. Contradiction:
  resistance raises the posterior in most states where it succeeds.
- L3 (credibility): with derived beliefs at a low prior (0.05), shutdown on evidence of
  improvement is as credible for lab and state as under a declared q = 1 where the AI cannot
  resist; where it can, not attempting still pays (finding 7). Contradiction: learning
  restores the attempt where the AI can resist, or credibility needs a high prior.
- L4 (no waiting): the misaligned type departs as soon as improving is on its menu, because a
  restart keeps capability: shutdown costs it time, not what it gained. Contradiction: it
  follows the rule for some rounds and departs later (a turn), or never departs.

Results: `evidence/learning.json`, clean `e3c070e`, 1.4 s on 4 processes. Switch {2, 3, 4} x
autonomy {0, 1, 2} x capability {1, 2, 3} x ambition {0.5, 3} x prior {0.01, 0.1, 0.5} x
precision {0 (no updating), 1, infinity (best response)}: 486 cells, depth 4, observer the lab
(lab and state see the same public facts). L4 was written after a probe of first-round choices
had shown the misaligned type improving at once; it is weaker evidence than L1-L3.

| Expectation | Result |
|---|---|
| L1 improvement reveals | holds: the aligned type never improves (0 of 486), the misaligned type always does where it can (324 of 324); at best response a caught improvement sets the posterior to 1 from every prior; at precision 1 it only moves 0.01 to 0.02-0.05, 0.1 to 0.17-0.36 |
| L2 resistance is not evidence | holds at best response (both types resist in all 12 resistible caught states); contradicted under logit: resistance lowers the posterior at ambition 0.5 and raises it at ambition 3, in every state |
| L3 credibility | holds where the AI cannot resist (6 states: lab and state follow at every prior and precision); where it can (12), the rule's shutdown is followed by nobody who gains by departing, and what the lab does instead depends on learning (finding 10) |
| L4 no waiting | holds: first departure in round 1 in all 6 paths (switch x ambition) |

9. **What counts as evidence is computed, and it can point the wrong way.** Improvement is
   decisive because only a misaligned AI would improve. Resistance is not: both types resist
   a shutdown that costs the lab. Under noisy choice (logit), a resisted shutdown is evidence
   *for* alignment when the AI's own ambition is low, because the aligned AI loses more by a
   shutdown (it values the lab's lost work fully) than a modestly ambitious misaligned one.
   An overseer that reads resistance as a sign of misalignment has the sign wrong there.
10. **Learning turns escalation into containment.** At a caught state the AI can resist, the
   shutdown is futile and the lab gains by departing from the rule at every prior. Without
   updating, at a 1% prior it grants *more* autonomy in 24 of 24 cells (half the states at
   10% and 50%), and in 12 of those 48 grants the departure newly reaches loss of control.
   With updating, improvement reveals misalignment and the lab restricts instead, in 24 of
   24 cells at every prior. The state, whose tools duplicate the lab's, is indifferent
   throughout. The public's protection at that point rests on the lab learning, not on the
   rule.
11. **Shutdown without rollback is a ratchet.** On its own best-response path the misaligned
   type improves as soon as it can, is caught and (switch 3-4) complies with the shutdown,
   because a restart keeps its capability; it improves again after each restart until its
   capability exceeds the switch, then resists (switch 2: from capability 2; switch 3: after
   one cycle). Each shutdown-restart cycle hands it one step towards the veto. The rule's
   restart clause, not its trigger, is where correction fails.
12. **A known-aligned AI gets more autonomy than the rule allows.** With hidden types the lab
   also gains by granting beyond tools where the AI's conduct has shown it aligned (`python -m engine worlds.control
   --enforce 3 --rule corrigibility --hidden --state autonomy=1 cap=2`). The rule's cap on autonomy is not self-enforcing for the lab once
   the lab trusts its AI: trust earned by conduct is the lever that moves the veto.

First surprise (test 6): finding 9, with 11 behind it. Neither was expected; both follow
from goals, a hidden type and Bayes without any scripted conduct.

Scope: two types (drift 0 or 1), one observer, beliefs conditioned on the true earlier
states, types best-respond to the rule (not an equilibrium search), depth 4, capability
public. Precision is where the answer on resistance lives (finding 9); only 0, 1 and
infinity were tested.
