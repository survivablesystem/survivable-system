"""T9.6: the frontier race and the AI control world composed. Case: rediscovery/race-control.md."""
import random

from engine.compose import uncovered
from engine.core import distribution
from engine.power import force
from engine.rules import checked_states, follow_value
from worlds import control as C, frontier as F, race_control as RC


def whole(**overrides):
    return RC.make({**RC.DEFAULTS, **overrides}, random.Random(0))


def test_register_and_exclusions_are_complete():
    assert set(RC.DEFAULTS) == set(RC.SPACE) and set(RC.FIXED) == set(RC.FIXED_REASONS)
    assert uncovered(RC.PARTS, RC.EXCLUDED, RC.COVERS) == []
    assert set(RC.HARMS) == {f"{p}: {h}" for p, m in RC.PARTS.items() for h in m.HARMS}


def test_uncoupled_whole_reproduces_the_parts_power():
    w = whole(coupled=False)
    s = w.initial_state()
    s["parts"]["control"] = {**s["parts"]["control"], "autonomy": 1, "cap": 3}
    s["parts"]["frontier"] = {**s["parts"]["frontier"], "deployed": {"l0": True, "l1": False}}
    ctl = C.make({**C.DEFAULTS, "horizon": 4}, random.Random(0))
    fr = F.make({**F.DEFAULTS, "horizon": 4}, random.Random(0))
    for whole_ids, part_ids in ((["lab A"], ["lab"]), (["AI"], ["ai"]), (["state"], ["state"])):
        assert force(w, s, whole_ids, 1, lambda x: "control: shutdown resisted" in w.harmed(x)) == \
            force(ctl, s["parts"]["control"], part_ids, 1, lambda x: "shutdown resisted" in ctl.harmed(x))
    assert force(w, s, ["lab A"], 1, lambda x: "frontier: unsafe deployment" in w.harmed(x)) == \
        force(fr, s["parts"]["frontier"], ["l0"], 1, lambda x: "unsafe deployment" in fr.harmed(x)) == 1.0


def test_coupling_carries_the_ais_gains_into_the_race():
    for coupled, expected in ((True, 3), (False, 2)):
        w = whole(coupled=coupled)
        s = w.initial_state()
        s["parts"]["control"] = {**s["parts"]["control"], "autonomy": 1}
        joint = {"lab A": {"frontier": "wait", "control": "run"}, "lab B": {"frontier": "wait"},
                 "evaluator": {"frontier": "strict"}, "state": {"frontier": "allow", "control": "allow"},
                 "AI": {"control": "improve"}}
        nxt = next(x for _, x in distribution(w.outcomes(s, joint)))
        assert nxt["parts"]["control"]["cap"] == 2 and nxt["parts"]["frontier"]["cap"]["l0"] == expected


def test_lifted_rules_prescribe_menu_actions():
    w = whole()
    for name, rule in RC.RULES.items():
        for s in checked_states(w, rule, w.initial_state(), 1):
            follow_value(w, rule, s, 2)
