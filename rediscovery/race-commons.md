# Whole versus parts: an arms race on a shared fishery

E4, 2026-09-23. A composition of `worlds/treaty.py` and `worlds/commons.py`
(`worlds/race_commons.py`, decision `DECISIONS.md` 2026-09-23 E4). Not a historical case:
it tests whether analysing the whole shows harms the parts cannot.

**Setup.** East and west are both racing parties (treaty) and harvesters (commons); a
fisher only harvests. Each build removes `draw` low takes from the shared stock (the
authored interface; building does not require stock). Parts run their own kernels; the
coupling runs after both. Stakeholders are mapped to one set of names across parts;
every part exclusion is carried into the whole or covered (the fisher covers the
treaty's "third states"; tested).

**Expected before runs.** With `draw` 0 the whole reproduces the fishery alone (control).
With a positive draw, fishery harms become forceable by the racers, and a party may face
a forced choice between its own safety and the fishery. Contradiction: no row changes.

## Findings (`evidence/race-commons.json`, clean `2d220b6`, 5 min; T=2, p=1)

1. **The whole shows harms the parts do not.** 8 of 18 fishery harm rows differ between
   the fishery alone and the whole; all differences are at positive draws, none at draw 0.
   At S=30, draw 2: nobody can force collapse in the fishery alone; in the whole, east
   and west together can. Depletion, which needed two harvesters alone, can be forced by
   either racer by itself. Preventing it now needs both racers: the fisher is in no
   minimal preventing coalition. The bystander loses its power to protect the stock
   through a mechanism neither part contains.
2. **Forced choices appear only in the whole.** In 4 of 27 settings (all at draw 2), a
   coalition can prevent its own disarmament or the fishery's collapse, but not both: a
   racer alone at S=30; a racer together with the fisher at S=20. Preventing one harm
   forces the other on someone. No single-part query can show a tradeoff between harms
   that live in different parts.
3. **Behavior: the race brings the fishery's collapse forward, it does not cause it.**
   With the planner (react), 3 harvesters, r=0.3 and sanctions, the fishery alone
   "survives" 30 rounds, as does the whole at draw 0, but both are on a depletion cycle
   (stock 8.9 at round 30). One build at draw 0.5 moves collapse to round 29; at draw 2,
   to 25. The finite label hides a trajectory the power profile would flag. Under
   `others = plan` the composite exceeds the work cap by round 5: unresolved.

Limits: three actors, T=2 exact; the coupling is one authored flow. Exponential in actors
and menus (the composite's menus are products). Nothing here is about real fisheries or
arms races; it shows that the tool now finds cross-part harms when they exist in the model.

## A population of fishers (E2 step 2)

Decision `DECISIONS.md` 2026-09-23 (E2 step 2). Fishers are declared exchangeable inside the
whole (derived from the commons' declaration; the coupling reads only east and west). The
fishery has 2 + `fishers` harvesters; each build still removes `draw` low takes of the
three-harvester fishery, an absolute amount.

**Expected before runs** (T=2, p=1, S in 20/30/40, draw in 0/1/2, fishers 1 to 10):
- E-a. At draw 0 thresholds follow the fishery alone: shares, not numbers (coalition-power
  finding 9).
- E-b. At a positive draw, wherever one racer alone can force a fishery harm at one
  fisher, it still can at ten: the build is an absolute lever and the racer's own take
  shrinks only as 1/n. By duality no coalition without that racer can then prevent it.
- E-c. The smallest preventing coalition is both racers plus a number of fishers that grows
  with the population, so the gap between who can force the harm and how many must
  coordinate to stop it widens with n.
Contradiction: a single racer's forcing power disappears as fishers are added (dilution
protects the stock), or the preventing coalition stays at the two racers at every size.
