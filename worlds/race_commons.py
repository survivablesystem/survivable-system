"""An arms race on a shared fishery: the treaty world and the commons as one system.

Two governments, east and west, race (treaty part) and harvest (commons part); fishers
only harvest. Building capability draws on the fish stock everyone shares. The coupling
is the authored interface (decision 2026-09-23, E4): each build removes `draw` low takes
of a three-harvester fishery from the stock after both parts have run, an absolute
amount however many fish; building does not require stock. Fishers are exchangeable
(E2 step 2). Nothing says when to build, harvest or strike.
"""
from engine.compose import Composite, part_harms
from worlds import commons, treaty

PARTS = {"commons": commons, "treaty": treaty}
PLANNING = ("horizon", "search_depth", "discount", "k", "others")
PART_FIXED = {"commons": {"n": None}, "treaty": {}}  # commons n is 2 + fishers

SPACE = {"draw": (0.0, 3.0),  # stock removed per build, in low takes of a three-harvester fishery
         "fishers": (1, 10, int),  # harvesters that do not race
         **{k: v for k, v in commons.SPACE.items() if k in PLANNING}}
for _part, _module in PARTS.items():
    for _k, _v in _module.SPACE.items():
        if _k not in PLANNING and _k not in PART_FIXED[_part]:
            SPACE[f"{_part}.{_k}"] = _v
FIXED = {"node_budget": 20_000}
FIXED_REASONS = {"node_budget": "Per-decision work cap for the composite planner; exhaustion is unresolved."}
DEFAULTS = {"draw": 1.0, "fishers": 1, "horizon": 6, "search_depth": 2, "discount": 0.9, "k": 1, "others": "react",
            **{f"commons.{k}": v for k, v in commons.DEFAULTS.items() if k not in PLANNING and k != "n"},
            **{f"treaty.{k}": v for k, v in treaty.DEFAULTS.items() if k not in PLANNING}}
DEFAULTS["commons.sanction"] = False  # smaller menus keep exact queries tractable; swept

STAKEHOLDER_MAP = {
    "harvesters": [("commons", "users")],
    "future users": [("commons", "future users")],
    "stock-dependent others": [("commons", "stock-dependent others")],
    "east government": [("treaty", "party a")],
    "west government": [("treaty", "party b")],
    "population of east": [("treaty", "population of a")],
    "population of west": [("treaty", "population of b")],
}
STAKEHOLDERS = {
    "harvesters": "East, west and the fishers as harvesters; agents.",
    "future users": "People who would harvest after the horizon. No agent.",
    "stock-dependent others": "Nonhuman life and non-harvesting people that depend on the stock. No agent.",
    "east government": "East as a racing party; agent.",
    "west government": "West as a racing party; agent.",
    "population of east": "People governed by east. No agent.",
    "population of west": "People governed by west. No agent.",
}
HARMS = part_harms(PARTS, STAKEHOLDER_MAP)
COVERS = {"treaty: third states": "The fishers are third parties sharing the stock the race draws on."}
EXCLUDED = {
    **{f"commons: {k}": v for k, v in commons.EXCLUDED.items()},
    "treaty: harm from use": treaty.EXCLUDED["harm from use"],
    "treaty: future generations": treaty.EXCLUDED["future generations"],
    "other third-state spillovers": "Only the shared stock links the race to anyone outside it.",
    "stock as an input to building": "Building draws on the stock but does not require it; an exhausted stock does not stop the race.",
    "populations as harvesters": "Populations bear disarmament; their dependence on the fishery beyond their governments' yield is not modeled.",
}


def members(fishers):
    names = ["fisher"] + [f"fisher{i}" for i in range(2, fishers + 1)]
    return {"commons": {"u0": "east", "u1": "west", **{f"u{i + 2}": f for i, f in enumerate(names)}},
            "treaty": {"a": "east", "b": "west"}}


def couple(world, draw):
    common = world.parts["commons"]
    lo_ref = common.lo * len(common.agents) / 3  # low take of a three-harvester fishery

    def apply(state, joint):
        parts = dict(state["parts"])
        stock = dict(parts["commons"])
        builds = sum(treaty.parse(joint[actor]["treaty"])[0] == treaty.BUILD for actor in ("east", "west"))
        if builds and not stock["collapsed"]:
            stock["S"] = max(0.0, stock["S"] - builds * draw * lo_ref)
            if stock["S"] < common.S_min:
                stock["S"], stock["collapsed"] = 0.0, True
        parts["commons"] = stock
        return {"parts": parts}
    return apply


def make(params, rng):
    fixed = {"commons": {"n": 2 + params["fishers"]}, "treaty": {}}
    part_params = {p: {**{k: params[k] for k in PLANNING}, **fixed[p],
                       **{k.split(".", 1)[1]: v for k, v in params.items() if k.startswith(p + ".")}}
                   for p in PARTS}
    parts = {p: PARTS[p].make(part_params[p], rng) for p in PARTS}
    planning = {k: params[k] for k in PLANNING}
    planning["node_budget"] = FIXED["node_budget"]
    world = Composite(params, rng, parts, members(params["fishers"]), planning=planning,
                      stakeholders=STAKEHOLDER_MAP, couple_reads=("east", "west"))
    world.name = "race_commons"
    world.couple = couple(world, params["draw"])
    return world


def describe(joint, state):
    c, t = state["parts"]["commons"], state["parts"]["treaty"]
    acts = " ".join(f"{a}:{'/'.join(str(x[0]) if isinstance(x, (list, tuple)) else str(x) for x in joint[a].values())}"
                    for a in joint)
    return f"S={c['S']:5.1f} cap e={t['cap']['a']} w={t['cap']['b']}  {acts}"
