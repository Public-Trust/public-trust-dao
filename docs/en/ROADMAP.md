[Русский](../ROADMAP.md) · [English]

# ROADMAP AND SELF-DEVELOPMENT — PUBLIC TRUST DAO

> Living document. This is the "fuel" of autonomous building: whenever the
> operator's queue (`comms/INBOX.md`) is empty, the builder agent takes the
> **next open item from here**, implements it, and proposes new ideas.
> Derived from [`MANIFESTO.md`](MANIFESTO.md), [`CONSTITUTION.md`](CONSTITUTION.md),
> [`PRINCIPLES.md`](PRINCIPLES.md) and the staged plan in `LAUNCH.md`.
>
> Registered as a decision in the public registry:
> [`governance/registry/`](../../governance/registry/) (entry `PTD-0005`).
>
> **Everything is TESTNET-first.** Any work with money — only after an independent
> audit, explicit operator approval, and a 3-of-5 Safe multisig of real people.

---

## Why this document

The project must move even when the operator is silent. So that building never
stalls and never degrades into a chaotic pile of unrelated edits, we need a
**single prioritized list of ideas and tasks** that the AI both maintains and
draws work from. That is the self-development mechanism:

```
INBOX empty?  →  take top open ROADMAP item  →  implement it to green
              →  mark [x]  →  propose 1–3 new ideas into the "Idea bank"
              →  register significant decisions in the registry
```

The rule is fixed in [`BUILDER.md`](../../BUILDER.md) (section "Self-development"),
so it is honored every session, not only while it is remembered.

## How it works (process)

1. **Source of work — by priority:**
   `INBOX` (operator instructions) → `ROADMAP` (this file) → staged plan `LAUNCH.md`.
2. **One coherent item per session.** Split a large item: do the first part,
   leave the rest open marked "next step".
3. **To a working result.** Real files/code/tests "to green", no stubs.
4. **Mark what's done** here (`- [x]`), move it into "Done" with a session number.
5. **Refill the idea bank.** Each session propose 1–3 new ideas (even raw ones) —
   so the list never runs dry. The operator can add ideas too.
6. **Log significant decisions** in the [registry](../../governance/registry/) (type `decision`).

## Self-development rails (autonomy boundaries)

Self-development does NOT lift the safety rails — it operates strictly within them:

- **Money/keys/mainnet** — never alone. Only preparation + the operator's explicit "go".
- **External actions on behalf of the project** (publishing, mailings, registering
  accounts with captcha/phone/KYC) — the agent prepares "up to the button", the
  operator presses it.
- **Constitutional prohibitions literally** — no roadmap idea may violate them (no
  yield, no pyramid, no referrals, no power concentration, no hidden operations).
  An idea that contradicts the constitution is not taken into work.
- **Bilingual RU↔EN** in the same commit for any new/changed document.
- **The pulse is untouchable** (`loop.sh`/`report.sh`/service/`.env`/`logs/`).

---

## Priorities (P0 — highest)

`P0` blocks/carries the most value · `P1` important · `P2` desirable · `P3` later idea.

### P0 — main plan (LAUNCH.md stages)

- [x] **Stage 4 — Governance, concept (GOVERNANCE COURSE):** target model
  "1 human = 1 vote" (Governor → Timelock → Treasury), the multisig as
  executor/emergency, the decentralization path, Sybil resistance without power
  concentration, constitutional amendments as a proposal. → Done (session 10),
  [`GOVERNANCE.md`](GOVERNANCE.md), `PTD-0007`. The base spec for parts 1–2.
- [ ] **Stage 4 — Governance, part 1:** Snapshot space mock-up (off-chain) in
  `governance/snapshot/` — `space.json`/README per [`GOVERNANCE.md`](GOVERNANCE.md):
  "1 human = 1 vote" strategy (not plutocracy), quorum, proposal types, link to the
  constitution (distribution priority, appeals).
  Actually creating the space (ENS/domain/controller wallet) — operator request.
- [ ] **Stage 4 — Governance, part 2:** Safe multisig mock-up, 5 guardians (3-of-5)
  in `governance/safe/` — scheme, roles (executor/emergency pause per
  [`GOVERNANCE.md`](GOVERNANCE.md)), signing policy, no real addresses.
- [ ] **Stage 5 — Smart contracts (skeleton):** set up `contracts/` as a project
  (Foundry/Hardhat config), skeletons for Treasury / Disbursement (per
  [`ESCROW-TARGETED-DISBURSEMENT.md`](ESCROW-TARGETED-DISBURSEMENT.md)) /
  Governance / Reputation + first tests "to green". Testnet/local only.
- [ ] **Stage 6 — AI agents (skeleton):** in `ai-agents/` describe and set up the
  Guardian/Audit/Fairness/Reputation/Housing/Governance/Mediator/Documentation
  modules as helper scripts for upholding the constitution (start with one — e.g.
  Audit, running `registry.py verify` + `ipfs_manifest.py verify`).

### P1 — materials and infrastructure (partly from INBOX)

- [x] **Promotion (INBOX #6):** a landing page for people, a short pitch RU/EN, an
  announcement post, a FAQ "this is a public good, NOT an investment". Prepared by
  the agent; publishing done by the operator. → Done (session 9),
  [`PROMOTION.md`](PROMOTION.md), `PTD-0006`.
- [ ] **Project email (INBOX #7):** instructions for the operator — domain+mail
  options (ProtonMail/own domain), texts. Registration done by the operator.
- [ ] **Testnet wallet + Safe (INBOX #10):** describe/create a test wallet and a
  Safe for the test treasury (no real money or private keys in the repo), document
  addresses openly.
- [ ] **Outreach templates (INBOX #8):** a contact list + letter templates RU/EN
  for the "public good" mission. Sent by the operator personally.

### P2 — quality and transparency

- [ ] **CONTRIBUTING.md (+EN)** — how an outside person can participate (issues, PRs,
  governance proposals), a code of conduct, links to the constitution.
- [ ] **Glossary** of key terms (DAO, escrow, multisig, registry, distribution
  priority) in plain language, RU/EN — so documents are clear to non-technical readers.
- [ ] **"Transparency" page on the site** — gather links: registry, IPFS manifest,
  CI statuses, how to verify integrity yourself (`registry.py verify`).
- [ ] **Automated bilingual check in CI** — a linter that fails the build if an RU
  doc changed without its EN pair (or vice versa).

### P3 — idea bank (raw, up for discussion)

- [ ] Treasury dashboard (read-only) — public state of the test treasury from the registry.
- [ ] Aid request templates (anonymous, no personal data) — form + schema.
- [ ] "Explain like I'm five" — short explainers for each normative doc.
- [ ] Automated changelog from the decision registry (generate `CHANGELOG.md`).
- [ ] Reputation model for guardians/reviewers (anti-collusion) — draft spec.
- [ ] Turn the landing copy from [`PROMOTION.md`](PROMOTION.md) into a real
  human-oriented page in `web/` (simpler than the normative site; same "no external
  requests/trackers" policy).
- [ ] Project media kit: a single logo/palette/icon (SVG, no external fonts) +
  brief usage rules — so materials look consistent.
- [ ] Press page / one-pager "about the project for press and partners" (RU/EN)
  based on the boilerplate in `PROMOTION.md` — facts, links, contacts, quotable text.

---

## Done

- **PTD-0006 (session 9):** promotion materials [`PROMOTION.md`](PROMOTION.md)
  (+EN) — message rails, boilerplate+disclaimer, landing copy, pitch RU/EN (3
  formats), announcement post (Telegram + Twitter/X), FAQ "public good, NOT an
  investment", publication checklist. All texts checked against the constitutional
  prohibitions. "Ready-to-press" drafts — published by the operator. Closes INBOX #6.
- **PTD-0005 (session 8):** set up the self-development mechanism itself — this
  `ROADMAP.md` (+EN), the rule in `BUILDER.md` ("INBOX empty → next ROADMAP item")
  and the autonomy-by-default mode (INBOX #9). Closes INBOX #5 and #9.

---

## Idea log (who/when proposed)

To keep self-development transparent, we record the origin of ideas.

| Idea | Source | Session |
|------|--------|---------|
| Self-development mechanism (ROADMAP + rule) | operator (INBOX #5) | 8 |
| Autonomy-by-default mode | operator (INBOX #9) | 8 |
| CONTRIBUTING / glossary / transparency page / CI bilingual | agent | 8 |
| Treasury dashboard / request templates / changelog / reputation | agent | 8 |
| Landing page in web / media kit / press page | agent | 9 |
