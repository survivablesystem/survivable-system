"""E9: public records as a module over any world."""
import random

import pytest

from engine.core import key
from engine.history import History
from engine.power import harm_target, power_table, row_for
from engine.rules import Check, checked_states, enforcement
from engine.transfers import Transfers
from worlds import authority as A, commons


def authority(**overrides):
    return A.make({**A.DEFAULTS, **overrides}, random.Random(0))


def test_worlds_must_opt_in_to_records():
    with pytest.raises(NotImplementedError):
        History(commons.make({**commons.DEFAULTS, "n": 2}, random.Random(0)), 2)


def test_records_hold_the_last_public_facts_newest_first():
    world = History(authority(), 2)
    s = world.initial_state()
    joint = {"ruler": A.EXTRACT, "c0": A.STAY, "p0": A.STAY, "p1": A.STAY}
    (_, s1), = list(world.outcomes(s, joint))
    (_, s2), = list(world.outcomes(s1, {**joint, "ruler": A.GOVERN}))
    (_, s3), = list(world.outcomes(s2, joint))
    assert [r["extracting"] for r in s2["record"]] == [True, False]  # facts of s1, then s
    assert [r["extracting"] for r in s3["record"]] == [False, True]  # length 2: s is gone
    for agent in world.agents:
        o = world.observe(s3, agent)
        assert o["record"] == s3["record"]
        assert all(key(world.observe(h, agent)) == key(o) for _, h in world.beliefs(o, agent))


def test_records_never_change_goal_free_power():
    world = History(authority(commands=2, army=4), 2)
    target = harm_target(world, "extraction")
    with_records = power_table(world, world.initial_state(), 2, target)
    plain = power_table(world.inner, world.inner.initial_state(), 2, harm_target(world.inner, "extraction"))
    for row in with_records:
        match = row_for(world.inner, plain, row["coalition"])
        assert (row["force"], row["prevent"]) == (match["force"], match["prevent"])


@pytest.mark.parametrize("assembly, records, holds", [("all", True, True), ("all", False, False), ("none", True, False)])
def test_restitution_holds_only_with_records_and_assembly_at_the_defaults(assembly, records, holds):
    base = authority(assembly=assembly)
    world = Transfers(base, A.restitution_pairs(base), (1.2,), "public")
    if records:
        world = History(world, 2)
    report = enforcement(world, A, A.restitution, world.initial_state(), 4, reach=1)
    assert report["holds_unilaterally"] is holds
    if not holds:
        assert report["unilateral"]["c0"]["gain"] > 0  # the commander's coup is what pays
