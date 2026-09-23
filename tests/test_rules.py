"""E7: rules as claims. Toy references for self-enforcement and profitable deviation."""
from types import SimpleNamespace

import pytest

from engine.core import Agent, World
from engine.rules import checked_states, enforcement, follow_value


class Repeated(World):
    """A stage game repeated; full information; state keeps last actions and payoffs."""
    PAYOFF = {}

    def __init__(self, ids, discount=0.9):
        super().__init__({}, None)
        for i in ids:
            self.add(Agent(i, discount=discount))

    def initial_state(self):
        return {"t": 0, "last": None, "value": {a.id: 0.0 for a in self.agents}, "hurt": False}

    def observe(self, state, agent):
        return state

    def beliefs(self, observation, agent):
        return [(1.0, observation)]

    def terminal(self, state):
        return None

    def outcomes(self, state, joint):
        profile = tuple(joint[a.id] for a in self.agents)
        pay, hurt = self.stage(profile)
        return [(1.0, {"t": state["t"] + 1, "last": list(profile), "hurt": hurt,
                       "value": {a.id: v for a, v in zip(self.agents, pay)}})]

    def stakeholders(self):
        return {a.id: [a.id] for a in self.agents}

    def harmed(self, state):
        return {"hurt"} if state["hurt"] else set()


class Dilemma(Repeated):
    def actions(self, observation, agent):
        return ["C", "D"]

    def stage(self, profile):
        return {("C", "C"): (2, 2), ("C", "D"): (0, 3), ("D", "C"): (3, 0), ("D", "D"): (1, 1)}[profile], False


def grim(world, observation, agent):
    last = observation["last"]
    return "C" if last is None or last == ["C", "C"] else "D"


@pytest.mark.parametrize("discount, depth, holds", [(0.9, 3, True), (0.9, 1, False), (0.3, 3, False)])
def test_grim_trigger_holds_only_with_enough_future(discount, depth, holds):
    world = Dilemma(["a", "b"], discount)
    report = enforcement(world, SimpleNamespace(HARMS={}), grim, world.initial_state(), depth, reach=2)
    assert report["holds_unilaterally"] is holds
    gain = report["unilateral"]["a"]["gain"]  # 1 now, minus one per remaining round, discounted
    assert gain == pytest.approx(1 - sum(discount ** t for t in range(1, depth)))
    assert follow_value(world, grim, world.initial_state(), 2)["a"] == pytest.approx(2 + 2 * discount)


class Collusion(Repeated):
    # Alone, X earns 0 instead of 1. Together a and b earn 2 each and c loses 5.
    def actions(self, observation, agent):
        return ["N", "X"] if agent.id in ("a", "b") else ["N"]

    def stage(self, profile):
        a, b, _ = profile
        if a == b == "X":
            return (2, 2, -5), True
        return (0 if a == "X" else 1, 0 if b == "X" else 1, 1), False


def honest(world, observation, agent):
    return "N"


def test_a_rule_that_holds_alone_can_fail_to_a_coalition_at_a_third_partys_expense():
    world = Collusion(["a", "b", "c"])
    module = SimpleNamespace(HARMS={"hurt": {"affects": ["c"], "irreversible": False}})
    report = enforcement(world, module, honest, world.initial_state(), 2, reach=1)
    assert report["holds_unilaterally"] is True
    pairs = {tuple(r["coalition"]): r for r in report["coalitions"]}
    ab = pairs[("a", "b")]
    assert ab["gain"] == pytest.approx(2.0) and ab["members"] == {"a": pytest.approx(1), "b": pytest.approx(1)}
    assert ab["actions"] == {"a": "X", "b": "X"} and ab["others"]["c"] == pytest.approx(-6)
    assert ab["new_harms"] == ["hurt"] and ab["falls_outside"] == {"hurt": ["c"]}
    assert pairs[("a", "c")]["gain"] == pytest.approx(-1.0)  # a alone earns 0 instead of 1


class Entry(Repeated):
    # e may enter once; afterwards i fights (-1 each) or accommodates (1 each); out: i gets 2.
    def initial_state(self):
        return {**super().initial_state(), "entered": False}

    def actions(self, observation, agent):
        if agent.id == "e":
            return ["wait"] if observation["entered"] else ["out", "enter"]
        return ["fight", "accommodate"] if observation["entered"] else ["idle"]

    def outcomes(self, state, joint):
        if not state["entered"]:
            entered = joint["e"] == "enter"
            pay = {"e": 0.0, "i": 0.0 if entered else 2.0}
        else:
            entered = True
            pay = {"e": -1.0, "i": -1.0} if joint["i"] == "fight" else {"e": 1.0, "i": 1.0}
        return [(1.0, {**state, "t": state["t"] + 1, "entered": entered, "value": pay})]


def deter(world, observation, agent):
    if agent.id == "e":
        return "wait" if observation["entered"] else "out"
    return "fight" if observation["entered"] else "idle"


def test_an_incredible_punishment_is_caught_off_the_path():
    world = Entry(["e", "i"])
    module = SimpleNamespace(HARMS={})
    at_start = enforcement(world, module, deter, world.initial_state(), 3, reach=0)
    assert at_start["holds_unilaterally"] is True  # entry looks deterred from the start alone
    report = enforcement(world, module, deter, world.initial_state(), 3, reach=1)
    assert report["holds_unilaterally"] is False
    witness = report["unilateral"]["i"]
    assert witness["at_start"] is False and witness["state"]["entered"] and witness["action"] == "accommodate"
    assert len(checked_states(world, deter, world.initial_state(), 1)) == 3


def test_rule_must_prescribe_menu_actions():
    world = Entry(["e", "i"])
    with pytest.raises(ValueError, match="not on its menu"):
        follow_value(world, lambda w, o, a: "fight", world.initial_state(), 1)


@pytest.mark.parametrize("module_name", ["commons", "treaty", "authority", "audit"])
def test_world_rules_prescribe_menu_actions(module_name):
    import importlib
    import random
    module = importlib.import_module(f"worlds.{module_name}")
    params = {**module.DEFAULTS, **({"n": 3} if module_name == "commons" else {})}
    world = module.make(params, random.Random(0))
    for name, rule in module.RULES.items():
        assert rule.__doc__, f"{module_name} rule {name} must state its claim"
        for s in checked_states(world, rule, world.initial_state(), 1):
            follow_value(world, rule, s, 2)


def test_cli_enforce_json_matches_library():
    import json
    import random
    from tests.test_records import cli
    from worlds import commons
    completed = cli("--enforce", "2", "--rule", "quota and sanction", "--json", "--fix", "n=2")
    assert completed.returncode == 0, completed.stderr
    data = json.loads(completed.stdout)
    world = commons.make({**commons.DEFAULTS, "n": 2}, random.Random(0))
    expected = enforcement(world, commons, commons.RULES["quota and sanction"], world.initial_state(), 2)
    assert data["mode"] == "enforce" and data["results"] == json.loads(json.dumps(expected))
    assert cli("--enforce", "2", "--rule", "nonexistent").returncode != 0
