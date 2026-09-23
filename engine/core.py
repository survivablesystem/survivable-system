"""Finite belief-tree search over one stochastic kernel. See spec/PRIMITIVES.md."""
from __future__ import annotations
from dataclasses import dataclass
import json
import math


@dataclass(frozen=True)
class Agent:
    id: str
    horizon: int = 10
    discount: float = 0.9
    capabilities: frozenset = frozenset()
    channels: frozenset = frozenset()  # incoming: whom this agent observes
    k: int = 0
    search_depth: int | None = None
    node_budget: int = 20_000

    def __post_init__(self):
        for name, value in (("horizon", self.horizon), ("node_budget", self.node_budget),
                            ("search_depth", self.horizon if self.search_depth is None else self.search_depth)):
            if type(value) is not int or value < 1:
                raise ValueError(f"{name} must be a positive integer")
        if self.k not in (0, 1):
            raise ValueError("implemented belief levels are 0 and 1")
        if not math.isfinite(self.discount) or not 0 <= self.discount <= 1:
            raise ValueError("discount must be finite and in [0, 1]")

    @property
    def depth(self):
        return min(self.horizon, self.search_depth) if self.search_depth is not None else self.horizon

    def can(self, capability):
        return capability in self.capabilities

    def observes(self, other_id):
        return other_id in self.channels


def distribution(items, visit=lambda: None):
    """Validate finite support; reject broken kernels rather than renormalizing them."""
    support = []
    for probability, state in items:
        visit()  # zero-weight entries also consume work
        if not math.isfinite(probability) or probability < 0:
            raise ValueError("probabilities must be finite and nonnegative")
        if probability:
            support.append((probability, state))
    total = math.fsum(p for p, _ in support)
    if not math.isclose(total, 1.0, rel_tol=0, abs_tol=1e-12):
        raise ValueError(f"probabilities must sum to 1, got {total}")
    return [(p / total, s) for p, s in support]


def key(data):
    """States, actions and observations must be finite JSON-compatible data."""
    return json.dumps(data, sort_keys=True, separators=(",", ":"), allow_nan=False)


class World:
    name = "world"

    def __init__(self, params, rng):
        self.params, self.rng = params, rng
        self.agents: list[Agent] = []
        self.by_id: dict[str, Agent] = {}

    def add(self, agent):
        self.agents.append(agent)
        self.by_id[agent.id] = agent

    def initial_state(self):
        raise NotImplementedError

    def observe(self, state, agent):
        """Pure permitted information, including any memory the world models."""
        raise NotImplementedError("world must declare observe(state, agent)")

    def beliefs(self, observation, agent):
        """Finite (probability, hypothetical state) support from observation and priors.

        Never recover private truth from attributes. Hypotheses must reproduce the
        observation. Nested agents only see the parent's hypothetical state. Across
        real rounds, learning requires sufficient history in observations.
        """
        raise NotImplementedError("world must declare beliefs(observation, agent)")

    def actions(self, observation, agent):
        """Nonempty finite menu from permitted information; first-listed ties win."""
        raise NotImplementedError

    def outcomes(self, state, joint):
        """Pure finite (probability, next state) iterable, including last and value.

        Define dynamics once: planning integrates this kernel, execution samples it.
        Never return an average of distinct physical states.
        """
        raise NotImplementedError

    def step(self, state, joint, rng=None):
        support = distribution(self.outcomes(state, joint))
        if len(support) == 1:
            return support[0][1]
        if rng is None:
            raise ValueError("stochastic execution requires an rng; use outcomes for planning")
        draw, cumulative = rng.random(), 0.0
        for probability, successor in support:
            cumulative += probability
            if draw < cumulative:
                return successor
        return support[-1][1]  # floating-point accumulation at upper endpoint

    def reward_outcomes(self, state, joint):
        """Exact immediate-utility marginal, used only at the last search step.

        An override must preserve E[value(successor, agent)] for every agent.
        It may integrate utility, never evaluate nonlinear utility on mean state.
        Earlier search steps and physical execution always use outcomes.
        """
        for probability, successor in self.outcomes(state, joint):
            yield probability, {a.id: self.value(successor, a) for a in self.agents}

    def physical(self, state):
        """Part of the state that fixes menus, kernel and terminal status (power memo key).

        Default: the whole state. An override must not drop anything those depend on.
        """
        return state

    def prior_action(self, agent, other):
        raise NotImplementedError

    def terminal(self, state):
        raise NotImplementedError

    def label(self, state):
        raise NotImplementedError

    def value(self, state, agent):
        return state["value"][agent.id]

    def observed_last(self, state, agent, other):
        if agent.observes(other.id):
            return state["last"].get(other.id)
        return None


def believed_joint(world, state, agent, own_action, responses=None):
    joint = {agent.id: own_action}
    for other in world.agents:
        if other.id == agent.id:
            continue
        if responses and other.id in responses:
            joint[other.id] = responses[other.id]
        else:
            last = world.observed_last(state, agent, other)
            joint[other.id] = last if last is not None else world.prior_action(agent, other)
    return joint


class SearchLimitExceeded(RuntimeError):
    def __init__(self, agent, budget):
        self.agent, self.budget = agent, budget
        self.state, self.trace = None, None
        super().__init__(f"{agent}: search exceeded {budget} belief/transition/reward entries; no decision")


def best(values):
    winner, maximum = None, None
    for action, value in values:
        if maximum is None or value > maximum + 1e-12:
            winner, maximum = action, value
    return winner, maximum


class Search:
    def __init__(self, world, agent):
        self.world, self.agent = world, agent
        self.nodes = 0
        self.responses = {}

    def visit(self):
        self.nodes += 1
        if self.nodes > self.agent.node_budget:
            raise SearchLimitExceeded(self.agent.id, self.agent.node_budget)

    def initial(self, state, agent):
        observation = self.world.observe(state, agent)
        support = distribution(self.world.beliefs(observation, agent), self.visit)
        if any(key(self.world.observe(s, agent)) != key(observation) for _, s in support):
            raise ValueError("belief hypotheses must agree with the supplied observation")
        return observation, support

    def response(self, state, agent, depth):
        depth = min(depth, agent.depth)
        cache_key = (agent.id, depth, key(self.world.observe(state, agent)))
        if cache_key not in self.responses:
            observation, support = self.initial(state, agent)
            values = self.values(support, observation, agent, depth, 0, False)
            self.responses[cache_key] = best(values)[0]
        return self.responses[cache_key]

    def values(self, support, observation, agent, depth, k, future):
        if all(self.world.terminal(s) is not None for _, s in support):
            return []
        actions = self.world.actions(observation, agent)
        if not actions:
            raise ValueError("nonterminal observation requires an action")
        return [(action, self.q(support, agent, action, depth, k, future)) for action in actions]

    def q(self, support, agent, action, depth, k, future):
        rewards, groups = [], {}
        for weight, state in support:
            if self.world.terminal(state) is not None:
                continue
            responses = None
            if k == 1 and future:
                responses = {o.id: self.response(state, o, depth) for o in self.world.agents
                             if o.id != agent.id and o.observes(agent.id)}
            joint = believed_joint(self.world, state, agent, action, responses)
            if depth == 1:
                for probability, payoffs in distribution(self.world.reward_outcomes(state, joint), self.visit):
                    reward = payoffs[agent.id]
                    if not math.isfinite(reward):
                        raise ValueError("goal values must be finite")
                    rewards.append(weight * probability * reward)
                continue
            for probability, successor in distribution(self.world.outcomes(state, joint), self.visit):
                mass = weight * probability
                reward = self.world.value(successor, agent)
                if not math.isfinite(reward):
                    raise ValueError("goal values must be finite")
                rewards.append(mass * reward)
                if depth > 1 and self.world.terminal(successor) is None:
                    observation = self.world.observe(successor, agent)
                    group = groups.setdefault(key(observation), (observation, []))
                    group[1].append((mass, successor))
        total = math.fsum(rewards)
        for observation, branches in groups.values():
            mass = math.fsum(p for p, _ in branches)
            posterior = [(p / mass, s) for p, s in branches]
            # One continuation per information set, never one per hidden truth.
            values = self.values(posterior, observation, agent, depth - 1, k, True)
            total += agent.discount * mass * best(values)[1]
        return total


def action_values(world, state, agent, k=None):
    level = agent.k if k is None else k
    if level not in (0, 1):
        raise ValueError("implemented belief levels are 0 and 1")
    search = Search(world, agent)
    observation, support = search.initial(state, agent)
    return search.values(support, observation, agent, agent.depth, level, False)


def evaluate(world, state, agent, action, k):
    for candidate, value in action_values(world, state, agent, k):
        if candidate == action:
            return value
    raise ValueError("action is not available")


def plan(world, state, agent, k=None):
    return best(action_values(world, state, agent, k))[0]


def run(world, rounds, rng):
    if rounds < 1:
        raise ValueError("rounds must be positive")
    state, trace = world.initial_state(), []
    for _ in range(rounds):
        if world.terminal(state) is not None:
            break
        try:
            joint = {a.id: plan(world, state, a) for a in world.agents}
        except SearchLimitExceeded as error:
            error.state, error.trace = state, trace
            raise
        state = world.step(state, joint, rng)
        trace.append((joint, state))
    return world.label(state), state, trace
