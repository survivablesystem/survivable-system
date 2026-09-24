"""E16: every query across the register; designs compared on the same cells."""
import json
from pathlib import Path
import random
import subprocess
import sys

import pytest

from engine.grid import Setup, cells, compare, evaluate, parse_grid, run, summarize
from engine.power import counts
from engine.rules import enforcement
from tests import grid_toy
from worlds import commons, treaty

TOY = Setup("tests.grid_toy")
EXT = {"mode": "externalities", "rounds": 2}


def by_measure(summary):
    return {e["measure"]: e for e in summary}


def test_a_measure_depends_on_the_one_key_that_moves_it():
    grid = parse_grid(["wall=0,1,2,3", "colour=red,blue"], grid_toy.SPACE)
    results = run(TOY, EXT, cells(grid_toy, {}, grid), jobs=1)
    s = by_measure(summarize(results, grid_toy))
    force = s["breach: force"]
    assert force["values"] == {"1": 4, "2": 4}  # one pusher suffices up to wall 1 within two rounds
    assert force["depends_on"] == {"wall": [2, 2]}  # never colour
    assert "depends_on" not in s["breach: the affected can prevent"] and s["breach: the affected can prevent"]["constant"]
    moved = [e for block in compare(results, "colour")["against"] for e in block["measures"] if e["changed"]]
    assert moved == []


def test_compare_reports_transitions_and_what_they_move_with():
    grid = parse_grid(["colour=red,blue", "wall=1,2"], grid_toy.SPACE)
    results = run(TOY, EXT, cells(grid_toy, {}, grid), jobs=1)
    block = compare(results, "wall")["against"][0]
    force = next(e for e in block["measures"] if e["measure"] == "breach: force")
    assert force["changed"] == 2 and force["pairs"] == 2
    assert force["transitions"] == [{"from": "1", "to": "2", "count": 2}]
    assert "depends_on" in force and force["depends_on"] == {}  # the same move under every colour


def test_draws_do_not_depend_on_what_is_gridded_and_parallel_equals_serial():
    one = cells(grid_toy, {}, parse_grid(["wall=0,2"], grid_toy.SPACE), draws=3, seed=7)
    two = cells(grid_toy, {}, parse_grid(["colour=red"], grid_toy.SPACE), draws=3, seed=7)
    assert [c["params"]["reward"] for c in one[::2]] == [c["params"]["reward"] for c in two]
    query = {"mode": "enforce", "rounds": 2, "rule": "hold"}
    assert run(TOY, query, one, seed=7, jobs=1) == run(TOY, query, one, seed=7, jobs=2)
    s = by_measure(summarize(run(TOY, query, one, seed=7, jobs=1), grid_toy))
    assert s["a harmful"]["depends_on"] == {"wall": [3, 3]}  # the draw index never moves it


def test_grid_rejects_undeclared_values():
    with pytest.raises(ValueError):
        parse_grid(["wall=0,9"], grid_toy.SPACE)
    with pytest.raises(ValueError):
        parse_grid(["height=1"], grid_toy.SPACE)
    with pytest.raises(ValueError):
        parse_grid(["wall=1,1"], grid_toy.SPACE)
    with pytest.raises(ValueError):
        parse_grid(["rule=hold"], grid_toy.SPACE)  # a rule grid needs a rule check
    with pytest.raises(ValueError):
        parse_grid(["rule=hold,obey"], grid_toy.SPACE, grid_toy.RULES)


def test_a_rule_cell_equals_the_direct_check():
    grid = parse_grid(["rule=restraint,reciprocity"], treaty.SPACE, treaty.RULES)
    query = {"mode": "enforce", "rounds": 2, "reach": 1, "size": 2}
    for cell, result in zip(cells(treaty, {}, grid), run(Setup("worlds.treaty"), query, cells(treaty, {}, grid), jobs=1)):
        world = treaty.make(dict(cell["params"]), random.Random(0))
        direct = enforcement(world, treaty, treaty.RULES[cell["rule"]], world.initial_state(), 2, 1, 2)
        assert json.loads(json.dumps(result["report"])) == json.loads(json.dumps(direct))


def up_to_symmetry(world, value):
    if isinstance(value, dict) and "witnesses" in value:
        return {**value, "witnesses": sorted({counts(world, w) for w in value["witnesses"]})}
    return value


def test_reproduces_saved_externalization_evidence_cell_for_cell():
    saved = json.loads(Path("evidence/externalization.json").read_text(encoding="utf-8"))
    rounds = saved["settings"]["rounds"]
    query = {"mode": "externalities", "rounds": rounds}
    grid = parse_grid(["lead=0,2", "domains=1,2", "verification=none,exact"], treaty.SPACE)
    got = {json.dumps(r["grid"], sort_keys=True): r["report"]["harms"]
           for r in run(Setup("worlds.treaty"), query, cells(treaty, {}, grid))}
    commons_cells = [c for over, S in (({"n": 3}, (8.0, 20.0, 30.0, 50.0)), ({"n": 3, "restraint": False}, (20.0, 30.0)))
                     for c in cells(commons, over, {"state.S": list(S)})]
    for c in commons_cells:
        c["key"] = json.dumps({"restraint": c["params"]["restraint"], "S": c["state"]["S"]}, sort_keys=True)
    got_commons = {c["key"]: r["report"]["harms"] for c, r in zip(commons_cells, run(Setup("worlds.commons"), query, commons_cells))}
    checked = 0
    for kind, rows in saved["results"].items():
        for row in rows:
            if kind == "treaty":
                report = got[json.dumps(row["params"], sort_keys=True)]
            else:
                restraint = row["params"].get("restraint", commons.DEFAULTS["restraint"])
                report = got_commons[json.dumps({"restraint": restraint, "S": row["S"]}, sort_keys=True)]
            world = (treaty if kind == "treaty" else commons).make({**(treaty if kind == "treaty" else commons).DEFAULTS,
                                                                  **row["params"]}, random.Random(0))
            for old, new in zip(row["report"], report):
                # fields added since (keep, veto) aside; witnesses listed once per symmetry class since E2
                assert {k: up_to_symmetry(world, new[k]) for k in old} == {k: up_to_symmetry(world, v) for k, v in old.items()}
                checked += 1
    assert checked == sum(len(r["report"]) for rows in saved["results"].values() for r in rows)


def test_cli_grid_runs_and_rejects_a_compare_key_outside_the_grid():
    base = [sys.executable, "-m", "engine", "tests.grid_toy", "--externalities", "2", "--jobs", "1"]
    ok = subprocess.run(base + ["--grid", "wall=0,2", "--compare", "wall", "--json"], capture_output=True, text=True, check=True)
    out = json.loads(ok.stdout)
    assert out["mode"] == "grid" and len(out["results"]["cells"]) == 2 and out["results"]["comparison"]["key"] == "wall"
    bad = subprocess.run(base + ["--grid", "wall=0,2", "--compare", "colour"], capture_output=True, text=True)
    assert bad.returncode != 0 and "--compare" in bad.stderr


def test_numeric_measures_compare_by_direction():
    grid = parse_grid(["rule=hold", "reward=0.0,0.5,1.0"], grid_toy.SPACE, grid_toy.RULES)
    results = run(TOY, {"mode": "enforce", "rounds": 2}, cells(grid_toy, {}, grid), jobs=1)
    s = by_measure(summarize(results, grid_toy))
    assert s["a margin"]["range"] == [0.0, 1.0] and not s["a margin"]["constant"]
    assert s["a+b capture gain"]["values"] == {"none": 1} and s["a+b capture gain"]["numeric_cells"] == 2
    block = compare(results, "reward")["against"][0]
    margin = next(e for e in block["measures"] if e["measure"] == "a margin")
    assert margin["directions"] == {"rises": 1} and margin["transitions"] == []
