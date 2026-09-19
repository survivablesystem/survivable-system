"""CLI.

    python -m engine worlds.commons                       sweep the world's SPACE
    python -m engine worlds.commons --fix n=4 horizon=12  sweep with some params fixed
    python -m engine worlds.commons --trace --fix n=4     play one world and print each round
    python -m engine worlds.commons --oat                 move one parameter at a time from DEFAULTS
"""
import argparse
import importlib
import json
import random

from .core import run
from .sweep import one_at_a_time, report, report_oat, sample_params, sweep


def parse_fix(items):
    out = {}
    for item in items or []:
        k, v = item.split("=", 1)
        for cast in (int, float):
            try:
                out[k] = cast(v)
                break
            except ValueError:
                continue
        else:
            out[k] = {"true": True, "false": False}.get(v.lower(), v)
    return out


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("world", help="module path, e.g. worlds.commons")
    p.add_argument("--samples", type=int, default=100)
    p.add_argument("--rounds", type=int, default=40)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--fix", nargs="*", help="param=value pairs held fixed")
    p.add_argument("--trace", action="store_true", help="play one world (DEFAULTS plus --fix) and print rounds")
    p.add_argument("--oat", action="store_true", help="one parameter at a time from DEFAULTS plus --fix")
    p.add_argument("--seeds", type=int, default=4, help="seeds per point for --oat")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()

    mod = importlib.import_module(args.world)
    space = dict(mod.SPACE)
    fixed = parse_fix(args.fix)
    space.update(fixed)

    if args.trace:
        rng = random.Random(args.seed)
        params = {**getattr(mod, "DEFAULTS", {}), **fixed}
        for k in space:
            params.setdefault(k, sample_params({k: space[k]}, rng)[k])
        world = mod.make(params, rng)
        label, state, trace = run(world, args.rounds, world.rng)
        print("params:", params)
        for t, (joint, s) in enumerate(trace):
            print(f"round {t:3d}  " + mod.describe(joint, s))
        print("label:", label)
        return

    if args.oat:
        baseline = {**getattr(mod, "DEFAULTS", {}), **fixed}
        print(f"world: {mod.__name__}")
        print(report_oat(one_at_a_time(mod.make, mod.SPACE, baseline, args.seeds, args.rounds, args.seed)))
        return

    rows = sweep(mod.make, space, args.samples, args.rounds, args.seed)
    if args.json:
        print(json.dumps({"rows": rows}, indent=1, default=str))
    else:
        print(f"world: {mod.__name__}")
        print(report(rows, space))


if __name__ == "__main__":
    main()
