# Log

Append-only. Newest at the bottom. One entry per session: who, date, what changed, what was learned, what the next agent must know.

## 2026-09-15  Fable: assessment

Read the static linter (analyzer, two components, one case) and ran it. Found: cost marked only on a flow's receiver, so surveillance was inexpressible; net-losers summed five incommensurable currencies; the sweep varied ranges but never the weights between currencies; flows and payoffs were two ledgers that did not reconcile; the demo found only what its author had typed into the notes. Owner's goal was wider than the linter's scope.

## 2026-09-15  Fable: direction

Owner rejected hand-written failure pathways and buildability-first scoping. Direction set: the agent as the single primitive, no scripted behavior, architectures as rules and channels, chains as outputs. Wrote `spec/PRIMITIVES.md` and three paper cases. The paper work forced three corrections: rules are claims enforced by contest; selection is explicit in the world; beliefs about others are first-class.

## 2026-09-15  Fable: rework and engine v0

Owner approved reworking the workspace. Flattened `files/` to the root, initialized git (no commit; the owner makes the first). Removed the linter, its components, cases and spec; DECISIONS.md records where each idea went. Rewrote INTENT.md, AGENTS.md, README.md. Added TASKS.md and this log. Built `engine/` and `worlds/commons.py`; 12 tests green.

Learned, in order of cost:
- The commons collapsed three times for three reasons. Level-0 beliefs cannot hold a norm (finding, kept as a test). Harvest-before-regrowth made the sustainable yield a knife-edge (artifact, fixed). Sanction-target tie-break by id let low ids defect for free (artifact, fixed). Probe per-round action values before touching the model.
- Second-order free riding is real in the engine: a sanction that only benefits the shared stock is never chosen. Sustained use needs sanctioning to pay the sanctioner. The paper case had this wrong. Intent test 6 passed on the first world.
- With paid sanctioning and full observability, group size does not matter. The size effect must come through channels. T1.1.
- A random sweep buries an outcome that needs several conditions at once. The one-at-a-time mode is the informative view. Both exist.
- Bash heredocs longer than about 6 KB get cut by the tool transport. One file per call.

Next agent: T1.1 (sparse channels) is small and finishes the commons. Stage 2 (captured auditor) is the first world that needs a resource conversion; read its case file first. Owner asked for kinship/trust and money issuance; briefs exist as stages 5 and 6.

## 2026-09-19  Codex: T0.1, reliable evidence and publication

Owner authorized improvements, repository creation and push. Preserved the original prototype in commit `1c1b39a`; implementation is `f26e7f9`. Created the public MIT repository https://github.com/survivablesystem/survivable-system, branch main, remote origin. GitHub CLI works; the separate connector was not needed. Sandbox network denial had misleadingly appeared as invalid authentication during the earlier access check.

Changed: intent/spec and research acceptance now permit disconfirmation and state planner limits; finite survival is `survived`, not an attractor. All CLI modes emit versioned JSON with normalized source hashes, revision/dirty state, fixed reasons, parameters, seeds, duration, terminal status and final state. Trace includes actions/states. OAT honors fixed parameters; CLI rejects unknown/invalid overrides and nonpositive run sizes. Sorted channel iteration fixes hash-dependent assignment of random contest draws. Sampling now records integer seeds; old seed-specific sweep trajectories are not preserved. No stronger planner or new world was added.

Learned: the same commons configuration survives one round and collapses at five. Saved and replayed its trace from clean commit `f26e7f9` in `evidence/commons-collapse.json`. Dimensionless stock fractions are substantive assumptions, not unit scale. Several random seeds at one favorable point do not establish robustness. Existing historical briefs remain unverified; a failed expectation need not mean a missing primitive.

Validation: baseline 12 tests passed. Final 34 tests passed locally (Python 3.12); text-mode CLI smoke checks passed. GitHub Actions run 35434930895 passed on Windows and Linux. Tests cover every JSON mode, replay, cross-process hash seeds, OAT controls, invalid inputs and missing-Git provenance. CI pins official action release commits; evidence and task/log-only changes do not rerun code tests.

Next agent: pull first, then T1.0 (information/planner audit) before sparse channels. Preserve contrary outcomes. T2.0 requires sources and rival explanations before the auditor world; paired design comparisons moved forward to stage 2. Coalition guarantees, structural uncertainty, affected-group metrics and a working civilizational protocol remain unimplemented. Do not describe the green suite as model validation.

## 2026-09-19  Codex: T1.0, information and planner audit

Owner directed continued work and explicitly authorized coherent extensions or complete rebuilds when they improve capability while preserving the core. Recorded this in INTENT/AGENTS/DECISIONS; spec size and old architecture are not constraints in themselves. Internal model/aggregation choices need evidence and a decision record, not renewed permission. Values and real-world boundaries still need owner steering.

Pulled main; baseline 34 tests passed. Pre-fix diagnostics committed as `ab6b02a`, repairs as `7e9bba0`, developed on `codex/planner-audit` and fast-forwarded/pushed to main. Five arithmetic cases expose directed observation, hidden truth, tie order, action sequences and nonlinear threshold risk. Before/after JSON artifacts record clean source revisions and fixture hashes. They are constructed diagnostics, not empirical evidence.

Fixed: response modeling followed whom the actor sees instead of who sees the actor. With a one-way observer, take was valued at 2 instead of -1. Planning also read hidden truth through actions/rollouts, including nested responses. Worlds must now implement pure `belief_state`; candidate menus and rollouts share that projection while execution uses truth. Nested plans stay inside the parent hypothesis. `action_values` exposes the same evaluation path as `plan`. Commons masks unobserved action history and explicitly treats stock, wealth, utility and topology as known. World authors can still violate the contract through private attributes; this is not an isolation sandbox.

Learned: equal utility can hide order-dependent side effects. Constant-action planning rejects invest-then-consume worth 3 in favor of consume-twice worth 2. Expected-state planning values risky at 2 even though branch-weighted utility is -4 and safe is 1. These limits remain measured, not patched with behavioral heuristics. T1.3 now precedes sparse channels and calls for one coherent transition/search replacement. During that work, retain exact references and migrate assertions about the old approximation rather than preserving wrong answers.

Validation: six information-contract tests failed before the fix; all 52 tests pass afterward, including four channel directions, hidden/revealed information, menus, nested plans, actual execution, and reference gaps at several costs/probabilities. Archived commons trajectory replays unchanged; existing full/no-channel outcomes pass under the current approximation. Windows and Linux passed GitHub Actions run 35435973073. Checked that tie, investment and threshold cases are unchanged between audit artifacts.

Next agent: T1.3, not T1.1. Use the arithmetic counterexamples to justify the replacement and compare commons results/runtime explicitly. Point beliefs, known topology/utilities, direct-observation-only response and deterministic tie order remain declared assumptions. No stronger-planner or civilizational validity claim follows from this audit.


## 2026-09-19  Codex: T1.3, coherent planner and transition replacement

Pulled main; baseline 52 tests passed. Claimed T1.3 and recorded the simplest design before code. Pre-change comparison is `16e208e`; implementation `8bfa73a`, developed on `codex/planner-replacement`, fast-forwarded and pushed to main. User's standing direction permits replacing internals; purpose and evidence standards remain intact.

Changed: one finite `outcomes` kernel drives both planning and execution. Adaptive action search integrates branch utilities and chooses one continuation per observable history, preventing hidden-branch clairvoyance. `observe`/finite `beliefs` replace the point projection; menus use observations. Direct observers replan at level 0 within remaining depth. Desired horizon, effective depth and work budget are separate and recorded. Budget exhaustion returns no decision; schema-2 evidence marks unresolved runs with null labels and retains them in share denominators. Old seed-specific stochastic paths are not preserved by the joint-CDF sampler; old artifacts retain their source revisions.

Learned: investment and nonlinear-risk references now agree with exact arithmetic. Commons defaults to depth 2 for tractability and collapses at round 17. Crucially, the archived old horizon-2 planner also collapses at 17 while old horizon 12 survives 30. Do not attribute that reversal to adaptive planning or branch integration, or claim equivalent depth-12 coverage. Initial action values and every baseline round/agent were probed before revising outcome tests. Ten-user depth 2/3 hits the 20,000-entry budget; this is no population-size finding. Four identical symmetric seeds add no realized behavioral diversity.

Evidence: before/after 12-round comparisons, old-source 30-round depth control, current 30-round depth/size study and exact diagnostics in `evidence/`. Final artifacts all identify clean implementation `8bfa73a`; old duration control identifies its git-archive revision. Final local timing: new baseline three 12-round runs plus probe 1.58 s; four n=4 depth-3 runs 39.75 s. Timing varies between passes; limits and raw timings are preserved.

Validation: 77 tests pass locally; GitHub Actions 35437610089 passes Windows and Linux. Tests cover hidden future branches, nonuniform beliefs, changing menus, discounting, terminal rewards, kernel probability arithmetic, deterministic replay and aborting partial searches. Text CLI smoke check reports a ten-user depth-3 search limit without a survival label. Verified artifact source revisions/clean flags and diagnostic values.

Next: T1.4, measured search reduction before sparse channels or long-horizon conclusions. Profile branching/nested response costs; justify exact reduction or calibrate any approximation against these references, including hidden-information and threshold cases. No additional world, institution ranking, global-optimum claim or civilizational protocol has been validated. First-listed ties and explicitly modeled belief memory remain limitations.

## 2026-09-19  Codex: T1.4, exact leaf reward reduction

Pulled main; baseline 77 tests passed. Local Python command is
`C:/Users/Bob/AppData/Local/Programs/Python/Python312/python.exe`; `python` is absent
from PATH and the launcher selects an inaccessible Store installation. Claimed
T1.4 on `codex/search-reduction`. Hypothesis/profile fixture commit `2535e47`;
implementation `96e7c54`. Decision recorded before core edits.

Profile disproved simple duplicate caching as the main remedy: after all users
take high, n=10/depth=2 exhausted 20,000 entries in just 116 kernel calls (93 unique).
Independent contest leaves dominate. Added optional exact `reward_outcomes`:
default integrates the physical kernel; commons shares preparation/payoff code
and sums expected confiscations. Only depth-1 search uses the marginal. Interior
branches, observations, posteriors, execution and goals remain unchanged. The cap
now counts emitted belief/transition/reward entries; it is not a time bound.

Learned: the n=8/depth=2 contested decision completes in 5,241 entries. Full
enumeration under a separate 2,000,000 reference cap needs 348,202 and agrees
exactly. Thirty-round requests, seeds 0/1, now finish with collapse at 17, matching
the smaller baseline's depletion cycle. Identical symmetric seeds do not establish
diversity or a real size effect. Ten-user depth 2 still stops after round 1; depth 3
initial probes still fail. Some unresolved searches take longer because they
reach more nested decisions before the cap. No depth-12 claim.

Validation: 99 local tests pass, including asymmetric plans, exhaustive three-user
joints at boundary stocks, nonlinear branch loss, hidden future information and
reward-budget aborts. All 21 retained traces replay; all agents' values/actions in
the 17-round baseline agree. Maximum marginal discrepancy across 128 registered
samples is 8.88e-16. Clean-source profile and paired study artifacts identify
`96e7c54`; source and fixture hashes verified. Complete n=4/depth=3 runs took about
10 s with full leaves and 5 s reduced; newly covered n=8 runs took 18–19 s.

Publication pending: automatic approval review rejected the proposed fast-forward
and push to remote main, citing missing specific authorization for default-branch
publication. The command did not execute; main remains unchanged, work is committed
locally on `codex/search-reduction`, and remote Windows/Linux CI has not run.
Request explicit publication approval; do not work around the rejection.

Next: T1.1 sparse channels. Keep unknown/search-limit results distinct from physical
collapse and avoid extrapolating coverage. Larger/deeper comparisons need evidence
for reducing interior branching. No new world or institutional validation added.

## 2026-09-19  Codex: T1.4 publication approved

Owner explicitly approved the pending push and future project pushes. Recorded
standing authorization in AGENTS.md, including fast-forwarding/pushing main and
checking remote changes and CI. Fetched origin, fast-forwarded local main to
`464aa59`, and pushed. Windows and Linux passed GitHub Actions run 35456833505;
99 tests pass. This resolves the prior publication block. Source evidence remains
at its recorded revisions. Next task remains T1.1; no new research task was claimed.

## 2026-09-23  Claude: T1.5, goal-free coalition power

Owner asked for a rethink of direction before continuing. Read: four sessions made the
goal-driven planner exact on one toy world; every result still rests on authored goals,
horizons and planner depth. INTENT's core question (who can force or block an
irreversible outcome) needs none of those. Inserted T1.5 before T1.1, decision before code
(`DECISIONS.md` 2026-09-23), hypotheses in `rediscovery/coalition-power.md` before runs.

Changed: `engine/power.py` computes, for every coalition, the max-min probability of
entering a terminal label within T rounds against a coordinated full-information
adversary; alpha/beta stage orders bracket randomized play; prevention is the dual;
thresholds carry exactness flags; witnesses give first-round actions. Optional
`World.physical(state)` is only a memo key (commons: stock and collapse; tested against
menus, kernel and terminal). CLI `--power T [--target labels]`. Spec v0.3 queries section.
No planner change; goals never read (a toy world raises if they are).

Learned: see the case file. Headline: in the paid baseline the irreversible step (S below
S* = 27.64) was a unanimous all-high choice at round 13 that any one user could have
blocked; the collapse label fires four rounds later. Paid sanctions are pure deterrence;
unpaid sanctions give denial that agents do not use. H3 as stated was contradicted.
The commons menu has no take below `lo`, so the group's best preventive play at low stock
under unpaid sanctions is to defect and be confiscated: a wrong-world signal (T1.6).

Evidence: `evidence/coalition-power.json`, clean `d7fcd10`, 6 min 45 s. An earlier run
aborted when a 12-round check hit the work cap; the study now records null there. Writing
the artifact inside the repo during the run would mark provenance dirty; write elsewhere,
then copy. 124 tests pass locally. Pushed to `claude/lucid-gates-mepgtk`, not main: this
session's harness restricts pushes to that branch, so main publication and CI on main
await the owner.

Next agent: T1.6 before T1.1. Exact power enumeration is exponential (menus^n per stage,
reachable states per round); n <= 4, T <= 4 are comfortable, 8+ rounds at n=4 hit the cap.
Symmetry by declared types (T8.1) is the scaling path for both queries. When you report
a behavioral result, report the power profile beside it (T1.7).

## 2026-09-23  Claude: T1.6, commons restraint

Owner authorized merging and pushing to main going forward; T1.5 fast-forwarded main to
`2583b92`. Claimed T1.6; hypotheses R1-R4 in `open-commons.md` before building.

Changed: register option `restraint` adds `(rest, no sanction)`; default now True. Resting
users cannot sanction (declared; resting sanctioners untested). Menu order puts rest after
the two plain takes, before sanction actions; ties resolve accordingly. `power_study.py`
pins `restraint=False` so T1.5 evidence still reproduces (checked 33 map entries).

Learned: restraint removes every sealed state; minorities can prevent collapse. Agents
with depth 1-3 still do not rest in the baseline or 15 of 16 variants, and collapse at the
same round. One random sample survives only with restraint, by a rest-and-raid cycle.
The bigger lesson: the depth cap, not goals, now decides behavior in this world. Added
T1.8 ahead of sparse channels.

Evidence `evidence/restraint.json` (clean `4175ae0`, 3 min). 133 tests pass.

Next agent: T1.7 (report power beside behavior), then T1.8. Enlarged menus raise planner
and power cost (5 actions per user with sanctions; one sample became unresolved).

## 2026-09-23  Claude: T1.7, behavior beside power

Added `engine.power.profile` and `--trace --profile T [--target labels]`. Each played round
shows the smallest coalitions able to force or prevent the target within T from the state
the round began in; fragile (one agent can force it) and sealed flags. Tests: toy trace,
CLI/library agreement, `--profile` requires `--trace`. 135 tests pass.

Learned: with restraint on, the paid baseline's final collapse step is everyone taking the
enforced low take at S=9.7 (three resters would have prevented it): the sanction rule
protects a fixed quota, not the stock. The restraint-only survivor was fragile at every
rest round. Evidence `evidence/power-profiles.json` (clean `81bece6`).

Next agent: T1.8 (planner reach). New worlds must ship this report with their first case.

## 2026-09-23  Claude: T1.8, planner reach (negative)

Measured before building: depth-4/5 decisions need 25k/481k entries; the 20k default cap,
not the method, blocked them. Ran exact depth 4/5 baselines under a recorded 2M study cap.
Collapse at 22/18/17; depth 5 with restraint unresolved. Deeper search delays collapse by
at most five rounds, non-monotonically. No tail value adopted. Evidence `evidence/depth.json`.

Direction note for the next agent: in the commons, behavior is dominated by planner reach
and power results are not. Power claims are the robust output; behavioral claims should be
reported as conditional on search depth. Next: stage 3 (treaty and capability race),
reordered ahead of stage 2 because it is the case where goal-free lock-in queries answer
the AI-governance question directly. Sparse channels (T1.1) and the readiness tie (T1.2)
are deferred: their behavioral effects would be conditional on the same depth limit.

## 2026-09-23  Claude: T3.0-T3.1, treaty and capability race

Reordered stage 3 ahead of stage 2 (reason in TASKS). T3.0: sources checked at
bibliographic/abstract level; rivals from Powell (commitment), Coe and Vaynman
(transparency-security) and Armstrong, Bostrom and Shulman (information). Design point:
the full-information power query cannot see verification, so added `engine.power.sure`
(knowledge-set construction, decision record first; tests include a hidden-bit toy).

T3.1: `worlds/treaty.py` (hold/build/strike, ratio or threshold contest, verification
none/exact, relative-capability goals, `opening` assumption added after the first probe).
Kernel bug found by tests: two zero-capability strikers both "won" under threshold; fixed.
Findings in the case file: verification changes behavior, not power; its behavioral effect
favored the leader; lock-in is now-or-never; the first-strike default depends on the root
opponent model. Evidence `evidence/treaty.json` (clean `a2d4c64`, 6 s). 153 tests pass.

Next agent: T3.2 (scarce responses; ratio-raising returns). The treaty world is cheap, so
larger sweeps and depth 3 are affordable. A1 now has a recorded case.

## 2026-09-23  Claude: T3.2, scarce responses and ratio-raising returns

Added `elasticity`, `budget` (scarce: two units per build, one per round), `reserve`.
Defaults reproduce T3.1; `treaty_study` pins the new keys and reproduced its first 20
behavior pairs exactly. First study run crashed on a belief bug (scarce, reserve 0,
round 0: zero rival builds treated as infeasible; certain builder with no affordable
schedule got zero mass); fixed with parametrized tests, then recorded.

Learned: scarcity does not make verification buy denial; the defender's best preventive
move (build when affordable) is uniformly best, so information cannot add guarantees.
Elasticity 2 makes lock-in accumulate. Verification's behavioral effect runs both ways.
Evidence `evidence/treaty-scarce.json` (clean `684448e`, 22 s). 162 tests pass.

Next agent: T3.3 (hidden choice: domains). The blind-versus-informed sure comparison is
a general check any world can run: if equal, information has no denial value there.

## 2026-09-23  Claude: T3.3, hidden choice

Generalized the treaty world to per-domain capability (`domains` 1 or 2); actions
`build`/`strike` for the first domain, `build:1`/`strike:1` for the second. One domain
reproduces every T3.1 outcome and default trace; state representation changed, so older
studies replay at their revisions. Fixed a study summary bug (second-domain builds not
counted) before the recorded run.

Learned: verification buys denial only when the defender's right move depends on the
rival's hidden choice; two domains show it (10/90 cells), one domain and scarce budgets
do not. Behavior shows a reassurance effect: blind leaders strike on the possibility of a
closing window. Evidence `evidence/treaty-domains.json`. 164 tests pass.

Next agent: stage 3 has answered its question within scope. Candidate next steps in the
case file: the leader's own information (sure reach), longer horizons under scarcity, a
third party (inspector with its own goals, T9.1 needs ASK). Or return to stage 2 (captured
auditor), where the same power/information queries apply to evaluation of AI systems.
