"""E2: symmetry-reduced power equals full enumeration where both run."""
import random
from itertools import permutations

import pytest

from engine.core import World, key
from engine.power import externalization, power_table
from worlds import commons


class Unreduced:
    """A view of a world that claims no symmetry."""
    def __init__(self, world):
        self.world = world

    def __getattr__(self, name):
        return getattr(self.world, name)

    def types(self):
        return World.types(self.world)


def expand(world, rows):
    """Reduced rows mapped to every coalition they stand for, keyed by counts."""
    from engine.power import counts
    return {counts(world, r["coalition"]): (r["force"], r["prevent"]) for r in rows}


@pytest.mark.parametrize("overrides", [{"confiscation_to": "stock"}, {"confiscation_to": "sanctioners"},
                                       {"restraint": False, "confiscation_to": "stock"}, {"sanction": False}])
@pytest.mark.parametrize("S", [8.0, 20.0, 30.0])
def test_reduced_power_equals_full_enumeration(overrides, S):
    world = commons.make({**commons.DEFAULTS, "n": 3, **overrides}, random.Random(0))
    state = {**world.initial_state(), "S": S}
    reduced = power_table(world, state, 2, "collapsed")
    full = power_table(Unreduced(world), state, 2, "collapsed")
    assert len(reduced) == 4 and len(full) == 8
    assert sum(r["stands_for"] for r in reduced) == 8
    for row in full:
        k = len(row["coalition"])
        match = next(r for r in reduced if len(r["coalition"]) == k)
        assert row["force"] == pytest.approx(match["force"]) and row["prevent"] == pytest.approx(match["prevent"])
    assert sum(r["work"]["alpha"] for r in reduced) < sum(r["work"]["alpha"] for r in full)


def test_commons_kernel_is_invariant_under_permuting_users_actions():
    world = commons.make({**commons.DEFAULTS, "n": 3, "confiscation_to": "stock"}, random.Random(0))
    rng = random.Random(1)
    menu = world.actions(world.observe(world.initial_state(), world.agents[0]), world.agents[0])
    ids = [a.id for a in world.agents]
    for S in (10.0, 30.0):
        state = {**world.initial_state(), "S": S}
        for _ in range(20):
            acts = [rng.choice(menu) for _ in ids]
            reference = None
            for perm in permutations(acts):
                dist = {}
                for p, s in world.outcomes(state, dict(zip(ids, perm))):
                    k = key(world.physical(s))
                    dist[k] = dist.get(k, 0.0) + p
                dist = {k: round(v, 12) for k, v in dist.items()}
                reference = reference or dist
                assert dist == reference


def test_externalization_outsider_witnesses_exclude_the_affected():
    world = commons.make({**commons.DEFAULTS, "n": 3}, random.Random(0))
    for row in externalization(world, commons, {**world.initial_state(), "S": 30.0}, 2):
        affected = set(row["affected_agents"])
        for w in row["outsiders_force"]["witnesses"]:
            assert not set(w) & affected


# E2 step 2: symmetry inside composites, and the generic check.

from engine.compose import Composite
from engine.power import symmetry_violations
from worlds import race_commons as rc, treaty


def commons_whole(couple=None, couple_reads=None):
    params = {**commons.DEFAULTS, "n": 3, "sanction": False}
    part = commons.make(params, random.Random(0))
    planning = {k: params[k] for k in ("horizon", "search_depth", "discount", "k", "others")}
    return Composite(params, random.Random(0), {"commons": part}, {"commons": {"u0": "x", "u1": "y", "u2": "z"}},
                     couple=couple, planning=planning, couple_reads=couple_reads,
                     stakeholders={name: [("commons", name)] for name in commons.STAKEHOLDERS})


def test_composite_derives_groups_from_parts_and_a_coupling_claims_none_unless_declared():
    assert commons_whole().types() == [["x", "y", "z"]]
    nudge = lambda state, joint: state  # any coupling that is not the identity
    assert commons_whole(nudge).types() == [["x"], ["y"], ["z"]]
    assert commons_whole(nudge, couple_reads=("x",)).types() == [["x"], ["y", "z"]]
    whole = rc.make({**rc.DEFAULTS, "fishers": 3}, random.Random(0))
    assert whole.types() == [["east"], ["west"], ["fisher", "fisher2", "fisher3"]]
    assert rc.make(dict(rc.DEFAULTS), random.Random(0)).types() == [["east"], ["west"], ["fisher"]]


@pytest.mark.parametrize("draw", [0.0, 2.0])
def test_fishers_are_exchangeable_in_the_whole(draw):
    whole = rc.make({**rc.DEFAULTS, "fishers": 3, "draw": draw, "commons.sanction": True}, random.Random(0))
    states = [at_stock(whole, S) for S in (8.0, 20.0, 30.0)]
    assert symmetry_violations(whole, states, random.Random(2), samples=30) == []


def test_the_check_catches_a_false_declaration():
    class Paired:
        def __init__(self, world):
            self.world = world

        def __getattr__(self, name):
            return getattr(self.world, name)

        def types(self):
            return [["a", "b"]]

    params = {**treaty.DEFAULTS, "lead": 1, "advantage": 2.0}
    world = Paired(treaty.make(params, random.Random(0)))
    assert symmetry_violations(world, [world.initial_state()], random.Random(0), samples=30)


@pytest.mark.parametrize("S", [20.0, 30.0])
def test_reduced_whole_equals_full_enumeration(S):
    whole = rc.make({**rc.DEFAULTS, "fishers": 2, "draw": 2.0}, random.Random(0))
    target = lambda s: "commons: depleted" in whole.harmed(s)
    reduced = power_table(whole, at_stock(whole, S), 2, target)
    full = power_table(Unreduced(whole), at_stock(whole, S), 2, target)
    assert len(reduced) == 12 and len(full) == 16 and sum(r["stands_for"] for r in reduced) == 16
    for row in full:
        match = next(r for r in reduced if len(r["coalition"]) == len(row["coalition"])
                     and {"east", "west"} & set(r["coalition"]) == {"east", "west"} & set(row["coalition"]))
        assert row["force"] == pytest.approx(match["force"]) and row["prevent"] == pytest.approx(match["prevent"])


def test_a_build_draws_the_same_stock_however_many_fish():
    removed = []
    for fishers in (1, 4):
        whole = rc.make({**rc.DEFAULTS, "fishers": fishers, "draw": 2.0}, random.Random(0))
        rest = {a.id: {"commons": ("rest", False)} for a in whole.agents}
        state = at_stock(whole, 30.0)
        quiet = [s for _, s in whole.outcomes(state, {**rest, "east": {**rest["east"], "treaty": "hold"},
                                                      "west": {**rest["west"], "treaty": "hold"}})]
        built = [s for _, s in whole.outcomes(state, {**rest, "east": {**rest["east"], "treaty": "build"},
                                                      "west": {**rest["west"], "treaty": "hold"}})]
        removed.append(quiet[0]["parts"]["commons"]["S"] - built[0]["parts"]["commons"]["S"])
    assert removed[0] == pytest.approx(removed[1]) and removed[0] > 0


def at_stock(world, S):
    state = world.initial_state()
    state["parts"]["commons"] = {**state["parts"]["commons"], "S": S}
    return state


def test_one_more_fisher_strips_a_racer_of_unilateral_force_and_protection():
    """Race-commons findings 5 and 6 (evidence/fishers.json): S=30, draw 2, T=2."""
    from engine.power import force
    values = {}
    for fishers in (1, 2):
        whole = rc.make({**rc.DEFAULTS, "fishers": fishers, "draw": 2.0}, random.Random(0))
        state = at_stock(whole, 30.0)
        depleted = lambda s, w=whole: "commons: depleted" in w.harmed(s)
        collapse = lambda s, w=whole: "commons: collapse" in w.harmed(s)
        others = [a.id for a in whole.agents if a.id != "east"]
        values[fishers] = (force(whole, state, ["east"], 2, depleted),
                           1.0 - force(whole, state, others, 2, collapse, order="beta"))
    assert values == {1: (1.0, 1.0), 2: (0.0, 0.0)}
