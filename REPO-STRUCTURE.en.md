[Русский](REPO-STRUCTURE.md) · [English]

# REPOSITORY MAP — PUBLIC TRUST DAO

> Navigation document: what lives where and **where to put new things**, so the
> repository stays transparent and free of chaos. This is a living map — keep it
> up to date when adding new directories/layers (the rule is fixed in
> [`BUILDER.md`](BUILDER.md)).
>
> Auxiliary document. The supreme law is [`docs/en/MANIFESTO.md`](docs/en/MANIFESTO.md)
> and [`docs/en/CONSTITUTION.md`](docs/en/CONSTITUTION.md).

---

## Layout principle

One directory = one layer of responsibility. If you're unsure where a file goes —
check the table below; don't spawn new top-level directories without need and
without an entry in this map. Every public artifact (code, document, decision)
must be committed and explained.

Project layers (see [`docs/en/PRODUCT-INTERFACES.md`](docs/en/PRODUCT-INTERFACES.md)):
**treasury → smart contracts → AI agents → interface**. The repo directories
mirror this logic, plus the normative base and the autonomy loop.

---

## Top-level directories

| Path | Purpose | What to put here | What NOT to put here |
|---|---|---|---|
| `docs/` | Normative and design documentation (RU originals). | Manifesto, constitution, principles, priorities, anti-abuse, specifications (escrow, product form), future design specs. | Code, secrets, the built site. |
| `docs/en/` | English mirror of `docs/`. | EN version of every document in `docs/` (same base file name). | RU texts, files with no RU original. |
| `contracts/` | Smart contracts (Stage 5) + their tests. | Solidity contracts for treasury/voting/reputation/escrow, unit and integration tests, network config (testnet). | Private keys, mainnet deploys, real funded addresses. |
| `ai-agents/` | AI agent modules (Stage 6). | Guardian/Audit/Fairness/Reputation/Housing/Governance/Mediator/Documentation as scripts/modules that help enforce the constitution. | Autonomous power over funds; anything bypassing multisig/registry. |
| `web/` | Public static site (GitHub Pages) and the future web-dApp. | `index.html`, local assets (`assets/`), `.nojekyll`. No external requests/CDN/trackers. | Build junk, keys, surveillance analytics. |
| `governance/` | Governance and transparency (Stages 3–4). | Public decision registry (`registry/`), IPFS manifest (`ipfs/`), future Snapshot (`snapshot/`) and Safe multisig (`safe/`) mockups. | Applicants' personal data; real private keys. |
| `scripts/` | Tooling and the autonomy loop (pulse). | Dependency-free helper tools (`registry.py`, `ipfs_manifest.py`). | ⛔ Pulse edits: do NOT touch `loop.sh`, `report.sh`, `operator_bridge.py` (heartbeat). Build artifacts (`__pycache__/`, `*.pyc`) are in `.gitignore`. |
| `comms/` | "Operator ↔ agent" channel. | `INBOX.md` (operator instructions), `operator-thread.md` (exchange history). | Anything other than correspondence/instructions. |
| `.github/workflows/` | CI/CD (public guarantees). | Workflows: `registry.yml`, `ipfs.yml`, `pages.yml`. | Secrets in cleartext (use GitHub Secrets only). |

## Root files

| File | Purpose |
|---|---|
| `README.md` / `README.en.md` | Entry point: mission, disclaimer (NOT an investment / NOT a pyramid), doc map, licenses. RU + EN. |
| `LAUNCH.md` | Manifesto-constitution and the full stage plan (1→6). The project's north star. |
| `BUILDER.md` | Mandate of the autonomous builder agent (session protocol, safety rails). |
| `PROGRESS.md` | Progress log + "next step" + "needed from operator". Memory across sessions. |
| `DECISIONS.md` | Significant decisions and their reasons (briefly). |
| `REPO-STRUCTURE.md` / `REPO-STRUCTURE.en.md` | This document — the repository map. RU + EN. |
| `LICENSE` | Code license — AGPL-3.0. |
| `LICENSE-DOCS` | Document license — CC-BY-SA-4.0. |
| `.gitignore` | Exclusions: secrets, pulse logs/state, build artifacts. |

---

## Rules (in brief)

1. **Bilingual.** Keep any new/changed document in sync RU↔EN in the **same commit**.
   RU originals — in `docs/` and root; EN mirror — in `docs/en/` and `*.en.md`.
   Each one has a `[Русский] · [English]` switcher at the top.
2. **Decisions into the registry.** Log significant architectural/product decisions
   into `governance/registry/` via `scripts/registry.py append` (append-only,
   hash-chain), not only in prose.
3. **Secrets never in the repo.** `.env`, keys, wallets — local/env only; `.gitignore`
   covers this. Real money/keys only beyond the threshold of an audit + Safe multisig
   3-of-5 + operator approval.
4. **The pulse is untouchable.** `scripts/loop.sh`, `scripts/report.sh`,
   `scripts/operator_bridge.py`, `logs/` — do not edit and do not commit state.
5. **Keep the map alive.** Added a directory/layer — add a row here (and in the EN mirror).
