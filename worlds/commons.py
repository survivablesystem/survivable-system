"""Open-access commons. Paper case: rediscovery/open-commons.md.

n users draw from one regenerating stock. Each round a user takes a low (sustainable
share) or high amount, and, if it has the capability and a channel, may sanction. A
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
}
# Only K is a scale choice. The dimensionless fractions are substantive assumptions.
FIXED = {"K": 100.0, "S0_frac": 0.5, "S_min_frac": 0.05, "lo_frac": 0.8,
         "node_budget": 20_000}
FIXED_REASONS = {
    "node_budget": "Per-decision belief/transition-entry cap, including nested plans. Exhaustion is unresolved, not a physical outcome; chosen to bound exact enumeration cost.",
    "K": "Resource unit scale; yields and sanction costs scale with carrying capacity.",
    "S0_frac": "Starts at maximum logistic growth. Held fixed for baseline comparability; recovery from depleted stock is untested.",
    "S_min_frac": "Assumed irreversible collapse threshold. Held fixed in v0; threshold sensitivity is untested.",
    "lo_frac": "Low demand is 80% of maximum sustainable yield, below the knife-edge. Other margins are untested.",
}
# Used by --trace when a swept param is not fixed on the command line.
DEFAULTS = {"n": 4, "horizon": 12, "discount": 0.9, "channels": "all", "sanction": True,
            "sanction_cost": 0.1, "prior": "lo", "r": 0.5, "hi_mult": 2, "k": 1,
            "confiscation_to": "sanctioners", "search_depth": 2}

LO, HI = "lo", "hi"


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
                           p["search_depth"], FIXED["node_budget"]))

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

    def beliefs(self, observation, agent):
        last = {o.id: observation["last"].get(o.id, self.prior_action(agent, o)) for o in self.agents}
        return [(1.0, {**observation, "last": last})]

    def actions(self, state, agent):
        acts = [(LO, False), (HI, False)]
        if agent.can("sanction") and agent.channels:
            acts += [(LO, True), (HI, True)]
        return acts

    def prior_action(self, agent, other):
        return self.prior_last()

    def amount(self, level):
        return self.lo if level == LO else self.hi

    def outcomes(self, state, joint):
        ids = list(joint)
        value = {i: 0.0 for i in ids}
        if state["collapsed"]:
            yield 1.0, {**state, "last": dict(joint), "value": value}
            return
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
        ordered_targets = sorted(targets)
        # Independent Bernoulli contests; one joint kernel for planning and play.
        for hits in product((False, True), repeat=len(ordered_targets)):
            probability = 1.0
            confiscated = {i: 0.0 for i in ids}
            received = {i: 0.0 for i in ids}
            for j, hit in zip(ordered_targets, hits):
                sanctioners = targets[j]
                m = len(sanctioners)
                p_success = m / (m + 1)
                probability *= p_success if hit else 1 - p_success
                confiscated[j] = yields[j] if hit else 0.0
                if self.params["confiscation_to"] == "sanctioners":
                    for i in sanctioners:
                        received[i] += confiscated[j] / m
            returned = sum(confiscated.values()) if self.params["confiscation_to"] == "stock" else 0.0
            S2 = S - sum(yields.values()) + returned
            collapsed = S2 < self.S_min
            wealth, value = dict(state["wealth"]), {}
            for i in ids:
                value[i] = yields[i] - confiscated[i] - cost[i] + received[i]
                wealth[i] += value[i]
            yield probability, {"S": 0.0 if collapsed else S2, "collapsed": collapsed,
                                "last": dict(joint), "value": value, "wealth": wealth}

    def terminal(self, state):
        return "collapsed" if state["collapsed"] else None

    def label(self, state):
        return "collapsed" if state["collapsed"] else "survived"


def make(params, rng):
    return Commons(params, rng)


def describe(joint, state):
    acts = " ".join(f"{i}:{a[0]}{'!' if a[1] else ' '}" for i, a in joint.items())
    return f"S={state['S']:6.1f}  {acts}"
