[Русский](../IDENTITY-VERIFICATION.md) · [English]

# MAKING SURE A REAL HUMAN IS BEHIND AN ACCOUNT — WITHOUT SURVEILLANCE — PUBLIC TRUST DAO

> This document explains **how the fund checks that one real, living human stands
> behind a participant** — so that one person can't open ten accounts, inflate
> votes, or receive aid many times under different names — while **not turning into
> a surveillance system** and not collecting a database of people's faces.
>
> Plain words first, technical details for developers below.
>
> Grounded in [`CONSTITUTION.md`](CONSTITUTION.md) (art. 1–3 "no owner, human
> dignity, clarity", art. 7 "abuse protection"), [`PRINCIPLES.md`](PRINCIPLES.md)
> (what the fund must not do), [`GOVERNANCE.md`](GOVERNANCE.md) ("one human = one
> vote", anti-fraud without surveillance), [`ANTI-ABUSE.md`](ANTI-ABUSE.md).
> Connected to [`PROOF-OF-CONTRIBUTION.md`](PROOF-OF-CONTRIBUTION.md) and
> [`REWARDS-MODEL.md`](REWARDS-MODEL.md) (where verifying a person is required
> before voting, aid, and payout).
>
> This is a **design document** — rules for future smart contracts (Stage 5) and
> the "Guardian"/"Audit" AI helpers (Stage 6). The document itself verifies nothing
> and controls no data.
>
> Unfamiliar technical words (proof-of-personhood, liveness, zero-knowledge,
> nullifier, vouching) are explained in plain language in the
> [glossary](GLOSSARY.md) — the "Personhood verification" group.
>
> Registered as a decision in the public registry:
> [`governance/registry/`](../../governance/registry/) (record `PTD-0041`).
>
> **Safety rail.** Everything below is **design and testnet**. The fund enables no
> real face check or biometrics until an independent audit reviews it and the
> community consents. No real personal data is collected meanwhile.

---

## The main point — in plain words

The fund has an honest task: **one real human — one account**. Otherwise one clever
person opens a hundred "identities", grabs a hundred votes, and receives a hundred
times the aid meant for a hundred different people. That is "inflation" (in technical
terms — a ["Sybil attack"](GLOSSARY.md)): many fake accounts in one person's hands.

But there is a second, equally important task: **not to offend or scare living
people**. Among those the fund wants to help are refugees, people without documents,
and people with nothing to hide who are still afraid to hand their face to someone
else's database. So the fund's rule is strict:

> **We verify that a person is real and single — but we don't build a dossier on
> them and don't surveil them.**

How this works in practice:

1. **The fund does not store people's faces.** If a face comparison is needed, a
   separate specialized service does it, and the fund receives only a short answer
   "yes, a living and unique human" or "no". The photo itself **does not stay** with
   the fund.
2. **The face template (if needed at all) stays with the person** — on their phone,
   in their wallet. The fund keeps only a "verified" mark, like a stamp, but without
   the passport itself.
3. **Only the fact, not the identity, goes into the public log (blockchain).**
   Recorded: "participant #N verified as a unique human" — and that's it. Not a name,
   not a face, not an address. A person can prove "I am real and single" **without
   revealing who they are**.
4. **We don't reinvent face checking from scratch.** Proven services for "proving
   you are a living, unique human" already exist. The fund gives a person a **choice
   of several**, including ones that need no face at all.
5. **There is always a fallback with no camera or smartphone.** If a person has no
   phone, no internet, or simply doesn't want to show their face — they can be
   confirmed "in person" by the vouching of several participants or guardians.
   Without this we would cut off exactly the most vulnerable — that is not allowed.
6. **The strictness of the check depends on what the person does.** Just browsing
   the site and reading the log — no check at all. But voting, receiving aid, or a
   payout — here a strong "you are real and single" check is needed, because common
   money and trust are at stake.

In short: **verify the human — yes; collect a database of humans — no.**

---

## Why the fund does NOT collect a face database itself

The operator proposed the right goal — "one human = one account" — and the idea of a
face check. We fully accept the goal. But **the fund must not store people's faces
itself**, and here's the honest why:

- **A face can't be changed like a password.** If a password database is stolen,
  people change passwords. If a face database is stolen, it's stolen forever. That's
  too large a risk to take on.
- **Biometrics are specially protected data by law.** Faces, fingerprints, voices
  are protected by strict laws (in Europe — GDPR; in parts of the US — BIPA and
  analogues). Collecting such a database is a huge legal and moral liability that a
  tiny public-good fund should not shoulder.
- **It would scare away the very people the fund is built for.** A refugee, a person
  without documents, a person in a hard situation will more likely leave than hand
  their face to someone's database. The fund would lose exactly those who most need
  help.
- **It contradicts our own "no surveillance" principle.** [`GOVERNANCE.md`](GOVERNANCE.md)
  states plainly: the fund confirms a person is unique but does not surveil them or
  build a dossier. A face database of one's own *is* surveillance, even with good
  intentions.

What we **take fully** from the operator's proposal: **only facts of agreements and
checks go on-chain, never personal data**. This is the right and important principle
— it becomes the law of this document.

---

## What the check is made of

To be sure "real and single", the fund checks three different things. It's important
not to confuse them:

| What we check | In plain words | Why |
|---|---|---|
| **Living human** | a living person is behind the screen, not a bot or a photo | so accounts aren't stamped out by a program |
| **Unique human** | this living person hasn't opened an account here already | so one person doesn't become "a hundred people" |
| **Right to act** | when needed — that the person is 18, is eligible for aid, etc. | for specific sensitive actions |

The most important boundary of the whole document:

> **Uniqueness is not power.** The check confirms a person is real and single. It
> **grants no access to money** and controls nothing. Money moves only by vote and
> through the shared wallet (3 of 5 guardians) — see [`GOVERNANCE.md`](GOVERNANCE.md).
> These are two separate layers, and they don't mix.

---

## Ready-made verification methods (the person chooses)

The fund does not build its own face check. Instead it accepts several existing,
proven ways to "prove you are a living, unique human". A person picks whichever is
convenient — for both convenience and to avoid depending on a single provider.

- **A method via social connections, with no biometrics at all.** A person is
  confirmed by already-verified people who know them (a "circle of acquaintances"
  approach). No face or documents needed. *(An example service is BrightID.)*
- **A method via a "passport of many signals".** A person gathers several
  independent confirmations of not being a bot (different accounts, participation in
  different systems), and these add up to a "likely a living, unique human" score.
  Biometrics not required. *(An example — Gitcoin Passport.)*
- **A "liveness" face check — but at an external service.** If a person chooses this
  path, a specialized service does the check: it confirms a living, unique human is
  before the camera and **returns only a yes/no to the fund**. The photo does not
  stay with the fund. *(World ID and similar services use this approach.)*
- **A fallback with no camera or smartphone — in-person vouching** (see below).

We **do not lock into a single service forever**: the list of allowed methods is a
setting the community changes by vote (with a delay for review) if a service proves
unreliable or a better method appears.

---

## The fallback: vouching by living people

This is a mandatory part, not a "nice extra". If a person has **no smartphone, no
internet, no documents, or simply doesn't want to show their face** — they can still
be confirmed.

In plain words: several already-verified participants or guardians personally confirm
that they know this person and that they are real and single. Their vouching puts
their reputation on the line: if they confirm an invented person or a "double", they
risk their participant mark and trust (see the reputation-staking model in
[`PROOF-OF-CONTRIBUTION.md`](PROOF-OF-CONTRIBUTION.md)).

Why this is non-negotiable: if only a phone-and-camera check remained, the fund would
automatically cut off the most vulnerable — those who have none of that, yet need
help most. That directly contradicts the mission (art. 5 "fair distribution") and
human dignity (art. 3). So the "in person" path always exists.

---

## How much checking is needed — depends on the action

There's no need to check everyone equally strictly. The more common money and trust
are at stake — the stricter. The more harmless the action — the fewer barriers.

| What the person does | What check is needed |
|---|---|
| Browse the site, read the public decision log, inspect the treasury | **None.** Transparency for all, no login or check. |
| Submit an aid request (for review) | A light check that it's a living human; identity need not be revealed. |
| **Vote** (one human = one vote) | **Strong** uniqueness check — else votes get inflated. |
| **Receive aid or a payout** | **Strong** uniqueness check — else one person receives for many. |

This keeps the fund open to anyone who simply wants to look and trust, and strict
where harm would otherwise be possible.

---

## What goes into the public log, and what doesn't

The principle: **outward — only the fact of the check, never personal data.**

| Visible to all (in the log / blockchain) | Never leaves the person's device / not collected by the fund |
|---|---|
| "participant #… verified as a unique human", date, by which method (no details) | face, photo, "liveness" video |
| the fact of an aid agreement and the course of the payout (per [`ESCROW-TARGETED-DISBURSEMENT.md`](ESCROW-TARGETED-DISBURSEMENT.md)) | name, passport, address, biometric template |
| that the participant has a vote (weight 1) | the link "this account = this specific person" |

This satisfies both the operator's request (on-chain — only facts of agreements) and
the constitutional requirement of "no surveillance, with respect for dignity".

---

## How this connects to the rest of the fund

- **"One human = one vote"** ([`GOVERNANCE.md`](GOVERNANCE.md)) rests directly on
  this check: the personal non-transferable participant mark is issued only after a
  "real and single" confirmation.
- **Protection from inflation and abuse** ([`ANTI-ABUSE.md`](ANTI-ABUSE.md)): the
  uniqueness check is the first barrier against fake accounts and collusion.
- **Proof of contribution and aid** ([`PROOF-OF-CONTRIBUTION.md`](PROOF-OF-CONTRIBUTION.md),
  [`REWARDS-MODEL.md`](REWARDS-MODEL.md)): both the aid recipient and the person
  doing paid work must be confirmed as living, unique humans — else one person
  collects both as the "needy" and as the "volunteer".
- **The constitution**: art. 3 (clarity and dignity), art. 7 (abuse protection), the
  "no surveillance" principle — the document follows all of these to the letter.

---

## Technical section — for developers

Below are details for future contracts (Stage 5) and AI helpers (Stage 6). They are
stated in plain words above; here are the precise terms.

### T.1. Trust model and roles

- [Proof-of-personhood](GLOSSARY.md) is performed by an **external provider**; the
  fund receives only a boolean `verified: true|false` (+ method and timestamp).
  Images, [liveness](GLOSSARY.md) video, raw biometrics **never reach the fund's
  infrastructure** (data minimization, GDPR art. 5(1)(c)).
- A biometric template (if a method uses one) is stored **client-side** (the user's
  device/wallet). Only a membership attribute is written on-chain.
- **Uniqueness ≠ funds authority.** `Reputation.sol` already implements a soulbound
  mark (`votingUnits = 1 + min(rep, cap)`, no `transfer`); the verifier only
  `mint`/`revoke`. Treasury access is a separate circuit
  `Governor → Timelock → Treasury/Disbursement`. The layers don't mix.

### T.2. Binding the verifier to the participant mark (soulbound)

- Today the participant badge is issued by the `verifier` role in `Reputation.sol`
  (`mint(address, registryRef)`). The "verified" source for `verifier` is one of the
  accepted proof-of-personhood methods below.
- On the path to decentralization the `verifier` address becomes either an adapter
  contract (verifying a provider's cryptographic proof) or a role under `Timelock`
  (granted/revoked only by vote) — see phases A→D in `GOVERNANCE.md`.

### T.3. Accepted proof-of-personhood methods (allow-list, governed)

The list is a governed parameter (`parameter-change` → `Timelock`, audit window):

| Method | Biometrics | What it yields on-chain | Notes |
|---|---|---|---|
| Social graph (e.g. BrightID) | no | uniqueness confirmation | inclusive, no camera |
| Signal passport (e.g. Gitcoin Passport) | no (by default) | threshold "not-a-bot" score | configurable threshold |
| Liveness+uniqueness at an external service (e.g. World ID) | yes, provider-side | nullifier/uniqueness proof | fund sees only yes/no |
| Vouching ([web-of-trust](GLOSSARY.md), in person) | no | confirmation via ≥N verified participants | mandatory fallback |

The method registry and thresholds are `governed:true`. The requirement that **at
least one non-biometric and one offline path** always exist is `governed:false` (the
inclusivity core, not removable by ordinary vote).

### T.4. Privacy of the proof (zero-knowledge)

- Goal: the participant proves a predicate (`is_unique`, `age ≥ 18`, `eligible`)
  **without revealing identity** (this is [zero-knowledge / proof without
  disclosure](GLOSSARY.md)). On-chain — only the predicate result and, where
  applicable, a **[nullifier](GLOSSARY.md)** (a one-time "this person already
  registered here" mark that does not reveal who it is).
- The nullifier enforces "one human = one account" without an "account ↔ identity"
  link.
- No source attributes (document, date of birth, biometrics) are published on-chain
  or written to the PTD log.

### T.5. Assurance levels

| Level | Action | Requirement |
|---|---|---|
| L0 | reading site/registry/treasury | none |
| L1 | submitting a request (review) | proof-of-liveness, no identity |
| L2 | voting; receiving aid/payout | strong uniqueness (any T.3 method, incl. vouching) |

Level threshold parameters are `governed:true`. The very existence of L2 for voting
and payouts is an `ANTI-ABUSE.md` requirement (anti-Sybil), `governed:false`.

### T.6. What is written to the registry / on-chain (minimization)

- To the PTD log and on-chain: `member_id` (pseudonym), `verified:true`, `method`,
  `assurance_level`, `timestamp`, `registryRef`. **No** PII or biometrics.
- The source of truth about the "person ↔ template" link is the user's device, not
  the fund.

### T.7. Safety rails (verbatim)

- **No real biometrics or face check is enabled** before an independent audit and
  explicit community consent (TESTNET/design).
- The fund **does not collect or store** images/biometrics; only a "verified"
  attribute.
- An offline path (vouching) and at least one non-biometric method are mandatory —
  else the most vulnerable are excluded (art. 3, art. 5).
- Identity verification **grants no power over funds** (uniqueness ≠ authority).
- All settings are governed with a delay; the inclusivity core is non-reducible.

---

*This document is bilingual: [Русский](../IDENTITY-VERIFICATION.md) · [English].
Documentation license — CC-BY-SA-4.0. This is a public good, NOT an investment.*
