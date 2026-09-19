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
