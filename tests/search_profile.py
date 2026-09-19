"""T1.4 reproducible work profile. Run as python -m tests.search_profile."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import random
from time import perf_counter

from engine.core import Search, SearchLimitExceeded, key
from engine.records import provenance
from worlds import commons


def probe(params, after_high=False):
    world = commons.make(params, random.Random(0))
    state = world.initial_state()
    if after_high:
        state = world.step(state, {a.id: ("hi", False) for a in world.agents}, world.rng)
    calls, entries = Counter(), Counter()
    kernel = world.outcomes

    def counted(state, joint):
        identity = key([state, joint])
        calls[identity] += 1
        for item in kernel(state, joint):
            entries[identity] += 1
            yield item

    world.outcomes = counted
    actor = world.agents[0]
    search = Search(world, actor)
    start = perf_counter()
    values, status = None, "complete"
    try:
        observation, support = search.initial(state, actor)
        values = search.values(support, observation, actor, actor.depth, actor.k, False)
    except SearchLimitExceeded:
        status = "search_limit"
    return {"params": params, "seed": 0, "physical_rounds_before_probe": int(after_high),
            "status": status, "values": values, "nodes": search.nodes,
            "elapsed_seconds": perf_counter() - start,
            "kernel_calls": sum(calls.values()), "unique_kernel_calls": len(calls),
            "kernel_entries": sum(entries.values()),
            "cached_responses": len(search.responses),
            "search_metrics": getattr(search, "metrics", None)}


def study():
    return [probe({**commons.DEFAULTS, "n": n, "search_depth": depth}, after_high)
            for n, depth in [(4, 2), (4, 3), (10, 2), (10, 3)]
            for after_high in (False, True)]


if __name__ == "__main__":
    result = {"schema_version": 1, "kind": "search-profile", "provenance": provenance(),
              "fixture_sha256": hashlib.sha256(Path(__file__).read_text(encoding="utf-8").encode()).hexdigest(),
              "fixed": commons.FIXED, "fixed_reasons": commons.FIXED_REASONS,
              "settings": {"seed": 0, "probe_actor": "u0", "duration": "one decision per state"},
              "results": study()}
    print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))
