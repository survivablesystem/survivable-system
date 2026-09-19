# Rediscovery brief: kinship and the trust radius

Brief only. Derivation and world not yet done. Most of human history was lived in kin-based societies, and they are as much a subject here as states and labs.

**Known outcomes, three.** Kin groups sustain cooperation without formal enforcement at small scale. They fail to extend it: cooperation stops at the kin boundary, with nepotism inside and feuding across (Fukuyama's trust radius; Henrich on kin-based versus impersonal institutions). Impersonal institutions, rules with third-party enforcement, extend cooperation beyond kin, but only where the enforcement pays whoever does it (Greif's contrast of Maghribi traders, who relied on reputation inside a closed group, with Genoese traders, who built courts).

## Setup in primitives

```
types:
  person (many): goals: own consumption plus a weight w on the consumption of kin.
                 capabilities: exchange (cooperate or defect in a pairwise trade), sanction.
groups: kin groups of size g. Channels dense inside a group, sparse or absent across.
selection: optionally at the group level. Groups whose members cooperate more grow.
modules: an impersonal enforcer, a delegated agent paid per enforcement, with channels
         across groups.
```

Trust, in this model, is a belief about another agent's next action grounded in a channel. The trust radius is the set of agents about whom one holds such beliefs. That makes the radius an output, not an input.

## Expected

High w and dense channels: cooperation inside groups with no sanctions at all. Across groups: defection, unless a channel and a paid enforcer exist. Adding the enforcer extends cooperation exactly as far as its channels and its pay reach. Group-level selection should favor high w at small g and favor impersonal enforcement at large scale. The transition from the first to the second is the outcome history knows, and the interesting output is what structure sits at the transition.

## Expected to force

Goals over other agents' states (shared with treaty). Structured channels (a group graph, not all-or-none), which the commons also needs for its size effect. Selection at the group level, if the transition does not emerge without it.
