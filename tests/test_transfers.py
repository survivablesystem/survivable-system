"""E8: side payments as a module over any world."""
import random

import pytest

from engine.core import key
from engine.power import harm_target, power_table, row_for
from engine.rules import Check, checked_states, enforcement
from engine.transfers import NONE, Transfers, lift
from worlds import audit, authority, commons, treaty


def wrap(module, pairs, amounts=(0.5, 1.0), disclosure="parties", **overrides):
    params = {**module.DEFAULTS, **({"n": 3} if module is commons else {}), **overrides}
    return Transfers(module.make(params, random.Random(0)), pairs, amounts, disclosure)


@pytest.mark.parametrize("module, pairs", [(audit, [("firm", "a0")]), (authority, [("ruler", "c0")]),
                                           (treaty, [("a", "b")]), (commons, [("u0", "u1")])])
def test_payments_never_change_goal_free_power(module, pairs):
    world = wrap(module, pairs)
    harm = next(iter(module.HARMS))
    with_pay = power_table(world, world.initial_state(), 2, harm_target(world, harm))
    without = power_table(world.base, world.base.initial_state(), 2, harm_target(world.base, harm))
    for row in with_pay:  # the base world may declare symmetry; compare coalition by coalition
        match = row_for(world.base, without, row["coalition"])
        assert (row["force"], row["prevent"]) == (match["force"], match["prevent"])


def test_payment_moves_utility_and_is_seen_by_the_parties_only():
    world = wrap(audit, [("firm", "a0")])
    s = world.initial_state()
    joint = {"firm": ("honest>a0", "pay:a0:1.0"), "a0": ("strict", NONE), "a1": ("idle", NONE),
             "regulator": ("wait", NONE)}
    base_joint = {i: a[0] for i, a in joint.items()}
    (p, after), = [(p, x) for p, x in world.outcomes(s, joint) if not x["base"]["weak"]][:1]
    (q, plain), = [(q, x) for q, x in world.base.outcomes(s["base"], base_joint) if not x["weak"]][:1]
    assert after["value"]["firm"] == pytest.approx(plain["value"]["firm"] - 1.0)
    assert after["value"]["a0"] == pytest.approx(plain["value"]["a0"] + 1.0)
    assert world.observe(after, world.by_id["a0"])["paid"] == {"firm": "pay:a0:1.0"}
    assert world.observe(after, world.by_id["regulator"])["paid"] == {}
    public = wrap(audit, [("firm", "a0")], disclosure="public")
    assert public.observe(after, public.by_id["regulator"])["paid"] == {"firm": "pay:a0:1.0"}
    for agent in world.agents:
        o = world.observe(after, agent)
        assert all(key(world.observe(h, agent)) == key(o) for _, h in world.beliefs(o, agent))


def test_lifted_rules_follow_the_base_rule_and_pay_nothing():
    world = wrap(audit, [("firm", "a0")])
    rule = lift(audit.independence)
    for s in checked_states(world, rule, world.initial_state(), 1):
        base = Check(world.base, audit.independence).prescribed(s["base"])
        assert Check(world, rule).prescribed(s) == {i: (a, NONE) for i, a in base.items()}


def test_a_bribe_makes_capture_pay_every_member():
    plain = audit.make(dict(audit.DEFAULTS), random.Random(0))
    state = {**plain.initial_state(), "weak": True}
    without = Check(plain, audit.independence).joint(state, ["firm", "a0"], 4, lambda h: {x: ["investors"] for x in h})
    assert without["externalizing"]["every_member"] is False  # the auditor gains nothing by itself
    world = wrap(audit, [("firm", "a0")])
    lifted = {"base": state, "paid": {}, "value": {a.id: 0.0 for a in world.agents}}
    paid = Check(world, lift(audit.independence)).joint(lifted, ["firm", "a0"], 4, lambda h: {x: ["investors"] for x in h})
    assert paid["externalizing"]["every_member"] is False  # summed value cannot tell a bribe from none
    e = paid["externalizing_every"]
    assert e["every_member"] and e["actions"]["firm"][1].startswith("pay:a0") and e["actions"]["a0"][0] == "lenient"
