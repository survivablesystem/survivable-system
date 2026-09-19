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
