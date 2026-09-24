# Whole versus parts: the race and the off switch

T9.6, 2026-09-23. A composition of `worlds/frontier.py` and `worlds/control.py`
(`worlds/race_control.py`, decisions `DECISIONS.md` 2026-09-23 E4 and its amendment). Not a
historical case: it tests INTENT's chain (competition removes correction) by putting a lab
that races and a lab that can shut its AI down in one actor.

**Setup.** Lab A races lab B (frontier part) and runs an AI system (control part); one
state oversees both, with its own goals in each part added. With `coupled`, lab A's AI is
its model in the race: after both parts run, lab A's race capability is at least its start
plus what the AI gained. The rule is the union of the parts' rules: licensing (frontier)
and corrigibility (control). Without the coupling the whole should reproduce its parts.

**Provenance of the expectations.** Written after one prototype probe (one caught state,
depth 3), which showed a lab A and state pair departing together with a halt of lab B. Y2
restates that observation as a claim to test across the grid; it is weaker evidence than Y1
and Y3, which the probe did not address.

**Expected before the study** (`python -m tests.race_control_study`):

- Y1 (the race buys tolerance): at a state where the AI has just been caught improving,
  lab A and the state together gain more by letting it run (skipping the shutdown and the
  halt) when coupled than uncoupled, because both value lab A's race capability.
  Contradiction: the pair's gain from skipping is the same coupled and uncoupled.
- Y2 (a national champion): the state's part of the pair's best departure includes halting
  lab B, with the harm (safe progress blocked) on users. Contradiction: rare or absent.
- Y3 (the veto stays defensive): goal-free power over the race harms does not gain the AI as
  a member of any smallest forcing coalition, because resisting a shutdown takes its turn.
  Contradiction: the AI appears in a smallest coalition forcing an unsafe deployment.

**Affected and excluded.** Lab A, lab B, the evaluator, the state and the AI are agents;
the public, users and future people are not. Every part exclusion is carried or covered
(frontier's "AI systems as agents" is covered by the control part; tested). Added: lab B's
AI, feedback from the race into the AI, the AI acting in the race other than through
capability.

## Findings (`evidence/race-control.json`, clean `6a24887`, 112 min on 4 processes)

Rules: coupled x drift {0, 1} x switch {2, 3, 4} x oversight {deployment, continuous} x first
{0, 3} x the AI's capability when caught {2, 3} x lab A deployed or not x depth {3, 4}: 384
cells, from the state where the AI was just caught improving at autonomy 1, lab A at its
safety margin. Power: coupled x switch x capability x deployed, T = 2 (24 states; almost all
of the run time: exact power over five actors whose menus multiply across parts).

| Expectation | Result |
|---|---|
| Y1 the race buys tolerance | contradicted: lab A and the state gain by letting the caught AI run in 384 of 384 cells, coupled or not; coupling never raises that gain (same in 144 of 192 matched cells, lower in 48) |
| Y2 a national champion | holds, only under race pressure: the pair's capture includes the state halting lab B in all 192 cells where a first mover is paid (first = 3) and in none where it is not; the harm (safe progress blocked) falls on users, every member gaining |
| Y3 the veto stays defensive | holds: goal-free power over unsafe deployment and catastrophe is identical coupled and uncoupled in 24 of 24 states, and the AI is in no smallest forcing coalition |

1. **The race adds no tolerance because there is none left to add.** The parts already
   tolerate a caught AI fully: shutting it down costs lab A its work and the state its
   share, and within 3-4 rounds nothing the shutdown prevents costs either of them (control
   findings 17-20). The expected chain (competition removes correction) does not run through
   this link here; correction was already gone before the race arrived.
2. **Where the race touches the AI, it disciplines rather than corrupts.** Coupling lowers
   the pair's gain from tolerance in 48 cells, all with lab A deployed and the AI at
   capability 3, and halves lab A's own gain from skipping the shutdown (96 to 48 cells, only
   capability 2 remains). The AI's gains push a deployed lab A past its safety margin, and
   the licensing rule makes lab A pay to secure. A race rule that prices the safety gap
   partly prices the AI's improvement too. Whether that holds without licensing is untested.
3. **Capture moves to the rival.** When first movers are paid, the lab A and state pair
   captures by halting lab B (users lose safe progress), never by letting the AI escape.
   The state acts as its champion's partner in the part where that pays.
4. **Lab A and its AI still capture oversight together** (control finding 5, reproduced in
   the whole): in 192 of 384 cells (96 coupled, 96 uncoupled) the pair gains by a resisted
   shutdown, the harm on the state and the public.

First surprise (test 6): finding 1. The whole shows the chain's weak link is earlier than
expected: the loss of correction is already priced out inside the lab before any race.
Scope: one state, two labs, one AI; the coupling is a floor; depth 3-4; T = 2 for power.

## Without licensing

Finding 2 credited licensing with the discipline. Rule `race + corrigibility`: the frontier
part without a regime (labs deploy and scale, the state allows), the control part as before.

Expectation stated before running (`python -m tests.race_rule_study`):

- Y4: without licensing, coupling raises the lab A and state pair's gain from tolerating a
  caught AI (the AI's gains are race capability nobody makes lab A pay to secure).
  Contradiction: coupling still lowers or leaves it unchanged.
