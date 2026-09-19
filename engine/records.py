"""Finite-run evidence. No inference about convergence or real-world probability."""
import hashlib
from pathlib import Path
import platform
import random
import subprocess

from .core import SearchLimitExceeded, run


def run_record(make_world, params, rounds, seed, *, include_trace=False):
    if rounds < 1:
        raise ValueError("rounds must be positive")
    world = make_world(dict(params), random.Random(seed))
    failure = None
    try:
        label, state, trace = run(world, rounds, world.rng)
    except SearchLimitExceeded as error:
        label, state, trace = None, error.state, error.trace
        failure = {"agent": error.agent, "node_budget": error.budget, "message": str(error)}
    record = {
        "params": dict(params), "seed": seed, "rounds_requested": rounds,
        "rounds_run": len(trace), "label": label,
        "terminal": world.terminal(state), "final_state": state,
        "status": "search_limit" if failure else "complete",
        "planning": {a.id: {"horizon": a.horizon, "effective_depth": a.depth,
                            "node_budget": a.node_budget, "k": a.k} for a in world.agents},
    }
    if failure:
        record["error"] = failure
    if include_trace:
        record["trace"] = [{"round": t + 1, "actions": actions, "state": s}
                           for t, (actions, s) in enumerate(trace)]
    return record


def register(space):
    """Describe sampling without losing integer/float types in JSON."""
    out = {}
    for key, spec in space.items():
        if isinstance(spec, list):
            out[key] = {"kind": "choice", "values": spec}
        elif isinstance(spec, tuple):
            out[key] = {"kind": "int" if len(spec) == 3 and spec[2] is int else "float",
                        "min": spec[0], "max": spec[1]}
        else:
            out[key] = {"kind": "fixed", "value": spec}
    return out


def provenance():
    root = Path(__file__).resolve().parents[1]

    def git(*args):
        try:
            return subprocess.check_output(["git", *args], cwd=root,
                                           stderr=subprocess.DEVNULL, text=True).strip()
        except (OSError, subprocess.CalledProcessError):
            return None

    # Normalize line endings so Windows and Linux identify the same source text.
    paths = sorted([*root.joinpath("engine").rglob("*.py"),
                    *root.joinpath("worlds").rglob("*.py"),
                    *root.joinpath("spec").rglob("*.md"), root / "INTENT.md"])
    hashes = {p.relative_to(root).as_posix(): hashlib.sha256(
        p.read_text(encoding="utf-8").encode("utf-8")).hexdigest() for p in paths}
    status = git("status", "--porcelain", "--untracked-files=normal")
    return {"git_commit": git("rev-parse", "HEAD"),
            "git_dirty": bool(status) if status is not None else None,
            "python": platform.python_version(), "implementation": platform.python_implementation(),
            "source_sha256": hashes}


def artifact(module, mode, settings, results):
    reasons = module.FIXED_REASONS
    if set(reasons) != set(module.FIXED) or not all(reasons.values()):
        raise ValueError("FIXED_REASONS must provide a nonempty reason for every FIXED value")
    return {
        "schema_version": 2, "world": module.__name__, "mode": mode,
        "provenance": provenance(), "settings": settings,
        "register": register(module.SPACE), "defaults": module.DEFAULTS,
        "fixed": {k: {"value": v, "reason": reasons[k]} for k, v in module.FIXED.items()},
        "limitations": [
            "Shares describe sampled assumptions, not probabilities of the world.",
            "Nonterminal outcomes only describe survival through the recorded duration.",
            "Finite belief-tree search is exact only within declared support, effective depth and opponent model; no utility beyond the depth cap is estimated.",
            "Search-limit runs are unresolved, not survival or collapse; shares retain them in the denominator.",
            "Beliefs and observations are authored; known topology/utilities and direct-observer level-0 responses are assumptions, not equilibrium reasoning.",
            "Information isolation is a world contract; history across real rounds must be represented by the world.",
            "One-at-a-time endpoints omit interactions; random-sweep associations are not causal effects.",
            "Source hashes cover local engine, worlds, spec and intent; external data/dependencies need separate provenance.",
        ],
        "results": results,
    }
