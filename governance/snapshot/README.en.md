[Русский](README.md) · [English]

# Snapshot — off-chain voting space (one person = one vote)

> Mock-up and "ready-to-click" guide for the community's **off-chain voting** on
> the [Snapshot](https://snapshot.org) platform. Implements the target model of
> [`docs/GOVERNANCE.md`](../../docs/en/GOVERNANCE.md): **each verified person has
> one vote** (one person = one vote); power and money cannot be bought.
>
> This is part of Stage 4 (Governance). Snapshot is a **discussion/signal
> chamber** BEFORE on-chain execution: voting is off-chain (signature, gasless),
> Snapshot **does not move funds**. Execution happens via Safe/Timelock after a
> passed vote (see [`docs/GOVERNANCE.md`](../../docs/en/GOVERNANCE.md) §4, §7).

---

## 0. What this is and is NOT

| It is | It is NOT |
|---|---|
| Community off-chain voting (gasless signatures) | On-chain execution / movement of funds |
| "One person = one vote": each admitted address = exactly 1 vote | Plutocracy of "more money — more influence" |
| Signal/discussion before on-chain submission to the Governor | Final disposal of the treasury (that's vote → Timelock → treasury) |
| Admission only for verified unique participants | A body owning a "registry of people" or the right to hand out funds |

**Snapshot spends nothing by itself.** It is a tool for expressing will. Real
fund movement happens only through on-chain execution after audit and approval
([`CONSTITUTION.md`](../../docs/en/CONSTITUTION.md) art. 4.4). The agent never
crosses this threshold.

## 1. Why off-chain voting now

On-chain voting costs gas and requires deployed contracts. Snapshot provides a
**cheap, verifiable discussion chamber** already at the bootstrap stage: the
community can express its will with a wallet signature (free), and the result is
public and immutable. This is the "DISCUSSION/signal" step of the proposal
lifecycle ([`docs/GOVERNANCE.md`](../../docs/en/GOVERNANCE.md) §7) — before a
decision goes to on-chain execution via Governor → Timelock → Treasury.

## 2. Parameters (see also `space.json`)

- **Platform:** Snapshot (off-chain, gasless signatures).
- **Reference network:** Polygon **Amoy testnet** (`chain_id = 80002`) — matches
  [`governance/safe`](../safe/README.en.md). Snapshot needs the network only as a
  reference point (snapshot block) for strategies; voting is off-chain.
- **Voting strategy:** `ticket` with `value = 1` — **each admitted address gets
  exactly 1 vote**, regardless of balance.
- **Admission:** only verified unique participants (`filters.onlyMembers` +
  `validation`) — otherwise "one person = one vote" is vulnerable to Sybil.
- **Real funds:** none. Snapshot does not move them.

Why `ticket`, not token-balance strategies:

- **Not plutocracy.** Vote weight does not depend on money: a cleaner's vote
  equals a donor's ([`docs/GOVERNANCE.md`](../../docs/en/GOVERNANCE.md) §2,
  art. 2, prohibition #5).
- **Not for sale.** The right to vote is non-transferable (soulbound) and not
  traded.
- **The validator enforces it:** strategies that weight votes by balance
  (`erc20-balance-of`, weighted `erc721`, delegation, etc.) are **rejected**
  (see §6).

## 3. Proposal types

Defined in `space.json` → `proposal_types` (all off-chain — this is signal,
execution is separate):

| Key | What | Anchor |
|---|---|---|
| `signal` | Non-binding poll of community sentiment | — |
| `disbursement-direction` | Directions/priorities of aid | [`PRIORITIES.md`](../../docs/en/PRIORITIES.md), [`ANTI-ABUSE.md`](../../docs/en/ANTI-ABUSE.md) |
| `parameter-change` | Quorum, timelines, limits, anti-Sybil params, multisig powers | [`GOVERNANCE.md`](../../docs/en/GOVERNANCE.md) §5–6 |
| `constitution-amendment` | Amendment under art. 10 (raised quorum, supermajority; core untouched) | [`CONSTITUTION.md`](../../docs/en/CONSTITUTION.md) |
| `phase-transition` | Decentralization phase transition A→B→C→D | [`GOVERNANCE.md`](../../docs/en/GOVERNANCE.md) §6 |

## 4. Anti-Sybil: uniqueness ≠ power

For "one person = one vote" to mean anything, only verified unique participants
may vote. But admission **confirms a person's uniqueness, it does not grant power
over the treasury** ([`docs/GOVERNANCE.md`](../../docs/en/GOVERNANCE.md) §3):

1. **proof-of-personhood** (decentralized, preferred).
2. **Social vouching** (web-of-trust, with limits).
3. **Uniqueness review panel** (temporary, bootstrap; does not sign payouts).

> Privacy: what is public is the fact "address X is a verified unique
> participant", **not the identity** (pseudonymity, as in the registry and
> [`ANTI-ABUSE.md`](../../docs/en/ANTI-ABUSE.md)).

## 5. Operator guide — create the space "ready to click"

The agent does not create external accounts or sign transactions — the operator
does. Steps:

1. **ENS domain.** A Snapshot space is controlled by an ENS name (e.g.
   `publictrust.eth`). Register ENS (a one-off external step by the operator on
   mainnet) and set a controller wallet.
2. **Create space.** Open [snapshot.org](https://snapshot.org) → "Create space"
   → link ENS → set the settings from `space.json` → `settings` (name, network
   `80002`, strategy `ticket` value=1, `filters.onlyMembers`, `validation`,
   voting types, quorum/timelines).
3. **Send identifiers.** Copy the `ens`, space `id`, `controller` address and
   public `url` and send them via [`comms/INBOX.md`](../../comms/INBOX.md) (or the
   operator fills them in). These are **public** data.
4. **The agent fills in** `space.ens/id/controller/url`, switches `status` →
   `deployed-testnet`, sets the quorum, runs the validator (§6), adds a link to
   the site/README and registers an entry in the [registry](../registry).

> The list of verified participants (badge/whitelist) is wired in via the
> admission strategy. While the community is small — via the uniqueness review
> panel (§4), publicly and with appeal. Participant addresses are pseudonymous
> (not identity).

## 6. Config check (rails validator)

`space.json` is checked by a dependency-free script — it fails the build on any
rails violation:

```bash
python3 scripts/snapshot_config.py verify
```

The script checks: the schema (`schema/snapshot-space.schema.json`);
`off_chain_signaling` (vote is signal, not fund movement); **testnet only**
(`is_testnet=true`, `chain_id` from the testnet allow-list, rejection on
mainnet); **"one person = one vote"** (only equal-weight `ticket` value=1
strategies; **rejection** of plutocratic token-balance strategies); restriction
of voting to verified participants (anti-Sybil); allowed voting type; and — most
importantly — that **the config contains no private keys/seed phrases/secrets**
(it catches 64-hex strings and the words `private key`/`mnemonic`/`seed`). CI
([`.github/workflows/snapshot.yml`](../../.github/workflows/snapshot.yml)) runs
this check on every push.

## 7. Relation to the plan

- **Stage 4 (Governance):** this mock-up (off-chain vote) +
  [`governance/safe`](../safe/README.en.md) (executor/emergency) +
  [`docs/GOVERNANCE.md`](../../docs/en/GOVERNANCE.md) (the model). Snapshot covers
  the "discussion/signal" step.
- **Stage 5 (Contracts):** on-chain Governor → Timelock → Treasury; Snapshot
  remains a discussion chamber before on-chain execution.
- **Decentralization path:** in phase B Snapshot is exactly what sets the will,
  while the multisig executes it manually and reports publicly
  ([`docs/GOVERNANCE.md`](../../docs/en/GOVERNANCE.md) §6).

## NEEDED FROM THE OPERATOR

- **ENS domain** for the space + controller wallet (a one-off external step).
- **Creating the space** on [snapshot.org](https://snapshot.org) (requires a
  wallet and signature) — steps in §5. After that the agent fills in the
  identifiers and registers.

---

> This is a public good, **not an investment** and **not a pyramid**. The right
> to vote yields no income and is not for sale; vote weight = 1 and cannot be
> bought. Governance exists so that the community's will is verifiable and power
> is not concentrated in anyone.

Related: [`docs/GOVERNANCE.md`](../../docs/en/GOVERNANCE.md) ·
[`docs/CONSTITUTION.md`](../../docs/en/CONSTITUTION.md) ·
[`docs/PRIORITIES.md`](../../docs/en/PRIORITIES.md) ·
[`docs/ANTI-ABUSE.md`](../../docs/en/ANTI-ABUSE.md) ·
[`governance/safe`](../safe/README.en.md) · [`governance/registry`](../registry) ·
[`space.json`](space.json)
