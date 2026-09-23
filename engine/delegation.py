"""Delegation with drift as a goal module over any world. Decision 2026-09-23 (E11).

For each declared delegate, utility becomes (1 - drift) x its principal's utility plus
drift x its own (the world's value for it). Kernel, observations, menus and harms are
untouched: goal-free power cannot change; drift changes which rules hold and what agents do.
"""
from __future__ import annotations

from .core import World


class Delegation(World):
    def __init__(self, inner, principals, drift):
        super().__init__(inner.params, inner.rng)
        ids = {a.id for a in inner.agents}
        for d, p in principals.items():
            if d not in ids or p not in ids or d == p:
                raise ValueError(f"invalid delegation {d!r} <- {p!r}")
            if not 0.0 <= drift[d] <= 1.0:
                raise ValueError("drift must be in [0, 1]")
        self.inner, self.principals, self.drift = inner, dict(principals), dict(drift)
        self.name = f"{inner.name}+delegation"
        for agent in inner.agents:
            self.add(agent)

    def __getattr__(self, name):
        if name == "inner":
            raise AttributeError(name)
        return getattr(self.inner, name)

    def mixed(self, successor):
        values = {a.id: self.inner.value(successor, a) for a in self.agents}
        for d, p in self.principals.items():
            values[d] = (1 - self.drift[d]) * values[p] + self.drift[d] * values[d]
        return values

    def outcomes(self, state, joint):
        for p, successor in self.inner.outcomes(state, joint):
            yield p, {**successor, "value": self.mixed(successor)}

    # Everything else is the inner world's.
    def initial_state(self): return self.inner.initial_state()
    def physical(self, state): return self.inner.physical(state)
    def public(self, state): return self.inner.public(state)
    def observe(self, state, agent): return self.inner.observe(state, agent)
    def beliefs(self, observation, agent): return self.inner.beliefs(observation, agent)
    def actions(self, observation, agent): return self.inner.actions(observation, agent)
    def prior_action(self, agent, other): return self.inner.prior_action(agent, other)
    def observed_last(self, state, agent, other): return self.inner.observed_last(state, agent, other)
    def stakeholders(self): return self.inner.stakeholders()
    def harmed(self, state): return self.inner.harmed(state)
    def terminal(self, state): return self.inner.terminal(state)
    def label(self, state): return self.inner.label(state)
    def types(self): return self.inner.types()
