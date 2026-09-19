# Rediscovery suite

The test of `spec/PRIMITIVES.md`. Each case is a structure whose outcome history already knows. The case is set up in primitives only. First the derivation is followed by hand; then a world in `worlds/` runs it. Nothing about the outcome is written into the setup.

Pass: the known outcome emerges. Fail: it does not, which means a primitive is missing. Both are recorded. A fail is the more valuable result, because it names the missing primitive. A third result exists and is the best of all: the outcome emerges for a different reason than the paper derivation gave. The commons did this on its first run.

Each case file has: setup, derivation, whether it emerges, the gap found, what the engine should show, and, once a world exists, engine findings with the one-at-a-time table.

| Case | Tests | Paper | Engine |
|---|---|---|---|
| open-commons.md | beliefs, coalition formation, correction | emerges | `worlds/commons.py`; both outcomes, sanctioning must pay the sanctioner |
| standing-army.md | rules as claims, contests, delegation drift, lock-in | emerges | not yet |
| captured-auditor.md | channels, selection, horizon | emerges | not yet |
| treaty-no-verification.md | relative goals, verification channel, repeated play | brief only | not yet |
| kinship-trust.md | goals over others' outcomes, trust radius, group selection | brief only | not yet |
| money-issuance.md | money as a claim, issuance capability, acceptance as belief | brief only | not yet |

Briefs state the known outcomes and what the case is expected to force. The derivation is done by whoever claims the task.
