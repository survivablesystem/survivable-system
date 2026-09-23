"""One-screen assessment of a world and, optionally, a proposed rule (task A3).

Ordered by robustness: first what holds whatever anyone wants (goal-free power over the
declared harms), then what depends on stated goals (whether the rule pays, who breaks it,
who captures it), then what the model leaves out. Every line names who bears the harm.
"""
from __future__ import annotations

from .power import externalization, joint_prevention, lock_in
from .rules import enforcement


def assess(world, module, state, rounds, rule=None, keep=None, depth=4, reach=1, window=2):
    members = world.stakeholders()
    report = {"stakeholders": {name: {"agents": ids, "represented": bool(ids)} for name, ids in members.items()},
              "power": externalization(world, module, state, rounds),
              "forced_choices": [r for r in joint_prevention(world, module, state, rounds) if r["forced_choice"]],
              "locks": lock_in(world, module, state, rounds, keep) if keep else None,
              "rule": None, "excluded": dict(module.EXCLUDED),
              "settings": {"rounds": rounds, "keep": keep, "depth": depth, "reach": reach, "window": window}}
    if rule is not None:
        r = enforcement(world, module, rule, state, depth, reach, max_size=2, window=window)
        harmful = {i: {k: u["harmful"][k] for k in ("gain", "action", "new_harms", "at_start")}
                   for i, u in r["unilateral"].items() if u.get("harmful") and u["harmful"]["gain"] > 1e-9}
        capture = []
        for c in r["coalitions"]:
            for kind, e in (("same round", c.get("externalizing")), ("over rounds", c.get("sequential"))):
                if not e or e.get("gain") is None or e["gain"] <= 1e-9:
                    continue
                if kind == "over rounds" and not e.get("capture"):
                    continue
                capture.append({"coalition": c["coalition"], "kind": kind, "gain": e["gain"],
                                "needs_payment": not e["every_member"], "falls_on": e["falls_outside"],
                                "actions": e.get("actions") or e.get("first")})
        report["rule"] = {"claim": (rule.__doc__ or "").strip(), "holds": r["holds_unilaterally"],
                          "no_harmful_departure": r["no_harmful_departure"], "harmful": harmful,
                          "capture": sorted(capture, key=lambda x: -x["gain"]), "harms_if_followed": r["harms_under_rule"]}
    return report


def render(report, params):
    size = lambda m: "unresolved" if m is None else ("nobody" if m["size"] is None else
                                                     f"{m['size']}: {', '.join('+'.join(w) or '(none)' for w in m['witnesses'][:2])}")
    lines = [f"assumptions: {params}", ""]
    unrepresented = [n for n, s in report["stakeholders"].items() if not s["represented"]]
    lines.append(f"stakeholders without an agent: {', '.join(unrepresented) or 'none'}")
    s = report["settings"]
    lines.append(f"\nWHAT CAN BE FORCED (goal-free, within {s['rounds']} rounds, certainty)")
    locks = {r["harm"]: r["lock"] for r in report["locks"] or []}
    for h in report["power"]:
        tag = " [irreversible]" if h["irreversible"] else ""
        tag += " [happening now]" if h["realized_now"] else ""
        lines.append(f"- {h['harm']}{tag}, falls on {', '.join(h['affects'])}")
        lines.append(f"    force: {size(h['force'])}; without the affected: {size(h['outsiders_force'])}; prevent: {size(h['prevent'])}")
        if h["harm"] in locks:
            lines.append(f"    force and keep {s['keep']} rounds against everyone: {size(locks[h['harm']])}")
        if h["realized_now"]:
            lines.append(f"    end it: {size(h['correct'])}; veto on ending it: {h['veto']}")
    for c in report["forced_choices"]:
        lines.append(f"- forced choice {' / '.join(c['harms'])}: {c['forced_choice'][:3]}")
    rule = report["rule"]
    if rule is not None:
        lines.append(f"\nDOES THE RULE HOLD (depends on the stated goals; depth {s['depth']}, one round off the path)")
        lines.append(f"  {rule['claim']}")
        lines.append(f"  every single agent keeps to it: {rule['holds']}; no single agent gains by a harmful departure: {rule['no_harmful_departure']}")
        for i, h in rule["harmful"].items():
            lines.append(f"  - {i} gains {h['gain']:+.2f} by {h['action']}{'' if h['at_start'] else ' (off the start)'}, reaching {', '.join(h['new_harms'])}")
        lines.append("  capture (needs the pair; the harm lands outside it):" + ("" if rule["capture"] else " none found"))
        for c in rule["capture"][:6]:
            falls = "; ".join(f"{h} on {', '.join(n)}" for h, n in c["falls_on"].items())
            lines.append(f"  - {'+'.join(c['coalition'])} {c['kind']} {c['gain']:+.2f}{', needs a payment' if c['needs_payment'] else ''}: {falls}")
    lines.append("\nNOT IN THE MODEL")
    for name, reason in report["excluded"].items():
        lines.append(f"- {name}: {reason}")
    lines.append("\nNot a forecast: what these assumptions imply. Power ignores goals; the rule section does not.")
    return "\n".join(lines)
