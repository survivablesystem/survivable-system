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
        super().__init__(f"rule check exceeded {budget} kernel entries in one evaluation; unresolved")

    def __reduce__(self):  # survive pickling across processes with the right message
        return (RuleLimitExceeded, (self.budget,))


class Check:
    def __init__(self, world, rule, budget=BUDGET, persistent=None):
        """`persistent`: an agent that has revealed itself by departing and keeps optimizing
        for itself afterwards (best response by backward induction, full information) while
        everyone else follows the rule (decision 2026-09-23, E12). None: everyone follows."""
        self.world, self.rule, self.budget, self.persistent = world, rule, budget, persistent
        self.memo, self.policies, self.work = {}, {}, 0

    def visit(self):
        self.work += 1
        if self.work > self.budget:
            raise RuleLimitExceeded(self.budget)

    def fresh(self):
        """Start a new evaluation's work count; memoized values stay (they are exact)."""
        self.work = 0
        return self

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

    def policy(self, state, depth):
        """What is played if nobody departs now: the rule, except a persistent agent's best
        response (ties go to the rule's action)."""
        base = self.prescribed(state)
        r = self.persistent
        if r is None:
            return base
        memo_key = (key(state), depth)
        if memo_key not in self.policies:
            agent = self.world.by_id[r]
            best_action, best_value = base[r], self.play(state, base, depth)[0][r]
            for action in self.world.actions(self.world.observe(state, agent), agent):
                if key(action) == key(base[r]):
                    continue
                v = self.play(state, {**base, r: action}, depth)[0][r]
                if v > best_value + TOLERANCE:
                    best_action, best_value = action, v
            self.policies[memo_key] = {**base, r: best_action}
        return self.policies[memo_key]

    def follow(self, state, depth):
        memo_key = (key(state), depth)
        if memo_key not in self.memo:
            self.memo[memo_key] = self.play(state, self.policy(state, depth), depth)
        return self.memo[memo_key]

    def menus(self, state, coalition):
        return [self.world.actions(self.world.observe(state, self.world.by_id[i]), self.world.by_id[i])
                for i in coalition]

    def unilateral(self, state, agent_id, depth):
        """Best one-shot departure of one agent using only its own information: one action
        per observation, valued over its beliefs. Gain is over following, same beliefs."""
        return unilateral_over([(1.0, self)], state, agent_id, depth)

    def joint(self, state, coalition, depth, outside=lambda harms: {}):
        """Best one-shot joint departure of a coalition (every member departs), full
        information, summed value. Externalizing departures must also need the coalition:
        its summed gain beats what any one member gets it by departing alone. And
        the best among departures that newly reach a harm falling outside the coalition
        (`outside` maps new harms to the outside stakeholders they fall on), with summed value
        and, separately, among those where no member loses and one gains (no side payments
        needed beyond those the world itself offers)."""
        base = self.prescribed(state)
        follow, follow_harms = self.follow(state, depth)
        menus = self.menus(state, coalition)
        # What the coalition's summed value gains when one member departs alone: a joint
        # departure counts as needing the coalition only if it beats all of these.
        alone = 0.0
        for i, menu in zip(coalition, menus):
            for a in menu:
                if key(a) != key(base[i]):
                    values, _ = self.play(state, {**base, i: a}, depth)
                    alone = max(alone, math.fsum(values[j] - follow[j] for j in coalition))
        top = ext = every = None
        for choice in product(*menus):
            if any(key(a) == key(base[i]) for i, a in zip(coalition, choice)):
                continue  # every member departs; departures by fewer are checked as smaller coalitions
            values, harms = self.play(state, {**base, **dict(zip(coalition, choice))}, depth)
            total = math.fsum(values[i] for i in coalition)
            falls = {h: names for h, names in outside(sorted(harms - follow_harms)).items() if names}
            entry = (total, values, harms, dict(zip(coalition, choice)), falls)
            if top is None or total > top[0] + TOLERANCE:
                top = entry
            needs_all = total - math.fsum(follow[i] for i in coalition) > alone + TOLERANCE
            if falls and needs_all and (ext is None or total > ext[0] + TOLERANCE):
                ext = entry
            gains = [values[i] - follow[i] for i in coalition]
            if falls and needs_all and all(g >= -TOLERANCE for g in gains) and any(g > TOLERANCE for g in gains) \
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
                    "externalizing": None, "externalizing_every": None, "alone": alone}
        return {**describe(top), "externalizing": describe(ext), "externalizing_every": describe(every), "alone": alone}


    def sequence(self, state, free, score, depth, window, memo):
        """Best departure over the next `window` rounds by the members in `free` (each may
        also follow in any round), then everyone follows; chosen round by round to maximize
        the summed value of `score` (full information). Returns (values, harms, first joint)."""
        world = self.world
        if window == 0 or world.terminal(state) is not None:
            values, harms = self.follow(state, depth)
            return values, harms, None
        memo_key = (key(state), depth, window, tuple(free))
        if memo_key in memo:
            return memo[memo_key]
        base = self.prescribed(state)
        best_entry = None
        for choice in product(*self.menus(state, free)):
            joint = {**base, **dict(zip(free, choice))}
            values = {a.id: 0.0 for a in world.agents}
            harms = set()
            for p, successor in distribution(world.outcomes(state, joint), self.visit):
                harms |= set(world.harmed(successor))
                later = {a.id: 0.0 for a in world.agents}
                if depth > 1 and world.terminal(successor) is None:
                    later, later_harms, _ = self.sequence(successor, free, score, depth - 1, window - 1, memo)
                    harms |= later_harms
                for a in world.agents:
                    values[a.id] += p * (world.value(successor, a) + a.discount * later[a.id])
            total = math.fsum(values[i] for i in score)
            if best_entry is None or total > best_entry[0] + TOLERANCE:
                best_entry = (total, values, harms, dict(zip(free, choice)))
        memo[memo_key] = (best_entry[1], best_entry[2], best_entry[3])
        return memo[memo_key]

    def sequential(self, state, coalition, depth, window, outside=lambda harms: {}):
        """Best coordinated departure of a coalition over `window` rounds (a report, then an
        act on it; a payment, then a favor), with what one member could get it alone over the
        same window. Capture if it needs the coalition and newly reaches a harm outside it."""
        follow, follow_harms = self.follow(state, depth)
        base = math.fsum(follow[i] for i in coalition)
        memo = {}
        values, harms, first = self.sequence(state, list(coalition), list(coalition), depth, window, memo)
        alone = max(math.fsum(self.sequence(state, [i], list(coalition), depth, window, memo)[0][j]
                              for j in coalition) - base for i in coalition)
        gain = math.fsum(values[i] for i in coalition) - base
        members = {i: values[i] - follow[i] for i in coalition}
        new = sorted(harms - follow_harms)
        falls = {h: names for h, names in outside(new).items() if names}
        return {"gain": gain, "alone": alone, "needs_all": gain > alone + TOLERANCE, "members": members,
                "every_member": all(g >= -TOLERANCE for g in members.values()) and any(g > TOLERANCE for g in members.values()),
                "others": {i: values[i] - follow[i] for i in follow if i not in coalition},
                "first": first, "new_harms": new, "falls_outside": falls,
                "capture": gain > alone + TOLERANCE and bool(falls)}


def unilateral_over(checks, state, agent_id, depth):
    """The unilateral check under a mixture of continuations: `checks` is [(weight, Check)],
    e.g. a revealed departer that persists with probability q and returns to the rule with
    1 - q (decision 2026-09-23, E12). Values are weighted before the best action is taken."""
    first = checks[0][1]
    world, agent = first.world, first.world.by_id[agent_id]
    observation = world.observe(state, agent)
    support = distribution(world.beliefs(observation, agent), first.visit)
    follow = math.fsum(w * p * c.follow(s, depth)[0][agent_id] for w, c in checks for p, s in support)
    rule_action = first.rule(world, observation, agent)
    follow_harms = set().union(*(c.follow(s, depth)[1] for w, c in checks if w > 0 for _, s in support))
    top, choice, harmful = None, rule_action, None
    for action in world.actions(observation, agent):
        if key(action) == key(rule_action):
            continue  # gain is over the best alternative: negative means a margin
        plays = [(w * p, c.play(s, {**c.prescribed(s), agent_id: action}, depth))
                 for w, c in checks if w > 0 for p, s in support]
        v = math.fsum(q * values[agent_id] for q, (values, _) in plays)
        if top is None or v > top + TOLERANCE:
            top, choice = v, action
        new = sorted(set().union(*(harms for _, (_, harms) in plays)) - follow_harms)
        if new and (harmful is None or v - follow > harmful["gain"] + TOLERANCE):
            harmful = {"gain": v - follow, "action": action, "new_harms": new}
    if top is None:  # nothing else on the menu
        return {"gain": 0.0, "action": rule_action, "rule_action": rule_action, "harmful": None}
    return {"gain": top - follow, "action": choice, "rule_action": rule_action, "harmful": harmful}


def follow_value(world, rule, state, depth, budget=BUDGET):
    """Everyone's expected discounted value within `depth` rounds if all follow the rule."""
    return Check(world, rule, budget).follow(state, depth)[0]


def checked_states(world, rule, state, reach, budget=BUDGET):
    """The start and every state within `reach` rounds where at most one agent departs per
    round: the rule's path and the punishments it prescribes one step off it."""
    return [s for s, _ in checked_with_departers(world, rule, state, reach, budget)]


def checked_with_departers(world, rule, state, reach, budget=BUDGET):
    """checked_states with, for each state, the agent whose departure reached it (the last
    one; None on the rule's path)."""
    check = Check(world, rule, budget)
    frontier, seen, who = [state], {key(state): state}, {key(state): None}
    for _ in range(reach):
        nxt = []
        for s in frontier:
            if world.terminal(s) is not None:
                continue
            base = check.prescribed(s)
            joints = [(base, who[key(s)])] + [({**base, a.id: action}, a.id) for a in world.agents
                                              for action in world.actions(world.observe(s, a), a)
                                              if key(action) != key(base[a.id])]
            for joint, departer in joints:
                for _, s2 in distribution(world.outcomes(s, joint), check.visit):
                    if key(s2) not in seen and world.terminal(s2) is None:
                        seen[key(s2)], who[key(s2)] = s2, departer
                        nxt.append(s2)
        frontier = nxt
    return [(s, who[k]) for k, s in seen.items()]


def enforcement(world, module, rule, state, depth, reach=1, max_size=2, budget=BUDGET, window=1,
                precaution=False, persistent_world=None):
    """Does `rule` hold from `state` within `depth` rounds?

    unilateral: per agent, the largest one-shot gain of its best alternative over following
    (its own information; negative is a margin) over the checked states, with the witness
    state and action, and `harmful`, the most profitable departure that newly reaches a
    declared harm (a rule can fail harmlessly: a lab that secures more than required). coalitions: per coalition
    up to `max_size`, the largest one-shot joint gain (full information, summed value, so
    an upper bound) over the same states, with per-member gains, what non-members lose and
    declared harms newly reached; and `externalizing`, the largest gain among departures
    that newly reach a harm falling on stakeholders outside the coalition (capture), and
    `externalizing_every`, the same restricted to departures that pay every member without
    side payments the world does not offer. With `window` > 1, `sequential`: the best
    coordinated departure over that many rounds (a report, then an act on it), preferring one
    that needs the coalition and lands a harm outside it (capture). With `precaution` (True, or
    a probability q), single agents at a state reached by another's departure are checked
    against a departer that keeps optimizing for itself with probability q (a declared
    posterior that the departer is a type that persists), so a precaution (shutting down an
    agent caught departing) has the value of what it prevents. `persistent_world`: the same world
    with the persisting type's goals (for example a delegate at full drift), or a mapping from
    agent id to such a world (other departers persist with their own goals); default `world`. None marks a check stopped by the work cap: unresolved.
    """
    check = Check(world, rule, budget)
    tagged = checked_with_departers(world, rule, state, reach, budget)
    states = [s for s, _ in tagged]
    departers = {key(s): d for s, d in tagged}
    members = world.stakeholders()
    ids = [a.id for a in world.agents]
    persistent_checks = {}

    q = 1.0 if precaution is True else float(precaution or 0.0)
    if not 0.0 <= q <= 1.0:
        raise ValueError("precaution is a probability (or True for certainty)")

    class Mixed:
        """i checked against j persisting with probability q, returning to the rule otherwise."""
        def __init__(self, persistent):
            self.parts = [(q, persistent), (1.0 - q, check)]

        def fresh(self):
            for _, c in self.parts:
                c.fresh()
            return self

        def unilateral(self, s, i, depth):
            return unilateral_over(self.parts, s, i, depth)

    def checker(s, i):
        """With `precaution` q, at a state reached by j's departure, i (not j) is checked
        against a j that keeps optimizing for itself with probability q (E12)."""
        j = departers.get(key(s))
        if q == 0.0 or j is None or j == i:
            return check
        if j not in persistent_checks:  # the persisting type may have its own goals
            persisting = (persistent_world or {}).get(j, world) if isinstance(persistent_world, dict) \
                else (persistent_world or world)
            persistent_checks[j] = Check(persisting, rule, budget, persistent=j)
        return Mixed(persistent_checks[j]) if q < 1.0 else persistent_checks[j]

    def worst(evaluate):
        out = None
        for n, s in enumerate(states):
            try:
                check.fresh()
                for c in persistent_checks.values():
                    c.fresh()
                r = evaluate(s)
            except RuleLimitExceeded as error:
                return {"gain": None, "error": str(error)}
            if out is None or r["gain"] > out["gain"] + TOLERANCE:
                out = {**r, "at_start": n == 0, "state": s}
        return out

    unilateral = {i: worst(lambda s, i=i: checker(s, i).unilateral(s, i, depth)) for i in ids}
    for i, r in unilateral.items():  # the most profitable departure that newly reaches a declared harm
        if r["gain"] is None:
            continue
        best_harmful = None
        for n, s in enumerate(states):
            h = checker(s, i).fresh().unilateral(s, i, depth)["harmful"]
            if h is not None and (best_harmful is None or h["gain"] > best_harmful["gain"] + TOLERANCE):
                best_harmful = {**h, "at_start": n == 0, "state": s}
        r["harmful"] = best_harmful
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
                    try:
                        for n, s in enumerate(states):
                            e = check.fresh().joint(s, list(coalition), depth, outside)[field]
                            if e is not None and (ext is None or e["gain"] > ext["gain"] + TOLERANCE):
                                ext = {**e, "at_start": n == 0, "state": s}
                    except RuleLimitExceeded as error:
                        ext = {"gain": None, "error": str(error)}
                    r[field] = ext
            if window > 1 and r["gain"] is not None:  # coordinated departures over several rounds
                seq = None
                try:
                    for n, s in enumerate(states):
                        q = check.fresh().sequential(s, list(coalition), depth, window, outside)
                        rank = (q["capture"], q["gain"])
                        if seq is None or rank > (seq["capture"], seq["gain"] + TOLERANCE):
                            seq = {**q, "at_start": n == 0, "state": s}
                except RuleLimitExceeded as error:
                    seq = {"gain": None, "error": str(error)}
                r["sequential"] = seq
            coalitions.append({"coalition": list(coalition), **r})
    gains = [r["gain"] for r in unilateral.values()]
    harmful = [(r.get("harmful") or {}).get("gain") for r in unilateral.values() if r["gain"] is not None]
    return {"holds_unilaterally": None if None in gains else all(g <= TOLERANCE for g in gains),
            # weaker: no single agent gains by a departure that newly reaches a declared harm
            "no_harmful_departure": None if None in gains else all(g is None or g <= TOLERANCE for g in harmful),
            "unilateral": unilateral, "coalitions": coalitions,
            "follow": check.follow(state, depth)[0], "harms_under_rule": sorted(check.follow(state, depth)[1]),
            "depth": depth, "reach": reach, "states_checked": len(states), "precaution": precaution}
