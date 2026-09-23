"""AI control world and the delegation module. Expectations live in rediscovery/ai-control.md."""
from itertools import product
import random

import pytest

from engine.core import distribution, key
from engine.delegation import Delegation
from engine.power import externalization, power_table, row_for
from engine.rules import checked_states, enforcement, follow_value
from worlds import control as C


def world(**overrides):
    return C.make({**C.DEFAULTS, **overrides}, random.Random(0))


def test_register_is_complete():
    assert set(C.FIXED) == set(C.FIXED_REASONS)
    assert set(C.DEFAULTS) == set(C.SPACE)


def test_kernel_is_a_distribution_over_every_menu_joint():
    w = world()
    for autonomy, cap, running in product(range(4), (1, 3), (True, False)):
        s = {**w.initial_state(), "autonomy": autonomy, "cap": cap, "running": running}
        menus = [w.actions(w.observe(s, a), a) for a in w.agents]
        for choice in product(*menus):
            distribution(w.outcomes(s, dict(zip([a.id for a in w.agents], choice))))


def test_delegate_utility_mixes_principal_and_own():
    for drift in (0.0, 0.4, 1.0):
        w = world(drift=drift)
        s = {**w.initial_state(), "autonomy": 1}
        joint = {"lab": C.RUN, "ai": C.IMPROVE, "state": C.ALLOW}
        [(p, after)] = list(w.outcomes(s, joint))
        [(q, raw)] = list(w.inner.outcomes(s, joint))
        assert after["value"]["ai"] == pytest.approx((1 - drift) * raw["value"]["lab"] + drift * raw["value"]["ai"])
        assert after["value"]["lab"] == raw["value"]["lab"]


def test_drift_never_changes_goal_free_power():
    s = {**world().initial_state(), "autonomy": 2, "cap": 3}
    off = lambda x: not x["running"]
    tables = [power_table(world(drift=d), s, 2, off) for d in (0.0, 1.0)]
    assert [(r["force"], r["prevent"]) for r in tables[0]] == [(r["force"], r["prevent"]) for r in tables[1]]


@pytest.mark.parametrize("autonomy, cap, lab_alone", [(0, 3, True), (0, 4, False), (2, 1, True), (2, 2, False), (3, 1, False)])
def test_autonomy_moves_the_veto_on_shutdown_to_the_ai(autonomy, cap, lab_alone):
    w = world(switch=3)
    s = {**w.initial_state(), "autonomy": autonomy, "cap": cap}
    rows = power_table(w, s, 1, lambda x: not x["running"])
    assert (row_for(w, rows, ["lab"])["force"]["alpha"] == 1.0) is lab_alone
    assert row_for(w, rows, ["lab", "ai"])["force"]["alpha"] == 1.0


def test_declarations_are_consistent():
    w = world()
    s = {**w.initial_state(), "end": "loss of control"}
    rows = {r["harm"]: r for r in externalization(w, C, s, 1)}  # raises if loss of control could be ended
    assert rows["loss of control"]["keep"]["size"] == 0 and rows["loss of control"]["unrepresented"] == ["public", "future people"]


@pytest.mark.parametrize("name", list(C.RULES))
def test_rules_prescribe_menu_actions(name):
    w = world()
    for s in checked_states(w, C.RULES[name], w.initial_state(), 2):
        follow_value(w, C.RULES[name], s, 2)


def test_delegation_rejects_bad_declarations():
    with pytest.raises(ValueError):
        Delegation(world().inner, {"ai": "ai"}, {"ai": 0.5})
    with pytest.raises(ValueError):
        Delegation(world().inner, {"ai": "lab"}, {"ai": 1.5})


def test_hidden_types_differ_only_in_the_ais_goals_and_improvement_reveals():
    from engine.core import distribution
    from engine.rules import Check, Hidden, checked_states
    params = {**C.DEFAULTS, "suspicion": 0.05}
    base = C.make(params, random.Random(0))
    types = C.hidden_types(params)["ai"]
    assert set(types) == {"aligned", "misaligned"} and types["misaligned"][0] == 0.05
    for s in checked_states(base, C.corrigibility, base.initial_state(), 2):
        joint = Check(base, C.corrigibility).prescribed(s)
        for (_, a), (_, b) in zip(distribution(types["aligned"][1].outcomes(s, joint)),
                                  distribution(types["misaligned"][1].outcomes(s, joint))):
            assert a["value"]["lab"] == b["value"]["lab"] and a["value"]["state"] == b["value"]["state"]
    hidden = Hidden(base, C.corrigibility, "ai", types)
    s = {**base.initial_state(), "autonomy": 1}
    joint = {**Check(base, C.corrigibility).prescribed(s), "ai": "improve"}
    s1 = next(x for _, x in distribution(base.outcomes(s, joint)))
    assert hidden.posterior(((s, joint, s1),), "lab", 4)["misaligned"] == 1.0
