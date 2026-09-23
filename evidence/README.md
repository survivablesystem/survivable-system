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

`restraint.json` identifies clean source `4175ae0`. Reproduce with
`python -m tests.restraint_study` at that revision (about 3 minutes). Paired runs with
restraint off and on (same parameters and seed; menus differ, so random draws are not
guaranteed to align), full traces for the one-at-a-time neighborhood, random-sample
outcomes, and T=3 power maps. See `rediscovery/open-commons.md`, restraint findings.

## Power profiles

`power-profiles.json` identifies clean source `81bece6`. Reproduce with
`python -m tests.profile_study` (about 2 minutes). Five commons runs with full traces
and, per round, force/prevent thresholds within 3 rounds, fragile and sealed flags.

## Depth

`depth.json` identifies clean source `7c1b92d`. Reproduce with `python -m tests.depth_study`
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
