"""Arithmetic diagnostics from rediscovery/planner-audit.md, not empirical worlds.

Run with: python -m tests.planner_cases
Zero/one flags encode logic. Horizons are the shortest that distinguish the cases;
discount 1 removes discounting as a confound. Payoffs are named in each FIXED dict.
"""
import itertools
import json
import hashlib
from pathlib import Path

from engine.core import Agent, World, evaluate, plan
from engine.records import provenance


class DiagnosticWorld(World):
    """These fixtures declare their state known unless they override belief_state."""

    def __init__(self, params):
        super().__init__(params, None)

    def belief_state(self, state, agent):
        return state

    def terminal(self, state):
        return None

    def label(self, state):
        return "nonterminal"


class DirectedResponse(DiagnosticWorld):
    FIXED = {"gain": 1.0, "penalty": 3.0, "response_reward": 1.0,
             "wrong_response_cost": 1.0, "horizon": 2, "discount": 1.0}

    def __init__(self, actor_observes, responder_observes):
        super().__init__({**self.FIXED, "actor_observes": actor_observes,
                          "responder_observes": responder_observes})
        self.add(Agent("actor", horizon=self.params["horizon"], discount=1.0, k=1,
                       channels=frozenset({"responder"} if actor_observes else ())))
        self.add(Agent("responder", horizon=1, discount=1.0,
                       channels=frozenset({"actor"} if responder_observes else ())))

    def initial_state(self):
        return {"t": 0, "last": {"actor": "quiet", "responder": "ignore"},
                "value": {"actor": 0.0, "responder": 0.0}}

    def actions(self, state, agent):
        return ["quiet", "take"] if agent.id == "actor" else ["ignore", "respond"]

    def prior_action(self, agent, other):
        return "quiet" if other.id == "actor" else "ignore"

    def step(self, state, joint, rng=None):
        taking, responding = joint["actor"] == "take", joint["responder"] == "respond"
        actor = self.params["gain"] * taking - self.params["penalty"] * taking * responding
        responder = (self.params["response_reward"] if taking else
                     -self.params["wrong_response_cost"]) if responding else 0.0
        return {"t": state["t"] + 1, "last": dict(joint),
                "value": {"actor": actor, "responder": responder}}


class HiddenBit(DiagnosticWorld):
    FIXED = {"prior_bit": 0, "correct": 1.0, "incorrect": 0.0,
             "horizon": 1, "discount": 1.0}

    def __init__(self, secret, visible=False):
        super().__init__({**self.FIXED, "visible": visible})
        self.initial_secret = secret
        self.add(Agent("guesser", horizon=1, discount=1.0))

    def initial_state(self):
        return {"secret": self.initial_secret, "visible": self.params["visible"],
                "last": {}, "value": {"guesser": 0.0}}

    def belief_state(self, state, agent):
        # A declared point belief, not a distribution or Bayesian learning model.
        return {**state, "secret": state["secret"] if state["visible"] else self.params["prior_bit"]}

    def actions(self, state, agent):
        return [0, 1]

    def prior_action(self, agent, other):
        return self.params["prior_bit"]

    def step(self, state, joint, rng=None):
        value = self.params["correct"] if joint["guesser"] == state["secret"] else self.params["incorrect"]
        return {**state, "last": dict(joint), "value": {"guesser": value}}


class EqualActions(DiagnosticWorld):
    FIXED = {"payoff": 1.0, "horizon": 1, "discount": 1.0}

    def __init__(self, order=("left", "right")):
        super().__init__({**self.FIXED, "order": order})
        self.add(Agent("chooser", horizon=1, discount=1.0))

    def initial_state(self):
        return {"last": {"chooser": "right"}, "value": {"chooser": 0.0}, "beneficiary": None}

    def actions(self, state, agent):
        return list(self.params["order"])

    def prior_action(self, agent, other):
        return self.params["order"][0]

    def step(self, state, joint, rng=None):
        return {"last": dict(joint), "value": {"chooser": self.params["payoff"]},
                "beneficiary": joint["chooser"]}


class Investment(DiagnosticWorld):
    FIXED = {"consume": 1.0, "cost": 1.0, "return": 4.0, "horizon": 2, "discount": 1.0}

    def __init__(self, overrides=None):
        super().__init__({**self.FIXED, **(overrides or {})})
        self.add(Agent("investor", horizon=self.params["horizon"], discount=self.params["discount"]))

    def initial_state(self):
        return {"t": 0, "asset": False, "last": {}, "value": {"investor": 0.0}}

    def actions(self, state, agent):
        return ["consume", "invest"]

    def prior_action(self, agent, other):
        return "consume"

    def step(self, state, joint, rng=None):
        investing = joint["investor"] == "invest"
        reward = -self.params["cost"] if investing else self.params["return" if state["asset"] else "consume"]
        return {"t": state["t"] + 1, "asset": state["asset"] or investing,
                "last": dict(joint), "value": {"investor": reward}}

    def sequence_values(self):
        """Exact enumeration of this deterministic, two-action toy; not an engine planner."""
        actor = self.agents[0]
        rows = []
        for sequence in itertools.product(self.actions(self.initial_state(), actor), repeat=actor.horizon):
            state, total = self.initial_state(), 0.0
            for t, action in enumerate(sequence):
                state = self.step(state, {actor.id: action})
                total += actor.discount ** t * self.value(state, actor)
            rows.append({"actions": sequence, "value": total})
        return rows


class ThresholdRisk(DiagnosticWorld):
    FIXED = {"safe": 1.0, "upside": 2.0, "loss": -10.0, "low_stock": 3.0,
             "high_stock": 7.0, "threshold": 4.0, "low_probability": 0.5,
             "horizon": 1, "discount": 1.0}

    def __init__(self, overrides=None):
        super().__init__({**self.FIXED, **(overrides or {})})
        self.add(Agent("chooser", horizon=1, discount=1.0))

    def initial_state(self):
        return {"stock": self.params["high_stock"], "collapsed": False,
                "last": {}, "value": {"chooser": 0.0}}

    def actions(self, state, agent):
        return ["safe", "risky"]

    def prior_action(self, agent, other):
        return "safe"

    def at_stock(self, state, joint, stock):
        if state["collapsed"]:
            return {**state, "last": dict(joint), "value": {"chooser": 0.0}}
        safe = joint["chooser"] == "safe"
        collapsed = not safe and stock < self.params["threshold"]
        payoff = self.params["safe"] if safe else self.params["loss" if collapsed else "upside"]
        return {"stock": stock, "collapsed": collapsed, "last": dict(joint), "value": {"chooser": payoff}}

    def step(self, state, joint, rng=None):
        p = self.params["low_probability"]
        if joint["chooser"] == "safe":
            stock = state["stock"]
        elif rng is None:
            stock = p * self.params["low_stock"] + (1 - p) * self.params["high_stock"]
        else:
            stock = self.params["low_stock" if rng.random() < p else "high_stock"]
        return self.at_stock(state, joint, stock)

    def terminal(self, state):
        return "collapsed" if state["collapsed"] else None

    def exact_values(self):
        state, actor, p = self.initial_state(), self.agents[0], self.params["low_probability"]
        return {action: sum(probability * self.value(self.at_stock(state, {actor.id: action}, stock), actor)
                            for probability, stock in [(p, self.params["low_stock"]),
                                                       (1 - p, self.params["high_stock"])])
                for action in self.actions(state, actor)}


def inspect(world, state=None, actor=None):
    state = world.initial_state() if state is None else state
    actor = world.agents[0] if actor is None else actor
    return {"values": [{"action": action, "value": evaluate(world, state, actor, action, actor.k)}
                       for action in world.actions(state, actor)], "chosen": plan(world, state, actor)}


def audit():
    investment, risk = Investment(), ThresholdRisk()
    return {
        "directed": [{"actor_observes": a, "responder_observes": r,
                      **inspect(DirectedResponse(a, r))} for a, r in itertools.product((False, True), repeat=2)],
        "hidden": [{"secret": bit, "visible": visible, **inspect(HiddenBit(bit, visible))}
                   for visible, bit in itertools.product((False, True), (0, 1))],
        "ties": [{"order": order, **inspect(EqualActions(order))}
                 for order in [("left", "right"), ("right", "left")]],
        "investment": {**inspect(investment), "sequences": investment.sequence_values(),
                       "after_invest": inspect(investment, investment.step(investment.initial_state(), {"investor": "invest"}))},
        "threshold": {**inspect(risk), "exact_values": risk.exact_values()},
        "fixed": {cls.__name__: cls.FIXED for cls in
                  (DirectedResponse, HiddenBit, EqualActions, Investment, ThresholdRisk)},
    }


if __name__ == "__main__":
    print(json.dumps({"schema_version": 1, "kind": "planner-audit", "provenance": provenance(),
                      "fixture_sha256": hashlib.sha256(Path(__file__).read_text(encoding="utf-8").encode()).hexdigest(),
                      "cases": audit()}, indent=2, sort_keys=True))
