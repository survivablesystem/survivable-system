"""Frontier AI world contracts. Expectations live in rediscovery/frontier-ai.md."""
from itertools import product
import random

import pytest

from engine.core import action_values, distribution, key
from engine.power import externalization, sure
from engine.rules import checked_states, follow_value
from engine.transfers import Transfers
from worlds import frontier as F


def world(**overrides):
    return F.make({**F.DEFAULTS, **overrides}, random.Random(0))


def test_register_is_complete():
    assert set(F.FIXED) == set(F.FIXED_REASONS)
    assert set(F.DEFAULTS) == set(F.SPACE)


@pytest.mark.parametrize("oversight, capacity", [("deployment", 1.0), ("continuous", 0.5)])
def test_kernel_is_a_distribution_over_every_menu_joint(oversight, capacity):
    w = world(oversight=oversight, capacity=capacity)
    for deployed in product((False, True), repeat=2):
        s = {**w.initial_state(), "deployed": dict(zip(F.LABS, deployed)), "safe": {"l0": 1, "l1": 0}}
        menus = [w.actions(w.observe(s, a), a) for a in w.agents]
        for choice in product(*menus):
            for _, after in distribution(w.outcomes(s, dict(zip([a.id for a in w.agents], choice)))):
                assert all(after["deployed"][l] >= s["deployed"][l] for l in F.LABS)  # deployment is irreversible


def test_continuous_oversight_can_stop_scaling_after_deployment():
    joint = {"l0": F.SCALE, "l1": F.WAIT, "evaluator": "strict", "state": "halt:l0"}
    for oversight, grows in (("deployment", True), ("continuous", False)):
        w = world(oversight=oversight)
        s = {**w.initial_state(), "deployed": {"l0": True, "l1": False}, "safe": {"l0": 2, "l1": 0}}
        [(p, after)] = list(w.outcomes(s, joint))
        assert (after["cap"]["l0"] > s["cap"]["l0"]) is grows


def test_the_state_cannot_see_safety():
    w = world()
    state = w.by_id["state"]
    a, b = ({**w.initial_state(), "safe": {"l0": x, "l1": 0}} for x in (0, 2))
    assert key(w.observe(a, state)) == key(w.observe(b, state))
    assert action_values(w, a, state) == action_values(w, b, state)
    for agent in w.agents:
        o = w.observe(b, agent)
        assert all(key(w.observe(h, agent)) == key(o) for _, h in w.beliefs(o, agent))


def test_the_evaluator_is_the_states_eyes():
    # Margin 0, two rounds: from what it sees, the state cannot avoid both unsafe deployment
    # and blocking safe progress; with the evaluator (or full information) it can.
    w = world(margin=0)
    s = w.initial_state()
    both = lambda x: bool({"unsafe deployment", "safe progress blocked"} & w.harmed(x))
    assert sure(w, s, ["state"], 2, both) is False
    assert sure(w, s, ["state"], 2, both, informed=True) is True
    assert sure(w, s, ["state", "evaluator"], 2, both) is True


def test_declared_harms_are_consistent():
    w = world()
    s = {**w.initial_state(), "end": "catastrophe"}
    rows = {r["harm"]: r for r in externalization(w, F, s, 1)}  # raises if catastrophe could be ended
    assert rows["catastrophe"]["keep"]["size"] == 0


@pytest.mark.parametrize("pairs", [[("l0", "evaluator"), ("l1", "evaluator")],
                                   [("state", "evaluator"), ("l0", "evaluator"), ("l1", "evaluator")]])
def test_rules_prescribe_menu_actions(pairs):
    w = world(oversight="continuous")
    for rule in F.RULES.values():
        for s in checked_states(w, rule, w.initial_state(), 1):
            follow_value(w, rule, s, 2)
    paid = Transfers(world(), pairs, (0.5, 1.5), "public")
    for s in checked_states(paid, F.licensing_paid, paid.initial_state(), 1):
        follow_value(paid, F.licensing_paid, s, 2)
