# Concentration and correction (standing army, revised)

T4.0 evidence review, 2026-09-23. The earlier brief is kept below as the paper conjecture.
This case tests the chain named in INTENT: surveillance enables concentration,
concentration removes correction, uncorrected error becomes irreversible.

## Question

Who can end a harmful use of office, and when does that stop being possible? Two
separate questions, as in the treaty case:

- **Power (goal-free).** Which coalitions can depose a holder who extracts, which can keep
  extraction going against everyone else, and from which state on is it kept for good
  (entrenched)? Irreversibility here is political, not physical: nothing in the kernel
  forbids deposing the holder. So "irreversible" cannot be a declared flag; it must be
  computed (engine extension, decision first).
- **Behavior (goal-driven).** Do agents organize, rise, defend, purge? Conditional on
  planner reach and the opponent model (T1.8, A1).

## Sources and evidence status

| Claim | Source | Status here |
|---|---|---|
| Coup-proofing (loyal groups, parallel militaries, overlapping security agencies) makes a small group's seizure of power harder and lowers usable military power | Quinlivan, "Coup-proofing: Its Practice and Consequences in the Middle East", *International Security* 24(2), 1999, 131-165 | verified abstract |
| The resources that let repressive agents suppress opposition also let them act against the regime (moral hazard); strong apparatus guards against mass threats but raises coup risk | Svolik, *The Politics of Authoritarian Rule*, Cambridge UP 2012, ch. 5 | verified publisher summary |
| Counterbalancing lowers the success of coup attempts, not their frequency | De Bruin, "Preventing Coups d'etat: How Counterbalancing Works", *JCR* 62(7), 2018, 1433-1458 | verified abstract |
| Most coups occur in autocracies, and coups against autocrats can open paths to democratization | Thyne and Powell, "Coup d'etat or Coup d'Autocracy?", *Foreign Policy Analysis* 12(2), 2016, 192-213 | verified abstract |
| Limits on officials are self-enforcing only if citizens coordinate to police them; policing rights is a coordination problem | Weingast, "The Political Foundations of Democracy and the Rule of Law", *APSR* 91(2), 1997, 245-263 | verified abstract |
| Praetorian Guard, Mamluks and "most coups" decide succession | earlier brief | unsourced; not used |

## Hypotheses and rivals

- H1 (brief): whoever commands coercion decides who rules; splitting command raises the
  number of commanders needed to seize office.
- Rival M (moral hazard, Svolik; coups as correction, Thyne and Powell): the capability
  that lets agents usurp is the capability that lets them remove a harmful ruler. In a
  goal-free model the two are one act, deposing the holder. Splitting command should
  then raise the correction threshold against the ruler as much as the seizure threshold.
- H2 (INTENT chain): surveillance lets the holder purge organizers before they rise, so
  a holder becomes entrenched with less coercion and sooner.
- Rival W (coordination, Weingast): what stops a holder is citizens' coordination, which
  is belief and information, not capability. In a full-information power query that
  cannot show; a channel among citizens can change behavior only.
- Written succession rule alone: a rule that is not in the kernel cannot change any
  goal-free power value. That is a property of the query, stated here so it is not
  reported as a finding. Whether it changes behavior depends on goals and priors.

## Minimal world (proposal, `worlds/authority.py`)

Agents: a ruler holding office, `commands` commanders sharing an army of strength
`army`, `citizens` citizens of strength one each. Everyone's integer strength is public.
The holder may govern, extract (its own strength grows by `gain`, the conversion of office
into coercion; extraction harms citizens), or purge one agent it sees organizing (a
contest). Others may stay, defend the holder, organize (covert), or rise if they
organized last round. A rise is a contest between risers and holder plus defenders
(`contest`: threshold with `advantage`, or ratio). Success deposes the holder (strength
zero) and gives office to the strongest riser; failure disarms the risers. Strength does
not regrow. `surveillance` (none, army, all) sets whose organizing the holder sees and
so whom it can purge; `assembly` (none, all) sets whether non-holders see each other
organize. Office carries the surveillance apparatus to whoever holds it.

Harms: `extraction` (reversible, on citizens and the governed population without an
agent), `citizen disarmed` (irreversible by the kernel: strength never regrows).

## Expectations stated before runs

- P1 (rival M against H1): with the army split (commands 2, same total), the smallest
  coalition that can depose an extracting ruler grows exactly where the smallest coalition
  of commanders that can seize office grows. Contradiction: a setting where splitting
  raises the seizure threshold and leaves correction no harder.
- P2 (H2): with surveillance, the ruler alone can entrench extraction (lock) at lower
  initial guard or within fewer rounds. Contradiction: no lock value changes with
  surveillance.
- P3 (point of no return): the round from which the holder alone can keep extraction
  against everyone comes before the holder's strength exceeds `advantage` times everyone
  else's (physical dominance). Contradiction: the two coincide in every tested run.
- P4 (rival W): `assembly` changes no power value (by construction, stated), and changes
  some behavioral outcomes. Contradiction for the behavioral half: no outcome changes.

## Affected and excluded

Modeled: ruler, commanders, citizens (agents); the governed population and future
people (no agent) bear extraction. Excluded and named: external threats (the reason for
an army, and Svolik's mass threat), production and the economy (extraction is a flow of
harm only), soldiers as individuals (a commander controls its unit: delegation drift is
complete by assumption), succession at the ruler's exit (the brief's original setting),
foreign intervention, legitimacy beliefs beyond level 1.

## Engine findings (E5, 2026-09-23)

Artifact `evidence/authority.json`, clean `67b7fcb`, 20 min on 4 processes;
`python -m tests.authority_study`. Two citizens, advantage 1.5 (threshold). Grid:
commands {1, 2} x army {2, 4} x guard {0, 1, 2} x gain {0, 1, 2} x contest x surveillance
(216 cells), from a ruler already extracting, T = K = 3. Certainty (p = 1) under the
threshold contest; p = 0.5 under ratio, where certainty is empty. Lock from the start
state over the army-4 cells (108), reach within 2 rounds, keep 3. Behavior: 60 register
samples (seed 4104), each run with assembly none and all, 12 rounds.

| Expectation | Result |
|---|---|
| P1 splitting raises correction where it raises seizure | holds: 14 cells raise both, none raise seizure alone; but 71 raise correction with seizure unchanged, and under ratio 6 cells make correction possible |
| P2 surveillance lets the ruler lock alone | holds in scope: the ruler locks alone in 9 of 108 cells, every one with surveillance; never without |
| P3 point of no return before physical dominance | holds: dominance at strength 4; the ruler alone keeps extraction from 3, 2 or 1 once purges or conversion exist (K = 3 and 5 agree) |
| P4 assembly changes behavior, not power | power unchanged by construction (tested); 4 of 60 outcomes change, both directions, all ratio with `others = plan` |

1. **Splitting command mostly makes correction harder, not seizure.** Commanders alone
   can rarely seize against everyone else (citizens can defend the ruler), so splitting
   changes their seizure threshold in 18 of 108 pairs. It raises the smallest coalition
   that can end the ruler's extraction without him in 85 (typically 2 to 3, 3 to 4).
   Coup-proofing is paid for in correction capacity, as rival M says, and far more often
   than it buys protection from a coup.
2. **Under decisive contests, splitting plus surveillance plus conversion entrenches the
   ruler.** Threshold, army 4, guard 1-2, gain 1-2, surveillance on: with one command
   nobody holds a veto on correction; with the army split the ruler alone does (5 cells).
   He can purge a half-command he could never purge whole, and extraction pays for the
   strength to do it. In the default trace with a split army the ruler is
   uncorrectable from round 2 onward. The brief lists splitting as the remedy; here it is
   the step that removes correction.
3. **Under probabilistic contests the sign reverses.** Ratio, army 2-4: splitting removes
   the ruler's veto in 6 cells. One purge per round cannot remove two commanders, so a
   split army is harder to disarm before it rises. Whether coup-proofing entrenches
   depends on how decisive contests are, a swept assumption (A2 now has a case).
4. **The point of no return comes well before dominance.** Physical dominance (the ruler
   stronger than everyone else divided by the advantage) needs strength 4. The ruler alone
   can keep extraction against everyone from 3 with one purge or one unit of conversion,
   from 2 with both or with gain 2, and from 1 with gain 2 and surveillance of everyone.
   Under the threshold contest the entrenching purge is of the weakest organizer, the one
   the ruler can win against: surveillance of citizens entrenched, surveillance of the
   (stronger) army alone did not. Under ratio, army surveillance did most of the work.
5. **Whoever deposes an extractor inherits the means to entrench.** Default trace: the
   commander deposes the ruler in round 2 (a correction: extraction stops for one round),
   extracts from round 3, and from then on holds a veto on ending it. Correction and
   usurpation are one act in this model; what follows depends on the new holder's goals,
   and nothing in the world constrains them.
6. **Behavior: every run ends with someone extracting** (120 of 120). This follows from
   goals, not from structure: rent is non-negative and extraction also buys strength, so
   extracting is never worse for a holder in the register. It is not a finding. Assembly
   changed 4 outcomes (3 toward deposition, 1 against), all under ratio contests with
   `others = plan`; power is blind to it, as stated.

First surprise (test 6): finding 2. The intervention the brief proposes against
lock-in is, with surveillance and conversion, what lets the ruler lock in; the tool
shows it because it asks who can still correct, not only who can seize.

Scope: at most five agents, K up to 5, one purge per round, no regrowth, no pay, no
succession, no external threat (the reason to have an army at all). Correction here
means deposition; nothing models rules, courts or elections that could end extraction
without a contest of strength. No claim about real regimes: the case supports "in this
model, coup-proofing trades protection from seizure for loss of correction, and whether
it entrenches the ruler depends on how decisive contests are".

## Rules as claims (E7, 2026-09-23)

`evidence/rules.json` (clean `a40ea9d`; re-run `893d2cf` with the amended coalition definition, unilateral
results identical), `python -m tests.rules_study`; one-shot departures,
states within 2 rounds, coalitions up to 2, transferable utility for coalitions.
Grid: assembly x surveillance x commands {1, 2} x army {2, 4} x gain {0, 1} x rent {0.5, 1.5},
depth 4.

- `loyalty` (the army defends whoever holds office) fails in 64/64 at the start: the
  ruler extracts, since defense is unconditional. The ruler needs nobody for it: after the
  amendment requiring the pair, no coalition's departure under loyalty needs its members;
  under `accountability`, the ruler and a commander who does not punish do (64/64).
- `accountability` (organize after extraction, rise once organized, defend a governing
  holder against organizers) holds for the ruler at the start in every cell, then fails
  off the start in 64/64: once organizing has begun, punishment is the same whether the
  ruler stops or not, so extracting again is free. A rule without marginal deterrence
  deters the first breach and none after it.
- Commanders profit from the rule's own "rise once organized" clause (organize, then rise
  as prescribed) in 44 of 64 cells: 28/32 without assembly, 16/32 with it. Whether
  citizens see each other organize changes no power value (finding P4) but halves the
  cells where a coup pays under this rule. Information channels decide which rules can
  hold, not what can be forced.

## E6: correction without a contest of strength (expectations before the sweep)

E7 showed `accountability` fails for two reasons: punishment is the same whether the
ruler stops or continues (no marginal deterrence), and a commander can use the rule's own
"rise once organized" clause. Two general modules address what the world lacked: side
payments (E8) let a rule ask for restitution instead of deposition; public records (E9)
let a rule tell a warning from a coup. `restitution` (in `worlds/authority.py`): the
holder repays the citizens the round after it extracts; everyone else organizes after an
extraction, rises only if the record shows the extraction and the holder extracted again
or did not repay, stands down once repaid, and defends a governing holder against
unwarranted organizing. Sweep: `tests/correction_study.py`.

- R1: repayment below rent / discount leaves the first extraction profitable; at or above
  it, the ruler's first breach is deterred. Contradiction: the ruler's gain does not
  depend on the amount.
- R2: without records, the commander's coup pays; with records and citizens who see each
  other organize, it does not. Contradiction: records do not change the commander's gain.
- R3: with payments seen only by the parties, commanders cannot see repayment and rise
  against a repaying ruler, so repaying stops paying and the rule fails. Contradiction:
  the rule holds with private payments.
- R4: when the ruler may also pay a commander, the ruler and commander together gain by
  extracting and buying the army's inaction, at the citizens' expense, without anyone
  losing (no transferable-utility assumption). Contradiction: no such pact pays every member.

### E6 results

`evidence/correction.json`, clean `2ccdfa6`; re-run clean `893d2cf` after the E7 amendments
(every holds/fails result identical), 3.5 min on 4 processes. Grid: assembly x
records {none, 2 rounds} x repayment {0.8, 1.0, 1.2, 1.5} x disclosure {parties, public} x
commands x army {2, 4} x contest x gain {0, 1} (512 cells), rent 1, discount 0.9, depth 4,
states within one round; pact grid: the full design plus ruler-to-commander payments of 0.5
or 1.0 (32 cells), pairs checked.

| Expectation | Result |
|---|---|
| R1 repayment below rent / discount leaves the first extraction profitable | holds: the ruler gains in 128/128 cells at 0.8 and 1.0, in 88/128 at 1.2 and 1.5 |
| R2 records and assembly stop the commander's coup | holds in part: a commander gains in 112/128 cells with either missing, 64/128 with both |
| R3 private payments break the rule | holds: 0/256 cells hold with parties-only disclosure |
| R4 ruler and commander gain by a bought pact | contradicted: 2/32 cells have a pact that needs both and where no member loses (8/32 before requiring the pair; six were the ruler's own extraction), and none uses a payment |

1. **Correction without deposition can hold.** The rule holds in 18/512 cells, 12 of the
   16 threshold cells with the full design (records, assembly, public payments, repayment
   at or above rent / discount). There the ruler repays instead of being removed, the
   first breach does not pay, continuing does not pay, and the record keeps the warning
   clause from being a coup license. Every part is needed: take away public payments,
   records or adequate repayment and it fails everywhere or nearly so.
2. **Repayment returns the rent, not the strength it bought.** The 4 threshold failures
   of the full design are all army 2 with gain 1: one extraction adds a unit of strength,
   which makes the ruler unremovable by the small army, and no repayment of rent undoes
   that. The conversion of office into coercion (E5 finding 4) is the part a fine cannot
   reach.
3. **Under probabilistic contests standing down does not hold.** All 16 ratio cells of the
   full design fail: organized citizens and commanders prefer to rise anyway, because any
   rise has some chance of winning office. Accountability by warning needs contests
   decisive enough that an unwarranted rise surely fails (A2's case grows).
4. **The pact that remains is not bought.** In the 2 cells where ruler and commander need
   each other, the commander gains by skipping the risky rise the rule asks of it, not by
   payment; loyalty payments were available and never chosen. The failure is the rule's
   demand on its enforcers, not the price of the army.
5. **The rules check caught two rule errors first.** Any payment counted as repayment (the
   ruler underpaid); fixed so only the declared amount counts. Recorded because a claim that
   leaves "how much" unstated is a hole a real institution would also have.

Scope: one-shot departures within 4 rounds, one round off the path, at most five agents,
utility payments without budgets, records of public facts only. No claim about real
constitutions: the case supports "in this model, correction by restitution holds only
with public payments, records and decisive contests, and cannot undo coercion bought by
the breach".

## Earlier brief (paper conjecture, 2026-09-15; unsourced, kept for history)

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

## Contest family (A2)

Finding 3 left open whether coup-proofing entrenches (finding 2) or protects correction
depending on how decisive contests are. Register option `contest = tullock`: an attack wins
with probability a^m / (a^m + (advantage x d)^m); m = 1 with advantage 1 is the ratio
contest (tested), large m decides at level one half as the threshold contest does (tested).
All forms are read at level p = 0.5, where the deterministic threshold contest decides as it
does at certainty, so the comparison does not change level with form.

Expectations stated before running (`python -m tests.contest_study`):

- A1 (a switch in decisiveness): over the cells of findings 2-3, the cells where splitting
  gives the ruler a veto on correction rise with m, and those where it removes one fall,
  crossing at some m between ratio and threshold. Contradiction: no monotone change in m.
- A2 (advantage): with the defender's advantage 1.5 the switch comes at a lower m than with
  advantage 1. Contradiction: advantage does not move it, or moves it the other way.

Results: `evidence/contest.json`, clean `21dda20`, 10 min on 4 processes. Army {2, 4} x guard
{1, 2} x gain {1, 2} x surveillance {army, all} (16 cells, citizens 2), each with one and two
commands, K = 3, level 0.5; forms: Tullock at advantage {1, 1.5} x m {1, 2, 4, 16, 64, 1024},
and the threshold contest as reference. The m = 1, advantage 1 rows equal the E5 ratio evidence
(32 of 32). After the first run (m to 16) showed no switch, m = 64 and 1024 and the threshold
reference were added; that run's rows reproduce exactly in the second.

Splitting command, per form: cells where it gives the ruler a veto on correction / removes it
/ ruler veto either way / neither.

| Form | gives | removes | both | neither |
|---|---|---|---|---|
| threshold (advantage 1.5, ties to the attacker) | 5 | 0 | 7 | 4 |
| Tullock, advantage 1.5, m = 1024 | 1 | 0 | 7 | 8 |
| Tullock, advantage 1.5, m = 2-64 | 0 | 0 | 8 | 8 |
| Tullock, advantage 1.5, m = 1 | 0 | 4 | 8 | 4 |
| Tullock, advantage 1, m = 1-64 (m = 1 is ratio) | 0 | 6 | 2 | 8 |
| Tullock, advantage 1, m = 1024 | 0 | 4 | 2 | 10 |

| Expectation | Result |
|---|---|
| A1 a switch in decisiveness | contradicted: no crossing. Between ratio and threshold lies a wide neutral band (advantage 1.5, m 2-64: splitting changes no veto); entrenchment appears only at the threshold itself |
| A2 advantage moves the switch | holds in another form: advantage decides more than decisiveness. At advantage 1 splitting protects correction at every m; at 1.5 it is neutral from m = 2 |

7. **Finding 2 rests on ties.** A Tullock contest with m = 1024 decides as the threshold
   contest does except at exact ties, where it gives one half instead of certainty to the
   attacker. It keeps 1 of finding 2's 5 entrenching cells. The ruler's purge of a
   half-command succeeds there only because an attack exactly equal to advantage x defense
   is declared a sure win. With integer strengths and advantage 1.5 such ties are common;
   the result is a property of the tie convention, not of decisiveness. Finding 2 is
   retained with this scope.
8. **Finding 3 is the wider result, but not a sign reversal.** Splitting removes the ruler's
   veto under ratio contests (4-6 cells) and, with no defender advantage, at every
   decisiveness short of the tie-deciding limit. With a defender advantage it does nothing
   from m = 2 on. Whether coup-proofing entrenches or protects is mostly decided by the
   defender's advantage and the tie rule; across most of the family it does neither.

First surprise (test 6): finding 7. A mechanism read off one contest form ("purge a
half-command you could never purge whole") was a tie in integer strengths.

## Term limits (E6 remainder)

Office changes hands today only by a successful rise, so a term limit cannot even be
stated. Register option `succession` (default off; states without it unchanged): the holder
may `yield`, passing office to the designated heir (the first commander, else the first
citizen, with strength) without a contest; it keeps its own strength. The state counts the
holder's `tenure`. Candidate rule `term limit` (kept out of RULES): the holder governs and
yields once its tenure reaches `term`; everyone defends a holder within its term, organizes
against one that extracts or overstays and rises once organized (accountability with a term:
a first draft without the extraction clause made extracting the holder's best departure and
confounded the question; changed before any study run).

Expectations stated before running (`python -m tests.term_study`):

- T1 (overstaying pays where strength accrues): the holder gains by overstaying (not yielding
  at the limit) where extraction converts into strength (gain > 0) and a rise against it
  would then fail. Contradiction: the limit holds for the holder at gain 2.
- T2 (the heir enforces): the heir gains by following the rule (rising against an overstayer)
  more often than any other agent, because it is the one the rule hands office to.
  Contradiction: the heir departs from enforcement as often as others.
- T3 (the retired strongman): after yielding, the former holder, keeping its strength, gains
  by rising against its successor where its strength suffices. Contradiction: no such gain.
- T4 (the shadow of the next turn), added after a two-cell probe showed overstaying paying
  even at gain 0 at depth 4: removal is also what compliance costs, so only the rotation
  (a deposed holder is disarmed and loses its turn) can deter; the limit holds for the
  holder only when a full rotation fits in its horizon. Contradiction: overstaying still pays
  at a horizon that covers the holder's next turn.
