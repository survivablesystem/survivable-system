"""Evidence can be replayed, including stochastic outcomes across processes."""
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

from engine.records import artifact, provenance, run_record
from engine.sweep import one_at_a_time, shares, sweep
from worlds import commons


ROOT = Path(__file__).resolve().parents[1]


def cli(*args):
    return subprocess.run([sys.executable, "-m", "engine", "worlds.commons", *args],
                          cwd=ROOT, capture_output=True, text=True)


def test_finite_survival_is_not_convergence():
    params = {**commons.DEFAULTS, "horizon": 1, "sanction": False}
    short = run_record(commons.make, params, 1, 0)
    longer = run_record(commons.make, params, 30, 0)
    assert short["label"] == "survived" and short["terminal"] is None
    assert short["rounds_run"] == 1
    assert longer["label"] == longer["terminal"] == "collapsed"
    assert longer["rounds_run"] == 5 < longer["rounds_requested"]


@pytest.mark.parametrize("mode", ["trace", "oat", "sweep"])
def test_cli_json_records_replay(mode):
    args = [] if mode == "sweep" else [f"--{mode}"]
    completed = cli(*args, "--json", "--samples", "2", "--seeds", "2", "--rounds", "3",
                    "--fix", "n=4", "horizon=1", "k=0")
    assert completed.returncode == 0, completed.stderr
    data = json.loads(completed.stdout)
    assert data["schema_version"] == 1 and data["mode"] == mode
    assert data["world"] == "worlds.commons"
    assert data["register"]["n"]["kind"] == "int"
    assert data["fixed"]["S_min_frac"]["reason"]
    assert data["provenance"]["source_sha256"]["worlds/commons.py"]
    if mode == "oat":
        # --fix means fixed throughout the experiment, not just at the baseline.
        assert not {"n", "horizon", "k"} & {r["parameter"] for r in data["results"]}
        runs = [run for group in data["results"] for run in group["runs"]]
        for group in data["results"]:
            assert group["shares"] == shares(group["runs"])
            assert [r["seed"] for r in group["runs"]] == [0, 1]
    else:
        runs = data["results"]
    for saved in runs:
        assert saved["params"]["n"] == 4
        assert saved["params"]["horizon"] == 1
        replay = run_record(commons.make, saved["params"], saved["rounds_requested"],
                            saved["seed"], include_trace=mode == "trace")
        assert json.loads(json.dumps(replay)) == saved


def test_stochastic_contests_replay_across_hash_seeds():
    script = """
import json, random
from worlds import commons
w = commons.make({**commons.DEFAULTS, 'n': 6}, random.Random(0))
joint = {a.id: (commons.LO, True) if i < 2 else (commons.HI, False)
         for i, a in enumerate(w.agents)}
print(json.dumps(w.step(w.initial_state(), joint, w.rng), sort_keys=True))
"""
    outputs = []
    for hash_seed in ("1", "123", "999"):
        result = subprocess.run([sys.executable, "-c", script], cwd=ROOT,
                                env={**os.environ, "PYTHONHASHSEED": hash_seed},
                                capture_output=True, text=True, check=True)
        outputs.append(result.stdout)
    assert len(set(outputs)) == 1
    wealth = json.loads(outputs[0])["wealth"]
    assert len({wealth[f"u{i}"] for i in range(2, 6)}) > 1  # actually exercised random hits


def test_sweep_replays_each_recorded_seed():
    space = {**commons.DEFAULTS, "prior": ["lo", "hi", "ready"], "horizon": 1}
    rows = sweep(commons.make, space, 5, 4, seed=42)
    assert rows == sweep(commons.make, space, 5, 4, seed=42)
    assert len({r["seed"] for r in rows}) == 5
    for row in rows:
        assert row == run_record(commons.make, row["params"], 4, row["seed"])


@pytest.mark.parametrize("args", [
    ["--rounds", "0"], ["--samples", "-1"], ["--seeds", "0"],
    ["--trace", "--oat"], ["--fix", "unknown=4"], ["--fix", "n=4.5"],
    ["--fix", "n=0"], ["--fix", "sanction=1"], ["--fix", "discount=nan"],
    ["--fix", "n"], ["--fix", "n=4", "n=5"],
])
def test_invalid_cli_requests_fail_before_simulation(args):
    completed = cli(*args)
    assert completed.returncode == 2
    assert "error:" in completed.stderr
    assert "Traceback" not in completed.stderr
    assert not completed.stdout


def test_provenance_available_without_git(monkeypatch):
    def missing_git(*args, **kwargs):
        raise FileNotFoundError("git")
    monkeypatch.setattr(subprocess, "check_output", missing_git)
    source = provenance()
    assert source["git_commit"] is None and source["git_dirty"] is None
    assert len(source["source_sha256"]["engine/core.py"]) == 64


def test_fixed_assumptions_require_reasons(monkeypatch):
    monkeypatch.setattr(commons, "FIXED_REASONS", {})
    with pytest.raises(ValueError, match="FIXED_REASONS"):
        artifact(commons, "trace", {}, [])


def test_oat_all_fixed_has_only_baseline():
    params = {**commons.DEFAULTS, "horizon": 1}
    rows = one_at_a_time(commons.make, params, params, seeds=1, rounds=2)
    assert len(rows) == 1 and rows[0]["parameter"] is None


@pytest.mark.parametrize("args", [(0, 1), (1, 0)])
def test_empty_sweep_is_rejected(args):
    with pytest.raises(ValueError, match="positive"):
        sweep(commons.make, commons.SPACE, *args)
