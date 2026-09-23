"""Capability race under a no-building treaty. Paper case: rediscovery/treaty-no-verification.md.

Two parties, a and b, hold, build or strike each round. Building adds capability, with
swept returns to scale, and costs welfare. A strike is a contest decided by start-of-round
capabilities; success disarms the target, an irreversible outcome. Verification decides
what each party sees of the other. The treaty ("neither builds") is not in the kernel:
whether it holds is a pattern of play, enforced only by the rival's response.

Nothing here says when to build or strike. The planner decides from goals.
"""
from math import comb, floor

from engine.core import Agent, World

SPACE = {
    "returns": (0.0, 0.5),            # build gain is 1 + floor(returns * capability)
    "contest": ["ratio", "threshold"],
    "advantage": (1.5, 3.0),          # threshold contest: success iff striker >= advantage * target
    "lead": (0, 3, int),              # a's initial capability minus b's
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
}
FIXED = {"base": 2, "cap": 12, "node_budget": 20_000}
FIXED_REASONS = {
    "base": "Trailing party's initial capability. Scale choice; the lead is swept.",
    "cap": "Capability ceiling keeping the state space finite. Runs that reach it are visible in their traces; behavior at the ceiling is an artifact.",
    "node_budget": "Per-decision work cap, as in the commons. Exhaustion is unresolved, not an outcome.",
}
DEFAULTS = {"returns": 0.25, "contest": "threshold", "advantage": 2.0, "lead": 1,
            "verification": "exact", "security": 0.5, "build_cost": 0.3, "strike_cost": 0.1,
            "prize": 2.0, "prior_build": 0.5, "horizon": 6, "search_depth": 2,
            "discount": 0.9, "k": 1, "opening": "hold"}

HOLD, BUILD, STRIKE = "hold", "build", "strike"
RIVAL = {"a": "b", "b": "a"}


class Treaty(World):
    name = "treaty"

    def __init__(self, params, rng):
        super().__init__(params, rng)
        p = params
        exact = p["verification"] == "exact"
        for i in ("a", "b"):
            channels = frozenset({RIVAL[i]}) if exact else frozenset()
            self.add(Agent(i, p["horizon"], p["discount"], frozenset({"build", "strike"}),
                           channels, p["k"], p["search_depth"], FIXED["node_budget"]))

    def start(self, i):
        return FIXED["base"] + (self.params["lead"] if i == "a" else 0)

    def grow(self, c):
        return min(FIXED["cap"], c + 1 + floor(self.params["returns"] * c))

    def after_builds(self, i, k):
        c = self.start(i)
        for _ in range(k):
            c = self.grow(c)
        return c

    def initial_state(self):
        return {"t": 0, "cap": {i: self.start(i) for i in ("a", "b")},
                "builds": {"a": 0, "b": 0}, "strikes": {"a": 0, "b": 0},
                "last": {"a": self.params["opening"], "b": self.params["opening"]},
                "value": {"a": 0.0, "b": 0.0}, "end": None}

    def physical(self, state):
        # Menus are fixed; the kernel reads capabilities; terminal status is `end`.
        return {"cap": state["cap"], "end": state["end"]}

    def observe(self, state, agent):
        i, j = agent.id, RIVAL[agent.id]
        seen = {"t": state["t"], "end": state["end"], "strikes": dict(state["strikes"]),
                "cap": {i: state["cap"][i]}, "builds": {i: state["builds"][i]},
                "last": {i: state["last"][i]}}
        if agent.observes(j):
            seen["cap"][j] = state["cap"][j]
            seen["builds"][j] = state["builds"][j]
            seen["last"][j] = state["last"][j]
        return seen

    def beliefs(self, observation, agent):
        i, j = agent.id, RIVAL[agent.id]
        base = {**observation, "value": {"a": 0.0, "b": 0.0}}
        if j in observation["cap"]:
            return [(1.0, base)]
        # Unobserved rival: it built in each non-strike round with probability prior_build.
        rounds = observation["t"] - observation["strikes"][j]
        q = self.params["prior_build"]
        support = []
        for k in range(rounds + 1):
            probability = comb(rounds, k) * q ** k * (1 - q) ** (rounds - k)
            if probability:
                support.append((probability, {
                    **base, "cap": {**observation["cap"], j: self.after_builds(j, k)},
                    "builds": {**observation["builds"], j: k},
                    "last": {**observation["last"], j: self.prior_action(agent, self.by_id[j])}}))
        return support

    def actions(self, observation, agent):
        return [HOLD, BUILD, STRIKE]

    def prior_action(self, agent, other):
        return BUILD if self.params["prior_build"] >= 0.5 else HOLD

    def contest(self, striker, target, cap):
        cs, ct = cap[striker], cap[target]
        if self.params["contest"] == "threshold":
            return 1.0 if cs > ct and cs >= self.params["advantage"] * ct else 0.0
        return cs / (cs + ct) if cs + ct else 0.5

    def outcomes(self, state, joint):
        p = self.params
        if state["end"] is not None:
            yield 1.0, {**state, "last": dict(joint), "value": {"a": 0.0, "b": 0.0}}
            return
        cap = state["cap"]
        strikers = [i for i in ("a", "b") if joint[i] == STRIKE]
        if len(strikers) == 2:
            if p["contest"] == "threshold":
                wins = {"a": self.contest("a", "b", cap), "b": self.contest("b", "a", cap)}
                branches = [(wins["a"], "b"), (wins["b"], "a"), (1 - wins["a"] - wins["b"], None)]
            else:
                pa = self.contest("a", "b", cap)
                branches = [(pa, "b"), (1 - pa, "a")]
        elif strikers:
            s = strikers[0]
            success = self.contest(s, RIVAL[s], cap)
            branches = [(success, RIVAL[s]), (1 - success, None)]
        else:
            branches = [(1.0, None)]
        for probability, loser in branches:
            if probability <= 0:
                continue
            new_cap = {i: self.grow(cap[i]) if joint[i] == BUILD else cap[i] for i in ("a", "b")}
            if loser is not None:
                new_cap[loser] = 0
            value = {}
            for i in ("a", "b"):
                j = RIVAL[i]
                v = p["security"] * (new_cap[i] - new_cap[j]) / FIXED["cap"]
                v -= p["build_cost"] * (joint[i] == BUILD) + p["strike_cost"] * (joint[i] == STRIKE)
                if loser is not None:
                    v += p["prize"] if loser == j else -p["prize"]
                value[i] = v
            yield probability, {
                "t": state["t"] + 1, "cap": new_cap,
                "builds": {i: state["builds"][i] + (joint[i] == BUILD) for i in ("a", "b")},
                "strikes": {i: state["strikes"][i] + (joint[i] == STRIKE) for i in ("a", "b")},
                "last": dict(joint), "value": value,
                "end": None if loser is None else f"{loser}_disarmed"}

    def terminal(self, state):
        return state["end"]

    def label(self, state):
        return state["end"] or "no_disarm"


def make(params, rng):
    return Treaty(params, rng)


def describe(joint, state):
    return (f"a:{joint['a']:6s} b:{joint['b']:6s}  cap a={state['cap']['a']:2d} b={state['cap']['b']:2d}"
            + (f"  {state['end']}" if state["end"] else ""))
