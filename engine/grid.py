"""Every query across the register; designs compared on the same assumptions.
Decision 2026-09-24 (E16).

A grid is a product of declared values: register parameters, start-state fields
(`state.<path>`) and, for rule checks, `rule`. Draws cross it with seeded samples of the rest
of the register. Each cell's report is flattened into named measures. The summary says, per
measure, whether it is the same in every cell, and otherwise which keys change it: holding
every other key (and the draw) fixed, in how many settings moving that key alone changes the
measure. A compared key pairs cells that differ only in it. Robustness is relative to the
grid: nothing here speaks for values outside it.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, replace
import importlib
from itertools import product
import json
import math
from multiprocessing import Pool
import random

from .history import History, lift as lift_history
from .prices import Prices
from .power import externalization, joint_prevention, lock_in, power_table, threshold
from .rules import TOLERANCE, enforcement
from .sweep import dependence, sample_params
from .transfers import Transfers, lift

LEVELS = (1.0, 0.5)  # thresholds reported by --power
NUMERIC = 1e-9       # a numeric measure moves when it changes by more than this


def parse_value(text):
    for cast in (int, float):
        try:
            return cast(text)
        except ValueError:
            continue
    return {"true": True, "false": False}.get(text.lower(), text)


def parse_fix(items):
    out = {}
    for item in items or []:
        if "=" not in item:
            raise ValueError(f"expected param=value, got {item!r}")
        k, v = item.split("=", 1)
        if not k or not v or k in out:
            raise ValueError(f"empty or duplicate override: {item!r}")
        out[k] = parse_value(v)
    return out


def validate_fix(fixed, space):
    for key, value in fixed.items():
        if key not in space:
            raise ValueError(f"unknown parameter {key!r}; choose from {', '.join(space)}")
        spec = space[key]
        if isinstance(spec, list):
            valid = any(type(value) is type(v) and value == v for v in spec)
        elif isinstance(spec, tuple):
            integer = len(spec) == 3 and spec[2] is int
            valid = (type(value) is int if integer else type(value) in (int, float))
            valid = valid and spec[0] <= value <= spec[1] and math.isfinite(value)
        else:
            valid = type(value) is type(spec) and value == spec
        if not valid:
            raise ValueError(f"invalid value {value!r} for {key}; declared domain: {spec}")


@dataclass(frozen=True)
class Setup:
    """A world module and the modules wrapped around it. Picklable: workers rebuild it."""
    module: str
    pay: tuple = ()               # (payer, recipient) pairs, engine/transfers.py
    amounts: tuple = (0.5, 1.0)
    disclosure: str = "parties"
    records: int | None = None    # engine/history.py
    prices: tuple = ()            # ((agent, harm), amount) pairs, engine/prices.py, innermost

    def build(self):
        """(module, make, rules): the world factory and its rules, lifted through the wrappers."""
        mod = importlib.import_module(self.module)
        make, rules = mod.make, dict(getattr(mod, "RULES", {}))
        if self.prices:
            plain, priced = make, dict(self.prices)
            make = lambda params, rng: Prices(plain(params, rng), priced, mod.HARMS)
        if self.pay:
            base, pairs, amounts = make, [tuple(p) for p in self.pay], list(self.amounts)
            make = lambda params, rng: Transfers(base(params, rng), pairs, amounts, self.disclosure)
            rules = {name: lift(rule) for name, rule in rules.items()}
            rules.update(getattr(mod, "PAID_RULES", {}))  # rules that use payments themselves
        if self.records:
            inner = make
            make = lambda params, rng: History(inner(params, rng), self.records)
            rules = {name: lift_history(rule) for name, rule in rules.items()}
            if not self.pay:
                rules.update(getattr(mod, "RECORD_RULES", {}))  # rules that read the record themselves
        return mod, make, rules


def baseline(module, fixed, seed):
    """DEFAULTS plus overrides; a register key with no default is drawn with `seed`."""
    space = {**module.SPACE, **fixed}
    rng = random.Random(seed)
    params = {**getattr(module, "DEFAULTS", {}), **fixed}
    for k in space:
        if k not in params:
            params[k] = sample_params({k: space[k]}, rng)[k]
    return params


def apply_state(state, overrides):
    """Start-state overrides; dotted paths reach nested fields (parts.commons.S)."""
    for k, v in overrides.items():
        *path, leaf = k.split(".")
        node = state
        for step in path:
            if not isinstance(node.get(step), dict):
                raise ValueError(f"unknown state path {k!r}")
            child = dict(node[step])
            node[step] = child
            node = child
        if leaf not in node:
            raise ValueError(f"unknown state field {k!r}; choose from {', '.join(node)}")
        node[leaf] = float(v) if isinstance(node[leaf], float) and isinstance(v, int) else v
    return state


def parse_grid(items, space, rules=None):
    """`k=v1,v2` per item. Keys: register parameters, `state.<path>`, `rule` (names from RULES),
    `price.<agent>.<harm>` (amounts, engine/prices.py)."""
    grid = {}
    for item in items or []:
        k, sep, text = item.partition("=")
        if not sep or not k or not text or k in grid:
            raise ValueError(f"expected key=v1,v2 once per key, got {item!r}")
        if k == "rule":
            values = text.split(",")
            if rules is None:
                raise ValueError("a rule grid needs a rule check (--enforce)")
            unknown = [v for v in values if v not in rules]
            if unknown:
                raise ValueError(f"unknown rules {unknown}; choose from: {', '.join(rules)}")
        else:
            values = [parse_value(v) for v in text.split(",")]
            if k.startswith("price."):
                if k.count(".") < 2 or not all(numeric(v) for v in values):
                    raise ValueError(f"expected price.AGENT.HARM=amounts, got {item!r}")
            elif not k.startswith("state."):
                for v in values:
                    validate_fix({k: v}, space)
        if len({json.dumps(v) for v in values}) != len(values):
            raise ValueError(f"repeated value in {item!r}")
        grid[k] = values
    return grid


def cells(module, fixed, grid, draws=None, seed=0, state=None):
    """One dict per cell: draw index, grid values, full parameters, state overrides, rule.
    Without draws every cell starts from `baseline`; with draws, from seeded samples of the
    register (fixed values held), identical whatever is gridded."""
    if draws:
        rng = random.Random(seed)
        space = {**module.SPACE, **fixed}
        bases = [(d, sample_params(space, rng)) for d in range(draws)]
    else:
        bases = [(None, baseline(module, fixed, seed))]
    out = []
    for d, base in bases:
        for values in product(*grid.values()):
            g = dict(zip(grid, values))
            params = {**base, **{k: v for k, v in g.items() if k != "rule" and not k.startswith(("state.", "price."))}}
            overrides = {**(state or {}), **{k[len("state."):]: v for k, v in g.items() if k.startswith("state.")}}
            prices = {":".join(k[len("price."):].split(".", 1)): v for k, v in g.items() if k.startswith("price.")}
            out.append({"draw": d, "grid": g, "params": params, "state": overrides, "rule": g.get("rule"),
                        "prices": prices})
    return out


# Measures: each report flattened into named, comparable strings.

def text(x):
    return x if isinstance(x, str) else json.dumps(x, sort_keys=True)


def size(m):
    if m is None:
        return "unresolved"
    if m["size"] is None:
        return "nobody" if m["exact"] else "unresolved"
    return str(m["size"]) + ("" if m["exact"] else " (upper bound)")


def who(m):
    if m is None or m["size"] is None:
        return size(m)
    return " | ".join("+".join(w) or "(none)" for w in m["witnesses"])


def number(x):
    """A numeric measure, rounded so float noise does not count as a change."""
    return "unresolved" if x is None else round(x, 9)


def numeric(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def minimal(coalitions):
    sets = [frozenset(c) for c in coalitions]
    return [c for c, s in zip(coalitions, sets) if not any(o < s for o in sets)]


def yes(value):
    return "unresolved" if value is None else "yes" if value else "no"


def harm_measures(report):
    out = {}
    for r in report["harms"]:
        h = r["harm"]
        out[f"{h}: realized now"] = yes(r["realized_now"])
        out[f"{h}: force"], out[f"{h}: force by"] = size(r["force"]), who(r["force"])
        out[f"{h}: without the affected"] = "n/a" if r["outsiders_force"] is None else size(r["outsiders_force"])
        out[f"{h}: prevent"], out[f"{h}: prevent by"] = size(r["prevent"]), who(r["prevent"])
        own = r["affected_prevent"]
        out[f"{h}: the affected can prevent"] = ("no agents" if own is None else
                                                 yes(None if own["alpha"] is None else own["alpha"] >= 1 - 1e-12))
        if r["realized_now"]:
            out[f"{h}: end"], out[f"{h}: end by"] = size(r["correct"]), who(r["correct"])
            out[f"{h}: keep"] = size(r["keep"])
            out[f"{h}: veto"] = "unresolved" if r["veto"] is None else "+".join(r["veto"]) or "none"
    for r in report.get("locks") or []:
        out[f"{r['harm']}: lock"], out[f"{r['harm']}: lock by"] = size(r["lock"]), who(r["lock"])
    for c in report["joint_prevention"]:  # per pair: the smallest coalitions that must choose which to prevent
        out[f"forced choice: {' / '.join(c['harms'])}"] = " | ".join("+".join(w) for w in minimal(c["forced_choice"])) or "none"
    return out


def power_measures(report):
    out = {}
    for m in report["thresholds"]:
        out[f"{m['kind']} (p>={m['p']})"], out[f"{m['kind']} by (p>={m['p']})"] = size(m), who(m)
    return out


def rule_measures(report):
    out = {"holds": yes(report["holds_unilaterally"]), "no harmful departure": yes(report["no_harmful_departure"])}
    for i, r in report["unilateral"].items():
        out[f"{i} margin"] = number(r["gain"])  # best one-shot departure over following; <= 0 holds
        if r["gain"] is None:
            out[f"{i} departs"] = "unresolved"
        elif r["gain"] <= TOLERANCE:
            out[f"{i} departs"] = "no"
        else:
            where = "" if r["at_start"] else " (off the start)"
            kind = f" as {r['type']}" if r.get("type") else ""
            out[f"{i} departs"] = f"{text(r.get('rule_action'))} -> {text(r.get('action'))}{kind}{where}"
        h = r.get("harmful")
        out[f"{i} harmful"] = ("no" if h is None or h["gain"] <= TOLERANCE else
                               f"{text(h['action'])}: {', '.join(h['new_harms'])}")
    gain, capture, over = [], [], []
    for c in report["coalitions"]:
        name = "+".join(c["coalition"])
        out[f"{name} gain"] = number(c["gain"])  # summed over members: an upper bound
        for field, label in (("externalizing", "capture gain"), ("externalizing_every", "capture gain, every member")):
            e = c.get(field)
            if field in c:
                out[f"{name} {label}"] = "none" if e is None else number(e.get("gain"))
        if c["gain"] is None or c["gain"] > TOLERANCE:
            gain.append(name + (" (unresolved)" if c["gain"] is None else ""))
        e = c.get("externalizing")
        if e and (e.get("gain") is None or e["gain"] > TOLERANCE):
            capture.append(name + (" (unresolved)" if e.get("gain") is None else
                                   ": " + ", ".join(e["falls_outside"]) + ("" if e["every_member"] else " (paid)")))
        s = c.get("sequential")
        if s and (s.get("gain") is None or (s.get("capture") and s["gain"] > TOLERANCE)):
            over.append(name + (" (unresolved)" if s.get("gain") is None else ""))
    out["coalitions that gain"] = ", ".join(gain) or "none"
    out["capture"] = "; ".join(capture) or "none"
    if report["coalitions"] and "sequential" in report["coalitions"][0]:
        out["capture over rounds"] = ", ".join(over) or "none"
    out["harms if followed"] = ", ".join(report["harms_under_rule"]) or "none"
    return out


def evaluate(setup, query, cell, seed=0):
    """Run one query in one cell. `query`: mode (externalities, power, enforce) and its settings."""
    if cell.get("prices"):
        merged = {**dict(setup.prices), **{tuple(k.split(":", 1)): v for k, v in cell["prices"].items()}}
        setup = replace(setup, prices=tuple(sorted(merged.items())))
    mod, make, rules = setup.build()
    world = make(dict(cell["params"]), random.Random(seed))
    state = apply_state(world.initial_state(), cell["state"])
    mode, T = query["mode"], query["rounds"]
    if mode == "externalities":
        report = {"harms": externalization(world, mod, state, T), "joint_prevention": joint_prevention(world, mod, state, T),
                  "locks": lock_in(world, mod, state, T, query["lock"]) if query.get("lock") else None}
        measures = harm_measures(report)
    elif mode == "power":
        rows = power_table(world, state, T, query.get("target"))
        report = {"rows": rows, "thresholds": [threshold(rows, kind, p) for kind in ("force", "prevent") for p in LEVELS]}
        measures = power_measures(report)
    elif mode == "enforce":
        name = cell["rule"] or query["rule"]
        types = mod.hidden_types(dict(cell["params"]), make) if query.get("hidden") else None
        report = enforcement(world, mod, rules[name], state, T, query.get("reach", 1), query.get("size", 2),
                             window=query.get("window", 1), types=types, precision=query.get("precision", math.inf))
        measures = rule_measures(report)
    else:
        raise ValueError(f"unknown query mode {mode!r}")
    return {**cell, "measures": measures, "report": report}


def _evaluate(job):
    return evaluate(*job)


def run(setup, query, cell_list, seed=0, jobs=None):
    """Evaluate every cell, in parallel unless jobs == 1. Output order is cell order."""
    work = [(setup, query, c, seed) for c in cell_list]
    if jobs == 1 or len(work) < 2:
        return [_evaluate(j) for j in work]
    with Pool(jobs) as pool:
        return pool.map(_evaluate, work, chunksize=1)


# Summary: what is the same everywhere, what changes, with what.

def names(results):
    seen = {}
    for r in results:
        for m in r["measures"]:
            seen.setdefault(m, None)
    return list(seen)


def lines_along(results, key, value):
    """Per setting of every other grid key and the draw, the values `value` takes as `key`
    moves alone. Returns (settings where it changes, settings with at least two cells)."""
    groups = {}
    for r in results:
        rest = (r["draw"], json.dumps({k: v for k, v in r["grid"].items() if k != key}, sort_keys=True))
        groups.setdefault(rest, []).append(value(r))
    lines = [g for g in groups.values() if len(g) > 1]
    return sum(len(set(g)) > 1 for g in lines), len(lines)


def depends(results, keys, value):
    out = {}
    for k in keys:
        changed, total = lines_along(results, k, value)
        if changed:
            out[k] = [changed, total]
    return out


def keys_of(results):
    keys = list(results[0]["grid"]) if results else []
    return keys + (["draw"] if results and results[0]["draw"] is not None else [])


def with_draw_key(results):
    """Treat the draw index as one more key, so flips along it count settings too."""
    return [{**r, "grid": {**r["grid"], "draw": r["draw"]}, "draw": None} for r in results]


def summarize(results, module=None, fixed=None):
    """Per measure: its values and cell counts; if not constant, the keys that change it.
    With draws, also associations with the drawn register values (median splits)."""
    rows = with_draw_key(results) if results and results[0]["draw"] is not None else results
    keys = keys_of(results)
    drawn = {}
    if module is not None and results and results[0]["draw"] is not None:
        gridded = set(results[0]["grid"])
        drawn = {k: v for k, v in module.SPACE.items() if k not in (fixed or {}) and k not in gridded}
    out = []
    for m in names(results):
        value = lambda r, m=m: r["measures"].get(m, "-")
        values = [value(r) for r in results]
        numbers = [v for v in values if numeric(v)]
        entry = {"measure": m, "values": dict(Counter(v for v in values if not numeric(v)))}
        if numbers:
            entry["range"], entry["numeric_cells"] = [min(numbers), max(numbers)], len(numbers)
        entry["constant"] = len(set(values)) == 1
        if not entry["constant"]:
            entry["depends_on"] = depends(rows, keys, value)
            if drawn:
                pseudo = [{"params": r["params"], "label": value(r)} for r in results]
                entry["associations"] = dependence(pseudo, drawn)
        out.append(entry)
    return out


def compare(results, key):
    """Pairs of cells that differ only in `key`: per other value of it, per measure, the
    transitions from the first value, and the keys along which the transition changes."""
    if not results or key not in results[0]["grid"]:
        raise ValueError(f"--compare {key}: not a grid key")
    order = []
    for r in results:
        if r["grid"][key] not in order:
            order.append(r["grid"][key])
    first, rest_keys = order[0], [k for k in keys_of(results) if k != key]
    base = {}
    for r in results:
        if r["grid"][key] == first:
            base[(r["draw"], json.dumps({k: v for k, v in r["grid"].items() if k != key}, sort_keys=True))] = r
    report = {"key": key, "baseline": first, "against": []}
    for other in order[1:]:
        pairs = []
        for r in results:
            if r["grid"][key] != other:
                continue
            b = base[(r["draw"], json.dumps({k: v for k, v in r["grid"].items() if k != key}, sort_keys=True))]
            pairs.append((b, r))
        rows = [{"draw": r["draw"], "grid": {k: v for k, v in r["grid"].items() if k != key}, "pair": (b, r)}
                for b, r in pairs]
        if rows and rows[0]["draw"] is not None:
            rows = with_draw_key(rows)
        measures = []
        for m in names([p for pair in pairs for p in pair]):
            def move(row, m=m):
                a, b = row["pair"][0]["measures"].get(m, "-"), row["pair"][1]["measures"].get(m, "-")
                if numeric(a) and numeric(b):  # numbers: the direction, not the values
                    return "rises" if b > a + NUMERIC else "falls" if b < a - NUMERIC else "same"
                return (a, b)
            moves = [move(row) for row in rows]
            changed = [row for row, x in zip(rows, moves) if x not in ("same",) and not (isinstance(x, tuple) and x[0] == x[1])]
            entry = {"measure": m, "pairs": len(rows), "changed": len(changed),
                     "directions": dict(Counter(x for x in moves if isinstance(x, str))),
                     "transitions": [{"from": a, "to": b, "count": n}
                                     for (a, b), n in Counter(x for x in moves if isinstance(x, tuple)).items()]}
            if changed:
                entry["depends_on"] = depends(rows, rest_keys, move)
            measures.append(entry)
        report["against"].append({"value": other, "measures": measures})
    return report


def render(summary, comparison=None, header=""):
    lines = [header] if header else []
    same = [e for e in summary if e["constant"]]
    varied = [e for e in summary if not e["constant"]]
    lines.append(f"\nSAME IN EVERY CELL ({len(same)} measures)")
    def shown(e):
        parts = [f"{e['range'][0]:g}..{e['range'][1]:g} ({e['numeric_cells']})"] if "range" in e else []
        return "; ".join(parts + [f"{v} ({n})" for v, n in e["values"].items()])
    for e in same:
        lines.append(f"  {e['measure']}: " + (f"{e['range'][0]:g}" if "range" in e else next(iter(e["values"]))))
    lines.append(f"\nCHANGES ACROSS THE GRID ({len(varied)} measures)")
    for e in varied:
        lines.append(f"  {e['measure']}: {shown(e)}")
        along = ", ".join(f"{k} ({c} of {t})" for k, (c, t) in e.get("depends_on", {}).items())
        lines.append(f"      moving one key alone changes it: {along or 'no single key (only joint moves)'}")
        for a in e.get("associations", [])[:3]:
            lines.append(f"      association with drawn {a['param']} (effect {a['effect']})")
    if comparison:
        for block in comparison["against"]:
            moved = [e for e in block["measures"] if e["changed"]]
            n = block["measures"][0]["pairs"] if block["measures"] else 0
            lines.append(f"\nCOMPARED: {comparison['key']} = {comparison['baseline']} -> {block['value']} "
                         f"({n} paired settings; {len(block['measures']) - len(moved)} measures never move)")
            for e in moved:
                moves = "; ".join([f"{d} ({n})" for d, n in e["directions"].items()]
                                  + [f"{t['from']} => {t['to']} ({t['count']})" for t in e["transitions"] if t["from"] != t["to"]])
                lines.append(f"  {e['measure']}: changes in {e['changed']} of {e['pairs']}: {moves}")
                along = ", ".join(f"{k} ({c} of {t})" for k, (c, t) in e.get("depends_on", {}).items())
                if along:
                    lines.append(f"      the change itself moves with: {along}")
    lines.append("\nSame in every cell means across this grid only; untested values and unmodeled mechanisms remain open.")
    return "\n".join(lines)
