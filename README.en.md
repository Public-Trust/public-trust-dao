[Русский](README.md) · [English]

# Public Trust DAO

**An open, decentralized system of mutual aid and public goods.**

Public Trust DAO provides people with basic security, human dignity, housing, food, medical care, education, and the restoration of self-reliance — and the opportunity, once helped, to help others over time.

> ⚠️ **This is NOT an investment, NOT a financial pyramid, NOT a profit-extraction instrument.** It is open mutual-aid infrastructure governed by a constitution, a transparent on-chain treasury, open source code, and a community.

## Core principle
No one owns the project. The founder is an ordinary participant. The project belongs to its **mission, constitution, and community**. People and AI are temporary stewards of the mission.

## What's inside
- [`docs/en/MANIFESTO.md`](docs/en/MANIFESTO.md) — the full manifesto and constitution (the project's north star and law).
- [`docs/en/CONSTITUTION.md`](docs/en/CONSTITUTION.md) — the constitution by articles (the supreme law, referenced by contracts and agents).
- [`docs/en/PRINCIPLES.md`](docs/en/PRINCIPLES.md) — principles and constitutional prohibitions (verbatim).
- [`docs/en/PRIORITIES.md`](docs/en/PRIORITIES.md) — the priority of fair distribution (specification).
- [`docs/en/ANTI-ABUSE.md`](docs/en/ANTI-ABUSE.md) — anti-abuse protection mechanisms (specification).
- [`docs/en/ESCROW-TARGETED-DISBURSEMENT.md`](docs/en/ESCROW-TARGETED-DISBURSEMENT.md) — the targeted-use / escrow model (how aid reaches its purpose instead of going cash-in-hand).
- [`docs/en/PRODUCT-INTERFACES.md`](docs/en/PRODUCT-INTERFACES.md) — product form and interface roadmap (web dApp → Telegram bot → mobile app).
- [`AUTHORS.en.md`](AUTHORS.en.md) — authors and stewards: project author/initiator **Fedor Grigoriev** (authorship ≠ ownership).
- [`REPO-STRUCTURE.en.md`](REPO-STRUCTURE.en.md) — repository map: what lives where and where to put new things.
- [`CONTRIBUTING.en.md`](CONTRIBUTING.en.md) — how to contribute: issues/PRs/governance proposals, contribution rails, code of conduct (contribution ≠ power over the treasury).
- [`CODE_OF_CONDUCT.en.md`](CODE_OF_CONDUCT.en.md) — code of conduct (canonical file): human dignity, unacceptable behavior, breaking the safety rails = breaking the code.
- [`SECURITY.en.md`](SECURITY.en.md) — security policy (canonical file): how to report a vulnerability privately, what counts as a vulnerability, safe harbor, constitutional rails (TESTNET-first, no one owns it alone).
- [`docs/en/GLOSSARY.md`](docs/en/GLOSSARY.md) — glossary of key terms in plain language (DAO, escrow, multisig, registry, distribution priority, etc.), RU/EN — so the documents are understandable beyond technical people.
- [`docs/en/ROADMAP.md`](docs/en/ROADMAP.md) — roadmap and self-development mechanism (living, prioritized list of ideas/tasks).
- [`docs/en/PROMOTION.md`](docs/en/PROMOTION.md) — promotion materials: landing copy, pitch (RU/EN), announcement post, FAQ "public good, NOT an investment".
- [`docs/en/EMAIL-SETUP.md`](docs/en/EMAIL-SETUP.md) — project email: options, operator guide, signature and reply templates (RU/EN).
- [`docs/en/OUTREACH.md`](docs/en/OUTREACH.md) — outreach: recipient categories and letter templates (RU/EN) for reaching people with an audience as a public good (the operator sends).
- [`docs/en/GOVERNANCE.md`](docs/en/GOVERNANCE.md) — governance course: the voice of every verified human (Governor), the multisig as executor/emergency, Sybil resistance without power concentration.
- [`docs/en/SUPPORT-MODEL.md`](docs/en/SUPPORT-MODEL.md) — how the project accepts support: through the system itself (transparent multisig treasury + registry), with no separate "Donate" button; a real-money address only after launch and an audit.
- [`docs/en/REWARDS-MODEL.md`](docs/en/REWARDS-MODEL.md) — the adaptive parametric reward-and-distribution model: three separate streams (aid / work / volunteering), the reward share grows with treasury health under a hard ceiling (aid always ≥ 70%), coefficients governed by vote, validation and verifiability.
- [`LAUNCH.md`](LAUNCH.md) — technical specification for building the infrastructure.
- [`contracts/`](contracts/) — smart contracts (TESTNET first). Stage 5, skeleton:
  [`Treasury.sol`](contracts/contracts/Treasury.sol) — base treasury layer (release
  only via executor=multisig/Timelock, per-release cap, emergency pause, events)
  + tests "to green". No real funds/keys.
- `web/` — public website (GitHub Pages).
- `governance/` — governance (Safe multisig 3-of-5, Snapshot/Aragon).
  - [`governance/registry/`](governance/registry/) — a public, verifiable,
    tamper-resistant registry of decisions (append-only hash-chain).
  - [`governance/safe/`](governance/safe/) — Safe multisig 3-of-5 test-treasury
    blueprint (testnet, no real money/keys) + a rail validator.
  - [`governance/snapshot/`](governance/snapshot/) — off-chain Snapshot voting
    blueprint (one person = one vote, not plutocracy) + a rail validator.
- [`ai-agents/`](ai-agents/) — AI modules serving the mission (they hold no funds and
  have no power; Art. 9). Stage 6, scaffold: the **Audit agent**
  [`audit_agent.py`](ai-agents/audit_agent.py) — one command checks the integrity of
  the whole governance layer (registry/IPFS/Safe/Snapshot), tied to constitution articles.

## Principles
openness · transparency · immutability of records · no owner · distributed governance · verifiability · open source · human dignity · mutual aid · fairness · protection against abuse.

## Status
🚧 Bootstrap. Stages 1–2 are complete (documents, licenses, website). Stage 3 — transparency:
a public registry of decisions is live (hash-chain, CI integrity check); next comes
IPFS pinning. All development is public and verifiable.

## License
- **Code** — [GNU AGPL-3.0](LICENSE). Copyleft: any derivatives and networked
  deployments must remain open. This protects the project from closed
  forks and aligns with the principle "everything open, nothing hidden."
- **Documents** (`docs/`, the manifesto, constitution, specifications) —
  [CC-BY-SA-4.0](LICENSE-DOCS). Free to use and distribute with
  attribution and preservation of the same license.

## Author
The author of the idea and initiator of the project is **Fedor Grigoriev**
(Федор Григорьев; see [`AUTHORS.en.md`](AUTHORS.en.md)). Authorship ≠ ownership:
under the constitution no one owns the project, and the founder is an ordinary
participant/steward (one vote). The project belongs to its mission, constitution,
and community.

© Fedor Grigoriev and Public Trust DAO contributors. Code — AGPL-3.0, docs — CC-BY-SA-4.0.
