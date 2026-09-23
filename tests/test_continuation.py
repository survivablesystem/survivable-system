"""E2 step 3: exact reward integration inside the tree, by declared continuation."""
import random
from dataclasses import replace

import pytest

from engine.core import World, action_values, continuation_violations, run
from worlds import commons, race_commons as rc


class Unreduced:
    """A view of a world that declares no continuation and integrates nothing inside the tree."""
    def __init__(self, world):
        self.world = world

    def __getattr__(self, name):
        return getattr(self.world, name)

    def continuation(self, state):
        return state

    def planning_outcomes(self, state, joint, visit=lambda: None):
        return World.planning_outcomes(self, state, joint, visit)

    def reward_outcomes(self, state, joint):
        return World.reward_outcomes(self, state, joint)


def states_of(world, rounds=6, seed=0):
    """States along a run, plus the initial one."""
    _, _, trace = run(world, rounds, random.Random(seed))
    return [world.initial_state()] + [s for _, s in trace]


@pytest.mark.parametrize("destination", ["sanctioners", "stock"])
@pytest.mark.parametrize("prior", ["lo", "hi", "ready"])
def test_commons_declarations_hold(destination, prior):
    world = commons.make({**commons.DEFAULTS, "n": 4, "confiscation_to": destination, "prior": prior,
                          "horizon": 3, "search_depth": 2}, random.Random(0))
    states = states_of(world) + [{**world.initial_state(), "S": S} for S in (6.0, 12.0)]
    assert continuation_violations(world, states, random.Random(1), samples=8) == []


@pytest.mark.parametrize("destination", ["sanctioners", "stock"])
@pytest.mark.parametrize("n, others", [(3, "react"), (4, "react"), (3, "plan")])
def test_planner_values_equal_full_enumeration(destination, n, others):
    world = commons.make({**commons.DEFAULTS, "n": n, "confiscation_to": destination, "others": others},
                         random.Random(0))
    full = Unreduced(world)
    for state in states_of(world, 4):
        for agent in world.agents:
            actor = replace(agent, node_budget=10**7)
            reduced, unreduced = action_values(world, state, actor), action_values(full, state, actor)
            assert [a for a, _ in reduced] == [a for a, _ in unreduced]
            assert [v for _, v in reduced] == pytest.approx([v for _, v in unreduced], abs=1e-9)


def test_commons_traces_are_unchanged():
    for destination in ("sanctioners", "stock"):
        params = {**commons.DEFAULTS, "n": 4, "confiscation_to": destination}
        label, _, trace = run(commons.make(params, random.Random(0)), 30, random.Random(3))
        full = Unreduced(commons.make(params, random.Random(0)))
        full_label, _, full_trace = run(full, 30, random.Random(3))
        assert label == full_label and [j for j, _ in trace] == [j for j, _ in full_trace]


def test_one_class_when_confiscations_go_to_sanctioners():
    world = commons.make({**commons.DEFAULTS, "n": 8}, random.Random(0))
    joint = {a.id: (commons.LO, True) if i < 2 else (commons.HI, False) for i, a in enumerate(world.agents)}
    assert len(list(world.outcomes(world.initial_state(), joint))) == 2 ** 6
    assert len(list(world.planning_outcomes(world.initial_state(), joint))) == 1


@pytest.mark.parametrize("fishers", [1, 2])
def test_composite_declarations_hold(fishers):
    whole = rc.make({**rc.DEFAULTS, "fishers": fishers, "draw": 1.0, "commons.sanction": True, "horizon": 3},
                    random.Random(0))
    assert continuation_violations(whole, states_of(whole, 3), random.Random(2), samples=4) == []


def test_the_check_catches_a_false_continuation():
    class Forgetful:
        """Claims the stock does not matter."""
        def __init__(self, world):
            self.world = world

        def __getattr__(self, name):
            return getattr(self.world, name)

        def continuation(self, state):
            return {"collapsed": state["collapsed"], "last": state["last"]}

        def planning_outcomes(self, state, joint, visit=lambda: None):
            return World.planning_outcomes(self, state, joint, visit)

    world = Forgetful(commons.make({**commons.DEFAULTS, "n": 3, "confiscation_to": "stock", "horizon": 3},
                                   random.Random(0)))
    joint_states = [{**world.initial_state(), "S": 12.0}]
    assert continuation_violations(world, joint_states, random.Random(0), samples=10)


def test_composite_planner_values_equal_full_enumeration():
    whole = rc.make({**rc.DEFAULTS, "fishers": 2, "draw": 1.0, "commons.sanction": True}, random.Random(0))
    full = Unreduced(whole)
    for state in states_of(whole, 3):
        for agent in whole.agents:
            actor = replace(agent, node_budget=10**7)
            reduced, unreduced = action_values(whole, state, actor), action_values(full, state, actor)
            assert [a for a, _ in reduced] == [a for a, _ in unreduced]
            assert [v for _, v in reduced] == pytest.approx([v for _, v in unreduced], abs=1e-9)
