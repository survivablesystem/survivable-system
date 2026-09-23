"""E1: declared harms and stakeholders; who can force, impose, prevent. Toy references."""
import random
from types import SimpleNamespace

import pytest

from engine.power import externalization
from tests.test_power import Push, Toy
from worlds import commons, treaty


class Bystander(Push):
    # Push's collapse falls on the parties and on bystanders; "b hurt" falls only on b.
    def stakeholders(self):
        return {"a": ["a"], "b": ["b"], "bystanders": []}

    def harmed(self, state):
        return {"collapse", "b hurt"} if state["end"] == "collapsed" else set()


MODULE = SimpleNamespace(
    STAKEHOLDERS={"a": "", "b": "", "bystanders": "No agent."},
    HARMS={"collapse": {"affects": ["bystanders"], "irreversible": True},
           "b hurt": {"affects": ["b"], "irreversible": True}},
    EXCLUDED={})


def by_harm(report):
    return {row["harm"]: row for row in report}


def test_harm_on_a_non_agent_is_imposed_from_outside_and_unrepresented():
    world = Bystander(1.0)  # a push always collapses: b cannot block
    rows = by_harm(externalization(world, MODULE, world.initial_state(), 2))
    collapse = rows["collapse"]
    assert collapse["unrepresented"] == ["bystanders"] and collapse["affected_agents"] == []
    assert collapse["outsiders_force"]["size"] == 1 and collapse["outsiders_force"]["witnesses"] == [["a"]]
    assert collapse["affected_prevent"] is None


def test_harmed_agent_that_can_block_is_not_exposed():
    world = Bystander(0.0)  # a block always holds
    hurt = by_harm(externalization(world, MODULE, world.initial_state(), 2))["b hurt"]
    assert hurt["affected_agents"] == ["b"] and hurt["unrepresented"] == []
    assert hurt["outsiders_force"]["size"] is None  # a alone cannot impose it
    assert hurt["affected_prevent"] == {"alpha": 1.0, "beta": 1.0}
    assert hurt["prevent"]["size"] == 1 and hurt["prevent"]["witnesses"] == [["a"], ["b"]]  # a can also just wait


def test_undeclared_worlds_fail_loudly():
    class Silent(Toy):
        pass
    with pytest.raises(NotImplementedError):
        Silent({}, None).harmed({})
    with pytest.raises(ValueError):
        externalization(Bystander(0.5), SimpleNamespace(STAKEHOLDERS={"a": ""}, HARMS={}, EXCLUDED={}),
                        {"t": 0, "end": None}, 1)


@pytest.mark.parametrize("module", [commons, treaty])
def test_worlds_declare_consistent_harms(module):
    world = module.make(dict(module.DEFAULTS), random.Random(0))
    assert set(world.stakeholders()) == set(module.STAKEHOLDERS)
    for spec in module.HARMS.values():
        assert set(spec["affects"]) <= set(module.STAKEHOLDERS) and "irreversible" in spec
    assert all(module.EXCLUDED.values())
    assert world.harmed(world.initial_state()) == set()


def test_commons_harms_read_only_physical_state():
    world = commons.make({**commons.DEFAULTS, "n": 3}, random.Random(0))
    for S in (5.0, 20.0, 30.0):
        base = {**world.initial_state(), "S": S}
        other = {**base, "wealth": {a.id: 9.0 for a in world.agents}, "last": {a.id: ("hi", True) for a in world.agents}}
        assert world.harmed(base) == world.harmed(other)
    assert world.harmed({**world.initial_state(), "S": 20.0}) == {"depleted"}


def test_commons_collapse_falls_on_the_unrepresented_and_the_users_force_it():
    world = commons.make({**commons.DEFAULTS, "n": 3}, random.Random(0))
    rows = by_harm(externalization(world, commons, {**world.initial_state(), "S": 20.0}, 2))
    collapse = rows["collapse"]
    assert collapse["unrepresented"] == ["future users", "stock-dependent others"]
    assert collapse["outsiders_force"]["size"] is None  # only the empty coalition is outside, and it forces nothing
    assert rows["depleted"]["realized_now"] and rows["depleted"]["affected_agents"] == []


def test_treaty_leader_can_impose_disarmament_on_a_population_without_agents():
    world = treaty.make({**treaty.DEFAULTS, "lead": 2}, random.Random(0))  # 4 vs 2, advantage 2
    rows = by_harm(externalization(world, treaty, world.initial_state(), 1))
    b = rows["b disarmed"]
    assert b["outsiders_force"]["witnesses"] == [["a"]] and b["affected_prevent"]["alpha"] == 0.0
    assert b["unrepresented"] == ["population of b"]
    assert rows["a disarmed"]["force"]["size"] is None


def test_realized_reversible_harm_reports_who_can_end_it():
    world = commons.make({**commons.DEFAULTS, "n": 3}, random.Random(0))  # restraint on by default
    depleted = by_harm(externalization(world, commons, {**world.initial_state(), "S": 20.0}, 1))["depleted"]
    assert depleted["realized_now"] and depleted["affected_correct"] is None  # it falls on no agent
    # One round of regrowth from 20 needs the others' restraint: taking low or high keeps it below 25.
    assert depleted["correct"]["size"] == 3
    collapse = by_harm(externalization(world, commons, {**world.initial_state(), "S": 20.0}, 1))["collapse"]
    assert collapse["correct"] is None and not collapse["realized_now"]


def test_cli_externalities_json_matches_library():
    import json
    from tests.test_records import cli
    completed = cli("--externalities", "1", "--json", "--fix", "n=2", "--state", "S=20")
    assert completed.returncode == 0, completed.stderr
    data = json.loads(completed.stdout)
    assert data["mode"] == "externalities" and data["harms"] == commons.HARMS
    world = commons.make({**commons.DEFAULTS, "n": 2}, random.Random(0))
    assert data["results"] == externalization(world, commons, {**world.initial_state(), "S": 20.0}, 1)
    assert cli("--power", "1", "--state", "nope=1").returncode != 0
