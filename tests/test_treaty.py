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
            state = {**w.initial_state(), "cap": {"a": [ca], "b": [cb]}}
            for ja in treaty.HOLD, treaty.BUILD, treaty.STRIKE:
                for jb in treaty.HOLD, treaty.BUILD, treaty.STRIKE:
                    support = distribution(w.outcomes(state, {"a": ja, "b": jb}))
                    assert all(s["end"] in (None, "a_disarmed", "b_disarmed") for _, s in support)


def test_hidden_rival_capability_does_not_change_values():
    w = world(verification="none")
    a = w.by_id["a"]
    base = {**w.initial_state(), "t": 2}
    variants = [{**base, "cap": {"a": [3], "b": [c]}, "builds": {"a": [0], "b": [k]}} for c, k in ((2, 0), (3, 1), (4, 2))]
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
    state = {**w.initial_state(), "cap": {"a": [4], "b": [2]}}
    [(p, after)] = list(w.outcomes(state, {"a": treaty.STRIKE, "b": treaty.BUILD}))
    assert p == 1.0 and after["end"] == "b_disarmed" and after["value"]["a"] > 0 > after["value"]["b"]
    state = {**w.initial_state(), "cap": {"a": [3], "b": [2]}}
    [(p, after)] = list(w.outcomes(state, {"a": treaty.STRIKE, "b": treaty.BUILD}))
    assert after["end"] is None and after["cap"] == {"a": [3], "b": [3]}


def test_power_reads_no_goals():
    reference = None
    for overrides in [{}, {"security": 0.0, "prize": 5.0}, {"build_cost": 1.0, "horizon": 1, "k": 0}]:
        w = world(**overrides)
        s = w.initial_state()
        values = [force(w, s, c, 3, "b_disarmed") for c in ([], ["a"], ["b"], ["a", "b"])]
        reference = reference or values
        assert values == reference
    assert sure(w, s, ["b"], 3, "b_disarmed", informed=True) in (True, False)


def test_elasticity_one_is_the_t31_growth():
    w = world(elasticity=1.0, returns=0.5)
    assert [w.grow(c) for c in range(2, 8)] == [min(12, c + 1 + int(0.5 * c)) for c in range(2, 8)]
    steep = world(elasticity=2.0, returns=0.5)
    assert steep.grow(2) == w.grow(2) and steep.grow(6) > w.grow(6)


def test_scarce_budget_limits_building_and_accrues_income():
    w = world(budget="scarce", reserve=0)
    s = w.initial_state()
    a = w.by_id["a"]
    assert treaty.BUILD not in w.actions(w.observe(s, a), a)
    [(_, s)] = list(w.outcomes(s, {"a": treaty.HOLD, "b": treaty.HOLD}))
    [(_, s)] = list(w.outcomes(s, {"a": treaty.HOLD, "b": treaty.HOLD}))
    assert s["budget"] == {"a": 2, "b": 2} and treaty.BUILD in w.actions(w.observe(s, a), a)
    [(_, s)] = list(w.outcomes(s, {"a": treaty.BUILD, "b": treaty.HOLD}))
    assert s["budget"] == {"a": 1, "b": 3}
    free = world()
    assert treaty.BUILD in free.actions(free.observe(free.initial_state(), a), a)


def test_scarce_beliefs_reproduce_observation_and_respect_the_budget():
    w = world(budget="scarce", reserve=1, verification="none")
    state = {**w.initial_state(), "t": 3}
    for agent in w.agents:
        observation = w.observe(state, agent)
        support = w.beliefs(observation, agent)
        assert sum(p for p, _ in support) == pytest.approx(1)
        assert all(key(w.observe(s, agent)) == key(observation) for _, s in support)
        rival = treaty.RIVAL[agent.id]
        assert max(sum(s["builds"][rival]) for _, s in support) == 1  # 1 + 3 - 2k >= 1
        assert all(s["budget"][rival] >= 0 for _, s in support)


@pytest.mark.parametrize("prior", [0.0, 0.5, 1.0])
@pytest.mark.parametrize("reserve", [0, 3])
def test_scarce_beliefs_are_a_distribution_at_every_round(prior, reserve):
    w = world(budget="scarce", reserve=reserve, verification="none", prior_build=prior)
    for t in range(0, 6):
        state = {**w.initial_state(), "t": t}
        for agent in w.agents:
            support = w.beliefs(w.observe(state, agent), agent)
            assert sum(p for p, _ in support) == pytest.approx(1)
            if prior == 1.0 and t:
                rival = treaty.RIVAL[agent.id]
                assert sum(support[0][1]["builds"][rival]) == max(
                    k for k in range(t + 1) if k == 0 or reserve + t - 2 * k >= 1)


def test_two_domains_menus_contests_and_mutual_disarmament():
    w = world(domains=2, contest="threshold", advantage=2.0)
    a = w.by_id["a"]
    assert w.actions(w.observe(w.initial_state(), a), a) == ["hold", "build", "build:1", "strike", "strike:1"]
    state = {**w.initial_state(), "cap": {"a": [4, 2], "b": [2, 4]}}
    [(p, after)] = list(w.outcomes(state, {"a": "strike", "b": "strike:1"}))
    assert after["end"] == "both_disarmed" and after["value"]["a"] == pytest.approx(after["value"]["b"])
    [(p, after)] = list(w.outcomes(state, {"a": "build:1", "b": "strike"}))
    assert after["end"] is None and after["cap"]["a"] == [4, 3]
    ratio = world(domains=2, contest="ratio")
    support = distribution(ratio.outcomes({**state, "cap": {"a": [3, 1], "b": [1, 3]}}, {"a": "strike", "b": "strike:1"}))
    assert len(support) == 4 and sum(p for p, s in support if s["end"] == "both_disarmed") == pytest.approx(9 / 16)


def test_two_domain_beliefs_split_unobserved_builds():
    w = world(domains=2, verification="none", prior_build=0.5)
    state = {**w.initial_state(), "t": 2}
    agent = w.by_id["a"]
    support = w.beliefs(w.observe(state, agent), agent)
    assert sum(p for p, _ in support) == pytest.approx(1) and len(support) == 6
    by = {tuple(s["builds"]["b"]): p for p, s in support}
    assert by[(0, 0)] == pytest.approx(0.25) and by[(1, 1)] == pytest.approx(0.125)
    assert all(key(w.observe(s, agent)) == key(w.observe(state, agent)) for _, s in support)


@pytest.mark.parametrize("opening", ["hold", "build"])
@pytest.mark.parametrize("verification", ["none", "exact"])
def test_opponent_model_decides_the_default_first_strike(opening, verification):
    # Decision 2026-09-23: with others planning at the root, the leader disarms the
    # trailer under every default opening and verification; with reacting others it does
    # so only when verified and the opening is hold (treaty finding 4).
    from engine.records import run_record
    params = {**treaty.DEFAULTS, "opening": opening, "verification": verification}
    plan = run_record(treaty.make, {**params, "others": "plan"}, 12, 0)
    react = run_record(treaty.make, {**params, "others": "react"}, 12, 0)
    assert plan["label"] == "b_disarmed"
    assert react["label"] == ("b_disarmed" if (opening, verification) == ("hold", "exact") else "no_disarm")
