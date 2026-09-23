"""Composition: several worlds analysed as one system. Decision 2026-09-23 (E4).

Parts keep their own kernels, observations and beliefs. Local agent ids map to global
actors, so one actor can act in several parts; its action is a mapping part -> local
action. Each round the parts run in a declared order with independent chance, then a
declared, deterministic `couple` carries flows between parts. The interface (mapping,
order, coupling, covered exclusions) is an authored assumption stated by the composite's
module; everything else is the parts' own mechanics.
"""
from __future__ import annotations
from itertools import product

from .core import Agent, World, distribution, key


def identity(state, joint):
    return state


class Composite(World):
    name = "composite"

    def __init__(self, params, rng, parts, members, couple=None, planning=None, stakeholders=None,
                 couple_reads=None):
        """parts: name -> World (in kernel order); members: part -> {local id: global id};
        couple(state, joint) -> state, pure and deterministic; planning: Agent keyword
        arguments shared by every actor; stakeholders: global name -> [(part, local name)];
        couple_reads: actors the coupling reads by identity (None with a coupling: all)."""
        super().__init__(params, rng)
        self.parts, self.members = dict(parts), {p: dict(m) for p, m in members.items()}
        self.couple_reads = couple_reads
        for part, world in self.parts.items():
            if set(self.members[part]) != {a.id for a in world.agents}:
                raise ValueError(f"members of {part} must map exactly its agents")
        self.couple = couple or identity
        self.local = {}  # global id -> {part: local agent}
        for part, mapping in self.members.items():
            for local, actor in mapping.items():
                self.local.setdefault(actor, {})[part] = self.parts[part].by_id[local]
        self.outsider = {}  # global id -> stand-in agent for parts it is not in
        for actor, where in self.local.items():
            channels = frozenset(self.members[part][other] for part, agent in where.items()
                                 for other in agent.channels)
            self.add(Agent(actor, channels=channels, capabilities=frozenset().union(
                *(a.capabilities for a in where.values())), **(planning or {})))
            self.outsider[actor] = Agent(actor)
        self.stakeholder_map = stakeholders or {}

    def types(self):
        """Actors exchangeable in every part they share, and not read by identity by the
        coupling (decision 2026-09-23, E2 step 2). The coupling may read part states only
        through what the parts' `physical` keeps symmetric."""
        reads = self.couple_reads
        if reads is None:
            reads = [] if self.couple is identity else [a.id for a in self.agents]
        position = {p: {i: n for n, group in enumerate(w.types()) for i in group} for p, w in self.parts.items()}
        groups = {}
        for a in self.agents:
            signature = (a.id,) if a.id in reads else tuple(
                position[p].get(self.local[a.id][p].id) if p in self.local[a.id] else None for p in self.parts)
            groups.setdefault(signature, []).append(a.id)
        return list(groups.values())

    def view(self, part, actor):
        return self.local[actor].get(part, self.outsider[actor])

    def initial_state(self):
        return {"parts": {p: w.initial_state() for p, w in self.parts.items()}, "value": {a.id: 0.0 for a in self.agents}}

    def physical(self, state):
        return {p: w.physical(state["parts"][p]) for p, w in self.parts.items()}

    def observe(self, state, agent):
        return {p: w.observe(state["parts"][p], self.view(p, agent.id)) for p, w in self.parts.items()}

    def beliefs(self, observation, agent):
        support = [(1.0, {})]
        for p, w in self.parts.items():
            part_support = distribution(w.beliefs(observation[p], self.view(p, agent.id)))
            support = [(q * r, {**s, p: sub}) for q, s in support for r, sub in part_support]
        return [(q, {"parts": s, "value": {a.id: 0.0 for a in self.agents}}) for q, s in support]

    def actions(self, observation, agent):
        where = self.local[agent.id]
        menus = [self.parts[p].actions(observation[p], where[p]) for p in where]
        return [dict(zip(where, choice)) for choice in product(*menus)]

    def prior_action(self, agent, other):
        return {p: self.parts[p].prior_action(self.view(p, agent.id), local)
                for p, local in self.local[other.id].items()}

    def part_joint(self, part, joint):
        return {local: joint[actor][part] for local, actor in self.members[part].items()}

    def outcomes(self, state, joint):
        branches = [(1.0, {})]
        for p, w in self.parts.items():
            part_support = distribution(w.outcomes(state["parts"][p], self.part_joint(p, joint)))
            branches = [(q * r, {**s, p: sub}) for q, s in branches for r, sub in part_support]
        for probability, parts in branches:
            coupled = self.couple({"parts": parts}, joint)
            value = {a.id: sum(self.parts[p].value(coupled["parts"][p], local)
                               for p, local in self.local[a.id].items()) for a in self.agents}
            yield probability, {"parts": coupled["parts"], "value": value}

    def continuation(self, state):
        return {p: w.continuation(state["parts"][p]) for p, w in self.parts.items()}

    def payoff_sum(self, part_payoffs):
        return {a.id: sum(part_payoffs[p][local.id] for p, local in self.local[a.id].items()) for a in self.agents}

    def planning_outcomes(self, state, joint, visit=lambda: None):
        """Parts' continuation classes, combined; the coupling acts on each representative
        and must not change part values (decision 2026-09-23, E2 step 3)."""
        branches = [(1.0, {}, {})]
        for p, w in self.parts.items():
            support = list(w.planning_outcomes(state["parts"][p], self.part_joint(p, joint), visit))
            branches = [(q * r, {**s, p: sub}, {**pay, p: part_pay}) for q, s, pay in branches for r, sub, part_pay in support]
        for probability, parts, payoffs in branches:
            coupled = self.couple({"parts": parts}, joint)
            value = {a.id: sum(self.parts[p].value(coupled["parts"][p], local)
                               for p, local in self.local[a.id].items()) for a in self.agents}
            yield probability, {"parts": coupled["parts"], "value": value}, self.payoff_sum(payoffs)

    def reward_outcomes(self, state, joint):
        branches = [(1.0, {})]
        for p, w in self.parts.items():
            support = list(w.reward_outcomes(state["parts"][p], self.part_joint(p, joint)))
            branches = [(q * r, {**pay, p: part_pay}) for q, pay in branches for r, part_pay in support]
        for probability, payoffs in branches:
            yield probability, self.payoff_sum(payoffs)

    def observed_last(self, state, agent, other):
        """What `agent` saw `other` do last, part by part; priors where it saw nothing."""
        seen, out = False, {}
        for p, local_other in self.local[other.id].items():
            viewer = self.view(p, agent.id)
            last = self.parts[p].observed_last(state["parts"][p], viewer, local_other) if viewer.channels else None
            seen = seen or last is not None
            out[p] = last if last is not None else self.parts[p].prior_action(viewer, local_other)
        return out if seen else None

    def terminal(self, state):
        labels = {p: w.terminal(state["parts"][p]) for p, w in self.parts.items()}
        if all(label is not None for label in labels.values()):
            return "; ".join(f"{p}: {label}" for p, label in labels.items())
        return None

    def label(self, state):
        return "; ".join(f"{p}: {w.label(state['parts'][p])}" for p, w in self.parts.items())

    def stakeholders(self):
        out = {}
        for name, sources in self.stakeholder_map.items():
            ids = []
            for part, local_name in sources:
                ids += [self.members[part][i] for i in self.parts[part].stakeholders()[local_name]]
            out[name] = sorted(set(ids), key=[a.id for a in self.agents].index)
        return out

    def harmed(self, state):
        return {f"{p}: {h}" for p, w in self.parts.items() for h in w.harmed(state["parts"][p])}


def lift_rules(part_rules):
    """The whole's rule: each actor follows each part's rule in the parts it acts in, from its
    view of that part (decision 2026-09-23, E4 amendment)."""
    def rule(world, observation, agent):
        return {p: part_rules[p](world.parts[p], observation[p], world.local[agent.id][p])
                for p in world.local[agent.id]}
    rule.__doc__ = " ".join(f"{p}: {(r.__doc__ or '').strip()}" for p, r in part_rules.items())
    return rule


def part_harms(modules, stakeholder_map):
    """HARMS of the whole: each part harm, prefixed, with stakeholders renamed globally."""
    rename = {(part, local): name for name, sources in stakeholder_map.items() for part, local in sources}
    out = {}
    for part, module in modules.items():
        for harm, spec in module.HARMS.items():
            out[f"{part}: {harm}"] = {**spec, "affects": sorted({rename[(part, s)] for s in spec["affects"]})}
    return out


def uncovered(modules, excluded, covers):
    """Part exclusions that the whole neither carries nor covers (must be empty)."""
    carried = set(excluded) | set(covers)
    return [f"{part}: {name}" for part, module in modules.items() for name in module.EXCLUDED
            if f"{part}: {name}" not in carried]
