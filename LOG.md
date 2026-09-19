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
