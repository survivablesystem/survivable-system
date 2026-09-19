"""Sweep a world over its assumptions register and report attractor shares.

Two modes. `sweep` samples the whole register at random and reports attractor shares
with a dependence table (median split per numeric parameter, per value for categorical
ones). `one_at_a_time` starts from a baseline and moves one parameter at a time; it is
the informative view when an outcome needs several conditions at once, which a random
sweep buries (commons: sustained in 2% of random samples, no parameter above threshold).
"""
from __future__ import annotations

import random
from statistics import median

from .core import run


def sample_params(space: dict, rng: random.Random) -> dict:
    """space values: list -> categorical; (lo, hi) -> float; (lo, hi, int) -> int; anything else -> fixed."""
    out = {}
    for k, spec in space.items():
        if isinstance(spec, list):
            out[k] = rng.choice(spec)
        elif isinstance(spec, tuple) and len(spec) == 3 and spec[2] is int:
            out[k] = rng.randint(spec[0], spec[1])
        elif isinstance(spec, tuple) and len(spec) == 2:
            out[k] = rng.uniform(spec[0], spec[1])
        else:
            out[k] = spec
    return out


def sweep(make_world, space: dict, samples: int, rounds: int, seed: int = 0) -> list:
    rng = random.Random(seed)
    rows = []
    for _ in range(samples):
        params = sample_params(space, rng)
        world = make_world(params, random.Random(rng.random()))
        label, _, _ = run(world, rounds, world.rng)
        rows.append((params, label))
    return rows


def shares(rows: list) -> dict:
    n = len(rows)
    labels = sorted({label for _, label in rows})
    return {lab: sum(1 for _, l in rows if l == lab) / n for lab in labels}


def dependence(rows: list, space: dict, threshold: float = 0.2) -> list:
    """Parameters whose value moves an attractor share by more than `threshold`."""
    out = []
    for k, spec in space.items():
        if not isinstance(spec, (list, tuple)):
            continue
        values = [p[k] for p, _ in rows]
        if isinstance(spec, list):
            groups = {v: [r for r in rows if r[0][k] == v] for v in spec}
        else:
            m = median(values)
            groups = {f"<={m:.3g}": [r for r in rows if r[0][k] <= m],
                      f">{m:.3g}": [r for r in rows if r[0][k] > m]}
        groups = {g: r for g, r in groups.items() if r}
        if len(groups) < 2:
            continue
        per_group = {g: shares(r) for g, r in groups.items()}
        labels = {lab for s in per_group.values() for lab in s}
        effect = max(
            max(s.get(lab, 0.0) for s in per_group.values()) - min(s.get(lab, 0.0) for s in per_group.values())
            for lab in labels
        )
        if effect > threshold:
            out.append({"param": k, "effect": round(effect, 2),
                        "shares": {g: {lab: round(v, 2) for lab, v in s.items()} for g, s in per_group.items()}})
    return sorted(out, key=lambda d: -d["effect"])


def one_at_a_time(make_world, space: dict, baseline: dict, seeds: int = 4, rounds: int = 30, seed: int = 0) -> list:
    """For each swept parameter, hold everything else at the baseline and try each categorical
    value, or the low and high end of a numeric range. Returns rows of (param, value, shares)."""
    def shares_at(params):
        labels = []
        for s in range(seeds):
            world = make_world(params, random.Random(seed + s))
            labels.append(run(world, rounds, world.rng)[0])
        return {lab: labels.count(lab) / len(labels) for lab in sorted(set(labels))}

    rows = [("baseline", None, shares_at(baseline))]
    for k, spec in space.items():
        if isinstance(spec, list):
            values = spec
        elif isinstance(spec, tuple):
            values = [spec[0], spec[1]]
        else:
            continue
        for v in values:
            if v == baseline.get(k):
                continue
            rows.append((k, v, shares_at({**baseline, k: v})))
    return rows


def report_oat(rows: list, threshold: float = 0.25) -> str:
    base = rows[0][2]
    lines = ["baseline: " + ", ".join(f"{lab}={s:.2f}" for lab, s in base.items()), "moved alone:"]
    for k, v, s in rows[1:]:
        labels = set(base) | set(s)
        effect = max(abs(s.get(lab, 0.0) - base.get(lab, 0.0)) for lab in labels)
        mark = "  <-- flips" if effect >= threshold else ""
        lines.append(f"  {k}={v}: " + ", ".join(f"{lab}={s.get(lab, 0.0):.2f}" for lab in sorted(labels)) + mark)
    return "\n".join(lines)


def report(rows: list, space: dict) -> str:
    lines = [f"samples: {len(rows)}", "attractor shares:"]
    for lab, s in shares(rows).items():
        lines.append(f"  {lab}: {s:.2f}")
    deps = dependence(rows, space)
    lines.append("depends on:" if deps else "depends on: nothing above threshold")
    for d in deps:
        detail = "; ".join(f"{g}: " + ", ".join(f"{lab}={v}" for lab, v in s.items()) for g, s in d["shares"].items())
        lines.append(f"  {d['param']} (effect {d['effect']}): {detail}")
    lines.append("not modeled: anything outside the world file. Shares are over the sweep, not probabilities of the world.")
    return "\n".join(lines)
