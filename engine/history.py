"""Public records as a module over any world. Decision 2026-09-23 (E9).

Worlds declare `public(state)`: facts anyone could record. `History(world, length)` keeps
the last `length` records (newest first) in the state and adds them to every observation
as `record`; the inner observation is `now`. The inner kernel, physical state, harms and
labels are untouched, so goal-free power cannot change.
"""
from __future__ import annotations

from .core import World


class History(World):
    def __init__(self, inner, length):
        super().__init__(inner.params, inner.rng)
        if type(length) is not int or length < 1:
            raise ValueError("length must be a positive integer")
        inner.public(inner.initial_state())  # fails loudly if the world declares no public facts
        self.inner, self.length = inner, length
        self.name = f"{inner.name}+history"
        for agent in inner.agents:
            self.add(agent)

    def __getattr__(self, name):  # rules may reach the inner world's helpers (units, people, ...)
        if name == "inner":
            raise AttributeError(name)
        return getattr(self.inner, name)

    def initial_state(self):
        return {"inner": self.inner.initial_state(), "record": [], "value": {a.id: 0.0 for a in self.agents}}

    def physical(self, state):
        return self.inner.physical(state["inner"])

    def public(self, state):
        return self.inner.public(state["inner"])

    def observe(self, state, agent):
        return {"now": self.inner.observe(state["inner"], agent), "record": state["record"]}

    def beliefs(self, observation, agent):
        return [(p, {"inner": s, "record": observation["record"], "value": {a.id: 0.0 for a in self.agents}})
                for p, s in self.inner.beliefs(observation["now"], agent)]

    def actions(self, observation, agent):
        return self.inner.actions(observation["now"], agent)

    def prior_action(self, agent, other):
        return self.inner.prior_action(agent, other)

    def observed_last(self, state, agent, other):
        return self.inner.observed_last(state["inner"], agent, other)

    def outcomes(self, state, joint):
        record = ([self.inner.public(state["inner"])] + state["record"])[:self.length]
        for p, successor in self.inner.outcomes(state["inner"], joint):
            yield p, {"inner": successor, "record": record,
                      "value": {a.id: self.inner.value(successor, a) for a in self.agents}}

    def stakeholders(self):
        return self.inner.stakeholders()

    def harmed(self, state):
        return self.inner.harmed(state["inner"])

    def terminal(self, state):
        return self.inner.terminal(state["inner"])

    def label(self, state):
        return self.inner.label(state["inner"])
