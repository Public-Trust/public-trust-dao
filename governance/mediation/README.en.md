[Русский](README.md) · [English]

# Mediation — dispute & appeal process (structure, not power)

> The dispute/appeal lifecycle artifact and its machine check. Implements
> mechanism #6 **"Appeals"** of [`docs/ANTI-ABUSE.md`](../../docs/en/ANTI-ABUSE.md):
> every participant has a **transparent path to contest** a rejection or sanction.
> **People decide**, not the AI (Constitution [art. 9.2](../../docs/en/CONSTITUTION.md)).

## Why this exists

The right to appeal in `ANTI-ABUSE.md` is described in words. So that it does not
remain a slogan and does not silently drift from the constitution, the process is
pinned as a verifiable artifact [`dispute-process.json`](dispute-process.json),
and the **Mediator AI agent**
([`ai-agents/mediator_agent.py`](../../ai-agents/mediator_agent.py)) proves on
every push/PR that the process still matches the constitution.

**The Mediator structures the dispute but NEVER decides it.** The agent does not
punish, does not acquit, and moves no funds — it only checks the shape of the
process and reports "green/red". A "red" is a signal to the community, not an action.

## Dispute / appeal lifecycle

The artifact describes a finite state machine of stages:

| Stage | Role | Run by | Deadline |
|---|---|---|---|
| `intake` (start) | structure | Mediator agent (structures the request) | 3 days |
| `review` | **decide** | independent reviewers, **≥2 people** | 7 days |
| `escalation` | **decide** | guardian council (multisig), **≥3** | 14 days |
| `resolved` (terminal) | record | outcome recorded in the public registry | — |

Only people decide, and only collectively (≥2). The Mediator agent is allowed
solely on non-deciding stages (intake and the `resolved` record).

## Sanctions with a right to appeal

Every sanction in `ANTI-ABUSE.md` must have an appeal path:

- `disbursement-rejection` — rejection of a payment/help request;
- `reputation-sanction` — reputation reduction (#7);
- `temporary-freeze` — temporary freeze of payments (#8);
- `exclusion` — exclusion of a participant (#9).

An appeal is heard by **someone other** than who issued the sanction (independence, §3).

## What the agent checks (6 checks)

| Check | What it guarantees | Norm |
|---|---|---|
| `appeal-for-every-sanction` | each canonical sanction has an appeal | §6 |
| `mediator-not-decider` | people decide (≥2), not AI/mediator/one person | art. 9.2 / §3 |
| `independent-review` | the appeal is not decided by the sanction's author | §3 |
| `valid-lifecycle` | one start, a terminal exists, no dead ends/orphans | art. 3 |
| `bounded-timelines` | every non-terminal stage has a deadline > 0 | art. 3 / §6 |
| `process-links` | all doc links of the process resolve to real files | art. 3 |

## How to run

```bash
python3 ai-agents/mediator_agent.py          # human-readable report
python3 ai-agents/mediator_agent.py --json    # machine-readable (for CI/agents)
python3 ai-agents/test_mediator.py            # invariant test: "red is caught"
```

No dependencies (Python standard library), no network — deterministic in any CI.
**TESTNET-ONLY:** the agent never touches real funds/keys/mainnet.

## Rails

- The AI is not an organ of power and owns nothing (Constitution art. 9). The
  Mediator **does not decide**.
- Resolving a dispute always rests with an independent collective of people, never one person.
- Everything is open: the process, the check, and the outcomes are public (decision registry).
- Privacy: the fact/address is public, not the participant's identity.
