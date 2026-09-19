# Diagnostic cases: information and planning (T1.0)

These are constructed counterexamples with arithmetic reference answers, not historical claims. They test engine contracts before sparse channels or hidden-information worlds rely on them. Constants are named in the diagnostic fixtures; no result is a frequency estimate about real systems.

## Questions and disconfirmation

| Case | Setup and expected diagnostic | What would contradict the concern |
|---|---|---|
| Directed observation | Actor gets 1 from taking; a responding observer imposes 3. Horizon 2. Compare all four directions of the channel pair. | A one-way observer's response is anticipated even when the actor cannot observe it. |
| Hidden bit | An uninformed agent guesses a hidden bit, with a fixed prior guess 0. Compare otherwise indistinguishable states. | Hidden truth cannot change action values, menus or choices; a revealed bit can. |
| Ties | Two actions pay the actor equally; their side effects differ. Reverse action order. | The selected action is independent of menu order. |
| Investment | Over two rounds, consumption pays 1; investment costs 1 and enables later consumption of 4. | The planner values invest-then-consume (3) above consume-twice (2). |
| Threshold risk | Safe pays 1. Risky leaves stock 3 or 7 with equal chance; below threshold 4 pays -10, otherwise 2. | It compares branch-weighted utility (-4), not utility at mean stock 5 (2), and chooses safe. |

Diagnose first. An information-path defect can be repaired without claiming the other approximations are adequate. If investment and risk reverse decisions, retain the examples as acceptance cases for a coherent planner replacement, not world-specific workarounds.

Affected parties: directed observation includes an actor and responder; the tie example exposes side effects ignored by the actor's utility. The other fixtures use one decision-maker to isolate the computation. They do not represent future people, institutions, aggregate welfare or real-world catastrophe rates.

## Engine findings

Pre-fix source: `ab6b02a`, stored in `evidence/planner-audit-before.json`. Each artifact records engine source provenance and the diagnostic fixture hash. Run `python -m tests.planner_cases` for current values. `tests/test_planner_audit.py` contains the contracts and arithmetic checks.

| Case | Before | After the information repair | Interpretation |
|---|---|---|---|
| Actor cannot see responder; responder sees actor | take = 2; chooses take | take = -1, quiet = 0; chooses quiet | Response predicate used the wrong direction. |
| Neither sees the other, or only actor sees responder | take = 2 | take = 2 | Negative controls: no direct incoming observation means no modeled response. |
| Both see each other | take = -1 | take = -1 | Symmetric-channel control unchanged. |
| Hidden bit 0 versus 1; identical information | chooses 0 versus 1 | chooses 0 in both; values (1, 0) under the declared point prior | Full-state rollout leaked hidden truth. Revealing the bit still changes the choice. |
| Equal utilities, reversed menu | picks first action | still picks first action | Equal own utility does not imply equal side effects. Ordering remains a substantive assumption. |
| Invest then consume | repeated-invest value -2; consume-twice 2 | unchanged; exact sequence value 3 | More horizon alone does not supply a missing change of action. |
| Threshold risk | risky 2 > safe 1 | unchanged; exact risky value -4 < safe 1 | Expected state is not expected utility at an irreversible threshold. |

The first surprise is the direction reversal: observation of another agent is not observation by that agent. Full/no-channel commons tests could not expose it. All four directed configurations now have regression tests; hidden information is tested through menus, direct evaluation, nested response plans and actual execution with a wrong prior.

A world now declares `belief_state`; the engine uses it before enumerating candidates and rolling forward. The projection is a complete hypothetical state, not a deletion of fields needed by physics. A nested agent plans inside the parent's hypothesis. Authors must not restore hidden truth from world attributes. This is an explicit modeling contract, not a proof that every world obeys it.

The sequence gap holds for investment costs 0.5, 1 and 1.5 at return 4; the risk ranking reversal holds at low-stock probabilities 0.25, 0.5 and 0.75. With zero branch uncertainty the risk reference agrees with the current planner. These are exact toy comparisons, not a parameter sweep of an empirical case.

## Consequences for the commons and next architecture

The existing full/no-channel outcome regressions and archived collapse trajectory are retained as compatibility checks under this approximation. The audit establishes no general claim that paid sanctioning is necessary or sufficient, and no size effect. The missing-sequence and nonlinear-risk mechanisms could change those conclusions; compare them after the planner replacement.

T1.3 now comes before sparse-channel research. Develop one transition representation that supports branch-weighted utility and changing actions, rather than a separate investment rule and catastrophe penalty. Exact small cases anchor the implementation; larger searches need explicit limits and comparisons. A distribution over hidden states should replace the current point-belief path if required, not coexist as an inconsistent second truth.

Tests of the present approximation deliberately expose its gaps. During replacement, retain the information contracts and independent arithmetic references, and migrate assertions about the old planner's wrong ranking with a decision record. They are evidence to improve upon, not instructions to preserve the defect.
