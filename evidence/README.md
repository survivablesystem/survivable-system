# Saved evidence

`commons-collapse.json` is a trace from clean source commit `f26e7f93bc44ccb953caacce0e27f39c1f2286de`. It uses the commons defaults with horizon 1, sanction capability off, seed 0 and a 30-round limit. Collapse occurs at round five. The first round alone would be labeled `survived`; neither finite result establishes an attractor.

Generate a fresh artifact from the matching source:

```sh
python -m engine worlds.commons --trace --rounds 30 --seed 0 --fix horizon=1 sanction=false --json
```

Replay the saved trajectory from the repository root:

```python
import json
from engine.records import run_record
from worlds import commons

with open("evidence/commons-collapse.json", encoding="utf-8") as f:
    evidence = json.load(f)
saved = evidence["results"][0]
actual = run_record(commons.make, saved["params"], saved["rounds_requested"],
                    saved["seed"], include_trace=True)
assert json.loads(json.dumps(actual)) == saved
```

The artifact preserves per-user wealth, actions and stock at each round, fixed assumptions with reasons, the register, source hashes and planner limitations. This is a reporting counterexample, not empirical evidence about real commons. Historical table claims still need separate evidence review.

## Planner audit

`planner-audit-before.json` comes from clean commit `ab6b02a8a578649ce7ce4c78d24c45218369cad0`; `planner-audit-after.json` comes from clean commit `7e9bba06720218d9ce4b9a06e525417b4cc59e82`. In each checkout, reproduce with:

```sh
python -m tests.planner_cases
```

Each artifact stores source provenance, the diagnostic fixture hash, fixed constants, candidate values, chosen actions and exact arithmetic references. The information repairs change the one-way-response and hidden-bit results. Tie ordering, the investment sequence gap and the threshold-risk reversal remain unchanged; they justify the next planner replacement. See `rediscovery/planner-audit.md` for scope and `tests/test_planner_audit.py` for the contracts.

Replaying an artifact means using its recorded source revision. Later, better planners are expected to change outcomes; preserve old evidence instead of silently rewriting it.

## Exact search reduction

`search-profile-before.json` identifies clean source `2535e47`; after profile and
`search-reduction.json` identify clean implementation `96e7c54`. Reproduce with
`python -m tests.search_profile` and `python -m tests.search_reduction` at those
revisions. The before revision has only the profile fixture.

The paired study compares full physical leaf enumeration and exact reward
marginals under the same planner/kernel. It records parameters, seeds, complete
physical traces, unresolved runs, work counts, raw timings and fixture/source
hashes. A separate larger-cap reference certifies one newly covered decision;
it does not count as coverage at the default cap. Retained 12-round traces and
17-round action probes check equivalence across the physical-kernel refactor.
Marginal sampling and stock probes test arithmetic, not institutional robustness.
See `rediscovery/search-reduction.md` for findings and limits.

## Coalition power

`coalition-power.json` identifies clean source `d7fcd10`. Reproduce with
`python -m tests.power_study` at that revision (about 7 minutes). It records the query
definition, stock grid, designs, per-size force/prevent brackets, thresholds with
exactness flags, symmetry checks, work counts, timings, behavioral trajectories with
per-round power profiles, grand-coalition witnesses and 12-round unavoidability checks
(null where the work cap was reached). No goal or planner parameter enters a power
value. See `rediscovery/coalition-power.md`.

## Restraint

`restraint.json` identifies clean source `98cafb1` (re-run of the `4175ae0` study after interior
reward integration; neighborhood behavior identical, five unresolved random runs now resolve). Reproduce with
`python -m tests.restraint_study` at that revision (about 3 minutes). Paired runs with
restraint off and on (same parameters and seed; menus differ, so random draws are not
guaranteed to align), full traces for the one-at-a-time neighborhood, random-sample
outcomes, and T=3 power maps. See `rediscovery/open-commons.md`, restraint findings.

## Power profiles

`power-profiles.json` identifies clean source `81bece6`. Reproduce with
`python -m tests.profile_study` (about 2 minutes). Five commons runs with full traces
and, per round, force/prevent thresholds within 3 rounds, fragile and sealed flags.

## Depth

`depth.json` identifies clean source `98cafb1` (re-run of the `7c1b92d` study after interior reward
integration; completed rows identical, depth 5 with restraint now resolves). Reproduce with `python -m tests.depth_study`
(about 10 minutes). Baseline runs at depths 4 and 5, restraint on and off, full traces,
under a recorded study cap of 2,000,000 entries.

## Treaty

`treaty.json` identifies clean source `a2d4c64`. Reproduce with `python -m tests.treaty_study`
(seconds). Power grid with full-information force values and sure prevention blind,
verified and informed; default runs with round-1 action values; 120 verification-paired
random samples with outcomes, build and strike counts. See
`rediscovery/treaty-no-verification.md`.

## Treaty: scarce responses

`treaty-scarce.json` identifies clean source `684448e`. Reproduce with
`python -m tests.treaty_scarce_study` (about 20 seconds). 1,800-cell power grid with
force values and blind/verified/informed sure prevention, and 120 verification-paired
samples of the full register.

## Treaty: capability domains

`treaty-domains.json` identifies clean source `b38af92`. Reproduce with
`python -m tests.treaty_domains_study` (about 2 minutes). 360-cell grid of blind, verified
and informed sure prevention for one and two domains, and 120 two-domain samples paired
on verification.

## Opponent models

`opponent-models.json` identifies clean source `c81efb5`. Reproduce with
`python -m tests.opponents_study` (about 25 seconds). Commons neighborhood and the T3.1
treaty samples under both level-1 opponent models (`others` react and plan).

## Externalization

`externalization.json` identifies clean source `6b48e9b`. Reproduce with
`python -m tests.externalization_study` (seconds). Declarations of both worlds and
per-harm reports for commons stocks and treaty settings at T=3.

## Race on a shared fishery (composition)

`race-commons.json` identifies clean source `98cafb1` (re-run after interior reward integration;
power rows unchanged from `2d220b6`, previously unresolved `plan` runs now resolve). Reproduce with
`python -m tests.race_commons_study` (about 5 minutes). Declarations and coverage,
fishery harms alone versus in the whole by draw and stock, forced choices over draw,
stock and treaty settings, and planner runs under both opponent models.

## Scale

`scale.json` identifies clean source `dc8a981`. Reproduce with `python -m tests.scale_study`
(about 4 minutes). Exact commons power tables for n up to 20 using declared symmetry, with
per-size rows, `stands_for` counts, thresholds, work and timing.

## Fishers (E2 step 2)

`fishers.json` identifies clean source `c0d3226`. Reproduce with `python -m tests.fishers_study`
(about 27 minutes on 4 processes). Race-on-a-fishery power tables for depletion and collapse
with 1 to 10 exchangeable fishers over stock and draw, with per-coalition rows, `stands_for`,
thresholds, work and timing.

## Size (E2 step 3)

`size.json` identifies clean source `0221c21`. Reproduce with `python -m tests.size_study`
(about 13 minutes on 4 processes). Commons runs over sanctions, prior, regrowth, high take,
n from 2 to 24 and two seeds, 30 rounds, per-round choice counts and stock; plus the
sanction-cost discriminating check.

## Authority and correction

`authority.json` identifies clean source `67b7fcb`. Reproduce with
`python -m tests.authority_study` (about 20 minutes on 4 processes). Correction grid (who
can end extraction without the ruler, commanders-only seizure, the ruler's keep value,
veto players), lock grid, point-of-no-return strengths by contest, gain and surveillance,
per-round correction along four traces, and 60 behavior samples paired on assembly.

## Rules as claims

`rules.json` identifies clean source `893d2cf` (re-run after the E7 amendments; the first run was `a40ea9d`, recoverable from git history). Reproduce with `python -m tests.rules_study`
(about 2.5 minutes). Every declared rule in the commons, treaty, authority and audit worlds
over a grid each: unilateral and coalition one-shot departures with witnesses, externalizing
departures, and audit margins at the decision state.

## Correction without a contest (E6)

`correction.json` identifies clean source `893d2cf` (re-run after the E7 amendments; the first run was `2ccdfa6`). Reproduce with
`python -m tests.correction_study` (about 3.5 minutes on 4 processes). The restitution rule
checked over 512 designs (records, assembly, repayment, disclosure, army, contest, gain) and
32 pact designs with ruler-to-commander payments, with witnesses per agent and pair.

## Frontier AI (T9.1)

`frontier.json` identifies clean source `67cf935` (re-run; the first run was `893d2cf`). Reproduce with
`python -m tests.frontier_study` (about 40 minutes on 4 processes; the payment designs use two-round checks). Information-restricted sure prevention of unsafe
deployment and of blocked safe progress for four coalitions over 72 designs; licensing and
race rules over 144 designs with harmful-departure witnesses and pair captures; three payment
designs against evaluator liability; per-harm power at the defaults under both oversight modes.

## AI systems as agents (T9.2)

`control.json` identifies clean source `81067bc`. Reproduce with `python -m tests.control_study`
(about 4 minutes on 4 processes). Shutdown and escape power over 240 states; corrigibility
and full-autonomy rules over 160 designs from 8 starting states each, with coordinated
departures over two rounds.

## Rule-making (E10)

`amendment.json` identifies clean source `87c1a0d`. Reproduce with `python -m tests.amendment_study`
(about 4 minutes). Frontier licensing under three rule-making settings (state alone; labs
seated, majority; labs seated, unanimity) over 24 designs each.

## Binding certification (T9.1)

`binding.json` identifies clean source `af8b46e`. Reproduce with `python -m tests.binding_study`
(about 9 minutes on 4 processes). Plain and bound licensing over 144 designs x evaluator
liability {0, 2, 10}, with single-agent, one-round and two-round coalition departures.

## Precaution (E12, T9.2)

`precaution.json` identifies clean source `e3c070e` (replacing `2ec45c1`, whose lab and state
gains for a persisting type came from a bug fixed in `e3c070e`; finding 7 corrected).
Reproduce with `python -m tests.precaution_study` (seconds). Lab, state and AI incentives right
after the AI is caught, over 27 states and five posteriors that the AI persists as a misaligned
type.

## Learning about hidden goals (E12, derived posteriors)

`learning.json` identifies clean source `975dd56` (re-run after the scale-free choice rule; the
`e3c070e` run's logit and off-path posteriors compared utilities across types). Reproduce with `python -m tests.learning_study`
(seconds). 486 cells: switch, autonomy, capability, ambition, prior, precision; posteriors after
each AI action, lab and state gains when the AI is caught improving, resistance as evidence, and
the misaligned type's own path from the sandbox.

## Does improvement reveal only because capability is worthless? (T9.4)

`leverage.json` identifies clean source `975dd56`. Reproduce with `python -m tests.leverage_study`
(seconds). 360 cells: corrigibility and a tolerant rule x leverage x switch x autonomy x
capability x ambition, prior 0.1; which types improve, what improvement and failed escape tell
the lab, lab and state departures after an improvement, each type's 6-round play from the sandbox.

## Re-run after interior reward integration (E2 step 3)

Every planner-using study was re-run from clean `98cafb1`. Identical apart from timing, work
counts and register entries added since: opponent models, precaution, power profiles,
treaty, treaty domains, treaty scarce, correction, amendment, control, binding, rules,
authority, frontier (those files are kept). Changed only where runs used to stop at the
work cap, and replaced: restraint, race-commons, depth.

## Rollback on restart (T9.3)

`rollback.json` identifies clean source `2c6c352`. Reproduce with `python -m tests.rollback_study`
(seconds). Each type's 10-round path under corrigibility with and without rollback; whether the
lab honors a restore after a caught improvement, over 768 cells including the lab's horizon.
At `2c6c352` the learning, leverage, precaution and control studies were re-run: results
identical (control's recorded defaults and exclusions list the options added since).

## Escrowed checkpoints (T9.5)

`escrow.json` identifies clean source `aeff9c8`. Reproduce with `python -m tests.escrow_study`
(under a minute). 1,152 cells: the lab's rollback against the state holding the checkpoint, over
spillover, horizon and vigilance, with lab-state capture over two rounds. At `aeff9c8` the
learning, leverage, precaution and rollback studies were re-run: results identical.

## The race and the off switch (T9.6)

`race-control.json` identifies clean source `6a24887`. Reproduce with `python -m tests.race_control_study`
(about 2 hours on 4 processes, nearly all in the 24 power states). 384 rule cells from a caught
AI, coupled and uncoupled; goal-free power over the race harms at T = 2. A preview run from a
dirty tree gave identical results.

## Contest family (A2)

`contest.json` identifies clean source `21dda20`. Reproduce with `python -m tests.contest_study`
(about 10 minutes on 4 processes). Ruler vetoes on correction with one and two commands over 16
authority cells and 13 contest forms; the ratio endpoint equals `authority.json` (32 of 32).

`race-rule.json` identifies clean source `c68303d`. Reproduce with `python -m tests.race_rule_study`
(about a minute). The T9.6 rule cells under licensing and under the unregulated race; licensing
rows equal `race-control.json`.
