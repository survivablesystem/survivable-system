"""E10: amendable rules as a module over any world."""
import random
from types import SimpleNamespace

import pytest

from engine.constitution import KEEP, Constitution, constitutional
from engine.core import key
from engine.power import harm_target, power_table, row_for
from engine.rules import enforcement
from tests.test_rules import Collusion, honest
from worlds import frontier as F


def collude(world, observation, agent):
    return "X" if agent.id in ("a", "b") else "N"


MODULE = SimpleNamespace(HARMS={"hurt": {"affects": ["c"], "irreversible": False}})


def captured(report):
    out = []
    for c in report["coalitions"]:
        for e in (c.get("externalizing"), c.get("sequential")):
            acts = e and (e.get("actions") or e.get("first"))
            if e and e.get("gain") and e["gain"] > 1e-9 and (e.get("capture", True)) and \
                    any(a[1] != KEEP for a in acts.values()):
                out.append(c["coalition"])
    return out


@pytest.mark.parametrize("voters, threshold, capture", [(["a", "b"], 2, True), (["a", "b", "c"], 3, False)])
def test_a_pair_that_can_amend_captures_the_rulebook(voters, threshold, capture):
    world = Constitution(Collusion(["a", "b", "c"]), {"honest": honest, "collude": collude}, voters, threshold, "honest")
    report = enforcement(world, MODULE, constitutional, world.initial_state(), 3, reach=1)
    assert report["holds_unilaterally"] is True  # one vote changes nothing
    assert (["a", "b"] in captured(report)) is capture


def test_amendment_takes_effect_next_round_and_is_public():
    world = Constitution(Collusion(["a", "b", "c"]), {"honest": honest, "collude": collude}, ["a", "b"], 2, "honest")
    s = world.initial_state()
    joint = {"a": ("N", "amend:collude"), "b": ("N", "amend:collude"), "c": ("N", KEEP)}
    [(p, after)] = list(world.outcomes(s, joint))
    assert after["regime"] == "collude" and not after["inner"]["hurt"]
    assert world.observe(after, world.by_id["c"])["regime"] == "collude"
    for agent in world.agents:
        o = world.observe(after, agent)
        assert all(key(world.observe(h, agent)) == key(o) for _, h in world.beliefs(o, agent))


def test_amendment_never_changes_goal_free_power():
    base = F.make(dict(F.DEFAULTS), random.Random(0))
    world = Constitution(base, {"licensing": F.licensing, "race": F.race}, ["state", "l0", "l1"], 2, "licensing")
    target = harm_target(world, "unsafe deployment")
    with_c = power_table(world, world.initial_state(), 2, target)
    plain = power_table(base, base.initial_state(), 2, harm_target(base, "unsafe deployment"))
    for row in with_c:
        match = row_for(base, plain, row["coalition"])
        assert (row["force"], row["prevent"]) == (match["force"], match["prevent"])
