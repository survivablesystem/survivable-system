# Survivable System

A simulation for finding civilizational-scale architectures that lower existential risk. Agents with goals, capabilities and information act inside architectures of rules and channels. No behavior is scripted. Failure chains are outputs: the tool asks what structures form, who can force irreversible outcomes, who can still correct errors, and how a proposed institution or a change in technology moves those answers.

Read [`INTENT.md`](INTENT.md) first. It is the measure for every change.

## Quick start

```
pip install -r requirements.txt
python -m pytest -q
python -m engine worlds.commons --oat
```

The last command starts from a favorable commons and moves one assumption at a time. Six of them flip the outcome on their own; see `rediscovery/open-commons.md` for what each means.

## Layout

| Path | What |
|---|---|
| `INTENT.md` | Why this exists and the six tests every change must pass |
| `AGENTS.md` | How to work here, for people and AI agents |
| `TASKS.md` | Ordered build plan with acceptance lines. Claim, build, mark done |
| `LOG.md` | One entry per session. Append-only |
| `DECISIONS.md` | Core changes and why they passed the tests |
| `spec/PRIMITIVES.md` | The model: one object, the agent, at every scale |
| `engine/` | Planner, run loop, sweeps, CLI. Stdlib only |
| `worlds/` | One file per world: the assumptions register and the dynamics |
| `tests/` | The rediscovery expectations as tests |
| `rediscovery/` | Structures whose outcomes history knows. The primitives are right when those outcomes emerge uncoded |

## What a result means

An attractor share is the share of a sweep over stated assumptions, never a probability of the world. A green test suite means the known outcomes emerge. It says nothing about unknown ones. The dominant failure is a wrong world, and nothing catches what is not modeled.

## License

MIT.
