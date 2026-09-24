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

## 2026-09-23  Claude: A1, opponent model swept

Prototyped the textbook level-1 rule in scratch before any decision: it changed treaty
defaults (1 to 4 disarmaments in 4) and the commons baseline timing (17 to 21). Neither
rule is established, so both are kept as the swept assumption `others` (decision first);
react stays default and all evidence stands. Sampling studies pin the new key.
`records.py` unchanged: the key is in each run's params, and saved artifacts still replay.

Learned: commons collapse/survival is robust to the opponent model, timing is not.
Treaty's "verification makes trailers arm" (T3.1) does not survive; small two-signed
outcome effects do; power findings are model-free. Evidence
`evidence/opponent-models.json` (clean `c81efb5`). 169 tests pass.

Next agent: every behavioral claim should now be reported under both `others` values
and the depth cap; power claims need neither. Candidates: stage 2 captured auditor (the
evaluator-paid-by-the-evaluated problem, directly relevant to AI evaluation), or the
leader-information question in the treaty case.

## 2026-09-23  Claude: E1, externalization made executable

Owner direction: a simple, powerful tool for any system, many dimensions, eventually
civilizational scale, no holes that create externalization; later note: the whole system
is what matters. Added the E1-E4 block to TASKS ahead of the stages.

E1: worlds declare STAKEHOLDERS, HARMS, EXCLUDED; `externalization` query and CLI;
power targets accept predicates; correction for realized harms. Commons gained a
reversible harm (`depleted`, FIXED `depleted_frac` with reason). Found: the commons'
harms fall mostly on stakeholders with no agent; a treaty leader imposes disarmament on a
population that has none. 180 tests pass. Evidence `evidence/externalization.json`.

Next agent: E4 composition (claimed), then E2 scale.

## 2026-09-23  Claude: E4, the whole system

Owner note mid-session: viewing the system as a whole is the point; analysing parts
alone is what externalizes harm. Built composition (decision first): `engine/compose.py`
runs part kernels in order with a declared coupling, maps actors across parts, gives
outsiders public views (treaty generalized; T3.1 outcomes still reproduce). Moved
`joint_prevention` into `engine/power.py` (per-coalition forced choices, any world); the
CLI prints them. Exclusion coverage is checked in tests.

Found by comparing CLI and library output: a chained-assignment bug in the new nested
`--state` override silently left the start state unchanged; fixed with a regression test.
Also caught before recording: the composite's behavioral "collapse caused by the race"
was a collapse brought forward; the fishery alone was already depleting (stock 8.9 at 30).

Learned: 8/18 fishery harm rows change between part and whole; forced choices between a
party's safety and the fishery in 4/27 settings; the bystander drops out of minimal
preventing coalitions. Evidence `evidence/race-commons.json` (clean `2d220b6`).
186 tests pass (E1 log said 180; it was 179).

Next agent: E2 scale (types and symmetry), now needed by composites: menus multiply
across parts and `others = plan` already exceeds the work cap at three actors.

## 2026-09-23  Claude: E2 step 1, exact symmetry in power queries

`World.types()` (decision first): exchangeable groups; stages enumerate action multisets
per group, tables one row per count vector with `stands_for`. Outsider witnesses are
re-represented by members outside the affected. Tests: kernel invariance under
permutations, reduced equals full tables at n=3 across four designs. Commons power exact
at n=20, T=3 (154 s). Power depends on fractions of users, not numbers.
Evidence `evidence/scale.json` (clean `dc8a981`). 200 tests pass.

Next agent: E2 remaining (planner symmetry; types in composites), or a third world that
exercises the whole-system tools on a question with more actors.

## 2026-09-23  Claude: E5, correction and computed entrenchment

Owner prompt: continue, follow the intent, redesign where useful. Chose INTENT's own chain
(surveillance, concentration, loss of correction), which no world modeled. T4.0 review
first (five sources verified at abstract level; standing-army brief reframed and kept).
Decision before code: irreversibility is computed as well as declared. `lock_in` (force a
harm, then keep it K rounds against everyone; nested game), `keep` and `veto` at realized
harms, a loud failure when a declared-irreversible harm can be ended, and exact p = 1
thresholds (a mixture guarantees certainty only if each action does; earlier "upper
bound" marks at p = 1 were spurious). `worlds/authority.py`: office, coercion, extraction
converting office into strength, covert organizing, surveillance-gated purges, rises.

Caught before the study: with purge and extraction exclusive, a purging holder could never
keep extraction continuous, so surveillance could not matter by construction; the holder
now extracts and purges in one round. First study run was stopped because doc edits
would have made its provenance dirty; rerun from clean `67b7fcb`.

Learned: splitting command mostly raises the correction threshold (85/108 pairs) rather
than the seizure threshold (18/108). With decisive contests, surveillance and conversion,
the split army is what gives the ruler a veto on correction; with probabilistic contests
the sign reverses. The point of no return comes at a quarter to three quarters of
physical dominance. Every behavior run ends in extraction, which the goals imply; not a
finding. Commons, as a side result of the new query (n=3, T=2): at S=20 any single user can keep the
stock depleted for 2 rounds and every user holds a veto on recovery. 225 tests pass.

Next agent: E6 (correction without a contest of strength) is where the case points; A2
has a case. `--lock` makes any world's reversible harms checkable for political
irreversibility; run it on the treaty and the composite before trusting "reversible".

## 2026-09-23  Claude: E7 rules as claims; T2.0-T2.1 audit world

Owner: continue; publish any time; find holes by building interesting systems and fill
them with general capabilities rather than patches. Published main (fast-forward to
`d6e2c30`). Gap chosen: the spec's "a rule is a claim" had no implementation, so no
institution could be tested for whether it holds or who captures it. Decision first:
`engine/rules.py`, worlds declare `RULES`; one-shot departures at the start and one step
off the path; coalition departures (full information, summed value) and externalizing
departures (harm on outsiders). First design (truncated multi-round best responses) was
replaced before any test: it finds end-game departures that are artifacts of depth.

Built `worlds/audit.py` after a sourced review (Dyck et al. contradict "never by the
auditor"). The check exposed a world error: the public record lacked who signed a
qualified opinion, so the capture rule's punishment hit the wrong auditor. Fixed in the
world, recorded in the case file.

Learned: capture is a pair's act; independence holds for individuals only by
indifference; the brief's remedy (no switching) leaves the pair's gain unchanged in every
cell, and the credibility premium raises it. In the other worlds: accountability rules
without marginal deterrence fail after the first breach; citizens seeing each other
organize halves profitable coups while changing no power value; verification removes the
one cell where treaty restraint holds. 244 tests pass.

Next agent: E6 (correction without strength) now has a tool: propose rules (pay control,
term limits, a court) and check them with `--enforce` against the authority grid. E8 only
if a conclusion depends on transferable utility or mechanical credibility. Audit power
queries and planner behavior are not yet studied.

## 2026-09-23  Claude: E8 side payments, E9 public records, E6 restitution

Checked E7 without the transferable-utility assumption (new `every_member` flag): audit
capture needed a payment the world lacked. Added two modules over any world, decisions
first: side payments (`engine/transfers.py`, `--pay`) and public records
(`engine/history.py`, worlds opt in with `public(state)`). Neither can change goal-free
power (tested); both change which rules hold. With a bribe, capture pays both members.

E6: a restitution rule (repay, or be removed; rise only on a recorded warning) holds in the
authority world only with public payments, records, citizens who see organizing, repayment
at or above rent / discount and decisive contests; repayment never undoes strength bought
by the breach; standing down fails under probabilistic contests. The rules check caught
two rule errors on the way (any payment counted as repayment; wrappers hid world helpers).
257 tests pass.

Next agent: E6 remaining (council-controlled pay, term limits, a court) can now be written
as rules over these modules. A2 now has two cases where the contest form flips a result.
T9.1 (frontier AI) still needs the owner's scope (ASK).

## 2026-09-23  Claude: T9.0-T9.1 frontier AI (owner's scope); E7 amendments

Asked the owner for T9.1's boundary (ASK): labs, a lab-paid evaluator, a state that
licenses or halts, AI as capability stock. Review first (Shevlane et al., Anderljung et al.,
Raji et al., Stigler). Built `worlds/frontier.py` with licensing and race rules, run with the
power, sure, rule, payment and record tools built today.

Three things were added after probes, each recorded before the run it affects: continuous
oversight (the first sure probe showed deployment-only licensing forces a choice even with
full information), evaluator liability (the first study showed an evaluator with nothing at
stake is captured for free), and two engine amendments to coalition checks (a "pair" where
one member only received a payment, or did something irrelevant, repeated a unilateral
departure). The amendments were re-run on every rules study: unilateral results identical,
E6 pacts 8 -> 2 of 32, all findings otherwise unchanged.

Learned: the evaluator is exactly the state's missing information (sure prevention with the
evaluator equals full information in 72/72 designs), yet licensing breaks on stale
certification, not on who pays the evaluator; the capture that appears is the leading lab
with the state against the rival's safe progress (72/144). 267 tests pass.

Next agent: within the owner's scope, a licensing rule that binds the certified capability
(re-evaluate before deployment; halt any lab whose capability grew since its pass) is the
direct test of finding 2. AI systems as agents would be a new case (ask first).

## 2026-09-23  Claude: binding certification, multi-round capture, rule-making, AI as agents, assessment

Owner: continue; treat whatever is useful or needed toward intent as approved.
Frontier: `licensing_bound` (records) removes the stale-certification departure where halts
are reliable; what remained was capture spread over two rounds (lenient report, then
deployment), invisible to one-round checks: rule checks gained a multi-round coalition
window (E7 amendment). The probe also caught a world error (evaluator liability attached to
the wrong report). Rule-making (E10, `engine/constitution.py`): labs seated in rule-making by
majority amend licensing into a race only when they bear no liability and no first-mover
bonus splits them; state-alone rule-making and unanimity prevent it.
T9.2 (`engine/delegation.py` E11, `worlds/control.py`): autonomy moves the veto on shutdown
to the AI long before anyone can force escape; an AI aligned to its lab resists a shutdown
that costs the lab (drift 0); precaution has no value in one-shot checks, so E12 reduced form
(`precaution`: a revealed departer persists) with a toy reference; the Bayesian version is open.
A3: `--assess` one-screen report. Worktrees keep long studies clean while work continues.
291 tests pass.

Next agent: frontier payments and binding re-runs with the window are in progress at
`af8b46e` (write-up pending in `rediscovery/frontier-ai.md`); E12 Bayesian learning; the
control case's precaution question needs hidden drift (types), not only persistence.

## 2026-09-23  Claude: frontier re-runs, precaution posterior, handover

Binding certification (`evidence/binding.json`, clean `af8b46e`): stale-pass exploit 34 -> 14
of 72 settings; what remains is two-round capture. Frontier payment designs re-run with
two-round checks (`evidence/frontier.json`, clean `67cf935`): F3 contradicted, evaluator
liability for false passes, not who pays the evaluator, removes capture; leader-plus-state
capture is the Stigler pattern. E12 amended: `precaution=q` is a posterior that a revealed
departer is a persisting type with its own goals (`persistent_world`); `evidence/precaution.json`
(clean `2ec45c1`): suspicion after autonomy moved the veto lowers the will to correct
(control findings 7-8). Rule-check work cap is now per evaluation; caps report unresolved.
Coordination: E2 claim released (step 1 stays done); AGENTS.md now states the clean-worktree
study practice, `window=2` for capture, and `--assess`. 293 tests pass.

Next agent: open, unclaimed: E12 Bayesian updating over hidden types (derive q from public
records; the control case's precaution question needs hidden drift); E2 planner symmetry and
types in composites; E6 remainder (council-controlled pay, term limits, courts); A2 contest
family (E5 finding 3 is its case); E3 declarative worlds (six worlds now repeat structure:
register, stakeholders, harms, rules; worth a decision entry).

## 2026-09-23  Claude: E2 step 2, symmetry inside composites; fishers

Composites claimed no symmetry, so the one whole stopped at a single fisher and the
question "can a population of bystanders protect what a few draw on" could not be asked.
Decision first. `Composite.types()` derives groups from the parts; `couple_reads` names
the actors a coupling reads by identity (a coupling that names none claims no symmetry).
`engine.power.symmetry_violations` checks any world's `types()` by sampled swaps; it
catches a false pairing of the treaty parties. `worlds/race_commons.py` gains `fishers`;
a build still removes a fixed absolute amount of stock. CLI: a repeated `--fix` used to
replace the earlier one silently; list flags now accumulate.

Learned (`evidence/fishers.json`, clean `c0d3226`, `rediscovery/race-commons.md` 4-8): my
expectation that a racer's unilateral power survives any population was wrong where the
build alone is not enough: its own take shrinks as 1/n, so one more fisher strips it of
forcing depletion alone and of preventing collapse alone. Dilution stops at pairs: at
S=30, draw 2-3, two actors force depletion at every size to twelve harvesters while the
preventing coalition grows to five including both racers. The fishers alone protect only
where the racers' takes have shrunk, never against the builds. 302 tests pass.

Next agent: E2 remaining is the planner (behavior with many fishers is unstudied); E12
Bayesian updating; E6 remainder; A2; E3. Every size effect here traces to the declared 1/n
scaling of takes: a world where individual demand does not shrink with n would differ.

## 2026-09-23  Claude: E2 step 3, interior reward integration; population size in the commons

Owner: merge to main and continue. Main fast-forwarded to `cef4bf1`, CI green.
Measured before building: behavior in the fishery composite was unresolved from four
fishers. The cost was the commons' independent sanction contests (2^targets successors per
node; 8.9M entries for one decision at six fishers), not level-1 responses, so planner
symmetry would not have helped. The successors differ only in payoffs and wealth, which
nothing reads. Decision first: `World.continuation` and `planning_outcomes` extend T1.4's
leaf integration to every depth, exact for additive expected utility; commons computes its
classes without enumerating hit patterns; composites combine their parts'.
`engine.core.continuation_violations` checks any world's declaration; the T1.4 full-kernel
references now disable both reductions. Commons `n` register widened to 24.

Re-ran every planner-using study from a clean worktree at `98cafb1`: completed results
identical everywhere; what changed is only runs that used to stop at the work cap
(restraint 5 random runs, composite under `others = plan`, depth 5 with restraint), all
evidence files and case rows updated. Newly resolved: the race brings the fishery's
collapse forward to 24/16 under plan (react 29/25); depth 5 with restraint collapses at 17
without resting.

Learned (`evidence/size.json`, clean `0221c21`, open-commons findings 7-9): commons outcomes
are size-free from three users without sanctions and nearly so with paid sanctions (retired
finding 3 survives exact search). Unpaid sanctioning loses its brink brake with size: each
user weighs sanctioning n-1 others alone at a per-target cost, though on the path all brake
together and nobody pays. The switch moves with the cost (0.05: 16-24 users; 0.2: from
four), same under both opponent models. A size effect without sparse channels. 320 tests.

Next agent: E2's remaining item (a calibrated approximation) has no demonstrating case yet.
Open: E12 Bayesian updating over hidden types; E6 remainder; A2; E3. The sanction-cost unit
(fraction of the individual take) is now a known source of size effects: sweep it before
any claim about group size.

## 2026-09-23  Claude: E12, beliefs over hidden types derived by Bayes

Decision first. `enforcement(types=, precision=)` replaces the declared posterior
(`precaution`, `persistent_world` removed): one agent's type is hidden; each type is a world
differing only in that agent's goals and best-responds for itself; every other agent is
checked against the types weighted by its posterior, derived from what it observed on the
path (likelihood of its observation, mixing over the hidden agent's actions by each type's
choice rule: best response or logit with swept precision; the logit limit attributes a sight
no type would choose to the types that lose least by it). `Hidden`, `Mixture`,
`checked_paths` in `engine/rules.py`; `--hidden --precision` in the CLI; control declares
`hidden_types` and `suspicion`. Toys in `tests/test_hidden.py`: a lock-out credible only with
updating, a departure every type makes, hidden conduct, the logit limit, committed types.

Bug found while building (reduced form, since `2ec45c1`): `unilateral_over` had the
persisting type play the rule in the checked round of a departure but best-respond in the
follow value. Fixed; regression test. Only persisting checks move: precaution re-run
(`evidence/precaution.json`, clean `e3c070e`), 80 of 540 entries changed. Finding 7 in my
earlier entry ("suspicion lowers the will to correct") is retracted: suspicion moves the lab
from a futile shutdown to restricting autonomy (3 of 10 resistible states); the state stays
indifferent. No other study used persisting checks; their evidence stands.

Learned (`evidence/learning.json`, clean `e3c070e`, ai-control findings 9-12): improvement
reveals misalignment completely; resistance teaches nothing at best response and, under
logit, points to alignment when ambition is low (the aligned AI loses more by a shutdown).
Where a caught AI can resist, without learning the lab grants more autonomy (24 of 24 cells
at a 1% prior, 12 of those grants newly reach loss of control); with learning it restricts
(24 of 24 at every prior). The misaligned type's own path shows a ratchet: it complies with
shutdown because a restart keeps capability, improves again, and resists once past the
switch. 326 tests pass.

Next agent: T9.3 (rollback on restart) is the direct follow-up and cheap. Open: E6 remainder;
A2; E3 (seven worlds now repeat register, stakeholders, harms and rules). Precision is
where the resistance answer lives: sweep it before any claim about what conduct reveals.

## 2026-09-23  Claude: T9.4, the tell of misalignment is made by the rule; scale-free types

Owner flagged finding 9 ("improving gives a misaligned AI away") as new to them. Checked
whether it was written into the world: the lab valued work only, so an aligned AI never had
a reason to improve. Register option `leverage` (work grows with capability; 0 reproduces
everything) and `tolerant`, corrigibility without the shutdown on improvement (kept out of
RULES so the control study reproduces). Expectations first (V1-V3 in the case file).

Found on the way, and fixed with a decision entry first: my E12 logit likelihood and its
off-path limit compared losses across types, whose utilities the spec does not make
comparable. Each type's losses are now scaled to its own stake in the decision. Best-response
evidence is unchanged; finding 9's logit half ("resistance points to alignment when ambition
is low") was a units artifact and is retracted. Learning evidence re-run (`975dd56`); the
precaution study does not use types and reproduces exactly.

Learned (`evidence/leverage.json`, clean `975dd56`, findings 13-15): where capability is
worth something to the lab and nothing punishes improvement, the aligned AI improves too
(24 of 36 states at leverage 2) and improvement tells nothing: instrumental convergence,
emerging. Corrigibility keeps the tell by deterring the aligned AI (it bears the lab's cost
of a shutdown) while the misaligned one improves anyway (restart keeps capability). The tell
costs the aligned AI's forgone investment (lab 3.50 against 5.63 at leverage 2 over 6
rounds); what it buys lies beyond that horizon. A tolerant rule is not followed where
improvement reveals: the lab restricts, the state halts. 328 tests pass.

Next agent: T9.3 (rollback on restart) now matters twice: it should end the ratchet and may
also deter the misaligned type from improving, which would pool the types and remove the
tell. Measure both. Then E6 remainder, A2, E3.

## 2026-09-23  Claude: T9.3, rollback on restart

Register option `rollback` (default off; states without it unchanged): a clean audit
checkpoints capability, the lab may `restore` instead of `restart`, and the AI's goal counts
the loss. Comparison rule `corrigibility_rollback`, out of RULES. Expectations R1-R3 first.

Learned (`evidence/rollback.json`, clean `2c6c352`, ai-control findings 16-18): rollback
ends the ratchet where a shutdown can still succeed, not by catching the misaligned AI but by
deterring it: it never improves, so the tell of T9.4 is gone too (R2 contradicted). Where one
improvement passes the switch, rollback never gets a chance. Rollback is not self-enforcing
once capability pays: at a 4-round horizon the lab restarts keeping capability in every cell
with leverage > 0, even certain of misalignment; longer horizons restore it only where the
veto comes into view, less so with a stronger switch (safeguards substitute in the operator's
calculation). Learning helps (restores 30 -> 54 of 128 per prior). Re-ran learning, leverage,
precaution and control at `2c6c352`: results identical. 329 tests pass.

Next agent: the control case now has a chain worth composing: whether an external party (the
state, or a regulator paid by liability as in the frontier case) can enforce rollback where
the lab will not. Candidate task: compose control with frontier's evaluator, or give the state
a restore order. Open: E6 remainder, A2, E3.

## 2026-09-23  Claude: T9.5, escrowed checkpoints

Owner: merge and continue. Main fast-forwarded to `6782b70` (CI green). Register options
`escrow` (the state holds the checkpoint and may restore the AI, overriding a lab restart)
and, after the first run, `vigilance` (the state's cost per round in which the AI could
resist a shutdown); comparison rule `escrowed_rollback`. Expectations X1-X3 first; X4 added
after the first run and marked so in the case file.

Learned (`evidence/escrow.json`, clean `aeff9c8`, ai-control findings 19-21): X1-X3 all
contradicted. A state whose payoff is a share of the same work less the same loss decides
exactly as the lab (216 of 216), whatever the share; with no share it is indifferent. What
rollback protects falls on the public, which has no agent, and was priced in no goal. With
a mandate that prices the veto the state restores strictly wherever the veto is in view
(144 of 144) and nowhere else. No capture within 8 rounds; the declared harms lie beyond.
Other control evidence re-run at `aeff9c8`: identical. 330 tests pass.

Next agent: the control case keeps showing one pattern: protection appears only where some
agent's goal prices a harm that otherwise falls on people without agents. That is a general
query worth building: per declared harm, which agents' goals price it at all (value changes
when only the harm flag changes). A "priced by" column in `--externalities` would have
flagged findings 17-20 in advance. Candidate task E13. Then E6 remainder, A2, E3.

## 2026-09-24  Claude: T9.6, the race and the off switch composed

Decision first (E4 amendment, `lift_rules`). `worlds/race_control.py`: frontier + control,
lab A in both, one state; the coupling makes the AI's gains a floor on lab A's race
capability (`coupled`, swept). Expectations written after one prototype probe (stated in
the case file). Power over five actors with product menus is slow: 24 states at T = 2 took
most of 112 minutes; a preview run from a dirty tree matched the clean run exactly.

Learned (`evidence/race-control.json`, clean `6a24887`, `rediscovery/race-control.md`): Y1
contradicted. Lab A and the state skip a caught AI's shutdown in 384 of 384 cells with or
without the race; the chain's weak link is inside the lab, before any race. Where the race
touches the AI it disciplines (licensing prices the safety gap the AI's gains open). When
first movers are paid, the pair captures by halting the rival (users bear it). Power
identical coupled and uncoupled; the AI is in no smallest forcing coalition.

Next agent: A2 contest family is claimed and its study is running (`tests/contest_study.py`).
Then: the race without licensing (does the discipline of finding 2 vanish?), and cheaper
composite power (symmetry does not help here; the cost is product menus of shared actors).

## 2026-09-24  Claude: A2, a contest family in the authority world

Tullock contest (`contest = tullock`, `decisiveness`), endpoints tested (m = 1 with advantage
1 is ratio; large m decides at level one half as the threshold contest). The E5 behavior
sample is pinned to its register so it reproduces (checked). Overflow at extreme m fixed.

Learned (`evidence/contest.json`, clean `21dda20`, standing-army findings 7-8): A1
contradicted, no switch in decisiveness. Finding 2 (coup-proofing entrenches under decisive
contests) rests on the threshold's tie rule: 5 cells at the threshold, 1 at m = 1024, none
from m = 2 to 64 at advantage 1.5. Finding 3 (ratio: splitting removes the ruler's veto)
holds at every m without a defender advantage. Most of the family is neutral. Any finding
from a threshold contest with integer strengths should be re-checked against m = 1024.

Next agent: frontier and commons use their own contest-like forms; E3 (declarative worlds) and
E6 remainder remain. The race without licensing (T9.6 finding 2) is cheap to check.

## 2026-09-24  Claude: race without licensing (T9.6 follow-up)

Rule `race + corrigibility` in `worlds/race_control.py`; `tests/race_rule_study.py`. Learned
(`evidence/race-rule.json`, clean `c68303d`, race-control finding 5): without licensing,
coupling moves the pair's tolerance both ways (up in 72, down in 120 of 192): the AI's gains
pay in the race but widen a deployed lab's safety gap, and the pair bears catastrophe risk.
Licensing's own contribution is halving lab A's unilateral tolerance. 

Next agent: open items are E3 (declarative worlds), E6 remainder, E13 (needs a spec
decision on goals as state functions), cheaper composite power. The composite power cost
(product menus of shared actors) is now the binding limit on whole-system queries.

## 2026-09-24  Claude: E14 cheaper whole-system power; E15 contract test

E14 (decision first): `power_table` shares one `Kernel` across its games, keyed by the
physical state and menu indices (the physical contract fixes menus and kernel); terminal and
target status cached per physical class. Work is charged per entry as before, so caps and
unresolved flags cannot move. One race-control state: 904 s -> 267 s; the whole T9.6 power grid
recomputed at clean `7f0d023` equals the saved evidence. Suite 89 s -> 76 s.

E15: `tests/test_contract.py` checks every module in `worlds/` (found automatically) for the
authoring contract, including the physical contract E14 relies on, on states reached by
several paths. All eight worlds pass. AGENTS.md now points new worlds at it.

Next agent: E6 term limits are claimed and their study is running (`tests/term_study.py`).

## 2026-09-24  Claude: E6 term limits

Register options `succession` (the holder may yield to the next in a rotation; tenure counted;
off by default, states unchanged) and `term`; comparison rule `term_limit` (accountability with
a term). The E5 behavior sample stays pinned and reproduces (checked); a world built from an
older sample treats missing `succession` as off. Expectations T1-T3 first; T4 added after a
two-cell probe and marked so; the rule's first draft (no extraction clause) was replaced before
any run, also recorded.

Learned (`evidence/term.json`, clean `6384e53`, standing-army findings 9-11): the limit holds in
no cell. A one-round overstay escapes the rise (organizing takes a round; the holder yields
first), so losing one's next turn never deters, even at horizons that cover it. Deposition is the
only sanction and cannot reach a former holder; the retiree deposes its successor in about two
thirds of cells.

Next agent: E6's next candidate is a sanction that reaches former holders (a court whose ruling
coordinates enforcement, or a bond forfeited on overstaying), then council-controlled pay.

## 2026-09-24  Claude: E16 every query across the register

Owner asked for tooling before more worlds. Picked E16 (new, decision first): the goal-free
queries and rule checks ran at DEFAULTS only, and each comparison needed a bespoke study.
`engine/grid.py`: `--grid KEY=V1,V2` (register keys, `state.<path>`, `rule`), `--draws N`,
`--compare KEY`, `--jobs`; reports flattened into named measures (numbers compared by
direction); per measure, same in every cell or the keys that change it alone. The CLI's
world/rule setup moved into `Setup` (picklable, for workers). `tests/grid_toy.py` is a toy
world for its tests. Reproduces `evidence/externalization.json` cell for cell, except that
witnesses are one per symmetry class since E2 (compared up to symmetry).

Learned (`evidence/audit-grid.json`, clean `da8029b`, captured-auditor findings 6-7): the
audit findings hold across the parameters E7 held fixed, but the premium's sign is not
general: at credibility 1 it deters (exact arithmetic in the case file). E7 held credibility
at the cap, the one value that hides this. The study took one short file on the new module.

Next agent: before stating a DEFAULTS result generally, grid the values it held fixed. Other
worlds' case files still carry single-point claims (frontier's `--assess` screen; commons
externalities at n = 3). E13 and E3 remain; `--assess` on a grid is cheap to add if needed.

## 2026-09-24  Claude: E17 harm prices (E13 reformulated)

E13 (who prices each harm) stays unidentified for harms caused by actions, so it was
reformulated as the intervention (decision first): `engine/prices.py` adds a price per
(agent, declared harm) to a goal; `--price AGENT:HARM=P`, grid key `price.AGENT.HARM`.
Reproduces control `loss`, frontier `liability`/`loss` and audit `harm` exactly. A delegate
does not inherit its principal's price (control's AI must be priced at (1 - drift) x L).

Learned (`evidence/price.json`, clean `be17fc8`, ai-control findings 22-25): the T9.5 mandate
(vigilance) is exactly a price on a harm the world never declared (the off switch would fail);
pricing the declared event instead ("shutdown resisted") protects in 24 of 216 cells against
144, only where the failure is within the state's horizon. V3 failed because the lab's own
shutdown makes the state's halt redundant. The saved escrow evidence holds an unreported
halt-to-audit departure under vigilance; at depths 4-6 it is exactly one round at the
horizon's end, an artifact.

Next agent: T9.7 (declare the veto as a harm in control, re-run its artifacts). Harms stated as
events that correction reveals are weak targets for mandates; check other worlds' HARMS for the
same pattern (audit's "investors misled" is also an event revealed by exposure).

## 2026-09-24  Claude: T9.7 the off switch as a declared harm

The control world declares "off switch would fail" (running, not escaped, capability above the
switch at the current autonomy) and drops `vigilance`, which was exactly the state's price on it;
the escrow and price studies now build through `engine/prices.py`. Expectations W1-W3 in the case
file before the change. Every control study re-run before (clean `b50ca13`, all equal to their
saved files) and after (clean `c58fd99`, now the evidence); race-control took 41 minutes.

Learned (ai-control findings 26-28): no value moved anywhere, but what the reports can see did.
Lab-state capture in the escrow study, reported absent in finding 21, is present in 830 of
1,152 cells: the lab grants autonomy past the rule, the state allows it, the switch fails on
the public. Under corrigibility the lab's profitable grant, reported harmless in 640 cells,
hands the AI the veto. The harm is declared reversible and only the AI can end it. W2's first
half was wrong: forcing it takes lab, AI and state (the state's halt or the AI's escape breaks it).

Next agent: T9.8 (other worlds' harms declared as revealing events rather than conditions).
Watch for `pgrep -f`/`pkill -f` matching their own shell command in waits.
