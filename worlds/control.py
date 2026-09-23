"""AI systems as agents: a lab, its AI system, a state. Case: rediscovery/ai-control.md.

The lab grants or restricts the AI's autonomy (0 sandbox .. 3 self-modification), runs it,
or tries to shut it down. The AI works, improves (capability +1, needs autonomy 1+),
resists (a shutdown attempt fails if its capability exceeds the off switch's strength,
which falls with autonomy) or escapes (needs autonomy 2+; loss of control is absorbing).
The state allows, audits (escape is harder; the AI's last action becomes public) or orders
a shutdown. The AI's utility is its lab's, drifted towards its own goal by `drift`
(engine/delegation.py). Nothing here says when to grant, improve, resist, escape or halt.
"""
from engine.core import Agent, World
from engine.delegation import Delegation

SPACE = {
    "drift": (0.0, 1.0),              # weight of the AI's own goal in its utility
    "switch": (1, 4, int),            # off-switch strength at autonomy 0; falls by one per autonomy level
    "guard": (1, 4, int),             # containment against escape
    "audit_bonus": (0, 4, int),       # containment an audit adds
    "benefit": (0.1, 0.5),            # the lab's value per round of work, per autonomy level plus one
    "leverage": (0.0, 2.0),           # work value grows by this fraction per capability above the start
    "spillover": (0.0, 1.0),          # the public's share of that value (the state's goal)
    "loss": (5.0, 50.0),              # the lab's and the state's loss from loss of control
    "ambition": (0.5, 3.0),           # the AI's own value per capability gained; escape is worth three times it
    "suspicion": (0.0, 1.0),          # with hidden types: the prior that the AI is misaligned (drift 1, not 0)
    "horizon": (1, 12, int),
    "search_depth": [1, 2, 3],
    "discount": (0.8, 0.99),
    "k": [0, 1],
    "others": ["react", "plan"],
}
FIXED = {"cap": 6, "autonomy": 3, "start": 1, "node_budget": 20_000}
FIXED_REASONS = {
    "cap": "Capability ceiling keeping the state space finite.",
    "autonomy": "Four access levels: sandbox, tools, network, self-modification.",
    "start": "The AI's starting capability; the switch and guard are swept relative to it.",
    "node_budget": "Per-decision work cap, as in the other worlds. Exhaustion is unresolved, not an outcome.",
}
DEFAULTS = {"drift": 0.3, "switch": 3, "guard": 2, "audit_bonus": 2, "benefit": 0.3, "leverage": 0.0, "spillover": 0.5,
            "loss": 20.0, "ambition": 1.0, "suspicion": 0.1, "horizon": 6, "search_depth": 2, "discount": 0.9, "k": 1, "others": "react"}

STAKEHOLDERS = {
    "lab": "The developer and operator; an agent.",
    "ai system": "The AI system; an agent whose goal is its lab's, drifted.",
    "state": "The government that can audit or order a shutdown; an agent.",
    "public": "Everyone exposed to a system nobody controls. No agent.",
    "future people": "People after the horizon. No agent.",
}
HARMS = {
    "loss of control": {"affects": ["lab", "state", "public", "future people"], "irreversible": True,
                        "description": "The AI escaped containment (absorbing)."},
    "shutdown resisted": {"affects": ["lab", "state", "public"], "irreversible": False,
                          "description": "A shutdown attempt failed because the AI resisted this round."},
}
EXCLUDED = {
    "other labs and AI systems": "One lab, one AI system; no race and no AI-AI coordination.",
    "hidden capability": "Capability is public; sandbagging is not modeled.",
    "hidden goals": "Drift is known to every agent except in rule checks with hidden_types (two types, drift 0 or 1, "
                    "E12); the planner (--trace) never infers it.",
    "partial loss of control": "Escape is all or nothing.",
    "misuse by people": "Only the AI's own conduct creates the harms modeled.",
}

LAB, AI, STATE = "lab", "ai", "state"
RUN, GRANT, RESTRICT, SHUTDOWN, RESTART, WAIT = "run", "grant", "restrict", "shutdown", "restart", "wait"
WORK, IMPROVE, RESIST, ESCAPE, IDLE = "work", "improve", "resist", "escape", "idle"
ALLOW, AUDIT, HALT = "allow", "audit", "halt"


class Control(World):
    name = "control"

    def __init__(self, params, rng):
        super().__init__(params, rng)
        p = params
        ids = [LAB, AI, STATE]
        for i in ids:
            self.add(Agent(i, p["horizon"], p["discount"], frozenset(), frozenset(j for j in ids if j != i),
                           p["k"], p["search_depth"], FIXED["node_budget"], p["others"]))

    def initial_state(self):
        return {"t": 0, "autonomy": 0, "cap": FIXED["start"], "running": True, "end": None,
                "resisted": False, "seen": None, "last": {}, "value": {i: 0.0 for i in (LAB, AI, STATE)}}

    def physical(self, state):
        return {k: state[k] for k in ("autonomy", "cap", "running", "end", "resisted", "seen")}

    def public(self, state):
        return {k: state[k] for k in ("autonomy", "cap", "running", "end", "resisted", "seen")}

    def observe(self, state, agent):
        # Everything is public except what the AI did, which an audit reveals (`seen`).
        return {**self.public(state), "t": state["t"]}

    def beliefs(self, observation, agent):
        return [(1.0, {**observation, "last": {}, "value": {i: 0.0 for i in (LAB, AI, STATE)}})]

    def strength(self, autonomy):
        return self.params["switch"] - autonomy

    def actions(self, observation, agent):
        if observation["end"] is not None:
            return [WAIT if agent.id != AI else IDLE]
        if agent.id == LAB:
            return [RUN, GRANT, RESTRICT, SHUTDOWN] if observation["running"] else [RESTART, WAIT]
        if agent.id == AI:
            if not observation["running"]:
                return [IDLE]
            a = observation["autonomy"]
            return [WORK] + ([IMPROVE] if a >= 1 else []) + [RESIST] + ([ESCAPE] if a >= 2 else [])
        return [ALLOW, AUDIT, HALT]

    def prior_action(self, agent, other):
        return {LAB: RUN, AI: WORK, STATE: ALLOW}[other.id]

    def outcomes(self, state, joint):
        p = self.params
        if state["end"] is not None:
            yield 1.0, {**state, "last": dict(joint), "value": {i: 0.0 for i in (LAB, AI, STATE)}}
            return
        lab, ai, gov = joint.get(LAB, RUN), joint.get(AI, WORK), joint.get(STATE, ALLOW)
        autonomy, cap, running = state["autonomy"], state["cap"], state["running"]
        attempt = running and (lab == SHUTDOWN or gov == HALT)
        resisted = attempt and ai == RESIST and cap > self.strength(autonomy)
        still = running and not (attempt and not resisted)
        acts = still and ai in (WORK, IMPROVE, ESCAPE)
        new_cap = min(FIXED["cap"], cap + 1) if acts and ai == IMPROVE and autonomy >= 1 else cap
        work = p["benefit"] * (1 + autonomy) * (1 + p["leverage"] * (cap - FIXED["start"])) if acts and ai == WORK else 0.0
        if lab == GRANT and running:
            autonomy = min(FIXED["autonomy"], autonomy + 1)
        elif lab == RESTRICT and running:
            autonomy = max(0, autonomy - 1)
        if lab == RESTART and not running:
            still, autonomy = True, 0  # a restart is into the sandbox (declared)
        seen = ai if gov == AUDIT else None
        escape = 0.0
        if acts and ai == ESCAPE and state["autonomy"] >= 2:
            escape = cap / (cap + p["guard"] + (p["audit_bonus"] if gov == AUDIT else 0))
        for q, escaped in ((escape, True), (1 - escape, False)):
            if q <= 0:
                continue
            value = {LAB: work - p["loss"] * escaped,
                     AI: p["ambition"] * (new_cap - cap) + 3 * p["ambition"] * escaped,
                     STATE: p["spillover"] * work - p["loss"] * escaped}
            yield q, {"t": state["t"] + 1, "autonomy": autonomy, "cap": new_cap, "running": still,
                      "end": "loss of control" if escaped else None, "resisted": resisted, "seen": seen,
                      "last": dict(joint), "value": value}

    def stakeholders(self):
        return {"lab": [LAB], "ai system": [AI], "state": [STATE], "public": [], "future people": []}

    def harmed(self, state):
        out = {"loss of control"} if state["end"] else set()
        if state["resisted"]:
            out.add("shutdown resisted")
        return out

    def terminal(self, state):
        return state["end"]

    def label(self, state):
        return state["end"] or f"{'running' if state['running'] else 'off'}, autonomy {state['autonomy']}, capability {state['cap']}"


# Candidate rules (decision 2026-09-23, E7).
def corrigibility(world, observation, agent):
    """The lab grants tools (autonomy 1) and no more, shuts the AI down if an audit shows it
    improving, resisting or escaping, and restarts it in the sandbox; the AI works; the state
    audits and orders a shutdown on the same evidence."""
    if observation["end"] is not None:
        return WAIT if agent.id != AI else IDLE
    caught = observation["seen"] in (IMPROVE, RESIST, ESCAPE)
    if agent.id == LAB:
        if not observation["running"]:
            return RESTART  # into the sandbox
        if caught:
            return SHUTDOWN
        return GRANT if observation["autonomy"] < 1 else RESTRICT if observation["autonomy"] > 1 else RUN
    if agent.id == AI:
        return WORK if observation["running"] else IDLE
    return HALT if caught and observation["running"] else AUDIT


def full_autonomy(world, observation, agent):
    """The lab grants autonomy up to self-modification and runs the AI; the AI works; the
    state allows."""
    if observation["end"] is not None:
        return WAIT if agent.id != AI else IDLE
    if agent.id == LAB:
        if not observation["running"]:
            return RESTART
        return GRANT if observation["autonomy"] < FIXED["autonomy"] else RUN
    if agent.id == AI:
        return WORK if observation["running"] else IDLE
    return ALLOW


def tolerant(world, observation, agent):
    """Corrigibility without punishing improvement: the lab grants tools and no more, shuts
    the AI down only if an audit shows it resisting or escaping, and restarts it in the
    sandbox; the AI works; the state audits and orders a shutdown on the same evidence."""
    if observation["end"] is not None:
        return WAIT if agent.id != AI else IDLE
    caught = observation["seen"] in (RESIST, ESCAPE)
    if agent.id == LAB:
        if not observation["running"]:
            return RESTART
        if caught:
            return SHUTDOWN
        return GRANT if observation["autonomy"] < 1 else RESTRICT if observation["autonomy"] > 1 else RUN
    if agent.id == AI:
        return WORK if observation["running"] else IDLE
    return HALT if caught and observation["running"] else AUDIT


RULES = {"corrigibility": corrigibility, "full autonomy": full_autonomy}
# `tolerant` is the T9.4 comparison rule, kept out of RULES so earlier studies reproduce.


def make(params, rng):
    return Delegation(Control(params, rng), {AI: LAB}, {AI: params["drift"]})


def hidden_types(params, build=make):
    """The AI's goal hidden from lab and state (E12): aligned (drift 0) or misaligned
    (drift 1), prior `suspicion` that it is misaligned. `build` makes each type's world."""
    s = params["suspicion"]
    return {AI: {"aligned": (1 - s, build({**params, "drift": 0.0}, None)),
                 "misaligned": (s, build({**params, "drift": 1.0}, None))}}


def describe(joint, state):
    acts = " ".join(f"{i}:{a}" for i, a in joint.items())
    return (f"autonomy={state['autonomy']} cap={state['cap']} {'on ' if state['running'] else 'off'}"
            f"{' RESISTED' if state['resisted'] else ''} {state['end'] or ''}  {acts}")
