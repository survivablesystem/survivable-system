"""Open-access commons. Paper case: rediscovery/open-commons.md.

n users draw from one regenerating stock. Each round a user takes a low (sustainable
share) or high amount, and, if it has the capability and a channel, may sanction. A
sanctioner acts against every visible user whose take exceeds its own, paying a cost per
target. Each target faces a contest (its sanctioners' combined capability against its
own); on success its take that round is confiscated and goes either back to the stock
or to the sanctioners, a design choice in the register.

Nothing here says when to take or when to sanction. The planner decides from goals.
"""
from engine.core import Agent, World

# Assumptions register for this world. Everything here is swept.
SPACE = {
    "n": (2, 12, int),
    "horizon": (1, 20, int),
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
# Fixed with a reason. K, S0_frac and S_min_frac set scale only; changing them rescales every
# quantity together. lo_frac puts the low take at 80% of maximum sustainable yield so that the
# all-low path is a stable equilibrium rather than a knife-edge that tips into decline.
FIXED = {"K": 100.0, "S0_frac": 0.5, "S_min_frac": 0.05, "lo_frac": 0.8}
# Used by --trace when a swept param is not fixed on the command line.
DEFAULTS = {"n": 4, "horizon": 12, "discount": 0.9, "channels": "all", "sanction": True,
            "sanction_cost": 0.1, "prior": "lo", "r": 0.5, "hi_mult": 2, "k": 1,
            "confiscation_to": "sanctioners"}

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
            self.add(Agent(i, p["horizon"], p["discount"], caps, channels, p["k"]))

    def prior_last(self):
        p = self.params["prior"]
        return (LO, True) if p == "ready" else (p, False)

    def initial_state(self):
        ids = [a.id for a in self.agents]
        return {"S": FIXED["S0_frac"] * self.K, "collapsed": False,
                "last": {i: self.prior_last() for i in ids},
                "value": {i: 0.0 for i in ids}, "wealth": {i: 0.0 for i in ids}}

    def actions(self, state, agent):
        acts = [(LO, False), (HI, False)]
        if agent.can("sanction") and agent.channels:
            acts += [(LO, True), (HI, True)]
        return acts

    def prior_action(self, agent, other):
        return self.prior_last()

    def amount(self, level):
        return self.lo if level == LO else self.hi

    def step(self, state, joint, rng=None):
        ids = list(joint)
        value = {i: 0.0 for i in ids}
        if state["collapsed"]:
            return {**state, "last": dict(joint), "value": value}
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
            for j in self.by_id[i].channels:
                if takes[j] > takes[i]:
                    targets.setdefault(j, []).append(i)
                    cost[i] += self.cost
        confiscated = {i: 0.0 for i in ids}
        received = {i: 0.0 for i in ids}
        for j, sanctioners in targets.items():
            m = len(sanctioners)
            p_success = m / (m + 1)            # contest: m of capability 1 against 1 of capability 1
            hit = p_success if rng is None else (1.0 if rng.random() < p_success else 0.0)
            confiscated[j] = yields[j] * hit
            if self.params["confiscation_to"] == "sanctioners":
                for i in sanctioners:
                    received[i] += confiscated[j] / m

        returned = sum(confiscated.values()) if self.params["confiscation_to"] == "stock" else 0.0
        S2 = S - sum(yields.values()) + returned
        collapsed = S2 < self.S_min
        if collapsed:
            S2 = 0.0
        wealth = dict(state["wealth"])
        for i in ids:
            value[i] = yields[i] - confiscated[i] - cost[i] + received[i]
            wealth[i] += value[i]
        return {"S": S2, "collapsed": collapsed, "last": dict(joint), "value": value, "wealth": wealth}

    def terminal(self, state):
        return "collapsed" if state["collapsed"] else None

    def label(self, state):
        return "collapsed" if state["collapsed"] else "sustained"


def make(params, rng):
    return Commons(params, rng)


def describe(joint, state):
    acts = " ".join(f"{i}:{a[0]}{'!' if a[1] else ' '}" for i, a in joint.items())
    return f"S={state['S']:6.1f}  {acts}"
