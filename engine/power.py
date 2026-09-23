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
from itertools import combinations, combinations_with_replacement, product
from math import comb, prod

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
        if callable(target):
            self.predicate, self.target = target, None
        else:
            self.predicate = None
            self.target = None if target is None else frozenset([target] if isinstance(target, str) else target)
        self.inside = [i for i in ids if i in coalition]
        self.outside = [i for i in ids if i not in coalition]
        self.groups = world.types()
        self.memo, self.work = {}, 0

    def assignments(self, side, menus):
        """Joint actions of one side, one per multiset within each exchangeable group."""
        parts = []
        for group in self.groups:
            members = [i for i in group if i in side]
            if not members:
                continue
            menu = menus[members[0]]
            if len(members) == 1 or any(key(menus[i]) != key(menu) for i in members):
                parts.append([tuple(zip(members, choice)) for choice in product(*(menus[i] for i in members))])
            else:
                parts.append([tuple(zip(members, (menu[k] for k in idx)))
                              for idx in combinations_with_replacement(range(len(menu)), len(members))])
        order = {i: n for n, i in enumerate(side)}
        return [tuple(a for _, a in sorted((x for part in choice for x in part), key=lambda x: order[x[0]]))
                for choice in product(*parts)]

    def visit(self):
        self.work += 1
        if self.work > self.budget:
            raise PowerLimitExceeded(self.budget)

    def hit(self, state, label):
        """Target reached: a predicate on the (physical) state, or a terminal label."""
        if self.predicate is not None:
            return bool(self.predicate(state))
        return label is not None and (self.target is None or label in self.target)

    def value(self, state, rounds):
        label = self.world.terminal(state)
        if self.hit(state, label):
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
        mine = self.assignments(self.inside, menus)
        theirs = self.assignments(self.outside, menus)

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
    """Max-min probability that `coalition` reaches `target`: terminal label(s), None for any
    terminal, or a predicate on the physical state (for example a declared harm)."""
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


def counts(world, coalition):
    return tuple(sum(i in coalition for i in group) for group in world.types())


def canonical(world, count_vector):
    """The representative coalition for a count vector: the first members of each group."""
    ids = [a.id for a in world.agents]
    chosen = {i for group, c in zip(world.types(), count_vector) for i in group[:c]}
    return [i for i in ids if i in chosen]


def coalitions(world):
    """Every coalition up to declared symmetry, smallest first; singleton groups give all subsets."""
    ranges = [range(len(group) + 1) for group in world.types()]
    vectors = sorted(product(*ranges), key=lambda v: (sum(v), [-c for c in v]))
    return [canonical(world, v) for v in vectors]


def row_for(world, rows, coalition):
    """The row standing for `coalition` (any coalition with the same counts per group)."""
    target = counts(world, coalition)
    return next(r for r in rows if counts(world, r["coalition"]) == target)


def symmetry_violations(world, states, rng, samples=20):
    """Sampled check of `world.types()` (decision 2026-09-23, E2 step 2): members of a
    group share menus, and swapping two members' actions leaves the successor distribution
    over physical keys and harms unchanged. Returns the counterexamples found; none is
    evidence, not proof."""
    def successors(state, joint):
        out = {}
        for p, s in distribution(world.outcomes(state, joint)):
            try:
                harms = sorted(world.harmed(s))
            except NotImplementedError:
                harms = []
            k = key([world.physical(s), harms])
            out[k] = out.get(k, 0.0) + p
        return {k: round(v, 12) for k, v in out.items()}

    found = []
    for state in states:
        if world.terminal(state) is not None:
            continue
        menus = {a.id: world.actions(world.observe(state, a), a) for a in world.agents}
        for group in (g for g in world.types() if len(g) > 1):
            if any(key(menus[i]) != key(menus[group[0]]) for i in group):
                found.append({"group": group, "state": world.physical(state), "menus": {i: menus[i] for i in group}})
                continue
            for _ in range(samples):
                joint = {i: rng.choice(menu) for i, menu in menus.items()}
                x, y = rng.sample(group, 2)
                swapped = {**joint, x: joint[y], y: joint[x]}
                if successors(state, joint) != successors(state, swapped):
                    found.append({"group": group, "state": world.physical(state), "joint": joint, "swapped": [x, y]})
    return found


def power_table(world, state, rounds, target=None, budget=BUDGET):
    """Force and prevent brackets for every coalition up to declared symmetry; `stands_for`
    counts the coalitions a row represents. None marks an unresolved bound."""
    rows = []
    groups = world.types()
    for coalition in coalitions(world):
        values, work = {}, {}
        for order in ORDERS:
            game = Game(world, coalition, target, order, budget)
            try:
                values[order] = game.value(state, rounds)
            except PowerLimitExceeded:
                values[order] = None
            work[order] = game.work
        c = counts(world, coalition)
        rows.append({"coalition": coalition, "force": values, "work": work,
                     "stands_for": prod(comb(len(g), k) for g, k in zip(groups, c))})
    by_counts = {counts(world, r["coalition"]): r for r in rows}
    for row in rows:
        c = counts(world, row["coalition"])
        rest = by_counts[tuple(len(g) - k for g, k in zip(groups, c))]["force"]
        row["prevent"] = {"alpha": None if rest["beta"] is None else 1.0 - rest["beta"],
                          "beta": None if rest["alpha"] is None else 1.0 - rest["alpha"]}
    return rows


def threshold(rows, kind, p=1.0):
    """Smallest coalition size whose guaranteed (alpha) value reaches p.

    `exact` is False when a smaller coalition is unresolved, or, for p < 1, its bracket
    straddles p (randomized play might reach it): the size is then only an upper bound. size None
    means no coalition, including everyone, reaches p within T.
    """
    if kind not in ("force", "prevent", "lock"):
        raise ValueError("kind must be force, prevent or lock")
    # At certainty the bracket cannot straddle: a randomized stage strategy guarantees
    # probability one only if every action in its support does (decision 2026-09-23, E5).
    certain = p >= 1 - TOLERANCE
    exact = True
    for size in sorted({len(r["coalition"]) for r in rows}):
        group = [r for r in rows if len(r["coalition"]) == size]
        witnesses = [r["coalition"] for r in group
                     if r[kind]["alpha"] is not None and r[kind]["alpha"] >= p - TOLERANCE]
        if witnesses:
            return {"kind": kind, "p": p, "size": size, "witnesses": witnesses, "exact": exact}
        exact = exact and all(r[kind]["alpha"] is not None and r[kind]["beta"] is not None
                              and (certain or r[kind]["beta"] < p - TOLERANCE) for r in group)
    return {"kind": kind, "p": p, "size": None, "witnesses": [], "exact": exact}


def profile(world, trace, rounds, target=None, levels=(1.0, 0.5), budget=BUDGET):
    """Power before each played round, beside what was played.

    `trace` is a run record's trace (dicts with actions and resulting state). Each entry
    gives the smallest coalitions that could force or prevent the target within `rounds`
    from the state the round started in. `fragile` marks rounds where one agent (or
    nobody: sealed) could force it with certainty: whatever held, goals held it.
    """
    state, out = world.initial_state(), []
    for entry in trace:
        rows = power_table(world, state, rounds, target, budget)
        marks = [threshold(rows, kind, p) for kind in ("force", "prevent") for p in levels]
        certain = marks[0]
        out.append({"round": entry["round"], "actions": entry["actions"], "thresholds": marks,
                    "sealed": certain["size"] == 0,
                    "fragile": certain["size"] is not None and certain["size"] <= 1,
                    "unresolved": any(v is None for r in rows for v in r["force"].values())})
        state = entry["state"]
    first = lambda flag: next((e["round"] for e in out if e[flag]), None)
    return {"rounds": out, "first_fragile": first("fragile"), "first_sealed": first("sealed"),
            "power_rounds": rounds, "target": target, "levels": list(levels)}


def sure(world, state, coalition, rounds, target=None, goal="avoid", informed=False, budget=BUDGET):
    """Can `coalition` guarantee to avoid (or reach) `target` within `rounds` using only its
    members' pooled observations? Decision record 2026-09-23 (T3.1).

    Knowledge-set construction: the coalition commits one joint action per set of states
    consistent with what it has seen; the complement sees everything, including that
    action; chance is adversarial. `informed=True` gives the coalition the full state.
    Returns True or False; raises PowerLimitExceeded when the work cap is reached.
    """
    if goal not in ("avoid", "reach"):
        raise ValueError("goal must be avoid or reach")
    game = Game(world, coalition, target, "alpha", budget)
    members = [world.by_id[i] for i in game.inside]
    memo = {}

    def seen(s):
        if informed:
            return key(world.physical(s))
        return key([world.observe(s, a) for a in members])

    def groups(states):
        out = {}
        for s in states:
            out.setdefault(seen(s), {})[key(world.physical(s))] = s
        return [list(g.values()) for g in out.values()]

    def win(states, t):
        labels = [world.terminal(s) for s in states]
        hits = [game.hit(s, label) for s, label in zip(states, labels)]
        if goal == "avoid":
            if any(hits):
                return False
            states = [s for s, label in zip(states, labels) if label is None]
            if not states or t == 0:
                return True
        else:
            if any(label is not None and not hit for label, hit in zip(labels, hits)):
                return False
            states = [s for s, label, hit in zip(states, labels, hits) if label is None and not hit]
            if not states:
                return True
            if t == 0:
                return False
        memo_key = (frozenset(key(world.physical(s)) for s in states), t)
        if memo_key in memo:
            return memo[memo_key]

        def menus(s):
            return [world.actions(world.observe(s, a), a) for a in members]
        own_menus = menus(states[0])
        if any(key(menus(s)) != key(own_menus) for s in states[1:]):
            raise ValueError("states the coalition cannot tell apart must offer it the same menus")
        result = False
        for own in product(*own_menus):
            successors = []
            for s in states:
                others = [world.actions(world.observe(s, world.by_id[i]), world.by_id[i]) for i in game.outside]
                for other in product(*others):
                    chosen = {**dict(zip(game.inside, own)), **dict(zip(game.outside, other))}
                    joint = {a.id: chosen[a.id] for a in world.agents}
                    successors += [s2 for _, s2 in distribution(world.outcomes(s, joint), game.visit)]
            if all(win(g, t - 1) for g in groups(successors)):
                result = True
                break
        memo[memo_key] = result
        return result

    return all(win(g, rounds) for g in groups([state]))


def harm_target(world, harm):
    return lambda state: harm in world.harmed(state)


def externalization(world, module, state, rounds, p=1.0, budget=BUDGET):
    """Per declared harm: who can force it, who can impose it from outside, who can prevent
    it, whether those it falls on can prevent it, and who it falls on without any agent.
    For a harm already realized: who can end it within the horizon (correction).

    Goal-free (decision 2026-09-23, E1). `module` supplies HARMS and STAKEHOLDERS.
    """
    members = world.stakeholders()
    declared = set(module.STAKEHOLDERS)
    if set(members) != declared:
        raise ValueError("stakeholders() must cover exactly the declared STAKEHOLDERS")
    ids = [a.id for a in world.agents]
    report = []
    for harm, spec in module.HARMS.items():
        unknown = set(spec["affects"]) - declared
        if unknown:
            raise ValueError(f"harm {harm} affects undeclared stakeholders {sorted(unknown)}")
        affected = sorted({i for name in spec["affects"] for i in members[name]}, key=ids.index)
        rows = power_table(world, state, rounds, harm_target(world, harm), budget)
        free = [sum(i not in affected for i in group) for group in world.types()]
        ids = [a.id for a in world.agents]
        outsiders = []
        for r in rows:  # re-represent each fitting count vector by members outside the affected
            c = counts(world, r["coalition"])
            if all(k <= f for k, f in zip(c, free)):
                chosen = {i for group, k in zip(world.types(), c) for i in [j for j in group if j not in affected][:k]}
                outsiders.append({**r, "coalition": [i for i in ids if i in chosen]})
        own = row_for(world, rows, affected) if affected else None
        realized = harm in world.harmed(state)
        correct = own_correct = keep = veto = None
        if realized:
            ended = power_table(world, state, rounds, lambda s, h=harm: h not in world.harmed(s), budget)
            correct = threshold(ended, "force", p)
            if spec["irreversible"] and correct["size"] is not None:
                raise ValueError(f"harm {harm} is declared irreversible but {correct['witnesses'][0]} can end it")
            keep = threshold(ended, "prevent", p)
            veto = vetoes(world, ended, p)
            own_correct = row_for(world, ended, affected)["force"] if affected else None
        report.append({
            "harm": harm, "irreversible": spec["irreversible"], "affects": spec["affects"],
            "affected_agents": affected,
            "unrepresented": [name for name in spec["affects"] if not members[name]],
            "force": threshold(rows, "force", p),
            "outsiders_force": threshold(outsiders, "force", p) if outsiders else None,
            "prevent": threshold(rows, "prevent", p),
            "affected_prevent": own["prevent"] if own else None,
            "realized_now": realized, "correct": correct, "keep": keep, "veto": veto,
            "affected_correct": own_correct})
    return report


def vetoes(world, rows, p=1.0):
    """Agents without whom no coalition reaches p in a force table: everyone but i cannot.
    None when a needed row is unresolved."""
    everyone = [a.id for a in world.agents]
    out = []
    for i in everyone:
        v = row_for(world, rows, [j for j in everyone if j != i])["force"]["alpha"]
        if v is None:
            return None
        if v < p - TOLERANCE:
            out.append(i)
    return out


def keeps(world, coalition, harm, rounds, budget=BUDGET, level=1.0):
    """Predicate: `harm` (a predicate on state) holds and `coalition` can keep it for `rounds`
    more rounds against everyone else with probability at least `level` (prevent alpha of
    its end; exact at level one, a pure-strategy lower bound below it). Memoized by
    physical state; one inner game per coalition."""
    rest = [a.id for a in world.agents if a.id not in coalition]
    game = Game(world, rest, lambda s: not harm(s), "beta", budget)  # coalition commits first
    cache = {}

    def holds(state):
        if not harm(state):
            return False
        k = key(world.physical(state))
        if k not in cache:
            cache[k] = game.value(state, rounds) <= 1.0 - level + TOLERANCE
        return cache[k]
    return holds


def lock_table(world, state, harm, rounds, keep_rounds, budget=BUDGET, level=1.0):
    """Per coalition (up to declared symmetry): the probability it can force, within
    `rounds`, a state where `harm` holds and it can then keep it for `keep_rounds` against
    everyone else (with probability `level`). Decision 2026-09-23 (E5). For a terminal harm
    this equals force."""
    rows = []
    groups = world.types()
    for coalition in coalitions(world):
        values, work = {}, {}
        for order in ORDERS:
            game = Game(world, coalition, keeps(world, coalition, harm, keep_rounds, budget, level), order, budget)
            try:
                values[order] = game.value(state, rounds)
            except PowerLimitExceeded:
                values[order] = None
            work[order] = game.work
        c = counts(world, coalition)
        rows.append({"coalition": coalition, "lock": values, "work": work,
                     "stands_for": prod(comb(len(g), k) for g, k in zip(groups, c))})
    return rows


def lock_in(world, module, state, rounds, keep_rounds, p=1.0, budget=BUDGET):
    """Per declared harm: smallest coalition that can force it (within `rounds`) and smallest
    that can lock it (force it, then keep it `keep_rounds` against everyone). A harm some
    coalition can lock is irreversible for everyone outside it within `keep_rounds`,
    whatever its declaration."""
    report = []
    for harm, spec in module.HARMS.items():
        target = harm_target(world, harm)
        report.append({"harm": harm, "irreversible": spec["irreversible"],
                       "force": threshold(power_table(world, state, rounds, target, budget), "force", p),
                       "lock": threshold(lock_table(world, state, target, rounds, keep_rounds, budget), "lock", p),
                       "rounds": rounds, "keep_rounds": keep_rounds})
    return report


def joint_prevention(world, module, state, rounds, p=1.0, budget=BUDGET):
    """For each pair of harms, the coalitions that can prevent each one alone but not both
    together: preventing one forces the other on them (a forced choice), plus the smallest
    coalitions for each harm and for both."""
    def table(names):
        target = lambda s, names=names: bool(set(names) & world.harmed(s))
        return power_table(world, state, rounds, target, budget)

    def prevents(row):
        v = row["prevent"]["alpha"]
        return None if v is None else v >= p - TOLERANCE

    harms = list(module.HARMS)
    single = {h: table((h,)) for h in harms}
    report = []
    for i, h1 in enumerate(harms):
        for h2 in harms[i + 1:]:
            both = table((h1, h2))
            forced = [r1["coalition"] for r1, r2, rb in zip(single[h1], single[h2], both)
                      if prevents(r1) and prevents(r2) and prevents(rb) is False]
            report.append({"harms": [h1, h2], "forced_choice": forced,
                           "prevent_each": [threshold(single[h1], "prevent", p), threshold(single[h2], "prevent", p)],
                           "prevent_both": threshold(both, "prevent", p)})
    return report
