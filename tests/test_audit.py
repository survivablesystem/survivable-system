"""Audit world contracts. Expectations live in rediscovery/captured-auditor.md."""
from itertools import product
import random

import pytest

from engine.core import action_values, distribution, key
from engine.power import externalization
from engine.rules import checked_states, follow_value
from worlds import audit as W


def world(**overrides):
    return W.make({**W.DEFAULTS, **overrides}, random.Random(0))


def test_register_is_complete():
    assert set(W.FIXED) == set(W.FIXED_REASONS)
    assert set(W.DEFAULTS) == set(W.SPACE)


@pytest.mark.parametrize("assignment", ["firm", "fixed"])
def test_kernel_is_a_distribution_over_every_menu_joint(assignment):
    w = world(assignment=assignment, auditors=2)
    for weak, exposed, licensed in product((False, True), ([], ["a0"]), (["a0", "a1"], ["a1"], [])):
        s = {**w.initial_state(), "weak": weak, "exposed": exposed, "licensed": licensed}
        menus = [w.actions(w.observe(s, a), a) for a in w.agents]
        for choice in product(*menus):
            support = distribution(w.outcomes(s, dict(zip([a.id for a in w.agents], choice))))
            for _, after in support:
                assert set(after["licensed"]) <= set(licensed)
                assert after["hired"] in after["licensed"] or (not after["licensed"] and after["hired"] == "none")


def test_misleading_needs_both_the_firm_and_a_lenient_auditor():
    w = world(exposure=0.0)
    s = {**w.initial_state(), "weak": True}
    joint = lambda f, a: {"firm": f, "a0": a, "a1": W.IDLE, "regulator": W.WAIT}
    after = lambda f, a: {x["misled"] for _, x in distribution(w.outcomes(s, joint(f, a)))}
    assert after("misstate>a0", W.LENIENT) == {True}
    assert after("misstate>a0", W.STRICT) == after("honest>a0", W.LENIENT) == {False}


def test_outsiders_cannot_see_the_books():
    w = w0 = world()
    regulator = w.by_id["regulator"]
    weak, sound = ({**w.initial_state(), "weak": b} for b in (True, False))
    assert key(w.observe(weak, regulator)) == key(w.observe(sound, regulator))
    assert action_values(w, weak, regulator) == action_values(w, sound, regulator)
    for agent in w0.agents:
        for s in (weak, sound):
            observation = w.observe(s, agent)
            assert all(key(w.observe(h, agent)) == key(observation) for _, h in w.beliefs(observation, agent))


def test_revocation_is_irreversible_and_declared_so():
    w = world(auditors=1)
    s = {**w.initial_state(), "licensed": [], "hired": "none"}
    rows = {r["harm"]: r for r in externalization(w, W, s, 2)}  # raises if a license could return
    assert rows["no licensed auditor"]["keep"]["size"] == 0


@pytest.mark.parametrize("name", list(W.RULES))
def test_rules_prescribe_menu_actions_everywhere_checked(name):
    w = world()
    for s in checked_states(w, W.RULES[name], w.initial_state(), 2):
        follow_value(w, W.RULES[name], s, 2)  # raises if a prescribed action is off the menu
