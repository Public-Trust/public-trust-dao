[Русский](../SUPPORT-MODEL.md) · [English]

# SUPPORTING THE PROJECT — PUBLIC TRUST DAO

> How the project receives support (donations). In short: **support comes from the
> working system itself, not from a separate button or a wallet address on the
> side.** Derived from [`PRINCIPLES.md`](PRINCIPLES.md),
> [`CONSTITUTION.md`](CONSTITUTION.md), [`GOVERNANCE.md`](GOVERNANCE.md) and
> [`ESCROW-TARGETED-DISBURSEMENT.md`](ESCROW-TARGETED-DISBURSEMENT.md).
>
> Registered as a decision in the public registry:
> [`governance/registry/`](../../governance/registry/) (record `PTD-0014`).
>
> **Safety rail.** Until the working system is live (contracts + a public
> multisig treasury 3-of-5 after an audit), the project **publishes no address for
> real money** and opens no separate fundraiser. TESTNET-first; real funds only
> after an independent audit and under a multisig of living guardians
> (Constitution Art. 4.4). No one controls funds single-handedly.

---

## 1. The principle: support is part of the system, not a button on the side

Many projects stick a "Donate" button on the side with a single wallet controlled
by one person or a small team. For a project about **public trust and
transparency** that is a contradiction: it amounts to "entrust your money to
people no one verifies."

So Public Trust DAO **does not create a separate "Support" section with a
bootstrap address**. Accepting support is a built-in part of the running DAO:

- donations flow through the **transparent public multisig treasury** (Safe 3-of-5,
  see [`../../governance/safe/`](../../governance/safe/)) and the treasury **smart
  contracts**;
- every inflow and every outflow is **visible in the public registry**
  ([`governance/registry/`](../../governance/registry/)) and on-chain;
- no one disposes of funds single-handedly — spending is executed only on a passed
  community vote (see [`GOVERNANCE.md`](GOVERNANCE.md)); the multisig merely
  executes the will of the vote and can hit an emergency pause.

In other words, "support the project" and "support those the project helps" are
**one and the same transparent flow** — not a separate cash box held by the team.

## 2. Why this way (mapping to the Constitution)

| Constitutional principle | How the support model implements it |
|---|---|
| No owner (Art. 1–2) | No private "team" wallet; funds sit in the shared multisig treasury, spending follows a vote. |
| Hide nothing (Art. 6) | Every inflow/outflow is on-chain and in the public registry, explained. |
| No yield promises, no pyramid (prohibitions) | Support is a gift to a public good, **not an investment**: a donor receives no share, yield, asset token or right of return. |
| No pay-to-recruit | No referral bonuses for "bring a donor"; support does not convert into power or a recruiting reward. |
| Real-funds latch (Art. 4.4) | Real money only after audit + multisig; until then no real-money address is published. |

## 3. What this means now (bootstrap/testnet stage)

- **No real-money address is published.** The system is not in production yet;
  publishing a wallet prematurely would create the very "button on the side" we
  rejected, plus the risk that funds end up under single-handed control before the
  latches are in place.
- **The best support right now is not money but a contribution to the
  infrastructure:** code, documentation, review/audit, ideas, public-benefit work.
  That directly moves the project toward launch (see "How to take part" on the site
  and in the README).
- **Once the system is live** (contracts on testnet → audit → public treasury under
  a Safe 3-of-5 of living guardians → community approval), support can be directed
  **into the open treasury**, visible in the registry like any other flow. Then —
  and only then — public addresses appear in the README and on the site, as a
  separate registry record.

## 4. What we do NOT do (rails)

- ❌ No "Donate/Support" button with a single wallet on the side.
- ❌ No bootstrap real-money address before the system launches and is audited.
- ❌ No promises of yield, share, asset token, return or any benefit to donors.
- ❌ No referral bonuses for recruiting donors.
- ❌ No accepting funds where one person or team controls them.
- ❌ No hidden inflow or outflow — everything is in the registry and on-chain.

## 5. In plain words

> "Supporting the project" here does not mean "send money to the team's wallet." It
> means putting a contribution (help now, or — once the system works — funds) into a
> **shared transparent fund**, where every unit is visible to everyone, where
> spending is decided by the community by vote rather than by one person, and where
> help reaches the person in need directly (see
> [`ESCROW-TARGETED-DISBURSEMENT.md`](ESCROW-TARGETED-DISBURSEMENT.md)). While the
> system is being built, the most valuable support is participation.

## 6. Link to the plan stages

- **Now (Stage 4):** the public multisig treasury is described and checked by a
  validator — [`../../governance/safe/`](../../governance/safe/). Guardian addresses
  and Safe deployment are the operator's.
- **Stage 5 (contracts):** treasury + accepting inflows + distribution by priority
  and staged payouts — on testnet, under tests, until green.
- **After the audit:** the public treasury moves under a Safe 3-of-5; support with
  funds becomes openly available, and public addresses are published as a separate
  registry record.

---

See also: [`GOVERNANCE.md`](GOVERNANCE.md) ·
[`ESCROW-TARGETED-DISBURSEMENT.md`](ESCROW-TARGETED-DISBURSEMENT.md) ·
[`ANTI-ABUSE.md`](ANTI-ABUSE.md) · [`../../governance/safe/`](../../governance/safe/) ·
[`PROMOTION.md`](PROMOTION.md)
