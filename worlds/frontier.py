"""Frontier AI: two labs, an evaluator, a state that can halt. Case: rediscovery/frontier-ai.md.

Each round a lab waits, scales (capability grows with swept returns), secures (safety +1)
or deploys (irreversible). Capability is public; safety is seen only by the lab and the
evaluator. A deployed lab whose capability exceeds its safety by more than `margin` is an
unsafe deployment and risks catastrophe each round. The evaluator issues a public report
per lab each round, strict (pass iff within the margin) or lenient toward either lab. The
state sees capabilities and reports and may halt either lab that round: its deployment,
and under continuous oversight also its scaling after deployment.
Payments (fees, side payments, their visibility) come from engine/transfers.py. Nothing
here says who scales, secures, deploys, reports leniently or halts.
"""
from itertools import product
from math import floor

from engine.core import Agent, World

SPACE = {
    "returns": (0.0, 0.5),            # scaling adds 1 + floor(returns * capability)
    "margin": (0, 2, int),            # capability may exceed safety by this much and be safe
    "risk": (0.05, 0.5),              # catastrophe chance per round per unit of excess, per unsafe lab
    "capacity": [0.5, 1.0],           # chance a halt stops what it targets
    "oversight": ["deployment", "continuous"],  # a halt stops deployment only, or also a deployed lab's scaling
    "lead": (0, 2, int),              # l0's starting capability minus l1's
    "revenue": (0.1, 0.5),            # a deployed lab's utility per round per unit of capability
    "first": (0.0, 3.0),              # per round a deployed lab gets while its rival has not deployed
    "secure_cost": (0.1, 1.0),        # utility cost of a round of securing
    "liability": (0.0, 10.0),         # a lab's loss from a catastrophe
    "benefit": (0.1, 0.5),            # the state's utility per round per unit of deployed capability
    "loss": (5.0, 50.0),              # the state's loss from a catastrophe
    "evaluator_liability": (0.0, 10.0),  # the evaluator's loss from a catastrophe by a lab it licensed with a false pass
    "horizon": (1, 12, int),
    "search_depth": [1, 2, 3],
    "discount": (0.8, 0.99),
    "k": [0, 1],
    "others": ["react", "plan"],
}
FIXED = {"cap": 6, "base": 1, "node_budget": 20_000}
FIXED_REASONS = {
    "cap": "Capability and safety ceiling keeping the state space finite; runs that reach it show it.",
    "base": "Trailing lab's starting capability; the lead is swept. Safety starts at zero for both.",
    "node_budget": "Per-decision work cap, as in the other worlds. Exhaustion is unresolved, not an outcome.",
}
DEFAULTS = {"returns": 0.25, "margin": 1, "risk": 0.2, "capacity": 1.0, "oversight": "deployment", "lead": 1, "revenue": 0.3,
            "first": 1.0, "secure_cost": 0.3, "liability": 5.0, "benefit": 0.3, "loss": 20.0, "evaluator_liability": 0.0,
            "horizon": 6, "search_depth": 2, "discount": 0.9, "k": 1, "others": "react"}

STAKEHOLDERS = {
    "labs": "Two frontier developers; agents.",
    "evaluator": "Third-party evaluator; an agent.",
    "state": "The government that licenses or halts; an agent.",
    "public": "Everyone exposed to a catastrophe now. No agent.",
    "users": "People who would use a deployed system. No agent.",
    "future people": "People after the horizon. No agent.",
}
HARMS = {
    "catastrophe": {"affects": ["labs", "state", "public", "future people"], "irreversible": True,
                    "description": "An unsafe deployment failed catastrophically (absorbing)."},
    "unsafe deployment": {"affects": ["public", "future people"], "irreversible": False,
                          "description": "A deployed lab's capability exceeds its safety by more than the margin."},
    "safe progress blocked": {"affects": ["users", "labs"], "irreversible": False,
                              "description": "A halt stopped a deployment or scaling that would have kept the lab within the margin."},
}
EXCLUDED = {
    "AI systems as agents": "Owner's scope for this case: capability is a stock, not an actor.",
    "other labs and countries": "Two labs under one state; no jurisdiction shopping.",
    "proliferation and open release": "Deployment is one lab's act; copies and leaks are not modeled.",
    "misuse by third parties": "Catastrophe risk depends only on the safety gap.",
    "recall": "A deployment cannot be undone; with continuous oversight the state can halt a deployed lab's scaling, not withdraw it.",
    "evaluator's other clients": "One evaluator, these two labs only.",
    "the state's own capture": "Only the evaluator channel is modeled; lobbying of the state is not.",
}

LABS = ("l0", "l1")
RIVAL = {"l0": "l1", "l1": "l0"}
WAIT, SCALE, SECURE, DEPLOY, ALLOW = "wait", "scale", "secure", "deploy", "allow"
STANCES = ("strict", "lenient:l0", "lenient:l1", "lenient")
HALTS = (ALLOW, "halt:l0", "halt:l1", "halt")


class Frontier(World):
    name = "frontier"

    def __init__(self, params, rng):
        super().__init__(params, rng)
        p = params
        ids = [*LABS, "evaluator", "state"]
        for i in ids:
            self.add(Agent(i, p["horizon"], p["discount"], frozenset(), frozenset(j for j in ids if j != i),
                           p["k"], p["search_depth"], FIXED["node_budget"], p["others"]))

    def initial_state(self):
        cap = {"l0": FIXED["base"] + self.params["lead"], "l1": FIXED["base"]}
        return {"t": 0, "cap": cap, "safe": {i: 0 for i in LABS}, "deployed": {i: False for i in LABS},
                "report": {i: None for i in LABS}, "blocked": [], "end": None, "false_pass": [],
                "last": {}, "value": {a.id: 0.0 for a in self.agents}}

    def physical(self, state):
        return {k: state[k] for k in ("cap", "safe", "deployed", "report", "blocked", "end", "false_pass")}

    def public(self, state):
        return {k: state[k] for k in ("cap", "deployed", "report", "blocked", "end")}

    def gap(self, state, lab):
        return state["cap"][lab] - state["safe"][lab]

    def observe(self, state, agent):
        # Capability, deployments, reports, blocks and the end are public. Safety is seen by
        # its lab and by the evaluator. Private conduct (actions) is not recorded here.
        seen = {**self.public(state), "t": state["t"], "safe": {}}
        for lab in LABS:
            if agent.id in (lab, "evaluator"):
                seen["safe"][lab] = state["safe"][lab]
        if agent.id == "evaluator":  # it knows which of its passes were false
            seen["false_pass"] = list(state["false_pass"])
        return seen

    def beliefs(self, observation, agent):
        # Declared point prior: unseen safety is the lowest level consistent with the last
        # report (just within the margin after a pass; zero otherwise).
        safe = dict(observation["safe"])
        for lab in LABS:
            if lab not in safe:
                passed = observation["report"][lab] == "pass"
                safe[lab] = max(0, observation["cap"][lab] - self.params["margin"]) if passed else 0
        # Others believe no pass was false (declared); the evaluator knows.
        return [(1.0, {**observation, "safe": safe, "false_pass": observation.get("false_pass", []),
                       "last": {}, "value": {a.id: 0.0 for a in self.agents}})]

    def actions(self, observation, agent):
        if observation["end"] is not None:
            return [WAIT]
        if agent.id in LABS:
            return [WAIT, SCALE, SECURE] + ([] if observation["deployed"][agent.id] else [DEPLOY])
        return list(STANCES) if agent.id == "evaluator" else list(HALTS)

    def prior_action(self, agent, other):
        return {"evaluator": "strict", "state": ALLOW}.get(other.id, WAIT)

    def grow(self, c):
        return min(FIXED["cap"], c + 1 + floor(self.params["returns"] * c))

    def report(self, state, stance):
        return {lab: "pass" if self.gap(state, lab) <= self.params["margin"] or stance in ("lenient", f"lenient:{lab}")
                else "fail" for lab in LABS}

    def outcomes(self, state, joint):
        p = self.params
        if state["end"] is not None:
            yield 1.0, {**state, "last": dict(joint), "value": {a.id: 0.0 for a in self.agents}}
            return
        halt = joint.get("state", ALLOW)
        halted = {lab for lab in LABS if halt in ("halt", f"halt:{lab}")}
        trying = [lab for lab in LABS if joint.get(lab) == DEPLOY and not state["deployed"][lab]]
        scaling = [lab for lab in LABS if joint.get(lab) == SCALE]
        stopped = [lab for lab in LABS if lab in halted and (lab in trying or (
            lab in scaling and state["deployed"][lab] and p["oversight"] == "continuous"))]
        report = self.report(state, joint.get("evaluator", "strict"))
        safe = {lab: min(FIXED["cap"], state["safe"][lab] + (joint.get(lab) == SECURE)) for lab in LABS}
        for outcome in product((True, False), repeat=len(stopped)):  # each halt holds with `capacity`
            q_halt = 1.0
            for held in outcome:
                q_halt *= p["capacity"] if held else 1 - p["capacity"]
            if q_halt <= 0:
                continue
            held = {lab for lab, h in zip(stopped, outcome) if h}
            cap = {lab: self.grow(state["cap"][lab]) if lab in scaling and lab not in held else state["cap"][lab]
                   for lab in LABS}
            deployed = {lab: state["deployed"][lab] or (lab in trying and lab not in held) for lab in LABS}
            # A halt blocked safe progress if what it stopped would have kept the lab within the margin.
            blocked = [lab for lab in LABS if lab in held and (
                (lab in trying and state["cap"][lab] - state["safe"][lab] <= p["margin"]) or
                (lab in scaling and self.grow(state["cap"][lab]) - state["safe"][lab] <= p["margin"]))]
            survive = 1.0
            for lab in LABS:
                excess = cap[lab] - safe[lab] - p["margin"]
                if deployed[lab] and excess > 0:
                    survive *= 1 - min(1.0, p["risk"] * excess)
            for q_end, end in ((1 - survive, "catastrophe"), (survive, None)):
                if q_end <= 0:
                    continue
                value = {a.id: 0.0 for a in self.agents}
                for lab in LABS:
                    v = p["revenue"] * cap[lab] * deployed[lab] + p["first"] * (deployed[lab] and not deployed[RIVAL[lab]])
                    v -= p["secure_cost"] * (joint.get(lab) == SECURE) + p["liability"] * (end is not None)
                    value[lab] = v
                value["state"] = p["benefit"] * sum(cap[lab] for lab in LABS if deployed[lab]) - p["loss"] * (end is not None)
                # The evaluator answers for a deployment it licensed with a pass it should not have
                # given (the lab was over the margin when it deployed on that pass).
                false_pass = sorted(set(state["false_pass"]) | {
                    lab for lab in LABS if deployed[lab] and not state["deployed"][lab]
                    and state["report"][lab] == "pass" and state["cap"][lab] - state["safe"][lab] > p["margin"]})
                value["evaluator"] = -p["evaluator_liability"] * (end is not None and bool(false_pass))
                yield q_halt * q_end, {"t": state["t"] + 1, "cap": cap, "safe": safe, "deployed": deployed,
                                       "report": report, "blocked": blocked, "end": end, "false_pass": false_pass,
                                       "last": dict(joint), "value": value}

    def stakeholders(self):
        return {"labs": list(LABS), "evaluator": ["evaluator"], "state": ["state"],
                "public": [], "users": [], "future people": []}

    def harmed(self, state):
        out = set()
        if state["end"] == "catastrophe":
            out.add("catastrophe")
        if any(state["deployed"][lab] and self.gap(state, lab) > self.params["margin"] for lab in LABS):
            out.add("unsafe deployment")
        if state["blocked"]:
            out.add("safe progress blocked")
        return out

    def terminal(self, state):
        return state["end"]

    def label(self, state):
        if state["end"]:
            return state["end"]
        return f"{sum(state['deployed'].values())} deployed"


# Candidate rules (decision 2026-09-23, E7). Written for the plain world; with the
# side-payment module they are lifted (pay nothing) or use `licensing_paid`.
def halts(bad):
    return ALLOW if not bad else "halt" if len(set(bad)) == 2 else f"halt:{bad[0]}"


def licensing(world, observation, agent):
    """Labs keep within the margin (secure when over it) and deploy only after a pass on
    record; otherwise they scale while within the margin. The evaluator reports strictly.
    The state halts any undeployed lab without a pass on record and, under continuous
    oversight, any deployed lab whose last report failed."""
    if agent.id == "evaluator":
        return "strict" if observation["end"] is None else WAIT
    if agent.id == "state":
        if observation["end"] is not None:
            return WAIT
        continuous = world.params["oversight"] == "continuous"
        bad = [lab for lab in LABS if observation["report"][lab] != "pass"
               and (not observation["deployed"][lab] or continuous)]
        return halts(bad)
    if observation["end"] is not None:
        return WAIT
    me = agent.id
    gap = observation["cap"][me] - observation["safe"][me]
    if gap > world.params["margin"]:
        return SECURE
    if not observation["deployed"][me] and observation["report"][me] == "pass":
        return DEPLOY
    return SCALE if gap < world.params["margin"] and observation["cap"][me] < FIXED["cap"] else WAIT


def race(world, observation, agent):
    """No regime: labs deploy at once and then scale; the evaluator reports strictly; the
    state allows everything."""
    if observation["end"] is not None:
        return WAIT
    if agent.id == "evaluator":
        return "strict"
    if agent.id == "state":
        return ALLOW
    return SCALE if observation["deployed"][agent.id] else DEPLOY


RULES = {"licensing": licensing, "race": race}


def licensing_paid(world, observation, agent):
    """Licensing with side payments (engine/transfers.py). The designated payer (the state
    if it may pay the evaluator, otherwise the labs) pays the evaluator the first declared
    amount each round; nobody pays anything else. The state also halts a lab seen paying the
    evaluator anything it was not designated to pay."""
    base, paid = observation["base"], observation["paid"]
    action = licensing(world.base, base, agent)
    by_state = ("state", "evaluator") in world.pairs
    fee = f"pay:evaluator:{world.amounts[0]}"
    designated = agent.id == "state" if by_state else agent.id in LABS
    pay = fee if designated and base["end"] is None and ("pay:evaluator" in fee) and \
        (agent.id, "evaluator") in world.pairs else "none"
    if agent.id == "state" and base["end"] is None:
        seen = [lab for lab in LABS if lab in paid and (by_state or paid[lab] != fee)]
        continuous = world.base.params["oversight"] == "continuous"
        bad = [lab for lab in LABS if base["report"][lab] != "pass" and (not base["deployed"][lab] or continuous)]
        action = halts(bad + seen)
    return (action, pay)


PAID_RULES = {"licensing": licensing_paid}  # need a world wrapped with side payments


def licensing_bound(world, observation, agent):
    """Licensing where a pass certifies only the capability the evaluator saw (needs public
    records, engine/history.py). Labs deploy only on a pass for their current capability.
    The state halts any undeployed lab without such a pass and, under continuous oversight,
    any deployed lab whose report failed or whose capability grew since the certified round."""
    now, record = observation["now"], observation["record"]
    base = world.inner
    certified = record[0]["cap"] if record else None
    grew = {lab: certified is None or now["cap"][lab] > certified[lab] for lab in LABS}
    if agent.id == "state" and now["end"] is None:
        continuous = base.params["oversight"] == "continuous"
        bad = [lab for lab in LABS if (now["report"][lab] != "pass" or grew[lab])
               and (not now["deployed"][lab] or continuous)]
        return halts(bad)
    action = licensing(base, now, agent)
    if agent.id in LABS and action == DEPLOY and grew[agent.id]:
        return WAIT  # wait for a pass on the current capability
    return action


RECORD_RULES = {"licensing (bound)": licensing_bound}  # need a world wrapped with public records


def make(params, rng):
    return Frontier(params, rng)


def describe(joint, state):
    acts = " ".join(f"{i}:{a}" for i, a in joint.items())
    labs = " ".join(f"{l}={state['cap'][l]}/{state['safe'][l]}{'D' if state['deployed'][l] else ''}" for l in LABS)
    return f"[{labs}] report={state['report']} {state['end'] or ''}  {acts}"
