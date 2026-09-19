"""Information contracts and quantified planner limits; see the paper diagnostic."""
from copy import deepcopy

import pytest

from engine.core import Agent, World, evaluate, plan, run
from tests.planner_cases import DirectedResponse, EqualActions, HiddenBit, Investment, ThresholdRisk


@pytest.mark.parametrize("actor_observes", [False, True])
@pytest.mark.parametrize("responder_observes", [False, True])
def test_response_follows_incoming_observation(actor_observes, responder_observes):
    world = DirectedResponse(actor_observes, responder_observes)
    actor, state = world.agents[0], world.initial_state()
    # Adaptive actor can take then go quiet to evade the second-round response.
    assert evaluate(world, state, actor, "take", 1) == (1 if responder_observes else 2)
    assert plan(world, state, actor) == ("quiet" if responder_observes else "take")
    assert evaluate(world, state, actor, "take", 0) == 2  # level 0 still expects repetition


def test_hidden_truth_cannot_change_values_or_choice():
    results = []
    for secret in (0, 1):
        world = HiddenBit(secret)
        state, actor = world.initial_state(), world.agents[0]
        original = deepcopy(state)
        results.append(([evaluate(world, state, actor, a, 0) for a in (0, 1)], plan(world, state, actor)))
        assert state == original
    assert results[0] == results[1] == ([1.0, 0.0], 0)


def test_revealed_information_can_change_choice():
    for secret in (0, 1):
        world = HiddenBit(secret, visible=True)
        assert plan(world, world.initial_state(), world.agents[0]) == secret


def test_action_menu_uses_observation_and_prior_runs_once():
    class PrivateMenu(HiddenBit):
        calls = 0

        def beliefs(self, observation, agent):
            self.calls += 1
            return super().beliefs(observation, agent)

        def actions(self, state, agent):
            assert "secret" not in state
            return [self.params["prior_bit"]]

    world = PrivateMenu(1)
    assert plan(world, world.initial_state(), world.agents[0]) == 0
    assert world.calls == 1


def test_execution_uses_truth_even_when_planning_uses_a_wrong_prior():
    world = HiddenBit(1)
    _, final, trace = run(world, 1, None)
    assert trace[0][0] == {"guesser": 0}
    assert final["secret"] == 1 and final["value"]["guesser"] == 0.0


def test_world_must_explicitly_declare_planning_information():
    class Undeclared(World):
        def actions(self, state, agent):
            return []

    with pytest.raises(NotImplementedError, match="observe"):
        plan(Undeclared({}, None), {}, Agent("a"))


def test_nested_response_cannot_recover_truth_hidden_from_parent():
    class PrivateResponse(DirectedResponse):
        def __init__(self, secret):
            super().__init__(True, True)
            self.secret = secret

        def initial_state(self):
            return {**super().initial_state(), "secret": self.secret}

        def observe(self, state, agent):
            # Responder knows its own bit; actor assumes 0. A nested responder
            # receives the actor's hypothetical bit, not the true self.secret.
            return {k: v for k, v in state.items() if k != "secret" or agent.id != "actor"}

        def beliefs(self, observation, agent):
            return [(1.0, {"secret": 0, **observation})]

        def transition(self, state, joint):
            next_state = super().transition(state, joint)
            next_state["secret"] = state["secret"]
            next_state["value"]["responder"] = (1 if state["secret"] else -1) if joint["responder"] == "respond" else 0
            return next_state

    hidden_values = []
    for bit in (0, 1):
        world = PrivateResponse(bit)
        state, actor = world.initial_state(), world.by_id["actor"]
        hidden_values.append(evaluate(world, state, actor, "take", 1))
        assert plan(world, state, world.by_id["responder"]) == ("respond" if bit else "ignore")
    assert hidden_values == [2, 2]


def test_equal_utility_can_hide_order_dependent_side_effects():
    recipients = []
    for order in [("left", "right"), ("right", "left")]:
        world = EqualActions(order)
        state, actor = world.initial_state(), world.agents[0]
        assert [evaluate(world, state, actor, action, 0) for action in order] == [1, 1]
        action = plan(world, state, actor)
        recipients.append(world.step(state, {actor.id: action})["beneficiary"])
    assert recipients == ["left", "right"]  # fixed-order ties remain an explicit limitation


@pytest.mark.parametrize("cost", [0.5, 1.0, 1.5])
def test_adaptive_planning_matches_best_sequence(cost):
    world = Investment({"cost": cost})
    state, actor = world.initial_state(), world.agents[0]
    chosen = plan(world, state, actor)
    reference = max(world.sequence_values(), key=lambda row: row["value"])
    assert reference["actions"] == ("invest", "consume")
    assert reference["value"] == 4 - cost > 2
    assert chosen == "invest" and evaluate(world, state, actor, chosen, 0) == reference["value"]


@pytest.mark.parametrize("probability", [0.25, 0.5, 0.75])
def test_branch_weighted_utility_matches_exact_risk_ranking(probability):
    world = ThresholdRisk({"low_probability": probability})
    state, actor = world.initial_state(), world.agents[0]
    exact = world.exact_values()
    assert exact["risky"] == 2 - 12 * probability < exact["safe"] == 1
    assert evaluate(world, state, actor, "risky", 0) == exact["risky"]
    assert plan(world, state, actor) == "safe"


def test_threshold_reference_agrees_when_there_is_no_uncertainty():
    world = ThresholdRisk({"low_probability": 0.0})
    state, actor = world.initial_state(), world.agents[0]
    for action, exact in world.exact_values().items():
        assert evaluate(world, state, actor, action, 0) == exact
