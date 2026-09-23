"""Side payments as a module over any world. Decision 2026-09-23 (E8).

Each agent's action becomes (world action, transfer): "none" or "pay:<recipients>:<amount>"
for a declared (payer, recipients) pair and amount. Recipients are one agent or a group
("p0+p1"), who split the amount equally. Payments are utility, unconditional
within the round and unlimited by wealth. The base world's kernel, physical state, harms
and labels are untouched: goal-free power cannot change. `disclosure` decides who sees a
payment: "parties" (payer and recipient) or "public".
"""
from __future__ import annotations

from .core import World

NONE = "none"


class Transfers(World):
    def __init__(self, base, pairs, amounts, disclosure="parties"):
        super().__init__(base.params, base.rng)
        if disclosure not in ("parties", "public"):
            raise ValueError("disclosure must be parties or public")
        ids = {a.id for a in base.agents}
        for payer, recipient in pairs:
            group = recipient.split("+")
            if payer not in ids or not set(group) <= ids or payer in group or len(set(group)) != len(group):
                raise ValueError(f"invalid payment pair {payer!r} -> {recipient!r}")
        if not amounts or any(not a > 0 for a in amounts):
            raise ValueError("amounts must be positive")
        self.base, self.pairs, self.amounts, self.disclosure = base, [tuple(p) for p in pairs], tuple(amounts), disclosure
        self.name = f"{base.name}+transfers"
        for agent in base.agents:
            self.add(agent)

    def payments(self, agent_id):
        return [NONE] + [f"pay:{r}:{a}" for p, r in self.pairs if p == agent_id for a in self.amounts]

    @staticmethod
    def parse(transfer):
        """(recipients, amount); recipients a list, empty for no payment."""
        if transfer == NONE:
            return [], 0.0
        _, recipient, amount = transfer.split(":")
        return recipient.split("+"), float(amount)

    def initial_state(self):
        return {"base": self.base.initial_state(), "paid": {}, "value": {a.id: 0.0 for a in self.agents}}

    def physical(self, state):
        return self.base.physical(state["base"])

    def seen(self, paid, agent_id):
        return {p: t for p, t in paid.items()
                if self.disclosure == "public" or agent_id == p or agent_id in self.parse(t)[0]}

    def observe(self, state, agent):
        return {"base": self.base.observe(state["base"], agent), "paid": self.seen(state["paid"], agent.id)}

    def beliefs(self, observation, agent):
        # Payments the agent did not see are believed absent (declared point prior).
        return [(p, {"base": s, "paid": dict(observation["paid"]), "value": {a.id: 0.0 for a in self.agents}})
                for p, s in self.base.beliefs(observation["base"], agent)]

    def actions(self, observation, agent):
        return [(a, t) for a in self.base.actions(observation["base"], agent) for t in self.payments(agent.id)]

    def prior_action(self, agent, other):
        return (self.base.prior_action(agent, other), NONE)

    def observed_last(self, state, agent, other):
        last = self.base.observed_last(state["base"], agent, other)
        if last is None:
            return None
        return (last, self.seen(state["paid"], agent.id).get(other.id, NONE))

    def outcomes(self, state, joint):
        base_joint = {i: action[0] for i, action in joint.items()}
        paid = {i: action[1] for i, action in joint.items() if action[1] != NONE}
        for p, successor in self.base.outcomes(state["base"], base_joint):
            value = {a.id: self.base.value(successor, a) for a in self.agents}
            for payer, transfer in paid.items():
                recipients, amount = self.parse(transfer)
                value[payer] -= amount
                for r in recipients:
                    value[r] += amount / len(recipients)
            yield p, {"base": successor, "paid": paid, "value": value}

    def public(self, state):
        return {"base": self.base.public(state["base"]),
                "paid": dict(state["paid"]) if self.disclosure == "public" else {}}

    def stakeholders(self):
        return self.base.stakeholders()

    def harmed(self, state):
        return self.base.harmed(state["base"])

    def terminal(self, state):
        return self.base.terminal(state["base"])

    def label(self, state):
        return self.base.label(state["base"])


def lift(rule):
    """A base-world rule in the transfer world: same conduct, pay nothing."""
    def lifted(world, observation, agent):
        return (rule(world.base, observation["base"], agent), NONE)
    lifted.__doc__ = f"{(rule.__doc__ or '').strip()} Nobody pays anyone."
    return lifted
