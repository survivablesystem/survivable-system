"""E4 composition: parts reproduce, couplings act, the whole shows what parts cannot."""
import random

import pytest

from engine.compose import Composite, uncovered
from engine.core import run
from engine.power import externalization, force, joint_prevention
from worlds import commons, race_commons as rc, treaty


def single(params=None):
    params = {**commons.DEFAULTS, "n": 3, **(params or {})}
    part = commons.make(params, random.Random(0))
    planning = {k: params[k] for k in ("horizon", "search_depth", "discount", "k", "others")}
    whole = Composite(params, random.Random(0), {"commons": part}, {"commons": {"u0": "u0", "u1": "u1", "u2": "u2"}},
                      planning={**planning, "node_budget": commons.FIXED["node_budget"]},
                      stakeholders={name: [("commons", name)] for name in commons.STAKEHOLDERS})
    return part, whole


def test_one_part_composite_reproduces_its_part():
    part, whole = single()
    label, state, trace = run(part, 20, random.Random(3))
    w_label, w_state, w_trace = run(whole, 20, random.Random(3))
    assert [{i: a["commons"] for i, a in j.items()} for j, _ in w_trace] == [j for j, _ in trace]
    assert w_state["parts"]["commons"] == state
    at = {**part.initial_state(), "S": 12.0}
    w_at = {**whole.initial_state(), "parts": {"commons": at}}
    values = []
    for coalition in ([], ["u0"], ["u0", "u1"], ["u0", "u1", "u2"]):
        values.append(force(part, at, coalition, 2, "collapsed"))
        assert force(whole, w_at, coalition, 2, lambda s: "commons: collapse" in whole.harmed(s)) == values[-1]
    assert 0 < max(values)  # the comparison is not vacuous


def at_stock(world, S):
    state = world.initial_state()
    state["parts"]["commons"] = {**state["parts"]["commons"], "S": S}
    return state


def rename(report, mapping):
    return [(r["force"]["size"], r["prevent"]["size"], [sorted(mapping[i] for i in w) for w in r["prevent"]["witnesses"]])
            for r in report]


def test_without_a_draw_the_whole_reproduces_the_fishery():
    whole = rc.make({**rc.DEFAULTS, "draw": 0.0}, random.Random(0))
    from tests.test_symmetry import Unreduced
    part = Unreduced(commons.make({**commons.DEFAULTS, "n": 3, "sanction": False}, random.Random(0)))
    for S in (30.0, 40.0):
        w = [r for r in externalization(whole, rc, at_stock(whole, S), 2) if r["harm"].startswith("commons")]
        p = externalization(part, commons, {**part.initial_state(), "S": S}, 2)
        assert rename(w, {i: i for i in ("east", "west", "fisher")}) == rename(p, rc.members(1)["commons"])


def test_building_draws_on_the_shared_stock_and_outsiders_see_only_public_facts():
    whole = rc.make({**rc.DEFAULTS, "draw": 2.0}, random.Random(0))
    state = at_stock(whole, 30.0)
    joint = {"east": {"commons": ("rest", False), "treaty": "build"},
             "west": {"commons": ("rest", False), "treaty": "build"}, "fisher": {"commons": ("rest", False)}}
    [(p, after)] = list(whole.outcomes(state, joint))
    grown = 30.0 + 0.5 * 30.0 * (1 - 30.0 / 100.0)
    assert after["parts"]["commons"]["S"] == pytest.approx(grown - 2 * 2.0 * whole.parts["commons"].lo)
    seen = whole.observe(state, whole.by_id["fisher"])["treaty"]
    assert seen["cap"] == {} and seen["strikes"] == {"a": 0, "b": 0}


def test_every_part_exclusion_is_carried_or_covered():
    assert uncovered(rc.PARTS, rc.EXCLUDED, rc.COVERS) == []
    assert uncovered(rc.PARTS, rc.EXCLUDED, {}) == ["treaty: third states"]
    whole = rc.make(dict(rc.DEFAULTS), random.Random(0))
    assert set(whole.stakeholders()) == set(rc.STAKEHOLDERS)
    assert whole.stakeholders()["harvesters"] == ["east", "west", "fisher"]


@pytest.mark.parametrize("draw, expected", [(0.0, []), (2.0, [["west"]])])
def test_forced_choice_between_own_safety_and_the_fishery_appears_only_with_a_draw(draw, expected):
    whole = rc.make({**rc.DEFAULTS, "draw": draw, "treaty.lead": 0, "treaty.advantage": 1.5}, random.Random(0))
    rows = {tuple(r["harms"]): r for r in joint_prevention(whole, rc, at_stock(whole, 30.0), 2)}
    assert rows[("commons: collapse", "treaty: b disarmed")]["forced_choice"] == expected


def test_cli_nested_state_override_reaches_the_part():
    import json, subprocess, sys
    from pathlib import Path
    out = subprocess.run([sys.executable, "-m", "engine", "worlds.race_commons", "--externalities", "1", "--json",
                          "--state", "parts.commons.S=12", "--fix", "draw=0.0"],
                         cwd=Path(__file__).resolve().parents[1], capture_output=True, text=True)
    assert out.returncode == 0, out.stderr
    whole = rc.make({**rc.DEFAULTS, "draw": 0.0}, random.Random(0))
    expected = externalization(whole, rc, at_stock(whole, 12.0), 1)
    assert json.loads(out.stdout)["results"]["harms"] == json.loads(json.dumps(expected))


def test_cli_repeated_fix_flags_accumulate():
    import subprocess, sys
    from pathlib import Path
    out = subprocess.run([sys.executable, "-m", "engine", "worlds.race_commons", "--externalities", "1", "--json",
                          "--fix", "fishers=2", "--fix", "draw=2.0"],
                         cwd=Path(__file__).resolve().parents[1], capture_output=True, text=True)
    assert out.returncode == 0, out.stderr
    import json
    baseline = json.loads(out.stdout)["settings"]["baseline"]
    assert baseline["fishers"] == 2 and baseline["draw"] == 2.0
