"""A toy world for E16 grid tests: two agents push against a wall. Only `wall` matters to
power; `colour` is declared and moves nothing."""
from engine.core import Agent, World

SPACE = {"wall": (0, 3, int), "colour": ["red", "blue"], "reward": (0.0, 1.0)}
FIXED = {}
FIXED_REASONS = {}
DEFAULTS = {"wall": 1, "colour": "red", "reward": 0.5}
STAKEHOLDERS = {"a": "Agent.", "b": "Agent.", "town": "Behind the wall. No agent."}
HARMS = {"breach": {"affects": ["town"], "irreversible": True, "description": "Pressure above the wall."}}
EXCLUDED = {"everything else": "A toy."}


class Wall(World):
    name = "grid toy"

    def __init__(self, params, rng):
        super().__init__(params, rng)
        for i in ("a", "b"):
            self.add(Agent(i, 2, 1.0, frozenset(), frozenset({"a", "b"} - {i})))

    def initial_state(self):
        return {"t": 0, "pressure": 0, "end": None, "last": {}, "value": {"a": 0.0, "b": 0.0}}

    def observe(self, state, agent):
        return state

    def beliefs(self, observation, agent):
        return [(1.0, observation)]

    def actions(self, observation, agent):
        return ["wait"] if observation["end"] else ["wait", "push"]

    def prior_action(self, agent, other):
        return "wait"

    def outcomes(self, state, joint):
        pushes = 0 if state["end"] else sum(a == "push" for a in joint.values())
        pressure = state["pressure"] + pushes
        end = state["end"] or ("breached" if pressure > self.params["wall"] else None)
        value = {i: self.params["reward"] * (joint.get(i) == "push") for i in ("a", "b")}
        yield 1.0, {"t": state["t"] + 1, "pressure": pressure, "end": end, "last": dict(joint), "value": value}

    def stakeholders(self):
        return {"a": ["a"], "b": ["b"], "town": []}

    def harmed(self, state):
        return {"breach"} if state["end"] else set()

    def terminal(self, state):
        return state["end"]

    def label(self, state):
        return state["end"] or "standing"


def hold(world, observation, agent):
    """Nobody pushes."""
    return "wait"


RULES = {"hold": hold}


def make(params, rng):
    return Wall(params, rng)
