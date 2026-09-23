"""Open-access commons. Paper case: rediscovery/open-commons.md.

n users draw from one regenerating stock. Each round a user takes a low (sustainable
share) or high amount and, if it has the capability and a channel, may sanction. If the
register allows restraint, a user may instead rest: take nothing, sanction no one. A
sanctioner acts against every visible user whose take exceeds its own, paying a cost per
target. Each target faces a contest (its sanctioners' combined capability against its
own); on success its take that round is confiscated and goes either back to the stock
or to the sanctioners, a design choice in the register.

Nothing here says when to take or when to sanction. The planner decides from goals.
"""
from itertools import product

from engine.core import Agent, World

# Assumptions register for this world. Everything here is swept.
SPACE = {
    "n": (2, 12, int),
    "horizon": (1, 20, int),
    "search_depth": [1, 2, 3],       # explicit computational cap; no tail estimate
    "discount": (0.8, 0.99),
    "channels": ["none", "all"],      # whether users observe each other's takes
    "sanction": [False, True],        # whether users have the sanction capability
    "sanction_cost": (0.0, 1.0),      # per round, as a fraction of the sustainable take
    "prior": ["lo", "hi", "ready"],   # initial state: all low, all high, or all low and standing ready to sanction (an established norm)
    "r": (0.3, 0.8),                  # stock regrowth rate
    "hi_mult": (2, 4, int),           # high take as a multiple of the sustainable take
    "k": [0, 1],                      # belief level, see engine/core.py
    "confiscation_to": ["stock", "sanctioners"],  # where a confiscated take goes: a design choice
    "restraint": [False, True],       # whether a user may rest (take nothing); resting users cannot sanction
    "others": ["react", "plan"],      # level-1 opponent model, see engine/core.py
}
# Only K is a scale choice. The dimensionless fractions are substantive assumptions.
FIXED = {"K": 100.0, "S0_frac": 0.5, "S_min_frac": 0.05, "lo_frac": 0.8,
         "node_budget": 20_000, "depleted_frac": 0.25}
FIXED_REASONS = {
    "node_budget": "Per-decision emitted belief/transition/reward-entry cap, including nested plans and exact leaf reward marginals. Exhaustion is unresolved, not a physical outcome; chosen to bound enumeration cost.",
    "K": "Resource unit scale; yields and sanction costs scale with carrying capacity.",
    "S0_frac": "Starts at maximum logistic growth. Held fixed for baseline comparability; recovery from depleted stock is untested.",
    "S_min_frac": "Assumed irreversible collapse threshold. Held fixed in v0; threshold sensitivity is untested.",
    "lo_frac": "Low demand is 80% of maximum sustainable yield, below the knife-edge. Other margins are untested.",
    "depleted_frac": "Reversible harm threshold: half the stock of maximum growth. A reporting line, not a dynamic; other lines untested.",
}
# Who the modeled outcomes fall on (decision 2026-09-23, E1). Agents or not.
STAKEHOLDERS = {
    "users": "The n harvesters; the only agents.",
    "future users": "People who would harvest after the modeled horizon. No agent.",
    "stock-dependent others": "Nonhuman life and non-harvesting people that depend on the stock. No agent.",
}
HARMS = {
    "collapse": {"affects": ["users", "future users", "stock-dependent others"], "irreversible": True,
                 "description": "Stock below S_min: absorbing, no further yield or regrowth."},
    "depleted": {"affects": ["future users", "stock-dependent others"], "irreversible": False,
                 "description": "Stock below depleted_frac * K: regrowth and standing stock reduced while it lasts."},
}
EXCLUDED = {
    "entry and exit of users": "Population is fixed; newcomers and leavers are not modeled.",
    "users' dependents": "Harm to households of users is folded into users' yield.",
    "distribution within the future": "Future users are one stakeholder; who among them bears the loss is not modeled.",
}
# Used by --trace when a swept param is not fixed on the command line.
DEFAULTS = {"n": 4, "horizon": 12, "discount": 0.9, "channels": "all", "sanction": True,
            "sanction_cost": 0.1, "prior": "lo", "r": 0.5, "hi_mult": 2, "k": 1,
            "confiscation_to": "sanctioners", "search_depth": 2, "restraint": True,
            "others": "react"}

REST, LO, HI = "rest", "lo", "hi"


class Commons(World):
    name = "commons"

    def __init__(self, params, rng):
        super().__init__(params, rng)
        p = params
        self.K = FIXED["K"]
        self.S_min = FIXED["S_min_frac"] * self.K
        msy = p["r"] * self.K / 4              # maximum sustainable yield of a logistic stock
        self.lo = FIXED["lo_frac"] * msy / p["n"]
        self.hi = p["hi_mult"] * self.lo
        self.cost = p["sanction_cost"] * self.lo
        ids = [f"u{i}" for i in range(p["n"])]
        caps = frozenset({"take", "sanction"} if p["sanction"] else {"take"})
        for i in ids:
            channels = frozenset(j for j in ids if j != i) if p["channels"] == "all" else frozenset()
            self.add(Agent(i, p["horizon"], p["discount"], caps, channels, p["k"],
                           p["search_depth"], FIXED["node_budget"], p["others"]))

    def prior_last(self):
        p = self.params["prior"]
        return (LO, True) if p == "ready" else (p, False)

    def initial_state(self):
        ids = [a.id for a in self.agents]
        return {"S": FIXED["S0_frac"] * self.K, "collapsed": False,
                "last": {i: self.prior_last() for i in ids},
                "value": {i: 0.0 for i in ids}, "wealth": {i: 0.0 for i in ids}}

    def observe(self, state, agent):
        # Stock, wealth, dynamics, utilities and channel topology are known in this
        # world. Other users' unobserved actions are omitted.
        last = {other.id: state["last"][other.id]
                for other in self.agents if other.id == agent.id or agent.observes(other.id)}
        return {**state, "last": last}

    def physical(self, state):
        # Menus depend only on fixed capabilities and channels; the kernel reads S and
        # collapse. Last actions, payoffs and wealth never change what happens next.
        return {"S": state["S"], "collapsed": state["collapsed"]}

    def beliefs(self, observation, agent):
        last = {o.id: observation["last"].get(o.id, self.prior_action(agent, o)) for o in self.agents}
        return [(1.0, {**observation, "last": last})]

    def actions(self, state, agent):
        acts = [(LO, False), (HI, False)]
        if self.params["restraint"]:
            acts.append((REST, False))
        if agent.can("sanction") and agent.channels:
            acts += [(LO, True), (HI, True)]
        return acts

    def prior_action(self, agent, other):
        return self.prior_last()

    def amount(self, level):
        return {REST: 0.0, LO: self.lo, HI: self.hi}[level]

    def round_inputs(self, state, joint):
        """Shared deterministic preparation for physical and leaf reward kernels."""
        ids = list(joint)
        S = state["S"]
        S = S + self.params["r"] * S * (1 - S / self.K)     # regrowth, then harvest
        takes = {i: self.amount(a[0]) for i, a in joint.items()}
        demand = sum(takes.values())
        scale = min(1.0, S / demand) if demand > 0 else 0.0
        yields = {i: t * scale for i, t in takes.items()}

        # sanctions: each sanctioner acts against every visible user taking more than it does
        targets = {}
        cost = {i: 0.0 for i in ids}
        for i, a in joint.items():
            if not a[1]:
                continue
            for j in sorted(self.by_id[i].channels):
                if takes[j] > takes[i]:
                    targets.setdefault(j, []).append(i)
                    cost[i] += self.cost
        return S, yields, targets, cost

    def payoffs(self, yields, targets, cost, confiscated):
        received = {i: 0.0 for i in yields}
        if self.params["confiscation_to"] == "sanctioners":
            for j in sorted(targets):
                sanctioners = targets[j]
                for i in sanctioners:
                    received[i] += confiscated[j] / len(sanctioners)
        return {i: yields[i] - confiscated[i] - cost[i] + received[i] for i in yields}

    def reward_outcomes(self, state, joint):
        # Payoffs are affine in confiscation. E[C_j] = yield_j * m/(m+1).
        # Collapse affects continuation, not this round's utility. This shortcut
        # is invalid for a nonlinear replacement of value without re-derivation.
        if state["collapsed"]:
            yield 1.0, {i: 0.0 for i in joint}
            return
        _, yields, targets, cost = self.round_inputs(state, joint)
        confiscated = {i: 0.0 for i in joint}
        for j, sanctioners in targets.items():
            m = len(sanctioners)
            confiscated[j] = yields[j] * (m / (m + 1))
        yield 1.0, self.payoffs(yields, targets, cost, confiscated)

    def successor(self, state, joint, S, yields, targets, cost, confiscated):
        ids = list(joint)
        returned = sum(confiscated.values()) if self.params["confiscation_to"] == "stock" else 0.0
        S2 = S - sum(yields.values()) + returned
        collapsed = S2 < self.S_min
        wealth = dict(state["wealth"])
        value = self.payoffs(yields, targets, cost, confiscated)
        for i in ids:
            wealth[i] += value[i]
        return {"S": 0.0 if collapsed else S2, "collapsed": collapsed,
                "last": dict(joint), "value": value, "wealth": wealth}

    def outcomes(self, state, joint):
        ids = list(joint)
        if state["collapsed"]:
            yield 1.0, {**state, "last": dict(joint), "value": {i: 0.0 for i in ids}}
            return
        S, yields, targets, cost = self.round_inputs(state, joint)
        ordered_targets = sorted(targets)
        # Independent Bernoulli contests; one joint kernel for planning and play.
        for hits in product((False, True), repeat=len(ordered_targets)):
            probability = 1.0
            confiscated = {i: 0.0 for i in ids}
            for j, hit in zip(ordered_targets, hits):
                sanctioners = targets[j]
                m = len(sanctioners)
                p_success = m / (m + 1)
                probability *= p_success if hit else 1 - p_success
                confiscated[j] = yields[j] if hit else 0.0
            yield probability, self.successor(state, joint, S, yields, targets, cost, confiscated)

    def continuation(self, state):
        # Payoffs and wealth are bookkeeping: no menu, kernel, choice or goal reads them
        # (decision 2026-09-23, E2 step 3; checked in tests/test_continuation.py).
        return {"S": state["S"], "collapsed": state["collapsed"], "last": state["last"]}

    def planning_outcomes(self, state, joint, visit=lambda: None):
        """Contest outcomes grouped by the stock they return, without enumerating hit
        patterns: one class when confiscations go to sanctioners. Conditional expected
        confiscations make payoffs exact (they are affine in confiscation)."""
        ids = list(joint)
        if state["collapsed"] or not joint or not any(a[1] for a in joint.values()):
            for probability, successor in self.outcomes(state, joint):
                visit()
                yield probability, successor, {i: self.value(successor, self.by_id[i]) for i in ids}
            return
        S, yields, targets, cost = self.round_inputs(state, joint)
        to_stock = self.params["confiscation_to"] == "stock"
        # Classes keyed by the running sum `outcomes` computes, in the same id order,
        # so keys equal its floats exactly: total -> [mass, {target: P(hit, total)}, witness].
        classes = {0.0: [1.0, {}, ()]}
        for j in (i for i in ids if i in targets):
            m = len(targets[j])
            p_success = m / (m + 1)
            grown = {}
            for total, (mass, hit_mass, witness) in classes.items():
                for hit, q in ((False, 1 - p_success), (True, p_success)):
                    visit()
                    if not q:
                        continue
                    t = total + yields[j] if (hit and to_stock) else total
                    entry = grown.setdefault(t, [0.0, {}, witness + ((j,) if hit else ())])
                    entry[0] += mass * q
                    for k, v in hit_mass.items():
                        entry[1][k] = entry[1].get(k, 0.0) + v * q
                    if hit:
                        entry[1][j] = entry[1].get(j, 0.0) + mass * q
            classes = grown
        for mass, hit_mass, witness in classes.values():
            visit()
            expected = {i: yields[i] * hit_mass.get(i, 0.0) / mass for i in ids}
            payoffs = self.payoffs(yields, targets, cost, expected)
            actual = {i: yields[i] if i in witness else 0.0 for i in ids}
            yield mass, self.successor(state, joint, S, yields, targets, cost, actual), payoffs

    def types(self):
        # Users share menus, capability and a symmetric channel structure (all or none);
        # the kernel and harms read only the stock, so permuting their actions changes
        # nothing physical. Checked in tests/test_symmetry.py.
        return [[a.id for a in self.agents]]

    def stakeholders(self):
        return {"users": [a.id for a in self.agents], "future users": [], "stock-dependent others": []}

    def harmed(self, state):
        if state["collapsed"]:
            return {"collapse", "depleted"}
        return {"depleted"} if state["S"] < FIXED["depleted_frac"] * self.K else set()

    def terminal(self, state):
        return "collapsed" if state["collapsed"] else None

    def label(self, state):
        return "collapsed" if state["collapsed"] else "survived"


# Candidate rules (decision 2026-09-23, E7): declared conduct, tested, never enforced by the kernel.
def quota(world, observation, agent):
    """Everyone takes the low (sustainable) share and nobody sanctions."""
    return (LO, False)


def quota_and_sanction(world, observation, agent):
    """Everyone takes the low share and stands ready to sanction anyone seen taking more."""
    return (LO, bool(agent.can("sanction") and agent.channels))


RULES = {"quota": quota, "quota and sanction": quota_and_sanction}


def make(params, rng):
    return Commons(params, rng)


def describe(joint, state):
    acts = " ".join(f"{i}:{a[0]}{'!' if a[1] else ' '}" for i, a in joint.items())
    return f"S={state['S']:6.1f}  {acts}"
