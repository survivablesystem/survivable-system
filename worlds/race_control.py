"""The race and the off switch: the frontier race and the AI control world as one system.

Lab A races lab B (frontier part) and runs an AI system it may shut down (control part);
one state oversees both. The coupling is the authored interface (decisions 2026-09-23, E4
and its amendment): with `coupled`, lab A's AI is its model in the race, so after both
parts run, lab A's race capability is at least its starting capability plus what its AI
gained (capped). Scaling in the race adds other capability (compute, products) and does not
raise the AI's. Nothing says who skips a shutdown, grants autonomy, deploys or halts.
Case: rediscovery/race-control.md.
"""
from engine.compose import Composite, lift_rules, part_harms
from worlds import control, frontier

PARTS = {"frontier": frontier, "control": control}
PLANNING = ("horizon", "search_depth", "discount", "k", "others")

SPACE = {"coupled": [False, True],  # lab A's race capability has its AI's gains as a floor
         **{k: v for k, v in frontier.SPACE.items() if k in PLANNING}}
for _part, _module in PARTS.items():
    for _k, _v in _module.SPACE.items():
        if _k not in PLANNING:
            SPACE[f"{_part}.{_k}"] = _v
FIXED = {"node_budget": 20_000}
FIXED_REASONS = {"node_budget": "Per-decision work cap for the composite planner; exhaustion is unresolved."}
DEFAULTS = {"coupled": True, "horizon": 4, "search_depth": 2, "discount": 0.9, "k": 1, "others": "react",
            **{f"frontier.{k}": v for k, v in frontier.DEFAULTS.items() if k not in PLANNING},
            **{f"control.{k}": v for k, v in control.DEFAULTS.items() if k not in PLANNING}}

MEMBERS = {"frontier": {"l0": "lab A", "l1": "lab B", "evaluator": "evaluator", "state": "state"},
           "control": {"lab": "lab A", "ai": "AI", "state": "state"}}
STAKEHOLDER_MAP = {
    "labs": [("frontier", "labs"), ("control", "lab")],
    "AI system": [("control", "ai system")],
    "evaluator": [("frontier", "evaluator")],
    "state": [("frontier", "state"), ("control", "state")],
    "public": [("frontier", "public"), ("control", "public")],
    "users": [("frontier", "users")],
    "future people": [("frontier", "future people"), ("control", "future people")],
}
STAKEHOLDERS = {
    "labs": "Lab A (races and runs the AI) and lab B (races); agents.",
    "AI system": "Lab A's AI system; an agent whose goal is lab A's, drifted.",
    "evaluator": "Third-party evaluator of both labs; an agent.",
    "state": "One government overseeing the race and the AI; an agent.",
    "public": "Everyone exposed to a catastrophe or to a system nobody controls. No agent.",
    "users": "People who would use a deployed system. No agent.",
    "future people": "People after the horizon. No agent.",
}
HARMS = part_harms(PARTS, STAKEHOLDER_MAP)
COVERS = {"frontier: AI systems as agents": "Lab A's AI is an agent in the control part."}
EXCLUDED = {
    **{f"control: {k}": v for k, v in control.EXCLUDED.items()},
    **{f"frontier: {k}": v for k, v in frontier.EXCLUDED.items() if k != "AI systems as agents"},
    "lab B's AI": "Lab B's model is a capability stock; only lab A's AI is an agent.",
    "feedback from the race to the AI": "Race scaling does not raise the AI's capability; only the AI's gains carry into the race.",
    "the AI in the race": "The AI acts only through its capability; it cannot deploy, lobby or act on lab B.",
}


def couple(world):
    start = frontier.FIXED["base"] + world.parts["frontier"].params["lead"] - control.FIXED["start"]

    def apply(state, joint):
        parts = dict(state["parts"])
        race = dict(parts["frontier"])
        cap = dict(race["cap"])
        cap["l0"] = min(frontier.FIXED["cap"], max(cap["l0"], start + parts["control"]["cap"]))
        race["cap"] = cap
        parts["frontier"] = race
        return {"parts": parts}
    return apply


def make(params, rng):
    part_params = {p: {**{k: params[k] for k in PLANNING},
                       **{k.split(".", 1)[1]: v for k, v in params.items() if k.startswith(p + ".")}}
                   for p in PARTS}
    parts = {p: PARTS[p].make(part_params[p], rng) for p in PARTS}
    planning = {k: params[k] for k in PLANNING}
    planning["node_budget"] = FIXED["node_budget"]
    world = Composite(params, rng, parts, MEMBERS, planning=planning, stakeholders=STAKEHOLDER_MAP,
                      couple_reads=("lab A", "AI"))
    world.name = "race_control"
    if params["coupled"]:
        world.couple = couple(world)
    return world


RULES = {
    "licensing + corrigibility": lift_rules({"frontier": frontier.licensing, "control": control.corrigibility}),
    "race + full autonomy": lift_rules({"frontier": frontier.race, "control": control.full_autonomy}),
    "race + corrigibility": lift_rules({"frontier": frontier.race, "control": control.corrigibility}),
}


def describe(joint, state):
    f, c = state["parts"]["frontier"], state["parts"]["control"]
    labs = " ".join(f"{l}={f['cap'][l]}/{f['safe'][l]}{'D' if f['deployed'][l] else ''}" for l in frontier.LABS)
    acts = " ".join(f"{a}:{'/'.join(str(x) for x in joint[a].values())}" for a in joint)
    return (f"[{labs}] AI cap={c['cap']} autonomy={c['autonomy']} {'on' if c['running'] else 'off'}"
            f"{' RESISTED' if c['resisted'] else ''} {f['end'] or ''}{c['end'] or ''}  {acts}")
