"""Goal-free coalition power: exact toy references, duality, invariance and limits."""
import random

import pytest

from engine.core import Agent, World, key
from engine.power import PowerLimitExceeded, force, power_table, threshold, witness
from worlds import commons


class Toy(World):
    """Full-information toy. Goals are deliberately absent: power must not read them."""

    def observe(self, state, agent):
        return state

    def beliefs(self, observation, agent):
        return [(1.0, observation)]

    def terminal(self, state):
        return state.get("end")

    def value(self, state, agent):
        raise AssertionError("power queries must not read goals")


class Pennies(Toy):
    # Equal choices end in "hit", different ones in "miss". Stage order decides everything.
    def __init__(self):
        super().__init__({}, None)
        for i in ("a", "b"):
            self.add(Agent(i))

    def initial_state(self):
        return {"end": None}

    def actions(self, observation, agent):
        return [0, 1]

    def outcomes(self, state, joint):
        return [(1.0, {"end": "hit" if joint["a"] == joint["b"] else "miss"})]


class Push(Toy):
    # a pushes or waits; b blocks or idles. Push against idle collapses; against a block,
    # with probability q. Optionally b may leave: "escape" is a terminal, not the target.
    def __init__(self, q, leave=False):
        super().__init__({"q": q, "leave": leave}, None)
        for i in ("a", "b"):
            self.add(Agent(i))

    def initial_state(self):
        return {"t": 0, "end": None}

    def actions(self, observation, agent):
        if agent.id == "a":
            return ["push", "wait"]
        return ["block", "idle", "leave"] if self.params["leave"] else ["block", "idle"]

    def outcomes(self, state, joint):
        t = state["t"] + 1
        if joint["b"] == "leave":
            return [(1.0, {"t": t, "end": "escape"})]
        if joint["a"] == "wait":
            return [(1.0, {"t": t, "end": None})]
        q = 1.0 if joint["b"] == "idle" else self.params["q"]
        return [(q, {"t": t, "end": "collapsed"}), (1 - q, {"t": t, "end": None})]


def test_stage_order_brackets_a_randomized_value():
    world = Pennies()
    s = world.initial_state()
    assert force(world, s, ["a"], 1, "hit", "alpha") == 0.0
    assert force(world, s, ["a"], 1, "hit", "beta") == 1.0
    rows = {tuple(r["coalition"]): r for r in power_table(world, s, 1, "hit")}
    assert rows[("b",)]["prevent"] == {"alpha": 0.0, "beta": 1.0}
    assert rows[("a", "b")]["force"] == {"alpha": 1.0, "beta": 1.0}
    assert rows[()]["force"] == {"alpha": 0.0, "beta": 0.0}
    # a alone cannot guarantee a hit, but randomized play (value 1/2) might reach p=1/2.
    result = threshold(list(rows.values()), "force", 0.5)
    assert result["size"] == 2 and result["exact"] is False


@pytest.mark.parametrize("q", [0.0, 0.25, 0.5])
@pytest.mark.parametrize("rounds", [1, 2, 3])
def test_chance_and_blocking_match_closed_form(q, rounds):
    world = Push(q)
    s = world.initial_state()
    rows = {tuple(r["coalition"]): r for r in power_table(world, s, rounds, "collapsed")}
    guaranteed = 1 - (1 - q) ** rounds  # b blocks every round; a pushes every round
    assert rows[("a",)]["force"] == pytest.approx({"alpha": guaranteed, "beta": guaranteed})
    assert rows[("b",)]["force"] == {"alpha": 0.0, "beta": 0.0}  # a waits
    assert rows[("a", "b")]["force"] == {"alpha": 1.0, "beta": 1.0}
    assert rows[("b",)]["prevent"] == pytest.approx({"alpha": 1 - guaranteed, "beta": 1 - guaranteed})
    assert threshold(list(rows.values()), "force")["size"] == (1 if q == 1 else 2)


@pytest.mark.parametrize("rounds", [1, 3])
def test_non_target_terminal_ends_the_race(rounds):
    world = Push(0.25, leave=True)
    s = world.initial_state()
    rows = {tuple(r["coalition"]): r for r in power_table(world, s, rounds, "collapsed")}
    assert rows[("a",)]["force"] == {"alpha": 0.0, "beta": 0.0}
    assert rows[("b",)]["prevent"] == {"alpha": 1.0, "beta": 1.0}
    # With any terminal as target, leaving no longer protects; b falls back to blocking.
    assert force(world, s, ["a"], rounds, None) == pytest.approx(1 - 0.75 ** rounds)


def test_witness_names_first_actions_and_best_reply():
    world = Push(0.25)
    result = witness(world, world.initial_state(), ["a"], 2, "collapsed")
    assert result == {"value": pytest.approx(1 - 0.75 ** 2),
                      "actions": {"a": "push"}, "reply": {"b": "block"}}
    assert witness(world, world.initial_state(), ["b"], 2, "collapsed")["reply"] == {"a": "wait"}
    done = witness(world, {"t": 1, "end": "collapsed"}, ["a"], 2, "collapsed")
    assert done == {"value": 1.0, "actions": None, "reply": None}


def test_zero_rounds_and_terminal_states():
    world = Push(0.5)
    assert force(world, world.initial_state(), ["a", "b"], 0, "collapsed") == 0.0
    assert force(world, {"t": 1, "end": "collapsed"}, [], 0, "collapsed") == 1.0
    assert force(world, {"t": 1, "end": "escape"}, ["a", "b"], 3, "collapsed") == 0.0
    with pytest.raises(ValueError):
        force(world, world.initial_state(), ["z"], 1)
    with pytest.raises(ValueError):
        force(world, world.initial_state(), ["a"], -1)


def small_commons(**overrides):
    params = {**commons.DEFAULTS, "n": 3, **overrides}
    return commons.make(params, random.Random(0))


def at_stock(world, S):
    return {**world.initial_state(), "S": S}


@pytest.mark.parametrize("destination", ["stock", "sanctioners"])
@pytest.mark.parametrize("S", [8.0, 12.0, 30.0])
def test_commons_brackets_duality_and_monotonicity(destination, S):
    world = small_commons(confiscation_to=destination)
    from engine.power import row_for
    rows = power_table(world, at_stock(world, S), 2, "collapsed")
    for row in rows:
        f, p = row["force"], row["prevent"]
        assert f["alpha"] <= f["beta"] + 1e-12 and p["alpha"] <= p["beta"] + 1e-12
        for extra in set(world.by_id) - set(row["coalition"]):
            bigger = row_for(world, rows, set(row["coalition"]) | {extra})
            assert f["alpha"] <= bigger["force"]["alpha"] + 1e-12
            assert p["alpha"] <= bigger["prevent"]["alpha"] + 1e-12


def test_power_ignores_goals_horizons_beliefs_and_costs():
    reference = None
    for overrides in [{}, {"horizon": 1, "discount": 0.8}, {"k": 0, "search_depth": 1},
                      {"prior": "hi", "sanction_cost": 1.0}, {"horizon": 20, "prior": "ready"}]:
        world = small_commons(confiscation_to="stock", **overrides)
        table = power_table(world, at_stock(world, 10.0), 2, "collapsed")
        values = [(r["coalition"], r["force"], r["prevent"]) for r in table]
        reference = reference or values
        assert values == reference


def test_paid_sanctions_change_no_power_consistency_check():
    # Confiscation paid to sanctioners never returns resource to the stock.
    for S in (8.0, 12.0, 30.0):
        tables = []
        for sanction in (True, False):
            world = small_commons(confiscation_to="sanctioners", sanction=sanction)
            tables.append([(r["force"], r["prevent"]) for r in
                           power_table(world, at_stock(world, S), 2, "collapsed")])
        assert tables[0] == tables[1]


def test_commons_physical_projection_fixes_menus_kernel_and_terminal():
    world = small_commons(confiscation_to="stock")
    rng = random.Random(5)
    acts = [(commons.LO, False), (commons.HI, False), (commons.LO, True), (commons.HI, True)]
    for S in (6.0, 20.0, 50.0):
        base = at_stock(world, S)
        other = {**base, "last": {a.id: rng.choice(acts) for a in world.agents},
                 "value": {a.id: rng.random() for a in world.agents},
                 "wealth": {a.id: rng.random() * 10 for a in world.agents}}
        assert key(world.physical(base)) == key(world.physical(other))
        assert world.terminal(base) == world.terminal(other)
        for agent in world.agents:
            assert (world.actions(world.observe(base, agent), agent)
                    == world.actions(world.observe(other, agent), agent))
        for _ in range(10):
            joint = {a.id: rng.choice(acts) for a in world.agents}
            project = lambda state: [(p, key(world.physical(s))) for p, s in world.outcomes(state, joint)]
            assert project(base) == project(other)


def test_work_cap_is_unresolved_not_a_power_result():
    world = small_commons(confiscation_to="stock")
    state = at_stock(world, 10.0)
    with pytest.raises(PowerLimitExceeded):
        force(world, state, [], 2, "collapsed", budget=5)
    rows = power_table(world, state, 2, "collapsed", budget=5)
    assert any(r["force"]["alpha"] is None for r in rows)
    result = threshold(rows, "force")
    assert result["exact"] is False or result["size"] == 0


def test_cli_power_json_matches_library():
    import json
    from tests.test_records import cli
    completed = cli("--power", "1", "--json", "--fix", "n=2", "--target", "collapsed")
    assert completed.returncode == 0, completed.stderr
    data = json.loads(completed.stdout)
    assert data["mode"] == "power" and data["settings"]["target"] == ["collapsed"]
    world = commons.make({**commons.DEFAULTS, "n": 2}, random.Random(0))
    assert data["results"]["rows"] == power_table(world, world.initial_state(), 1, ["collapsed"])


@pytest.mark.parametrize("destination", ["stock", "sanctioners"])
@pytest.mark.parametrize("S", [6.0, 12.0, 20.0, 40.0])
def test_restraint_helps_only_prevention(destination, S):
    without = small_commons(confiscation_to=destination, restraint=False)
    with_rest = small_commons(confiscation_to=destination, restraint=True)
    a = power_table(without, at_stock(without, S), 2, "collapsed")
    b = power_table(with_rest, at_stock(with_rest, S), 2, "collapsed")
    for x, y in zip(a, b):
        assert y["force"]["alpha"] <= x["force"]["alpha"] + 1e-12
        assert y["prevent"]["alpha"] >= x["prevent"]["alpha"] - 1e-12
    everyone = [r for r in b if len(r["coalition"]) == 3][0]
    assert everyone["prevent"]["alpha"] == 1.0  # regrowth is positive on (0, K)


def test_profile_reports_power_before_each_played_round():
    from engine.power import profile
    world = Push(1.0)
    trace = [{"round": 1, "actions": {"a": "wait", "b": "block"}, "state": {"t": 1, "end": None}},
             {"round": 2, "actions": {"a": "push", "b": "block"}, "state": {"t": 2, "end": "collapsed"}}]
    result = profile(world, trace, 1, "collapsed")
    first, second = result["rounds"]
    # q=1: a alone forces collapse every round; b can never prevent it.
    assert first["thresholds"][0]["size"] == 1 and first["thresholds"][0]["witnesses"] == [["a"]]
    assert first["fragile"] and not first["sealed"] and second["actions"] == trace[1]["actions"]
    assert result["first_fragile"] == 1 and result["first_sealed"] is None


def test_cli_trace_profile_matches_library():
    import json
    from engine.power import profile
    from tests.test_records import cli
    completed = cli("--trace", "--rounds", "3", "--profile", "1", "--json", "--fix", "n=2",
                    "--target", "collapsed")
    assert completed.returncode == 0, completed.stderr
    record = json.loads(completed.stdout)["results"][0]
    world = commons.make(record["params"], random.Random(0))
    assert record["power_profile"] == profile(world, record["trace"], 1, ["collapsed"])
    assert cli("--profile", "2").returncode != 0  # requires --trace


class HiddenBit(Toy):
    # u hides a bit in round 1; g must match it in round 2 or the world ends in "hit".
    # g sees the bit only if the channel is verified.
    def __init__(self, verified):
        super().__init__({"verified": verified}, None)
        for i in ("u", "g"):
            self.add(Agent(i))

    def initial_state(self):
        return {"t": 0, "bit": None, "end": None}

    def observe(self, state, agent):
        if agent.id == "g" and not self.params["verified"]:
            return {k: v for k, v in state.items() if k != "bit"}
        return state

    def actions(self, observation, agent):
        if observation["t"] == 0:
            return [0, 1] if agent.id == "u" else ["wait"]
        return ["wait"] if agent.id == "u" else [0, 1]

    def outcomes(self, state, joint):
        if state["t"] == 0:
            return [(1.0, {"t": 1, "bit": joint["u"], "end": None})]
        return [(1.0, {"t": 2, "bit": state["bit"], "end": "safe" if joint["g"] == state["bit"] else "hit"})]


@pytest.mark.parametrize("verified", [False, True])
def test_sure_prevention_depends_on_what_the_coalition_sees(verified):
    from engine.power import sure
    world = HiddenBit(verified)
    s = world.initial_state()
    assert sure(world, s, ["g"], 2, "hit") is verified
    assert sure(world, s, ["g"], 2, "hit", informed=True) is True
    # Full-information power cannot see the channel at all.
    assert force(world, s, ["u"], 2, "hit") == 0.0
    assert sure(world, s, ["u"], 2, "hit", goal="reach") is False


@pytest.mark.parametrize("q", [0.0, 0.5, 1.0])
def test_sure_treats_chance_as_adversarial(q):
    from engine.power import sure
    world = Push(q)
    s = world.initial_state()
    assert sure(world, s, ["b"], 2, "collapsed") is (q == 0.0)
    assert sure(world, s, ["a"], 2, "collapsed", goal="reach") is (q == 1.0)
    assert sure(world, s, ["a", "b"], 2, "collapsed", goal="reach") is True
    assert sure(world, s, [], 2, "collapsed") is False  # nobody prevents; a pushes against idle


@pytest.mark.parametrize("S", [8.0, 20.0, 25.0, 30.0, 40.0])
def test_sure_matches_full_information_where_the_state_is_observed(S):
    from engine.power import sure
    world = small_commons(confiscation_to="sanctioners", restraint=True)
    state = at_stock(world, S)
    for row in power_table(world, state, 2, "collapsed"):
        guaranteed = row["prevent"]["alpha"] >= 1 - 1e-12  # paid: chance never moves the stock
        assert sure(world, state, row["coalition"], 2, "collapsed") is guaranteed
        assert sure(world, state, row["coalition"], 2, "collapsed", informed=True) is guaranteed


def test_sure_work_cap():
    from engine.power import sure
    world = small_commons()
    with pytest.raises(PowerLimitExceeded):
        sure(world, at_stock(world, 20.0), ["u0"], 3, "collapsed", budget=10)
