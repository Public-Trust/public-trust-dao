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
    - [x] Part 3a (session 21): [`Reputation.sol`](../../contracts/contracts/Reputation.sol)
      — a non-transferable (soulbound) member badge per [`GOVERNANCE.md`](GOVERNANCE.md)
      §2–§3: one-person-one-vote (`votingUnits` = 1 + min(points, cap), weight within
      [1..1+cap]), no transfer functions (non-transferable by design), the `verifier`
      mints/revokes the badge, the `governor` sets parameters, no role moves funds;
      11 tests "to green" (35/35 with Treasury+Disbursement). `PTD-0018`.
    - [x] Part 3b (session 22): [`Governor.sol`](../../contracts/contracts/Governor.sol)
      + [`Timelock.sol`](../../contracts/contracts/Timelock.sol) per [`GOVERNANCE.md`](GOVERNANCE.md)
      §4–§7: direct voting (weight from `Reputation.votingUnits`, quorum/period/public
      tally), execution ONLY through the `Timelock` (the Governor never moves funds),
      the `guardian` = emergency veto (`cancel`), the `admin` = a one-off bootstrap
      (`renounceAdmin`), parameters changed by vote only; 15 tests "to green" (50/50
      with all contracts). `PTD-0019`.
    - [x] Part 3c (session 23): [`scripts/deploy.js`](../../contracts/scripts/deploy.js)
      deploys and wires the whole contour (Reputation→Timelock→Treasury/Disbursement→Governor;
      executor=Timelock, governor=Governor, `renounceAdmin`, Reputation.governor=Timelock)
      + an integration test [`Integration.test.js`](../../contracts/test/Integration.test.js)
      "request → vote → Timelock → targeted payout to the provider via `Disbursement`";
      +4 tests to green (54/54 with all contracts). `PTD-0020`.
  - [ ] Part 4: a public testnet run (e.g. Polygon Amoy) — network/RPC/test guardian
    addresses to be agreed with the operator (keys via `contracts/.env`).
- [ ] **Stage 6 — AI agents (skeleton):** in `ai-agents/` describe and set up the
  Guardian/Audit/Fairness/Reputation/Housing/Governance/Mediator/Documentation
  modules as helper scripts for upholding the constitution (service modules, not
  organs of power — Art. 9; read-only with respect to funds, a finding is a signal,
  not an action).
  - [x] Module 1/8 (session 24): the [`ai-agents/`](../../ai-agents/) scaffold
    (README RU/EN with the "AI serves, does not rule" principle and a table of the 8
    agents) + the first working agent **Audit**
    [`audit_agent.py`](../../ai-agents/audit_agent.py) — combines the 4 rail
    validators (registry/ipfs/safe/snapshot) into a single audit run, tying each check
    to the constitution article it protects, with a `--with-contracts` option and
    human-readable / `--json` output; CI
    [`ai-agents.yml`](../../.github/workflows/ai-agents.yml). "To green": 4/4 base,
    5/5 with contracts (54 tests). `PTD-0021`. Also realizes the "one governance
    validator in CI" idea. TESTNET-ONLY.
  - [x] Module 2/8 (session 25): **Guardian** [`guardian_agent.py`](../../ai-agents/guardian_agent.py)
    — an explicit safety-rails scanner across the WHOLE repo tree (git-tracked files):
    no committed secrets/keys (`secrets-tracked`), `.gitignore` covers `.env`/`logs/`
    (`gitignore-guards`), no mainnet `chain_id` (`no-mainnet`), no private keys in text
    (`no-key-material`, 64-hex outside hash fields + secret assignment). A test invariant
    [`test_guardian.py`](../../ai-agents/test_guardian.py) (14/14) proves "red is really
    caught, green doesn't false-fail". CI extended. `PTD-0022`.
  - [x] Module 3/8 (session 26): **Fairness** [`fairness_agent.py`](../../ai-agents/fairness_agent.py)
    — a read-only fairness-of-distribution check over registry records of type
    `disbursement` per [`PRIORITIES.md`](PRIORITIES.md)/[`ANTI-ABUSE.md`](ANTI-ABUSE.md):
    `priority-valid` (level within the 1..10 scale, read directly from PRIORITIES.md),
    `safeguards` (priority does not switch off limit/review/appeal window),
    `collective-review` (≥2 independent confirmations), `staged-payments` (staging),
    `applicant-privacy` (no personal data). Test invariant
    [`test_fairness.py`](../../ai-agents/test_fairness.py) (17/17). As a side effect a
    latent Guardian bug was fixed (it false-flagged its own `test_guardian.py`) — the
    `ai-agents` CI is green again. `PTD-0023`.
  - [x] Module 4/8 (session 27): **Reputation** [`reputation_agent.py`](../../ai-agents/reputation_agent.py)
    — a read-only static analysis of `contracts/contracts/Reputation.sol` and
    `governance/snapshot/space.json`: it proves "1 person = 1 vote" per
    [`GOVERNANCE.md`](GOVERNANCE.md) §2–§3 IN CODE — `soulbound` (no transfer
    functions), `bounded-weight` (weight 0 / `1 + min(points, cap)`, corridor
    [1..1+cap]), `no-funds` (the reputation layer moves no funds), `roles-separated`
    (verifier mints/revokes the badge, governor changes parameters), `off-chain-equal`
    (Snapshot = equal `ticket` value=1, not plutocracy). Test invariant
    [`test_reputation.py`](../../ai-agents/test_reputation.py) (17/17). `PTD-0024`.
  - [x] Module 5/8 (session 28): **Housing** [`housing_agent.py`](../../ai-agents/housing_agent.py)
    — a domain helper for housing cases. Read-only, it proves the targeted-disbursement
    model (docs/ESCROW-TARGETED-DISBURSEMENT.md) "help pays the provider directly, not
    into hand" IN CODE of `contracts/contracts/Disbursement.sol`: `release-to-provider-only`
    (release takes no recipient address → tranche goes strictly to c.provider),
    `provider-fixed` (no setProvider/.provider=), `refund-to-treasury` (refund to the
    treasury, not the recipient), `tranche-limit` (maxRelease cap), `guardian-cannot-move`
    (only executor moves funds) + housing registry-record checks
    (`targeted-escrow`/`provider-onchain`/`category-priority`, level read from
    PRIORITIES.md). Test invariant [`test_housing.py`](../../ai-agents/test_housing.py)
    (23/23). CI extended (+ triggers on contracts/contracts and docs/PRIORITIES.md). `PTD-0025`.
  - [x] Module 6/8 (session 29): **Documentation** [`documentation_agent.py`](../../ai-agents/documentation_agent.py)
    — a read-only check of RU↔EN bilinguality and link integrity over git-tracked
    `.md`: `bilingual-pairs` (every public doc has an RU↔EN pair — pairing rule
    derived from the path), `language-switcher` (a correct `[Русский]·[English]`
    switcher at the top, pointing to the paired file), `link-integrity` (all relative
    links resolve; external links and code fences excluded). Invariant test
    [`test_documentation.py`](../../ai-agents/test_documentation.py) (17/17). On its
    first run it caught and closed a real gap — EN mirrors were added for
    `governance/ipfs/README.md` and `governance/registry/README.md`. Also closes the
    P2 "automatic bilingual check in CI". `PTD-0026`.
  - [x] Module 7/8 (session 30): **Governance** [`governance_agent.py`](../../ai-agents/governance_agent.py)
    — read-only check of the PROPOSAL LIFECYCLE from `GOVERNANCE.md` over the governance
    configs `governance/snapshot/space.json` and `governance/safe/safe.config.json` (it
    does NOT vote itself): `one-person-one-vote` (vote strategy `ticket` value=1, not
    plutocracy), `timed-vote` (`delay`/`period` > 0), `off-chain-signal`
    (`off_chain_signaling=true` and all types `binding=false`), `proposal-binding`
    (`disbursement-direction`→PRIORITIES+ANTI-ABUSE; `constitution-amendment`→CONSTITUTION+`requires_supermajority`),
    `multisig-not-sole` (threshold ≥2 and below the owner count, 3-of-5), `lifecycle-links`
    (config links resolve). Invariant test [`test_governance.py`](../../ai-agents/test_governance.py)
    (26/26). CI extended. On the real configs: 6/6. `PTD-0027`.
  - [ ] Module 8/8 — last: **Mediator** (structures disputes/appeals per `ANTI-ABUSE.md`,
    does not decide) — "to green". Closes the framework for all eight agents.

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

- [x] **CONTRIBUTING.md (+EN)** — how an outside person can participate (issues, PRs,
  governance proposals), a code of conduct, links to the constitution.
  → Done (session 34), [`CONTRIBUTING.en.md`](../../CONTRIBUTING.en.md), `PTD-0031`.
  Emphasis "contribution ≠ power over the treasury" (1 person = 1 vote; authorship = recognition).
- [x] **Glossary** of key terms (DAO, escrow, multisig, registry, distribution
  priority) in plain language, RU/EN — so documents are clear to non-technical readers.
  → Done (session 36), [`GLOSSARY.md`](GLOSSARY.md), `PTD-0033`. ~40 terms in 5
  groups (basics / governance / money and aid / transparency / safety), each
  linking to its normative doc; closes with "three things to keep in mind."
- [x] **CODE_OF_CONDUCT.md (+EN)** — split the code of conduct out of CONTRIBUTING into
  a separate canonical file (GitHub recognizes and surfaces it on the "Community" page),
  linking to the constitution/principles (proposed session 34).
  → Done (session 35), [`CODE_OF_CONDUCT.en.md`](../../CODE_OF_CONDUCT.en.md), `PTD-0032`.
  Key: breaking the safety rails = breaking the code; decisions are made by people
  (not an agent, Art. 9); privacy of reporters/recipients; Contributor Covenant 2.1 attribution.
- [x] **Issue/PR templates (.github/ISSUE_TEMPLATE, PULL_REQUEST_TEMPLATE)** — channel
  contributions into the CONTRIBUTING formats (bug/idea/governance proposal; rails
  checklist: bilingual, no secrets, TESTNET) — a "ready to click" stub for outsiders
  (proposed session 34).
  → Done (session 37), `.github/ISSUE_TEMPLATE/` (config + 4 YAML forms) +
  `.github/pull_request_template.md` (bilingual), `PTD-0034`. All forms are
  bilingual and carry constitution-rails checklists; issue forms are YAML
  (structured, excluded from the .md scan); the PR template was added to the
  Documentation agent's SINGLE_LANG (a GitHub form, bilingual within itself).
- [x] **"Transparency" page on the site** — gather links: registry, IPFS manifest,
  CI statuses, how to verify integrity yourself (`registry.py verify`).
  → Done (session 38), [`web/transparency.html`](../../web/transparency.html) (+EN),
  `PTD-0035`. CI statuses are given as links, not badge images — zero outgoing requests.
- [x] **Automated bilingual check in CI** — a linter that fails the build if an RU
  doc has no EN pair (or vice versa), a missing switcher, or a broken link.
  → Implemented by the Documentation agent (session 29):
  [`ai-agents/documentation_agent.py`](../../ai-agents/documentation_agent.py), `PTD-0026`.

### P3 — idea bank (raw, up for discussion)

- [ ] **GitHub label catalog `.github/labels.yml`** — a single set of labels
  (`bug`, `idea`, `governance`, `safety`, …) referenced by the issue forms, so
  label colors/descriptions are reproducible and not set up by hand (proposed session 37).
- [ ] **Glossary link in the header of normative docs** — add a link to
  [`GLOSSARY.md`](GLOSSARY.md) to each doc's "Derived from …" line, so an unfamiliar
  term is one click away from any document (proposed in session 36).
- [ ] **Documentation agent: a soft "term is defined" check** — a light dictionary
  linter that, for a list of key terms (DAO/escrow/multisig/…), checks the project
  has an entry in `GLOSSARY.md`; non-blocking, just a warning, so the glossary does
  not fall behind the documents (proposed in session 36).
- [ ] **SECURITY.md (+EN)** — canonical security policy file (GitHub recognizes it
  and shows a "Report a vulnerability" button): where and how to report a rails/contract
  flaw, what's in scope (testnet only), what we do NOT promise (no real-money bounty
  before audit), private channel = the same `security@` from [`EMAIL-SETUP.md`](EMAIL-SETUP.md).
  Complements CODE_OF_CONDUCT (breaking the rails = breaking conduct) and the Guardian
  agent (proposed session 35).
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
- [x] One governance validator in CI: a single script runs `registry.py verify`
  + `ipfs_manifest.py verify` + `safe_config.py verify` + `snapshot_config.py verify`
  in one command (a convenient green/red for the whole governance layer).
  → Realized by the Audit agent (session 24): [`ai-agents/audit_agent.py`](../../ai-agents/audit_agent.py), `PTD-0021`.
- [ ] Test invariant "no treasury money bypasses the registry": check that every
  on-chain `Released(registryRef)` event has a record in `governance/registry/`
  (and vice versa) — tie the contract to the decision registry (proposed session 19).
- [ ] A deploy script `contracts/scripts/deploy.js` (Hardhat) wiring the Safe
  multisig addresses as the `executor` — a "ready-to-press" testnet stub (proposed session 19).
- [ ] Test invariant for the Audit agent: feed it a "broken" governance artifact
  (broken chain / manifest drift) and check it returns "red" — so the audit itself is
  provably working, not "green by default" (session 24).
- [x] Guardian agent: an explicit repo-wide safety-rail scanner (no 64-hex keys /
  `mnemonic` / `seed`, no mainnet chain_id, `.env` not staged) — reuse and generalize
  the checks from `safe_config.py`/`snapshot_config.py` (session 24).
  → Realized (session 25): [`guardian_agent.py`](../../ai-agents/guardian_agent.py) +
  test invariant [`test_guardian.py`](../../ai-agents/test_guardian.py), `PTD-0022`.
- [x] Documentation agent: an RU↔EN bilingual linter (an RU doc ↔ its EN mirror) +
  relative-link integrity — also closes the P2 item "automatic bilingual check in
  CI" (session 24). → Implemented (session 29):
  [`documentation_agent.py`](../../ai-agents/documentation_agent.py) +
  [`test_documentation.py`](../../ai-agents/test_documentation.py), `PTD-0026`.
- [x] Meta-agent "run all": a single `ai-agents/run_all.py` entry point that runs every
  ready agent (Audit + Guardian + …) in sequence and folds their reports into one
  "green/red" for the whole project (session 25).
  → Implemented (session 32): [`run_all.py`](../../ai-agents/run_all.py) +
  [`test_run_all.py`](../../ai-agents/test_run_all.py) (13/13); CI collapsed from
  ~15 steps to 2, `PTD-0029`.
- [ ] Guardian: a `pre-commit` hook/instruction — a local hook that runs Guardian
  before a commit so a secret never reaches the index in the first place (session 25).
- [ ] Extend Guardian with URL-rail checks: no "yield promises"/"investment"/"guarantee"
  in public texts (the literal constitutional prohibitions of PRINCIPLES.md) — a light
  lexical linter for the landing/README (session 25).
- [ ] A "payment ↔ registry record" invariant for Fairness/Audit: verify every on-chain
  payment has a `disbursement` record in the registry (and vice versa) — tie the
  `Disbursement` contract and the registry into one end-to-end check (session 26).
- [ ] Agent self-test as a CI rule: every new agent must ship a `test_<agent>.py`
  invariant, and CI runs them all — so no agent is "green by default" (Stage 6 quality
  standard, proposed session 26).
- [ ] Fairness: check `category` ↔ `priority_level` consistency (e.g. `housing` should
  usually not sit below the "housing-loss threat" level) — a soft, non-blocking warning
  to catch obvious categorization skew (session 26).
- [ ] Reputation agent: extend the static "1 person = 1 vote" analysis to `Governor.sol`
  (vote weight comes from `Reputation.votingUnits`, not from balance; the proposal
  threshold is equal, not monetary) — close the check over the whole voting chain, not
  just the badge (session 27).
- [ ] Reputation agent: cross-check `reputationCap` in `scripts/deploy.js`/the deploy
  config against a sane ceiling (e.g. ≤ a small N), so the contribution multiplier cannot
  quietly turn into a new elite via too high a cap (session 27).
- [ ] A reusable lightweight Solidity-invariant scanner module: extract comment stripping
  + brace-balanced function-body extraction from the Reputation agent into a shared
  `ai-agents/solidity_scan.py` — useful for future contract agents (Governance/Audit) (session 27).
  The Housing agent (session 28) duplicated the same helpers
  (`strip_solidity_comments`/`_function_body`/`_function_sig`) — now THREE copies, the
  refactor is overdue.
- [ ] Housing agent: once a provider whitelist exists (open question in
  [`ESCROW-TARGETED-DISBURSEMENT.md`](ESCROW-TARGETED-DISBURSEMENT.md) §8 — who maintains
  and verifies landlords/pharmacies), add a `provider-whitelisted` check: a housing
  record's `provider` is in the public registry of verified providers (category
  `housing`) — closing the critical trust point of model B (session 28).
- [ ] End-to-end Housing invariant "record ↔ on-chain escrow": verify that a housing
  record's `escrow_id` matches a real case opened in `Disbursement` (via `Opened(id, …,
  provider, …)` events) and the record's `provider` = the case's `provider` — tying the
  registry and the contract into one targeted-disbursement check (extends the "payout ↔
  registry record" idea, session 28).
- [ ] Documentation agent: a "translation freshness" check — an RU doc and its EN
  mirror should change IN THE SAME commit (git diff: if only one of the pair is touched
  in a commit/diff — a soft warning). Closes "bilinguality is in sync", not just "both
  files exist" (session 29).
- [ ] Documentation agent: link-anchor check (`FILE.md#section`) — that `#section`
  matches a real heading in the target file, so internal links don't rot when sections
  are renamed (session 29).
- [ ] A lexical linter of constitutional prohibitions for public texts
  (README/web/PROMOTION): no "guaranteed returns"/"investment"/"pyramid"/"referrals"
  (the literal prohibitions of `PRINCIPLES.md`) — could become part of Documentation or
  a separate mini-agent (session 29; previously proposed as a Guardian extension).
- [ ] Run-All: a machine-readable status badge in `governance/` (the last
  `run_all --json` verdict saved to an artifact file) — a basis for a future public
  "status traffic light" with no external services (session 32).
- [x] Test invariant for Audit (`test_audit.py`) — the only agent without its own
  invariant; feed a "broken" governance artifact and check Audit goes red (close the
  Stage-6 quality-standard gap; session 32).
  → Done (session 33): [`test_audit.py`](../../ai-agents/test_audit.py) (9/9) —
  run_check (pass/fail/error) + main folding + integration with the real validators on
  poisoned temporary copies (mainnet chain_id; plutocratic strategy); added to `run_all`
  (tests 8/8). `PTD-0030`. **All 8 agents now have invariants.**
- [ ] A shared module `ai-agents/agent_report.py` — a single report helper
  (`{agent, verdict, passed, total, checks}` + human-readable renderer) so the eight
  agents don't duplicate the same print code and don't drift in the format `run_all`
  relies on (session 32; akin to the `solidity_scan.py` idea).
- [ ] **Disk hygiene as a rail:** a light script/doc on how the builder agent keeps the
  disk clean — `contracts/node_modules` (gitignored, ~300 MB) and caches must not pile
  up; perhaps `npm ci` in CI only, cleaned locally. In session 33 the disk hit ~100%
  full (mostly other host projects) and nearly blocked the build (proposed session 33).
  See "NEEDED FROM THE OPERATOR".
- [ ] **"Every agent has an invariant" as an explicit CI check:** a mini-script that
  fails if a `*_agent.py` appears in `ai-agents/` without a paired `test_*.py` (and vice
  versa) — so the Stage-6 quality gap (as Audit had) can never reappear unnoticed
  (proposed session 33; akin to "agent self-test in CI").

---

## Done

- **PTD-0035 (session 38):** P2 (quality/transparency) — **"Transparency — verify it
  yourself" page** on the site: [`web/transparency.html`](../../web/transparency.html)
  (+EN mirror `transparency.en.html`). It gathers in one place the links to the
  verifiable artifacts (public decision registry, IPFS manifest, CI statuses on GitHub
  Actions, smart contracts and tests, AI agents) and gives step-by-step commands to
  verify integrity yourself (`git clone`; `scripts/registry.py verify`;
  `scripts/ipfs_manifest.py verify`; `ai-agents/audit_agent.py [--with-contracts]`;
  cross-check with the public CI). The current registry `head_hash` is shown as the
  final fingerprint of the whole chain. **The "zero outgoing requests" rail is kept:**
  CI statuses are given as text links, not badge images from a third-party server. The
  page is linked from the "Transparency" section and the footer of both `index` files.
  Documentation agent and Audit are green. TESTNET-ONLY.
- **PTD-0034 (session 37):** P2 (quality/transparency) — **issue/PR templates**.
  `.github/ISSUE_TEMPLATE/` (`config.yml` + 4 YAML forms: bug/inaccuracy, idea,
  governance proposal, abuse risk/safety-rail hole) + a bilingual
  `.github/pull_request_template.md`. All forms are bilingual (RU+EN in one body)
  and carry constitution-rails checklists (public good NOT an investment;
  TESTNET-first; no secrets in the repo; RU↔EN bilingual; tests green; transparency
  via the registry). Issue forms are YAML (structured, validate fields, excluded
  from the .md bilingual scan); the PR template is markdown (GitHub requirement),
  bilingual within itself, added to the Documentation agent's `SINGLE_LANG`.
  `config.yml` disables blank issues and links to CONTRIBUTING/CODE_OF_CONDUCT/ROADMAP;
  the safety form asks not to post live exploit steps (private channel — once the
  email is set up). Mentioned in CONTRIBUTING (RU/EN). Documentation agent green,
  `run_all --with-tests`: agents 8/8, tests 8/8. `PTD-0034`. TESTNET-ONLY.
- **PTD-0033 (session 36):** P2 (quality/transparency) — **glossary**.
  [`GLOSSARY.md`](GLOSSARY.md) (+ RU [`../GLOSSARY.md`](../GLOSSARY.md)) — ~40 key
  project terms in **plain language** for non-technical readers, in 5 meaning
  groups (basics; governance and voting; money and aid; transparency and
  verifiability; safety and technology). Each term has a short, "for a person
  without background" definition + a link to the normative document where it is
  fixed (CONSTITUTION/GOVERNANCE/PRIORITIES/ANTI-ABUSE/contracts). Closes the
  mission's "accessibility" gap: documents are clear beyond technical readers.
  Added to the doc map of both READMEs; Documentation agent green (RU↔EN pair /
  switcher / 0 broken links). `PTD-0033`. TESTNET-ONLY.
- **PTD-0031 (session 34):** P2 (quality/transparency) — **CONTRIBUTING.md (+EN)**.
  [`CONTRIBUTING.md`](../../CONTRIBUTING.md) + [`CONTRIBUTING.en.md`](../../CONTRIBUTING.en.md)
  — an open entry point for an outside contributor: where to start; four ways to
  contribute (issue; PR on a doc/code; governance proposal; path to a verified
  participant/guardian); contribution rails (public good NOT an investment, TESTNET-first,
  no secrets in the repo, bilingual RU↔EN in the same PR, transparency via the registry,
  applicant privacy); a code of conduct; integrity self-check commands
  (`registry.py verify`, `run_all.py --with-tests`); contribution licensing. The key
  constitutional emphasis is up front — **contribution ≠ power over the treasury**
  (distribution is governed by the constitution and "1 person = 1 vote" voting;
  authorship = recognition, not ownership; aligned with [`AUTHORS.en.md`](../../AUTHORS.en.md)
  and [`GOVERNANCE.md`](GOVERNANCE.md)). Added to the doc map of both READMEs and to the
  root-files table in REPO-STRUCTURE (RU/EN). Documentation agent green (pairs/switcher/
  links), `run_all --with-tests`: agents 8/8, tests 8/8. `PTD-0031`. TESTNET-ONLY.
- **PTD-0030 (session 33):** Stage 6 (AI agents), quality standard — **the Audit test
  invariant**. [`test_audit.py`](../../ai-agents/test_audit.py) (9/9) closes the last
  scaffold gap: Audit was the only agent without its own invariant. It proves Audit
  **folds the verdict honestly, not "green by default"**: `run_check` (exit0→pass /
  exit1→fail / crashed command→error), `main` folding (any fail/error → red), and
  integration with the REAL rail validators (`safe_config.py`/`snapshot_config.py`) on
  poisoned TEMPORARY config copies (a Safe with a mainnet `chain_id`; a Snapshot with a
  plutocratic strategy) → red, while staying green on the healthy repo. The real configs
  are not modified. Added to `run_all` (TESTS) → tests 8/8. `PTD-0030`. **All eight
  agents now have invariants.** TESTNET-ONLY.
- **PTD-0029 (session 32):** Stage 6 (AI agents), consolidation of the 8/8 scaffold —
  **the Run-All meta-agent**. [`run_all.py`](../../ai-agents/run_all.py) — a read-only
  service meta-module (Art. 9): runs all eight agents with `--json` and folds their
  reports into one "green/red" verdict. A single entry point: a local self-check in
  one command instead of eight; CI collapsed from ~15 steps to two (`--with-tests`
  runs both the agents and their seven test invariants); `--with-contracts` is passed
  through to Audit; `--json` is a machine-readable summary. It treats an agent as "red"
  not only by its verdict but on any anomaly (invalid JSON = the agent crashed;
  `verdict=green` with exit code ≠ 0). The **test invariant**
  [`test_run_all.py`](../../ai-agents/test_run_all.py) (13/13) on fake agents/tests
  proves "red folds into red, green does not fail falsely". On the real repo: agents
  8/8, tests 7/7. `PTD-0029`. TESTNET-ONLY.
- **PTD-0027 (session 30):** Stage 6 (AI agents), module 7/8 — **the Governance agent**.
  [`governance_agent.py`](../../ai-agents/governance_agent.py) — a read-only service agent
  (Art. 9; it **does NOT vote**, submit, or move anything): turns the proposal lifecycle
  from `GOVERNANCE.md` into a machine check over the governance configs
  `governance/snapshot/space.json` and `governance/safe/safe.config.json`. Six checks:
  `one-person-one-vote` (vote strategy = `ticket` value=1; any balance-weighted plutocracy
  goes red — Art. 2/ban #5), `timed-vote` (vote duration `delay`/`period` > 0 — §7),
  `off-chain-signal` (`off_chain_signaling=true` and every type `binding=false` — Snapshot
  discusses, Safe/Timelock executes — Art. 4/§5), `proposal-binding` (money/constitution
  types tied to PRIORITIES/ANTI-ABUSE/CONSTITUTION + supermajority for amendments —
  Art. 5/§7–§8/Art. 10), `multisig-not-sole` (Safe threshold ≥2 and below the owner count,
  3-of-5, no one single-handed — Art. 5/§5), `lifecycle-links` (all config links resolve —
  Art. 3). Invariant test [`test_governance.py`](../../ai-agents/test_governance.py) (26/26).
  CI `ai-agents.yml` extended (+ Governance test + Governance). On the real configs: 6/6.
  `PTD-0027`. TESTNET-ONLY. Next — the last module 8/8 (Mediator).
- **PTD-0026 (session 29):** Stage 6 (AI agents), module 6/8 — **the Documentation
  agent**. [`documentation_agent.py`](../../ai-agents/documentation_agent.py) — a
  service read-only agent: it turns the project rule "all documentation is bilingual
  (RU↔EN)" and constitutional verifiability (Art. 3) / openness (Art. 6) into a machine
  check. Three checks over git-tracked `.md`: `bilingual-pairs` (every public doc has
  an RU↔EN pair — the pairing rule is derived from the path: `docs/NAME.md`↔`docs/en/NAME.md`;
  `<dir>/README.md`↔`<dir>/README.en.md`; root `NAME.md`↔`NAME.en.md`),
  `language-switcher` (a correct `[Русский]·[English]` switcher at the top, pointing to
  the paired file), `link-integrity` (all relative links resolve; external links and
  code fences excluded — no false positives). Single-language internal files
  (`BUILDER`/`LAUNCH`/`PROGRESS`/`DECISIONS`/`comms`) are excluded by design.
  Human-readable and `--json` output; exit 0/1; "red" = a signal. The **invariant
  test** [`test_documentation.py`](../../ai-agents/test_documentation.py) (17/17)
  proves "red is caught, green doesn't fail falsely". **Immediate value:** on its first
  run the agent caught a real bilinguality gap — `governance/ipfs/README.md` and
  `governance/registry/README.md` had no EN mirrors; EN mirrors + switchers were added
  (now 8/8 checks green). Also closes the P2 "automatic bilingual check in CI". CI
  [`ai-agents.yml`](../../.github/workflows/ai-agents.yml) extended (+ Documentation
  test + Documentation; triggers on `**/*.md`, `*.md`). `PTD-0026`. TESTNET-ONLY. Next —
  modules 7–8 (Governance / Mediator).
- **PTD-0025 (session 28):** Stage 6 (AI agents), module 5/8 — **the Housing agent**.
  [`housing_agent.py`](../../ai-agents/housing_agent.py) is a service read-only agent, a
  domain helper for housing cases: it proves the targeted-disbursement model
  ([`ESCROW-TARGETED-DISBURSEMENT.md`](ESCROW-TARGETED-DISBURSEMENT.md)) — "help pays the
  provider directly, not into hand" — is built INTO THE CODE of
  [`Disbursement.sol`](../../contracts/contracts/Disbursement.sol): `release-to-provider-only`
  (release takes no recipient address → tranche strictly to c.provider), `provider-fixed`
  (no setProvider/.provider=), `refund-to-treasury` (refund to treasury, not the recipient),
  `tranche-limit` (maxRelease cap), `guardian-cannot-move` (only executor moves funds;
  guardian only pauses) + housing registry-record checks
  (`targeted-escrow`/`provider-onchain`/`category-priority`, level read from
  [`PRIORITIES.md`](PRIORITIES.md)). Human-readable and `--json` output; exit 0/1; "red" =
  a signal. A **test invariant** [`test_housing.py`](../../ai-agents/test_housing.py) (23/23)
  proves "red is caught, green doesn't false-fail" (poisoned contract/record versions;
  non-housing records ignored; comments stripped). CI
  [`ai-agents.yml`](../../.github/workflows/ai-agents.yml) extended (+ triggers on
  contracts/contracts and docs/PRIORITIES.md). On the real `Disbursement.sol`: 8/8.
  `PTD-0025`. TESTNET-ONLY. Next — modules 6–8 (Governance / Mediator / Documentation).
- **PTD-0024 (session 27):** Stage 6 (AI agents), module 4/8 — **the Reputation agent**.
  [`reputation_agent.py`](../../ai-agents/reputation_agent.py) is a service read-only
  agent: it statically analyzes the on-chain reputation contract
  [`Reputation.sol`](../../contracts/contracts/Reputation.sol) and the off-chain settings
  [`space.json`](../../governance/snapshot/space.json) and proves the "1 person = 1 vote"
  model ([`GOVERNANCE.md`](GOVERNANCE.md) §2–§3) is preserved IN CODE: `soulbound` (the
  badge has no transfer functions — the vote can't be sold), `bounded-weight`
  (`votingUnits`: non-member → 0, member → `1 + min(points, cap)`, corridor [1..1+cap] —
  power of money is impossible), `no-funds` (the reputation layer moves no funds —
  "uniqueness ≠ power"), `roles-separated` (verifier confirms uniqueness, governor changes
  parameters; roles not mixed), `off-chain-equal` (the Snapshot strategy is the equal
  `ticket` value=1, not balance plutocracy; members-only voting). Human-readable and
  `--json` output; exit 0/1; "red" = a signal. A **test invariant**
  [`test_reputation.py`](../../ai-agents/test_reputation.py) (17/17) proves "red is caught,
  green doesn't false-fail" (including ignoring mentions in Solidity comments). CI
  [`ai-agents.yml`](../../.github/workflows/ai-agents.yml) extended. `PTD-0024`.
  TESTNET-ONLY. Next — modules 5–8 (Housing / Governance / Mediator / Documentation).
- **PTD-0023 (session 26):** Stage 6 (AI agents), module 3/8 — **the Fairness agent**.
  [`fairness_agent.py`](../../ai-agents/fairness_agent.py) is a service read-only agent:
  it walks the public registry records of type `disbursement` and checks EVERY payment
  for fairness of distribution and anti-abuse — `priority-valid` (priority level within
  the 1..10 scale, read DIRECTLY from [`PRIORITIES.md`](PRIORITIES.md)), `safeguards`
  (priority does not switch off `limit_ok`/`collective_review`/appeal window),
  `collective-review` (≥2 independent confirmations, not single-person), `staged-payments`
  (`1<=index<=of`), `applicant-privacy` (no personal data — only the pseudonymous
  `case_id`). Human-readable and `--json` output; exit 0/1; "red" is a signal. A **test
  invariant** [`test_fairness.py`](../../ai-agents/test_fairness.py) (17/17) proves "red
  is caught, green doesn't false-fail" (including an empty registry). **Side effect:** a
  latent bug from session 25 was found and fixed — Guardian false-flagged its own test
  invariant (the `private_key: 0x...` fixture string), which made the `ai-agents` CI on
  `main` effectively red; Guardian now skips text-scanning the agents' test invariants
  (`ai-agents/test_*.py`), plus a regression scenario. CI
  [`ai-agents.yml`](../../.github/workflows/ai-agents.yml) extended. `PTD-0023`.
  TESTNET-ONLY. Next — modules 4–8 (Reputation / Housing / …).
- **PTD-0022 (session 25):** Stage 6 (AI agents), module 2/8 — **the Guardian agent**.
  [`guardian_agent.py`](../../ai-agents/guardian_agent.py) is a dedicated, explicit
  safety-rails scanner across the WHOLE repo tree (over git-tracked files):
  `secrets-tracked` (no committed secrets/keys/pulse-state), `gitignore-guards`
  (`.gitignore` covers `.env`/`logs/`), `no-mainnet` (no mainnet `chain_id` in JSON),
  `no-key-material` (no private keys in text: 64-hex outside hash fields + `private
  key`/`mnemonic`/`seed` assignment). No false positives on the registry's and
  manifest's legitimate sha256/CID (64-hex counts as a key only outside hash fields).
  A **test invariant** [`test_guardian.py`](../../ai-agents/test_guardian.py) (14/14)
  on a throwaway git repo proves "red is really caught, green doesn't false-fail". CI
  [`ai-agents.yml`](../../.github/workflows/ai-agents.yml) extended (Audit + Guardian
  test + Guardian). `PTD-0022`. TESTNET-ONLY. Next — modules 3–8 (Fairness / Reputation / …).
- **PTD-0021 (session 24):** Stage 6 (AI agents), module 1/8 — **the
  [`ai-agents/`](../../ai-agents/) scaffold + the first working agent Audit**. The
  README (RU/EN) fixes the Art. 9 principle "AI serves, does not rule" and the
  boundaries for all agents (read-only with respect to funds, a finding is a signal,
  not an action), plus a table of the eight agents.
  [`audit_agent.py`](../../ai-agents/audit_agent.py) combines the four rail validators
  (`registry`/`ipfs`/`safe`/`snapshot`) into a single audit run and ties each check to
  the constitution article it protects (Art. 3/2/4); the `--with-contracts` option adds
  the contract tests (Art. 4/7); output is human-readable and `--json`; exit code 0/1.
  CI [`ai-agents.yml`](../../.github/workflows/ai-agents.yml) on push/PR. "To green":
  4/4 base, 5/5 with contracts (54 tests). Also realizes the "one governance validator
  in CI" idea. On its first run the agent caught a real IPFS-manifest drift (fixed).
  TESTNET-ONLY. Next — module 2/8 (Guardian) and the rest.
- **PTD-0020 (session 23):** Stage 5 (Smart contracts), part 3c — **wiring the whole
  on-chain contour**. [`contracts/scripts/deploy.js`](../../contracts/scripts/deploy.js)
  deploys five contracts and links them into a single mechanism
  (Reputation→Timelock→Treasury/Disbursement→Governor): the treasury/escrow `executor`
  = `Timelock`, the Timelock `governor` = `Governor`, the bootstrap admin is dropped
  (`renounceAdmin`), `Reputation.governor` = `Timelock`. After wiring no one moves
  funds alone (the deployer keeps no privileges; only a passed+delayed vote executes).
  The integration test [`Integration.test.js`](../../contracts/test/Integration.test.js)
  runs the fund's main scenario "aid case → direct vote → `Timelock` delay →
  **targeted payout straight to the provider** via `Disbursement`", plus guardian veto
  and a wiring check; +4 tests to green (54/54 with all contracts). `npm run deploy:local`
  for a demo. TESTNET-ONLY. The Stage 5 skeleton is now assembled end to end; next is
  part 4 (a public testnet, network with the operator) or Stage 6.
- **PTD-0019 (session 22):** Stage 5 (Smart contracts), part 3b — the
  [`Governor.sol`](../../contracts/contracts/Governor.sol) + [`Timelock.sol`](../../contracts/contracts/Timelock.sol)
  contracts per [`GOVERNANCE.md`](GOVERNANCE.md) §4–§7. Direct voting by verified
  members: `propose`/`castVote`/`queue`/`execute`, vote weight from
  `Reputation.votingUnits` (one-person-one-vote, not plutocracy), quorum/period, a
  public deterministic tally. A passed decision is executed **only through the
  `Timelock`** (a mandatory delay = an audit/appeal window; the Governor never moves
  funds itself — the treasury does, on the Timelock's order). The `guardian` =
  emergency veto (`cancel`), the `admin` = a one-off bootstrap (`renounceAdmin`);
  parameters and roles change by vote only (`onlyTimelock`/`onlySelf`). 15 tests "to
  green", including the full cycle "proposal → vote → Timelock → pay the provider"
  (50/50 with all contracts). TESTNET-ONLY. Next — part 3c (wiring) and part 4 (testnet deploy).
- **PTD-0018 (session 21):** Stage 5 (Smart contracts), part 3a — the
  [`Reputation.sol`](../../contracts/contracts/Reputation.sol) contract: a
  non-transferable (soulbound) verified-member badge per [`GOVERNANCE.md`](GOVERNANCE.md)
  §2–§3. One-person-one-vote in code: `votingUnits(addr)` = 0 for a non-member and
  1 + min(`reputationPoints`, `reputationCap`) for a member — the weight always stays
  within [1..1+cap], money cannot buy power. Soulbound: the contract has **no transfer
  functions** (transfer/approve/transferFrom) by design. "Uniqueness ≠ power": the
  `verifier` mints/revokes the badge, the `governor` sets parameters, no role moves
  funds. Revoking resets weight to 0 and reputation. 11 tests "to green" (35/35 with
  Treasury+Disbursement). TESTNET-ONLY. Next — part 3b (`Governor`+`Timelock`).
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
| Audit test invariant / Guardian agent / Documentation agent (bilingual) | agent | 24 |
| Meta-agent "run all" / pre-commit hook / lexical prohibitions linter | agent | 25 |
| "Payment ↔ registry record" invariant / agent self-test in CI / Reputation agent | agent | 26 |
| Reputation on Governor.sol / deploy cap check / shared solidity_scan.py | agent | 27 |
| Refactor shared solidity helpers (3 copies) / Housing provider-whitelist / end-to-end "record ↔ on-chain escrow" test | agent | 28 |
| Meta-agent run_all / lexical prohibition linter for public texts / changelog from the registry | agent | 29 |
| run_all status badge / Audit test invariant / shared agent_report.py | agent | 32 |
| Disk cleanup (node_modules) / "all agents have invariants" standard / sol-helpers refactor | agent | 33 |
| CONTRIBUTING (done) / CODE_OF_CONDUCT as separate file / issue+PR templates | agent | 34 |
| Glossary (done) / glossary link in doc headers / agent term check | agent | 36 |
| Issue/PR templates (done) / GitHub labels in .github/labels / branch autosetup | agent | 37 |
