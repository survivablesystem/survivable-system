# Planner replacement: paper checks

Constructed diagnostics, not empirical validation. T1.3 follows `planner-audit.md`.

Before building: the simplest adequate replacement enumerates action sequences and finite stochastic outcomes, then groups future states by the actor's observation. Candidate menus use that observation; conditional beliefs carry hidden possibilities. Execution samples the same outcome kernel. No investment rule or risk preference is added.

Expected: invest then consume is worth 3, consume then consume 2. Risky is worth -4, safe 1. An unrevealed fair bit permits only 1/2 expected accuracy even when search branches over both true bits; revealing it permits accuracy 1. A contrary result falsifies the implementation. Directed response must still depend on incoming observation; adaptive evasion can change its numerical value. Tie order remains explicit.

Search is exact only within the finite beliefs, opponent model and effective depth. Commons defaults to depth 2, sweeping 1/2/3 separately from horizon; no assumed utility beyond the cap. A work cap must stop with an unresolved result, never false survival or a partially scored winner. Initial terminal states need no action; terminal rewards count once.

Comparison: old and new commons, seeds 0/1/2, 12 rounds, defaults plus isolated controls (horizon 2, no channels, no sanctions, unpaid sanctions, k=0, n=2). Save per-agent initial values, full traces, elapsed seconds and source hashes. Record physical parameters and each implementation's planning limits. These are short local comparisons, not robustness evidence; matched seeds do not guarantee matched shocks when the sampler changes. Any changed outcome gets an action-value probe before altering an expectation.

## Findings

Pending implementation and comparison.
