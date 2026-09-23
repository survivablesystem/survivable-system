"""Qualitative expectations from rediscovery/open-commons.md, over several seeds.

Thresholds are generous on purpose. These are regressions at specified configurations,
not proof of historical mechanisms or parameter robustness. If an expectation fails,
diagnose it and record the finding; do not tune the model until it passes.
"""
import random

import pytest

from engine.core import action_values, run
from engine.records import run_record
from worlds import commons

BASELINE = commons.DEFAULTS
SEEDS = 4
ROUNDS = 30


def survival_share(overrides, seeds=SEEDS, rounds=ROUNDS):
    labels = []
    for s in range(seeds):
        params = {**BASELINE, **overrides}
        world = commons.make(params, random.Random(s))
        labels.append(run(world, rounds, world.rng)[0])
    return labels.count("survived") / len(labels)


def test_old_favorable_baseline_now_collapses():
    # T1.3: adaptive plans and branch-weighted payoffs produce a depleting cycle.
    # Preserve the contrary finding; no mechanism was tuned to restore survival.
    assert survival_share({}) <= 0.25


def test_baseline_depletion_cycle_has_computed_choices():
    world = commons.make(BASELINE, random.Random(0))
    state = world.initial_state()
    expected = [(commons.HI, False), (commons.LO, True), (commons.LO, False)]
    for action in expected:
        for actor in world.agents:
            values = action_values(world, state, actor)
            assert dict(values)[action] == max(value for _, value in values)
        state = world.step(state, {a.id: action for a in world.agents}, world.rng)
    assert state["S"] < world.initial_state()["S"]


def test_no_channels_collapses():
    assert survival_share({"channels": "none"}) <= 0.25


def test_no_sanction_capability_collapses():
    assert survival_share({"sanction": False}) <= 0.25


def test_channels_alone_are_not_enough():
    # detection without response
    assert survival_share({"sanction": False, "channels": "all"}) <= 0.25


def test_sanction_alone_is_not_enough():
    # response without detection
    assert survival_share({"sanction": True, "channels": "none"}) <= 0.25


def test_short_horizon_collapses():
    assert survival_share({"horizon": 1}) <= 0.25


def test_unpaid_sanctioning_collapses():
    # Scoped unpaid-sanction control; no universal free-riding claim.
    assert survival_share({"confiscation_to": "stock"}) <= 0.25


def test_larger_exact_search_is_unresolved_not_a_size_finding():
    for seed in range(SEEDS):
        record = run_record(commons.make, {**BASELINE, "n": 10}, ROUNDS, seed)
        assert record["status"] == "search_limit"
        assert record["label"] is None and record["terminal"] is None


def test_level0_beliefs_cannot_hold_a_norm():
    # Duration matters: this configuration survives 12 rounds, but not 30.
    assert survival_share({"k": 0}) <= 0.25


@pytest.mark.parametrize("destination", ["stock", "sanctioners"])
def test_contest_kernel_matches_independent_bernoulli_arithmetic(destination):
    world = commons.make({**BASELINE, "n": 6, "confiscation_to": destination}, random.Random(0))
    joint = {a.id: (commons.LO, True) if i < 2 else (commons.HI, False)
             for i, a in enumerate(world.agents)}
    state = world.initial_state()
    outcomes = list(world.outcomes(state, joint))
    # Two sanctioners per target: p=2/3. Four independent targets -> 16 branches.
    assert len(outcomes) == 16 and sum(p for p, _ in outcomes) == pytest.approx(1)
    assert state == world.initial_state()  # enumeration is pure
    means = {a.id: sum(p * s["value"][a.id] for p, s in outcomes) for a in world.agents}
    assert means["u2"] == pytest.approx(world.hi / 3)
    bounty = 4 * world.hi * (2 / 3) / 2 if destination == "sanctioners" else 0
    assert means["u0"] == pytest.approx(world.lo - 4 * world.cost + bounty)
    stock = state["S"] + BASELINE["r"] * state["S"] * (1 - state["S"] / world.K)
    stock -= 2 * world.lo + 4 * world.hi
    if destination == "stock":
        stock += 4 * world.hi * (2 / 3)
    assert sum(p * s["S"] for p, s in outcomes) == pytest.approx(stock)


def test_rest_takes_nothing_and_cannot_sanction():
    world = commons.make({**BASELINE, "restraint": True}, random.Random(0))
    state = world.initial_state()
    menu = world.actions(world.observe(state, world.agents[0]), world.agents[0])
    assert (commons.REST, False) in menu and (commons.REST, True) not in menu
    joint = {a.id: (commons.REST, False) for a in world.agents}
    [(p, after)] = list(world.outcomes(state, joint))
    grown = state["S"] + BASELINE["r"] * state["S"] * (1 - state["S"] / world.K)
    assert p == 1.0 and after["S"] == pytest.approx(grown)
    assert all(v == 0.0 for v in after["value"].values())
    base = commons.make({**BASELINE, "restraint": False}, random.Random(0))
    assert (commons.REST, False) not in base.actions(base.observe(state, base.agents[0]), base.agents[0])
