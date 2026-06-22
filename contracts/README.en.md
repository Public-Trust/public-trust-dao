[Русский](README.md) · [English]

# Smart contracts — Public Trust DAO (Stage 5, SKELETON)

> **SAFETY RAIL — TESTNET-FIRST.** These are contract skeletons for local and
> test networks. **There are no real funds or private keys here, and there never
> will be.** A real treasury comes ONLY after an independent audit + a 3-of-5 Safe
> multisig of living guardians + a separate operator approval (constitution, art. 4.4).

Derived from the normative documents:
[`CONSTITUTION`](../docs/en/CONSTITUTION.md) ·
[`PRIORITIES`](../docs/en/PRIORITIES.md) ·
[`ANTI-ABUSE`](../docs/en/ANTI-ABUSE.md) ·
[`ESCROW-TARGETED-DISBURSEMENT`](../docs/en/ESCROW-TARGETED-DISBURSEMENT.md) ·
[`GOVERNANCE`](../docs/en/GOVERNANCE.md).

## What exists so far

| Contract | Purpose | Status |
|---|---|---|
| [`Treasury.sol`](contracts/Treasury.sol) | Base treasury layer: holds test funds, releases them **only** through the `executor` (multisig/Timelock), per-release cap, emergency pause, an event on every movement. | skeleton + tests ✅ |
| [`Disbursement.sol`](contracts/Disbursement.sol) | Targeted aid escrow: locks funds per case and releases them **strictly to the service provider's address** (`open`/`release`/`refund`/`pause`). "We don't hand out cash — we pay the need." `refund` returns the remainder to the treasury. | skeleton + tests ✅ |
| [`Reputation.sol`](contracts/Reputation.sol) | Non-transferable (soulbound) verified-member badge: one-person-one-vote, `votingUnits` = 1 + a capped multiplier. `verifier` mints/revokes the badge (uniqueness), `governor` sets parameters (power). No role moves funds. | skeleton + tests ✅ |

### Constitutional properties built into `Treasury` (and asserted by tests)

- **No one owns the treasury alone** (art. 1–2): only the `executor` can move
  funds, and per the constitution that must be a 3-of-5 multisig / Timelock, not a
  single person. After the constructor the deployer **has no privileges**.
- **Safety ≠ power:** the `guardian` can only trigger an emergency pause but
  **cannot move funds**; the `executor` cannot pause (roles are separated).
- **Cap / phasing** ([`ANTI-ABUSE`](../docs/en/ANTI-ABUSE.md) §1): a per-release
  cap `maxRelease`; anything larger must be split into tranches.
- **Transparency** (art. 3): every movement (deposit/release/pause/role change)
  emits a public event; a release carries a `registryRef` linking to the decision
  record in the public registry [`governance/registry/`](../governance/registry/).
- **Path to decentralization** ([`GOVERNANCE`](../docs/en/GOVERNANCE.md), phases
  A→D): `setExecutor` lets execution pass from the bootstrap multisig to a voted
  Timelock — callable only by the current `executor`.

### Constitutional properties built into `Disbursement` (targeted escrow)

Implements [`ESCROW-TARGETED-DISBURSEMENT.md`](../docs/en/ESCROW-TARGETED-DISBURSEMENT.md)
(the `ITargetedDisbursement` interface):

- **"We don't hand out cash — we pay the need" (targeted spend, art. 5):** `open`
  fixes the service provider's address into the case; `release(id, amount)` **takes
  no recipient address at all** — the tranche goes strictly to that provider. The
  aid recipient physically cannot redirect funds to themselves.
- **Refund — only to the treasury:** if the service is not delivered, `refund(id)`
  returns the remainder to the `treasury` (collectively controlled), **not** to the
  recipient.
- **Phasing** ([`ANTI-ABUSE`](../docs/en/ANTI-ABUSE.md) §1–§2): monthly tranches via
  an accumulating `released` plus a per-tranche cap `maxRelease`, not an advance.
- **Escrow backing:** a case cannot be opened without free balance
  (`escrowedTotal ≤ balance`), tracked by `available()`.
- **Same roles as the treasury:** only the `executor` (multisig/Timelock) moves
  funds; the `guardian` only pauses; an event on every branch
  (`open`/`release`/`refund`/`pause`) + a `registryRef` to reconcile with the registry.

### Constitutional properties built into `Reputation` (member badge)

Implements [`GOVERNANCE.md`](../docs/en/GOVERNANCE.md) §2–§3 ("one person — one
vote", "uniqueness ≠ power"):

- **One-person-one-vote, not plutocracy (art. 2, prohibition #5):** `votingUnits(addr)`
  returns `0` for a non-member and `1 + min(reputationPoints, reputationCap)` for a
  member. The weight always stays within `[1 .. 1+cap]` — **money cannot buy power**.
- **Soulbound (non-transferable):** the contract has **no transfer function at all**
  (`transfer`/`approve`/`transferFrom`) — by design. A vote cannot be sold, gifted,
  or concentrated by buying up (GOVERNANCE.md §2, "a non-sellable right").
- **Uniqueness ≠ power:** the `verifier` only confirms a person's uniqueness
  (`mint`/`revoke` the badge), the `governor` sets parameters (reputation/cap/roles).
  **No role moves funds** — there are none in this contract; voting decides.
- **Hard multiplier cap:** the contribution bonus is clamped by `reputationCap` so no
  new elite emerges; the cap and reputation are changed only by the `governor` (by vote).
- **Transparency** (art. 3): every change (mint/revoke/reputation/role change) emits
  an event with a `registryRef`; role handover (`setVerifier`/`setGovernor`) is the
  path to decentralization (phases A→D).

## Run (locally, no network, no money)

```bash
cd contracts
npm install        # once
npm test           # compile + tests on the built-in Hardhat network
```

CI runs the same on every push/PR ([`.github/workflows/contracts.yml`](../.github/workflows/contracts.yml)).

## Stack

[Hardhat](https://hardhat.org) + ethers v6 + chai. Solidity `0.8.24`. Tests run on
the built-in in-process Hardhat network — **no external RPC, keys, or mainnet**.
A testnet deploy config (e.g. Polygon Amoy, chainId 80002) is a commented template
in [`hardhat.config.js`](hardhat.config.js); the operator supplies keys via
`contracts/.env` (git-ignored), never in the repository.

## Next steps (Stage 5 skeleton)

- ✅ `Disbursement` — targeted escrow per [`ESCROW-TARGETED-DISBURSEMENT.md`](../docs/en/ESCROW-TARGETED-DISBURSEMENT.md)
  (`open`/`release`/`refund`/`pause`, pay the provider directly) — **done** (skeleton + tests).
- ✅ `Reputation` — a non-transferable (soulbound) verified-member badge
  (one-person-one-vote, `votingUnits` with a capped multiplier) — **done** (skeleton + tests).
- `Governance` — Governor → Timelock (one-person-one-vote, [`GOVERNANCE.md`](../docs/en/GOVERNANCE.md));
  vote weight sourced from `Reputation.votingUnits`; the Timelock is the `executor` of treasury/escrow.
- A public testnet run once the network is agreed with the operator.
