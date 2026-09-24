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


def test_tullock_family_joins_ratio_and_threshold():
    ratio, tullock1 = world(contest="ratio"), world(contest="tullock", decisiveness=1.0, advantage=1.0)
    sharp, threshold = world(contest="tullock", decisiveness=64.0), world(contest="threshold")
    for a in range(0, 7):
        for d in range(0, 7):
            assert tullock1.contest(a, d) == pytest.approx(ratio.contest(a, d))
            # at level one half, a very decisive contest decides as the threshold contest does
            assert (sharp.contest(a, d) >= 0.5) == (threshold.contest(a, d) >= 0.5)
    assert 0.5 < world(contest="tullock", decisiveness=4.0, advantage=1.0).contest(3, 2) < 1.0


def test_tullock_survives_extreme_decisiveness():
    w = world(contest="tullock", decisiveness=1024.0)
    assert w.contest(1, 9) == 0.0 and w.contest(9, 1) == 1.0


def test_succession_passes_office_without_a_contest_and_counts_tenure():
    assert "tenure" not in world().initial_state()  # off by default: earlier states unchanged
    w = world(succession=True, term=2, commands=2, army=4)
    s = w.initial_state()
    assert "yield" in w.actions(w.observe(s, w.by_id["ruler"]), w.by_id["ruler"])
    stay = {a.id: "stay" for a in w.agents}
    kept = next(x for _, x in distribution(w.outcomes(s, {**stay, "ruler": "govern"})))
    assert kept["office"] == "ruler" and kept["tenure"] == 1
    passed = next(x for _, x in distribution(w.outcomes(kept, {**stay, "ruler": "yield"})))
    assert passed["office"] == "c0" and passed["tenure"] == 0
    assert passed["strength"]["ruler"] == kept["strength"]["ruler"]  # the retiree keeps its strength
    assert w.heir("c0", passed["strength"]) == "c1"
    due = {**kept, "tenure": 2}
    assert A.term_limit(w, w.observe(due, w.by_id["ruler"]), w.by_id["ruler"]) == "yield"
    over = {**kept, "tenure": 3}
    assert A.term_limit(w, w.observe(over, w.by_id["c0"]), w.by_id["c0"]) == "organize"
