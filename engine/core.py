"""Survivable System engine, v0.

Implements the parts of spec/PRIMITIVES.md marked implemented there. A World defines
state, available actions, dynamics and per-round goal values. The engine supplies what
no world may supply for itself: the planner, the run loop, and (in sweep.py) the sweep.

No behavior is scripted. Each round every agent evaluates each available action by
rolling the world forward over its horizon under its beliefs about the others, and takes
the action with the best discounted goal.

Beliefs are level-k, and k is a swept assumption:
  k = 0  an observed agent repeats its last action; an unobserved one takes the prior.
  k = 1  agents that observe this agent are modeled as level-0 planners: after one
         simulated step they pick a response and hold it, including one-way observers.
         Others repeat their last observed action or take the prior.
These are restricted, constant-action rollouts from an explicit subjective state,
not optimal adaptive policies or distributions over possible trajectories.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Agent:
    id: str
    horizon: int = 10           # rounds it plans over
    discount: float = 0.9       # per-round discount on goal value
    capabilities: frozenset = frozenset()
    channels: frozenset = frozenset()   # ids of agents this one observes
    k: int = 0                  # belief level, see module docstring

    def can(self, capability: str) -> bool:
        return capability in self.capabilities

    def observes(self, other_id: str) -> bool:
        return other_id in self.channels


class World:
    """Subclass per world in worlds/. Keep state as plain data and step pure, so rollouts
    are cheap copies. Every number a world uses is either in its SPACE (swept) or in its
    FIXED (with a reason). See AGENTS.md, "Adding a world"."""

    name = "world"

    def __init__(self, params: dict, rng):
        self.params = params
        self.rng = rng
        self.agents: list[Agent] = []
        self.by_id: dict[str, Agent] = {}

    def add(self, agent: Agent) -> None:
        self.agents.append(agent)
        self.by_id[agent.id] = agent

    # ---- a world must define these ----
    def initial_state(self) -> dict:
        raise NotImplementedError

    def belief_state(self, state: dict, agent: Agent) -> dict:
        """Pure projection to a complete hypothetical state for this agent.

        Use permitted observations and declared point priors, not inaccessible truth.
        Indistinguishable real states must yield the same planning state. Nested plans
        receive the parent's hypothetical state; never restore truth from world fields.
        Fully informed worlds may explicitly return state. All other planning methods
        must use the projected state and publicly known model, not stored private data.
        This is a modeling contract, not a security boundary or a belief distribution.
        """
        raise NotImplementedError("world must declare belief_state(state, agent)")

    def actions(self, state: dict, agent: Agent) -> list:
        """Available actions, in a fixed order. Ties in value go to the earlier one."""
        raise NotImplementedError

    def step(self, state: dict, joint: dict, rng=None) -> dict:
        """Apply every agent's action and advance one round. Pure: returns a new state.
        rng None means use expected values (rollouts); an rng means sample (actual play).
        Must set state["last"] = joint and state["value"][agent_id] = this round's goal value."""
        raise NotImplementedError

    def prior_action(self, agent: Agent, other: Agent):
        """What `agent` assumes `other` does when it cannot observe it."""
        raise NotImplementedError

    def terminal(self, state: dict):
        """Label if the world is in an absorbing state, else None."""
        raise NotImplementedError

    def label(self, state: dict) -> str:
        """Finite-outcome label at the end of a run; not evidence of convergence."""
        raise NotImplementedError

    # ---- defaults a world may override ----
    def value(self, state: dict, agent: Agent) -> float:
        return state["value"][agent.id]

    def observed_last(self, state: dict, agent: Agent, other: Agent):
        if agent.observes(other.id):
            return state["last"].get(other.id)
        return None


# ---------- planner ----------

def believed_joint(world: World, state: dict, agent: Agent, own_action, responses=None) -> dict:
    """Others' actions as `agent` believes them: a computed response if one is held,
    else the last observed action, else the prior."""
    joint = {agent.id: own_action}
    for other in world.agents:
        if other.id == agent.id:
            continue
        if responses and other.id in responses:
            joint[other.id] = responses[other.id]
            continue
        last = world.observed_last(state, agent, other)
        joint[other.id] = last if last is not None else world.prior_action(agent, other)
    return joint


def _evaluate(world: World, state: dict, agent: Agent, action, k: int) -> float:
    """Evaluate an action from an already projected planning state."""
    total = 0.0
    s = state
    responses = None
    for t in range(agent.horizon):
        if k >= 1 and t == 1:
            # The response depends on who sees me, not on whom I can see.
            responses = {o.id: plan(world, s, o, k - 1)
                         for o in world.agents if o.id != agent.id and o.observes(agent.id)}
        s = world.step(s, believed_joint(world, s, agent, action, responses))
        total += (agent.discount ** t) * world.value(s, agent)
        if world.terminal(s) is not None:
            break
    return total


def evaluate(world: World, state: dict, agent: Agent, action, k: int) -> float:
    """Discounted value of holding an action, using only this agent's planning state."""
    return _evaluate(world, world.belief_state(state, agent), agent, action, k)


def action_values(world: World, state: dict, agent: Agent, k: int | None = None) -> list:
    """Candidate/value pairs in tie-breaking order, from one information projection."""
    if k is None:
        k = agent.k
    belief = world.belief_state(state, agent)
    return [(action, _evaluate(world, belief, agent, action, k))
            for action in world.actions(belief, agent)]


def plan(world: World, state: dict, agent: Agent, k: int | None = None):
    best, best_value = None, None
    for action, v in action_values(world, state, agent, k):
        if best_value is None or v > best_value + 1e-12:
            best, best_value = action, v
    return best


# ---------- run ----------

def run(world: World, rounds: int, rng):
    """Play the world for `rounds` rounds or until terminal. Returns (label, state, trace)."""
    state = world.initial_state()
    trace = []
    for _ in range(rounds):
        joint = {a.id: plan(world, state, a) for a in world.agents}
        state = world.step(state, joint, rng)
        trace.append((joint, state))
        if world.terminal(state) is not None:
            break
    return world.label(state), state, trace
