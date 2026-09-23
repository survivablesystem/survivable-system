"""An auditor paid by the audited. Case: rediscovery/captured-auditor.md.

A firm learns each round whether its books are weak (chance). It reports honestly or
misstates, and names the auditor it will pay next round. The hired auditor sees the books
and commits to a response: strict (qualify a misstatement) or lenient (pass anything). A
misstatement that passes misleads investors, who have no agent; an independent channel
exposes it with probability `exposure`, costing the auditor credibility and the firm a
penalty. A clean opinion is worth more to the firm the more credible its auditor. If the
register allows it, a regulator may revoke an exposed auditor's license; revoked auditors
leave the market. Nothing here says who misstates, passes, switches or revokes.
"""
from engine.core import Agent, World

SPACE = {
    "auditors": [1, 2, 3],
    "weak": (0.1, 0.5),               # chance the books are weak in a round
    "exposure": (0.0, 1.0),           # chance a passed misstatement is exposed at once
    "regulator": ["none", "revokes"], # whether the regulator can revoke an exposed auditor
    "assignment": ["firm", "fixed"],  # who picks the auditor: the firm each round, or nobody (no switching)
    "fee": (0.5, 2.0),                # paid by the firm to the hired auditor each round
    "premium": (0.0, 2.0),            # firm's gain from a clean opinion by a fully credible auditor
    "penalty": (0.5, 3.0),            # firm's loss when weakness is revealed or a misstatement exposed
    "harm": (0.5, 3.0),               # investors' loss per misleading round (the regulator's goal)
    "credibility": (1, 3, int),       # each auditor's starting credibility
    "horizon": (1, 12, int),
    "search_depth": [1, 2, 3],
    "discount": (0.8, 0.99),
    "k": [0, 1],
    "others": ["react", "plan"],
}
FIXED = {"cap": 3, "node_budget": 20_000}
FIXED_REASONS = {
    "cap": "Credibility ceiling; one exposure costs one step. Premium scales with credibility / cap.",
    "node_budget": "Per-decision work cap, as in the other worlds. Exhaustion is unresolved, not an outcome.",
}
DEFAULTS = {"auditors": 2, "weak": 0.3, "exposure": 0.2, "regulator": "revokes", "assignment": "firm",
            "fee": 1.0, "premium": 1.0, "penalty": 1.5, "harm": 2.0, "credibility": 3,
            "horizon": 6, "search_depth": 2, "discount": 0.9, "k": 1, "others": "react"}

STAKEHOLDERS = {
    "firm": "The audited firm's management; an agent.",
    "auditors": "Audit firms competing for the engagement; agents.",
    "regulator": "Licensing authority acting for investors; an agent.",
    "investors": "People who rely on the audited report. No agent.",
}
HARMS = {
    "investors misled": {"affects": ["investors"], "irreversible": False,
                         "description": "A misstatement passed an audit this round."},
    "no licensed auditor": {"affects": ["investors", "firm"], "irreversible": True,
                            "description": "Every auditor's license is revoked; licenses never return."},
}
EXCLUDED = {
    "auditor entry": "No new audit firms enter; exit is by revocation only.",
    "investor behavior": "Investors do not act; the premium stands in for how they price a clean opinion.",
    "litigation": "No lawsuits; exposure costs are the penalty and lost credibility only.",
    "other clients": "Each auditor has one prospective client; portfolio effects are not modeled.",
    "the firm's workers and creditors": "Folded into investors.",
}

HONEST, MISSTATE, STRICT, LENIENT, IDLE, WAIT = "honest", "misstate", "strict", "lenient", "idle", "wait"


class Audit(World):
    name = "audit"

    def __init__(self, params, rng):
        super().__init__(params, rng)
        p = params
        self.auditors = [f"a{i}" for i in range(p["auditors"])]
        ids = ["firm", *self.auditors, "regulator"]
        for i in ids:
            self.add(Agent(i, p["horizon"], p["discount"], frozenset(), frozenset(j for j in ids if j != i),
                           p["k"], p["search_depth"], FIXED["node_budget"], p["others"]))

    def initial_state(self):
        c = self.params["credibility"]
        return {"t": 0, "weak": False, "hired": self.auditors[0], "credibility": {a: c for a in self.auditors},
                "licensed": list(self.auditors), "exposed": [], "opinion": "clean", "signed": None, "misled": False,
                "last": {}, "value": {a.id: 0.0 for a in self.agents}}

    def physical(self, state):
        return {k: state[k] for k in ("weak", "hired", "credibility", "licensed", "exposed", "misled")}

    def insider(self, state, agent_id):
        return agent_id in ("firm", state["hired"])

    def observe(self, state, agent):
        # The firm and its auditor see the books; everyone sees the opinion and who signed it,
        # credibility, licenses and exposures. Private conduct (reports, audit stance) is not public.
        if self.insider(state, agent.id):
            return {k: v for k, v in state.items() if k != "value"}
        return {k: state[k] for k in ("t", "hired", "credibility", "licensed", "exposed", "opinion", "signed")}

    def beliefs(self, observation, agent):
        if "weak" in observation:
            return [(1.0, {**observation, "value": {a.id: 0.0 for a in self.agents}})]
        q = self.params["weak"]
        # Outsiders: the books are weak with the prior chance; misleading is not seen (declared).
        return [(w, {**observation, "weak": weak, "misled": False, "last": {},
                     "value": {a.id: 0.0 for a in self.agents}})
                for w, weak in ((q, True), (1 - q, False)) if w > 0]

    def next_auditors(self, observation):
        licensed = observation["licensed"]
        if not licensed:
            return ["none"]
        if self.params["assignment"] == "fixed":
            return [observation["hired"] if observation["hired"] in licensed else licensed[0]]
        return list(licensed)

    def actions(self, observation, agent):
        if agent.id == "firm":
            reports = [HONEST, MISSTATE] if observation["weak"] and observation["hired"] in observation["licensed"] else [HONEST]
            return [f"{r}>{a}" for r in reports for a in self.next_auditors(observation)]
        if agent.id == "regulator":
            if self.params["regulator"] != "revokes":
                return [WAIT]
            return [WAIT] + [f"revoke:{a}" for a in observation["exposed"] if a in observation["licensed"]]
        if agent.id == observation["hired"] and agent.id in observation["licensed"]:
            return [STRICT, LENIENT]
        return [IDLE]

    def prior_action(self, agent, other):
        if other.id == "firm":
            return None  # resolved in role by outcomes
        return WAIT if other.id == "regulator" else STRICT

    def outcomes(self, state, joint):
        p, hired = self.params, state["hired"]
        firm = joint.get("firm") or f"{HONEST}>{hired}"
        report, _, chosen = firm.partition(">")
        audited = hired in state["licensed"]
        stance = joint.get(hired) if audited else None
        misstated = state["weak"] and report == MISSTATE and audited
        passed = misstated and stance == LENIENT
        revealed = state["weak"] and not passed  # honest report, or a qualified misstatement
        licensed = list(state["licensed"])
        act = joint.get("regulator", WAIT)
        if act.startswith("revoke:") and act.split(":", 1)[1] in licensed and act.split(":", 1)[1] in state["exposed"]:
            licensed.remove(act.split(":", 1)[1])
        nxt = chosen if chosen in licensed else (licensed[0] if licensed else "none")
        credible = state["credibility"].get(hired, 0) / FIXED["cap"] if audited else 0.0
        for q_exposed, exposed in ((p["exposure"], True), (1 - p["exposure"], False)) if passed else ((1.0, False),):
            if q_exposed <= 0:
                continue
            cred = dict(state["credibility"])
            if exposed:
                cred[hired] = max(0, cred[hired] - 1)
            value = {a.id: 0.0 for a in self.agents}
            value["firm"] = (p["premium"] * credible * (not revealed) - p["penalty"] * (revealed or exposed)
                             - p["fee"] * audited)
            if audited:
                value[hired] = p["fee"]
            value["regulator"] = -p["harm"] * passed
            opinion = "none" if not audited else "qualified" if (misstated and not passed) else "clean"
            for q_weak, weak in ((p["weak"], True), (1 - p["weak"], False)):
                if q_weak > 0:
                    yield q_exposed * q_weak, {
                        "t": state["t"] + 1, "weak": weak, "hired": nxt, "credibility": cred,
                        "licensed": licensed, "exposed": [hired] if exposed else [], "opinion": opinion,
                        "signed": hired if audited else None,
                        "misled": passed, "last": dict(joint), "value": value}

    def stakeholders(self):
        return {"firm": ["firm"], "auditors": list(self.auditors), "regulator": ["regulator"], "investors": []}

    def harmed(self, state):
        out = {"investors misled"} if state["misled"] else set()
        if not state["licensed"]:
            out.add("no licensed auditor")
        return out

    def terminal(self, state):
        return None

    def label(self, state):
        return f"{'misled' if state['misled'] else 'accurate'}, {len(state['licensed'])} licensed"


# Candidate rules (decision 2026-09-23, E7): declared conduct, tested, never enforced by the kernel.
def independence(world, observation, agent):
    """The firm reports honestly and keeps its auditor; auditors are strict; the regulator
    revokes any exposed auditor."""
    menu = world.actions(observation, agent)
    if agent.id == "firm":
        keep = [a for a in menu if a.startswith(HONEST) and a.endswith(">" + observation["hired"])]
        return keep[0] if keep else menu[0]
    if agent.id == "regulator":
        return next((a for a in menu if a.startswith("revoke:")), WAIT)
    return STRICT if STRICT in menu else IDLE


def capture(world, observation, agent):
    """The firm misstates weak books and drops an auditor that just qualified it; auditors
    are lenient; the regulator revokes any exposed auditor."""
    menu = world.actions(observation, agent)
    if agent.id == "firm":
        report = MISSTATE if any(a.startswith(MISSTATE) for a in menu) else HONEST
        hired = observation["hired"]
        drop = observation.get("opinion") == "qualified" and observation.get("signed") == hired
        options = [a for a in menu if a.startswith(report + ">")]
        keep = [a for a in options if a.endswith(">" + hired)]
        other = [a for a in options if not a.endswith(">" + hired)]
        return (other or options)[0] if drop else (keep or options)[0]
    if agent.id == "regulator":
        return next((a for a in menu if a.startswith("revoke:")), WAIT)
    return LENIENT if LENIENT in menu else IDLE


RULES = {"independence": independence, "capture": capture}


def make(params, rng):
    return Audit(params, rng)


def describe(joint, state):
    acts = " ".join(f"{i}:{a}" for i, a in joint.items())
    cred = " ".join(f"{a}={c}{'' if a in state['licensed'] else 'x'}" for a, c in state["credibility"].items())
    return f"{state['opinion']:9s} {'MISLED' if state['misled'] else '      '} hired={state['hired']} [{cred}]  {acts}"
