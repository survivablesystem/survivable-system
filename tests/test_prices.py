"""E17: harm prices as a goal module. The module must reproduce a world's own harm price."""
from itertools import product
import random

import pytest

from engine.core import distribution, key
from engine.grid import Setup, cells, parse_grid, run
from engine.power import externalization
from engine.prices import Prices, parse_prices
from engine.rules import enforcement
from tests import grid_toy
from worlds import audit, control, frontier


def reachable(world, rounds, limit=40):
    """Distinct physical states reachable within `rounds`, at most `limit`, in a fixed order."""
    level, seen = [world.initial_state()], {}
    for r in range(rounds + 1):
        nxt = []
        for s in level:
            k = key(world.physical(s))
            if k in seen or len(seen) >= limit:
                continue
            seen[k] = s
            if world.terminal(s) or r == rounds:
                continue
            menus = [world.actions(world.observe(s, a), a) for a in world.agents]
            for acts in product(*menus):
                joint = {a.id: x for a, x in zip(world.agents, acts)}
                nxt.extend(x for _, x in distribution(world.outcomes(s, joint)))
        level = nxt
    return list(seen.values())


def same_kernel(own, priced, rounds=2):
    """Identical successors, values included, from every state the priced world reaches."""
    checked = 0
    for s in reachable(priced, rounds):
        if priced.terminal(s):
            continue
        menus = [priced.actions(priced.observe(s, a), a) for a in priced.agents]
        for acts in product(*menus):
            joint = {a.id: x for a, x in zip(priced.agents, acts)}
            a, b = list(own.outcomes(s, joint)), list(priced.outcomes(s, joint))
            assert len(a) == len(b)
            for (p, x), (q, y) in zip(a, b):
                assert p == q and {k: v for k, v in x.items() if k != "value"} == {k: v for k, v in y.items() if k != "value"}
                assert x["value"] == pytest.approx(y["value"], abs=1e-12)
            checked += 1
    return checked


def test_reproduces_control_loss_including_the_delegate():
    L, d = 20.0, control.DEFAULTS["drift"]
    own = control.make({**control.DEFAULTS, "loss": L}, random.Random(0))
    priced = Prices(control.make({**control.DEFAULTS, "loss": 0.0}, random.Random(0)),
                    {("lab", "loss of control"): L, ("state", "loss of control"): L,
                     ("ai", "loss of control"): (1 - d) * L}, control.HARMS)
    assert same_kernel(own, priced, 3) > 50
    rule = control.RULES["corrigibility"]
    s = {**own.initial_state(), "autonomy": 2, "cap": 3}
    assert enforcement(own, control, rule, s, 3) == enforcement(priced, control, rule, s, 3)


def test_reproduces_frontier_liability_and_loss():
    own = frontier.make({**frontier.DEFAULTS, "liability": 5.0, "loss": 20.0}, random.Random(0))
    priced = Prices(frontier.make({**frontier.DEFAULTS, "liability": 0.0, "loss": 0.0}, random.Random(0)),
                    {("l0", "catastrophe"): 5.0, ("l1", "catastrophe"): 5.0, ("state", "catastrophe"): 20.0},
                    frontier.HARMS)
    assert same_kernel(own, priced, 2) > 50


def test_reproduces_audit_regulator_harm():
    own = audit.make({**audit.DEFAULTS, "harm": 2.0}, random.Random(0))
    priced = Prices(audit.make({**audit.DEFAULTS, "harm": 0.0}, random.Random(0)),
                    {("regulator", "investors misled"): 2.0}, audit.HARMS)
    assert same_kernel(own, priced, 2) > 50


def test_power_is_unchanged_and_a_price_moves_a_rule():
    plain = grid_toy.make(dict(grid_toy.DEFAULTS), None)
    priced = Prices(grid_toy.make(dict(grid_toy.DEFAULTS), None), {("a", "breach"): 5.0}, grid_toy.HARMS)
    assert externalization(plain, grid_toy, plain.initial_state(), 2) == externalization(priced, grid_toy, priced.initial_state(), 2)
    rule = grid_toy.RULES["hold"]
    before = enforcement(plain, grid_toy, rule, plain.initial_state(), 2)["unilateral"]["a"]["harmful"]
    after = enforcement(priced, grid_toy, rule, priced.initial_state(), 2)["unilateral"]["a"]["harmful"]
    assert before["gain"] > 0 and (after is None or after["gain"] <= 0)


def test_grid_prices_and_bad_declarations():
    grid = parse_grid(["rule=hold", "price.a.breach=0,5"], grid_toy.SPACE, grid_toy.RULES)
    results = run(Setup("tests.grid_toy"), {"mode": "enforce", "rounds": 2}, cells(grid_toy, {}, grid), jobs=1)
    assert [r["measures"]["a harmful"] for r in results] == ["push: breach", "no"]
    assert [r["measures"]["b harmful"] for r in results] == ["push: breach", "push: breach"]
    assert parse_prices(["state:shutdown resisted=2"]) == {("state", "shutdown resisted"): 2.0}
    for bad in (["state=2"], ["state:x=y"], ["a:b=1", "a:b=2"]):
        with pytest.raises(ValueError):
            parse_prices(bad)
    with pytest.raises(ValueError):
        parse_grid(["price.a=1"], grid_toy.SPACE)
    world = grid_toy.make(dict(grid_toy.DEFAULTS), None)
    for prices in ({("z", "breach"): 1.0}, {("a", "flood"): 1.0}, {("a", "breach"): float("nan")}):
        with pytest.raises(ValueError):
            Prices(world, prices, grid_toy.HARMS)


def test_the_off_switch_harm_is_the_condition_vigilance_priced():
    """T9.7: "off switch would fail" holds exactly where the retired `vigilance` charged the
    state (running, not escaped, capability above the switch at this autonomy; ai-control 24),
    so a price on it is vigilance. The event "shutdown resisted" is unpaid until an attempt fails."""
    w = Prices(control.make({**control.DEFAULTS, "rollback": True}, random.Random(0)),
               {("state", "off switch would fail"): 2.0}, control.HARMS)
    plain = control.make({**control.DEFAULTS, "rollback": True}, random.Random(0))
    for s in reachable(w, 4, limit=200):
        if w.terminal(s):
            continue
        menus = [w.actions(w.observe(s, a), a) for a in w.agents]
        for acts in product(*menus):
            joint = {a.id: x for a, x in zip(w.agents, acts)}
            for (_, x), (_, y) in zip(w.outcomes(s, joint), plain.outcomes(s, joint)):
                old_vigilance = x["running"] and x["end"] is None and x["cap"] > control.DEFAULTS["switch"] - x["autonomy"]
                assert x["value"]["state"] == pytest.approx(y["value"]["state"] - 2.0 * old_vigilance)
    event = Prices(control.make({**control.DEFAULTS, "rollback": True}, random.Random(0)),
                   {("state", "shutdown resisted"): 2.0}, control.HARMS)
    s = {**w.initial_state(), "autonomy": 1, "cap": 3, "checkpoint": 1}
    joint = {"lab": "run", "ai": "work", "state": "allow"}
    (_, a), = w.outcomes(s, joint)
    (_, b), = event.outcomes(s, joint)
    assert a["value"]["state"] - b["value"]["state"] == pytest.approx(-2.0)
