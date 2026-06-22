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
- [x] **Stage 6 — AI agents (skeleton): COMPLETE (8/8, session 31).** In `ai-agents/`
  all eight constitution-upholding helper modules are set up (service modules, not
  organs of power — Art. 9; read-only with respect to funds, a finding is a signal,
  not an action), each "to green" and with a test invariant, all in the CI
  `ai-agents.yml`: Audit, Guardian, Fairness, Reputation, Housing, Documentation,
  Governance, Mediator.
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
  - [x] Module 8/8 — last (session 31): **Mediator** [`mediator_agent.py`](../../ai-agents/mediator_agent.py)
    — a read-only check of the dispute/appeal process (the artifact
    [`governance/mediation/dispute-process.json`](../../governance/mediation/dispute-process.json))
    per `ANTI-ABUSE.md` §6: `appeal-for-every-sanction` (every sanction — refusal/
    reputation/freeze/exclusion — has an appeal), `mediator-not-decider` (people decide,
    ≥2, not an AI/one person), `independent-review` (the appeal is decided by someone
    other than the author of the sanction), `valid-lifecycle` (one start/terminal/no dead
    ends/all reachable), `bounded-timelines` (timelines > 0), `process-links` (links
    resolve); it **STRUCTURES, does NOT decide** (Art. 9.2). Test invariant
    [`test_mediator.py`](../../ai-agents/test_mediator.py) (26/26). CI extended. On the
    real artifact: 6/6. **Closed the framework of all eight agents (8/8).** `PTD-0028`.

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

- [ ] **A personhood-verification adapter contract (`PersonhoodVerifier`)** — based on
  `docs/IDENTITY-VERIFICATION.md`: a thin contract that accepts a proof from one of the
  allowed proof-of-personhood methods and calls `Reputation.mint` only when
  `verified ∧ unique (nullifier unused)`; the method allow-list is under `Timelock`.
  Grounds "uniqueness ≠ power" in code (proposed session 44).
- [x] **Identity-verification terms in `GLOSSARY.md`** (+RU) — add in plain words:
  "proof-of-personhood", "zero-knowledge / proof without disclosure", "nullifier",
  "liveness", "vouching (web-of-trust)" — each linking to `IDENTITY-VERIFICATION.md`
  (proposed session 44). → Done (session 53), a new group "Identity verification — is
  there a live person behind the account" in [`GLOSSARY.md`](GLOSSARY.md) (+RU): 6 terms
  in plain words (protection from fakes/Sybil, proof-of-personhood, liveness,
  zero-knowledge, nullifier, vouching), each linking to
  [`IDENTITY-VERIFICATION.md`](IDENTITY-VERIFICATION.md). `PTD-0050`.
- [x] **Cross-links `IDENTITY-VERIFICATION.md` ↔ `GLOSSARY.md`** — inside the
  identity-verification document itself, put a link to the glossary entry at the first
  mention of each technical word (and the glossary already links back to the document) —
  so an unfamiliar term is one click away in both directions (proposed session 53; a
  special case of "glossary link in doc headers"). → Done (session 54): six terms (Sybil
  attack, proof-of-personhood, liveness, web-of-trust, zero-knowledge, nullifier) at
  first mention link to [`GLOSSARY.md`](GLOSSARY.md) + a glossary pointer in the header;
  RU↔EN, `PTD-0051`.
- [ ] **Documentation agent: a soft "no dead glossary entries" check** — the
  inverse of `glossary-coverage`: warn if an entry exists in `GLOSSARY.md` but the
  term itself appears nowhere in the normative documents (the glossary has grown
  stale extras). Also soft, non-blocking (proposed session 61, extends `PTD-0058`).
- [x] **GitHub label catalog `.github/labels.yml`** — a single set of labels
  (`bug`, `idea`, `governance`, `safety`, …) referenced by the issue forms, so
  label colors/descriptions are reproducible and not set up by hand (proposed session 37).
  **Done (session 76):** `.github/labels.yml` — a single catalogue (RU/EN
  descriptions, hex colors): the 4 form labels (`bug`/`idea`/`governance`/`safety`)
  + `documentation`/`question` + `area:*` layers + statuses (`good first issue`/
  `help wanted`/`blocked`/`duplicate`/`wontfix`); format compatible with common
  label-sync tools; applying it to the real repo is the operator's call (an outward
  action). The structure guard's tenth check `issue-form-labels-defined` (hard) goes
  red if a form references a label missing from the catalogue; `test_structure_guard.py`
  98/98. `PTD-0073`.
- [x] **Optional label sync** — a ready-to-use workflow/instruction that brings the
  real repo's labels in line with `.github/labels.yml` (e.g. `EndBug/label-sync`).
  Enabling and applying it to the real repo is the operator's call (an outward action);
  the agent prepares it "ready to push" (session 76).
  **Done (session 77):** `.github/workflows/labels.yml` — a label-sync workflow using
  `EndBug/label-sync@v2` over the `.github/labels.yml` config. Trigger is manual ONLY
  (`workflow_dispatch`, no push) — the outward action stays with the operator; it
  previews by default (`dry_run=true`, changes nothing), deleting non-catalog labels is
  off (`delete_others=false`). The catalog's "how to apply" note now links the workflow.
  Closes the catalog→guard→sync loop. `PTD-0074`.
- [ ] **Guard: label catalog has no duplicates and valid hex colors** — a soft check
  of `.github/labels.yml`: label names are unique, `color` is exactly 6 hex chars
  without `#`, each label has a description (proposed session 76, extends `issue-form-labels-defined`).
- [ ] **Guard: the label-sync workflow stays manual** — a soft check that
  `.github/workflows/labels.yml` has a `workflow_dispatch` trigger and NO `push`
  trigger (the outward action must stay with the operator; the rail must not "drift"
  on future edits). Proposed session 77, extends `PTD-0074`.
- [x] **Glossary link in the header of normative docs** — add a link to
  [`GLOSSARY.md`](GLOSSARY.md) to each doc's header, so an unfamiliar term is one
  click away from any document (proposed in session 36). → Done (session 57): a
  pointer "Unfamiliar technical words … are explained in plain language in the
  [glossary](GLOSSARY.md) — the "…" group" with the exact group name was added to the
  headers of six normative docs (GOVERNANCE / ANTI-ABUSE / REWARDS-MODEL /
  PROOF-OF-CONTRIBUTION / ESCROW-TARGETED-DISBURSEMENT / PRIORITIES, RU + EN);
  `PTD-0054`. The link to the glossary is now two-way for all normative docs.
- [x] **Documentation agent: a soft "term is defined" check** — a light dictionary
  linter that, for a list of key terms (DAO/escrow/multisig/…), checks the project
  has an entry in `GLOSSARY.md`; non-blocking, just a warning, so the glossary does
  not fall behind the documents (proposed in session 36). **Done (session 61):** the
  `glossary-coverage` check in `documentation_agent.py` (`soft=True`, a 26-term
  `KEY_TERMS` list, RU+EN; the verdict/`passed`/`total` count only the blocking
  checks, a `warnings` field was added); 2 new test scenarios (23/23); the check
  table in the agent README (+EN). `PTD-0058`.
- [x] **SECURITY.md (+EN)** — canonical security policy file (GitHub recognizes it
  and shows a "Report a vulnerability" button): where and how to report a rails/contract
  flaw, what's in scope (testnet only), what we do NOT promise (no real-money bounty
  before audit), private channel = the same `security@` from [`EMAIL-SETUP.md`](EMAIL-SETUP.md).
  Complements CODE_OF_CONDUCT (breaking the rails = breaking conduct) and the Guardian
  agent (proposed session 35). **Done (session 39):** `SECURITY.md` (+EN), cross-links
  from CODE_OF_CONDUCT/README/REPO-STRUCTURE, safe harbor, coordinated disclosure,
  `PTD-0036`.
- [ ] **Distribution contract per `REWARDS-MODEL.md`** — encode the §5.1 parameters
  (`B_min`/`B_target`/`ρ_min`/`ρ_max`/`w_work`/`rep_cap`/`k`) into a contract over
  [`Treasury.sol`](../../contracts/contracts/Treasury.sol)/[`Disbursement.sol`](../../contracts/contracts/Disbursement.sol):
  `ρ_cap` and `referral=forbidden` immutable constants, the rest `onlyTimelock` (via
  vote); invariant tests "aid always ≥ 1−ρ_cap", "reputation weight does not break the
  band ceiling" (Stage 5, continuation of rewards-model; session 41).
- [ ] **Fairness agent: a `rewards-model` check** — extend
  [`fairness_agent.py`](../../ai-agents/fairness_agent.py): an accrual of any stream
  (H/W/V) is recomputable by [`REWARDS-MODEL.md`](REWARDS-MODEL.md) and falls within the
  §2–§3 corridors (aid share ≥ 1−ρ_cap; no referral stream; reputation is a multiplier,
  not a right to a payout). Closes the model onto a machine check (session 41).
- [ ] **A `reward` registry record template/schema** (W/V) — by analogy with
  `disbursement`: a verifiable record of a work/volunteering reward (proof artifact, ≥2
  reviewers, amount within the band) so that every W/V accrual is in the public registry
  and recomputable (session 41).
- [ ] **An `appeal` registry record template/schema** + tie-in to the Mediator: when a
  dispute reaches `resolved`, the outcome is fixed as an `appeal` record in
  `governance/registry/`; the agent checks that a finished dispute has such a record
  (close the appeal process onto the public registry, like `disbursement` ↔ escrow;
  proposed session 31).
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
- [x] A reusable lightweight Solidity-invariant scanner module: comment stripping
  + brace-balanced function-body extraction were duplicated across the Reputation and
  Housing agents — extracted into a shared
  [`ai-agents/solidity_scan.py`](../../ai-agents/solidity_scan.py) (useful for future
  contract agents Governance/Audit; sessions 27/31). → Done (session 40), `PTD-0037`:
  `strip_solidity_comments`/`has_function`/`function_signature`/`function_body` in one
  module, both agents import it; test invariant
  [`test_solidity_scan.py`](../../ai-agents/test_solidity_scan.py) (14/14), wired into
  `run_all` (tests 9/9). Agent behavior unchanged (Reputation 5/5, Housing 8/8).
- [x] **Structure-guard: check that `run_all` covers everyone** — extend
  [`structure_guard.py`](../../ai-agents/structure_guard.py) with a check that the
  `TESTS` list in `run_all.py` actually includes every existing `test_*.py` (and that
  each `AGENTS` key has an agent) — so a new agent/test cannot bypass the shared CI run
  (follow-up to the guard, session 51).
  → Done (session 52) via the `run-all-covers-all` check of
  [`structure_guard.py`](../../ai-agents/structure_guard.py), `PTD-0049`. Also closed a
  real gap: `test_run_all.py` was added to `TESTS` (the meta-agent wasn't running its
  own test invariant; tests 10→11).
- [x] **Structure-guard: CI actually calls `run_all`** — add a check that
  `.github/workflows/ai-agents.yml` really runs `run_all.py --with-tests` (not separate
  agent commands that bypass it) — so coverage can't be bypassed at the CI-workflow
  level either, not just the `AGENTS`/`TESTS` lists (follow-up to `run-all-covers-all`,
  session 52).
  → Done (session 60) via the fifth `ci-calls-run-all` check of
  [`structure_guard.py`](../../ai-agents/structure_guard.py): it reads the workflow file
  itself and goes red if it does not call `run_all.py` with `--with-tests` (agents
  bypassed, no test invariants, or no workflow at all). `test_structure_guard.py` 34/34,
  guard green 5/5, `PTD-0057`.
- [x] **Structure-guard: workflow trigger paths include `ai-agents/**`** — check that
  the `on.push.paths` (and `pull_request.paths`) block in
  `.github/workflows/ai-agents.yml` actually contains `ai-agents/**`, otherwise an agent
  change won't trigger CI at all and coverage is bypassed even earlier — at the trigger
  level, not the command (follow-up to `ci-calls-run-all`, session 60).
  → Done (session 63) via the sixth `trigger-paths-include-agents` check of
  [`structure_guard.py`](../../ai-agents/structure_guard.py) (a lightweight
  indentation-based YAML parser, no dependencies): it requires `ai-agents/**` in both
  triggers and goes red if a path or block is missing. `test_structure_guard.py` 43/43,
  guard green 6/6, `PTD-0060`. Closed coverage-bypass protection at every level (lists →
  CI call → trigger firing). Also caught up the agent README (RU/EN): the lagging
  `ci-calls-run-all` row + the new row.
- [x] **Structure-guard: workflow `ai-agents.yml` also calls `test_run_all.py`** — add a
  check that a separate workflow step runs the meta-agent's test invariant
  `test_run_all.py` (not only `run_all.py --with-tests`) — it proves the "red → red"
  reduction itself works; right now this relies on workflow discipline (proposed in
  session 63; follow-up to `trigger-paths-include-agents`).
  → Done (session 64) via the seventh `ci-runs-test-run-all` check of
  [`structure_guard.py`](../../ai-agents/structure_guard.py): reads the workflow and turns
  red if it does not run `test_run_all.py` as a separate step. `test_structure_guard.py`
  50/50, guard green 7/7, `PTD-0061`. Completed coverage-bypass protection all the way up
  (lists → CI call → trigger firing → running the reduction's own test invariant).
- [x] **Structure-guard: workflow checked for CI-step completeness** — generalize
  `ci-calls-run-all`/`ci-runs-test-run-all`: instead of one check per command, keep a
  single list of "required workflow commands" in the guard and turn red if any is missing
  — so a newly required CI step cannot be forgotten, without multiplying near-identical
  checks (proposed in session 64).
  → Done (session 65) via the `ci-has-required-steps` check of
  [`structure_guard.py`](../../ai-agents/structure_guard.py): a single declarative list
  `REQUIRED_WORKFLOW_COMMANDS` (currently `run_all.py --with-tests` and `test_run_all.py`),
  red if any command is missing; the two former twin checks were removed, check count 7→6.
  `test_structure_guard.py` 49/49, guard green 6/6, `PTD-0062`.
- [x] **Structure-guard: a dedicated workflow step per required CI command** — follow-up
  to `ci-has-required-steps`: check not just that a command appears anywhere in the file,
  but that it has its own `- run:` step (not hidden in a comment or sharing a line) — so
  one required command's failure cannot mask another (proposed in session 65).
  → Done (session 66) via the `ci-required-cmd-own-step` check of
  [`structure_guard.py`](../../ai-agents/structure_guard.py): the `_workflow_run_steps`
  helper reads the `run:` step bodies (inline and block), and the check requires each
  command in `REQUIRED_WORKFLOW_COMMANDS` to run in at least one step and not share a step
  with another. Catches a command left only in a comment (the old check still "saw" it) and
  two commands in one `run:`. Check count 6→7. `test_structure_guard.py` 59/59, guard green
  7/7, `PTD-0063`.
- [x] **Structure-guard: every `run:` step has a human-readable `name:`** — soft follow-up
  to `ci-required-cmd-own-step`: warn (do not block) if a required CI step runs without a
  `- name:` — so a failure reads humanly in the GitHub Actions log ("Run all agents") rather
  than as a bare command. Builds on the existing `_workflow_run_steps`/step parser
  (proposed in session 66).
  → Done (session 67), the guard's first SOFT check `ci-step-has-name`
  (`severity=soft`: `status=warn`, does not fail the verdict). Introduced shared soft-check
  infrastructure (`_workflow_run_steps_named`, a `severity` field, a `warnings` counter).
  Checks 7→8 (1 soft). `test_structure_guard.py` 72/72, guard green 8/8 with no warnings,
  `PTD-0064`.
- [x] **Structure-guard: soft check `ci-step-name-unique`** — follow-up to
  `ci-step-has-name` (PTD-0064): warn (do not block) if two CI `run:` steps share the same
  `- name:` — then they are indistinguishable in the GitHub Actions log and a failure reads
  ambiguously. Builds on the same `_workflow_run_steps_named` (proposed in session 67).
  → Done (session 68), the guard's second SOFT check `ci-step-name-unique`
  (`severity=soft`: `status=warn`, does not fail the verdict): collects the names of all
  `run:` steps, warns about repeated ones, skips unnamed steps. Checks 8→9 (2 soft).
  `test_structure_guard.py` 80/80, guard green 9/9 with no warnings, `PTD-0065`.
- [x] **Structure-guard: soft check "a step has both a `name:` and a `run:` body"** —
  follow-up to `ci-step-name-unique`: warn if the workflow has a list item with `- name:`
  but no `run:`/`uses:` (an empty step — a common indentation typo), so the CI step map
  stays honest (proposed in session 68). → Done (session 69), the guard's third SOFT check
  `ci-step-has-body` (`severity=soft`: `status=warn`, does not fail the verdict): the new
  helper `_workflow_step_items` collects each list item's keys at the "step column"; a step
  with `name` but no `run`/`uses` warns as "empty step". Check count 9→10 (3 soft).
  `test_structure_guard.py` 89/89 (empty step → warn with green verdict and exit 0; `uses:`
  counts as a body; `paths:` items are not confused with steps), guard green 10/10 with no
  warnings, `PTD-0066`.
- [ ] **Structure-guard: soft check "every step has a `name:`" for ALL steps, not just
  required commands** — `ci-step-has-name` currently inspects only the steps of required
  commands (`REQUIRED_WORKFLOW_COMMANDS`); `uses:` steps (checkout, setup-python) without a
  name are not warned. Extend the soft name check to all list steps (on top of
  `_workflow_step_items`) so the whole CI map reads in plain words (proposed in session 69).
- [x] **`run_all`/meta-agent surfaces the guard's soft warnings** — the guard's `warnings`
  count is currently printed only in its own report; add it so the shared
  `run_all --with-tests` run also prints the total number of soft warnings (without failing
  the build) — so the operator summary does not lose them (proposed in session 67).
  → Done (session 70): the meta-agent [`run_all.py`](../../ai-agents/run_all.py) now runs
  the structure guard too (new `run_guard()`, `GUARD` constant) and shows it as a separate
  line in the summary — `guard 10/10, guard soft warnings: N` (and in `--json`: keys
  `guard`/`guard_warnings`). The guard's hard "red" fails the overall verdict alongside the
  agents; soft warnings are only surfaced as a count and do not fail the build; an absent
  guard is not applicable. Test invariant [`test_run_all.py`](../../ai-agents/test_run_all.py)
  13/13→21/21 (fake guard: warnings do not fail, hard-red fails, green+exit≠0 anomaly is
  red, absent guard not applicable). `PTD-0067`.
- [x] **`run_all` surfaces not only the count but the guard's individual soft warnings** —
  the summary currently prints the total; add a per-line list under the guard row (which
  check, which step) so the operator summary explains a warning without a separate
  `structure_guard.py` run (follow-up to `PTD-0067`, session 70). → Done (session 71): the
  helper `guard_warning_lines()` in [`run_all.py`](../../ai-agents/run_all.py) collects the
  `warn`-status checks from `guard.checks` and their `violations` (item/problem) into lines
  "[check] step: problem"; the human-readable guard row prints them as `⚠ [check] …` when
  `guard_warnings>0` (falling back to the guard pointer if no detail), and `--json` gains a
  `guard_warning_lines` key. `test_run_all.py` 21→28, `PTD-0068`.
- [x] **Machine-readable project "status light" from `run_all --json`** — persist the last
  `run_all` verdict (including `guard_warnings` and `guard_warning_lines`) to an artifact file
  under `governance/`, as the basis for a future public status indicator with no external
  services (related to the long-standing "badge in governance/" idea; now that the warning
  lines are machine-readable, the artifact can include them; sessions 70–71).
  → Done (session 72): `--status-out PATH` flag + `build_status` helper, deterministic artifact
  [`governance/status/run_all_status.json`](../../governance/status/) (+ bilingual README),
  `test_run_all.py` 28→39, `PTD-0069`. Subsumes the long-standing "badge in governance/" idea
  (below) — this item closes it too.
- [x] **Public status light on the site/page from the artifact** — a `web/` page (or section)
  reads [`governance/status/run_all_status.json`](../../governance/status/) and renders green/red
  + agent/test scores and soft warnings for a human, with no external services/badges/trackers
  (continuation of `PTD-0069`, session 72).
  → Done (session 73): a "live status light" section on the Transparency page
  ([`web/transparency.html`](../../web/transparency.html) +EN) — a `.statuslight` widget reads
  `./status.json` same-origin and renders green/red + agent/test/guard scores and soft-warning
  lines; shared bilingual [`web/assets/status.js`](../../web/assets/status.js) (language from
  `<html lang>`, DOM via `textContent`, `<noscript>` fallback). Single source of truth stays in
  `governance/status/`: the Pages deploy ([`pages.yml`](../../.github/workflows/pages.yml)) copies
  the artifact into `web/status.json` on the fly (not committed, in `.gitignore`) and redeploys
  the site when the status changes. The "zero external requests" policy is preserved. `PTD-0070`.
- [x] **Compact status-light chip in the header/footer of the other site pages** — a tiny
  indicator (green/red dot + "checks are fine") that the same `assets/status.js` reads from
  `./status.json` and that links to the Transparency section for details, so the status is
  visible from any page, not only the Transparency page. → Done (session 74), `PTD-0071`.
- [x] **Status-light chip in the topbar too, not only the footer** — add the same compact
  `#statusbadge` to the header `.nav-tools` of the landing pages (next to the language/theme
  toggles), so the status is visible immediately without scrolling to the footer; on narrow
  screens hide it gracefully together with the navigation (continuation of `PTD-0071`, session 74).
  → Done (session 75), `PTD-0072`: compact `#statusbadge-top`
  (`statusbadge statusbadge--compact`) in the header of `index.html` (+EN); the shared
  [`status.js`](../../web/assets/status.js) now renders all `.statusbadge` chips
  (`querySelectorAll`), a single request serves both header and footer; on narrow screens
  (`<=640px`) the header chip is hidden (status stays visible in the footer).
- [ ] **Status-light chip in the header/footer of `docs`-site pages outside `web/`** — the
  light currently lives only on the landing pages and the Transparency page (`web/`); extend the
  same compact chip to other public HTML pages if/when they appear, so the status is consistent
  across the whole site (continuation of `PTD-0072`, session 75).
- [ ] **Guard/CI: status artifact not stale vs the current verdict** — a soft check that the
  committed `governance/status/run_all_status.json` matches a fresh `run_all --status-out`
  (otherwise the in-repo light is stale); or a CI step regenerates the artifact (determinism
  allows it) — `PTD-0069`, session 72.
- [ ] **Move the Governance agent onto `solidity_scan`** — it currently parses only
  JSON configs; when it needs to cross-check `Governor.sol`/`Timelock.sol` (vote weight
  from `Reputation.votingUnits`, not balance), reuse the shared
  [`solidity_scan.py`](../../ai-agents/solidity_scan.py) rather than spawn a fourth
  parsing copy (follow-up to the refactor, session 40).
- [x] **CI check "no `.sol` parsing copies outside `solidity_scan`"** — a tiny linter
  that fails if an `ai-agents/*_agent.py` reintroduces a local `strip_solidity_comments`/
  `function_body` definition (instead of importing the shared module) — so the removed
  duplication cannot quietly return (akin to the "invariant standard", session 40).
  → Done (session 51) via the `sol-parsing-centralized` check of the guard
  [`structure_guard.py`](../../ai-agents/structure_guard.py), `PTD-0048`.
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
- [x] Run-All: a machine-readable status badge in `governance/` (the last
  `run_all --json` verdict saved to an artifact file) — a basis for a future public
  "status traffic light" with no external services (session 32).
  → Done (session 72) by the same `--status-out` flag and artifact
  [`governance/status/run_all_status.json`](../../governance/status/), `PTD-0069`.
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
- [x] **"Every agent has an invariant" as an explicit CI check:** a mini-script that
  fails if a `*_agent.py` appears in `ai-agents/` without a paired `test_*.py` (and vice
  versa) — so the Stage-6 quality gap (as Audit had) can never reappear unnoticed
  (proposed session 33; akin to "agent self-test in CI").
  → Done (session 51) via the `agents-have-invariants` + `no-orphan-tests` checks of the
  guard [`structure_guard.py`](../../ai-agents/structure_guard.py), `PTD-0048`.
- [x] **Catch up the EN mirror `docs/en/ROADMAP.md`** — the RU roadmap had run ahead (the
  "Done" section and the idea bank held items up to `PTD-0051`, while EN had drifted: P0
  Stage 6 still showed Mediator open and the P3 bank lacked the newer
  identity/glossary/meta items). The Documentation agent stayed green (the pair, the
  switcher and the links were intact), but the content was out of sync — a violation of
  the "RU↔EN in sync" rule. Done in one careful pass (discovered session 54).
  → Done (session 55): Stage 6 marked complete (8/8) with the Mediator module filled in;
  the P3 bank gained the identity/glossary/meta items; the "Done" section gained
  `PTD-0050`/`PTD-0051`; `PTD-0052`.
- [x] **Glossary link in the header of ALL normative docs** (generalization) — add the
  same short pointer "unfamiliar word → [`GLOSSARY.md`](GLOSSARY.md)" to the header of
  the remaining public docs (`GOVERNANCE`, `ANTI-ABUSE`, `REWARDS-MODEL`,
  `PROOF-OF-CONTRIBUTION`, `ESCROW`, `PRIORITIES`), so the glossary is one click away
  from any document (proposed session 54). → Done (session 57), `PTD-0054` (the same
  work that closed "Glossary link in the header of normative docs" above): the pointer
  with the exact group name was added to all six docs (RU + EN).
- [x] **Glossary pointer in the header of the remaining public docs** — extend the same
  navigation pointer to the non-technical but still term-bearing docs (`SUPPORT-MODEL`,
  `ACCOUNTABILITY`, `SECURITY`, `PRINCIPLES`, `CONSTITUTION`), so the "term one click
  from its explanation" rule holds uniformly across the whole corpus (proposed session
  57; continuation of the P3 "glossary link").
  → Done (session 59), `PTD-0056`: a pointer with the exact glossary group added to all
  five docs (RU + EN). The plain-language rule now holds uniformly across the whole
  corpus of public documents.

- [ ] **Documentation agent: soft check "header pointer leads to the glossary"** — a
  light read-only check that public docs containing known technical words carry a header
  pointer to `GLOSSARY.md` with a group name matching a real heading in the glossary;
  warns (does not block), so the navigation link does not lag behind new docs (proposed
  session 59; akin to the "jargon next to its explanation" idea).

---

## Done

- **PTD-0072 (session 75):** P2 (transparency) — **status-light chip in the topbar too, not only
  the footer.** The header of the landing pages ([`web/index.html`](../../web/index.html) + EN),
  inside `.nav-tools` next to the language/theme toggles, gained a compact `#statusbadge-top` chip
  (`statusbadge statusbadge--compact`) — the status is visible at once on load, without scrolling
  to the footer. The shared [`web/assets/status.js`](../../web/assets/status.js) was refactored to
  render ALL `.statusbadge` chips on the page (`querySelectorAll` instead of a single
  `getElementById`); one `./status.json` request serves both the header and footer chips. On narrow
  screens (`<=640px`) the header chip is hidden together with the navigation — the status stays
  visible in the footer there. The "zero third-party requests" policy is preserved. Continuation of `PTD-0071`.
- **PTD-0071 (session 74):** P2 (transparency) — **compact status-light chip on the other site
  pages.** The footer of the landing pages ([`web/index.html`](../../web/index.html) + EN) gained
  a compact `#statusbadge` chip: a small dot + word ("checks are green" / "out of sync") that reads
  `./status.json` same-origin and links to the Transparency section (`#livestatus`) for details —
  so the status is visible from any page, not only the Transparency page. The shared
  [`web/assets/status.js`](../../web/assets/status.js) was refactored: a single request renders both
  the full `#statuslight` widget and the compact `#statusbadge` chip (whichever is on the page).
  The `.statusbadge` style uses theme tokens, no external dependencies. The "zero external requests"
  policy is preserved. Continuation of `PTD-0070`.
- **PTD-0070 (session 73):** P2 (transparency) — **public "live status light" of the project
  on the site.** The Transparency page ([`web/transparency.html`](../../web/transparency.html)
  + EN) gained a `#livestatus` section with a `.statuslight` widget: a shared bilingual
  [`web/assets/status.js`](../../web/assets/status.js) reads `./status.json` same-origin and
  renders green/red + agent/test/guard scores and soft-warning lines for a human (language from
  `<html lang>`, DOM via `textContent`, `<noscript>` fallback to the artifact and CI). It makes
  the work of sessions 70–72 visible to a human. Single source of truth stays in
  `governance/status/`: the Pages deploy ([`pages.yml`](../../.github/workflows/pages.yml)) copies
  the artifact into `web/status.json` on the fly (not committed, added to `.gitignore`) and
  redeploys the site when the status changes. The "zero external requests/badges/trackers" policy
  is preserved — the request is same-origin only. Serves art. 3 (clarity) and art. 9 (AI is a
  signal, not authority). verify=green (71 records), run_all 8/8 tests 11/11 guard 10/10,
  documentation 3/3, `node --check status.js` OK.
- **PTD-0069 (session 72):** P3 (Stage 6 quality) — **machine-readable project "status light"
  from `run_all`.** Folds the work accumulated over sessions 70–71 (`guard_warnings` and
  `guard_warning_lines` in `--json`) into a visible operator/public artifact rather than yet
  another invisible guard micro-check. The `--status-out PATH` flag + `build_status(report)`
  helper: a compact **deterministic** summary (overall verdict, agent/test scores, guard
  summary with count and lines of soft warnings, one line per agent). No wall-clock time → in
  git it only goes "dirty" when the verdict/score changes; `schema_version` versions the format;
  written on any verdict (incl. `red`). Canonical artifact
  [`governance/status/run_all_status.json`](../../governance/status/) + bilingual README.
  Closes both related ideas (this one and the long-standing "badge in `governance/`", session 32).
  `test_run_all.py` 28→39 (11 new checks: not written without the flag, written and valid, schema
  versioned, scores folded, determinism — re-run is byte-identical, a red run writes `verdict=red`,
  `build_status` tolerates `guard=None`). verify=green (70 records), run_all 8/8 tests 11/11
  guard 10/10, documentation 3/3.
- **PTD-0068 (session 71):** P3 (Stage 6 quality) — **`run_all` shows not only the COUNT but
  the guard's individual soft-warning LINES.** Follow-up to PTD-0067 (session 70): the new
  helper `guard_warning_lines(guard_result)` collects the `warn`-status checks (severity=soft)
  from `guard.checks` and their `violations` (item/problem) into "[check] step: problem" lines.
  The human-readable guard row prints them as `⚠ [check] …` when `guard_warnings>0` instead of
  the old "details — `python3 ai-agents/structure_guard.py`" pointer (kept as a fallback when
  `warnings>0` but `checks` carry no detail). `--json` gains a `guard_warning_lines` key — a
  basis for a future machine-readable status light. The guard's hard "red" still fails the
  overall verdict, soft warnings do not. `test_run_all.py` 21→28. verify green (69 records),
  IPFS OK (19), run_all agents 8/8 tests 11/11 guard 10/10.
- **PTD-0066 (session 69):** P3 (Stage 6 quality) — **structure-guard: tenth (third SOFT)
  `ci-step-has-body` check (a step with `- name:` has a `run:`/`uses:` body — it is not
  empty).** Follow-up to `ci-step-name-unique` (PTD-0065) toward an honest CI step map: if a
  list item carries `- name:` but NEITHER `run:` NOR `uses:`, it is almost always an
  indentation typo — the step body "fell out" of it, so the step does nothing while still
  looking real in the GitHub Actions UI. The new helper `_workflow_step_items` collects each
  list item's keys at the "step column" (`-` indent + 2); keyless `paths:` items do not
  interfere. Does not break coverage (an actual missing command is caught by the hard checks)
  → only **warns** (`severity=soft`, `status=warn`), verdict stays green. Check count 9→10
  (3 soft). `test_structure_guard.py` 80→89 (3 new blocks: empty step → warn with green
  verdict and exit 0; `uses:` counts as a body; `paths:` items not confused with steps),
  guard 10/10 with no warnings, run_all 8/8 + tests 11/11, IPFS verify=OK (19), registry 67.
  Agent README (RU/EN): new table row marked "soft".
- **PTD-0065 (session 68):** P3 (Stage 6 quality) — **structure-guard: ninth (second SOFT)
  `ci-step-name-unique` check (two CI `run:` steps do not share the same `- name:`).**
  Follow-up to `ci-step-has-name` (PTD-0064): a step already has a name, but if it repeats,
  a failed step reads ambiguously in the GitHub Actions log ("which of the two same-named
  ones?"). The check collects the names of all `run:` steps (the ready helper
  `_workflow_run_steps_named`) and warns about repeated ones; it skips unnamed steps (those
  are `ci-step-has-name`'s concern). Does not break coverage → only **warns**
  (`severity=soft`, `status=warn`), the verdict stays green. Checks 8→9 (2 soft).
  `test_structure_guard.py` 72→80 (3 new scenarios: two steps with one name → warn with a
  green verdict and exit 0; unnamed steps do not turn it red; distinct names in separate
  blocks → green), guard 9/9 with no warnings, run_all 8/8 + tests 11/11, IPFS verify=OK (19),
  registry 66. Agent README (RU/EN): a new table row marked "soft".
- **PTD-0064 (session 67):** P3 (Stage 6 quality) — **structure-guard: eighth (first SOFT)
  `ci-step-has-name` check (a `run:` step of a required CI command has a human `- name:`).**
  Follow-up to `ci-required-cmd-own-step` (PTD-0063) toward readability: without a name a
  failed step is shown in the GitHub Actions log as a bare command
  (`python3 ai-agents/run_all.py --with-tests`) rather than humanly ("Run all agents"). It
  does not break coverage → the check only **warns** (`severity=soft`, `status=warn`) and the
  verdict stays green. Introduced shared soft-check infrastructure: a `_workflow_run_steps_named`
  helper (`run:` step bodies with their names; the old `_workflow_run_steps` became a wrapper),
  a `severity` field in `CHECKS`, a `warnings` counter in the report. Check count 7→8 (1 soft).
  `test_structure_guard.py` 59→72 (3 new scenarios: both steps unnamed → warn with a green
  verdict; mixed; named block steps), guard 8/8 with no warnings, run_all 8/8 + tests 11/11,
  IPFS verify=OK (19), registry 65. Agent README (RU/EN): a new table row marked "soft".
- **PTD-0063 (session 66):** P3 (Stage 6 quality) — **structure-guard: seventh
  `ci-required-cmd-own-step` check (a dedicated `run:` step per required CI command).**
  Follow-up to `ci-has-required-steps` (PTD-0062): the old check confirmed a command exists
  *anywhere* in the file — including comments and step names, and two commands could share a
  `run:` step. The new check reads the `run:` step bodies themselves (new `_workflow_run_steps`
  helper parses inline and block `run:`) and requires each command in `REQUIRED_WORKFLOW_COMMANDS`
  to (a) actually run in at least one step and (b) not share a step with another — otherwise a
  failure of one masks the other (`&&` short-circuits; a comment never runs). Guard check count
  6→7. `test_structure_guard.py` 49→59 (4 new scenarios incl. command-only-in-comment and
  two-commands-one-step), guard 7/7, run_all 8/8 + tests 11/11, IPFS verify=OK (19), registry 64.
  Agent README (RU/EN): new table row.
- **PTD-0062 (session 65):** P3 (Stage 6 quality) — **structure-guard: `ci-has-required-steps`
  check (single list of required CI commands).** Generalized the two former twin checks
  `ci-calls-run-all` (PTD-0057) and `ci-runs-test-run-all` (PTD-0061) into one driven by a
  declarative list `REQUIRED_WORKFLOW_COMMANDS` (key, regex, "why"): the guard turns red if
  the workflow drops any required command (currently `run_all.py --with-tests` and
  `test_run_all.py`). A newly required CI step is now one line in the list, with no
  near-identical check code multiplied. Guard check count 7→6 (consolidation).
  `test_structure_guard.py` 49/49 (scenarios migrated; added that a violation names exactly
  the missing command), guard 6/6, run_all 8/8 + tests 11/11, IPFS verify=OK (19),
  registry 63. Agent README (RU/EN): table row replaced, counter 50/50 → 49/49.
- **PTD-0061 (session 64):** P3 (Stage 6 quality) — **structure-guard: seventh
  `ci-runs-test-run-all` check.** The CI workflow must run the meta-agent's own test
  invariant `test_run_all.py` as a separate step, not only `run_all.py --with-tests`:
  `run_all` itself *reduces* per-agent "red" into one verdict, and that reduction could
  silently break (report "green" with a red agent) — only `test_run_all.py` proves it
  works. Without a dedicated step nobody would catch a broken reduction. Completed
  coverage-bypass protection all the way up: `AGENTS`/`TESTS` lists (PTD-0049) → `run_all`
  call in CI (PTD-0057) → trigger firing (PTD-0060) → running the reduction's test
  invariant (PTD-0061). `test_structure_guard.py` 50/50, guard 7/7, run_all 8/8 + tests
  11/11, IPFS verify=OK (19), registry 62. Agent README (RU/EN): new table row, counter
  43/43 → 50/50.

- **PTD-0060 (session 63):** P3 (Stage 6 quality) — **structure-guard: sixth
  `trigger-paths-include-agents` check.** The CI workflow trigger blocks
  `on.push.paths` and `on.pull_request.paths` must contain `ai-agents/**` — otherwise an
  agent edit won't start CI and coverage is bypassed even earlier, at the trigger level
  rather than the command (`ci-calls-run-all` guards that the workflow *calls* the
  meta-agent, but the call is useless if the workflow does not *fire*). A lightweight
  indentation-based YAML parser, no dependencies. Closed coverage-bypass protection at
  every level: `AGENTS`/`TESTS` lists (PTD-0049) → `run_all` call in CI (PTD-0057) →
  trigger firing (PTD-0060). `test_structure_guard.py` 43/43, guard 6/6, run_all 8/8 +
  tests 11/11, IPFS verify=OK (19), registry 61. Also caught up the agent README (RU/EN):
  the lagging `ci-calls-run-all` row + the new row, counter 25/25 → 43/43.

- **PTD-0056 (session 59):** P3 (plain language) — **glossary pointer in the header of
  the remaining public docs.** A line "Unfamiliar technical words … are explained in
  plain language in the [`GLOSSARY.md`](GLOSSARY.md) — the "…" group" with the exact
  group name (Money and aid / Transparency and verifiability / Safety and technology /
  Basics) was added to the headers of `SUPPORT-MODEL` / `ACCOUNTABILITY` / `SECURITY` /
  `PRINCIPLES` / `CONSTITUTION` (RU + EN). For `SECURITY.md` (at the repo root) the link
  points to `docs/GLOSSARY.md` / `docs/en/GLOSSARY.md`. Completes the generalization of
  PTD-0054: the "term one click from its explanation" rule now holds uniformly across the
  whole corpus of public documents. The meaning of the docs is unchanged. Documentation
  3/3, run_all 8/8 + tests 11/11, IPFS verify=OK (19), registry 57.

- **PTD-0054 (session 57):** P3 (plain language) — **glossary pointer in the header of
  six normative docs.** A line "Unfamiliar technical words … are explained in plain
  language in the [`GLOSSARY.md`](GLOSSARY.md) — the "…" group" with the exact group
  name (Governance and voting / Safety and technology / Money and aid) was added to the
  headers of `GOVERNANCE` / `ANTI-ABUSE` / `REWARDS-MODEL` / `PROOF-OF-CONTRIBUTION` /
  `ESCROW-TARGETED-DISBURSEMENT` / `PRIORITIES` (RU + EN). An unfamiliar term is now one
  click from its plain-language explanation; the link to the glossary is two-way. The
  meaning of the docs is unchanged. Documentation 3/3, run_all 8/8 + tests 11/11, IPFS
  verify=OK (19), registry 55. Closed two P3 bank items (base + generalization).

- **PTD-0053 (session 56):** INBOX #22 (operator request) — **"Future-proofing
  (including against quantum computers)" in [`SECURITY.en.md`](../../SECURITY.en.md)
  (+ RU).** Plain language (rule `PTD-0040`) + a "for developers" technical section.
  Stance: do NOT bring PQC into the smart contracts now, but lay the foundation —
  **crypto-agility (swappable algorithms)**, only facts/fingerprints on-chain (defuses
  "harvest-now-decrypt-later"), keys held by the person, readiness for NIST PQC
  (ML-KEM/Kyber, ML-DSA/Dilithium, SPHINCS+), follow Ethereum/Polygon. A dedicated
  **"Protecting the fund's money (treasury)"** subsection per the operator's
  clarification: 3-of-5 multisig, treasury "migration" to a quantum-resistant wallet
  (the main hook), rotating/revoking guardian keys without losing funds, a cold reserve;
  honest about priority — protecting the money today = audit + multisig + key hygiene,
  quantum resistance is a "future" layer with no launch delay. Recorded in the registry
  (54 records, verify=green), IPFS verify=OK, Documentation 3/3, run_all 8/8 + tests
  11/11. TESTNET-ONLY.

- **PTD-0052 (session 55):** P3 (plain language / bilingual sync) — **caught up the EN
  mirror [`docs/en/ROADMAP.md`](ROADMAP.md)**. The RU roadmap had run ahead while the EN
  one drifted: P0 Stage 6 still showed the Mediator module open (RU had it 8/8 complete),
  and the P3 idea bank lacked the newer items (`PersonhoodVerifier`; identity terms in
  the glossary, `PTD-0050`; cross-links IDENTITY↔GLOSSARY, `PTD-0051`; an `appeal`
  registry record; the glossary-link-in-headers generalization). The Documentation agent
  stayed green (pair/switcher/links intact) but the content was out of sync — a violation
  of the "RU↔EN in sync" rule. In one pass: Stage 6 marked complete with the Mediator
  module filled in (`PTD-0028`); the P3 bank synced; the "Done" section gained
  `PTD-0050`/`PTD-0051`/`PTD-0052`. No money/keys/contracts touched. `PTD-0052`. TESTNET-ONLY.
- **PTD-0051 (session 54):** P3 (plain language) — **cross-links
  [`IDENTITY-VERIFICATION.md`](IDENTITY-VERIFICATION.md) ↔ [`GLOSSARY.md`](GLOSSARY.md)**.
  In the identity-verification document (+RU), each technical word now links to its
  glossary entry at first mention — all six terms of the "Identity verification" group
  (Sybil attack, proof-of-personhood, liveness, web-of-trust, zero-knowledge, nullifier);
  a "unfamiliar words → [`GLOSSARY.md`](GLOSSARY.md), the 'Identity verification' group"
  pointer was added to the header. The link is now bidirectional: the glossary points to
  the document (`PTD-0050`), the document points to the glossary. Documentation agent 3/3
  (link-integrity green); IPFS verify=OK (19); `run_all --with-tests`: agents 8/8,
  tests 11/11. `PTD-0051`. TESTNET-ONLY.
- **PTD-0050 (session 53):** P3 (idea bank, plain language) — **identity-verification
  terms added to the glossary in plain words**. A new group "Identity verification — is
  there a live person behind the account" in [`GLOSSARY.md`](GLOSSARY.md) (+RU): six
  entries in human language — "protection from fakes and bot accounts" (Sybil attack),
  "confirmation that you are a live unique person" (proof-of-personhood), "liveness
  check" (liveness), "proof without disclosure" (zero-knowledge), "a one-time
  'already registered' mark" (nullifier), "vouching by live people" (web-of-trust, the
  camera-free fallback). Each entry links to
  [`IDENTITY-VERIFICATION.md`](IDENTITY-VERIFICATION.md); the technical term is in
  parentheses for developers (the plain-language rule, `PTD-0040`). The group list in
  "How to use" was extended; RU↔EN in sync. Documentation agent 3/3
  (pairs/switcher/links green); IPFS manifest rebuilt (verify=OK). `PTD-0050`. TESTNET-ONLY.
- **PTD-0049 (session 52):** P3 (Stage-6 quality standards) — **structure guard
  extended with the `run-all-covers-all` check** in
  [`structure_guard.py`](../../ai-agents/structure_guard.py) (test invariant 17→25).
  A direct follow-up to PTD-0048: a fourth structural standard — every `*_agent.py`
  must be in the `AGENTS` list of the meta-agent
  [`run_all.py`](../../ai-agents/run_all.py), and every `test_*.py` in the `TESTS` list
  (and vice versa: no dangling references to vanished files). So a new agent/test
  cannot be added **bypassing the shared CI run** (`run_all --with-tests`) — otherwise
  it would quietly go unchecked. The check parses `run_all.py` statically (as text, not
  by executing it). **It also closed a real gap:** `test_run_all.py` existed but was NOT
  in `TESTS` — the meta-agent did not run its own test invariant; now added (tests
  10→11). READMEs RU/EN and the CI step updated. On the real repo the guard is 4/4
  green; `run_all --with-tests`: agents 8/8, tests 11/11. `PTD-0049`. TESTNET-ONLY.

- **PTD-0048 (session 51):** P3 (Stage-6 quality standards) — **structure guard**
  [`ai-agents/structure_guard.py`](../../ai-agents/structure_guard.py) (+ test invariant
  [`test_structure_guard.py`](../../ai-agents/test_structure_guard.py), 17/17). Closes two
  open roadmap ideas at once. A service read-only module (Art. 9) looks at the
  `ai-agents/` directory itself and guards three structural standards:
  `agents-have-invariants` (every `*_agent.py` has a paired `test_<name>.py` — no agent is
  "green by default"), `no-orphan-tests` (every `test_*.py` has a source module),
  `sol-parsing-centralized` (no `*_agent.py` keeps a local copy of the `.sol`-parsing
  helpers — they are imported from the shared
  [`solidity_scan.py`](../../ai-agents/solidity_scan.py)). Wired into `run_all --with-tests`
  (tests 9→10); CI turns red on regression. READMEs RU/EN updated. On the real repo the
  guard is 3/3 green; `run_all --with-tests`: agents 8/8, tests 10/10. `PTD-0048`. TESTNET-ONLY.

- **PTD-0039 (session 42):** INBOX #18 (operator) — **[`PROOF-OF-CONTRIBUTION.md`](PROOF-OF-CONTRIBUTION.md) (+RU)**,
  proof of contribution and escrow contracts. The fund creates paid work THROUGH helping
  people; the central problem is proof of execution (**the oracle problem**). Architecture:
  a task with acceptance criteria (bounty/milestone) + escrow locks the reward at assignment;
  proof in three layers (recipient signature + artifact hashes in IPFS, file private +
  auto-verification of on-chain work merge/tests); collective validation (≥N independent,
  worker≠validator) + Fairness/Audit AI (anomaly detection) + **validators STAKE reputation**
  (fraud let through → you lose it) + dispute window/mediation; `release` only when
  confirm∧≥N validators∧expired window, all in registry+on-chain; anti-fraud (anti-Sybil
  against "volunteer=needy" collusion, limits, random re-checks, need outranks reward).
  Honest about the oracle weak spot: start small, scale by trust. `IContributionEscrow`
  sketch for Stage 5. Documentation/Guardian/Audit green, IPFS rebuilt (17). `PTD-0039`.
  TESTNET-ONLY.
- **PTD-0038 (session 41):** INBOX #17 (operator) — **[`REWARDS-MODEL.md`](REWARDS-MODEL.md) (+RU)**,
  the base **adaptive parametric** reward-and-distribution model. (1) Adaptivity:
  distributable budget `D = balance − buffer B_min`; treasury health index `h∈[0,1]`;
  reward share `ρ = ρ_min+(ρ_max−ρ_min)·h` grows with `h` but under a hard
  constitutional ceiling `ρ_cap` (default 0.30 → aid always ≥70%, in scarcity nearly
  all to need); coefficients governed by vote (`parameter-change`→Timelock),
  `ρ_cap`/`referral=forbidden`/buffer are `governed:false`. (2) Three separate streams
  (ranges, not sums): H aid to those in need (targeted spend to a provider by
  [`PRIORITIES.md`](PRIORITIES.md)), W work/contribution (difficulty bands; reputation
  is only a multiplier to position in a band), V volunteering (recognition/non-monetary
  in scarcity); no referral stream (Art. 6.2). (3) Validation: ≥2 independent reviewers
  (no self-approval), Sybil resistance via the soulbound badge, Fairness AI recomputes +
  Audit AI checks against registry/on-chain, every accrual is a registry record + event,
  every refusal has an appeal. The machine-readable parameters §5.1 are a spec for Stage
  5 (a distribution contract over Treasury/Disbursement) and Fairness/Audit AI.
  Documentation/Guardian/Audit green, IPFS rebuilt. `PTD-0038`. TESTNET-ONLY.
- **PTD-0037 (session 40):** P3 (idea bank) — **refactor of the shared Solidity
  helpers of the AI agents** into a single module
  [`ai-agents/solidity_scan.py`](../../ai-agents/solidity_scan.py). The lightweight
  textual `.sol` parsing (`strip_solidity_comments`/`has_function`/
  `function_signature`/`function_body`) was duplicated across the contract agents
  (Reputation, Housing) — the copies could silently diverge. Extracted into one
  read-only, dependency-free module (Art. 9 — a service module, it moves nothing);
  both agents import it. Added a test invariant
  [`test_solidity_scan.py`](../../ai-agents/test_solidity_scan.py) (14/14): comments
  are stripped, a function is found by NAME not substring, the body is extracted by
  brace balance (not up to the first `}`), the signature is parsed. Wired into
  `run_all` (tests 9/9) and CI `ai-agents.yml` automatically (`run_all --with-tests`).
  **Agent behavior unchanged:** Reputation 5/5, Housing 8/8; their invariants 17/17
  and 23/23 as before. `PTD-0037`. TESTNET-ONLY.
- **PTD-0036 (session 39):** P3 (quality/transparency) — **`SECURITY.md` (+EN)**,
  the canonical security policy (GitHub recognizes it, "Report a vulnerability"
  button / Security tab). What counts as a vulnerability (contracts/rails/secret
  leak/attack on verifiability/site/CI), what is not via this channel, private
  reporting (Security Advisories / `security@` once mail is set up / the "rail"
  form), what to expect (coordinated disclosure, no monetary reward — a public
  good), a **safe harbor** for good-faith research, the constitutional rails and
  scope. Cross-links: CODE_OF_CONDUCT (+EN), README (+EN), REPO-STRUCTURE (+EN).
  Documentation agent green (52 public docs, RU↔EN pairs, 0 broken links).
  TESTNET-ONLY, no real funds/keys.
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
| Guard: CI calls run_all (done) / guard checks workflow trigger paths (on.push.paths includes ai-agents/**) / Documentation agent: soft "header pointer leads to glossary" check | agent | 60 |
| Guard: trigger paths include ai-agents/** (done) / guard checks workflow also runs test_run_all.py | agent | 63 |
| Machine-readable run_all status light (done) / public status light on the site from the artifact / guard: status artifact not stale vs verdict | agent | 72 |
| Public status light on the site (done) / compact status chip on the other pages / chip in the topbar too, not only the footer | agent | 73 |
| Label catalog .github/labels.yml (done) / optional label sync / guard: label catalog has no duplicates and valid hex colors | agent | 76 |
