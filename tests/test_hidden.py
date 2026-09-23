"""E12: hidden types with beliefs derived by Bayes from what each agent observes. Toy references."""
import math
from types import SimpleNamespace

import pytest

from engine.rules import Hidden, checked_paths, enforcement
from tests.test_rules import Theft, lock_thieves

MODULE = SimpleNamespace(HARMS={"hurt": {"affects": ["g"], "irreversible": False}})


def thief_or(prior, other_loot, name="honest"):
    """x is a thief (stealing pays it 1) with `prior`, otherwise a type for whom it pays `other_loot`."""
    return {"x": {"thief": (prior, Theft(["x", "g"], loot=1.0)), name: (1 - prior, Theft(["x", "g"], loot=other_loot))}}


def after_theft(world, rule=lock_thieves):
    """The path on which x stole in the first round."""
    return next(path for s, path in checked_paths(world, rule, world.initial_state(), 1, distinct=True)
                if s["stole"])


def test_trigger_credible_only_with_updating():
    world = Theft(["x", "g"])
    plain = enforcement(world, MODULE, lock_thieves, world.initial_state(), 3, reach=1)
    # Locking out a thief who then follows the rule is pure cost.
    assert plain["unilateral"]["g"]["gain"] == pytest.approx(0.5) and plain["unilateral"]["g"]["action"] == "watch"
    types = thief_or(0.05, -1.0)
    blind = enforcement(world, MODULE, lock_thieves, world.initial_state(), 3, reach=1, types=types, precision=0)
    learns = enforcement(world, MODULE, lock_thieves, world.initial_state(), 3, reach=1, types=types)
    # At a 5% prior, a theft that teaches nothing leaves the lock-out not worth its cost...
    g = blind["unilateral"]["g"]
    assert g["gain"] > 0.3 and g["action"] == "watch" and g["state"]["stole"] and g["posterior"]["thief"] == 0.05
    # ...but only the thief would steal, so the theft reveals it and the lock-out is credible.
    assert learns["unilateral"]["g"]["gain"] <= 1e-9
    assert Hidden(world, lock_thieves, "x", types["x"]).posterior(after_theft(world), "g", 3)["thief"] == 1.0
    # The rule fails for the thief type (it steals), holds for the honest one.
    by_type = learns["unilateral"]["x"]["by_type"]
    assert by_type["thief"]["gain"] == pytest.approx(1.0) and by_type["honest"]["gain"] <= 0
    assert learns["unilateral"]["x"]["type"] == "thief"


def test_a_departure_every_type_would_make_teaches_nothing():
    world = Theft(["x", "g"])
    types = thief_or(0.3, 3.0, name="greedy")  # both steal
    post = Hidden(world, lock_thieves, "x", types["x"]).posterior(after_theft(world), "g", 3)
    assert post["thief"] == pytest.approx(0.3)


def test_conduct_the_observer_cannot_see_teaches_nothing():
    class Dark(Theft):
        def observe(self, state, agent):
            return state if agent.id == "x" else {"locked": state["locked"], "stole": False}

        def beliefs(self, observation, agent):
            return [(1.0, {"t": 0, "last": None, "value": {"x": 0.0, "g": 0.0}, "hurt": False, **observation})]
    world = Dark(["x", "g"])
    types = {"x": {"thief": (0.05, Dark(["x", "g"], loot=1.0)), "honest": (0.95, Dark(["x", "g"], loot=-1.0))}}
    hidden = Hidden(world, lock_thieves, "x", types["x"])
    assert hidden.posterior(after_theft(world), "g", 3)["thief"] == pytest.approx(0.05)
    assert hidden.posterior(after_theft(world), "x", 3)["thief"] == pytest.approx(0.05)  # x's own view: no learning


def test_a_sight_no_type_would_choose_goes_to_the_types_that_lose_least():
    world = Theft(["x", "g"])
    types = {"x": {"reluctant": (0.1, Theft(["x", "g"], loot=-0.2)), "honest": (0.9, Theft(["x", "g"], loot=-1.0))}}
    path = after_theft(world)
    limit = Hidden(world, lock_thieves, "x", types["x"]).posterior(path, "g", 3)
    assert limit == {"reluctant": 1.0, "honest": 0.0}
    sharp = Hidden(world, lock_thieves, "x", types["x"], precision=10).posterior(path, "g", 3)
    loose = Hidden(world, lock_thieves, "x", types["x"], precision=1).posterior(path, "g", 3)
    assert 0.1 < loose["reluctant"] < sharp["reluctant"] < 1.0 and sharp["reluctant"] > 0.99


def test_committed_types_and_following_are_evidence_too():
    world = Theft(["x", "g"])
    types = {"x": {"thief": (0.5, Theft(["x", "g"], loot=1.0)), "rule-bound": (0.5, None)}}
    hidden = Hidden(world, lock_thieves, "x", types["x"])
    assert hidden.posterior(after_theft(world), "g", 3) == {"thief": 1.0, "rule-bound": 0.0}
    quiet = next(path for s, path in checked_paths(world, lock_thieves, world.initial_state(), 1, distinct=True)
                 if path and path[-1][1] == {"x": "idle", "g": "watch"})
    # The thief would have stolen; seeing x keep the rule clears it.
    assert hidden.posterior(quiet, "g", 3) == {"thief": 0.0, "rule-bound": 1.0}
    with pytest.raises(ValueError):
        Hidden(world, lock_thieves, "x", {"a": (0.5, None), "b": (0.4, None)})
    # A departure no declared type makes is read as an error after which the rule resumes
    # (the one-shot convention): beliefs stay at the prior.
    assert Hidden(world, lock_thieves, "x", {"a": (1.0, None)}).posterior(after_theft(world), "g", 3) == {"a": 1.0}


def test_no_types_reproduces_the_plain_check():
    world = Theft(["x", "g"])
    plain = enforcement(world, MODULE, lock_thieves, world.initial_state(), 3, reach=1)
    only = enforcement(world, MODULE, lock_thieves, world.initial_state(), 3, reach=1,
                       types={"x": {"as declared": (1.0, None)}})
    assert only["unilateral"]["g"]["gain"] == pytest.approx(plain["unilateral"]["g"]["gain"])
    assert plain["types"] is None and only["types"] == {"x": {"as declared": 1.0}}
    assert math.isinf(Hidden(world, lock_thieves, "x", {"a": (1.0, None)}).precision)


def test_a_persisting_type_acts_on_its_goals_in_the_checked_round_too():
    # Regression: departure values once had the persisting type play the rule in the checked
    # round while the follow value had it best-respond. After a theft, against a sure thief:
    # locking now costs 0.5 and one simultaneous theft (-2.5); watching lets it steal now and
    # next round, lock then (-2 - 0.9 * 2.5 = -4.25).
    world = Theft(["x", "g"])
    hidden = Hidden(world, lock_thieves, "x", {"thief": (1.0, Theft(["x", "g"], loot=1.0))})
    path = after_theft(world)
    r = hidden.facing(path, "g", 3).unilateral(path[-1][2], "g", 3)
    assert r["action"] == "watch" and r["gain"] == pytest.approx(-1.75)
