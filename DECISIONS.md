# Decisions

Log of changes to the core (`INTENT.md`, `spec/`, `engine/`). Newest first. Each entry names the intent tests it serves and the case that motivated it.

```
## YYYY-MM-DD  short title
Change / Motivated by / Intent tests / Alternatives rejected
```

## 2026-09-23  E2 step 2: declared symmetry inside composites; a generic invariance check

Proposed before implementation. Composites claim no symmetry, so every whole is enumerated
by identities and the one composite stops at three actors: the fishery under the race has
one fisher. Whether a population of bystanders can protect what a few actors draw on is the
externalization question at scale, and it cannot be asked.

Change:
- `Composite.types()` derives the groups from the parts: two actors are exchangeable in the
  whole when, in every part, both are absent or both sit in the same declared group. The
  coupling is the one place the parts' declarations cannot vouch for, so the composite takes
  `couple_reads`: actors whose actions or part states the coupling reads by identity; each
  is split into its own group. A coupling given without `couple_reads` claims no symmetry
  (every actor alone), which is the safe default. The coupling must read part states only
  through what the parts' `physical` keeps symmetric; stated, and tested.
- `engine.power.symmetry_violations(world, states, rng, samples)`: for every declared group
  of two or more, sampled joint actions and swaps of two members' actions; reports any
  change in the successor distribution over `physical` keys, in harms, or in members' menus.
  Any world's `types()` can now be tested the same way instead of by a per-world test.
- `worlds/race_commons.py` gains `fishers` (register): the commons part has 2 + fishers
  users. `draw` stays in low takes of the three-harvester fishery (an absolute amount per
  build), so the race's demand on the stock does not shrink as more people share it and
  the E4 evidence reproduces at fishers = 1.

Also fixed: repeated CLI list flags (`--fix`, `--state`, `--pay`, `--target`) accumulate; a
second `--fix` used to replace the first silently, dropping a stated assumption.

What it assumes and loses: exchangeable fishers are an authored claim (same menus, channels
and role), checked by sampling, not proved. Power only; the planner is unchanged.

Alternatives rejected: a composite-level `types` override (no check against the parts);
inferring the coupling's reads by instrumentation (brittle); mean field over fishers (not
exact; exact runs still fit).

Intent tests: 1 derived from existing declarations, one argument; 2 no behavior; 3 the
claim is declared and checked by a generic test; 4 reduced equals unreduced where both run;
5 who must coordinate to prevent a harm on many, and who alone can force it, at population
size; 6 whether a few actors' power over a shared resource dilutes with population.

## 2026-09-23  E12 (reduced form): precaution against revealed departers

Proposed before implementation. T9.2 showed that one-shot checks give precaution no value:
after a departure everyone is assumed to follow the rule again, so shutting down an agent
caught departing guards against nothing. The principled fix is learning over hidden types
(beliefs from records by Bayes); it needs each type's policy, an equilibrium question.
The reduced form, general and cheap: with `precaution`, at a state reached by j's
departure, other agents are checked against a j that keeps optimizing for itself (its best
response by backward induction, full information) while everyone else follows the rule.
That states the belief "a revealed departer persists" as an assumption, reported with the
result. A toy reference (a thief who is locked out) shows a trigger that is credible only
under it. Default off: every earlier result stands.

Scope: one revealed departer per state; the departer's own check is unchanged.
Amended the same day: `precaution` may be a probability q, the posterior that the departer
is a persisting type, computed by the case from a declared prior and a declared evidence
model (how likely each type is to depart) by Bayes; others' values mix the persisting and
the returning continuation before the best action is taken. What remains open is deriving
the evidence model from the types' own best responses (an equilibrium question).

Intent tests: 1 one option on the existing check; 2 conduct still computed; 3 the belief is
declared, not hidden; 4 a toy where the answer flips; 5 precautions that protect the public
become checkable; 6 whether a precaution is credible becomes a question with an answer.

## 2026-09-23  E11: delegation with drift as a goal module; AI systems as agents

Proposed before implementation. The spec's delegation primitive (an agent grants
capability to a sub-agent and sets its goal; the set goal drifts) was never implemented.
It is the structure of AI control (a lab grants an AI system access; its goal may drift),
of armies, firms and bureaucracies. The owner's standing approval (2026-09-23: "where
something is useful or needed to progress towards intent, view it as approved") covers
the scope step from the first frontier case (AI as a stock) to AI systems as agents.

Change: `engine/delegation.py`, `Delegation(world, principals, drift)`: for each declared
delegate, utility becomes (1 - drift) x its principal's utility + drift x its own (the
world's value for it), drift a swept assumption per delegate. Kernel, observations,
menus and harms are untouched: goal-free power cannot change (tested); drift changes
whether rules hold and what agents do. Granting capability is world mechanics (the
authority world's office, the control world's autonomy), not engine state: the engine does
not create agents mid-run; delegates exist from the start with whatever capability the
state gives them.

Scope: fixed agent set; drift is a mixture of two declared goals, not a learned or
hidden goal (hidden goals are a belief question for a later case).

Alternatives rejected: creating agents during a run (the agent set is part of every
query's enumeration; a delegate with zero capability is the same thing, finitely);
goal drift as noise on actions (scripts behavior instead of changing goals).

Intent tests: 1 one wrapper; 2 behavior still computed; 3 drift swept and declared; 4 the
off-switch result (a delegate sharing its principal's goal accepts shutdown) is a reference
that can fail; 5 loss of control falls on people with no agent and is named; 6 at what
autonomy correction is lost, and whether principal and delegate capture oversight together.

## 2026-09-23  E10: amendable rules (a constitution module over any world)

Proposed before implementation. The spec's rules have levels (L0 conduct; L1 who changes
L0; L2 who changes L1), and INTENT asks protocol proposals to specify amendment. Rules as
claims (E7) are fixed profiles: nothing can change which rule is in force, so capture by
rewriting the rules, the route standard-setting and regulatory capture usually take, is
invisible.

Change (`engine/constitution.py`): `Constitution(world, regimes, voters, threshold, initial)`
wraps any world. The regime in force is a public fact in the state. Declared voters add a
vote to each action ("keep" or "amend:<regime>"); when at least `threshold` votes name the
same regime it is in force from the next round. The constitutional rule is: follow the
conduct of the regime in force and vote to keep it. Nothing in the kernel changes, so
goal-free power cannot change (tested); what changes is which conduct the others follow if
they treat the regime in force as binding, which is the assumption under test. The rule
checks then show which coalitions gain by amending (one round or coordinated over rounds)
and whether the harms of the new regime land outside them. Voters and threshold are the
L1 rule; L2 (who changes voters and threshold) is the same module nested, not yet needed.

Scope: finite regime menu declared by the case; one vote per voter per round; no
deliberation, agenda control or courts.

Alternatives rejected: a regime switch inside each world (a patch per case); modeling
legitimacy as a goal term (hides the obedience assumption instead of stating it).

Intent tests: 1 one wrapper reusing the rule checks; 2 amendment is chosen, not scripted;
3 voters, threshold and regime menu declared; 4 a regime can be captured by amendment or
not, and the check shows which; 5 the harms of the amended regime are named with who bears
them; 6 capture of the rulebook, not of the regulator, becomes computable.

## 2026-09-23  T9.1 scope (owner, ASK answered)

The owner chose the first frontier-AI scenario's boundary: two labs racing, a third-party
evaluator paid by the labs, a state that can license or halt; AI systems as a capability
stock, not agents. Recorded in `rediscovery/frontier-ai.md`. AI systems as agents
(delegation with drift) and an international compute race were the alternatives offered;
they remain future cases.

## 2026-09-23  E9: public records as a module over any world

Proposed before implementation. Rules can condition only on the current observation. In
the authority world an accountability rule cannot tell citizens organizing after an
extraction (a warning) from a commander organizing for himself (a coup), because nothing
remembers why anyone organized: the commander uses the rule's own clause. Real
institutions keep records: court files, audit histories, election results. The engine
says worlds must model memory themselves; each world would grow its own history fields.

Change (`engine/history.py`): `History(world, length)` wraps any world (including a wrapped
one). Worlds declare `public(state)`, the facts anyone could record (default: none, so a
world must opt in). The wrapper keeps the last `length` public records in the state; every
observation gains them. Beliefs lift the inner world's with the record known exactly.
Physical state, kernel, harms and labels are untouched: goal-free power cannot change
(tested). Rules for a wrapped world read `observation["now"]` and `observation["record"]`.

Scope: public records only (no private memory, no learning over hidden types); bounded
length; no forgery or deletion of records (a later module could make records contestable).

Alternatives rejected: history fields added per world (a patch each time); private
per-agent memories (hidden states of others' memories multiply beliefs; no case needs it).

Intent tests: 1 one wrapper; 2 no behavior; 3 length and what is public declared; 4 a rule
that fails without records can be checked with them, and may still fail; 5 records are
how externalized harm becomes attributable; 6 whether an institution's memory is what
makes it hold becomes a question the tool can answer.

## 2026-09-23  E8: side payments as a module over any world

Proposed before implementation. E7's coalition results assume transferable utility, but no
world has a way to pay anyone. The new `every_member` flag shows the audit capture needs
side payments (the auditor gains nothing from leniency itself), so "capture is a pair's
act" rested on an assumption, not on the model. Real capture has a payment (consulting fees,
higher fees); loyalty is bought (the ruler pays the army); treaties trade concessions.

Change (`engine/transfers.py`): `Transfers(world, pairs, amounts, disclosure)` wraps any
world. Each agent's action becomes (world action, transfer), the transfer "none" or a
payment of a declared amount to a declared recipient. Payments are utility, move with
the round, are unconditional within the round (no contracts), and are not limited by
wealth (declared). The base kernel, physical state, harms, stakeholders and terminal
labels are untouched, so goal-free power is unchanged by construction (tested).
`disclosure` sets who sees a payment: the two parties, or everyone. Beliefs lift the base
world's; unseen payments are believed absent (point prior, declared). Rules lift with
"pay nothing". A module in the spec's sense: an intervention any world can take.

Scope: one payment per agent per round, declared pairs and amounts only; no enforcement
of promised payments; no budgets.

Alternatives rejected: a bribe action inside the audit world (a patch for one case);
assuming transferable utility in reports (what E7 did; now it is flagged instead);
contracts or escrow (no case needs them yet).

Intent tests: 1 one wrapper over the existing interface; 2 who pays whom is chosen, not
scripted; 3 amounts, pairs and disclosure declared; 4 the audit capture can now be checked
without the assumption, and may fail; 5 side payments are how harms are bought, and
disclosure decides who can see them; 6 bought loyalty and bought leniency in one mechanism.

## 2026-09-23  E7: rules as claims; self-enforcement and profitable deviation

Proposed before implementation. Owner direction: build interesting systems and fill what
is missing with general capabilities. Every institution so far lives in a kernel
(sanction contests, verification channels, office) or nowhere. The spec says a rule is a
claim, not a constraint, but nothing implements it. The tool can say what coalitions could
force (power) and what heuristic agents do (planner), not whether a proposed rule holds:
whether anyone gains by breaking it, and which groups gain by breaking it together while
someone outside bears the cost. That is the test any protocol proposal must pass, and
capture is its coalition form.

Change (`engine/rules.py`, over any world):
- A rule is declared conduct: a function (world, observation, agent) -> action, one for
  every agent, reading only that agent's observation. Worlds publish candidate rules as
  `RULES` (name -> function, with the claim in its docstring). The kernel is untouched:
  following is a choice. A rule is a proposal under test, not a behavior script.
- `follow_value`: everyone's expected discounted value within D rounds if all follow.
- One-shot departures: depart now, then everyone follows for the rest of D rounds. A
  multi-round best response truncated at D would always find end-game departures, an
  artifact of the truncation, not of the rule. Checked at the start and at every state
  reachable within `reach` rounds with at most one departure per round, so punishments the
  rule prescribes off its path are checked too (the one-shot deviation test, bounded).
  Value beyond D is not counted for following or punishing alike.
- Unilateral: information-respecting; the agent picks one action for its observation,
  valued over its own beliefs; gain over following under the same beliefs.
- Coalition: full information and transferable utility (members' summed value, an upper
  bound). Reports per-member gains, what non-members lose, and declared harms the
  departure newly reaches, with the stakeholders outside the coalition they fall on.
  Amended the same day (T9.1): every member must depart; a "pair" where one member only
  receives a payment repeated the other's unilateral departure. Reports also separate
  departures paying every member without side payments (E8) and, for single agents,
  departures that newly reach a harm from harmless ones. Externalizing (capture) departures
  must need the coalition: its summed gain must beat what any one member achieves by
  departing alone (exact for pairs; larger coalitions are compared with single members
  only).
- Amended again (T9.1, binding certification): one-round coalition checks cannot see
  coordinated departures spread over rounds (an evaluator's lenient report, then a lab's
  deployment on it). `window` > 1 adds `sequential`: the coalition's best coordinated
  departure over that many rounds, chosen round by round by summed value with full
  information, then everyone follows; capture if it beats what any one member achieves
  alone over the same window and newly lands a harm outside. Default window 1 keeps every
  earlier result.
- Work caps mark unresolved checks, never "holds".

Scope: finite depth D, no claim beyond it; one rule profile at a time; no belief learning.

Alternatives rejected: rules as kernel constraints (assert compliance); scripting norm
followers as a behavior type (hides the incentive question); a full equilibrium solver
(unbounded, and answers a different question than "does this proposal hold"); checking only
the root (misses incredible punishments); truncated multi-round best responses (end-game
artifacts; tried first in this session and replaced before any test).

Intent tests: 1 one interface, reused planner and kernel; 2 conduct is tested, not imposed;
3 depth, information and TU assumptions stated per report; 4 a proposed rule can fail, and
the witness shows how; 5 profitable departures that land on non-members are reported by
name; 6 capture and incredible punishment become computable in any world.

## 2026-09-23  E5: irreversibility computed as well as declared; correction and lock

Proposed before implementation. Irreversibility is a flag a world declares on a harm (or
a terminal label). A harm the kernel allows to be undone, but that nobody outside its
beneficiaries can undo, is reported as reversible and correctable: the report has a
hole exactly where INTENT's chain ends (concentration removes correction). No world
models authority, so the chain appears nowhere.

Change (`engine/power.py`, goal-free, over any world):
- At a state where a harm holds, beside the existing `correct` (smallest coalition that
  can end it within T): `keep`, the smallest coalition that can keep it for T rounds
  against everyone else (the prevent column of the same table, no new game), and
  `veto`, agents without whom nobody can end it (everyone but i cannot).
- `lock`, per harm: the smallest coalition C that can force, within T, a state where the
  harm holds and C can then keep it for T' more rounds against everyone. Nested: the
  outer target is "harm holds and C surely keeps it", evaluated by an inner game
  memoized by physical state. For a terminal harm lock equals force; so lock generalizes
  the irreversible flag: a harm that someone can lock is irreversible for everyone else
  within T', whatever its declaration.
- Declared irreversible harms are checked: if one is realized and some coalition can end
  it, the query raises. The declaration is then wrong.
- Certainty is exact. For p = 1 the alpha value (and prevent alpha) equals the value
  under randomized stage strategies: a mixture guarantees probability one only if every
  action in its support does. `threshold` no longer marks p = 1 sizes as upper bounds
  when brackets differ; p < 1 unchanged. Earlier artifacts printed such rows as "(upper
  bound)" conservatively; their values are unchanged.

Scope: inner keep is with certainty; T and T' are stated per report. Cost is the outer
game times inner games per visited state, exponential as before.

Alternatives rejected: an `entrenched` harm declared by each world (asserts the result);
physical dominance predicates such as "holder stronger than all others" (misses purges
and sequencing, and is world-specific); a separate correction primitive (the force/prevent
game already expresses ending and keeping a harm).

Intent tests: 1 reuses the power game, one nested target; 2 no behavior; 3 T' declared
and reported; 4 lock equals force on terminal harms, toy references; 5 makes locked
harms and veto players visible; 6 a harm declared reversible can be found locked.

## 2026-09-23  E2: exact symmetry reduction for power queries

Proposed before implementation. Power queries enumerate every coalition (2^n) and every
joint action per stage (menus^n). The commons stops at n=4; composites multiply menus.
Civilizational questions need populations, without trading exactness for a mean field.

Change: optional `World.types()` -> list of groups of exchangeable agent ids (default:
every agent alone, no reduction). A world declaring a group asserts that permuting those
agents' actions permutes nothing that matters: the successor distribution over
`physical` keys, menus and harms are invariant. Then (1) per stage, each side enumerates
multisets of actions per group instead of tuples (a representative assignment per
multiset); (2) `power_table` returns one row per count vector (coalition up to
permutation), with a representative coalition and the number it stands for; complements
and thresholds use the same canonical form. Exactness is claimed only under the declared
symmetry, and tests compare reduced and unreduced tables where both run.

What it assumes and loses: exchangeability is a modeling claim; agents that differ in
channels, capability or position are separate groups. Per-agent witnesses become "any k
of this group". The planner is unchanged (next step).

Alternatives rejected: mean field or sampling (not exact; saved for when exact fails and
calibrated against it); detecting symmetry automatically (costly and brittle; a
declaration is checkable).

Intent tests: 1 one optional declaration, one reduction; 2 no behavior; 3 symmetry is a
declared, tested assumption; 4 reduced equals unreduced where both run; 5 lets harms be
mapped at population scale; 6 larger populations may show what n<=4 hid.

## 2026-09-23  E4: composition, so the whole system is the unit of analysis

Proposed before implementation. Owner note: externalization comes from analysing parts
and not how they affect the rest. Every world has been analysed alone, so a harm one
subsystem imposes on another could not appear in any report.

Change: `engine/compose.py`, a generic `Composite(World)` built from part worlds.
- Actors: each part's local agent ids map to global ids; one actor may act in several
  parts. Its action is a mapping part -> local action; its menu is the product of its
  parts' menus (one action where a part is already terminal). Planning settings belong to
  the composite (one actor, one planner); channels are the union of mapped part channels.
- State: one substate per part. The kernel runs the parts in a declared order, chance
  independent across parts, then applies a declared, deterministic `couple` function that
  carries flows between parts (for example a resource one part draws from another). The
  interface is an authored assumption, stated in the composite's module.
- Observations and beliefs: per part, product of part beliefs. An actor outside a part
  sees what that part shows a non-member; parts must accept outsider agents in `observe`
  and `beliefs` (public information only). Values add across parts.
- Terminal only when every part is terminal; harms are the parts' harms, prefixed by part,
  plus any the composite declares. Stakeholders are mapped to global names so the same
  people are one stakeholder across parts. Every part exclusion must be carried into the
  whole's EXCLUDED or listed in COVERS with how the whole models it (tested).

New query `joint_prevention`: for pairs of harms, smallest coalition that prevents each
alone and both together. A larger joint threshold means preventing one harm forces the
other: a tradeoff only the whole can show.

Scope: exponential in actors and menus; the first composite is small. No planner or
power semantics change; composition is a world.

Alternatives rejected: hand-writing each combined world (no general tool, no check that
parts reproduce); shared-field identity only (cannot express flows or conversions);
running parts separately and summing reports (misses exactly the interactions at issue).

Intent tests: 1 one generic composite; 2 no behavior; 3 interface, order and coverage
declared; 4 parts must reproduce alone and the comparison part-versus-whole is the test;
5 cross-part harms and uncovered exclusions become visible; 6 tradeoffs between harms.

## 2026-09-23  E1: harms and stakeholders are declared; externalization is a query

Proposed before implementation. Owner direction: analyse any system on many dimensions
without holes that create externalization. Affected groups have lived in case-file prose;
the engine could not see them, so a world could leave out the people a harm falls on and
every report would still look complete. Terminal labels were the only harm the power
query knew.

Change: every world module declares `STAKEHOLDERS` (name -> description, agents or not),
`HARMS` (name -> affected stakeholders, irreversible or not, description) and `EXCLUDED`
(name -> reason). World methods `stakeholders()` (stakeholder -> agent ids, possibly
none) and `harmed(state)` (set of harm names now realized; a function of `physical`
state). The defaults raise, so a world that declares nothing cannot produce a report.
Power targets may be a predicate as well as terminal labels. New query
`externalization(world, state, rounds)` reports per harm: smallest coalition that can
force it; smallest coalition that can force it *without any affected agent* (the harm
can be imposed from outside); smallest coalition that can prevent it; whether the
affected agents together can prevent it; affected stakeholders with no agent at all
(unrepresented: by construction they can neither prevent nor consent). CLI
`--externalities T`; artifacts record stakeholders, harms and exclusions.

Scope: power only, so goal-free; a harm list is an authored assumption like any other,
and the report makes it visible and contestable rather than true. Exponential in agents
until E2.

Alternatives rejected: a welfare aggregate (hides who bears the cost, INTENT test 5);
harms as terminal labels only (misses reversible and partial harms, and harms to
non-agents); scoring "externalization" as one number (a report per harm keeps the
dimensions apart).

Intent tests: 1 one declaration format and one query built on the existing one; 2 no
behavior; 3 stakeholders, harms and exclusions are declared data in every artifact; 4
toy references where the answer is known; 5 this is test 5 made executable; 6 shows
which harms fall on parties who cannot prevent them, which prose never checked.

## 2026-09-23  A1: the level-1 opponent model becomes a swept assumption

Proposed before implementation. Level 1 currently treats others as level-0 planners
only where they react: at future nodes, and only if they observe the actor. At the root,
and when unobserved, they repeat their last action. The treaty case (finding 4) showed
the root rule decides whether a trailing party anticipates a leader's build. A scratch
prototype of the textbook rule (every other agent is a level-0 planner at every node,
root included) changes the treaty defaults from 1 disarmament in 4 to 4 in 4, and the
commons baseline from collapse at 17 to collapse at 21. Two defensible models of bounded
reasoning give different answers; neither is established.

Change: `Agent.others` in {"react", "plan"}; "react" is the existing rule and the default,
so all recorded evidence stands. "plan" makes every other agent a level-0 planner from the
hypothetical state at every node; unobserved actions enter their plans only through
their own observations. Only level 1 reads it. Worlds expose it as the register key
`others` and sweep it.

Alternatives rejected: replacing the rule (hides a demonstrated dependence behind one
authored choice); a level-2 planner (no case needs it); treating the prototype's outcomes
as a correction (the new rule is not better established, only more standard).

Discriminating checks: "react" reproduces every existing test and artifact; "plan" gives
the prototype's treaty and commons outcomes; level 0 ignores the option.

Intent tests: 1 one flag on one branch of `q`; 2 no behavior scripted; 3 the opponent
model is now in the register; 4 the treaty result that depended on it is re-run both ways;
5 unchanged; 6 shows which behavioral findings survive a change of opponent model.

## 2026-09-23  T3.1: information-restricted sure power

Proposed before implementation. The T1.5 query gives both sides the full state, so it
cannot register verification, disclosure or any channel: a treaty case built on it would
contain its conclusion ("verification never changes power"). The case needs: can a
coalition guarantee an outcome using only what its members observe, against a fully
informed adversary?

Add `sure(world, state, coalition, rounds, target, goal, informed)`: finite-horizon sure
winning with observation-based strategies, via the knowledge-set construction (Reif 1984;
Chatterjee, Doyen, Henzinger and Raskin, "Algorithms for omega-regular games with
imperfect information", CSL 2006 / LMCS 2007). The coalition pools its members'
observations; its knowledge is the set of states consistent with them. Each round it
commits one joint action per knowledge set; the complement sees everything, including
that action, and picks the worst response per state; chance is adversarial (every
positive-probability branch). The coalition wins iff every possible play avoids (or
reaches) the target within T. `informed=True` replaces observations by the state itself,
giving the full-information sure value as a control. Knowledge sets are deduplicated by
`physical(state)`, which the T1.5 contract already requires to fix menus, kernel and
terminal status.

Scope: certainty only. Probabilistic values under imperfect information need policy
enumeration or a solver; not adopted until a case needs them. Randomized coalition
strategies can matter under imperfect information; this query reports deterministic
guarantees, a lower bound.

Discriminating checks: a hidden-bit toy where a blind guesser cannot guarantee but a
verified one can; informed sure values equal full-information values with chance treated
adversarially (commons paid design, deterministic stock: equals prevent_alpha == 1);
observation contract (all states in a knowledge set share the coalition's menu); work cap.

Intent tests: 1 one construction over the existing kernel and observe contract; 2 no
behavior; 3 certainty, pooled observations and adversarial chance declared; 4 blind versus
verified is the discriminating comparison; 5 names who can prevent an irreversible harm
given what they can see; 6 measures what information buys as denial, not as deterrence.

## 2026-09-23  T1.5: goal-free coalition power beside goal-driven behavior

Proposed before implementation. Every commons result so far depends on authored
goals, horizons, beliefs and planner depth, the assumptions INTENT says hide
opinion. INTENT's central questions (who can force an irreversible outcome, who
can prevent or correct it) are questions of power, answerable without goals.
Separating them distinguishes protection by deterrence (rests on the goals of
the capable) from protection by denial (holds whatever anyone wants). Unknown or
drifting goals of new agents, AI systems included, make the distinction central.

Add `engine/power.py`: finite-horizon, zero-sum reachability over the world's own
kernel. A coalition maximizes the probability of entering a flagged terminal
label within T rounds; the complement minimizes it as one coordinated adversary;
chance follows `outcomes`. Both sides see the full state and act by pure,
history-dependent strategies; menus still come from each agent's observation.
Two stage orders bracket the value: alpha (coalition commits each round first)
is what it can guarantee; beta (complement commits first) bounds it above. By
induction any randomized stage strategy lies between them, so equality is exact.
Prevention is the dual: prevent_alpha(C) = 1 - force_beta(complement of C).
Thresholds are the smallest coalition sizes reaching a stated probability, with
witnesses; unresolved sizes block a threshold claim. Work is capped per query as
in `core`; exhaustion is unresolved, never a power result.

One optional world method, `physical(state)`: the part of the state that
determines menus, kernel and terminal status. Default is the whole state. It is
only a memo key for the power query; a wrong projection is a world bug, tested
by comparing menus, successor projections and terminal status across states that
share it. Commons declares stock and collapse.

This implements the spec's lock-in and prevention queries in a bounded form
(T4.2/T4.3 remain for rule/authority worlds and correction of error states).
It is not a planner change and scripts no behavior; goals are unused.

Alternatives rejected: sampling adversaries (cannot certify a guarantee);
restricting coalitions to stationary strategies (understates power, hides
adaptive defense); a mixed-strategy LP per stage (needs a solver and is only
needed where the bracket is open); symmetry reduction by coalition size (an
assumption about the world; checked, not assumed).

Discriminating checks: hand-computed toy games (one where order matters, one
with chance), duality, monotonicity in coalition, invariance to goal/planner
parameters, projection validity, work-cap aborts.

Intent tests: 1 one query over the existing kernel, one optional projection;
2 no behavior computed or scripted; 3 query horizon, probability level and state
grid are recorded settings, and goal parameters drop out of the claim; 4
hypotheses and contradictions in `rediscovery/coalition-power.md` before runs;
5 names who can force or block an irreversible harm regardless of intent; 6
compare what agents do with what they could do.

## 2026-09-19  T1.4: exact reward integration at search leaves

Proposed before implementation. Baseline profile `2535e47` shows branch expansion,
not mostly repeated kernels: n=10/depth=2 after one all-high round exhausts 20,000
entries in 116 kernel calls (93 unique); n=4/depth=3 uses 17,589 transition entries
and 213 cached nested responses. Caching full state/joint kernels alone cannot
remove this exponential leaf cost. See `evidence/search-profile-before.json`.

Add `reward_outcomes(state, joint)`: a finite distribution of per-agent immediate
utilities whose expectation must equal `outcomes` followed by `value`. Default
derives it from that kernel. A world may supply a proved exact marginal reduction;
commons uses linearity of expected confiscation/receipts over independent contests.
Share round preparation and payoff arithmetic with the physical kernel. Use this
distribution only at depth 1, where no future action, observation or terminal test
depends on successor identity. Never evaluate nonlinear utility on mean state.
Charge every emitted reward entry, including zero weight, to the same root work cap.
Document the changed work unit; leave physical sampling and earlier branches intact.

Compare extension versus replacement: a factor-graph planner/world rewrite might
reduce interior branching but needs new conditional inference and information-set
proofs. Leaf reward integration is smaller, general across finite worlds and retains
the existing exact references. Reject mean-state planning, sampled tails, symmetry
assumptions and increasing the cap to call unresolved searches completed.

Discriminating checks: exact kernel/reward expectations across commons configurations,
threshold-crossing states and joint actions; optimized versus full-kernel planner
values/traces; nonlinear-risk and asymmetric hidden-information diagnostics; work
caps and zero-weight entries. Record measured numerical error, timings and remaining
unresolved rows. No approximation or new behavioral primitive is introduced.

Intent tests: 1 one optional exact marginal interface; 2 no behavior scripted;
3 fixed cap, source and workload explicit; 4 compare full enumeration and negative
coverage results; 5 utility losses remain branch-weighted; 6 measure which apparent
population limits were computational, without inferring institutional effects.

Outcome: adopt the reduction. The n=8/depth=2 contested decision completes in
5,241 entries versus 348,202 with full enumeration under a separate reference cap,
with equal values. Its 30-round runs now reach collapse at 17. Retained traces and
action probes agree; numerical marginal error is below 9e-16. Ten-user depth-2/3
limits remain, and some unresolved searches take longer. No population/horizon
extrapolation follows. Full evidence and boundaries: `rediscovery/search-reduction.md`.

## 2026-09-19  T1.3: finite belief-tree search and one transition kernel

Proposed before implementation. Replace constant-action rollouts and mean-state transitions with a finite stochastic kernel shared by planning and execution. Optimize future actions by observable history, integrating utility over physical branches before comparing actions. Replace the point projection with `observe(state, agent)` and `beliefs(observation, agent)`; menus receive observations. Group indistinguishable future branches into one posterior before selecting an action. This prevents future choices from acquiring hidden branch information.

Simplest implementation: enumerate finite outcomes and finite-depth action trees, with no heuristic tail or sampling inside planning. Level 0 retains repetition/priors. Level 1 recomputes direct observers' level-0 responses at future nodes, bounded by the remaining search depth and their own horizon. Known utilities/topology, explicit subjective priors, first-listed ties and receding-horizon execution remain assumptions. Belief history must be represented in observations when a world needs memory across real rounds.

Bound work before scaling: separate desired horizon from an explicit search-depth cap; commons sweeps depths 1/2/3, default 2 (the shortest resolving the motivating sequence). A declared transition-work budget aborts an incomplete decision, never selects from partial scores. Record unresolved runs separately from physical outcomes, including partial traces and planning limits. Compare short matched commons runs against both the old default horizon and horizon 2. Do not require previous survival claims to persist.

Motivated by: T1.0's investment (optimal sequence 3, repeated consume 2) and threshold case (risky expectation -4, mean-state evaluation 2). Discriminating additions: hidden versus revealed future branches, exact branch arithmetic, menu changes, terminal payoffs and budget exhaustion. This changes interfaces coherently; old artifacts remain reproducible at their source revisions, not through a second legacy planner.

Intent tests: 1 one kernel and one finite search; 2 actions and responses still computed; 3 priors, search caps and unresolved work explicit; 4 independent small references and contrary commons results retained; 5 severe branch losses no longer disappear into an average state; 6 test whether richer planning overturns the earlier norm result. Rejected: investment scripts, extra catastrophe penalties, full-state tree search with clairvoyant continuations, unbounded exhaustive search, and unvalidated sampling/aggregation to conceal cost.

T1.3 outcome: arithmetic, observation-grouping and budget checks pass. Commons' new depth-2 baseline collapses at 17, but an archived old horizon-2 control does too; old horizon 12 survives 30. Thus depth confounds the apparent reversal, and deeper-horizon conclusions remain open. Ten-user exact searches hit the cap. Adopt the coherent replacement with these limits, retire the old paths, and insert measured search reduction before population/channel claims. Details and timings: `rediscovery/planner-replacement.md`.

## 2026-09-19  T1.0: explicit planning information and directed response

Change: require each world to provide `belief_state(state, agent)`, a pure projection to a complete hypothetical state using permitted information and declared point priors. Both candidate menus and rollouts use that projection; actual execution uses the real state. Nested plans project the parent's hypothetical state, never recover the original truth. Expose `action_values` through the same path used by `plan`. At level 1, model agents that observe the acting agent, whether or not the actor can observe them. Channel topology and utility functions are treated as known; direct observation triggers one response, not arbitrary inference from public effects.

Motivated by: `rediscovery/planner-audit.md`, executable at pre-fix commit `ab6b02a`. A one-way observer should make take worth -1 rather than 2 over two rounds, but was omitted. An unrevealed hidden bit changed values and the selected guess despite identical information. The projection replaces implicit full-state planning with one explicit boundary, rather than adding private-field exceptions in every planner operation.

Limits retained: a point belief is not a belief distribution or a posterior update; world authors must enforce the projection contract and keep true private data out of planning methods/attributes. First-listed ties remain explicit. Investment and threshold counterexamples justify a subsequent shared search/transition redesign; no special-case strategy or risk penalty is inserted here. The commons' full/no-channel regressions and saved trajectory must still hold, but this audit does not validate them under stronger planning.

Intent tests: 1 one information boundary and one directed predicate; 2 responses still computed from goals; 3 point priors and known-model assumptions declared; 4 tests compare indistinguishable truths and exact toy references; 5 unilateral observation and utility-neutral side effects exposed; 6 wrong rankings arise even with adequate horizons and level-1 beliefs. Alternatives rejected: hidden-state masking in the CLI only; treating channels as symmetric; sticky tie rules without sensitivity evidence; world-specific investment/risk fixes.

## 2026-09-19  T1.0: preserve purpose, replace machinery when evidence warrants

Change: adopt the owner's explicit direction that any implementation, planner or model abstraction may be expanded or rebuilt while preserving the core purpose and evidence standards. Simplicity means few coherent mechanisms, not a fixed line count or perpetual compatibility. Compare extension with replacement; retire obsolete paths instead of stacking case-specific fixes. Preserve counterexamples and revisioned evidence across migrations. Internal ontology and aggregation changes need evidence and a decision record, not renewed permission; unresolved values and real-world scenario boundaries still need owner steering.

Motivated by: the owner's instruction to continue and not protect early prototypes at the expense of a more general, powerful tool. This relaxes the literal spec-size/shrinkage target and the assumption that the present agent ontology or planner is permanent. It does not authorize changing the purpose, scripting desired outcomes or asserting validity from passing tests.

Intent tests: 1 prefer the simplest adequate architecture, including replacement; 2 retain computed choices; 3 keep explicit assumptions and migrations; 4 compare against disconfirming cases; 5 preserve affected-party accounting; 6 let limitations force general improvements. Alternatives rejected: freezing v0; adding complexity merely for imagined future needs; rewriting without a discriminating test.

## 2026-09-19  T0.1: evidence before expansion

Change: propose and adopt replacing mandatory historical outcomes with falsifiable hypotheses. A failed expectation can expose a wrong hypothesis, setup, implementation, planner or primitive; it does not identify which. State that the current planner compares constant-action rollouts, uses cardinal per-round utility and expected transitions, and does not establish global optimality. Finite survival becomes `survived`, not an attractor. Keep dynamics and planner choices otherwise unchanged.

Motivated by: the owner's review and request to improve and publish. The commons with horizon 1 and no sanction is labeled sustained after one round but collapses at round five. The rediscovery guide treated every failed expectation as a missing primitive. This reverses that validation rule explicitly; prior findings remain in history and gain scope notes.

Implementation: JSON records for sweep, one-at-a-time and trace, with schema version, normalized source hashes, Git revision/dirty status, Python version, register, fixed reasons, parameters, integer seeds, requested/executed rounds, terminal status and final state. Canonical target iteration prevents Python hash order assigning random draws to different targets. Fixed CLI overrides remain fixed in one-at-a-time experiments. Validate overrides instead of silently accepting misspellings. Add CI on Windows and Linux.

Intent tests: 1 reuses existing simulation with no new primitive; 2 does not prescribe agent choices; 3 records assumptions and limitations; 4 permits disconfirmation; 5 retains per-agent wealth in evidence and requires excluded harms to be declared; 6 preserves the finite-duration counterexample and tests for artifacts. No validated institutional or civilizational protocol is claimed.

Alternatives rejected: adding worlds before correcting the evidence contract; implementing a stronger planner without a discriminating case; reporting sample shares as probabilities; using only a Git SHA when the working tree may differ.

## 2026-09-15  one-at-a-time sweep mode
Change: `engine/sweep.py` gains `one_at_a_time`; CLI `--oat`.
Motivated by: the commons. Sustained needs six conditions at once; a random sweep found it in 2% of samples with no parameter above the dependence threshold. Moving one parameter from a favorable baseline shows each necessary condition.
Intent tests: 3, 6. Alternatives rejected: raising the sample count (does not fix a conjunctive outcome); a smarter dependence statistic (premature).

## 2026-09-15  where confiscated takes go is a design parameter
Change: `worlds/commons.py` register gains `confiscation_to: stock | sanctioners`.
Motivated by: second-order free riding. With takes returned to the stock nobody sanctions at any size or cost; with takes paid to sanctioners the norm holds and restarts. This is an institutional design choice, so it is swept, not fixed.
Intent tests: 1 (a world-level parameter, no engine change), 5, 6.

## 2026-09-15  planner: level-k beliefs, k in the register
Change: `Agent.k`. Level 0: others repeat their last observed action, unobserved take the prior. Level 1: observed others are level-0 planners who respond once, at the first rollout step where the agent's action is visible, then hold. Modeled others use their own horizon.
Motivated by: the commons. Level 0 cannot hold a norm, established or not: readiness has no value to an agent that expects only repetition.
Intent tests: 2, 3. Strains 1: the engine grew. Alternatives rejected: full re-planning of modeled others every rollout step (six times the cost, same qualitative result expected; add when a case needs it, A1); sticky or conditional belief heuristics (scripting by another name).

## 2026-09-15  contest function: ratio of capabilities
Change: success probability for m equal sanctioners against one target is m/(m+1).
Motivated by: the commons needs a contest; this is the simplest member of the ratio family.
Intent tests: 1. Open: A2, add a second form only when a case's outcome depends on the form.

## 2026-09-15  worlds are Python modules
Change: a world is a Python file exposing SPACE, FIXED, DEFAULTS, make, describe. No YAML, no DSL.
Motivated by: goal functions and dynamics are code. A declarative layer would be a second language to maintain before any world repeats boilerplate.
Intent tests: 1. Revisit when three worlds share structure that could be declared.

## 2026-09-15  adoption of PRIMITIVES.md; removal of the static linter
Change: `spec/PRIMITIVES.md` is the model. Removed `analyzer/`, `components/`, `cases/`, `spec/SPEC.md`, `spec/actors.yaml`, `.github/`, `CONTRIBUTING.md`. INTENT.md rewritten; the six tests now lead with simplicity and non-scripting.
Motivated by: the owner's goal. Where the linter's ideas went: sinks and net-losers become attractor and coalition queries over agents whose goals include the cost; concentration and capture become the lock-in threshold (T4.2); adoption becomes what the planner chooses; the sweep survives as the register; the disclosure channel and compute attestation return as modules in the frontier scenario (T9.1); actors become types.
Intent tests: all six re-derived. Alternatives rejected: keeping the linter as a time-zero snapshot (two models to maintain).

## 2026-09-14  capture restricted to connected actors
Change to the removed linter; kept for history. Capture considered only actors with a flow to the component. Motivated by the lab-oversight case ranking unconnected actors highest.

## Open questions

- **Claims as one primitive.** Rules, money and legitimacy may be one thing: a claim, worth what others are believed to honor, backed by the contest enforcing it would win. The money brief must test this against alternatives. Under the 2026-09-19 standing direction, revise the spec through evidence and a decision record; owner steering is needed if values or real-world scope change.
- **Readiness tie.** Standing ready and not are tied in value when nobody defects; ties go to the earlier action, so readiness alternates each round. Cosmetic so far. T1.2.
- **Horizon of modeled others.** Level-1 rollouts give modeled others their full horizon, which dominates runtime. A shorter modeled horizon would be a new parameter. Not until T8.2 shows it matters.
- **Sanction targeting.** Sanctioners act against every visible defector. A case that needs selective targeting would reintroduce a choice, and the id tie-break showed how a targeting rule can leak asymmetry.
