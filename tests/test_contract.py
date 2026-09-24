"""The world contract, checked on every module in worlds/ (AGENTS.md "Adding a world").

A new world is picked up automatically; one that leaves a declaration out fails here. The
physical contract (states with equal `physical` have equal menus, harms and terminal status)
is what memoized power queries and the E14 kernel rely on; it is checked on reachable states.
None of this validates a model; it catches holes in its declarations.
"""
import importlib
import pkgutil
import random
from itertools import product

import pytest

import worlds
from engine.core import continuation_violations, distribution, key
from engine.power import symmetry_violations

MODULES = [importlib.import_module(f"worlds.{m.name}") for m in pkgutil.iter_modules(worlds.__path__)]
REQUIRED = ("SPACE", "FIXED", "FIXED_REASONS", "DEFAULTS", "STAKEHOLDERS", "HARMS", "EXCLUDED", "make", "describe")


def ids(module):
    return module.__name__.split(".")[-1]


def build(module, params=None):
    return module.make(dict(params or module.DEFAULTS), random.Random(0))


def reachable(world, rounds=2, per_state=6, cap=40, seed=0):
    """States reached from the start by sampled joints (every menu entry appears in some joint)."""
    rng = random.Random(seed)
    frontier, seen = [world.initial_state()], {}
    seen[key(world.physical(frontier[0]))] = frontier[0]
    for _ in range(rounds):
        nxt = []
        for s in frontier:
            if world.terminal(s) is not None:
                continue
            menus = [world.actions(world.observe(s, a), a) for a in world.agents]
            joints = [[rng.choice(m) for m in menus] for _ in range(per_state)]
            joints += [[m[min(i, len(m) - 1)] for m in menus] for i in range(max(map(len, menus)))]
            for choice in joints:
                for _, s2 in distribution(world.outcomes(s, {a.id: c for a, c in zip(world.agents, choice)})):
                    k = key(world.physical(s2))
                    if k not in seen and len(seen) < cap:
                        seen[k] = s2
                        nxt.append(s2)
        frontier = nxt
    return list(seen.values())


def within(spec, value):
    if isinstance(spec, list):
        return value in spec
    if isinstance(spec, tuple) and len(spec) == 3 and spec[2] is int:
        return isinstance(value, int) and spec[0] <= value <= spec[1]
    if isinstance(spec, tuple) and len(spec) == 2:
        return spec[0] <= value <= spec[1]
    return True


@pytest.mark.parametrize("module", MODULES, ids=ids)
def test_register_is_declared_and_defaults_lie_in_it(module):
    missing = [name for name in REQUIRED if not hasattr(module, name)]
    assert not missing, f"{module.__name__} does not declare {missing}"
    assert set(module.DEFAULTS) == set(module.SPACE)
    assert set(module.FIXED) == set(module.FIXED_REASONS) and all(module.FIXED_REASONS.values())
    outside = {k: v for k, v in module.DEFAULTS.items() if not within(module.SPACE[k], v)}
    assert not outside, f"defaults outside the register: {outside}"


@pytest.mark.parametrize("module", MODULES, ids=ids)
def test_stakeholders_harms_and_exclusions_are_consistent(module):
    world = build(module)
    assert set(world.stakeholders()) == set(module.STAKEHOLDERS)
    assert all(set(ids_) <= {a.id for a in world.agents} for ids_ in world.stakeholders().values())
    for harm, spec in module.HARMS.items():
        assert set(spec["affects"]) <= set(module.STAKEHOLDERS), harm
        assert "irreversible" in spec and spec.get("description"), harm
    assert module.EXCLUDED and all(module.EXCLUDED.values())
    # a harm nobody could name the people of would be a hole: every harm falls on someone
    assert all(spec["affects"] for spec in module.HARMS.values())


@pytest.mark.parametrize("module", MODULES, ids=ids)
def test_kernel_menus_and_harms_on_reachable_states(module):
    world = build(module)
    for s in reachable(world):
        assert set(world.harmed(s)) <= set(module.HARMS)
        key(s)  # JSON-compatible
        for a in world.agents:
            menu = world.actions(world.observe(s, a), a)
            assert menu, f"{a.id} has an empty menu"
            key(menu)


@pytest.mark.parametrize("module", MODULES, ids=ids)
def test_physical_fixes_menus_harms_and_terminal_status(module):
    """What power memoization and the E14 kernel assume: states that agree on `physical`
    agree on menus, declared harms and terminal status. Pairs are reached by different paths."""
    world = build(module)
    classes = {}
    for seed in range(3):
        for s in reachable(world, seed=seed):
            classes.setdefault(key(world.physical(s)), []).append(s)
    for states in classes.values():
        first = states[0]
        for other in states[1:]:
            assert world.terminal(other) == world.terminal(first)
            assert set(world.harmed(other)) == set(world.harmed(first))
            for a in world.agents:
                assert key(world.actions(world.observe(other, a), a)) == key(world.actions(world.observe(first, a), a))


@pytest.mark.parametrize("module", MODULES, ids=ids)
def test_declared_symmetry_and_continuation_hold_on_reachable_states(module):
    world = build(module)
    states = reachable(world, cap=12)
    assert symmetry_violations(world, states, random.Random(1), samples=5) == []
    assert continuation_violations(world, states[:6], random.Random(1), samples=3) == []


@pytest.mark.parametrize("module", [m for m in MODULES if getattr(m, "RULES", None)], ids=ids)
def test_rules_prescribe_menu_actions_on_reachable_states(module):
    world = build(module)
    for s in reachable(world, cap=15):
        if world.terminal(s) is not None:
            continue
        for name, rule in module.RULES.items():
            for a in world.agents:
                observation = world.observe(s, a)
                assert key(rule(world, observation, a)) in {key(x) for x in world.actions(observation, a)}, (name, a.id)


@pytest.mark.parametrize("module", [m for m in MODULES if hasattr(m, "hidden_types")], ids=ids)
def test_hidden_types_differ_only_in_the_hidden_agents_goals(module):
    params = dict(module.DEFAULTS)
    world = build(module, params)
    for agent, types in module.hidden_types(params).items():
        assert abs(sum(p for p, _ in types.values()) - 1.0) < 1e-9
        others = [a.id for a in world.agents if a.id != agent]
        for s in reachable(world, cap=10):
            if world.terminal(s) is not None:
                continue
            menus = [world.actions(world.observe(s, a), a) for a in world.agents]
            for choice in list(product(*menus))[:20]:
                joint = {a.id: c for a, c in zip(world.agents, choice)}
                base = [(p, key(world.physical(x)), {i: x["value"][i] for i in others})
                        for p, x in distribution(world.outcomes(s, joint))]
                for _, typed in types.values():
                    if typed is None:
                        continue
                    got = [(p, key(typed.physical(x)), {i: x["value"][i] for i in others})
                           for p, x in distribution(typed.outcomes(s, joint))]
                    assert got == base
