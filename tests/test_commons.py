"""Qualitative expectations from rediscovery/open-commons.md, over several seeds.

Thresholds are generous on purpose. A test that only passes at one parameter point
would be a scripted outcome. If an expectation fails, the case file gets the finding;
the test is not tuned until it passes.
"""
import random

from engine.core import run
from worlds import commons

FAVORABLE = commons.DEFAULTS
SEEDS = 4
ROUNDS = 30


def sustained_share(overrides, seeds=SEEDS, rounds=ROUNDS):
    labels = []
    for s in range(seeds):
        params = {**FAVORABLE, **overrides}
        world = commons.make(params, random.Random(s))
        labels.append(run(world, rounds, world.rng)[0])
    return labels.count("sustained") / len(labels)


def test_favorable_conditions_sustain():
    assert sustained_share({}) >= 0.75


def test_no_channels_collapses():
    assert sustained_share({"channels": "none"}) <= 0.25


def test_no_sanction_capability_collapses():
    assert sustained_share({"sanction": False}) <= 0.25


def test_channels_alone_are_not_enough():
    # detection without response
    assert sustained_share({"sanction": False, "channels": "all"}) <= 0.25


def test_sanction_alone_is_not_enough():
    # response without detection
    assert sustained_share({"sanction": True, "channels": "none"}) <= 0.25


def test_short_horizon_collapses():
    assert sustained_share({"horizon": 1}) <= 0.25


def test_unpaid_sanctioning_collapses():
    # second-order free riding: a sanction whose only benefit is the shared stock is
    # never worth its cost to the sanctioner within its horizon, so nobody sanctions
    assert sustained_share({"confiscation_to": "stock"}) <= 0.25


def test_group_size_does_not_matter_when_sanctioning_pays():
    # engine finding against the paper case: with full observability and paid
    # sanctioning, ten users sustain as well as four. Size bites through channels.
    assert sustained_share({"n": 10}) >= 0.75


def test_level0_beliefs_cannot_hold_a_norm():
    # engine finding: with level-0 beliefs nobody expects a sanction before one has
    # happened, so everyone defects at once and there is never a target to sanction
    assert sustained_share({"k": 0}) <= 0.25
