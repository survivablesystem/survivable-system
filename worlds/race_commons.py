"""An arms race on a shared fishery: the treaty world and the commons as one system.

Two governments, east and west, race (treaty part) and harvest (commons part); a third
harvester, the fisher, only harvests. Building capability draws on the fish stock
everyone shares. The coupling is the authored interface (decision 2026-09-23, E4):
each build removes `draw` low takes from the stock after both parts have run; building
does not require stock. Nothing says when to build, harvest or strike.
"""
from engine.compose import Composite, part_harms
from worlds import commons, treaty

PARTS = {"commons": commons, "treaty": treaty}
MEMBERS = {"commons": {"u0": "east", "u1": "west", "u2": "fisher"},
           "treaty": {"a": "east", "b": "west"}}
PLANNING = ("horizon", "search_depth", "discount", "k", "others")
PART_FIXED = {"commons": {"n": 3}, "treaty": {}}

SPACE = {"draw": (0.0, 3.0),  # stock removed per build, in low takes
         **{k: v for k, v in commons.SPACE.items() if k in PLANNING}}
for _part, _module in PARTS.items():
    for _k, _v in _module.SPACE.items():
        if _k not in PLANNING and _k not in PART_FIXED[_part]:
            SPACE[f"{_part}.{_k}"] = _v
FIXED = {"commons.n": 3, "node_budget": 20_000}
FIXED_REASONS = {"commons.n": "East, west and one fisher: the smallest whole with a bystander. Exact search is exponential in actors.",
                 "node_budget": "Per-decision work cap for the composite planner; exhaustion is unresolved."}
DEFAULTS = {"draw": 1.0, "horizon": 6, "search_depth": 2, "discount": 0.9, "k": 1, "others": "react",
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
    "harvesters": "East, west and the fisher as harvesters; agents.",
    "future users": "People who would harvest after the horizon. No agent.",
    "stock-dependent others": "Nonhuman life and non-harvesting people that depend on the stock. No agent.",
    "east government": "East as a racing party; agent.",
    "west government": "West as a racing party; agent.",
    "population of east": "People governed by east. No agent.",
    "population of west": "People governed by west. No agent.",
}
HARMS = part_harms(PARTS, STAKEHOLDER_MAP)
COVERS = {"treaty: third states": "The fisher is a third party sharing the stock the race draws on."}
EXCLUDED = {
    **{f"commons: {k}": v for k, v in commons.EXCLUDED.items()},
    "treaty: harm from use": treaty.EXCLUDED["harm from use"],
    "treaty: future generations": treaty.EXCLUDED["future generations"],
    "other third-state spillovers": "Only the shared stock links the race to anyone outside it.",
    "stock as an input to building": "Building draws on the stock but does not require it; an exhausted stock does not stop the race.",
    "populations as harvesters": "Populations bear disarmament; their dependence on the fishery beyond their governments' yield is not modeled.",
}


def couple(world, draw):
    common = world.parts["commons"]

    def apply(state, joint):
        parts = dict(state["parts"])
        stock = dict(parts["commons"])
        builds = sum(treaty.parse(joint[actor]["treaty"])[0] == treaty.BUILD for actor in ("east", "west"))
        if builds and not stock["collapsed"]:
            stock["S"] = max(0.0, stock["S"] - builds * draw * common.lo)
            if stock["S"] < common.S_min:
                stock["S"], stock["collapsed"] = 0.0, True
        parts["commons"] = stock
        return {"parts": parts}
    return apply


def make(params, rng):
    part_params = {p: {**{k: params[k] for k in PLANNING}, **PART_FIXED[p],
                       **{k.split(".", 1)[1]: v for k, v in params.items() if k.startswith(p + ".")}}
                   for p in PARTS}
    parts = {p: PARTS[p].make(part_params[p], rng) for p in PARTS}
    planning = {k: params[k] for k in PLANNING}
    planning["node_budget"] = FIXED["node_budget"]
    world = Composite(params, rng, parts, MEMBERS, planning=planning, stakeholders=STAKEHOLDER_MAP)
    world.name = "race_commons"
    world.couple = couple(world, params["draw"])
    return world


def describe(joint, state):
    c, t = state["parts"]["commons"], state["parts"]["treaty"]
    acts = " ".join(f"{a}:{'/'.join(str(x[0]) if isinstance(x, (list, tuple)) else str(x) for x in joint[a].values())}"
                    for a in joint)
    return f"S={c['S']:5.1f} cap e={t['cap']['a']} w={t['cap']['b']}  {acts}"
