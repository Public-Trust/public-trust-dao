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
- [x] **Stage 4 — Governance, part 1:** Snapshot space mock-up (off-chain) in
  `governance/snapshot/` — `space.json`/README per [`GOVERNANCE.md`](GOVERNANCE.md):
  "1 human = 1 vote" strategy (not plutocracy), quorum, proposal types, link to the
  constitution (distribution priority, appeals).
  → Done (session 18), [`governance/snapshot/`](../../governance/snapshot/),
  `PTD-0015` (config + JSON schema + README RU/EN + rail validator
  `scripts/snapshot_config.py` + CI). Creating the space (ENS/controller) — operator request.
- [x] **Stage 4 — Governance, part 2:** Safe multisig mock-up, 5 guardians (3-of-5)
  in `governance/safe/` — scheme, roles (executor/emergency pause per
  [`GOVERNANCE.md`](GOVERNANCE.md)), signing policy, no real addresses.
  → Done (session 16), [`governance/safe/`](../../governance/safe/), `PTD-0013`
  (with INBOX #10: config + rail validator + CI).
- [ ] **Stage 5 — Smart contracts (skeleton):** set up `contracts/` as a project
  (Foundry/Hardhat config), skeletons for Treasury / Disbursement (per
  [`ESCROW-TARGETED-DISBURSEMENT.md`](ESCROW-TARGETED-DISBURSEMENT.md)) /
  Governance / Reputation + first tests "to green". Testnet/local only.
  - [x] Part 1 (session 19): the `contracts/` project (Hardhat + ethers v6 + chai,
    Solidity 0.8.24) + the [`Treasury.sol`](../../contracts/contracts/Treasury.sol)
    skeleton (release only via executor=multisig/Timelock, per-release cap, emergency
    pause, events + registryRef) + 10 tests "to green" + CI. `PTD-0016`. TESTNET-ONLY.
  - [x] Part 2 (session 20): [`Disbursement.sol`](../../contracts/contracts/Disbursement.sol)
    — targeted escrow `open/release/refund/pause`; the tranche goes strictly to the
    provider fixed in the case ("we don't hand out cash — we pay the need"), `refund`
    to the treasury, per-tranche cap, only the executor moves funds, the guardian only
    pauses; 14 tests "to green" (24/24 with Treasury); the registry schema gained
    `provider/category/escrow_id`. `PTD-0017`.
  - [ ] Part 3: `Governance` (Governor → Timelock) + `Reputation` (soulbound badge).
  - [ ] Part 4: a public testnet run (network to be agreed with the operator).
- [ ] **Stage 6 — AI agents (skeleton):** in `ai-agents/` describe and set up the
  Guardian/Audit/Fairness/Reputation/Housing/Governance/Mediator/Documentation
  modules as helper scripts for upholding the constitution (start with one — e.g.
  Audit, running `registry.py verify` + `ipfs_manifest.py verify`).

### P1 — materials and infrastructure (partly from INBOX)

- [x] **Promotion (INBOX #6):** a landing page for people, a short pitch RU/EN, an
  announcement post, a FAQ "this is a public good, NOT an investment". Prepared by
  the agent; publishing done by the operator. → Done (session 9),
  [`PROMOTION.md`](PROMOTION.md), `PTD-0006`.
- [x] **Project email (INBOX #7):** instructions for the operator — domain+mail
  options (ProtonMail/own domain), texts. Registration done by the operator.
  → Done (session 14), [`EMAIL-SETUP.md`](EMAIL-SETUP.md), `PTD-0011`.
- [x] **Testnet wallet + Safe (INBOX #10):** describe/create a test wallet and a
  Safe for the test treasury (no real money or private keys in the repo), document
  addresses openly. → Done (session 16), [`governance/safe/`](../../governance/safe/),
  `safe.config.json` + `scripts/safe_config.py` (rail validator) + CI, `PTD-0013`.
- [x] **Outreach templates (INBOX #8):** a contact list + letter templates RU/EN
  for the "public good" mission. Sent by the operator personally.
  → Done (session 15), [`OUTREACH.md`](OUTREACH.md), `PTD-0012`.
- [x] **Support/donations model (INBOX):** support comes through the working
  system itself (transparent multisig treasury + contracts, visible in the
  registry), with no separate "Donate" button; a real-money address only after
  launch and an audit. → Done (session 17), [`SUPPORT-MODEL.md`](SUPPORT-MODEL.md), `PTD-0014`.

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
- [ ] Snapshot proposal templates (RU/EN) for each `proposal_type` in
  `governance/snapshot/space.json` — a single format (context / what is proposed /
  link to the constitution / vote options) so proposals are comparable and verifiable.
- [ ] One governance validator in CI: a single script runs `registry.py verify`
  + `ipfs_manifest.py verify` + `safe_config.py verify` + `snapshot_config.py verify`
  in one command (a convenient green/red for the whole governance layer).
- [ ] Test invariant "no treasury money bypasses the registry": check that every
  on-chain `Released(registryRef)` event has a record in `governance/registry/`
  (and vice versa) — tie the contract to the decision registry (proposed session 19).
- [ ] A deploy script `contracts/scripts/deploy.js` (Hardhat) wiring the Safe
  multisig addresses as the `executor` — a "ready-to-press" testnet stub (proposed session 19).

---

## Done

- **PTD-0017 (session 20):** Stage 5 (Smart contracts), part 2 — the targeted-escrow
  contract [`Disbursement.sol`](../../contracts/contracts/Disbursement.sol) per
  [`ESCROW-TARGETED-DISBURSEMENT.md`](ESCROW-TARGETED-DISBURSEMENT.md): `open` fixes
  the provider into the case, `release(id, amount)` **takes no recipient address** —
  the tranche goes strictly to that provider ("we don't hand out cash — we pay the
  need"); `refund` returns the remainder to the treasury (not the recipient); phasing
  (accumulating `released` + per-tranche cap `maxRelease`); escrow backing
  (`available()`); only the `executor` moves funds, the `guardian` only pauses; events
  + `registryRef`. 14 tests "to green" (24/24 with Treasury). The `disbursement`
  registry schema gained `provider/category/escrow_id`. TESTNET-ONLY. Next — part 3
  (`Governance` + `Reputation`).
- **PTD-0016 (session 19):** Stage 5 (Smart contracts), part 1 — the
  [`contracts/`](../../contracts/) project (Hardhat + ethers v6 + chai, Solidity
  0.8.24) + the base [`Treasury.sol`](../../contracts/contracts/Treasury.sol)
  skeleton: the treasury releases funds only via the `executor` (multisig/Timelock),
  a per-release cap, an emergency `guardian` pause, an event on every movement +
  `registryRef` (link to the registry). 10 tests of constitutional properties "to
  green" + CI [`contracts.yml`](../../.github/workflows/contracts.yml). TESTNET-ONLY,
  no real funds/keys. Opens Stage 5 (parts 2–4 — Disbursement/Governance/Reputation/deploy).
- **PTD-0015 (session 18):** off-chain voting mock-up
  [`governance/snapshot/`](../../governance/snapshot/) — `space.json` (Snapshot
  settings: `ticket` value=1 strategy = "1 person = 1 vote", admission for verified
  participants only, proposal types, link to GOVERNANCE/PRIORITIES/CONSTITUTION) +
  JSON schema + README (RU/EN) + rail validator `scripts/snapshot_config.py` (testnet
  only, no token-balance plutocracy, anti-Sybil, no private keys) + CI. Snapshot =
  discussion/signal chamber, does not move funds. Closes Stage 4 part 1.
- **PTD-0014 (session 17):** support model [`SUPPORT-MODEL.md`](SUPPORT-MODEL.md)
  (+EN) — support comes from the working system itself (transparent multisig
  treasury 3-of-5 + contracts, every flow in the registry and on-chain, spending by
  vote), not a separate button/address on the side. Until launch and audit, no
  real-money address is published. On the site — an honest explanation with no donate
  button. Closes the INBOX donations item.
- **PTD-0012 (session 15):** outreach [`OUTREACH.md`](OUTREACH.md) (+EN) —
  recipient categories (with P0–P3 priorities) + where to find an official public
  contact, personalization rules and a "ladder of asks", 5 letter templates RU +
  5 EN, an after-reply protocol, an "agent vs operator" table. Ready-to-send draft:
  the operator sends personally, the agent does not mail. Closes INBOX #8.
- **PTD-0011 (session 14):** project email [`EMAIL-SETUP.md`](EMAIL-SETUP.md)
  (+EN) — option comparison (own domain / ProtonMail / Gmail) with a recommendation,
  addresses/aliases, step-by-step operator guide (Proton quick start + own domain
  with MX/SPF/DKIM/DMARC), signature boilerplate, reply templates RU/EN.
  "Ready-to-click" draft: the operator registers the box and stores the password.
  Closes INBOX #7.
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
| Snapshot proposal templates / one governance validator in CI | agent | 18 |
