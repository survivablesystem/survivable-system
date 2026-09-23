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
