[Русский](../ACCOUNTABILITY.md) · [English]

# EVERYTHING SIGNED AND TRACEABLE — PUBLIC TRUST DAO

> This document explains one of the fund's core principles: **every meaningful
> action has an author, is signed by them, and is recorded so it cannot be altered
> after the fact**. Who proposed what, who reviewed it, who executed it, what an AI
> helper did — all of it is visible, and someone is accountable for each.
>
> Plain words first; technical details for developers below.
>
> The document builds on [`CONSTITUTION.md`](CONSTITUTION.md) (Art. 3 "openness and
> verifiability", Art. 9 "AI has no power", Art. 2 "no owner"),
> [`PRINCIPLES.md`](PRINCIPLES.md) (what the fund may not do), and connects to
> [`GOVERNANCE.md`](GOVERNANCE.md) (how decisions are made),
> [`IDENTITY-VERIFICATION.md`](IDENTITY-VERIFICATION.md) (who stands behind a
> signature), [`PROOF-OF-CONTRIBUTION.md`](PROOF-OF-CONTRIBUTION.md) (how work is
> proven), [`ANTI-ABUSE.md`](ANTI-ABUSE.md) (fraud protection), and the public
> decision registry [`governance/registry/`](../../governance/registry/).
>
> This is a **design document** — a principle and rules for future smart contracts
> (Stage 5) and AI helpers (Stage 6). The document itself controls nothing.
>
> Unfamiliar technical words from this document are explained in plain language in the
> [glossary](GLOSSARY.md) — the "Transparency and verifiability" group.
>
> Registered as a decision in the public registry:
> [`governance/registry/`](../../governance/registry/) (record `PTD-0047`).
>
> **Safety rail.** Everything below is **design and testnet**. Real funds enter
> contracts only after an independent audit, separate approval, and moving the
> treasury under a 3-of-5 multisig of living people (Art. 4.4).

---

## The main idea — in plain words

In ordinary funds it's often unclear **who** made a decision and **why** money went
where it did. We build the opposite. The fund's core rule:

> **Every meaningful action has an author, is signed by them, and is recorded so the
> past cannot be rewritten unnoticed.**

This applies equally to everyone — an ordinary member, a developer, and an AI
helper. Here is what it means in practice:

1. **Every important action carries the author's name.** Filing a request, voting,
   reviewing someone's work, proposing a rule change, executing a payout — it's clear
   who did it. There are no anonymous "decisions out of nowhere".

2. **Signed means accountable.** A "signature" here isn't a pen stroke but an
   electronic confirmation "yes, I did this". You can't forge someone else's, and you
   can't deny your own.

3. **Recorded so the past can't be rewritten.** All decisions go into an open
   journal built as a chain: each new entry "seals" the previous one. If someone
   alters an old entry after the fact, the chain breaks and everyone sees it. History
   cannot be quietly tidied up.

4. **Not everything goes on-chain — only the important things.** Two things must be
   distinguished:
   - **"signed and accountable"** — applies to **all** meaningful actions;
   - **"anchored on-chain"** — only for the most important: **money, power, and
     agreements** (payouts, votes, rule changes, targeted aid).

   Putting every small action on-chain is impossible — it's expensive, slow, and
   personal data must never go there. So only a **fingerprint** (a short trace that
   lets anyone verify the record wasn't changed) goes on-chain, while the text itself
   lives in the open journal.

5. **AI is always under signature — but without power.** Every AI helper's action is
   signed and lands in the journal; important ones are anchored on-chain. And, most
   importantly: **AI does not move money or power itself**. It checks, computes, and
   advises; execution is done by a rule-bound contract or by living people. AI is
   always visible and verifiable — but holds no sole power (Art. 9).

6. **Developers are under signature too.** Any code change is already signed by the
   change history (each commit has an author). But **what actually gets deployed** and
   **which powers** change in the process is decided by a vote and executed by a
   contract — not quietly by one person.

In short: **you can see who did it, what they did, and it cannot be rewritten after
the fact.** That is the basis of trust without an owner.

---

## Why this matters

The fund is built to have **no owner** (Art. 2) and to be run by the community. But
"no owner" only works if every action has a **trace and an author** — otherwise
anything could be quietly slipped through under the cover of "the collective".
Traceability is what **replaces a boss**: instead of "trust us" the fund says "check
for yourself".

It delivers three things:

- **Accountability.** Since an action has an author and a signature, a specific
  person or role answers for a mistake or bad intent — not "the system in general".
- **Trust without taking it on faith.** Anyone can walk the journal and confirm the
  money moved by the rules and the decision was made honestly (Art. 3
  "verifiability").
- **Protection from tampering.** The chain of records and on-chain fingerprints make
  rewriting history unnoticed impossible — fraud is visible at once.

---

## Two levels: "under signature" and "on-chain"

This is the document's key distinction. They are easy to confuse, but they are
**different things**.

| | Under signature and in the journal | Anchored on-chain |
|---|---|---|
| **What goes here** | any meaningful action: requests, reviews, proposals, reports, AI actions | only money, power, agreements: payouts, votes, rule changes, targeted aid |
| **Why** | the action has an author, can't be forged, history isn't rewritten | an irreversible record of the most important things, executed by a program |
| **What is stored** | the text/fact + the author's signature in the open journal | a **fingerprint** of the fact (not personal data) + the contract event |
| **Cost** | cheap, fast | costlier and slower — so only for the important |

The rule is simple: **everything meaningful is under signature; the most important
(money/power/agreements) is also on-chain, but we put a fingerprint there, not
personal data.**

Why not everything on-chain: it's expensive, slow, and personal data (an applicant's
name, their history) **must not** go there — it would stay forever. Only a short
verification trace goes on-chain; details live in the open journal under pseudonyms
(see [`ESCROW-TARGETED-DISBURSEMENT.md`](ESCROW-TARGETED-DISBURSEMENT.md),
[`IDENTITY-VERIFICATION.md`](IDENTITY-VERIFICATION.md)).

---

## Who is responsible for what

The "under signature" principle applies equally to all participants, but shows up
differently.

| Who | What they sign | What is anchored on-chain |
|---|---|---|
| **Member** | aid request, vote, confirmation of receipt | their vote (weight 1), the fact of an aid agreement |
| **Reviewer / validator** | their verdict "work done / need confirmed" | confirmation before a payout is unlocked |
| **AI helper** | each of its computations, checks, alerts | a fingerprint of an important verdict (but **not** the money movement itself) |
| **Developer** | each code change (commit history) | what is deployed and which powers changed — via a vote |
| **Guardian (3-of-5)** | their part in execution / emergency pause | execution of the vote's will; a pause is always public |

An important boundary: **signature = accountability, not power.** The fact that an AI
or a guardian signed something does not mean they control money alone. Money moves
only by vote and through the shared wallet (see [`GOVERNANCE.md`](GOVERNANCE.md)).

---

## AI actions: always visible, but without power

This deserves its own section, because AI does a lot of invisible work in the fund
(reviewing requests, computing rewards, looking for anomalies). The rule for AI is
strict:

- **Every AI action is signed and in the journal.** It's clear which helper, when,
  and what it computed or proposed — and it can be re-checked.
- **Important verdicts are anchored on-chain by a fingerprint** — so they can't be
  quietly swapped after the fact.
- **AI does not move money or power itself.** It shows and advises; a vote decides, a
  rule-bound contract or a living person executes. This is a direct constitutional
  requirement (Art. 9: "AI has no power, AI does not own funds").
- **AI is always under signature, but without sole power.** That makes its
  usefulness visible while ruling out "the machine decided everything by itself".

---

## How this connects to the rest of the fund

- **The open decision journal** ([`governance/registry/`](../../governance/registry/))
  is the already-working foundation of this principle: an append-only chain with
  tamper protection (each entry seals the previous one). This document explains the
  principle the journal embodies.
- **Targeted aid** ([`ESCROW-TARGETED-DISBURSEMENT.md`](ESCROW-TARGETED-DISBURSEMENT.md))
  and **proof of contribution** ([`PROOF-OF-CONTRIBUTION.md`](PROOF-OF-CONTRIBUTION.md)):
  every payout and every work confirmation is under signature and in the journal;
  the important parts are on-chain.
- **Governance** ([`GOVERNANCE.md`](GOVERNANCE.md)): votes and rule changes are
  exactly the "agreements and power" that are anchored on-chain.
- **Who stands behind a signature** ([`IDENTITY-VERIFICATION.md`](IDENTITY-VERIFICATION.md)):
  a signature is tied to a confirmed unique person, but without revealing identity
  and without surveillance.
- **Fraud protection** ([`ANTI-ABUSE.md`](ANTI-ABUSE.md)): traceability is the first
  barrier, because cheating under your own signature in an unrewritable journal
  doesn't pay.

---

## Technical section — for developers

Below are details for future contracts (Stage 5) and AI helpers (Stage 6). Above
they are given in human words; here are the precise terms.

### T.1. Two layers of accountability

| Layer | Mechanism | Scope |
|---|---|---|
| **Authenticated & traceable** (under signature) | cryptographic author signature + append-only hash-chain journal | **all** meaningful actions |
| **On-chain anchored** | smart-contract event + on-chain hash/commitment | only money, power, agreements |

Minimization principle: on-chain stores a **commitment/hash** of the fact, not the
fact itself, and never PII. The full (pseudonymized) text lives in the PTD journal;
on-chain holds only a verification fingerprint (`keccak256`/`sha256` of the record).

### T.2. Signing an action

- Every meaningful action carries the author's signature (EIP-191/EIP-712 for the
  on-chain context; a detached signature or a signed commit for off-chain journal
  records).
- The author is tied to a confirmed unique participant (see
  [`IDENTITY-VERIFICATION.md`](IDENTITY-VERIFICATION.md)) — but only a
  pseudonym/`member_id` is revealed on-chain, not the identity.
- The signature provides **non-repudiation** (authorship can't be denied) and
  **authenticity** (someone else's can't be forged) — but **grants no power over
  funds** (that is the separate `Governor → Timelock → Treasury/Disbursement`
  circuit).

### T.3. Journal immutability (hash-chain)

- The registry [`governance/registry/`](../../governance/registry/) is append-only:
  each record holds `prev_hash` and `hash` (sha256 of canonicalized content).
  Altering any middle record breaks the chain → `registry.py verify` exits 1, CI
  fails the build (`.github/workflows/registry.yml`).
- `head_hash` in `index.json` is a fingerprint of the whole journal, convenient as an
  anchor in IPFS / on-chain (see [`scripts/ipfs_manifest.py`](../../scripts/ipfs_manifest.py)).

### T.4. On-chain anchoring (what and when)

On-chain anchoring triggers (important = money/power/agreements):

| Event | On-chain artifact |
|---|---|
| Payout / targeted spend | `Disbursement` event + hash of the registry record |
| Vote / rule change | proposal and result in `Governor` (+ `Timelock`) |
| Aid agreement | commitment of escrow terms (`ESCROW-TARGETED-DISBURSEMENT.md`) |
| Emergency pause | public `paused()` event with the `guardian` author |

Small/frequent/PII-bearing actions are **not** written on-chain — only signature +
journal. Journal↔chain link: on-chain stores `keccak256(registry_record)`, verifiable
against the public text.

### T.5. AI-agent actions

- On a meaningful output, each agent ([`ai-agents/`](../../ai-agents/)) writes a
  signed record to the journal (actor = agent identifier, e.g. `fairness-agent`);
  important verdicts are anchored by an on-chain hash.
- Agents hold **no** keys with treasury powers. The execution role is `Timelock`; the
  emergency-pause role is `guardian` (multisig). An agent can only signal (Art. 9).
  This matches the separation in [`ANTI-ABUSE.md`](ANTI-ABUSE.md).

### T.6. Developer actions

- Change authorship — signed git commits (repository history).
- **What gets deployed and which roles/powers change** — via
  `parameter-change`/`upgrade` → vote → `Timelock`, not directly by a developer's
  key. Correspondence to decentralization phases — see `GOVERNANCE.md` (T.6).

### T.7. Proposed constitutional amendment (requires ratification under Art. 10)

Below is a **proposal** for a future vote. Until ratified under
[`Art. 10`](CONSTITUTION.md), the constitution text is **unchanged**. The amendment
preserves the immutable core (Art. 1, 2, 3, clause 6.2) and only concretizes Art. 3.

- **A-4 (to Art. 3 "Openness and verifiability").** Add clause 3.4: "Every meaningful
  action of participants, AI agents, and developers has an author, is certified by
  their signature, and is recorded in a tamper-evident public journal. Actions that
  affect funds, powers, and agreements (payouts, votes, rule changes, targeted aid)
  are additionally anchored by a fingerprint on-chain. AI agents act only under
  signature and do not control funds or powers alone (Art. 9)."
- **Core protection.** The amendment introduces no sole owner, does not abolish
  openness, and introduces no promise of returns — it only strengthens verifiability
  (Art. 10.2 satisfied).

On ratification the wording moves into [`CONSTITUTION.md`](CONSTITUTION.md) (+RU) in a
separate commit referencing the vote record in the registry.

### T.8. Safety rails (literally)

- **Signature = accountability, not power.** Authoring an action grants no power over
  funds; money moves only via a vote and the 3-of-5 shared wallet.
- **On-chain — only a fingerprint, not PII.** Personal data goes neither on-chain nor
  into the public journal (only pseudonyms/hashes).
- **AI — under signature, no sole power** (Art. 9).
- **History immutability** is ensured by hash-chain + CI checks; a broken chain is
  immediately visible.
- **TESTNET-first**: real on-chain anchoring of funds only after audit and approval
  (Art. 4.4).

---

*This document is bilingual: [Русский](../ACCOUNTABILITY.md) · [English]. Documentation
license — CC-BY-SA-4.0. This is a public good, NOT an investment.*
