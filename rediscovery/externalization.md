# Externalization: declared harms, stakeholders and exclusions

E1, 2026-09-23. A method case, not a historical one. Decision: `DECISIONS.md` 2026-09-23 (E1).

**Why.** Affected groups lived in case-file prose. A world could leave out the people a
harm falls on and every report would still look complete. Now each world declares
`STAKEHOLDERS` (agents or not), `HARMS` (predicates on physical state, the stakeholders
each falls on, irreversible or not) and `EXCLUDED` (what is left out, with a reason);
artifacts carry all three, and a world that declares nothing cannot produce a report.

**Query** (`engine.power.externalization`, CLI `--externalities T [--state k=v]`), per
harm, goal-free, with certainty within T: smallest coalition that can force it; smallest
that can force it *without any affected agent* (imposed from outside); smallest that can
prevent it; whether the affected agents together can prevent it; for a harm already
realized, smallest coalition that can end it (the spec's correction query, bounded);
affected stakeholders with no agent at all.

## Findings (`evidence/externalization.json`, clean `6b48e9b`, T=3)

1. **The commons' largest harms fall mostly on stakeholders with no agent.** Collapse
   falls on users, future users and stock-dependent others; depletion only on the last
   two. Neither of those can prevent or end anything by construction. At S=30 any two of
   three users can force depletion within 3 rounds; at S=8 one user can force collapse
   and only all three together can prevent it. Case files listed future users as
   "excluded"; declared as stakeholders, they show up as the main bearers.
2. **In the treaty, a leader with the advantage imposes disarmament from outside.** At
   lead 2, a alone forces "b disarmed"; b cannot prevent it; b's population, which bears
   it, has no agent. Verification and domains do not change these rows at T=3.
3. **Correction is a different threshold from prevention.** At S=20 the commons is
   already depleted; two users are enough to end it within 3 rounds, three within 1.

Limits: declarations are authored assumptions, as contestable as goals; the report makes
them visible, not true. Exponential in agents (E2). Each world is still analysed alone:
a harm one subsystem imposes on another is invisible until they are composed (E4).
