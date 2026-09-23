"""Exact leaf reduction, with full physical enumeration as the reference."""
from dataclasses import replace
from itertools import product
import math
import random
from types import MethodType

import pytest

from engine.core import Search, SearchLimitExceeded, World, action_values, best, distribution
from tests.planner_cases import ThresholdRisk
from tests.test_search import FutureBit
from worlds import commons


def full_kernel(world):
    world.reward_outcomes = MethodType(World.reward_outcomes, world)
    world.planning_outcomes = MethodType(World.planning_outcomes, world)
    world.continuation = MethodType(World.continuation, world)
    return world


@pytest.mark.parametrize("destination", ["stock", "sanctioners"])
@pytest.mark.parametrize("stock", [0.0, 5.0, 10.0, 50.0])
def test_exact_marginal_matches_every_three_user_joint(destination, stock):
    world = commons.make({**commons.DEFAULTS, "n": 3, "confiscation_to": destination}, random.Random(0))
    state = {**world.initial_state(), "S": stock, "collapsed": stock == 0}
    menus = [world.actions(world.observe(state, a), a) for a in world.agents]
    for actions in product(*menus):
        joint = dict(zip(world.by_id, actions))
        physical = distribution(world.outcomes(state, joint))
        marginal = distribution(world.reward_outcomes(state, joint))
        for agent in world.agents:
            exact = math.fsum(p * world.value(s, agent) for p, s in physical)
            reduced = math.fsum(p * rewards[agent.id] for p, rewards in marginal)
            assert reduced == pytest.approx(exact, abs=1e-12)


@pytest.mark.parametrize("destination", ["stock", "sanctioners"])
@pytest.mark.parametrize("depth", [1, 2, 3])
def test_asymmetric_contested_values_and_choices_match_full_kernel(destination, depth):
    params = {**commons.DEFAULTS, "n": 3, "search_depth": depth,
              "confiscation_to": destination, "sanction_cost": 0.3}
    world = commons.make(params, random.Random(7))
    reference = full_kernel(commons.make(params, random.Random(7)))
    joint = {"u0": ("lo", True), "u1": ("hi", False), "u2": ("hi", True)}
    state = world.step(world.initial_state(), joint, world.rng)
    for actor in world.agents:
        values = action_values(world, state, actor)
        expected = action_values(reference, state, actor)
        assert dict(values) == pytest.approx(dict(expected), abs=1e-12)
        assert best(values)[0] == best(expected)[0]


@pytest.mark.parametrize("probability", [0.1, 0.5, 0.9])
def test_reduced_hidden_future_reward_retains_information_sets(probability):
    class MarginalBit(FutureBit):
        def reward_outcomes(self, state, joint):
            # Only t=1 has no continuation. Terminal t=2 never enters a kernel.
            assert state["t"] == 1
            yield 1.0, {"a": int(joint["a"] == state["secret"])}

    world = MarginalBit(probability)
    # FutureBit's depth 3 reaches t=1 at depth 2; use 2 to exercise leaf reduction.
    world.agents = [replace(world.agents[0], horizon=2)]
    world.by_id = {a.id: a for a in world.agents}
    actual = dict(action_values(world, world.initial_state(), world.agents[0]))
    assert actual == pytest.approx({"wait": max(probability, 1 - probability), "reveal": 0.9})
    for secret in (0, 1):
        state = {**world.initial_state(), "t": 1, "secret": secret}
        actor = replace(world.agents[0], horizon=1)
        assert dict(action_values(world, state, actor)) == pytest.approx({0: 1 - probability, 1: probability})


def test_default_marginal_integrates_nonlinear_branch_loss():
    world = ThresholdRisk()
    assert dict(action_values(world, world.initial_state(), world.agents[0])) == {"safe": 1, "risky": -4}


@pytest.mark.parametrize("entries, error", [
    ([(0.2, {"a": 0})], ValueError),
    ([(1.0, {"a": float("nan")})], ValueError),
    ([(0.0, {"a": 0})] * 4 + [(1.0, {"a": 0})], SearchLimitExceeded),
])
def test_reward_marginals_are_validated_and_charge_zero_entries(entries, error):
    world = FutureBit()
    actor = replace(world.agents[0], horizon=1, node_budget=4)
    world.reward_outcomes = lambda state, joint: iter(entries)
    with pytest.raises(error):
        action_values(world, world.initial_state(), actor)


def test_eight_user_contested_decision_extends_coverage_at_same_cap():
    params = {**commons.DEFAULTS, "n": 8}
    world = commons.make(params, random.Random(0))
    state = world.step(world.initial_state(), {a.id: ("hi", False) for a in world.agents}, world.rng)
    actor = world.agents[0]
    search = Search(world, actor)
    observation, support = search.initial(state, actor)
    values = search.values(support, observation, actor, actor.depth, actor.k, False)
    assert best(values)[0] == ("lo", True)
    assert search.nodes < actor.node_budget
    with pytest.raises(SearchLimitExceeded):
        action_values(full_kernel(world), state, actor)
