# Planner replacement: paper checks

Constructed diagnostics, not empirical validation. T1.3 follows `planner-audit.md`.

Before building: the simplest adequate replacement enumerates action sequences and finite stochastic outcomes, then groups future states by the actor's observation. Candidate menus use that observation; conditional beliefs carry hidden possibilities. Execution samples the same outcome kernel. No investment rule or risk preference is added.

Expected: invest then consume is worth 3, consume then consume 2. Risky is worth -4, safe 1. An unrevealed fair bit permits only 1/2 expected accuracy even when search branches over both true bits; revealing it permits accuracy 1. A contrary result falsifies the implementation. Directed response must still depend on incoming observation; adaptive evasion can change its numerical value. Tie order remains explicit.

Search is exact only within the finite beliefs, opponent model and effective depth. Commons defaults to depth 2, sweeping 1/2/3 separately from horizon; no assumed utility beyond the cap. A work cap must stop with an unresolved result, never false survival or a partially scored winner. Initial terminal states need no action; terminal rewards count once.

Comparison: old and new commons, seeds 0/1/2, 12 rounds, defaults plus isolated controls (horizon 2, no channels, no sanctions, unpaid sanctions, k=0, n=2). Save per-agent initial values, full traces, elapsed seconds and source hashes. Record physical parameters and each implementation's planning limits. These are short local comparisons, not robustness evidence; matched seeds do not guarantee matched shocks when the sampler changes. Any changed outcome gets an action-value probe before altering an expectation.

## Findings

Exact checks pass: investment values are consume 2 / invest 3; risky utility is -4 / safe 1. Directed take is now worth 1 with an incoming observer (take then quiet), versus 2 without one; quiet also reaches 1, so the old chosen action is preserved by the declared tie rule. Hidden future bits cannot yield clairvoyant guesses: without a signal accuracy is `max(p, 1-p)`, with a signal 1. The signal can be chosen despite its cost. Costs/probabilities vary across the small tests.

Matched 12-round comparisons (three seeds each):

| Isolated control | Old horizon-12 planner | New depth-2 planner |
|---|---|---|
| baseline | all survive 12 | all survive 12 |
| horizon 2 | all survive 12 | all survive 12 |
| no channels | collapse at 5 | collapse at 5 |
| no sanctions | collapse at 5 | collapse at 5 |
| unpaid sanctions | collapse at 10 | collapse at 7 |
| level 0 | all survive 12 | all survive 12 |
| two users | all survive 12 | collapse at 7 |

These comparisons change both search semantics and effective depth. A separate 30-round control from the archived old source distinguishes the depth confound: old horizon 12 survives all four seeds; old horizon 2 collapses at 17, exactly as the new depth-2 baseline does. **Do not attribute that baseline reversal to adaptive planning or branch integration.** Full depth-12 enumeration has not been completed; the former favorable claim remains historical evidence under its approximation, not a refuted same-horizon result.

The new baseline's first surprise is a profitable three-round cycle that depletes stock: high take, low with sanction, low without sanction. All four agents independently choose it. Initial values for u0, in menu order, are 10.825 / 13.325 / 7 / 13.325. Round 2 values are 4.75 / 7.25 / 11.5 / 7.25; round 3 are 7 / 3.5 / 7 / 3.5. The cycle lowers stock from 50 to 47.079; repeating it collapses at 17. Full per-round/per-agent probes are saved. No world rule or payoff was tuned to restore cooperation.

Depth/size checks, seeds 0..3, requested duration 30 (every seed agrees within each row):

| Users | Depth 1 | Depth 2 | Depth 3 |
|---|---|---|---|
| 2 | collapse 5 | collapse 7 | collapse 9 |
| 4 | collapse 17 | collapse 17 | collapse 17 |
| 10 | collapse 17 | unresolved after round 1 | unresolved before round 1 |

Four identical seeds here add no behavioral diversity: the symmetric realized baseline paths have no contested targets, although counterfactual planning branches are stochastic. This is a local depth/size check, not a sweep over structural uncertainty or evidence of a real-world size effect.

Cost on the local Windows/Python-3.12 machine: three 12-round baseline runs plus an initial value probe took about 2.08 s old horizon 12, 0.35 s old horizon 2, and 2.05 s new depth 2. Four new 30-round n=4 runs took about 0.08 / 2.89 / 42.48 s at depths 1/2/3. Ten-user depth 2 exhausted the 20,000-entry budget in all four runs. Timings are descriptive, not stable performance assertions. Exact enumeration is already the next bottleneck; deeper-horizon/sparse-channel conclusions must wait for demonstrated tractable coverage or evidence-preserving reduction.

Migration: `observe` + finite `beliefs` replace `belief_state`; `outcomes` replaces world-authored `step` and its mean-state switch. Schema 2 adds completion status and effective planning limits. One joint-CDF draw samples each physical transition, so old seed-specific stochastic paths are not preserved even where distributions are. Earlier artifacts retain their source revisions. No compatibility planner is kept.

Artifacts: `evidence/planner-replacement-before.json`, `planner-baseline-duration.json` (old source exported using `git archive`; its archive revision is explicit), `planner-replacement-after.json`, `planner-limits.json` and `planner-audit-replacement.json`. Fixtures record hashes and source provenance. Regenerate current comparisons with `python -m tests.planner_comparison` and `python -m tests.planner_limits`.
