"""Harm prices as a goal module over any world. Decision 2026-09-24 (E17).

Each declared (agent, harm, amount) subtracts the amount from that agent's utility on every
transition into a state where the harm holds: once per round a persisting harm holds, once
on entry for a terminal harm (terminal rewards count on entry only). Kernel, observations,
menus and harms are untouched: goal-free power cannot change; prices change which rules hold
and what agents do. This asks what happens if X's goal carries H, not whether it already
does: that attribution is not identified for harms caused by actions (see E13).

A price applies to the agent's final utility. Over a delegation (E11) a delegate does not
inherit its principal's price: price it too if the question is the principal's goal.
"""
from __future__ import annotations

from .core import World


class Prices(World):
    def __init__(self, inner, prices, harms):
        """`prices`: {(agent id, harm name): amount}; `harms`: the world's declared HARMS."""
        super().__init__(inner.params, inner.rng)
        ids = {a.id for a in inner.agents}
        for (agent, harm), amount in prices.items():
            if agent not in ids:
                raise ValueError(f"unknown agent {agent!r} in a harm price; choose from {', '.join(sorted(ids))}")
            if harm not in harms:
                raise ValueError(f"unknown harm {harm!r}; declared: {', '.join(harms)}")
            if not isinstance(amount, (int, float)) or isinstance(amount, bool) or amount != amount or abs(amount) == float("inf"):
                raise ValueError("a harm price must be a finite number")
        self.inner, self.prices = inner, {k: float(v) for k, v in prices.items()}
        self.name = f"{inner.name}+prices"
        for agent in inner.agents:
            self.add(agent)

    def __getattr__(self, name):  # rules may reach the inner world's helpers
        if name == "inner":
            raise AttributeError(name)
        return getattr(self.inner, name)

    def priced(self, successor):
        values = {a.id: self.inner.value(successor, a) for a in self.agents}
        harms = self.inner.harmed(successor) if self.prices else set()
        for (agent, harm), amount in self.prices.items():
            if harm in harms:
                values[agent] -= amount
        return values

    def outcomes(self, state, joint):
        for p, successor in self.inner.outcomes(state, joint):
            yield p, {**successor, "value": self.priced(successor)}

    # Payoffs are integrated per successor before grouping (World.planning_outcomes), so the
    # inner continuation still covers everything future choices depend on.
    def continuation(self, state): return self.inner.continuation(state)

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


def parse_prices(items):
    """`AGENT:HARM=AMOUNT` per item -> {(agent, harm): amount}."""
    out = {}
    for item in items or []:
        head, sep, amount = item.rpartition("=")
        agent, colon, harm = head.partition(":")
        if not sep or not colon or not agent or not harm:
            raise ValueError(f"expected AGENT:HARM=AMOUNT, got {item!r}")
        if (agent, harm) in out:
            raise ValueError(f"duplicate price for {agent}:{harm}")
        try:
            out[(agent, harm)] = float(amount)
        except ValueError:
            raise ValueError(f"a price must be a number, got {amount!r}") from None
    return out
