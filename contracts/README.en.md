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
| [`Governor.sol`](contracts/Governor.sol) | Direct voting by verified members: `propose`/`castVote`/`queue`/`execute`. Vote weight comes from `Reputation.votingUnits` (one-person-one-vote). Quorum, period, public tally. A passed decision is executed **only through the Timelock** — the Governor never moves funds itself. | skeleton + tests ✅ |
| [`Timelock.sol`](contracts/Timelock.sol) | Mandatory delay between "decision passed" and "treasury executed" (an audit/appeal window). `schedule`/`execute` — only the `governor` (= Governor), `cancel` — only the `guardian` (emergency veto). Set as the `executor` of `Treasury`/`Disbursement`. | skeleton + tests ✅ |
| [`scripts/deploy.js`](scripts/deploy.js) | **Wires the whole contour** in one pass: deploys all 5 contracts and links them (executor=Timelock, governor=Governor, `renounceAdmin`, Reputation.governor=Timelock). After wiring no single person can move funds alone. | script + integration test ✅ |

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

### Constitutional properties built into `Governor` + `Timelock` (governance)

Implements [`GOVERNANCE.md`](../docs/en/GOVERNANCE.md) §4–§7 (Governor → Timelock →
Treasury/Disbursement — direct voting executed with a mandatory delay):

- **One-person-one-vote, not plutocracy (art. 2, prohibition #5):** vote weight is
  sourced from [`Reputation.votingUnits`](contracts/Reputation.sol); a non-member can
  neither vote nor propose. The proposal threshold is equal for all (membership),
  **not monetary**.
- **The Governor never moves funds itself (art. 4):** a passed decision is queued in
  the `Timelock`, and the treasury (`Treasury`/`Disbursement`) executes only what the
  `Timelock` forwards after a passed vote. `execute` before the delay is impossible.
- **The delay = an audit/appeal/veto window** ([`ANTI-ABUSE`](../docs/en/ANTI-ABUSE.md)):
  a mandatory `minDelay` pause sits between "passed" and "executed"; within it the
  `guardian` can emergency-cancel an operation (`cancel`) — **a veto, not control of funds**.
- **Role separation:** the `governor` (= the Governor contract) schedules/executes;
  the `guardian` only emergency-cancels; the `admin` is a one-off bootstrap configurator
  that **must renounce** (`renounceAdmin`); no role moves the treasury.
- **Parameters — by vote only (§6, path A→D):** period/quorum/delay and role changes
  after renounce are changed **only through the mechanism itself** (`onlyTimelock`/
  `onlySelf`), never around it. Quorum and majority tallies are public and deterministic.

### Wiring the contour: `scripts/deploy.js` (part 3c)

The script deploys all five contracts and links them into a single mechanism per
[`GOVERNANCE.md`](../docs/en/GOVERNANCE.md) §4–§7:

```
  Reputation ──(one-person-one-vote weight)──▶ Governor
                                                  │ queue/execute
                                                  ▼
  guardian ──(emergency veto)──▶ Timelock ──(executor)──▶ Treasury
                                    ▲                     Disbursement
                                    └ governor = Governor
```

Wiring result (asserted by the integration test): `Treasury.executor` =
`Disbursement.executor` = **Timelock**; `Timelock.governor` = **Governor**;
`Timelock.admin` = **0** (bootstrap dropped via `renounceAdmin`);
`Reputation.governor` = **Timelock** (vote parameters change only by voting). After
wiring the deployer keeps no privileges — **no one moves funds alone** (art. 1–2).
On a real deploy the `guardian`/`verifier` roles are supplied via the
`GUARDIAN_ADDRESS`/`VERIFIER_ADDRESS` environment variables; locally test signers
are used.

## Run (locally, no network, no money)

```bash
cd contracts
npm install          # once
npm test             # compile + all tests on the built-in Hardhat network
npm run deploy:local # deploy and wire the whole contour on the in-process network (demo)
```

CI runs the tests on every push/PR ([`.github/workflows/contracts.yml`](../.github/workflows/contracts.yml)).
The integration scenario "request → vote → Timelock → targeted payout to the
provider" is covered in [`test/Integration.test.js`](test/Integration.test.js) (via `Disbursement`).

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
- ✅ `Governor` + `Timelock` — direct voting with a mandatory execution delay
  ([`GOVERNANCE.md`](../docs/en/GOVERNANCE.md) §4–§7); vote weight from `Reputation.votingUnits`;
  the `Timelock` is set as the `executor` of `Treasury`/`Disbursement` — **done** (skeleton + tests).
- ✅ **Wiring the whole contour (part 3c):** the [`scripts/deploy.js`](scripts/deploy.js)
  script deploys and links all contracts (Reputation→Timelock→Treasury/Disbursement→Governor,
  role wiring, `renounceAdmin`) + an integration scenario "request → vote → Timelock →
  targeted payout to the provider" in [`test/Integration.test.js`](test/Integration.test.js) — **done**.
- **Part 4:** a public testnet run (e.g. Polygon Amoy) — once the network, RPC and
  test guardian addresses are agreed with the operator (keys via `contracts/.env`).
