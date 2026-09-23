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
        # everyone else plays what the continuation says now: the rule, or a persisting
        # type's own best response (the same play the follow value assumes)
        plays = [(w * p, c.play(s, {**c.policy(s, depth), agent_id: action}, depth))
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
    return [s for s, _ in checked_paths(world, rule, state, reach, budget)]


def checked_paths(world, rule, state, reach, budget=BUDGET, distinct=False):
    """checked_states with the path that reached each: a tuple of (state, joint, successor)
    steps. With `distinct`, the same state reached by two paths is kept twice (what others
    have seen can differ, and with it what they believe)."""
    check = Check(world, rule, budget)
    ident = (lambda s, path: (key(s), key([j for _, j, _ in path]))) if distinct else (lambda s, path: key(s))
    frontier, seen = [(state, ())], {ident(state, ()): (state, ())}
    for _ in range(reach):
        nxt = []
        for s, path in frontier:
            if world.terminal(s) is not None:
                continue
            base = check.prescribed(s)
            joints = [base] + [{**base, a.id: action} for a in world.agents
                               for action in world.actions(world.observe(s, a), a)
                               if key(action) != key(base[a.id])]
            for joint in joints:
                for _, s2 in distribution(world.outcomes(s, joint), check.visit):
                    path2 = path + ((s, joint, s2),)
                    if ident(s2, path2) not in seen and world.terminal(s2) is None:
                        seen[ident(s2, path2)] = (s2, path2)
                        nxt.append((s2, path2))
        frontier = nxt
    return list(seen.values())


class Mixture:
    """An agent checked against a mixture of continuations, [(weight, Check)]: another
    agent's hidden types with the checked agent's posterior over them (E12)."""
    def __init__(self, parts, posterior=None):
        self.parts, self.posterior = [(w, c) for w, c in parts if w > 0], posterior

    def fresh(self):
        for _, c in self.parts:
            c.fresh()
        return self

    def unilateral(self, state, agent_id, depth):
        r = unilateral_over(self.parts, state, agent_id, depth)
        return {**r, "posterior": self.posterior} if self.posterior is not None else r


class Hidden:
    """One agent whose type the others do not know (decision 2026-09-23, E12).

    `types`: {name: (prior, world or None)}. A world differs from the declared one only in
    the hidden agent's goals; that type best-responds for itself while everyone else follows
    the rule. None is a committed type: it always plays the rule. Observer i's posterior at a
    checked state is the prior times, for each step of the path, the probability of what i
    observes of the successor, mixing over the hidden agent's actions by each type's choice
    rule: logit with `precision` over its own action values, best response (uniform over
    ties) at infinity. At infinity a sight no type's best response produces goes, as the
    logit limit, to the types that lose least by producing it. A sight only committed types
    could not produce is read as an error after which the rule resumes (the one-shot
    convention): beliefs stay at the prior. Precision 0: no updating."""

    def __init__(self, world, rule, agent, types, precision=math.inf, budget=BUDGET):
        if not types or any(p < 0 for p, _ in types.values()) or abs(math.fsum(p for p, _ in types.values()) - 1) > 1e-9:
            raise ValueError("hidden types need priors that are probabilities summing to one")
        if not precision >= 0:
            raise ValueError("precision is nonnegative (math.inf: best response)")
        ids = [a.id for a in world.agents]
        for name, (_, w) in types.items():
            if w is not None and [a.id for a in w.agents] != ids:
                raise ValueError(f"type {name!r} must have the declared world's agents")
        self.world, self.rule, self.agent, self.precision = world, rule, agent, precision
        self.prior = {name: p for name, (p, _) in types.items()}
        self.committed = {name for name, (_, w) in types.items() if w is None}
        # continuation others face: each type acting on its own goals (committed: the rule)
        self.continuation = {name: Check(world, rule, budget) if w is None else Check(w, rule, budget, persistent=agent)
                             for name, (_, w) in types.items()}
        # each strategic type's own one-shot check: depart once, then follow
        self.own = {name: Check(w, rule, budget) for name, (_, w) in types.items() if w is not None}
        self.choices, self.sights = {}, {}

    def fresh(self):
        for c in (*self.continuation.values(), *self.own.values()):
            c.fresh()
        return self

    def losses(self, name, s0, joint, depth):
        """[(action, loss)] for the hidden agent at s0, others playing `joint`: how much less
        than its best the type gets by each action (committed: 0 for the rule, else inf)."""
        memo_key = (name, key(s0), key({i: a for i, a in joint.items() if i != self.agent}), depth)
        if memo_key not in self.choices:
            check = self.continuation[name]
            agent = check.world.by_id[self.agent]
            menu = check.world.actions(check.world.observe(s0, agent), agent)
            if name in self.committed:
                rule_action = check.prescribed(s0)[self.agent]
                out = [(b, 0.0 if key(b) == key(rule_action) else math.inf) for b in menu]
            else:
                values = [check.play(s0, {**joint, self.agent: b}, depth)[0][self.agent] for b in menu]
                top = max(values)
                out = [(b, 0.0 if top - v <= TOLERANCE else top - v) for b, v in zip(menu, values)]
            self.choices[memo_key] = out
        return self.choices[memo_key]

    def sight(self, s0, joint, s1, observer, menu):
        """Per hidden action b: the probability that the observer sees what it saw of s1."""
        world, agent = self.world, self.world.by_id[observer]
        seen = key(world.observe(s1, agent))
        memo_key = (key(s0), key(joint), seen, observer)
        if memo_key not in self.sights:
            check = self.continuation[next(iter(self.continuation))]
            self.sights[memo_key] = [math.fsum(p for p, s in distribution(world.outcomes(s0, {**joint, self.agent: b}), check.visit)
                                               if key(world.observe(s, agent)) == seen) for b in menu]
        return self.sights[memo_key]

    def posterior(self, path, observer, depth):
        """{type: probability} for `observer` after the steps of `path`."""
        if self.precision == 0 or observer == self.agent:
            return dict(self.prior)
        names = list(self.prior)
        total = {n: 0.0 for n in names}   # summed leading-order loss (infinite precision)
        weight = {n: self.prior[n] for n in names}
        for s0, joint, s1 in path:
            for n in names:
                if weight[n] == 0.0:
                    continue
                losses = self.losses(n, s0, joint, depth)
                see = self.sight(s0, joint, s1, observer, [b for b, _ in losses])
                if math.isinf(self.precision):
                    visible = [(l, p) for (_, l), p in zip(losses, see) if p > 0]
                    m = min((l for l, _ in visible), default=math.inf)
                    if math.isinf(m):
                        weight[n] = 0.0
                        continue
                    best = sum(1 for _, l in losses if l == 0.0)
                    total[n] += m
                    weight[n] *= math.fsum(p for l, p in visible if abs(l - m) <= TOLERANCE) / best
                else:
                    z = math.fsum(math.exp(-self.precision * l) for _, l in losses)
                    weight[n] *= math.fsum(p * math.exp(-self.precision * l) / z for (_, l), p in zip(losses, see))
        live = [n for n in names if weight[n] > 0]
        if math.isinf(self.precision) and live:
            m = min(total[n] for n in live)
            live = [n for n in live if total[n] <= m + TOLERANCE * (1 + len(path))]
        mass = math.fsum(weight[n] for n in live)
        if mass <= 0:  # only committed types, and one departed: an error, after which the rule resumes
            return dict(self.prior)
        return {n: (weight[n] / mass if n in live else 0.0) for n in names}

    def facing(self, path, observer, depth):
        """The mixture of continuations `observer` is checked against."""
        post = self.posterior(path, observer, depth)
        return Mixture([(post[n], self.continuation[n]) for n in post], post)


def enforcement(world, module, rule, state, depth, reach=1, max_size=2, budget=BUDGET, window=1,
                types=None, precision=math.inf):
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
    that needs the coalition and lands a harm outside it (capture).

    `types` = {h: {name: (prior, world or None)}}: h's type is hidden (decision 2026-09-23,
    E12; see `Hidden`). Every other agent is checked, at each checked state, against h's
    types acting on their own goals, weighted by its posterior from what it observed on the
    path there (`precision`: the types' choice rule; 0 is no updating); the witness carries
    that posterior. h is checked once per strategic type (`by_type`; the reported gain is the
    largest). Coalition checks use the declared world. None marks a check stopped by the
    work cap: unresolved.
    """
    check = Check(world, rule, budget)
    hidden = None
    if types:
        if len(types) != 1:
            raise ValueError("one agent with hidden types per check")
        (h, declared), = types.items()
        hidden = Hidden(world, rule, h, declared, precision, budget)
    tagged = checked_paths(world, rule, state, reach, budget, distinct=hidden is not None)
    states = [s for s, _ in tagged]
    members = world.stakeholders()
    ids = [a.id for a in world.agents]

    def checker(n, i):
        if hidden is None or i == hidden.agent:
            return check
        return hidden.facing(tagged[n][1], i, depth)

    def worst(evaluate):
        out = None
        for n, s in enumerate(states):
            try:
                check.fresh()
                if hidden is not None:
                    hidden.fresh()
                r = evaluate(n, s)
            except RuleLimitExceeded as error:
                return {"gain": None, "error": str(error)}
            if out is None or r["gain"] > out["gain"] + TOLERANCE:
                out = {**r, "at_start": n == 0, "state": s}
        return out

    def add_harmful(r, i, of):
        """The most profitable departure by i that newly reaches a declared harm."""
        best_harmful = None
        for n, s in enumerate(states):
            h = of(n).fresh().unilateral(s, i, depth)["harmful"]
            if h is not None and (best_harmful is None or h["gain"] > best_harmful["gain"] + TOLERANCE):
                best_harmful = {**h, "at_start": n == 0, "state": s}
        r["harmful"] = best_harmful

    unilateral = {}
    for i in ids:
        if hidden is not None and i == hidden.agent:
            by_type = {}
            for name, own in hidden.own.items():
                r = worst(lambda n, s, own=own: own.unilateral(s, i, depth))
                if r["gain"] is not None:
                    add_harmful(r, i, lambda n, own=own: own)
                by_type[name] = r
            gains = [r["gain"] for r in by_type.values()]
            if None in gains:
                unilateral[i] = {**next(r for r in by_type.values() if r["gain"] is None), "by_type": by_type}
            elif not by_type:  # only committed types: nothing to check
                unilateral[i] = {"gain": 0.0, "action": None, "harmful": None, "by_type": {}}
            else:
                name = max(by_type, key=lambda x: by_type[x]["gain"])
                unilateral[i] = {**by_type[name], "type": name, "by_type": by_type}
            continue
        r = worst(lambda n, s, i=i: checker(n, i).unilateral(s, i, depth))
        if r["gain"] is not None:
            add_harmful(r, i, lambda n, i=i: checker(n, i))
        unilateral[i] = r
    coalitions = []
    for size in range(2, max_size + 1):
        for coalition in combinations(ids, size):
            c = set(coalition)
            outside = lambda harms, c=c: {h: [n for n in module.HARMS[h]["affects"] if not set(members[n]) & c]
                                          for h in harms}
            r = worst(lambda n, s, c=coalition, o=outside: check.joint(s, list(c), depth, o))
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
            "depth": depth, "reach": reach, "states_checked": len(states),
            "types": None if hidden is None else {hidden.agent: dict(hidden.prior)},
            "precision": None if hidden is None or math.isinf(precision) else precision}
