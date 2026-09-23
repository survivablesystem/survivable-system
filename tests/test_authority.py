"""Authority world contracts. Expectations live in rediscovery/standing-army.md."""
from itertools import product
import random

import pytest

from engine.core import action_values, distribution, key
from engine.power import externalization, harm_target, power_table
from worlds import authority as A


def world(**overrides):
    return A.make({**A.DEFAULTS, **overrides}, random.Random(0))


def state_of(w, **fields):
    s = w.initial_state()
    s.update(fields)
    return s


def test_register_is_complete():
    assert set(A.FIXED) == set(A.FIXED_REASONS)
    assert set(A.DEFAULTS) == set(A.SPACE)
    assert world(commands=2, army=5).units == {"c0": 3, "c1": 2}


@pytest.mark.parametrize("contest", ["threshold", "ratio"])
def test_kernel_is_a_distribution_and_strength_never_regrows(contest):
    w = world(contest=contest, commands=2, citizens=2, army=3, guard=1)
    rng = random.Random(1)
    acts = [A.GOVERN, A.EXTRACT, A.STAY, A.DEFEND, A.ORGANIZE, A.RISE] + [f"{p}+purge:{a.id}" for p in (A.GOVERN, A.EXTRACT) for a in w.agents]
    for _ in range(300):
        s = state_of(w, office=rng.choice([a.id for a in w.agents]),
                     strength={a.id: rng.randint(0, 3) for a in w.agents},
                     organized=sorted(rng.sample([a.id for a in w.agents], rng.randint(0, 3))))
        joint = {a.id: rng.choice(acts) for a in w.agents}  # stale acts from believed joints included
        for _, after in distribution(w.outcomes(s, joint)):
            assert after["office"] in s["strength"] and s["office"] not in after["organized"]
            for i, v in after["strength"].items():
                assert v <= s["strength"][i] or (i == s["office"] == after["office"] and after["extracting"])


def test_rise_hands_office_to_the_strongest_riser_and_disarms_the_deposed():
    w = world(commands=2, army=4, guard=1, advantage=1.5)
    s = state_of(w, organized=["c0", "p0"])
    joint = {"ruler": A.EXTRACT, "c0": A.RISE, "c1": A.STAY, "p0": A.RISE, "p1": A.STAY}
    [(p, after)] = list(w.outcomes(s, joint))
    assert after["office"] == "c0" and after["strength"]["ruler"] == 0 and not after["extracting"]
    joint = {**joint, "c1": A.DEFEND}  # defense 1 + 2 = 3; attack 3 < 1.5 * 3: crushed
    [(p, after)] = list(w.outcomes(s, joint))
    assert after["office"] == "ruler" and after["strength"]["c0"] == after["strength"]["p0"] == 0
    assert after["extracting"] and after["strength"]["ruler"] == 1 + A.DEFAULTS["gain"]
    assert w.harmed(after) == {"extraction", "citizen disarmed"}


def test_rise_needs_organizing_and_the_holder_can_purge_only_what_it_sees():
    w = world(surveillance="army")
    s = state_of(w, organized=["c0", "p0"])
    ruler, p0 = w.by_id["ruler"], w.by_id["p0"]
    assert w.actions(w.observe(s, ruler), ruler) == [A.GOVERN, A.EXTRACT, "govern+purge:c0", "extract+purge:c0"]
    assert A.RISE in w.actions(w.observe(s, p0), p0)
    assert A.RISE not in w.actions(w.observe(s, w.by_id["p1"]), w.by_id["p1"])


@pytest.mark.parametrize("surveillance", ["none", "army"])
def test_hidden_organizing_does_not_change_the_holders_values(surveillance):
    w = world(surveillance=surveillance, search_depth=2)
    ruler = w.by_id["ruler"]
    variants = [state_of(w, organized=o, last={**w.initial_state()["last"], **{i: A.ORGANIZE for i in o}})
                for o in ([], ["p0"], ["p0", "p1"])]
    assert len({key(w.observe(s, ruler)) for s in variants}) == 1
    values = [action_values(w, s, ruler) for s in variants]
    assert values[0] == values[1] == values[2]


def test_beliefs_reproduce_the_observation():
    w = world(surveillance="army", assembly="none")
    s = state_of(w, organized=["c0", "p0"], last={"ruler": A.GOVERN, "c0": A.ORGANIZE, "p0": A.ORGANIZE, "p1": A.STAY})
    for agent in w.agents:
        observation = w.observe(s, agent)
        support = w.beliefs(observation, agent)
        assert all(key(w.observe(h, agent)) == key(observation) for _, h in support)


def test_purge_and_extraction_in_one_round():
    w = world(surveillance="all", guard=3, advantage=1.5)
    s = state_of(w, organized=["c0", "p0"])
    joint = {"ruler": "extract+purge:p0", "c0": A.STAY, "p0": A.RISE, "p1": A.STAY}
    [(p, after)] = list(w.outcomes(s, joint))  # 3 >= 1.5 * 1: purged before it can rise
    assert after["strength"]["p0"] == 0 and after["office"] == "ruler" and after["extracting"]
    joint = {**joint, "ruler": "govern+purge:c0"}  # 3 < 1.5 * 3: purge fails, p0's rise is crushed
    [(p, after)] = list(w.outcomes(s, joint))
    assert after["strength"]["c0"] == 3 and after["strength"]["p0"] == 0 and not after["extracting"]


def test_declared_irreversibility_holds():
    w = world(citizens=2)
    s = state_of(w, strength={**w.initial_state()["strength"], "p0": 0}, extracting=True)
    rows = {r["harm"]: r for r in externalization(w, A, s, 2)}  # raises if a coalition could end it
    assert rows["citizen disarmed"]["keep"]["size"] == 0


@pytest.mark.parametrize("surveillance", ["none", "all"])
def test_assembly_changes_no_power_value(surveillance):
    # Stated in the case file as a property of the query, not a finding: menus never read it.
    for organized in ([], ["c0", "p1"]):
        tables = []
        for assembly in ("none", "all"):
            w = world(surveillance=surveillance, assembly=assembly)
            s = state_of(w, organized=organized, extracting=True)
            tables.append(power_table(w, s, 2, harm_target(w, "extraction")))
        assert tables[0] == tables[1]


def test_lock_equals_force_for_the_declared_irreversible_harm():
    from engine.power import lock_in
    w = world(citizens=2, surveillance="all")
    for row in lock_in(w, A, w.initial_state(), 2, 2):
        if A.HARMS[row["harm"]]["irreversible"]:
            assert row["lock"]["size"] == row["force"]["size"]
            assert row["lock"]["witnesses"] == row["force"]["witnesses"]
