"""Rules as claims: declared conduct, self-enforcement and profitable deviation.
Decision 2026-09-23 (E7).

A rule is a function (world, observation, agent) -> action for every agent, reading only
that agent's observation. The kernel never enforces it: following is a choice, and these
queries ask whether it is worth making. Goals are read here (unlike engine/power.py):
whether a rule holds depends on what agents want.

Checks are one-shot departures: depart now, then everyone follows the rule for the rest
of `depth` rounds. Applied at the start and at every state reachable with at most one
departure per round, this is the one-shot deviation test of the rule and of the
punishments it prescribes. Value beyond `depth` is not counted, for following or for
punishment alike.
"""
from __future__ import annotations
from itertools import combinations, product
import math

from .core import distribution, key

BUDGET = 2_000_000  # emitted kernel entries per query
TOLERANCE = 1e-9


class RuleLimitExceeded(RuntimeError):
    def __init__(self, budget):
        self.budget = budget
        super().__init__(f"rule check exceeded {budget} kernel entries; unresolved")


class Check:
    def __init__(self, world, rule, budget=BUDGET):
        self.world, self.rule, self.budget = world, rule, budget
        self.memo, self.work = {}, 0

    def visit(self):
        self.work += 1
        if self.work > self.budget:
            raise RuleLimitExceeded(self.budget)

    def prescribed(self, state):
        """The joint action the rule prescribes; each must be on the agent's menu."""
        joint = {}
        for a in self.world.agents:
            observation = self.world.observe(state, a)
            action = self.rule(self.world, observation, a)
            if key(action) not in {key(x) for x in self.world.actions(observation, a)}:
                raise ValueError(f"rule prescribes {action!r} to {a.id}, not on its menu")
            joint[a.id] = action
        return joint

    def play(self, state, joint, depth):
        """Per-agent values of `joint` now and following afterwards, and the declared harms
        reached with positive probability (within `depth` rounds, the start excluded)."""
        world = self.world
        values = {a.id: 0.0 for a in world.agents}
        harms = set()
        for p, successor in distribution(world.outcomes(state, joint), self.visit):
            harms |= set(world.harmed(successor))
            later = {a.id: 0.0 for a in world.agents}
            if depth > 1 and world.terminal(successor) is None:
                later, later_harms = self.follow(successor, depth - 1)
                harms |= later_harms
            for a in world.agents:
                values[a.id] += p * (world.value(successor, a) + a.discount * later[a.id])
        return values, harms

    def follow(self, state, depth):
        memo_key = (key(state), depth)
        if memo_key not in self.memo:
            self.memo[memo_key] = self.play(state, self.prescribed(state), depth)
        return self.memo[memo_key]

    def menus(self, state, coalition):
        return [self.world.actions(self.world.observe(state, self.world.by_id[i]), self.world.by_id[i])
                for i in coalition]

    def unilateral(self, state, agent_id, depth):
        """Best one-shot departure of one agent using only its own information: one action
        per observation, valued over its beliefs. Gain is over following, same beliefs."""
        world, agent = self.world, self.world.by_id[agent_id]
        observation = world.observe(state, agent)
        support = distribution(world.beliefs(observation, agent), self.visit)
        follow = math.fsum(p * self.follow(s, depth)[0][agent_id] for p, s in support)
        rule_action = self.rule(world, observation, agent)
        top, choice = None, rule_action
        for action in world.actions(observation, agent):
            if key(action) == key(rule_action):
                continue  # gain is over the best alternative: negative means a margin
            v = math.fsum(p * self.play(s, {**self.prescribed(s), agent_id: action}, depth)[0][agent_id]
                          for p, s in support)
            if top is None or v > top + TOLERANCE:
                top, choice = v, action
        if top is None:  # nothing else on the menu
            return {"gain": 0.0, "action": rule_action, "rule_action": rule_action}
        return {"gain": top - follow, "action": choice, "rule_action": rule_action}

    def joint(self, state, coalition, depth, outside=lambda harms: {}):
        """Best one-shot joint departure of a coalition, full information, summed value; and
        the best among departures that newly reach a harm falling outside the coalition
        (`outside` maps new harms to the outside stakeholders they fall on), with summed value
        and, separately, among those where no member loses and one gains (no side payments
        needed beyond those the world itself offers)."""
        base = self.prescribed(state)
        follow, follow_harms = self.follow(state, depth)
        top = ext = every = None
        for choice in product(*self.menus(state, coalition)):
            if all(key(a) == key(base[i]) for i, a in zip(coalition, choice)):
                continue
            values, harms = self.play(state, {**base, **dict(zip(coalition, choice))}, depth)
            total = math.fsum(values[i] for i in coalition)
            falls = {h: names for h, names in outside(sorted(harms - follow_harms)).items() if names}
            entry = (total, values, harms, dict(zip(coalition, choice)), falls)
            if top is None or total > top[0] + TOLERANCE:
                top = entry
            if falls and (ext is None or total > ext[0] + TOLERANCE):
                ext = entry
            gains = [values[i] - follow[i] for i in coalition]
            if falls and all(g >= -TOLERANCE for g in gains) and any(g > TOLERANCE for g in gains) \
                    and (every is None or total > every[0] + TOLERANCE):
                every = entry

        def describe(entry):
            if entry is None:
                return None
            total, values, harms, actions, falls = entry
            members = {i: values[i] - follow[i] for i in coalition}
            return {"gain": total - math.fsum(follow[i] for i in coalition), "members": members,
                    # without side payments: no member loses and one gains
                    "every_member": all(g >= -TOLERANCE for g in members.values()) and any(g > TOLERANCE for g in members.values()),
                    "others": {i: values[i] - follow[i] for i in follow if i not in coalition},
                    "actions": actions, "new_harms": sorted(harms - follow_harms), "falls_outside": falls}
        if top is None:
            return {"gain": 0.0, "members": {i: 0.0 for i in coalition}, "every_member": False, "others": {},
                    "actions": {i: base[i] for i in coalition}, "new_harms": [], "falls_outside": {},
                    "externalizing": None, "externalizing_every": None}
        return {**describe(top), "externalizing": describe(ext), "externalizing_every": describe(every)}


def follow_value(world, rule, state, depth, budget=BUDGET):
    """Everyone's expected discounted value within `depth` rounds if all follow the rule."""
    return Check(world, rule, budget).follow(state, depth)[0]


def checked_states(world, rule, state, reach, budget=BUDGET):
    """The start and every state within `reach` rounds where at most one agent departs per
    round: the rule's path and the punishments it prescribes one step off it."""
    check = Check(world, rule, budget)
    frontier, seen = [state], {key(state): state}
    for _ in range(reach):
        nxt = []
        for s in frontier:
            if world.terminal(s) is not None:
                continue
            base = check.prescribed(s)
            joints = [base] + [{**base, a.id: action} for a in world.agents
                               for action in world.actions(world.observe(s, a), a)
                               if key(action) != key(base[a.id])]
            for joint in joints:
                for _, s2 in distribution(world.outcomes(s, joint), check.visit):
                    if key(s2) not in seen and world.terminal(s2) is None:
                        seen[key(s2)] = s2
                        nxt.append(s2)
        frontier = nxt
    return list(seen.values())


def enforcement(world, module, rule, state, depth, reach=1, max_size=2, budget=BUDGET):
    """Does `rule` hold from `state` within `depth` rounds?

    unilateral: per agent, the largest one-shot gain of its best alternative over following
    (its own information; negative is a margin) over the checked states, with the witness
    state and action. coalitions: per coalition
    up to `max_size`, the largest one-shot joint gain (full information, summed value, so
    an upper bound) over the same states, with per-member gains, what non-members lose and
    declared harms newly reached; and `externalizing`, the largest gain among departures
    that newly reach a harm falling on stakeholders outside the coalition (capture), and
    `externalizing_every`, the same restricted to departures that pay every member without
    side payments the world does not offer. None marks a check stopped by the work cap: unresolved.
    """
    check = Check(world, rule, budget)
    states = checked_states(world, rule, state, reach, budget)
    members = world.stakeholders()
    ids = [a.id for a in world.agents]

    def worst(evaluate):
        out = None
        for n, s in enumerate(states):
            try:
                r = evaluate(s)
            except RuleLimitExceeded as error:
                return {"gain": None, "error": str(error)}
            if out is None or r["gain"] > out["gain"] + TOLERANCE:
                out = {**r, "at_start": n == 0, "state": s}
        return out

    unilateral = {i: worst(lambda s, i=i: check.unilateral(s, i, depth)) for i in ids}
    coalitions = []
    for size in range(2, max_size + 1):
        for coalition in combinations(ids, size):
            c = set(coalition)
            outside = lambda harms, c=c: {h: [n for n in module.HARMS[h]["affects"] if not set(members[n]) & c]
                                          for h in harms}
            r = worst(lambda s, c=coalition, o=outside: check.joint(s, list(c), depth, o))
            if r["gain"] is not None:  # the largest externalizing gains over the checked states
                for field in ("externalizing", "externalizing_every"):
                    ext = None
                    for n, s in enumerate(states):
                        e = check.joint(s, list(coalition), depth, outside)[field]
                        if e is not None and (ext is None or e["gain"] > ext["gain"] + TOLERANCE):
                            ext = {**e, "at_start": n == 0, "state": s}
                    r[field] = ext
            coalitions.append({"coalition": list(coalition), **r})
    gains = [r["gain"] for r in unilateral.values()]
    return {"holds_unilaterally": None if None in gains else all(g <= TOLERANCE for g in gains),
            "unilateral": unilateral, "coalitions": coalitions,
            "follow": check.follow(state, depth)[0], "harms_under_rule": sorted(check.follow(state, depth)[1]),
            "depth": depth, "reach": reach, "states_checked": len(states)}
