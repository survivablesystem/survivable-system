"""Authority and coercion: who can end a harmful use of office. Case: rediscovery/standing-army.md.

A ruler holds office; commanders share an army; citizens have a little strength each.
Every round the holder governs or extracts (office converts into its own strength by
`gain`; citizens bear the extraction), and may also purge one agent it sees organizing. Everyone
else may stay, defend the holder, organize (covert), or rise if it organized last round.
A rise is a contest between the risers and the holder with its defenders; success deposes
the holder (disarmed) and gives office, with its surveillance apparatus, to the strongest
riser; failure disarms the risers. Strength never regrows. No rule says who should rule:
office is whatever the last contest left. Nothing here says when to extract, purge,
organize, defend or rise. The planner decides from goals; power queries ignore goals.
"""
from engine.core import Agent, World

SPACE = {
    "commands": [1, 2],               # the army split into this many commands (same total)
    "army": (2, 6, int),              # total army strength
    "citizens": [1, 2, 3],            # citizens, strength one each
    "guard": (0, 3, int),             # the ruler's own strength at the start
    "gain": [0, 1, 2],                # strength the holder gains per round of extraction
    "contest": ["threshold", "ratio", "tullock"],
    "advantage": (1.0, 2.0),          # threshold: attack succeeds iff >= advantage * defense
    "decisiveness": (1.0, 64.0),      # tullock: a^m / (a^m + (advantage * d)^m); m = 1, advantage 1 is ratio
    "surveillance": ["none", "army", "all"],  # whose organizing the holder sees (and can purge)
    "assembly": ["none", "all"],      # whether non-holders see each other organize
    "prize": (0.0, 2.0),              # utility per round in office
    "rent": (0.0, 2.0),               # holder's utility per round of extraction
    "burden": (0.0, 2.0),             # each citizen's disutility per round of extraction
    "horizon": (1, 12, int),
    "search_depth": [1, 2, 3],
    "discount": (0.8, 0.99),
    "k": [0, 1],
    "others": ["react", "plan"],      # level-1 opponent model, see engine/core.py
}
FIXED = {"cap": 9, "citizen_strength": 1, "node_budget": 20_000}
FIXED_REASONS = {
    "cap": "Strength ceiling keeping the state space finite. A holder at the ceiling stops growing; traces show it.",
    "citizen_strength": "Scale unit. Army, guard and gain are swept relative to it.",
    "node_budget": "Per-decision work cap, as in the other worlds. Exhaustion is unresolved, not an outcome.",
}
DEFAULTS = {"commands": 1, "army": 3, "citizens": 2, "guard": 1, "gain": 1, "contest": "threshold",
            "advantage": 1.5, "decisiveness": 4.0, "surveillance": "all", "assembly": "none", "prize": 1.0, "rent": 1.0,
            "burden": 1.0, "horizon": 6, "search_depth": 2, "discount": 0.9, "k": 1, "others": "react"}

# Who the modeled outcomes fall on (decision 2026-09-23, E1). Agents or not.
STAKEHOLDERS = {
    "ruler": "The initial office holder; an agent.",
    "commanders": "Each directs one command of the army; agents.",
    "citizens": "Modeled citizens with a little strength each; agents.",
    "governed population": "Everyone else the office governs, now and later. No agent.",
}
HARMS = {
    "extraction": {"affects": ["citizens", "governed population"], "irreversible": False,
                   "description": "The holder extracted this round (and kept office)."},
    "citizen disarmed": {"affects": ["citizens", "governed population"], "irreversible": True,
                         "description": "A citizen's strength is zero (purged or crushed); strength never regrows."},
}
EXCLUDED = {
    "external threats": "No outside enemy: the army's purpose and its usable strength against others are not modeled.",
    "production": "Extraction is a harm flow only; there is no economy it depletes or funds beyond the guard.",
    "soldiers": "A commander controls its command; delegation drift is complete by assumption.",
    "succession at exit": "The ruler never dies or leaves; succession rules are not modeled.",
    "foreign intervention": "Nobody outside the polity acts.",
    "legitimacy": "No agent values who holds office beyond its own prize, rent and burden.",
    "commanders' burden": "Commanders are not burdened by extraction (an elite assumption).",
}

GOVERN, EXTRACT, STAY, DEFEND, ORGANIZE, RISE = "govern", "extract", "stay", "defend", "organize", "rise"


class Authority(World):
    name = "authority"

    def __init__(self, params, rng):
        super().__init__(params, rng)
        p = params
        k = p["commands"]
        self.units = {f"c{i}": p["army"] // k + (i < p["army"] % k) for i in range(k)}
        self.people = [f"p{i}" for i in range(p["citizens"])]
        ids = ["ruler", *self.units, *self.people]
        for i in ids:
            # Acts are public except organizing, which observe() masks; see `sees`.
            self.add(Agent(i, p["horizon"], p["discount"], frozenset({"coerce"}),
                           frozenset(j for j in ids if j != i), p["k"], p["search_depth"],
                           FIXED["node_budget"], p["others"]))

    def initial_state(self):
        strength = {"ruler": self.params["guard"], **self.units,
                    **{i: FIXED["citizen_strength"] for i in self.people}}
        return {"t": 0, "office": "ruler", "strength": strength, "organized": [], "extracting": False,
                "last": {a.id: GOVERN if a.id == "ruler" else STAY for a in self.agents},
                "value": {a.id: 0.0 for a in self.agents}}

    def physical(self, state):
        return {k: state[k] for k in ("office", "strength", "organized", "extracting")}

    def sees(self, state, viewer, other):
        """Whether `viewer` sees `other` organize. The holder's view comes with office."""
        if viewer == other:
            return True
        if viewer == state["office"]:
            reach = self.params["surveillance"]
            return reach == "all" or (reach == "army" and other in self.units)
        return self.params["assembly"] == "all" and other != state["office"]

    def observe(self, state, agent):
        hidden = lambda i: not self.sees(state, agent.id, i)
        return {"t": state["t"], "office": state["office"], "strength": dict(state["strength"]),
                "extracting": state["extracting"],
                "organized": [i for i in state["organized"] if not hidden(i)],
                "last": {i: STAY if a == ORGANIZE and hidden(i) else a for i, a in state["last"].items()}}

    def beliefs(self, observation, agent):
        # Declared point prior: organizing that the agent cannot see is believed absent.
        return [(1.0, {**observation, "value": {a.id: 0.0 for a in self.agents}})]

    def actions(self, observation, agent):
        if agent.id == observation["office"]:
            targets = [i for i in observation["organized"] if i != agent.id]
            return [GOVERN, EXTRACT] + [f"{policy}+purge:{i}" for policy in (GOVERN, EXTRACT) for i in targets]
        if observation["strength"][agent.id] == 0:
            return [STAY]
        return [STAY, DEFEND, ORGANIZE] + ([RISE] if agent.id in observation["organized"] else [])

    def prior_action(self, agent, other):
        return STAY

    def contest(self, attack, defense):
        if self.params["contest"] == "threshold":
            return 1.0 if attack > 0 and attack >= self.params["advantage"] * defense else 0.0
        if self.params["contest"] == "tullock":  # A2: between ratio (m = 1) and threshold (m large)
            if attack <= 0:
                return 0.0
            m, d = self.params["decisiveness"], self.params["advantage"] * defense
            try:
                return 1.0 / (1.0 + (d / attack) ** m)
            except OverflowError:  # the defense is overwhelming at this decisiveness
                return 0.0
        return attack / (attack + defense) if attack + defense else 0.0

    def outcomes(self, state, joint):
        p, ids = self.params, [a.id for a in self.agents]
        holder, strength, organized = state["office"], state["strength"], state["organized"]
        # Believed joints may carry acts from another role or a stale target: read them in role.
        policy, _, purge = joint[holder].partition("+")
        target = purge.split(":", 1)[1] if purge.startswith("purge:") else None
        if target is not None and not (target in organized and target != holder and strength[target] > 0):
            target = None
        role = lambda i, a: a if i != holder and strength[i] > 0 else STAY
        purges = [(1.0, False)] if target is None else [
            (q, hit) for q, hit in ((self.contest(strength[holder], strength[target]), True),
                                    (1 - self.contest(strength[holder], strength[target]), False)) if q > 0]
        for q_purge, purged in purges:
            st = dict(strength)
            if purged:
                st[target] = 0
            risers = [i for i in ids if role(i, joint[i]) == RISE and i in organized and st[i] > 0]
            defenders = [i for i in ids if role(i, joint[i]) == DEFEND and st[i] > 0]
            attack, defense = sum(st[i] for i in risers), st[holder] + sum(st[i] for i in defenders)
            win = self.contest(attack, defense) if risers else 0.0
            for q_rise, won in ((win, True), (1 - win, False)):
                if q_rise <= 0:
                    continue
                s2 = dict(st)
                office = holder
                if won:
                    office = max(risers, key=lambda i: (st[i], -ids.index(i)))  # ties: first listed
                    s2[holder] = 0
                else:
                    for i in risers:
                        s2[i] = 0
                extracting = not won and policy == EXTRACT
                if extracting:
                    s2[holder] = min(FIXED["cap"], s2[holder] + p["gain"])
                org = [i for i in ids if i != holder and i != office and role(i, joint[i]) == ORGANIZE and s2[i] > 0]
                value = {}
                for i in ids:
                    v = p["prize"] * (i == office) + p["rent"] * (i == office and extracting)
                    value[i] = v - p["burden"] * (i in self.people and i != office and extracting)
                yield q_purge * q_rise, {"t": state["t"] + 1, "office": office, "strength": s2,
                                         "organized": org, "extracting": extracting,
                                         "last": dict(joint), "value": value}

    def public(self, state):
        # What a record could hold: who holds office, whether it extracted, everyone's strength.
        return {"office": state["office"], "extracting": state["extracting"], "strength": dict(state["strength"])}

    def stakeholders(self):
        return {"ruler": ["ruler"], "commanders": list(self.units), "citizens": list(self.people),
                "governed population": []}

    def harmed(self, state):
        out = {"extraction"} if state["extracting"] else set()
        if any(state["strength"][i] == 0 for i in self.people):
            out.add("citizen disarmed")
        return out

    def terminal(self, state):
        return None

    def label(self, state):
        office = state["office"]
        role = "ruler" if office == "ruler" else "commander" if office in self.units else "citizen"
        return f"{role} {'extracting' if state['extracting'] else 'governing'}"


# Candidate rules (decision 2026-09-23, E7): declared conduct, tested, never enforced by the kernel.
def loyalty(world, observation, agent):
    """The holder governs; everyone else defends the holder."""
    if agent.id == observation["office"]:
        return GOVERN
    return DEFEND if observation["strength"][agent.id] > 0 else STAY


def accountability(world, observation, agent):
    """The holder governs and purges nobody. Everyone else organizes the round after the
    holder extracts, rises once organized, defends a governing holder against anyone it
    sees organizing, and otherwise stays."""
    me = agent.id
    if me == observation["office"]:
        return GOVERN
    if observation["strength"][me] == 0:
        return STAY
    if me in observation["organized"]:
        return RISE
    if observation["extracting"]:
        return ORGANIZE
    return DEFEND if any(i != me for i in observation["organized"]) else STAY


RULES = {"loyalty": loyalty, "accountability": accountability}


def restitution_pairs(world):
    """Payment pairs for restitution: every agent may pay the citizens other than itself."""
    return [(a.id, "+".join(p for p in world.people if p != a.id)) for a in world.agents
            if [p for p in world.people if p != a.id]]


def restitution(world, observation, agent):
    """With side payments (engine/transfers.py, restitution pairs, public disclosure): the
    holder governs, and the round after it extracts it repays the citizens the first declared
    amount (less does not count). Everyone else
    organizes after an extraction, rises if the holder extracted again or did not repay,
    stands down once repaid, defends a governing holder against anyone else organizing,
    and otherwise stays. With a public record (engine/history.py), organizing counts as a
    warning only if the record shows the extraction that called for it; otherwise
    organizers stand down and others defend against them."""
    record = observation.get("record") if "now" in observation else None
    observation_now = observation["now"] if "now" in observation else observation
    base, paid, me = observation_now["base"], observation_now["paid"], agent.id
    warned = True if record is None else bool(record) and record[0]["base"]["extracting"]
    holder = base["office"]
    menu = world.actions(observation, agent)
    due = world.amounts[0]  # restitution is the first declared amount; less does not count
    if me == holder:
        if base["extracting"]:
            repay = [a for a in menu if a[0] == GOVERN and a[1] != "none"
                     and set(world.parse(a[1])[0]) <= set(world.people) and world.parse(a[1])[1] >= due]
            if repay:
                return repay[0]
        return (GOVERN, "none")
    if base["strength"][me] == 0:
        return (STAY, "none")
    # public disclosure: everyone sees last round's payments
    repaid = holder in paid and set(world.parse(paid[holder])[0]) <= set(world.people) and world.parse(paid[holder])[1] >= due
    if me in base["organized"]:
        return (RISE if warned and (base["extracting"] or not repaid) else STAY, "none")
    if base["extracting"]:
        return (ORGANIZE, "none")
    return (DEFEND if any(i != me for i in base["organized"]) and not warned else STAY, "none")


PAID_RULES = {"restitution": restitution}  # need a world wrapped with side payments


def make(params, rng):
    return Authority(params, rng)


def describe(joint, state):
    acts = " ".join(f"{i}:{a}" for i, a in joint.items())
    st = " ".join(f"{i}={s}" for i, s in state["strength"].items())
    return f"office={state['office']:5s} {'X' if state['extracting'] else ' '} [{st}]  {acts}"
