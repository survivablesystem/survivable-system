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
