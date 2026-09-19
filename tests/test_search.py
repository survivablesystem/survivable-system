"""Independent references for finite belief trees, kernel execution and work limits."""
from dataclasses import replace
import random

import pytest

from engine.core import Agent, SearchLimitExceeded, action_values, distribution, plan, run
from engine.records import run_record
from engine.sweep import shares
from tests.planner_cases import DiagnosticWorld, Investment, ThresholdRisk
from tests.test_engine import TwoAction


class FutureBit(DiagnosticWorld):
    # A fair/biased bit is generated after an action; revealing costs 1/10 utility.
    # No guessed secret or payoff is observed before the guess. Horizon 3 checks
    # that the terminal reward (at t=2) is counted only once.
    def __init__(self, probability=0.5):
        super().__init__({"p_one": probability, "reveal_cost": 0.1})
        self.add(Agent("a", horizon=3, discount=1))

    def initial_state(self):
        return {"t": 0, "secret": None, "visible": False, "last": {}, "value": {"a": 0}}

    def observe(self, state, agent):
        return {k: v for k, v in state.items() if k != "secret" or state["visible"]}

    def beliefs(self, observation, agent):
        if observation["t"] == 0 or observation["visible"]:
            return [(1.0, {"secret": None, **observation})]
        p = self.params["p_one"]
        return [(1 - p, {**observation, "secret": 0}), (p, {**observation, "secret": 1})]

    def actions(self, observation, agent):
        return ["wait", "reveal"] if observation["t"] == 0 else [0, 1]

    def outcomes(self, state, joint):
        action = joint["a"]
        if state["t"] == 0:
            p = self.params["p_one"]
            return [(probability, {"t": 1, "secret": bit, "visible": action == "reveal",
                                   "last": dict(joint),
                                   "value": {"a": -self.params["reveal_cost"] if action == "reveal" else 0}})
                    for probability, bit in [(1 - p, 0), (p, 1)]]
        return [(1.0, {**state, "t": 2, "last": dict(joint), "value": {"a": int(action == state["secret"])}})]

    def terminal(self, state):
        return "finished" if state["t"] == 2 else None


@pytest.mark.parametrize("probability", [0.25, 0.5, 0.75])
def test_future_choices_cannot_see_hidden_branch(probability):
    world = FutureBit(probability)
    values = dict(action_values(world, world.initial_state(), world.agents[0]))
    assert values == pytest.approx({"wait": max(probability, 1 - probability), "reveal": 0.9})
    assert plan(world, world.initial_state(), world.agents[0]) == "reveal"


@pytest.mark.parametrize("probability", [0.25, 0.75])
def test_initial_belief_distribution_is_independent_of_hidden_truth(probability):
    world = FutureBit(probability)
    for bit in (0, 1):
        state = {**world.initial_state(), "t": 1, "secret": bit}
        assert dict(action_values(world, state, world.agents[0])) == {0: 1 - probability, 1: probability}


def test_depth_cap_is_effective_without_an_invented_tail_value():
    world = Investment()
    actor = replace(world.agents[0], search_depth=1)
    assert dict(action_values(world, world.initial_state(), actor)) == {"consume": 1, "invest": -1}
    assert plan(world, world.initial_state(), actor) == "consume"


@pytest.mark.parametrize("discount", [0.0, 0.5, 0.9])
def test_discounted_three_round_search_matches_sequence_enumeration(discount):
    world = Investment({"horizon": 3, "discount": discount})
    sequences = world.sequence_values()
    reference = {action: max(r["value"] for r in sequences if r["actions"][0] == action)
                 for action in ("consume", "invest")}
    assert dict(action_values(world, world.initial_state(), world.agents[0])) == pytest.approx(reference)


def test_initial_terminal_state_requires_no_action():
    class Finished(TwoAction):
        def terminal(self, state):
            return "done"

    world = Finished()
    assert plan(world, world.initial_state(), world.agents[0]) is None
    assert run(world, 5, None) == ("done", world.initial_state(), [])


def test_kernel_is_the_only_source_of_execution_randomness():
    world = ThresholdRisk()
    state, joint = world.initial_state(), {"chooser": "risky"}
    with pytest.raises(ValueError, match="requires an rng"):
        world.step(state, joint)
    # Fixed quantiles test both sides of the exact CDF, not a flaky frequency test.
    class Quantile:
        def __init__(self, value):
            self.value = value

        def random(self):
            return self.value

    for quantile, collapsed in [(0.0, True), (0.499, True), (0.5, False), (0.999, False)]:
        assert world.step(state, joint, Quantile(quantile))["collapsed"] == collapsed


@pytest.mark.parametrize("weights", [[0.2, 0.2], [-0.5, 1.5], [float("nan"), 1], []])
def test_invalid_kernel_is_rejected(weights):
    with pytest.raises(ValueError, match="probabilities"):
        distribution((p, {}) for p in weights)


def test_beliefs_must_not_contradict_observation():
    class Contradiction(TwoAction):
        def beliefs(self, observation, agent):
            return [(1.0, {**observation, "t": 99})]

    world = Contradiction()
    with pytest.raises(ValueError, match="hypotheses"):
        plan(world, world.initial_state(), world.agents[0])


class GrowingWork(TwoAction):
    def __init__(self, params=None, rng=None):
        super().__init__(params, rng)
        self.agents = [replace(self.agents[0], horizon=1, node_budget=3)]
        self.by_id = {a.id: a for a in self.agents}

    def outcomes(self, state, joint):
        successor = super().outcomes(state, joint)[0][1]
        return [(1.0, successor)] if state["t"] == 0 else [(0.5, successor), (0.5, successor)]


def test_budget_exhaustion_cannot_choose_from_partial_scores():
    world = GrowingWork()
    with pytest.raises(SearchLimitExceeded):
        plan(world, {**world.initial_state(), "t": 1}, world.agents[0])
    record = run_record(GrowingWork, {}, 5, 0, include_trace=True)
    assert record["status"] == "search_limit" and record["label"] is None
    assert record["terminal"] is None and record["rounds_run"] == 1
    assert record["final_state"]["t"] == 1 and len(record["trace"]) == 1
    assert record["planning"]["a"] == {"horizon": 1, "effective_depth": 1, "node_budget": 3, "k": 0}
    complete = {"status": "complete", "label": "survived"}
    assert shares([record, complete]) == {"survived": 0.5, "unresolved:search_limit": 0.5}


def test_nested_plans_share_root_budget():
    from tests.planner_cases import DirectedResponse
    world = DirectedResponse(False, True)
    actor = replace(world.agents[0], node_budget=4)
    with pytest.raises(SearchLimitExceeded):
        plan(world, world.initial_state(), actor)


@pytest.mark.parametrize("settings", [{"search_depth": 1.5}, {"horizon": 0}, {"node_budget": 0}, {"k": 2}])
def test_invalid_search_configuration(settings):
    with pytest.raises(ValueError):
        Agent("a", **settings)
