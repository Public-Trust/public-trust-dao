[Русский](README.md) · [English]

# Project status traffic-light

## The main idea — in plain words

This folder holds a single file — `run_all_status.json`. It is the project's
"traffic-light": a short machine-readable summary of the latest self-check. Green
means all eight helper AI agents and the quality checks are fine; red means
something needs fixing.

The file is produced not by a human but by the self-check runner
([`ai-agents/run_all.py`](../../ai-agents/run_all.py)): it runs every helper at
once and folds their answers into one short verdict. So any person or dashboard
can see the project's state at a glance — **with no external services, no
third-party badges, no tracking**. Everything is open and verifiable.

Important: this is a **signal, not power** (Constitution, art. 9). The file
decides nothing and commands nothing — it only shows what the self-check saw.
Power belongs to community voting and the Safe multisig.

## What's inside the file

- `verdict` — overall result: `green` (all good) or `red` (a violation).
- `agents` — how many of the eight helper AIs are green (`green` of `total`).
- `tests` — how many invariant tests passed (they prove that "red" is really
  caught, not "green by default").
- `guard` — structure guard summary: its verdict, score and **soft warnings**
  (count and the lines themselves — what is worth fixing, without failing the build).
- `agent_status` — one row per helper: its key and green/red.

## How it is updated

```
python3 ai-agents/run_all.py --with-tests --status-out governance/status/run_all_status.json
```

The file is **deterministic**: with the repository state unchanged it is
byte-for-byte the same. It deliberately contains NO wall-clock time — otherwise it
would go "dirty" in git on every run. The "when" comes from the commit time, not
from the file itself. So the artifact changes in history exactly when the verdict
or the score changes.

The `schema_version` field versions the format: if the format changes
incompatibly, the number grows and readers can adapt.

---

## Technical section — for developers

- The artifact is assembled by `build_status(report)` from the full
  `run_all --json` report; written by `write_status(path, report)` (creates parent
  dirs, trailing `\n`, `ensure_ascii=False`, `indent=2`).
- Folding completeness is proven by the invariant test
  [`test_run_all.py`](../../ai-agents/test_run_all.py): structure, determinism
  (re-run → byte-identical file), writing even on `verdict=red`, robustness to a
  missing guard (`guard=None`).
- This is the basis for a future public "status indicator" with no external
  services: a dashboard/page can read this file directly from the repository.
- TESTNET-only: the artifact touches no funds/keys and does not go online.
