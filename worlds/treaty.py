"""Capability race under a no-building treaty. Paper case: rediscovery/treaty-no-verification.md.

Two parties, a and b, hold, build or strike each round, in one of `domains` capability
domains. Building adds capability in a domain, with swept returns to scale, and costs
welfare. A strike is a contest decided by start-of-round capability in its domain; success
disarms the target, an irreversible outcome. Verification decides what each party sees of
the other. The treaty ("neither builds") is not in the kernel: whether it holds is a
pattern of play, enforced only by the rival's response.

Nothing here says when to build or strike. The planner decides from goals.
"""
from itertools import product
from math import factorial, floor, prod

from engine.core import Agent, World

SPACE = {
    "returns": (0.0, 0.5),            # build gain is 1 + floor(returns * capability * scale)
    "contest": ["ratio", "threshold"],
    "advantage": (1.5, 3.0),          # threshold contest: success iff striker >= advantage * target
    "lead": (0, 3, int),              # a's initial capability minus b's, in every domain
    "verification": ["none", "exact"],
    "security": (0.0, 1.0),           # weight on relative capability per round
    "build_cost": (0.0, 1.0),
    "strike_cost": (0.0, 0.5),
    "prize": (0.5, 5.0),              # gained by disarming the rival, lost by being disarmed
    "prior_build": (0.0, 1.0),        # belief that an unobserved rival built in a round
    "horizon": (1, 12, int),
    "search_depth": [1, 2, 3],
    "discount": (0.8, 0.99),
    "k": [0, 1],
    "opening": ["hold", "build"],     # last action each party saw the other take before round 1
    "elasticity": [1.0, 1.5, 2.0],    # above one, larger parties grow proportionally faster
    "budget": ["free", "scarce"],     # scarce: a build costs build_units, income one unit per round
    "reserve": (0, 3, int),           # scarce budget: units held before round 1
    "domains": [1, 2],                # capability domains; a strike is decided within one
    "others": ["react", "plan"],      # level-1 opponent model, see engine/core.py
}
FIXED = {"base": 2, "cap": 12, "node_budget": 20_000, "build_units": 2}
FIXED_REASONS = {
    "base": "Trailing party's initial capability per domain. Scale choice; the lead is swept.",
    "cap": "Capability ceiling per domain keeping the state space finite. Runs that reach it are visible in their traces; behavior at the ceiling is an artifact.",
    "node_budget": "Per-decision work cap, as in the commons. Exhaustion is unresolved, not an outcome.",
    "build_units": "Scarce budget: two rounds of income per build, so a party can build at most every other round on income alone. The simplest binding scarcity; other ratios untested.",
}
DEFAULTS = {"returns": 0.25, "contest": "threshold", "advantage": 2.0, "lead": 1,
            "verification": "exact", "security": 0.5, "build_cost": 0.3, "strike_cost": 0.1,
            "prize": 2.0, "prior_build": 0.5, "horizon": 6, "search_depth": 2,
            "discount": 0.9, "k": 1, "opening": "hold",
            "elasticity": 1.0, "budget": "free", "reserve": 2, "domains": 1,
            "others": "react"}

HOLD, BUILD, STRIKE = "hold", "build", "strike"
RIVAL = {"a": "b", "b": "a"}
PARTIES = ("a", "b")


def named(kind, d):
    """Domain 0 keeps the plain names; later domains are suffixed."""
    return kind if d == 0 else f"{kind}:{d}"


def parse(action):
    kind, _, d = action.partition(":")
    return kind, int(d) if d else 0


class Treaty(World):
    name = "treaty"

    def __init__(self, params, rng):
        super().__init__(params, rng)
        p = params
        exact = p["verification"] == "exact"
        for i in PARTIES:
            channels = frozenset({RIVAL[i]}) if exact else frozenset()
            self.add(Agent(i, p["horizon"], p["discount"], frozenset({"build", "strike"}),
                           channels, p["k"], p["search_depth"], FIXED["node_budget"], p["others"]))

    @property
    def domains(self):
        return range(self.params["domains"])

    def start(self, i):
        return FIXED["base"] + (self.params["lead"] if i == "a" else 0)

    def grow(self, c):
        scale = (c / FIXED["base"]) ** (self.params["elasticity"] - 1)
        return min(FIXED["cap"], c + 1 + floor(self.params["returns"] * c * scale))

    def scarce(self):
        return self.params["budget"] == "scarce"

    def after_builds(self, i, ks):
        caps = []
        for k in ks:
            c = self.start(i)
            for _ in range(k):
                c = self.grow(c)
            caps.append(c)
        return caps

    def initial_state(self):
        return {"t": 0, "cap": {i: [self.start(i) for _ in self.domains] for i in PARTIES},
                "builds": {i: [0 for _ in self.domains] for i in PARTIES}, "strikes": {"a": 0, "b": 0},
                "last": {"a": self.params["opening"], "b": self.params["opening"]},
                "budget": {i: self.params["reserve"] if self.scarce() else 0 for i in PARTIES},
                "value": {"a": 0.0, "b": 0.0}, "end": None}

    def physical(self, state):
        # Menus read the own budget; the kernel reads capabilities; terminal status is `end`.
        return {"cap": state["cap"], "budget": state["budget"], "end": state["end"]}

    def observe(self, state, agent):
        i, j = agent.id, RIVAL[agent.id]
        seen = {"t": state["t"], "end": state["end"], "strikes": dict(state["strikes"]),
                "cap": {i: state["cap"][i]}, "builds": {i: state["builds"][i]},
                "last": {i: state["last"][i]}, "budget": {i: state["budget"][i]}}
        if agent.observes(j):
            for field in ("cap", "builds", "last", "budget"):
                seen[field][j] = state[field][j]
        return seen

    def beliefs(self, observation, agent):
        j = RIVAL[agent.id]
        base = {**observation, "value": {"a": 0.0, "b": 0.0}}
        if j in observation["cap"]:
            return [(1.0, base)]
        # Unobserved rival: it built in each non-strike round with probability prior_build,
        # in a uniformly chosen domain. Scarce budget: k builds fit in the last k free rounds
        # iff reserve plus income covers them; strike timing is ignored (declared). Prior
        # renormalized over feasible totals; a certain builder builds whenever it can.
        rounds = observation["t"] - observation["strikes"][j]
        q, n = self.params["prior_build"], self.params["domains"]
        reserve = self.params["reserve"] if self.scarce() else 0
        feasible = {k for k in range(rounds + 1)
                    if k == 0 or not self.scarce()
                    or reserve + rounds - FIXED["build_units"] * k >= FIXED["build_units"] - 1}
        weights = {}
        for ks in product(range(rounds + 1), repeat=n):
            k = sum(ks)
            if k in feasible:
                ways = factorial(rounds) // (factorial(rounds - k) * prod(factorial(x) for x in ks))
                weights[ks] = ways * (q / n) ** k * (1 - q) ** (rounds - k)
        total = sum(weights.values())
        if not total:
            top = max(feasible)
            weights = {ks: 1.0 for ks in product(range(top + 1), repeat=n) if sum(ks) == top}
            total = sum(weights.values())
        support = []
        for ks, weight in weights.items():
            if weight:
                support.append((weight / total, {
                    **base, "cap": {**observation["cap"], j: self.after_builds(j, ks)},
                    "builds": {**observation["builds"], j: list(ks)},
                    "budget": {**observation["budget"],
                               j: reserve + observation["t"] - FIXED["build_units"] * sum(ks) if self.scarce() else 0},
                    "last": {**observation["last"], j: self.prior_action(agent, self.by_id[j])}}))
        return support

    def actions(self, observation, agent):
        affordable = not self.scarce() or observation["budget"][agent.id] >= FIXED["build_units"]
        builds = [named(BUILD, d) for d in self.domains] if affordable else []
        return [HOLD] + builds + [named(STRIKE, d) for d in self.domains]

    def prior_action(self, agent, other):
        return BUILD if self.params["prior_build"] >= 0.5 else HOLD

    def contest(self, striker, target, cap, d):
        cs, ct = cap[striker][d], cap[target][d]
        if self.params["contest"] == "threshold":
            return 1.0 if cs > ct and cs >= self.params["advantage"] * ct else 0.0
        return cs / (cs + ct) if cs + ct else 0.5

    def strike_branches(self, joint, cap):
        """(probability, disarmed parties) over this round's strikes."""
        strikes = {i: parse(joint[i])[1] for i in PARTIES if parse(joint[i])[0] == STRIKE}
        if len(strikes) == 2 and strikes["a"] == strikes["b"]:
            d = strikes["a"]  # one contest in the shared domain
            if self.params["contest"] == "threshold":
                wa, wb = self.contest("a", "b", cap, d), self.contest("b", "a", cap, d)
                return [(wa, ("b",)), (wb, ("a",)), (1 - wa - wb, ())]
            pa = self.contest("a", "b", cap, d)
            return [(pa, ("b",)), (1 - pa, ("a",))]
        branches = [(1.0, ())]
        for s, d in strikes.items():  # independent contests in different domains
            success = self.contest(s, RIVAL[s], cap, d)
            branches = [(p * q, lost + extra) for p, lost in branches
                        for q, extra in ((success, (RIVAL[s],)), (1 - success, ()))]
        return branches

    def outcomes(self, state, joint):
        p = self.params
        if state["end"] is not None:
            yield 1.0, {**state, "last": dict(joint), "value": {"a": 0.0, "b": 0.0}}
            return
        cap = state["cap"]
        built = {i: parse(joint[i])[1] if parse(joint[i])[0] == BUILD else None for i in PARTIES}
        for probability, lost in self.strike_branches(joint, cap):
            if probability <= 0:
                continue
            new_cap = {i: [self.grow(c) if built[i] == d else c for d, c in enumerate(cap[i])] for i in PARTIES}
            for loser in lost:
                new_cap[loser] = [0 for _ in self.domains]
            value = {}
            for i in PARTIES:
                j = RIVAL[i]
                v = p["security"] * (sum(new_cap[i]) - sum(new_cap[j])) / (FIXED["cap"] * len(self.domains))
                v -= p["build_cost"] * (built[i] is not None)
                v -= p["strike_cost"] * (parse(joint[i])[0] == STRIKE)
                v += p["prize"] * (j in lost) - p["prize"] * (i in lost)
                value[i] = v
            end = None if not lost else "both_disarmed" if len(lost) == 2 else f"{lost[0]}_disarmed"
            yield probability, {
                "t": state["t"] + 1, "cap": new_cap,
                "builds": {i: [k + (built[i] == d) for d, k in enumerate(state["builds"][i])] for i in PARTIES},
                "strikes": {i: state["strikes"][i] + (parse(joint[i])[0] == STRIKE) for i in PARTIES},
                "last": dict(joint), "value": value,
                "budget": {i: state["budget"][i] + 1 - FIXED["build_units"] * (built[i] is not None)
                           if self.scarce() else 0 for i in PARTIES},
                "end": end}

    def terminal(self, state):
        return state["end"]

    def label(self, state):
        return state["end"] or "no_disarm"


def make(params, rng):
    return Treaty(params, rng)


def describe(joint, state):
    return (f"a:{joint['a']:8s} b:{joint['b']:8s}  cap a={state['cap']['a']} b={state['cap']['b']}"
            + (f"  {state['end']}" if state["end"] else ""))
