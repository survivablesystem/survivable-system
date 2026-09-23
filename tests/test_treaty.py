"""Treaty world contracts. Outcome expectations live in rediscovery/treaty-no-verification.md."""
import random

import pytest

from engine.core import action_values, distribution, key
from engine.power import force, sure
from worlds import treaty


def world(**overrides):
    return treaty.make({**treaty.DEFAULTS, **overrides}, random.Random(0))


def test_register_is_complete():
    assert set(treaty.FIXED) == set(treaty.FIXED_REASONS)
    assert set(treaty.DEFAULTS) == set(treaty.SPACE)


@pytest.mark.parametrize("contest", ["ratio", "threshold"])
def test_kernel_is_a_distribution_for_every_joint(contest):
    w = world(contest=contest)
    for ca in range(0, 7):
        for cb in range(0, 7):
            state = {**w.initial_state(), "cap": {"a": ca, "b": cb}}
            for ja in treaty.HOLD, treaty.BUILD, treaty.STRIKE:
                for jb in treaty.HOLD, treaty.BUILD, treaty.STRIKE:
                    support = distribution(w.outcomes(state, {"a": ja, "b": jb}))
                    assert all(s["end"] in (None, "a_disarmed", "b_disarmed") for _, s in support)


def test_hidden_rival_capability_does_not_change_values():
    w = world(verification="none")
    a = w.by_id["a"]
    base = {**w.initial_state(), "t": 2}
    variants = [{**base, "cap": {"a": 3, "b": c}, "builds": {"a": 0, "b": k}} for c, k in ((2, 0), (3, 1), (4, 2))]
    observations = {key(w.observe(s, a)) for s in variants}
    assert len(observations) == 1
    values = [action_values(w, s, a) for s in variants]
    assert values[0] == values[1] == values[2]


def test_beliefs_reproduce_the_observation():
    w = world(verification="none")
    state = {**w.initial_state(), "t": 3, "strikes": {"a": 0, "b": 1}}
    for agent in w.agents:
        observation = w.observe(state, agent)
        support = w.beliefs(observation, agent)
        assert sum(p for p, _ in support) == pytest.approx(1)
        rival = treaty.RIVAL[agent.id]
        assert len(support) == 3 - state["strikes"][rival] + 1  # 0..k builds in non-strike rounds
        assert all(key(w.observe(s, agent)) == key(observation) for _, s in support)


def test_threshold_strike_disarms_only_with_the_advantage():
    w = world(contest="threshold", advantage=2.0)
    state = {**w.initial_state(), "cap": {"a": 4, "b": 2}}
    [(p, after)] = list(w.outcomes(state, {"a": treaty.STRIKE, "b": treaty.BUILD}))
    assert p == 1.0 and after["end"] == "b_disarmed" and after["value"]["a"] > 0 > after["value"]["b"]
    state = {**w.initial_state(), "cap": {"a": 3, "b": 2}}
    [(p, after)] = list(w.outcomes(state, {"a": treaty.STRIKE, "b": treaty.BUILD}))
    assert after["end"] is None and after["cap"] == {"a": 3, "b": 3}


def test_power_reads_no_goals():
    reference = None
    for overrides in [{}, {"security": 0.0, "prize": 5.0}, {"build_cost": 1.0, "horizon": 1, "k": 0}]:
        w = world(**overrides)
        s = w.initial_state()
        values = [force(w, s, c, 3, "b_disarmed") for c in ([], ["a"], ["b"], ["a", "b"])]
        reference = reference or values
        assert values == reference
    assert sure(w, s, ["b"], 3, "b_disarmed", informed=True) in (True, False)
