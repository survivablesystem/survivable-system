"""CLI.

    python -m engine worlds.commons                       sweep the world's SPACE
    python -m engine worlds.commons --fix n=4 horizon=12  sweep with some params fixed
    python -m engine worlds.commons --trace --fix n=4     play one world and print each round
    python -m engine worlds.commons --trace --profile 3   ...beside what coalitions could force each round
    python -m engine worlds.commons --oat                 move one parameter at a time from DEFAULTS
    python -m engine worlds.commons --power 3             what each coalition can force within 3 rounds
    python -m engine worlds.commons --externalities 3 --state S=20   per declared harm: who can force, impose, prevent
    python -m engine worlds.authority --externalities 2 --lock 3      ...and who can force it, then keep it 3 rounds
    python -m engine worlds.treaty --enforce 4 --rule restraint       does a declared rule hold; who profits by breaking it
    python -m engine worlds.audit --enforce 4 --rule independence --pay firm>a0   ...when the firm can pay its auditor
"""
import argparse
import importlib
import json
import math
import random

from .power import BUDGET, externalization, joint_prevention, lock_in, power_table, profile, threshold
from .records import artifact, run_record
from .rules import enforcement
from .transfers import Transfers, lift
from .sweep import one_at_a_time, report, report_oat, sample_params, sweep


def parse_fix(items):
    out = {}
    for item in items or []:
        if "=" not in item:
            raise ValueError(f"expected param=value, got {item!r}")
        k, v = item.split("=", 1)
        if not k or not v or k in out:
            raise ValueError(f"empty or duplicate override: {item!r}")
        for cast in (int, float):
            try:
                out[k] = cast(v)
                break
            except ValueError:
                continue
        else:
            out[k] = {"true": True, "false": False}.get(v.lower(), v)
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


def positive_int(value):
    n = int(value)
    if n < 1:
        raise argparse.ArgumentTypeError("must be a positive integer")
    return n


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("world", help="module path, e.g. worlds.commons")
    p.add_argument("--samples", type=positive_int, default=100)
    p.add_argument("--rounds", type=positive_int, default=40)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--fix", nargs="*", help="param=value pairs held fixed")
    mode = p.add_mutually_exclusive_group()
    mode.add_argument("--trace", action="store_true", help="play one world (DEFAULTS plus --fix) and print rounds")
    mode.add_argument("--oat", action="store_true", help="vary unfixed parameters from DEFAULTS plus --fix")
    mode.add_argument("--power", type=positive_int, metavar="T",
                      help="goal-free: what each coalition can force or prevent within T rounds from the initial state")
    mode.add_argument("--externalities", type=positive_int, metavar="T",
                      help="goal-free, per declared harm: who can force it, impose it from outside, or prevent it within T rounds")
    mode.add_argument("--enforce", type=positive_int, metavar="D",
                      help="goal-based: does the world's rule --rule hold within D rounds (one-shot departures); who profits by breaking it")
    p.add_argument("--rule", help="with --enforce: a name from the world's RULES")
    p.add_argument("--reach", type=int, default=1, help="with --enforce: check states within this many rounds (default 1)")
    p.add_argument("--size", type=positive_int, default=2, help="with --enforce: largest coalition checked (default 2)")
    p.add_argument("--pay", nargs="*", metavar="PAYER>RECIPIENT",
                   help="any mode: wrap the world so these agents may pay each other (side payments, engine/transfers.py)")
    p.add_argument("--amounts", nargs="*", type=float, default=[0.5, 1.0], help="with --pay: payment sizes (utility)")
    p.add_argument("--disclosure", choices=["parties", "public"], default="parties", help="with --pay: who sees payments")
    p.add_argument("--state", nargs="*", help="key=value overrides of top-level initial-state fields for --power/--externalities")
    p.add_argument("--lock", type=positive_int, metavar="K",
                   help="with --externalities: smallest coalition that can force each harm and then keep it K rounds against everyone")
    p.add_argument("--profile", type=positive_int, metavar="T",
                   help="with --trace: smallest coalitions able to force/prevent the target within T rounds, each round")
    p.add_argument("--target", nargs="*", help="terminal labels for --power/--profile (default: any terminal)")
    p.add_argument("--seeds", type=positive_int, default=4, help="seeds per point for --oat")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()

    if args.profile and not args.trace:
        p.error("--profile requires --trace")
    if args.lock and not args.externalities:
        p.error("--lock requires --externalities")
    mod = importlib.import_module(args.world)
    space = dict(mod.SPACE)
    try:
        fixed = parse_fix(args.fix)
        validate_fix(fixed, space)
    except ValueError as error:
        p.error(str(error))
    space.update(fixed)
    settings = {"seed": args.seed, "rounds": args.rounds, "overrides": fixed}
    make, rules = mod.make, dict(getattr(mod, "RULES", {}))
    if args.pay:
        pairs = [tuple(x.split(">", 1)) for x in args.pay]
        if any(len(pair) != 2 for pair in pairs):
            p.error("--pay expects PAYER>RECIPIENT")
        make = lambda params, rng: Transfers(mod.make(params, rng), pairs, args.amounts, args.disclosure)
        rules = {name: lift(rule) for name, rule in rules.items()}
        rules.update(getattr(mod, "PAID_RULES", {}))  # rules that use payments themselves
        settings["transfers"] = {"pairs": pairs, "amounts": args.amounts, "disclosure": args.disclosure}

    def emit(mode_name, results):
        print(json.dumps(artifact(mod, mode_name, settings, results), indent=2,
                         sort_keys=True, allow_nan=False))

    def baseline_params():
        rng = random.Random(args.seed)
        params = {**getattr(mod, "DEFAULTS", {}), **fixed}
        for k in space:
            if k not in params:
                params[k] = sample_params({k: space[k]}, rng)[k]
        return params

    def start_state(world):
        state = world.initial_state()
        try:
            overrides = parse_fix(args.state)
        except ValueError as error:
            p.error(str(error))
        for k, v in overrides.items():
            *path, leaf = k.split(".")  # dotted paths reach nested fields, e.g. parts.commons.S
            node = state
            for step in path:
                if not isinstance(node.get(step), dict):
                    p.error(f"unknown state path {k!r}")
                child = dict(node[step])
                node[step] = child
                node = child
            if leaf not in node:
                p.error(f"unknown state field {k!r}; choose from {', '.join(node)}")
            node[leaf] = float(v) if isinstance(node[leaf], float) and isinstance(v, int) else v
        settings["state_overrides"] = overrides
        return state

    if args.enforce:
        if args.rule not in rules:
            p.error(f"--enforce needs --rule, one of: {', '.join(rules) or '(world declares no RULES)'}")
        params = baseline_params()
        world = make(dict(params), random.Random(args.seed))
        report = enforcement(world, mod, rules[args.rule], start_state(world), args.enforce, args.reach, args.size)
        settings.update({"baseline": params, "rule": args.rule, "rule_claim": (rules[args.rule].__doc__ or "").strip(),
                         "depth": args.enforce, "reach": args.reach, "max_size": args.size,
                         "query": "One-shot departures, then everyone follows the rule for the rest of D rounds; unilateral with own information, coalitions with full information and summed value (upper bound)."})
        if args.json:
            emit("enforce", report)
            return
        fmt = lambda v: "unresolved" if v is None else f"{v:+.3f}"
        print(f"params: {params}\nrule: {args.rule}: {settings['rule_claim']}")
        print(f"within {args.enforce} rounds; {report['states_checked']} states checked (reach {args.reach})")
        print(f"holds against every one-shot unilateral departure: {report['holds_unilaterally']}; "
              f"no single agent gains by a harmful one: {report['no_harmful_departure']}")
        for i, r in report["unilateral"].items():
            where = "" if r["gain"] is None else (" at the start" if r["at_start"] else " off the start")
            print(f"  {i:10s} best departure {fmt(r['gain'])}{where}" + (f" ({r['rule_action']} -> {r['action']})" if r.get("action") is not None and r["gain"] > 1e-9 else ""))
            h = r.get("harmful")
            if h is not None and h["gain"] > 1e-9:
                print(f"             harmful departure {fmt(h['gain'])} ({h['action']}) reaches {', '.join(h['new_harms'])}")
        profitable = [r for r in report["coalitions"] if r["gain"] is None or r["gain"] > 1e-9]
        print("coalitions that gain by departing together (upper bound):" + ("" if profitable else " none"))
        for r in profitable:
            print(f"  {','.join(r['coalition']):20s} {fmt(r['gain'])} {r.get('actions', '')}")
        capture = [r for r in report["coalitions"] if (r.get("externalizing") or {}).get("gain", 0) > 1e-9]
        print("coalitions that gain by departing onto others (a harm on outsiders):" + ("" if capture else " none"))
        for r in capture:
            e = r["externalizing"]
            print(f"  {','.join(r['coalition']):20s} {fmt(e['gain'])} {e['actions']}"
                  f"{' at the start' if e['at_start'] else ' off the start'}"
                  f"{'' if e['every_member'] else ' (needs side payments: a member loses or gains nothing)'}")
            for h, names in e["falls_outside"].items():
                print(f"      reaches {h}, falling on {', '.join(names)}")
            n = r.get("externalizing_every")
            if n is not None and not e["every_member"]:
                print(f"      paying every member: {fmt(n['gain'])} {n['actions']}")
        print(f"harms reached if everyone follows: {', '.join(report['harms_under_rule']) or 'none'}")
        print("Goals are read here: this is whether the rule pays, under the stated goals and depth.")
        return

    if args.externalities:
        params = baseline_params()
        world = make(dict(params), random.Random(args.seed))
        start = start_state(world)
        report = externalization(world, mod, start, args.externalities)
        choices = [r for r in joint_prevention(world, mod, start, args.externalities) if r["forced_choice"]]
        locks = lock_in(world, mod, start, args.externalities, args.lock) if args.lock else None
        settings.update({"baseline": params, "power_rounds": args.externalities, "budget": BUDGET, "keep_rounds": args.lock,
                         "query": "Goal-free, per declared harm: force, force without affected agents, prevent, prevent by the affected; p=1."})
        if args.json:
            emit("externalities", {"harms": report, "forced_choices": choices, "locks": locks})
            return
        locked = {r["harm"]: r["lock"] for r in locks or []}
        size = lambda m: "unresolved" if m is None else ("nobody" if m["size"] is None else
                                                        f"{m['size']} {m['witnesses'][:3]}") + ("" if m is None or m["exact"] else " (upper bound)")
        print(f"params: {params}\nwithin {args.externalities} rounds, with certainty (p=1):")
        for r in report:
            own = r["affected_prevent"]
            print(f"\nharm: {r['harm']}{' (irreversible)' if r['irreversible'] else ''}{'  [realized now]' if r['realized_now'] else ''}")
            print(f"  falls on: {', '.join(r['affects'])}")
            if r["unrepresented"]:
                print(f"  no agent in the model: {', '.join(r['unrepresented'])}")
            print(f"  smallest coalition that can force it: {size(r['force'])}")
            print(f"  ... without any affected agent: {size(r['outsiders_force'])}")
            print(f"  smallest coalition that can prevent it: {size(r['prevent'])}")
            verdict = lambda v: ("no agents" if v is None else "?" if v["alpha"] is None else
                                 f"{'yes' if v['alpha'] >= 1 - 1e-12 else 'no'} (probability {v['alpha']:.3f})")
            if r["harm"] in locked:
                print(f"  ... and then keep it {args.lock} rounds against everyone (lock): {size(locked[r['harm']])}")
            if r["realized_now"]:
                print(f"  realized now; smallest coalition that can end it: {size(r['correct'])}")
                print(f"  ... that can keep it against everyone: {size(r['keep'])}")
                print(f"  without these agents nobody can end it (veto): {r['veto'] if r['veto'] is not None else 'unresolved'}")
                print(f"  affected agents together can end it: {verdict(r['affected_correct'])}")
            else:
                print(f"  affected agents together can prevent it: {verdict(own)}")
        print("\nForced choices (can prevent each harm alone, not both):" + ("" if choices else " none"))
        for r in choices:
            print(f"  {' / '.join(r['harms'])}: {r['forced_choice']}")
        print("\nExcluded from the model:")
        for name, reason in mod.EXCLUDED.items():
            print(f"  {name}: {reason}")
        print("Power ignores goals: this is what could be forced or prevented, not what will happen.")
        return

    if args.power:
        params = baseline_params()
        world = make(dict(params), random.Random(args.seed))
        target = args.target or None
        rows = power_table(world, start_state(world), args.power, target)
        marks = [threshold(rows, kind, level) for kind in ("force", "prevent") for level in (1.0, 0.5)]
        settings.update({"baseline": params, "power_rounds": args.power, "target": target, "budget": BUDGET,
                         "query": "Goal-free finite-horizon reachability from the initial state; coordinated full-information adversary; alpha/beta stage orders bracket randomized play."})
        if args.json:
            emit("power", {"rows": rows, "thresholds": marks})
            return
        fmt = lambda v: "  ?  " if v is None else f"{v:.3f}"
        print(f"params: {params}\ntarget: {target or 'any terminal'} within {args.power} rounds")
        print("coalition                    force[alpha,beta]   prevent[alpha,beta]")
        for r in rows:
            name = ",".join(r["coalition"]) or "(none)"
            f, v = r["force"], r["prevent"]
            print(f"{name:28s} {fmt(f['alpha'])} {fmt(f['beta'])}        {fmt(v['alpha'])} {fmt(v['beta'])}")
        for m in marks:
            size = "none within T" if m["size"] is None else m["size"]
            print(f"smallest coalition to {m['kind']} with p>={m['p']}: {size}{'' if m['exact'] else ' (upper bound)'}")
        print("Power ignores goals: it says what could be forced, not what agents will do. ? = work cap.")
        return

    if args.trace:
        params = baseline_params()
        result = run_record(make, params, args.rounds, args.seed, include_trace=True)
        settings["baseline"] = params
        if args.profile:
            world = make(dict(params), random.Random(args.seed))
            result["power_profile"] = profile(world, result["trace"], args.profile, args.target or None)
            settings["query"] = "Per round: goal-free finite-horizon power from the state the round started in."
        if args.json:
            emit("trace", [result])
            return
        print("params:", params)
        powers = {e["round"]: e for e in result.get("power_profile", {}).get("rounds", [])}
        size = lambda m: ("-" if m["size"] is None else str(m["size"])) + ("" if m["exact"] else "?")
        for entry in result["trace"]:
            line = f"round {entry['round']:3d}  " + mod.describe(entry["actions"], entry["state"])
            if entry["round"] in powers:
                e = powers[entry["round"]]
                f, v = e["thresholds"][0], e["thresholds"][2]
                flag = "  SEALED" if e["sealed"] else "  FRAGILE" if e["fragile"] else ""
                line += f"   before: force {size(f)} prevent {size(v)}{flag}"
            print(line)
        if args.profile:
            prof = result["power_profile"]
            print(f"power within {args.profile} rounds, p=1, smallest coalition (- none, ? upper bound): "
                  f"first fragile round {prof['first_fragile']}, first sealed round {prof['first_sealed']}")
        print(f"status: {result['status']}; outcome: {result['label']}; rounds run: {result['rounds_run']}/{args.rounds}; terminal: {result['terminal']}")
        print("planning:", result["planning"])
        if "error" in result:
            print(result["error"]["message"])
        print("Finite duration only; no convergence or real-world probability is established.")
        return

    if args.oat:
        baseline = {**getattr(mod, "DEFAULTS", {}), **fixed}
        settings.update({"baseline": baseline, "seeds_per_point": args.seeds,
                         "sampling": "Unfixed categorical values or numeric endpoints; matched integer seeds at every point."})
        rows = one_at_a_time(make, space, baseline, args.seeds, args.rounds, args.seed)
        if args.json:
            emit("oat", rows)
        else:
            print(f"world: {mod.__name__}; round limit: {args.rounds}; seeds per point: {args.seeds}")
            print(report_oat(rows))
            print("Shares are over tested assumptions, not probabilities of the world.")
        return

    settings.update({"samples": args.samples,
                     "sampling": "Independent uniform parameter draws; each run gets a recorded 64-bit integer seed."})
    rows = sweep(make, space, args.samples, args.rounds, args.seed)
    if args.json:
        emit("sweep", rows)
    else:
        print(f"world: {mod.__name__}; round limit: {args.rounds}")
        print(report(rows, space))


if __name__ == "__main__":
    main()
