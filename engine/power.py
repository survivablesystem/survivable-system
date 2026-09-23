"""Goal-free coalition power over a world's own kernel. See DECISIONS.md 2026-09-23.

force: the probability a coalition can make the world enter a target terminal label
within T rounds, against the complement acting as one coordinated minimizer. Both
sides see the full state; menus still come from each agent's observation. Chance
follows `outcomes`. Goals, horizons, discounts and beliefs are never read.

Stage order brackets the value. Alpha: the coalition commits each round first, so the
value is what it can guarantee. Beta: the complement commits first, an upper bound.
Randomized stage strategies lie between; equal brackets are exact. Prevention is the
dual, prevent_alpha(C) = 1 - force_beta(complement). No claim extends beyond T.
"""
from __future__ import annotations
from itertools import combinations, product

from .core import distribution, key

ORDERS = ("alpha", "beta")
BUDGET = 2_000_000  # emitted kernel entries per (coalition, order) query
TOLERANCE = 1e-12


class PowerLimitExceeded(RuntimeError):
    def __init__(self, budget):
        self.budget = budget
        super().__init__(f"power query exceeded {budget} kernel entries; unresolved")


class Game:
    def __init__(self, world, coalition, target, order, budget):
        ids = [a.id for a in world.agents]
        unknown = set(coalition) - set(ids)
        if unknown:
            raise ValueError(f"unknown agents: {sorted(unknown)}")
        if order not in ORDERS:
            raise ValueError(f"order must be one of {ORDERS}")
        self.world, self.order, self.budget = world, order, budget
        self.target = None if target is None else frozenset([target] if isinstance(target, str) else target)
        self.inside = [i for i in ids if i in coalition]
        self.outside = [i for i in ids if i not in coalition]
        self.memo, self.work = {}, 0

    def visit(self):
        self.work += 1
        if self.work > self.budget:
            raise PowerLimitExceeded(self.budget)

    def hit(self, label):
        return label is not None and (self.target is None or label in self.target)

    def value(self, state, rounds):
        label = self.world.terminal(state)
        if self.hit(label):
            return 1.0
        if rounds == 0 or label is not None:
            return 0.0
        memo_key = (key(self.world.physical(state)), rounds)
        if memo_key not in self.memo:
            self.memo[memo_key] = self.stage(state, rounds)
        return self.memo[memo_key]

    def stage(self, state, rounds):
        return self.choose(state, rounds)[0]

    def choose(self, state, rounds):
        """Stage value, the first mover's choice and the second mover's reply to it."""
        world = self.world
        menus = {a.id: world.actions(world.observe(state, a), a) for a in world.agents}
        mine = list(product(*(menus[i] for i in self.inside)))
        theirs = list(product(*(menus[i] for i in self.outside)))

        def q(own, other):
            chosen = {**dict(zip(self.inside, own)), **dict(zip(self.outside, other))}
            joint = {a.id: chosen[a.id] for a in world.agents}
            return sum(p * self.value(s, rounds - 1)
                       for p, s in distribution(world.outcomes(state, joint), self.visit))

        # Pruning is local to this node, so every stored value is exact. A candidate
        # that becomes the incumbent was never pruned, so its reply is a true optimum.
        first, second = (mine, theirs) if self.order == "alpha" else (theirs, mine)
        sign = 1 if self.order == "alpha" else -1  # alpha maximizes the inner minimum
        best, choice, reply = None, None, None
        for lead in first:
            inner, answer = None, None
            for follow in second:
                v = q(lead, follow) if self.order == "alpha" else q(follow, lead)
                if inner is None or sign * v < sign * inner:
                    inner, answer = v, follow
                if best is not None and sign * inner <= sign * best:
                    break
            if best is None or sign * inner > sign * best:
                best, choice, reply = inner, lead, answer
            if (self.order == "alpha" and best >= 1.0) or (self.order == "beta" and best <= 0.0):
                break
        return best, choice, reply


def force(world, state, coalition, rounds, target=None, order="alpha", budget=BUDGET):
    """Max-min probability that `coalition` enters `target` (label or labels; None: any terminal)."""
    if type(rounds) is not int or rounds < 0:
        raise ValueError("rounds must be a nonnegative integer")
    return Game(world, coalition, target, order, budget).value(state, rounds)


def witness(world, state, coalition, rounds, target=None, budget=BUDGET):
    """Guaranteed value, the coalition's first-round actions and the adversary's best reply.

    Later rounds adapt to the realized state; only the first stage is returned.
    """
    game = Game(world, coalition, target, "alpha", budget)
    label = world.terminal(state)
    if rounds == 0 or label is not None:
        return {"value": game.value(state, rounds), "actions": None, "reply": None}
    value, own, other = game.choose(state, rounds)
    return {"value": value, "actions": dict(zip(game.inside, own)),
            "reply": dict(zip(game.outside, other))}


def coalitions(world):
    ids = [a.id for a in world.agents]
    return [list(c) for size in range(len(ids) + 1) for c in combinations(ids, size)]


def power_table(world, state, rounds, target=None, budget=BUDGET):
    """Force and prevent brackets for every coalition. None marks an unresolved bound."""
    rows = []
    for coalition in coalitions(world):
        values, work = {}, {}
        for order in ORDERS:
            game = Game(world, coalition, target, order, budget)
            try:
                values[order] = game.value(state, rounds)
            except PowerLimitExceeded:
                values[order] = None
            work[order] = game.work
        rows.append({"coalition": coalition, "force": values, "work": work})
    ids = [a.id for a in world.agents]
    by_members = {frozenset(r["coalition"]): r for r in rows}
    for row in rows:
        rest = by_members[frozenset(ids) - frozenset(row["coalition"])]["force"]
        row["prevent"] = {"alpha": None if rest["beta"] is None else 1.0 - rest["beta"],
                          "beta": None if rest["alpha"] is None else 1.0 - rest["alpha"]}
    return rows


def threshold(rows, kind, p=1.0):
    """Smallest coalition size whose guaranteed (alpha) value reaches p.

    `exact` is False when a smaller coalition is unresolved, or its bracket straddles p
    (randomized play might reach it): the size is then only an upper bound. size None
    means no coalition, including everyone, reaches p within T.
    """
    if kind not in ("force", "prevent"):
        raise ValueError("kind must be force or prevent")
    exact = True
    for size in sorted({len(r["coalition"]) for r in rows}):
        group = [r for r in rows if len(r["coalition"]) == size]
        witnesses = [r["coalition"] for r in group
                     if r[kind]["alpha"] is not None and r[kind]["alpha"] >= p - TOLERANCE]
        if witnesses:
            return {"kind": kind, "p": p, "size": size, "witnesses": witnesses, "exact": exact}
        exact = exact and all(r[kind]["alpha"] is not None and r[kind]["beta"] is not None
                              and r[kind]["beta"] < p - TOLERANCE for r in group)
    return {"kind": kind, "p": p, "size": None, "witnesses": [], "exact": exact}
