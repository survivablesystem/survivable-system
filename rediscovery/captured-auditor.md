# Rediscovery: auditor paid by the audited

**Known outcome.** Audits become lenient. Fraud is exposed, if at all, through an independent channel, never by the auditor. Arthur Andersen and Enron. Rating agencies before 2008.

## Setup in primitives

```
types:
  firm (1):        goals: money, keep license. capabilities: choose auditor, pay auditor, misstate books.
  auditor (many):  goals: money over horizon. resources: money, credibility; credibility converts
                   to future money. capabilities: report honest or lenient.
  regulator (1):   goals: accurate reports. capabilities: revoke license on evidence.
  public (many):   goals: accurate reports. no capabilities that matter here.
channels: auditor observes the firm's books. Regulator and public observe the auditor's report only.
selection: auditors with no clients exit.
```

## Derivation

An auditor plans. Honest report: the firm switches auditor next round, income falls to zero. Lenient report: income continues. Credibility falls only if the misstatement is exposed. Exposure needs a channel into the firm that no one but the auditor holds. So credibility never falls, and lenient dominates for every horizon.

An auditor whose goals weight credibility heavily still reports honestly, and is selected out: it loses clients to lenient ones. The population converges to lenient regardless of individual goals.

## Emerges?

Yes, with the primitives as stated. Selection does most of the work. Individual honest goals do not survive.

## Gap found

No missing primitive. Selection must be explicit in the world, not left to the planner, or the second paragraph of the derivation cannot happen. Recorded in the spec.

## What the engine should show

| Intervention | Expected effect |
|---|---|
| Independent channel into the firm (a protected disclosure channel, a module in T9.1) | Credibility decays with probability p per lenient round. Lenient dominates only when p is low or horizon short. The boundary in (p, horizon) is the finding |
| Regulator assigns auditors; firm cannot choose | Firm's switching capability removed. Honest becomes dominant if credibility has any weight |
| Rotation every n rounds | Partial. Lenient still pays inside the window |

This is the removed linter's lab-oversight case rediscovered from below. That case typed "auditor paid by the audited is a capture surface" into a note. Here it is derived.
