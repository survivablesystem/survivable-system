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
