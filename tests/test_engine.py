"""Engine behavior that no world may change."""
import random

from engine.core import Agent, World, plan, run


class TwoAction(World):
    """One agent, two actions. 'good' pays 1 per round, 'bad' pays 0. Nothing else."""

    def __init__(self, params=None, rng=None):
        super().__init__(params or {}, rng)
        self.add(Agent("a", horizon=3))

    def initial_state(self):
        return {"t": 0, "last": {}, "value": {"a": 0.0}}

    def observe(self, state, agent):
        return state  # This deterministic, single-agent test has no private information.

    def beliefs(self, observation, agent):
        return [(1.0, observation)]

    def actions(self, state, agent):
        return ["bad", "good"]

    def outcomes(self, state, joint):
        return [(1.0, {"t": state["t"] + 1, "last": dict(joint), "value": {"a": 1.0 if joint["a"] == "good" else 0.0}})]

    def prior_action(self, agent, other):
        return "bad"

    def terminal(self, state):
        return None

    def label(self, state):
        return "done"


def test_planner_picks_higher_value():
    w = TwoAction()
    assert plan(w, w.initial_state(), w.agents[0]) == "good"


def test_step_is_pure():
    w = TwoAction()
    s0 = w.initial_state()
    s1 = w.step(s0, {"a": "good"})
    assert s0["t"] == 0 and s1["t"] == 1


def test_run_returns_label_and_trace():
    w = TwoAction()
    label, state, trace = run(w, 5, random.Random(0))
    assert label == "done" and state["t"] == 5 and len(trace) == 5


def test_opponent_model_is_validated_and_ignored_at_level_zero():
    import pytest
    from engine.core import Agent
    with pytest.raises(ValueError):
        Agent("x", others="guess")
    assert Agent("x", k=0, others="plan").others == "plan"
