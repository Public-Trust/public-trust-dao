[Русский](../PRODUCT-INTERFACES.md) · [English]

# PRODUCT FORM AND INTERFACES — PUBLIC TRUST DAO

> Normative design document (technical spec, section "Product form / interfaces").
> Derived from [`MANIFESTO.md`](MANIFESTO.md), [`CONSTITUTION.md`](CONSTITUTION.md),
> [`PRINCIPLES.md`](PRINCIPLES.md) and [`ESCROW-TARGETED-DISBURSEMENT.md`](ESCROW-TARGETED-DISBURSEMENT.md).
> It fixes the **form** in which the project reaches an ordinary person: which
> interfaces we build, in what order, and why.
>
> Registered as a decision in the public registry:
> [`governance/registry/`](../../governance/registry/) (entry `PTD-0003`).
>
> **Everything is TESTNET-first.** Every interface first runs on a test network
> with test funds. Production with real money — only after an independent contract
> audit, explicit operator approval, and a 3-of-5 Safe multisig of real people.

---

## 1. Why this document

The treasury, smart contracts and AI agents are the "engine". But an ordinary
person never interacts with a contract directly — they see an **interface**. The
quality and honesty of the interface decide whether the project is accessible to
those it is built to help: people in hardship, often without technical experience.

This document fixes the form of the end product, so that all later stages
(Stage 5 contracts, Stage 6 agents) are built with a clear human "face" rather
than as a pile of technical artifacts.

---

## 2. The four product layers

The project is four layers, bottom to top. The first three are the "engine", the
fourth is the "face". The interface adds no power: it merely gives people
convenient, verifiable access to what is already fixed in the constitution and code.

| # | Layer | What it is | Where in the repo |
|---|-------|------------|-------------------|
| 1 | **Treasury** | Public funds on the blockchain (Safe multisig, no sole owner) | Stage 4 (`governance/safe/`), Stage 5 |
| 2 | **Smart contracts** | Digital embodiment of the constitution: custody, voting, disbursements, reputation, audit, appeals | Stage 5 (`contracts/`) |
| 3 | **AI agents** | Guardian / Audit / Fairness / Reputation / Housing / Governance / Mediator / Documentation — help enforce the constitution, hold no power | Stage 6 (`ai-agents/`) |
| 4 | **Interface** | What a person actually uses the fund through: web dApp, Telegram bot, mobile app | Stage 2 onward (`web/`) |

Linking principle: **the interface decides nothing on its own**. It only displays
the state of the lower layers (registry, treasury, votes) and relays a person's
intent (request, vote) to the contracts. Any action that moves funds passes
through the contracts and the multisig — not through the interface. This follows
directly from the constitutional ban on concentration of power
([`PRINCIPLES.md`](PRINCIPLES.md)).

---

## 3. Interface roadmap (what we build, and in what order)

### 3.1. Web dApp — first and primary

A browser-based decentralized application. No install required, works from any
device, easiest to keep open and verifiable. This is the "main entrance".

**Minimum functions of the first release (testnet):**

1. **Submit an aid request** — a request form. Personal data is not published;
   only a pseudonymous `case_id` and the non-sensitive essence go to the public
   registry (see the privacy model in
   [`ESCROW-TARGETED-DISBURSEMENT.md`](ESCROW-TARGETED-DISBURSEMENT.md)).
2. **See the public decision registry** — a readable view of
   [`governance/registry/`](../../governance/registry/): who, what, when, with
   links; with the ability to verify the hash-chain locally.
3. **Vote** — participation in governance decisions (off-chain Snapshot at the
   start, on-chain later). Tied to the constitution: distribution priority, appeals.
4. **Verify treasury transactions** — a transparent view of fund movements
   (testnet), linking disbursements to registry entries and escrow states.

**Technical rails:** a static frontend (as already chosen in Stage 2 — no external
CDNs/trackers, not a single unnecessary outgoing request), wallet connection
(MetaMask/WalletConnect) only for actions that require a signature; reading the
registry and manifests works without a wallet, publicly and anonymously.

### 3.2. Telegram bot — a low-barrier entry

Many people in hardship live in a messenger, not in a dApp browser. The bot is a
**low barrier to entry**, not a separate product:

- submit a request and get its status without installing a wallet;
- notifications about review and disbursement stages (the escrow state machine);
- links to public registry entries for independent verification.

The bot **holds no funds and makes no decisions** — it is only a shell for
intake and notifications on top of the same contracts and registry. Any sensitive
data follows the privacy model, without publishing personal information.

### 3.3. Mobile app — on demand

A wrapper over the web dApp (PWA or native shell), once there is clear demand and
the resource to maintain it. It adds no new logic — the same functionality, more
convenient on a phone. To be done only after a stable dApp, so as not to spread
support thin.

---

## 4. Why this order

- **dApp first** — it is the most transparent and verifiable (open code in the
  browser), delivers all four key functions at once, and depends on no third-party
  platform.
- **Bot second** — it removes the technical barrier for the most vulnerable users,
  but relies on contracts and a registry that already exist.
- **Mobile app last** — it is convenience, not a new capability; built on demand,
  so as not to inflate support too early.

In all cases there is a single source of truth — the contracts and the public
registry. The interfaces are interchangeable and do not create a parallel "second
power".

---

## 5. Constitutional rails for interfaces

Every interface must:

- **never promise yield or guarantee profit**, anywhere in text or UI; everywhere
  explicitly: this is a public good, **not an investment, not a pyramid**;
- **never pay for recruiting people** — no referral rewards;
- **never publish applicants' personal data** (only a pseudonymous `case_id`);
- **display, not decide** — all actions on funds go through the contracts and the
  3-of-5 multisig, not through the UI;
- **be verifiable** — give a person a way to independently check the registry and
  the treasury (hash-chain, IPFS CIDs, tx hashes);
- **work without surveillance** — no third-party trackers, no needless outgoing
  requests.

These requirements follow directly from [`PRINCIPLES.md`](PRINCIPLES.md) and
[`CONSTITUTION.md`](CONSTITUTION.md) and are mandatory to check when accepting each
interface.

---

## 6. Link to the plan stages

| Interface | Relies on | When |
|-----------|-----------|------|
| Public site (read-only) | — | Stage 2 (done, part 1) |
| Web dApp (request/registry/vote/treasury) | registry (Stage 3), governance (Stage 4), contracts (Stage 5) | after the base contracts |
| Telegram bot | the same contracts and registry | after the dApp |
| Mobile app | web dApp | on demand |

This document is updated as the "engine" layers become ready.

---

*This document is open and explained. Changes are recorded in git and in the public registry.*
