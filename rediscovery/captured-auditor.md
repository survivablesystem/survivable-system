# An auditor paid by the audited

T2.0 evidence review, 2026-09-23. The earlier brief is kept below as the paper
conjecture. This is also the first case for rules as claims (E7): capture is a coalition
that profits by departing from a rule together while someone outside bears the cost.

## Question

When a firm pays and chooses its auditor, which conduct holds: independence (honest
reports, strict audits) or capture (misstatements passed)? Does any single agent gain by
breaking independence, or only the firm and its auditor together? What do an independent
exposure channel, license revocation, credibility and taking the choice of auditor away
from the firm change? Goal-free power answers only who is needed to mislead; the case is
about incentives, so the rule queries carry it.

## Sources and evidence status

| Claim | Source | Status here |
|---|---|---|
| Switching costs give incumbent auditors client-specific quasi-rents, a reason to please the client; larger auditors have more to lose and supply higher quality | DeAngelo, "Auditor size and audit quality", *J. Accounting and Economics* 3(3), 1981, 183-199 | verified abstract |
| Under issuer-pays, rating agencies inflate more when more investors are naive and expected reputation costs are low; issuers shop for ratings | Bolton, Freixas and Shapiro, "The Credit Ratings Game", *J. Finance* 67(1), 2012, 85-111 | verified abstract |
| In large US frauds 1996-2004, auditors revealed 14%, employees 19%, industry regulators 16%, media 14%, the SEC 6% | Dyck, Morse and Zingales, "Who Blows the Whistle on Corporate Fraud?", *J. Finance* 65(6), 2010, 2213-2253 | verified abstract |
| Governance and incentive problems of capital-market intermediaries contributed to Enron's rise and fall | Healy and Palepu, "The Fall of Enron", *J. Economic Perspectives* 17(2), 2003, 3-26 | verified abstract |

The brief's "never by the auditor" is contradicted by Dyck et al. (14%); dropped. Its
"regardless of individual goals" is a conjecture the rule queries can test.

## Hypotheses and rivals

- C1 (brief): when the firm can switch, leniency is self-enforcing for auditors; exposure
  and horizon bound it.
- C2 (brief): taking the choice of auditor from the firm makes honesty self-enforcing.
- Rival R (reputation; DeAngelo, Bolton et al.): credibility is worth money, so exposure
  times the credibility premium disciplines auditors.
- Rival P (pair capture): under independence no single agent gains by departing, but the
  firm and its auditor gain together at investors' expense. Then the problem is a coalition,
  and remedies aimed at one agent's incentive (switching) miss it.

## World (`worlds/audit.py`)

Firm, `auditors` audit firms, a regulator. Each round the books are weak with chance
`weak`; the firm reports honestly or misstates and names next round's auditor (unless
`assignment` is fixed); the hired auditor commits to strict or lenient (a contingent
stance, since moves are simultaneous). A passed misstatement misleads investors (no agent);
with chance `exposure` it is exposed at once: the auditor loses one credibility step and the
firm pays `penalty`. A clean opinion earns the firm `premium` times its auditor's
credibility share; revealed weakness costs `penalty`. The regulator (if `regulator` =
revokes) may revoke an exposed auditor; revoked auditors leave. Rules: `independence`
(honest, strict, keep the auditor, revoke the exposed) and `capture` (misstate weak books,
lenient, drop an auditor that just qualified, revoke the exposed).

## Expectations stated before the study

- Q1 (C1): under `capture`, the hired auditor loses by turning strict when the firm can
  switch and there is another auditor; not when assignment is fixed. Contradiction: strict
  pays under switching.
- Q2: `independence` holds against every unilateral departure in the grid. Contradiction:
  a single agent gains.
- Q3 (R): the firm-auditor pair's externalizing gain under `independence` falls with
  exposure and with revocation. Contradiction: no dependence on exposure.
- Q4 (P against C2): fixed assignment does not remove the pair's gain under `independence`.
  Contradiction: fixed assignment removes it.

## Affected and excluded

Modeled: firm, auditors, regulator (agents); investors (no agent) bear misleading. Excluded
and named: auditor entry, investor behavior, litigation, auditors' other clients, the
firm's workers and creditors (folded into investors).

## Earlier brief (paper conjecture, 2026-09-15; unsourced, kept for history)

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
