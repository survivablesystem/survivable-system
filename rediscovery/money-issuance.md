# Rediscovery brief: money issuance and acceptance

Brief only. Derivation and world not yet done. Related to the owner's protocol at https://github.com/mediumofexchange, "money as a promise you can read, price and carry", with private claims and publicly verifiable supply.

**Known outcomes, four.** An issuer with no constraint over-issues and acceptance collapses (Weimar, Zimbabwe). Money is accepted because others are expected to accept it, so acceptance is a coordination equilibrium and can fail suddenly. Community credit systems work at a scale where trust and limits hold (WIR, Sardex) and fail where limits or clearing are absent. A publicly verifiable supply constrains an issuer that a hidden supply does not.

## Setup in primitives

```
types:
  trader (many): goals: consumption over horizon. capabilities: produce, accept or refuse a
                 unit of money in exchange, hold.
  issuer (1 or more): goals: own consumption, which issuance funds. capabilities: issue,
                 optionally redeem against a stated promise.
claims: a unit of money is a claim. Its worth to a holder is the belief that others will
        accept it. Same primitive as a rule (enforced by contest) and as legitimacy.
channels: whether supply is visible to traders is the swept variable. Whether an issuer's
          promise is readable is a second.
```

## Expected

Hidden supply: the issuer over-issues, traders learn only through prices, acceptance collapses late and all at once. Visible supply: the issuer is constrained by anticipated refusal and issues within what traders will hold. Several issuers with visible supply and readable promises: traders select among them, and the selection should reward the constrained issuer. Several issuers with hidden supply: the bad money drives out the good, because holders pass on what they trust least.

The question for the owner's protocol is the third row: whether verifiable supply plus a readable promise is enough to make issuer selection work, or whether it also needs a channel about redemption behavior.

## Expected to force

Claims as an explicit primitive, unifying rules, money and legitimacy: a claim is worth what others are believed to honor, backed by the contest that enforcing it would win. Issuance as a capability. Nothing else that the commons and treaty do not already force.
