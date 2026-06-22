[Русский](../GOVERNANCE.md) · [English]

# GOVERNANCE COURSE — PUBLIC TRUST DAO

> Normative governance specification. Derived from
> [`CONSTITUTION.md`](CONSTITUTION.md), [`MANIFESTO.md`](MANIFESTO.md),
> [`PRINCIPLES.md`](PRINCIPLES.md). Defines the target model: **the voice of every
> verified human** governs the treasury directly, while the guardians' multisig is
> reduced to an **executor/emergency** role (it carries out the will of the vote, it
> does not rule).
>
> This is a **design proposal and a specification for Stages 4–5**, not a live
> on-chain body. No real funds are involved (see "Rails" below and
> [`CONSTITUTION.md`](CONSTITUTION.md) art. 4.4). The constitutional amendments in
> this document **take effect only after ratification** per [`art. 10`](CONSTITUTION.md)
> — here they are framed as a proposal, not as an already-adopted change.

---

## 0. Why this document exists

The operator set the course (INBOX): the project must be governed by **the voice of
every verified user** — the community votes directly, and the treasury executes
passed decisions automatically. The "5 guardians, 3 of 5" multisig must be reduced
to an **executor/emergency** role, with an explicit path to its gradual replacement
by community vote. At the same time, protection against Sybil attacks (inflating
votes with fake participants) must be provided **without handing power to a narrow
group** — this is the security of a shared wallet, not power over it.

This document turns that course into a verifiable architecture and ties it to the
constitution without breaking the immutable core (art. 1, 2, 3, clause 6.2).

## 1. Constitutional anchors

| Anchor | Source | How this course reinforces it |
|---|---|---|
| No one is the owner | art. 2 | Direct per-person vote spreads power as widely as possible |
| No sole control over funds | art. 2.4, ban #5 | The treasury moves by vote, not by a guardian's signature |
| Distributed governance | PRINCIPLES, chain principles | One-person-one-vote instead of token plutocracy |
| Everything open and verifiable | art. 3 | Every proposal, vote and execution is on-chain and in the registry |
| Constitution changes only via community | art. 10 | The Governor itself is the art. 10 procedure |
| Real-funds latch | art. 4.4 | Preserved: a vote does not waive audit + approval + 3-of-5 humans |

**Key thesis.** Direct voting is not a weakening of treasury security but a
strengthening of it: the wider the right to decide is distributed, the harder it is
for anyone to capture the fund.

## 2. The voting principle: one human — one vote

The right to vote comes from a **verified unique human**, not from an amount of
tokens/money. This follows directly from the ban on power concentration (#5) and
the principle of human dignity: a cleaner's vote equals a donor's vote.

- **NOT plutocracy.** Vote weight cannot be bought. You cannot buy more influence by
  contributing more funds — otherwise the fund becomes "the power of money", which
  directly contradicts art. 2 and the spirit of the project.
- **NOT a sellable right.** The right to vote is non-transferable (soulbound) and is
  not traded: otherwise a market for votes appears and "one human — one vote" is
  bypassed.
- **Base weight = 1.** A limited, transparent multiplier for verifiable socially
  useful contribution is possible (reputation, Stage 6 — Reputation AI), but **with a
  hard cap**, so that no new elite emerges. The multiplier is a governance parameter,
  changed only by vote, and never depends on people recruited (ban #4, art. 6.2).

> The right to vote is implemented as a **non-transferable "participant badge"**
> (soulbound, with no monetary value). It is not a "token asset" and not a share of
> profit — the project has no profit (art. 1.2). It is merely the technical marker
> "verified human = 1 vote".

## 3. Sybil resistance without power concentration

Direct voting is vulnerable to Sybil: one person creates hundreds of "participants"
and decides for everyone. We must confirm the **uniqueness of a human** without
creating a body that owns that uniqueness. The approach is **layered and
replaceable**, and no layer grants anyone power over the treasury:

1. **Proof-of-personhood layer (preferred, decentralized).** External uniqueness
   protocols (e.g. confirming "a living unique human" without revealing identity).
   The project **consumes** the proof but does not own a registry of people.
2. **Social vouching layer (web-of-trust).** Already-verified participants vouch for
   new ones, with limits and reputational liability for the voucher (tied to
   [`ANTI-ABUSE.md`](ANTI-ABUSE.md)). Distributed: there is no single "gatekeeper".
3. **Review-committee layer (temporary, bootstrap).** While the community is small —
   application checks by a rotating group with a public decision log and an appeal
   ([`art. 7`](CONSTITUTION.md)). This is a **check of personhood-uniqueness, not a
   right to dispose of funds** — the committee does not sign disbursements and does
   not control the treasury.

**The core distinction: uniqueness ≠ power.** Any layer answers only the question
"is this a unique living human?". It does **not** decide who is helped or how much,
and it does **not** move funds. Voting decides. The anti-Sybil parameters (which
layers are on, vouching limits) change only by vote and publicly.

> Privacy: uniqueness verification **does not publish personal data**. What is public
> is the fact "address X is a verified unique participant", not the identity (in the
> spirit of [`ANTI-ABUSE.md`](ANTI-ABUSE.md) and the registry — pseudonyms only).

## 4. Governance architecture (target, Stage 4→5)

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

- **Governor** — the heart of direct democracy: any verified participant submits a
  proposal, an open vote runs with quorum and a deadline, the tally is public.
- **Timelock** — a mandatory delay between "decision passed" and "treasury executed".
  A window in which the community/audit/emergency mechanism can stop a clearly harmful
  or captured decision before irreversible execution (tied to ANTI-ABUSE: staging,
  appeals).
- **Treasury** — the Stage 5 treasury contracts; they execute **only** what the
  Timelock sent after a passed vote.
- **Snapshot** — off-chain voting for cheap signals and discussion; it does not move
  funds itself, it serves as a "discussion chamber" before on-chain execution.

## 5. The multisig's new role: executor/insurance, not ruler

The "5 guardians, 3 of 5" multisig (art. 4.2) is **preserved**, but its powers are
narrowed to two functions — both subordinate to the will of the vote:

| What the multisig **can** do | What the multisig **CANNOT** do |
|---|---|
| Technically execute an **already-passed** vote when a manual step is needed | Spend funds without a passed vote |
| Hit the **emergency pause** on a clear exploit/bug (defense, not a decision) | Decide who is helped or how much |
| Sign a routine, uncontested operation within the vote's mandate | Change parameters/constitution bypassing the Governor |
| — | Concentrate power, block the community's will indefinitely |

- **Emergency pause ≠ power.** A pause can only **stop** (protect the treasury from
  irreversible harm), not **direct** funds anywhere. After a pause the question
  returns to a vote/appeal. Any use of the pause is publicly logged to the registry
  with a justification.
- **A guardian is an ordinary participant** (art. 2.2): they have one vote, like
  everyone; the guardian role is a technical safeguard, not a privilege in
  distribution.

## 6. The path of decentralization (gradual replacement of the multisig by vote)

The multisig is **scaffolding** for the time while the community is small and the
contracts have not been audited. An explicit path to removing it as the circuit
matures is built in:

- **Phase A — Bootstrap.** Few participants, contracts on testnet. Multisig 3-of-5 +
  uniqueness review committee. No real funds (art. 4.4).
- **Phase B — Off-chain vote.** Snapshot voting sets the will; the multisig executes
  it manually and reports publicly. The multisig's powers are already executor-only.
- **Phase C — On-chain Governor + Timelock.** Voting is executed automatically via
  the Timelock; the multisig remains an emergency pause only. Audit + explicit
  approval of operator/community + 3-of-5 humans open the real-funds latch (art. 4.4).
- **Phase D — Maturity.** The emergency-pause powers are handed over in stages to
  community mechanisms (e.g. a voted, rotating security council / decentralized
  "security council"). The goal — that no fixed group of five remains necessary
  forever.

The transition between phases is **itself a matter for a vote**: the circuit decides
by vote when it is ready for the next phase. This makes decentralization verifiable
rather than promised in words.

## 7. Proposal lifecycle

```
DRAFT → DISCUSSION (Snapshot/forum) → SUBMITTED to Governor →
VOTE (quorum+deadline) → PASSED/REJECTED →
[if passed] TIMELOCK delay (audit/appeal window) → EXECUTED by treasury →
RECORD in the public registry (governance/registry)
```

- **Who submits:** any verified participant (an anti-spam threshold — small and equal
  for all, not a monetary qualification).
- **Quorum and majority:** governance parameters; for changes touching the
  core/constitution — a raised quorum and supermajority (see §8).
- **Appeal:** every execution is subject to the appeal mechanism from
  [`ANTI-ABUSE.md`](ANTI-ABUSE.md); the Timelock gives it a real window.
- **Transparency:** every proposal and outcome is recorded in the decisions registry
  — a single immutable chronicle (as the PTD-XXXX records already do).

## 8. Proposed constitutional amendments (require ratification per art. 10)

Below is a **proposal**, framed for a future vote. Until ratified per
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

## 9. Safety rails

- **TESTNET-FIRST.** Governor/Timelock/Treasury are written and tested on testnet/
  locally. Real funds — only after audit + approval + 3-of-5 humans (art. 4.4). This
  document does not involve them.
- **No private keys or real guardian addresses in the repo.** Guardian addresses and
  test wallets are created by the operator (request — in PROGRESS).
- **A vote is not bought or sold.** Any mechanism that makes vote weight a function of
  money contradicts the constitution and is not accepted.
- **The emergency pause only stops, it does not direct.** And it is always logged.
- **Bilingual RU↔EN** in one commit (BUILDER.md rule).

## 10. Link to the plan and next steps

- **Stage 4 (Governance):** this document is the specification. Next: a
  `governance/snapshot/` mock-up (space config, "1 human = 1 vote" strategies, quorum,
  proposal types) and `governance/safe/` (multisig role scheme as executor/emergency,
  without real addresses).
- **Stage 5 (Contracts):** the `IGovernor`/`ITimelock`/`ITreasury` interfaces and the
  participant soulbound badge — designed per this model; test coverage on testnet to
  green.
- **Stage 6 (AI agents):** the Governance AI and Reputation AI — service modules
  (art. 9): they help run the process and compute the reputation multiplier
  transparently, **without holding a vote or power over the treasury**.

---

> This is a public good, **not an investment** and **not a pyramid**. The right to
> vote yields no income and is not for sale. Governance exists so that help reaches
> people honestly and verifiably, and power is concentrated in no one's hands.

Related documents: [`CONSTITUTION.md`](CONSTITUTION.md) ·
[`PRINCIPLES.md`](PRINCIPLES.md) · [`ANTI-ABUSE.md`](ANTI-ABUSE.md) ·
[`PRIORITIES.md`](PRIORITIES.md) · [`PRODUCT-INTERFACES.md`](PRODUCT-INTERFACES.md) ·
[`ROADMAP.md`](ROADMAP.md)
