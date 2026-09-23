"""Amendable rules: a constitution module over any world. Decision 2026-09-23 (E10).

The regime in force is a public fact. Declared voters add a vote to each action: "keep"
or "amend:<regime>". When at least `threshold` votes name the same regime, it is in force
from the next round. The kernel of the inner world is untouched, so goal-free power
cannot change; what an amendment changes is which conduct the others follow, if they
treat the regime in force as binding.
"""
from __future__ import annotations

from .core import World

KEEP = "keep"


class Constitution(World):
    def __init__(self, inner, regimes, voters, threshold, initial):
        super().__init__(inner.params, inner.rng)
        ids = {a.id for a in inner.agents}
        if initial not in regimes or not set(voters) <= ids or not 1 <= threshold <= len(voters):
            raise ValueError("initial regime, voters and threshold must be declared and consistent")
        self.inner, self.regimes = inner, dict(regimes)
        self.voters, self.threshold, self.initial = list(voters), threshold, initial
        self.name = f"{inner.name}+constitution"
        for agent in inner.agents:
            self.add(agent)

    def __getattr__(self, name):
        if name == "inner":
            raise AttributeError(name)
        return getattr(self.inner, name)

    def initial_state(self):
        return {"inner": self.inner.initial_state(), "regime": self.initial, "value": {a.id: 0.0 for a in self.agents}}

    def physical(self, state):
        return self.inner.physical(state["inner"])

    def public(self, state):
        return {"inner": self.inner.public(state["inner"]), "regime": state["regime"]}

    def observe(self, state, agent):
        return {"now": self.inner.observe(state["inner"], agent), "regime": state["regime"]}

    def beliefs(self, observation, agent):
        return [(p, {"inner": s, "regime": observation["regime"], "value": {a.id: 0.0 for a in self.agents}})
                for p, s in self.inner.beliefs(observation["now"], agent)]

    def votes(self, regime, agent_id):
        if agent_id not in self.voters:
            return [KEEP]
        return [KEEP] + [f"amend:{r}" for r in self.regimes if r != regime]

    def actions(self, observation, agent):
        return [(a, v) for a in self.inner.actions(observation["now"], agent)
                for v in self.votes(observation["regime"], agent.id)]

    def prior_action(self, agent, other):
        return (self.inner.prior_action(agent, other), KEEP)

    def observed_last(self, state, agent, other):
        last = self.inner.observed_last(state["inner"], agent, other)
        return None if last is None else (last, KEEP)

    def outcomes(self, state, joint):
        tally = {}
        for i, (_, vote) in joint.items():
            if vote != KEEP and i in self.voters:
                tally[vote.split(":", 1)[1]] = tally.get(vote.split(":", 1)[1], 0) + 1
        regime = next((r for r in self.regimes if tally.get(r, 0) >= self.threshold), state["regime"])
        for p, successor in self.inner.outcomes(state["inner"], {i: a[0] for i, a in joint.items()}):
            yield p, {"inner": successor, "regime": regime,
                      "value": {a.id: self.inner.value(successor, a) for a in self.agents}}

    def stakeholders(self):
        return self.inner.stakeholders()

    def harmed(self, state):
        return self.inner.harmed(state["inner"])

    def terminal(self, state):
        return self.inner.terminal(state["inner"])

    def label(self, state):
        return f"{self.inner.label(state['inner'])} under {state['regime']}"


def constitutional(world, observation, agent):
    """Follow the conduct of the regime in force and vote to keep it."""
    return (world.regimes[observation["regime"]](world.inner, observation["now"], agent), KEEP)
