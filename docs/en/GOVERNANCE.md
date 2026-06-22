[Русский](../GOVERNANCE.md) · [English]

# HOW THE FUND MAKES DECISIONS: EVERY PERSON'S VOICE — PUBLIC TRUST DAO

> This document explains **who decides where the money goes, and how** — and why no
> single person and no narrow group can dispose of the shared wallet alone. Plain
> words first, technical details for developers below.
>
> Derived from [`CONSTITUTION.md`](CONSTITUTION.md), [`MANIFESTO.md`](MANIFESTO.md),
> [`PRINCIPLES.md`](PRINCIPLES.md); linked to [`ANTI-ABUSE.md`](ANTI-ABUSE.md),
> [`PRIORITIES.md`](PRIORITIES.md),
> [`IDENTITY-VERIFICATION.md`](IDENTITY-VERIFICATION.md),
> [`REWARDS-MODEL.md`](REWARDS-MODEL.md).
>
> This is a **design proposal and a description for Stages 4–5**, not a live body
> yet. No real funds are involved here (see "Safety limits" below and
> [`CONSTITUTION.md`](CONSTITUTION.md) art. 4.4). The proposed constitution edits
> **take effect only after a community vote** (art. 10) — here they are framed as a
> proposal, not as an already-adopted change.
>
> Registered as a decision in the public registry:
> [`governance/registry/`](../../governance/registry/) (records `PTD-0007`, `PTD-0042`).

---

## In plain words

Imagine the fund has a shared wallet that no one owns personally. Then who decides
whom to help and what to spend on? The answer is simple: **the people decide, by
voting.**

1. **One person — one vote.** Every participant whose reality and uniqueness has been
   confirmed has the right to vote. A vote **cannot be bought with money** and
   **cannot be sold**: a cleaner's vote equals a major donor's vote.
2. **Any participant can propose a decision**, and the community votes "for" or
   "against". For a decision to pass, enough people must vote and the majority must be
   "for".
3. **A passed vote is executed by the treasury itself** — not instantly, but **with a
   delay for review**. That window lets people notice and stop a clearly harmful or
   "hijacked" decision before the money is gone.
4. **No single person disposes of the money.** A group of trusted guardians (a shared
   key-safe where any action needs at least 3 of 5 signatures) is not power but an
   **executor and an emergency brake**: it merely technically carries out an
   already-passed decision and can hit "pause" on a clear breakdown. It cannot send
   money anywhere on its own wish.
5. **So that no one inflates votes with fake accounts**, on joining it is confirmed
   that one living unique human stands behind the participant — but **this
   confirmation gives no one power over the money**, only the right to vote.
6. **Over time the fund becomes ever more self-reliant.** The guardians' role is
   temporary "scaffolding": as the community grows and the code passes review, their
   powers are handed to the community's own mechanisms.

The core idea everything follows from:

> **The more widely the right to decide is distributed, the harder it is for anyone
> to capture the fund.** Every person's direct vote is not a risk to the shared
> wallet but its best protection.

## One person — one vote (not the power of money)

The right to vote comes from a **confirmed unique living human**, not from the amount
of money or tokens on an account. This follows directly from the ban on power
concentration and the principle of human dignity.

- **A vote is not bought.** You cannot get more influence simply by contributing more
  funds. Otherwise the fund would turn into "the power of money" — directly against
  its essence (art. 2).
- **A vote is not sold or transferred.** The right to vote is a **personal,
  non-transferable participant marker**: it cannot be gifted, sold or bought up.
  Otherwise a market for votes would appear and "one person — one vote" would be
  easily bypassed.
- **The base weight is one vote each.** A small, transparent, capped **bonus for
  verifiable useful contribution** (reputation) is possible, but **with a hard cap**,
  so no new "elite" grows. The size of the bonus is a setting changed only by a vote,
  and it **never** depends on how many people someone recruited (forbidden, art. 6.2).

This "participant marker" is not an asset and not a share of profit (the fund has no
profit, art. 1.2). It is just the technical sign "verified living human = one vote".

## Protection against vote inflation and fake accounts

Direct voting has a weak spot: one person could try to create hundreds of
"participants" and decide for everyone (this is called an inflation/*Sybil* attack).
So on joining it is confirmed that **one real unique human** stands behind a
participant. But it is done so that **no body emerges that owns this check and rules
the fund through it**. The approach is several layers to choose from, none of which
grants power over the money:

1. **External "living and unique" check.** Special services confirm a person is real
   and unique without revealing who they are. The fund **receives only a yes/no
   answer** and keeps no database of people itself. Details in
   [`IDENTITY-VERIFICATION.md`](IDENTITY-VERIFICATION.md).
2. **Participants vouching for each other.** Already-verified participants vouch for
   new ones — with limits and the voucher's reputation at stake (vouch for a fake,
   lose reputation). There is no single "gatekeeper" here.
3. **A temporary review committee (at the start).** While the community is small,
   membership applications are checked by a rotating group, with a public decision log
   and the right to appeal (art. 7). This is a **check of uniqueness, not a right to
   dispose of money**: the committee does not sign disbursements and does not manage
   the treasury.

**The core distinction: uniqueness is not power.** Each of these layers answers only
the question "is this one unique living human?". It does **not** decide who is helped
or how much, and it does **not** move money. Voting decides. Which checks are on and
what their limits are — these too are settings, changed only by a vote and openly.

On privacy: the uniqueness check **does not publish personal data**. What is public
is only that "this participant is a verified unique human", not their identity (the
registry holds pseudonyms only).

## Who executes decisions: guardians as executor and brake, not ruler

The fund has a group of five guardians and a shared key-safe where any action needs
at least **3 of 5** signatures. Such a group could once have become a center of
power. Here it is the opposite: its powers are narrowed to two things, both
subordinate to the will of the vote.

| What guardians **can** do | What guardians **CANNOT** do |
|---|---|
| Technically carry out an **already-passed** vote when a manual step is needed | Spend money without a passed vote |
| Hit the **emergency pause** on a clear breakdown/hack (defense, not a decision) | Decide who is helped or how much |
| Sign a routine, uncontested operation within what the vote already approved | Change rules or the constitution bypassing the vote |
| — | Concentrate power or block the community's will indefinitely |

- **The emergency pause is not power.** A pause can only **stop** (protect the wallet
  from irreversible harm), not **direct** money anywhere. After a pause the question
  returns to a vote or appeal. Every use of the pause is publicly recorded in the
  registry with a justification.
- **A guardian is an ordinary participant** (art. 2.2): they have one vote, like
  everyone. The guardian role is a technical safeguard, not a privilege in handing out
  help.

## The path to self-reliance (how the fund gradually removes the "scaffolding")

The guardian group is **temporary scaffolding** while the community is small and the
code has not yet passed independent review. From the start there is an explicit path
for removing this scaffolding as the fund matures:

- **Start.** Few participants, everything on a test network. Guardians 3-of-5 and a
  uniqueness review committee operate. No real funds (art. 4.4).
- **Vote as a signal.** The community votes (in a way not yet binding for execution),
  and guardians carry out its will manually and report publicly.
- **The vote executes itself.** A passed vote is executed automatically, with a delay
  for review; guardians keep only the emergency pause. The fund starts using real
  money **only** after independent review of the code, explicit community consent, and
  signatures of 3 of 5 living people (art. 4.4).
- **Maturity.** Even the emergency pause is gradually handed to community mechanisms
  (e.g. a rotating security council that the community elects itself). The goal — that
  no fixed group of five remains necessary forever.

Moving from one stage to the next is **itself a matter for a vote**: the community
decides when it is ready to go further. This makes self-reliance verifiable, not
promised in words.

## How one decision goes, from idea to execution

1. **Draft and discussion.** Someone proposes an idea, it is discussed.
2. **Submission to a vote.** Any verified participant can submit a proposal (the
   anti-spam threshold is small and equal for all, with no monetary qualification).
3. **Voting.** It runs openly, with a clear deadline; to pass, enough people must vote
   and the majority must be "for". For decisions touching the core or the
   constitution, the bar is higher (broader agreement is needed).
4. **Delay for review.** If a decision passes, it is not executed instantly: there is
   a window to check it, appeal, or — on a clear breakdown — hit pause.
5. **Execution and record.** The treasury executes the decision, and it goes forever
   into the open registry ([`governance/registry/`](../../governance/registry/)) —
   records cannot be altered after the fact.

Every execution is subject to the **right of appeal** (see
[`ANTI-ABUSE.md`](ANTI-ABUSE.md)); the delay for review gives it real time.

## Safety limits (in brief)

- **Test network first.** Everything is written and tested on a test network or
  locally. Real money — only after independent review of the code, community consent,
  and signatures of 3 of 5 living guardians (art. 4.4). This document involves no real
  money.
- **No real keys or guardian addresses in the repository.** The operator creates them;
  the request is in `PROGRESS.md`.
- **A vote is not bought or sold.** Any mechanism where vote weight depends on money
  contradicts the constitution and is not accepted.
- **The emergency pause only stops, it does not direct** — and is always recorded.
- **Uniqueness is not power.** Confirming "a living unique human" grants the right to
  vote, not power over the money.
- **The document is kept in two languages** (Russian and English) in sync.

## Link to the plan

- **Stage 4 (governance):** this document is the description. Next — mock-ups of the
  voting space ([`governance/snapshot/`](../../governance/snapshot/)) and the guardian
  role scheme ([`governance/safe/`](../../governance/safe/)), without real addresses.
- **Stage 5 (contracts):** the voting, delay, and treasury programs and the personal
  non-transferable participant marker are written per this model and covered by tests
  on a test network "to green". Skeletons already exist
  ([`Governor.sol`](../../contracts/contracts/Governor.sol),
  [`Timelock.sol`](../../contracts/contracts/Timelock.sol),
  [`Treasury.sol`](../../contracts/contracts/Treasury.sol),
  [`Reputation.sol`](../../contracts/contracts/Reputation.sol)).
- **Stage 6 (AI assistants):** the governance and reputation assistants are service
  modules (art. 9): they help run the process and compute the contribution bonus
  transparently, **but hold no vote and no power over the money**.

---

> This is a public good, **not an investment** and **not a pyramid**. The right to
> vote yields no income and is not for sale. Governance exists so that help reaches
> people honestly and verifiably, and power is concentrated in no one's hands.

---

## Technical section — for developers

> Below is the precise architecture, component names, and the formal wording of the
> constitution amendments. This is for those writing the contracts and configuring
> voting. Not required to understand the essence — everything important is said above
> in plain words.

### T.1. Constitutional anchors

| Anchor | Source | How this course reinforces it |
|---|---|---|
| No one is the owner | art. 2 | Direct per-person vote spreads power as widely as possible |
| No sole control over funds | art. 2.4, ban #5 | The treasury moves by vote, not by a guardian's signature |
| Distributed governance | PRINCIPLES | "One person — one vote" instead of the power of money (token plutocracy) |
| Everything open and verifiable | art. 3 | Every proposal, vote and execution is on-chain and in the registry |
| Constitution changes only via community | art. 10 | The voting process itself is the art. 10 procedure |
| Real-funds latch | art. 4.4 | Preserved: a vote does not waive audit + approval + 3-of-5 humans |

### T.2. Architecture (target, Stage 4→5)

Four on-chain components + an off-chain layer for cheap signals:

```
  Verified participants (1 human = 1 vote, soulbound badge)
                         │  create and vote
                         ▼
   ┌─────────────────────────────────────────────┐
   │  GOVERNOR (on-chain)                          │
   │  proposals · quorum · timelines · tally       │
   └───────────────┬───────────────────────────────┘
                   │ passed decision
                   ▼
   ┌─────────────────────────────────────────────┐
   │  TIMELOCK (execution delay)                   │  ← window for audit/appeal/emergency veto
   └───────────────┬───────────────────────────────┘
                   │ executes
                   ▼
   ┌─────────────────────────────────────────────┐
   │  TREASURY (Stage 5 contracts)                 │
   └───────────────▲───────────────────────────────┘
                   │ emergency pause / execution of the will only
   ┌───────────────┴───────────────────────────────┐
   │  SAFE MULTISIG 3-of-5 (executor/insurance)     │
   └─────────────────────────────────────────────┘

   Snapshot (off-chain) — cheap signal/discussion before the on-chain vote.
   Public registry governance/registry — immutable chronicle of all decisions.
```

- **Governor** — the on-chain voting program: a verified participant submits a
  proposal, a vote runs with quorum and a deadline, the tally is public and
  deterministic.
- **Timelock** — a mandatory delay between "decision passed" and "treasury executed".
  A window for audit, appeal, and emergency halt before irreversible execution.
- **Treasury** — the Stage 5 treasury contracts; they execute **only** what the
  Timelock sent after a passed vote.
- **Snapshot** — off-chain voting for cheap signals and discussion; it does not move
  funds itself, serving as a "discussion chamber" before on-chain execution.
- **Sybil resistance (anti-Sybil)** — three replaceable layers: external
  proof-of-personhood, social vouching (web-of-trust), a temporary review committee.
  Parameters (which layers are on, limits) are under a vote.

### T.3. The right to vote: a soulbound badge

The right to vote is a non-transferable "participant badge" (soulbound, no monetary
value). Weight = `1 + min(reputation, cap)`; buying/transfer is impossible by design
(no `transfer`/`approve` in the contract). Implementation —
[`Reputation.sol`](../../contracts/contracts/Reputation.sol), `votingUnits(addr)`.

### T.4. Proposal lifecycle

```
DRAFT → DISCUSSION (Snapshot/forum) → SUBMITTED to Governor →
VOTE (quorum+deadline) → PASSED/REJECTED →
[if passed] TIMELOCK delay (audit/appeal window) → EXECUTED by treasury →
RECORD in the public registry (governance/registry)
```

Quorum and majority are governance parameters; for core/constitution changes — a
raised quorum and supermajority (T.5). The submission threshold is a small, equal
anti-spam bar, not a monetary qualification.

### T.5. Proposed constitutional amendments (require ratification per art. 10)

Below is a **proposal** for a future vote. Until ratified per
[`art. 10`](CONSTITUTION.md), the text of the constitution **does not change**. The
amendments preserve the immutable core (art. 1, 2, 3, clause 6.2) and merely make
governance concrete.

- **A-1 (to art. 4 "Treasury management").** Add: "The community's will is expressed
  by a vote of verified participants on a one-human-one-vote basis. Passed votes are
  executed by the treasury (via the Timelock). The Safe multisig 3-of-5 performs an
  executor and emergency (pause) role and cannot dispose of funds bypassing the vote."
- **A-2 (to art. 4).** Add: "The multisig's powers and the anti-Sybil parameters are
  a matter for the community vote and are subject to gradual decentralization
  according to the adopted phase plan."
- **A-3 (to art. 7 "Protection against abuse").** Add: "Confirmation of a
  participant's uniqueness provides the security of the shared wallet and the right to
  vote, but grants no body power over the distribution of funds."
- **Core protection.** No amendment may introduce a sole owner, abolish openness,
  introduce a promise of yield, or make the right to vote buyable/sellable —
  otherwise it is inadmissible (art. 10.2 + bans #1–5).

Upon ratification these formulations are moved into [`CONSTITUTION.md`](CONSTITUTION.md)
(+RU) in a separate commit with a link to the vote record in the registry.

### T.6. Decentralization phases (mapping to "The path to self-reliance")

- **Phase A — Bootstrap.** Multisig 3-of-5 + uniqueness review committee, testnet, no
  real funds.
- **Phase B — Off-chain vote.** Snapshot sets the will; the multisig executes manually.
- **Phase C — On-chain Governor + Timelock.** Auto-execution; the multisig is an
  emergency pause only; the art. 4.4 latch for real funds.
- **Phase D — Maturity.** The emergency pause is handed to a voted security council.

The transition between phases is itself a matter for a vote.

---

Related documents: [`CONSTITUTION.md`](CONSTITUTION.md) ·
[`PRINCIPLES.md`](PRINCIPLES.md) · [`ANTI-ABUSE.md`](ANTI-ABUSE.md) ·
[`PRIORITIES.md`](PRIORITIES.md) ·
[`IDENTITY-VERIFICATION.md`](IDENTITY-VERIFICATION.md) ·
[`REWARDS-MODEL.md`](REWARDS-MODEL.md) ·
[`PRODUCT-INTERFACES.md`](PRODUCT-INTERFACES.md) · [`ROADMAP.md`](ROADMAP.md)
