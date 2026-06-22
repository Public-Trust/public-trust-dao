[Русский](CONTRIBUTING.md) · [English]

# How to Contribute — Public Trust DAO

Thank you for wanting to help. Public Trust DAO is a **public good, NOT an
investment** and **not a way to make money**: there are no promises of returns,
no pyramid, no payment for recruiting people, and no owner. Contributing means
adding to a transparent mutual-aid system — not buying a share and not gaining
power over the treasury.

> **Contribution ≠ power over money.** No matter how much you do, it grants no
> right to control funds. Distribution is governed by the constitution and by
> community voting on a **"1 person = 1 vote"** basis (see
> [`docs/en/GOVERNANCE.md`](docs/en/GOVERNANCE.md)). Authorship and contributions
> are recorded by git history and the [public decision registry](governance/registry/)
> — this is recognition, not ownership (the same applies to the project's author,
> see [`AUTHORS.en.md`](AUTHORS.en.md)).

Before you start, read the project's supreme law: the constitution
([`docs/en/CONSTITUTION.md`](docs/en/CONSTITUTION.md)) and the principles with
their literal prohibitions ([`docs/en/PRINCIPLES.md`](docs/en/PRINCIPLES.md)).
Every contribution must comply with them — an idea that contradicts the
constitution is not taken into work.

---

## Where to start

1. **Look around.** Read [`README.en.md`](README.en.md) (mission and overview),
   the repository map [`REPO-STRUCTURE.en.md`](REPO-STRUCTURE.en.md) (what lives
   where), and the living roadmap [`docs/en/ROADMAP.md`](docs/en/ROADMAP.md)
   (what is being worked on and which ideas are open).
2. **Pick a scope that fits you.** You can report a bug/inaccuracy, improve a
   document, translate text, propose a governance idea, or send code with tests —
   see the formats below.
3. **Check the rails** (the "Contribution rails" section). They aren't
   bureaucracy — they keep the project honest and verifiable.

## Ways to contribute

### 1. Issue (question, bug, proposal)
The simplest entry point. When opening an issue, pick a ready-made form
(`.github/ISSUE_TEMPLATE/`: bug/inaccuracy, idea, governance proposal, abuse
risk) — it asks for the right context and walks you through the rails. Open an
issue if you:
- found a bug, inaccuracy, or broken link in the docs or code;
- see an abuse risk or a hole in the safety rails;
- want to propose an idea (it may land in the [roadmap "Idea bank"](docs/en/ROADMAP.md));
- don't understand something in the constitution/principles/mechanics — a
  question is valuable too.

Be specific: what you observed, what you expected, a link to the file/line. Don't
publish anyone's personal data, and never publish private keys or secrets.

### 2. Pull Request (doc or code change)
- **Documents.** Any new or changed public document is kept **in parallel in
  Russian and English (RU↔EN) within the same PR**: the RU original in `docs/` or
  the root, the EN mirror in `docs/en/` or `*.en.md`; each starts with a
  `[Русский] · [English]` language switcher. This is checked automatically (the
  Documentation agent in CI).
- **Code (contracts/scripts/agents).** Accompany changes with tests that go
  green. Contracts are for test networks/local only (see the rails). Style:
  match the surrounding code; dependencies stay minimal and justified.
- Make small, meaningful commits with a clear description. Every step is public
  and verifiable.
- When opening a PR, fill in the rails checklist from the template
  (`.github/pull_request_template.md`) — it is inserted automatically.

### 3. Governance proposal (how funds move / how rules change)
Decisions about the direction of aid, parameters, and rule changes are made not
by a single person but by the community — through voting. The mechanics, proposal
types, and decentralization path are described in
[`docs/en/GOVERNANCE.md`](docs/en/GOVERNANCE.md); the off-chain mock-up is in
[`governance/snapshot/`](governance/snapshot/). Significant adopted decisions are
recorded in the [public registry](governance/registry/) (append-only hash-chain —
history can't be rewritten unnoticed).

### 4. Become a verified participant / guardian
The right to vote comes from confirming a **person's uniqueness** (it can't be
bought or sold — a soulbound badge), not from wallet size. A multisig guardian is
an **executive/emergency role, not power over funds**, and an ordinary participant
with one vote. Details, and anti-Sybil without concentration of power, are in
[`docs/en/GOVERNANCE.md`](docs/en/GOVERNANCE.md). Setting up real addresses/Safe
is an action by human operators, not an automated agent.

## Contribution rails (boundaries — mandatory)

These rules mirror the project's safety rails and are checked in CI:

- **This is a public good, NOT an investment.** No text/code promises returns,
  guarantees profit, builds a pyramid, pays for recruiting people, or
  concentrates power (literal prohibitions —
  [`docs/en/PRINCIPLES.md`](docs/en/PRINCIPLES.md)).
- **TESTNET-first.** No mainnet deployments and no real funds. Real money — only
  after an independent audit, an explicit community decision, and a 3-of-5 Safe
  multisig of living people.
- **Secrets — never in the repository.** Private keys, tokens, passwords, `.env`
  files are not committed (the Guardian agent checks this). Use only test wallets
  with no real funds.
- **Bilingual RU↔EN** for any new/changed public document — in the same PR.
- **Transparency.** Code, documents, and decisions are public and explainable.
  Significant decisions are logged to the [registry](governance/registry/).
- **Applicant privacy.** Public artifacts carry only pseudonymous case
  identifiers, with no personal data of the people being helped.

## Code of conduct

The full text is in the canonical [`CODE_OF_CONDUCT.en.md`](CODE_OF_CONDUCT.en.md)
file (GitHub surfaces it on the "Community" tab). The project is built on human
dignity and mutual aid (see [`docs/en/PRINCIPLES.md`](docs/en/PRINCIPLES.md)). In
short:

- Respect people. Critique ideas and code, not individuals.
- Be honest and verifiable: back claims with links and facts.
- Don't use the project for self-promotion, spam, urgency pressure, or promises
  of gain.
- Remember who this is for: people in need are not a PR opportunity or "content".
- Violations of the safety rails (hiding operations, smuggling in real
  funds/keys, bypassing voting) are not acceptable.

## How to verify integrity yourself

The project is designed to be verifiable without trusting anyone:

```sh
python3 scripts/registry.py verify        # decision registry (schema + hash-chain + index)
python3 ai-agents/run_all.py --with-tests # run all constitution-compliance AI agents
```

A "red" from any agent is a **signal to the community**, not an action: the
agents fix nothing and control nothing (constitution, art. 9).

## Licenses

By contributing, you agree that your contribution is published under the
project's licenses: **code — AGPL-3.0** ([`LICENSE`](LICENSE)), **documents —
CC-BY-SA-4.0** ([`LICENSE-DOCS`](LICENSE-DOCS)). Authorship is preserved by git
history and the [decision registry](governance/registry/).

---

© Public Trust DAO and contributors. Text — CC-BY-SA-4.0, code — AGPL-3.0.
This is a public good, **not an investment**.
