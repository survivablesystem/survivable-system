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
