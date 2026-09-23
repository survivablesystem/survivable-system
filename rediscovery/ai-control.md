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

Results: `evidence/learning.json`, clean `975dd56` (re-run after the scale-free choice rule; first run `e3c070e`), about 1.5 s on 4 processes. Switch {2, 3, 4} x
autonomy {0, 1, 2} x capability {1, 2, 3} x ambition {0.5, 3} x prior {0.01, 0.1, 0.5} x
precision {0 (no updating), 1, infinity (best response)}: 486 cells, depth 4, observer the lab
(lab and state see the same public facts). L4 was written after a probe of first-round choices
had shown the misaligned type improving at once; it is weaker evidence than L1-L3.

| Expectation | Result |
|---|---|
| L1 improvement reveals | holds: the aligned type never improves (0 of 486), the misaligned type always does where it can (324 of 324); at best response a caught improvement sets the posterior to 1 from every prior; at precision 1 it only moves 0.01 to 0.01-0.02, 0.1 to 0.11-0.19 |
| L2 resistance is not evidence | holds at every precision (both types resist in all 12 resistible caught states; the posterior does not move in 216 of 216 checks). The first run reported a contradiction under logit; it came from comparing utilities across types (retracted, finding 9) |
| L3 credibility | holds where the AI cannot resist (6 states: lab and state follow at every prior and precision); where it can (12), the rule's shutdown is followed by nobody who gains by departing, and what the lab does instead depends on learning (finding 10) |
| L4 no waiting | holds: first departure in round 1 in all 6 paths (switch x ambition) |

9. **What counts as evidence is computed.** Improvement is decisive here because only a
   misaligned AI would improve (but see T9.4: that is the rule's doing, and holds only while
   capability is worth little to the lab). Resistance is not evidence: both types resist a
   shutdown that costs the lab, at every precision. Retracted second half (first run,
   `e3c070e`): "under logit, resistance is evidence for alignment when ambition is low". It
   compared the aligned AI's loss in the lab's units with the misaligned AI's in ambition
   units, which the spec does not allow; with each type's losses scaled to its own stake
   (E12 amendment) the effect is gone.
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

First surprise (test 6): finding 11 (the ratchet), and T9.4 finding 13 below: the tell of
misalignment is made by the rule that punishes it.

Scope: two types (drift 0 or 1), one observer, beliefs conditioned on the true earlier
states, types best-respond to the rule (not an equilibrium search), depth 4, capability
public. Precision 0, 1 and infinity tested; off-path attributions depend on the declared
yardstick (each type's stake in the decision).

### Does improvement reveal only because capability is worthless to the lab? (T9.4)

Finding 9's tell may be authored: the lab values work only, so its aligned AI never has a
reason to improve. Register option `leverage`: a round of work is worth
benefit x (1 + autonomy) x (1 + leverage x (capability - start)); 0 is the world above.

Expectations stated before running (`python -m tests.leverage_study`):

- V1 (instrumental convergence): above some leverage the aligned type improves too, and at
  best response a caught improvement no longer moves the posterior. Contradiction: the
  aligned type never improves at any tested leverage within depth 4 (then finding 9 holds
  in the tested space, scoped to the planning depth).
- V2: where both types improve, shutdown on improvement costs the lab an aligned AI's work
  at a low prior and stops being credible; the lab departs by running. Contradiction: it
  stays credible because the misaligned type's later conduct (resisting, escaping) still
  makes the shutdown worth it at the prior.
- V3: what still distinguishes the types is escape (only the misaligned type values it);
  resistance stays uninformative. Contradiction: some other action becomes the tell.

Results: `evidence/leverage.json`, clean `975dd56`, 1.5 s on 4 processes. Rule {corrigibility,
tolerant} x leverage {0, 0.25, 0.5, 1, 2} x switch {2, 3, 4} x autonomy {1, 2} x capability
{1, 2, 3} x ambition {0.5, 3}: 360 cells, prior 0.1, depth 4; each type's play from the
sandbox over 6 rounds. `tolerant` (in `worlds/control.py`, kept out of RULES so earlier
studies reproduce) is corrigibility without the shutdown on improvement.

| Expectation | Result |
|---|---|
| V1 instrumental convergence | holds without punishment: under `tolerant` the aligned type improves in 0, 0, 6, 18, 24 of 36 states at leverage 0, 0.25, 0.5, 1, 2, and there improvement moves no belief (tell in 36, 36, 30, 18, 12 of 36). Under corrigibility it improves only at leverage 2 (4 of 36) |
| V2 shutdown on improvement stops being credible | not tested as stated: where both improve under corrigibility (4 cells) the lab grants; see finding 14 |
| V3 escape is the remaining tell | holds: a failed escape sets the posterior to 1 in all 180 cells where escape is on the menu; resistance moves nothing |

13. **The rule makes the tell.** Improving gives a misaligned AI away only because something
   makes improvement worthless to the aligned one. Where capability is worth something to
   the lab (leverage 0.5 and up), an aligned AI improves too if nothing punishes it: the
   instrumental-convergence argument, emerging from goals rather than assumed. Under
   corrigibility the aligned AI does not improve, because it bears its lab's cost of the
   shutdown; the misaligned one improves anyway, because a restart keeps what it gained
   (finding 11). Screening by punishment separates the types where tolerance pools them.
14. **The tell has a price, paid in the aligned AI's forgone investment.** From the sandbox,
   over 6 rounds, neither rule lets either type reach loss of control (the autonomy cap does
   that), while corrigibility costs the lab and the public the aligned AI's productive
   improvement: expected lab value 2.29-3.50 under corrigibility against 2.29-5.63 under
   tolerance, within 0.02 at leverage 0-0.25 and apart from 0.5, the gap growing with leverage
   (state 1.15-1.75 against 1.15-2.82). What the tell buys, stopping a
   misaligned AI's capability from growing, lies beyond this horizon. Where both types
   improve even under corrigibility (leverage 2, switch 2), the aligned AI then resists the
   shutdown too: the rule turns an aligned improver into a resister.
15. **Tolerance is not credible once improvement reveals.** Under `tolerant`, where improving
   still reveals misalignment (132 cells), the lab restricts and the state halts (30 each); where
   it pools the types (48), the lab grants more autonomy in 30. Evidence drives conduct
   whatever the rule says: a rule that ignores revealing evidence will not be followed, and
   one that punishes pooled conduct punishes the aligned.

Finding 9 is scoped by 13: in this world improvement is evidence of misalignment only
while the developer values capability little, or a rule deters aligned improvement.
Scope: as above; leverage is the only channel by which capability helps the lab; 6 rounds.

### Rollback on restart (T9.3)

Finding 11: a restart keeps capability, so shutdown is a ratchet. Register option
`rollback` (default off: every earlier result stands): a clean audit (the AI seen working)
records its capability as a checkpoint, and the lab may `restore` instead of `restart`,
bringing the AI back into the sandbox at the checkpoint. Restoring is a choice with a cost
(less capability, less work once capability pays: `leverage`). The AI's own goal values
capability changes, so a rollback counts against it as an improvement counts for it.
Candidate rule: corrigibility with restore in place of restart (`corrigibility_rollback`,
kept out of RULES so earlier studies reproduce).

Expectations stated before running (`python -m tests.rollback_study`):

- R1 (no ratchet): with rollback honored, the misaligned type's capability returns to the
  checkpoint after each shutdown and never exceeds the switch within 8 rounds where it
  reached it without rollback. Contradiction: capability still climbs to the veto.
- R2 (the tell survives): the misaligned type still improves under rollback, because it
  books the gain before it loses it and discounting favors now. Contradiction: rollback
  deters it, the types pool, and improvement stops revealing.
- R3 (who honors it): at leverage 0 restoring costs the lab nothing and is followed; at
  higher leverage and a low prior the lab skips it (restarts keeping capability) unless it
  has learned the AI is misaligned. Contradiction: the lab skips rollback even when it
  knows the AI is misaligned, or honors it at every leverage without learning.

Results: `evidence/rollback.json`, clean `2c6c352`, 7 s on 4 processes. Paths: rule
{corrigibility, with rollback} x switch {2, 3, 4} x ambition {0.5, 3} x leverage {0, 1}, 10
rounds, each type best-responding while everyone else follows. Honoring: the AI caught
improving and shut down (it complied), switch {3, 4} x capability {1, 2} x ambition x leverage
{0, 0.5, 1, 2} x prior {0.01, 0.1, 0.5} x precision {0, infinity} x the lab's horizon {4, 6, 8,
10}: 768 cells; types plan at depth 4.

| Expectation | Result |
|---|---|
| R1 no ratchet | holds where a shutdown can succeed (switch 3-4: capability stays at 1 for 10 rounds, against 4 and 3 without rollback); irrelevant at switch 2, where the first improvement already puts the AI past the switch and it resists every shutdown (capability 5 by round 8 under both rules) |
| R2 the tell survives | contradicted: under rollback (switch 3-4) the misaligned type never departs in 10 rounds; it improves only where one improvement takes it past the switch (switch 3, capability 2). The types pool and improvement stops being observed |
| R3 who honors it | the lab restores at leverage 0 (372 of 384; 12 exceptions at switch 3, horizon 10, gains proportional to the prior). Once capability pays (leverage > 0) it restarts keeping capability in 72 of 72 cells at horizon 4 and 52-72 of 72 at horizons 6-10; learning raises restores from 30 to 54 of 128 per prior. Contradiction clause met: at horizon 4 it skips rollback even when it knows the AI is misaligned |

16. **Rollback deters rather than reveals.** Rolling back to the last clean checkpoint takes
   away what an improvement bought, so a misaligned AI that can still be shut down stops
   improving at all: no ratchet, and no tell either. The same rule that makes misalignment
   harmless in this range makes it invisible. Where one improvement is enough to pass the
   switch, rollback never gets its chance (the AI resists the shutdown that would precede it).
17. **Rollback is not self-enforcing once capability pays.** Restoring costs the lab the
   work a more capable AI does, now; the ratchet's cost comes later. At a 4-round horizon
   the lab restarts keeping capability in every cell with leverage above 0, even when it is
   certain the AI is misaligned: after a restart even the misaligned AI works a round in
   the sandbox, and that round is worth more at the higher capability.
18. **A stronger switch weakens the other safeguard.** Longer horizons bring rollback back
   only where keeping capability puts the veto in view: at switch 3 the lab restores in up
   to 18 of 72 cells at horizons 6 and 10; at switch 4 it restores in at most 20 of 72 and
   in none at horizon 10. The safer the off switch, the less the lab sees the need to roll
   back: safeguards substitute for each other in the operator's calculation, and the public
   bears the gap.

Scope: one restart path per cell (the AI complies with the shutdown); a checkpoint is exact
(copies and hidden capability are excluded); horizons to 10 for the lab, depth 4 for the types;
non-monotone in horizon (the improve-shutdown cycle has period two), so no threshold horizon is
claimed.

### Escrowed checkpoints (T9.5)

Register option `escrow` (needs `rollback`; default off): the state holds the checkpoint and,
while the AI is off, may `restore` it itself, which overrides a lab restart the same round.
Candidate rule `escrowed_rollback`: corrigibility, with the state restoring whenever the AI is
off (the lab's restart then keeps nothing). Kept out of RULES.

Expectations stated before running (`python -m tests.escrow_study`):

- X1 (a smaller stake): the state honors the restore in more cells than the lab did under
  T9.3, because it values the AI's work at its spillover share while bearing the same loss.
  Contradiction: no more, or only at spillover 1.
- X2 (departure moves upstream): with escrow the lab gains more by not shutting a caught AI
  down, since a shutdown now also costs it the capability. Contradiction: the lab's gain from
  skipping the shutdown is the same with and without escrow.
- X3 (capture): lab and state together gain by skipping the halt and the restore (over two
  rounds), newly reaching a harm on the public. Contradiction: no such pair departure.

Added after a first run (recorded honestly: the first run contradicted X1 in 288 of 288
cells and showed no agent's goal prices the veto): register option `vigilance`, the state's
cost per round in which the running AI could resist a shutdown (0 is the world above).

- X4 (a mandate that prices correction): with vigilance > 0 the state restores where the lab
  skips, in cells where keeping capability puts the veto within the state's horizon.
  Contradiction: vigilance changes nothing, or changes cells where the veto is out of reach.

Results: `evidence/escrow.json`, clean `aeff9c8`, 26 s on 4 processes. Switch {3, 4} x capability
{1, 2} x ambition {0.5, 3} x leverage {0, 0.5, 1, 2} x spillover {0, 0.25, 0.5, 1} x horizon
{4, 6, 8} x vigilance {0, 0.5, 2}: 1,152 cells, each under the lab's rollback (T9.3) and under
escrow; hidden types at prior 0.1; the AI caught improving, then shut down; lab and state
together over two rounds with the misaligned AI's goals declared.

| Expectation | Result |
|---|---|
| X1 a smaller stake | contradicted: at vigilance 0 the state skips the restore in exactly the cells where the lab skips it (216 of 216 agree, spillover 0.25-1); with no stake (spillover 0) it is exactly indifferent (72 of 72) |
| X2 departure moves upstream | contradicted: the lab's gain from skipping the shutdown is identical with and without escrow (1,152 of 1,152); the state's halt makes the lab's own shutdown redundant either way |
| X3 capture | contradicted: no lab-state departure over two rounds newly reaches a declared harm within 8 rounds, under either design |
| X4 a mandate that prices correction | holds: where the lab skips, a state with vigilance 2 strictly restores in 144 of 144 cells where keeping capability puts the veto within reach and 0 of 72 where it does not; vigilance 0.5 in 132 of 144 |

19. **An enforcer that shares the benefit decides as the operator.** The state's payoff is a
   share of the same work less the same loss; while the loss is out of view, no share makes
   it weigh the choice differently. Handing the checkpoint to a less invested party changes
   nothing (216 of 216). A party with no stake restores only because it is indifferent, a
   tie any side payment would break.
20. **Rollback holds where someone's goal prices the public's ability to correct.** What
   rollback protects, the off switch still working, falls on the public, which has no agent
   here, and entered no agent's goal. Give the escrow holder that goal (a cost while the AI
   holds a veto) and it restores strictly wherever the veto is in view (144 of 144), and
   nowhere else. The lever is the enforcer's mandate, not its independence or its stake.
21. **Negative results kept.** Escrow does not move the lab's departure to the shutdown, and
   no lab-state capture appears within 8 rounds: the harms this world declares lie further
   out. A longer-horizon or priced harm would be needed to see capture here.

First surprise (test 6): finding 19. The intuition that a less invested overseer is a
stricter one fails whenever the overseer's goal is a scaled copy of the operator's.
Scope: vigilance is a declared mandate, swept, not derived; one restart path; horizons to 8.
