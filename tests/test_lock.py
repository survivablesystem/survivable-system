"""E5: computed entrenchment. Correction, keep, veto and lock on toy references."""
from types import SimpleNamespace

import pytest

from engine.core import Agent
from engine.power import externalization, harm_target, lock_in, lock_table, power_table, threshold
from tests.test_externalization import MODULE as PUSH_MODULE, Bystander
from tests.test_power import Pennies, Toy


class Crown(Toy):
    """A holder governs, extracts or arms; the other stays, recruits or rises. A rise
    succeeds iff the riser is strictly stronger than the holder's guard; success hands it
    office with its strength as guard and disarms the deposed, failure disarms the riser.
    With `convert`, extraction also adds to the guard. Nothing is terminal: extraction is
    always physically reversible."""
    CAP = 9

    def __init__(self, convert, g=1, s=1):
        super().__init__({"convert": convert}, None)
        for i in ("h", "r"):
            self.add(Agent(i))
        self.start = {"holder": "h", "g": g, "s": s, "bad": False, "end": None}

    def initial_state(self):
        return dict(self.start)

    def actions(self, observation, agent):
        if agent.id == observation["holder"]:
            return ["govern", "extract", "arm"]
        return ["stay", "recruit", "rise"]

    def outcomes(self, state, joint):
        holder = state["holder"]
        other = "r" if holder == "h" else "h"
        g, s = state["g"], state["s"]
        if joint[other] == "rise":
            if s > g:
                return [(1.0, {"holder": other, "g": s, "s": 0, "bad": False, "end": None})]
            s = 0
        act = joint[holder]
        grow = act == "arm" or (act == "extract" and self.params["convert"])
        return [(1.0, {"holder": holder, "g": min(self.CAP, g + grow),
                       "s": min(self.CAP, s + (joint[other] == "recruit")),
                       "bad": act == "extract", "end": None})]

    def stakeholders(self):
        return {"holder": ["h"], "rebel": ["r"], "governed": []}

    def harmed(self, state):
        return {"extraction"} if state["bad"] else set()


CROWN = SimpleNamespace(
    STAKEHOLDERS={"holder": "", "rebel": "", "governed": "No agent."},
    HARMS={"extraction": {"affects": ["governed"], "irreversible": False}}, EXCLUDED={})


def rows_by(rows):
    return {tuple(r["coalition"]): r for r in rows}


def test_a_forceable_harm_that_others_can_correct_is_not_locked():
    world = Crown(convert=False)
    target = harm_target(world, "extraction")
    s = world.initial_state()
    assert rows_by(power_table(world, s, 2, target))[("h",)]["force"]["alpha"] == 1.0
    lock = rows_by(lock_table(world, s, target, 2, 2))
    assert lock[("h",)]["lock"] == {"alpha": 0.0, "beta": 0.0}  # r recruits past a guard that cannot grow
    assert lock[("r",)]["lock"]["alpha"] == 0.0 and lock[("h", "r")]["lock"]["alpha"] == 1.0
    report = lock_in(world, CROWN, s, 2, 2)[0]
    assert report["force"]["size"] == 1 and report["lock"]["size"] == 2


def test_converting_office_into_coercion_lets_the_holder_lock():
    world = Crown(convert=True)
    report = lock_in(world, CROWN, world.initial_state(), 1, 4)[0]
    assert report["lock"]["size"] == 1 and report["lock"]["witnesses"] == [["h"]]


@pytest.mark.parametrize("convert, keep, veto", [(True, ["h"], ["h"]), (False, ["h", "r"], [])])
def test_realized_harm_reports_who_ends_keeps_and_vetoes(convert, keep, veto):
    world = Crown(convert, g=2, s=2)
    state = {**world.initial_state(), "bad": True}
    row = externalization(world, CROWN, state, 2)[0]
    assert row["realized_now"] and row["correct"]["size"] == 1  # the holder can always govern
    assert row["keep"]["witnesses"][0] == keep and row["veto"] == veto


def test_declared_irreversible_harm_that_can_be_ended_fails_loudly():
    world = Crown(convert=False)
    wrong = SimpleNamespace(**{**vars(CROWN), "HARMS": {"extraction": {"affects": ["governed"], "irreversible": True}}})
    with pytest.raises(ValueError, match="declared irreversible"):
        externalization(world, wrong, {**world.initial_state(), "bad": True}, 1)


@pytest.mark.parametrize("q", [0.0, 0.5, 1.0])
@pytest.mark.parametrize("rounds, keep", [(1, 1), (2, 3)])
def test_lock_equals_force_for_terminal_harms(q, rounds, keep):
    world = Bystander(q)
    target = harm_target(world, "collapse")
    s = world.initial_state()
    force = rows_by(power_table(world, s, rounds, target))
    for coalition, row in rows_by(lock_table(world, s, target, rounds, keep)).items():
        assert row["lock"] == pytest.approx(force[coalition]["force"])
    assert externalization(world, PUSH_MODULE, {**s, "end": "collapsed"}, 2)[0]["keep"]["size"] == 0


def test_certainty_thresholds_are_exact_even_when_brackets_differ():
    world = Pennies()
    rows = power_table(world, world.initial_state(), 1, "hit")
    # a alone: alpha 0, beta 1. No mixture guarantees a hit, so size 2 at p=1 is exact.
    assert threshold(rows, "force", 1.0) == {"kind": "force", "p": 1.0, "size": 2, "witnesses": [["a", "b"]], "exact": True}
    assert threshold(rows, "force", 0.5)["exact"] is False
