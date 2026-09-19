# Search reduction: preimplementation checks

T1.4. Constructed computational diagnostics, not empirical evidence.

Hypothesis: repeated physical kernels and nested decisions account for enough work
that exact, per-decision reuse can extend covered depth/population. First profile
the existing search at n=4/10, depths 2/3, initial and contested states.
The simplest candidate caches identical state/joint kernels within one decision;
retain all state fields, posterior weights, observations and agent identities.
No averaging of branch losses or merging by observation alone.

Disconfirmation: little reuse, worse runtime/memory, any changed action ranking,
hidden-information leak, or failure to extend coverage at the same work cap.
If this fails, record the boundary before choosing a broader replacement.
Compare exact arithmetic diagnostics, asymmetric hidden beliefs, and retained
commons traces. Keep unresolved runs; measure actual work and elapsed time.
No depth-12 or population conclusion without completed matched runs.

## Profile and revised hypothesis

Baseline artifact: `evidence/search-profile-before.json`, clean source `2535e47`.
After one all-high round, n=4/depth=3 emits 17,589 kernel entries in 3,816 calls
(3,476 unique). The analogous n=10/depth=2 search stops at 20,001 total entries
after only 116 kernel calls, 93 unique. Simple duplicate reuse has limited reach;
large independent contest supports dominate. Nested responses already have an
observation/depth/agent cache (213 complete responses in the n=4/depth=3 probe).

Revised simplest design: at depth 1 only, use an exact immediate-utility marginal.
Default worlds retain full enumeration; commons shares payoff arithmetic and uses
expected confiscations. Earlier branches, posteriors, observations and all physical
transitions remain enumerated. Expect at least n=8/depth=2 or n=4/depth=4 coverage
to improve at the unchanged 20,000-entry cap; n=10 may still exhaust it on interior
branches. Any discrepancy from full-kernel utility or hidden-information references
rejects this reduction. Decision recorded before code in `DECISIONS.md`.

## Findings

Adopt exact leaf reward integration. Commons payoffs are affine in confiscated
amounts: each target's expected confiscation is its scaled yield times `m/(m+1)`.
Costs are deterministic and receipts are linear shares. This permits summing
expected immediate utility without constructing every independent contest outcome.
Collapse and information still require physical branches at earlier search steps.
Worlds with nonlinear utility retain the default full-kernel marginal unless they
prove another exact reduction. No sampling error or heuristic tail is introduced.

Work counts for u0 after one all-high physical round (20,000-entry cap):

| Users / depth | Full physical leaves | Reduced leaves | Result |
|---|---:|---:|---|
| 4 / 2 | 774 | 221 | identical values |
| 4 / 3 | 17,803 | 4,590 | identical values |
| 8 / 2 | unresolved at 20,001 | 5,241 | newly completed |
| 10 / 2 | unresolved at 20,001 | unresolved at 20,001 | no coverage claim |
| 10 / 3 | unresolved at 20,001 | unresolved at 20,001 | no coverage claim |

A separate 2,000,000-entry reference cap completes the eight-user decision in
348,202 entries. Both paths give, in menu order, 2.375 / 3.625 / 10.25 / 3.625 and
choose low take with sanction. This cap is only a correctness reference; the
coverage comparison uses the unchanged 20,000 cap. Per-entry computational cost
changes: leaf marginals count once, rather than once per physical branch. The cap
is not a runtime or memory bound, and work counts are not wall-time speedups.

Paired 30-round runs, seeds 0/1:

| Configuration | Full physical leaves | Reduced leaves |
|---|---|---|
| baseline n=4, depth 2 | collapse 17 | identical trace |
| n=4, depth 3 | collapse 17 | identical trace |
| n=8, depth 2 | unresolved after round 1 | collapse 17 |
| n=10, depth 2 | unresolved after round 1 | unresolved after round 1 |
| unpaid sanctions, n=4, depth 2 | collapse 7 | identical trace |

First finding: the eight-user limit was partly terminal contest enumeration, not a
different behavioral result. Completing this scoped case shows the same depletion
cycle. Both seeds follow identical symmetric paths; they do not establish
behavioral diversity or a population effect. No depth-12 comparison was attempted.

All 21 retained 12-round traces replay identically. Every agent's values and actions
in the retained 17-round baseline agree (maximum absolute error zero). Completed
paired decision probes also agree exactly. Across 128 registered parameter samples
with explicit stock/joint-action probes, maximum marginal utility discrepancy is
`8.89e-16` (floating-point roundoff, not approximation). Tests additionally enumerate
all three-user joints at four stocks and both confiscation destinations, compare
asymmetric contested plans, and check nonlinear risk, hidden/revealed future bits,
nonuniform priors and aborts on invalid or excessive reward entries.

Local trial timings: a four-user depth-3 complete run fell from roughly 13 s to
5 s; newly completed eight-user runs took 17–24 s. Some capped ten-user decision
probes took longer (roughly 0.5 s to 1.5 s): the reduction permits more costly
nested decisions before exhausting the same entry cap. Timing varies by pass;
artifacts retain each measurement. This is a bounded coverage improvement, not a
uniform speedup or full solution to interior branching.

## Reproduction and boundary

`python -m tests.search_profile` measures kernel calls and nested response cache
size. `python -m tests.search_reduction` compares full physical leaf enumeration
against the exact marginal under the current planner, checks the larger reference,
replays retained evidence and saves parameters/seeds/work/timing/source hashes.
Artifacts: `evidence/search-profile-before.json`, `search-profile-after.json`,
`search-reduction.json`. The before profile identifies clean source `2535e47`.
Tests: `python -m pytest -q`.

Affected parties remain the modeled commons users, with per-user wealth preserved
in physical traces. External users, future people and empirical institutional
validity remain excluded as in the original case. This computational change makes
more scoped calculations possible; it supplies no new evidence about those groups.

Next: T1.1 sparse channels, retaining unresolved rows. Larger/deeper inference
still needs a demonstrated reduction of interior branches, with observation and
posterior equivalence, before making same-horizon or broad population comparisons.
