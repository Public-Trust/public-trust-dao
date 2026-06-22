[Русский](README.md) · [English]

# Safe Multisig — community test treasury (3-of-5)

> A blueprint and "ready-to-press" guide for the community's shared wallet on
> **testnet**. It implements the constitutional principle **"no one controls funds
> single-handedly"** ([`CONSTITUTION.md`](../../docs/en/CONSTITUTION.md) art. 2.4,
> prohibition #5) in the open, **with no real money and no private keys in the
> repository**.
>
> Part of Stage 4 (Governance). The multisig's role is **executor / emergency
> pause, not ruler** (see [`docs/GOVERNANCE.md`](../../docs/en/GOVERNANCE.md) §5).

---

## 0. What this is and is NOT

| It is | It is NOT |
|---|---|
| A testnet Safe to exercise shared-treasury mechanics | A real treasury with real money |
| A 3-of-5 scheme of living guardians: 3 signatures for any operation | A wallet under single control (human or AI) |
| Addresses public and verifiable on the block explorer | A store of private keys / seed phrases (none in the repo, ever) |
| Executor of the vote's will + emergency pause | A body deciding "who gets how much" (voting decides that) |

**The real treasury is a separate Safe and only after** an independent contract
audit + an explicit separate approval + a live guardian multisig
([`CONSTITUTION.md`](../../docs/en/CONSTITUTION.md) art. 4.4). The agent never
crosses this threshold.

## 1. Why a shared wallet already on testnet

So the mechanism "shared funds move only collectively" is **visible and verifiable
in the open** before any real funds exist. Anyone can open a block explorer and
confirm: the treasury has no single owner, any operation needs 3 of 5 independent
signatures, and the operation history is public. This is the transparency from
[`PRINCIPLES.md`](../../docs/en/PRINCIPLES.md) — not as words, but verifiable
on-chain.

## 2. Parameters (see also `safe.config.json`)

- **Network:** Polygon **Amoy testnet** (`chain_id = 80002`), explorer
  `amoy.polygonscan.com`. (LAUNCH.md proposes Amoy as the test network;
  alternative — Ethereum **Sepolia** `11155111`.)
- **Signing scheme:** **3 of 5** (`threshold = 3`, `owners = 5`).
- **Safe version:** 1.4.1 (current at the time of writing).
- **Real funds:** none. Only test tokens from a faucet.

Why 3-of-5:

- **No single control** — one person (or one compromised key) cannot move funds.
- **Survives loss of up to 2 keys** — the remaining 3 guardians keep access and can
  replace a lost owner. The wallet does not "die" from a single loss.
- **Strict majority** — 3 of 5 is >50%, so a minority can neither block nor capture
  the treasury. (The validator enforces this rule, see §6.)

## 3. Guardian roles and policy

Filled in by the operator (addresses come from real people). Template lives in
`safe.config.json` → `owners_template`:

| Role | Who | Address (0x…) |
|---|---|---|
| guardian-1 | Guardian 1 | _awaiting operator_ |
| guardian-2 | Guardian 2 | _awaiting operator_ |
| guardian-3 | Guardian 3 | _awaiting operator_ |
| guardian-4 | Guardian 4 | _awaiting operator_ |
| guardian-5 | Guardian 5 | _awaiting operator_ |

- **Guardian = ordinary participant** (art. 2.2): one vote, like everyone. The role
  is technical insurance for the treasury, not a privilege in distributing aid.
- **What the multisig can / cannot do** — strictly per
  [`docs/GOVERNANCE.md`](../../docs/en/GOVERNANCE.md) §5: execute an **already-passed**
  vote and trigger an **emergency pause**; it must NOT spend without a vote, NOT
  decide who gets aid, NOT change parameters bypassing the Governor.
- **The emergency pause only halts**, it does not direct funds, and every use is
  logged in the public registry [`../registry`](../registry).

## 4. Key hygiene (rails)

- Each guardian keeps **their own** private key to themselves. A hardware wallet
  (Ledger/Trezor) is recommended **even for testnet** — to build the right habit
  before real funds.
- **Private keys and seed phrases NEVER** enter the repository, are never shared in
  chats, and are never stored in plaintext in the cloud. The repo holds **only
  public addresses** (`0x…`).
- Any secret (provider RPC key, etc.) goes in `.env` (which is in `.gitignore`),
  not in code. A test network is no excuse for bad habits.

## 5. Operator guide — create the test Safe "ready-to-press"

The agent does not create external wallets itself (it needs a browser wallet,
transaction signing, a faucet) — the operator does. Steps:

1. **Guardian wallets.** Each of the 5 guardians creates an address in a browser
   wallet (e.g. MetaMask) and switches to the **Polygon Amoy** network. They share
   only **public addresses** `0x…` with each other.
2. **Test funds.** One address gets a little test POL from the Amoy faucet — to pay
   gas for Safe creation. No real money needed.
3. **Create the Safe.** Open [app.safe.global](https://app.safe.global), network =
   Polygon Amoy, "Create new Safe" → add the **5** guardian addresses → threshold
   **3 of 5** → confirm the deployment transaction.
4. **Record the address.** Copy the resulting Safe address (`0x…`) and the 5 owner
   addresses and send them via `comms/INBOX.md` (or fill them in directly). These
   are **public** data — exactly what should be open.
5. **The agent will fill in the addresses** in `safe.config.json` (`status` →
   `deployed-testnet`, `safe.address`, `safe.owners`, addresses in
   `owners_template`), run the validator (§6), add a link to the Safe on the block
   explorer to the site/README, and register a registry entry. All verifiable.

> A future alternative for CI/reproducibility — deploy the Safe via script (Safe
> SDK / protocol-kit) from a test deploy key in `.env`. For now we keep the
> "via app.safe.global" path, since it requires no keys in the environment and is
> more transparent.

## 6. Config check (rail validator)

`safe.config.json` is checked by a dependency-free script that fails the build on
any rail violation:

```bash
python3 scripts/safe_config.py verify
```

It checks: the schema (`schema/safe-config.schema.json`); **testnet only**
(`is_testnet=true`, `chain_id` from a testnet allow-list, rejects mainnet networks);
the **3-of-5** scheme and strict majority; address validity; that owners are either
fully filled or the config is an empty draft; and crucially — that **the config
contains no private keys / seed phrases / secrets** (it catches 64-hex strings and
the words `private key`/`mnemonic`/`seed`). CI
([`.github/workflows/safe.yml`](../../.github/workflows/safe.yml)) runs this check
on every push.

## 7. Relation to the plan

- **Stage 4 (Governance):** this blueprint + [`docs/GOVERNANCE.md`](../../docs/en/GOVERNANCE.md)
  (the model) + (next) `governance/snapshot/` (off-chain voting).
- **Stage 5 (Contracts):** the Safe becomes the executor/emergency-pause for
  Governor→Timelock→Treasury; treasury contracts are written and tested at that stage.
- **Donations / support:** per the operator's clarification, support comes **from
  the working system itself**, not from a separate button/address on the side —
  donations will flow through this community multisig treasury + contracts, and each
  will be visible in the public registry. The real address is published **only**
  once it is protected by the guardian multisig (ideally after an audit). Until the
  system launches we publish no real-money address (see the INBOX "project support /
  donations" item).

## NEEDED FROM THE OPERATOR

- **The 5 guardian addresses** (`0x…`, public) and a decision on the test network
  (Amoy by default). After that the agent will create/fill in the deployment and
  register it.
- Creating the Safe itself at [app.safe.global](https://app.safe.global) (requires
  a browser wallet and signing) — steps in §5.

---

> This is a public good, **not an investment** and **not a pyramid**. The shared
> wallet exists so that **no one disposes of funds single-handedly** and every
> operation is visible. Real money — only after an audit and explicit approval.

Related: [`docs/GOVERNANCE.md`](../../docs/en/GOVERNANCE.md) ·
[`docs/CONSTITUTION.md`](../../docs/en/CONSTITUTION.md) ·
[`docs/ANTI-ABUSE.md`](../../docs/en/ANTI-ABUSE.md) ·
[`governance/registry`](../registry) · [`safe.config.json`](safe.config.json)
