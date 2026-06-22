[Русский](../PROOF-OF-CONTRIBUTION.md) · [English]

# HOW THE FUND CREATES PAID WORK — and honestly checks it was done

> This document explains how the fund **creates honest paid work around helping
> people** and how it **provably confirms that the work was actually done** before
> paying for it.
>
> Plain words first, technical details for developers below.
>
> The document rests on [`CONSTITUTION.md`](CONSTITUTION.md) (Art. 5 "fair
> distribution", Art. 6 "reward for contribution", Art. 7 "abuse protection", Art. 9
> "the role of AI"), [`PRINCIPLES.md`](PRINCIPLES.md) (what the fund cannot promise)
> and [`ANTI-ABUSE.md`](ANTI-ABUSE.md) (protection against deception). Closely linked
> to [`REWARDS-MODEL.md`](REWARDS-MODEL.md) (where the reward size comes from),
> [`ESCROW-TARGETED-DISBURSEMENT.md`](ESCROW-TARGETED-DISBURSEMENT.md) (the same
> mechanic of freezing money for a task, only for aid to those in need) and
> [`GOVERNANCE.md`](GOVERNANCE.md) (who checks the work and who changes the settings).
>
> This is a description of the rules for future reward smart contracts (Stage 5) and
> for the "Fairness", "Audit", "Reputation" AI helpers (Stage 6). The document itself
> moves no funds.
>
> Registered as a decision in the public registry:
> [`governance/registry/`](../../governance/registry/) (record `PTD-0039`).
>
> **About safety.** Everything below works for now **only on a test network and in
> calculations** — with no real money. The fund will distribute real money for such
> tasks only after an independent code review, separate consent, and under a shared
> wallet where any payout needs signatures from at least 3 of 5 living stewards
> (Article 4.4). We start with small amounts and strict checks, and trust and sizes
> grow gradually.

---

## The main idea — in plain words

The main idea in one line:

> **The fund does not only hand out aid — it creates honest work around that aid.
> Work is paid, but not on word.**

Helping people **creates work** in itself: someone has to review the request, arrange
things with a provider, drive a delivery, repair, write the intake code, mediate a
dispute, reconcile a report. This work can be **paid** — and then the fund becomes a
source of honest jobs inside a public good, not just a handout. Someone helped
yesterday can perform a paid task for the fund tomorrow — which is exactly growing
self-reliance.

But the moment work is paid, the key trust question appears:

> **How do we make sure the work was actually done in real life before paying for it?**

The fund handles it like this:

1. **The money is set aside for the task in advance.** When a person is given work,
   the reward is reserved and frozen at once. The worker sees the money really exists
   and is set aside for their task — this is not "we promise to pay someday later".
   And the fund sees the money will not move without confirmation.
2. **To receive it, you must prove the work was done — not on word.** You need a
   confirmation from the person the work was done **for**, traces of the work (photos,
   receipts, documents — visible as a "fingerprint" but not published), and a check by
   several independent people.
3. **The reviewers risk something of their own.** Whoever approved the work puts their
   good name on the line: miss a fraud and you lose trust (and part of your future
   opportunities). This turns "ticking the box without looking" into a real risk.
4. **There is time to challenge any payout.** After the check there is a period in
   which anyone can challenge the payout with a reason. Disputes are settled by people,
   not a machine.
5. **Everything is in the open.** Anyone can recompute who got paid, for what, and how
   much. Every payout is recorded in the open journal and matches the blockchain record.
6. **Aid first, reward second.** Aid to those in need always outranks paying for work —
   a salary does not queue ahead of need.

And honestly: **a machine cannot verify the real world 100%.** So we do not pretend to
have a "perfect truth detector". We build protection around this weakness: many
independent signals at once, reputation as a stake of honesty, a start with small
amounts and strict checks. Details in "Honest about the weak spot".

---

## What counts as "work"

Every paid job is framed as a **task with clear acceptance terms** — no "we'll pay if
we like it". Two formats:

| Format | What it is | When used |
|---|---|---|
| **One-off task** (developer term — *bounty*) | one task with a pre-announced reward range and clear "done" terms | discrete work: repair, transport, translate a document, close a code issue |
| **Staged work** (*milestone*) | large work split into stages; the reward is split per stage | long-running: developing a module, operationally running a direction |

The task's path in short: a task is **published** with acceptance terms and a reward
range from [`REWARDS-MODEL.md`](REWARDS-MODEL.md) → a worker is **assigned** → at that
moment the money is **frozen** for the task (reserved, but paid to no one yet) → the
worker submits the result with evidence → the result is **checked** → the money is
**unlocked** only when the payout condition is met (see "When the money is unlocked").

## Proof of completion — three pillars, not "on word"

The fact of completion is confirmed by a **combination** of evidence. The more money
and the closer the work is to real life (rather than a screen), the more pillars are
required.

**Pillar 1. Confirmation from the person the work was done for.** If the work was done
**for a specific person** (delivered medicine, helped with a move), the fact is
confirmed by the one **for whom** it was done: they confirm "yes, this was done for
me". Those without their own wallet confirm via a trusted coordinator. This is a
**two-sided** fact: the worker said "done" and the recipient confirmed "received". One
side alone is not enough.

**Pillar 2. Traces of the work (fingerprint in the open journal, file private).**
Documents, photos, receipts, acts stay **private**, but their **"fingerprint"** goes
into the open journal. That makes it provable that a document existed and was unchanged
— while personal data and photos are not published (privacy, Article 3).

**Pillar 3. Automatic verification (for digital work).** If the work is digital and a
machine can check it, the proof is **automatic and objective**: for code these are
accepted changes and green automatic checks (as in this very repository); for a
computation or report — a script whose result anyone can recompute. Here the question
"was it really done" is almost absent — a machine checks a machine. So it is sensible
for the fund's first paid tasks to be exactly the digital/verifiable kind.

## Who checks the work and how

The evidence is **checked by people and AI together** — and the reviewers **risk their
reputation**.

**Several independent people check (no one alone):**

- the result is confirmed by **at least two independent reviewers** (the number is a
  governed setting, [`REWARDS-MODEL.md`](REWARDS-MODEL.md));
- a reviewer **cannot** check their own work and cannot approve their own reward
  (Article 7, [`ANTI-ABUSE.md`](ANTI-ABUSE.md));
- protection against rigging and fake accounts: both the worker and the reviewers hold
  a **personal, non-transferable participant badge** (one person = one badge,
  [`GOVERNANCE.md`](GOVERNANCE.md)), so one person cannot play both the worker and all
  the reviewers.

**A reviewer puts their reputation at stake.** By approving work, a reviewer puts their
good name on the line. If it later surfaces that they let fraud through, **they lose
reputation** (and with it part of their future opportunities and trust weight).
Reputation **cannot be bought** and cannot be transferred; it is an auxiliary mark of
honesty, not power over money.

**AI counts and signals, but does not decide (Article 9).** The "Fairness" AI helper
recomputes the reward by the rules and checks that the safeguards hold (range, limits,
number of reviewers, the dispute period). The "Audit" AI helper reconciles that the
payout has a record in the open journal and that it matches the blockchain. Suspicious
repetitions (the same worker with the same recipient, spikes, templated confirmations)
the AI **flags as a signal** for stronger manual review — but it **pays nothing and
blocks nothing itself**.

**A dispute period and the right of appeal.** After the check there is a **period in
which anyone can challenge the payout**, attaching a reason. A dispute goes to
transparent mediation ([`../../governance/mediation/`](../../governance/mediation/),
[`ANTI-ABUSE.md`](ANTI-ABUSE.md)); people decide, not the AI and not one person. Any
rejection also has an appeal.

## When the money is unlocked

The frozen reward goes to the worker **only when all three** conditions hold at once:

1. the fact of work is **confirmed** (the applicable pillars above: for work "for a
   person", the recipient's confirmation is mandatory; for digital work, the automatic
   check);
2. it is approved by **at least two independent reviewers**;
3. the **dispute period has expired** with no active dispute.

If even one is missing, there is no payout. If the work was not confirmed or the
deadline passed, the reward **returns to the common pool** — it is not lost and does
not move outside the rules. Any movement of money is recorded in the open journal and
matches the blockchain — the payout can be recomputed and reproduced.

## How we defend against deception

| Threat | Defense |
|---|---|
| **Collusion "confirming one's own work"** | protection against fake accounts (one person = one badge); worker ≠ reviewer ≠ recipient; tracking of suspicious "worker ↔ recipient" repeats |
| **Fictitious work** | recipient confirmation + traces of the work (fingerprint) + at least two independent reviewers; for digital work — automatic verification |
| **A reviewer "rubber-stamps" approvals** | the reviewer **stakes reputation**: fraud let through → loss of trust |
| **Inflating volumes** | per-worker/period limits ([`ANTI-ABUSE.md`](ANTI-ABUSE.md)); excess → stronger review; the reward is from a range, not unbounded |
| **Buying influence** | reputation cannot be bought or transferred; in voting, one person = one vote ([`GOVERNANCE.md`](GOVERNANCE.md)) |
| **Quiet reviewer collusion** | **random spot re-checks** of a share of payouts by an independent review; the dispute period is open to all |
| **Need queued behind salaries** | by the constitution, aid to those in need **always outranks** reward for work ([`REWARDS-MODEL.md`](REWARDS-MODEL.md)) |

## Honest about the weak spot

We do not claim real life can be verified by a machine 100%. **It cannot.** Any system
that pays for off-chain work ultimately relies on confirmation by people, and that can
be faked by collusion. (Developers call this the "oracle problem": the blockchain
reliably executes rules but does not itself see whether the medicine really reached the
grandmother or whether the report is truthful.)

Our bet is not a "perfect truth detector" but **many pillars at once plus an economy of
honesty**:

- a **combination** of independent signals (recipient confirmation + independent
  reviewers + traces of the work + tracking of repeats) — you would have to fool all of
  them at once;
- **reputation as a stake**: lies and negligence cost a reviewer their good name, while
  honesty accumulates it (reputation is a multiplier on future opportunities, not money);
- **starting with small amounts and strict checks**, easing only as trust grows for a
  participant and direction;
- **verifiable (digital) work first**, where this problem is almost absent, and adding
  real-world tasks cautiously;
- **everything in the open**: every payout is reproducible from the journal and
  blockchain; random audits and an open dispute period make collusion risky and visible.

This does not remove the risk entirely — but it makes deception expensive, slow, and
visible, and honest participation profitable and simple.

## What is open and what stays private

| Open (blockchain / journal) | Private (never public) |
|---|---|
| Task number, acceptance terms, reward range | — |
| Pseudonymous worker/case number | Name, contacts, identity of worker and recipient |
| Fact of recipient confirmation | The recipient's personal data and history |
| **Fingerprint** of the work's traces (documents/photos/receipts) | The files themselves (stay private) |
| Reviewers' votes and their reputation stakes | — |
| Amount, status, date | — |

What is verifiable is **the work and its payment**, not people's identities (Article 3,
privacy).

## How to explain this to people

> The fund does not only hand out aid — it **creates honest work** around that aid.
> Work is paid, but **not on word**: the money is set aside for the task in advance,
> and to receive it you must prove the work was done — through confirmation by the one
> it was done for, photos and receipts (visible as a "fingerprint" but not published),
> and a check by several independent people. The reviewers **risk their reputation**:
> miss a fraud and you lose trust. There is time to challenge any payout. And all of it
> is in the open: anyone can recompute who got paid, for what, and how much. We admit
> honestly: a machine cannot verify the real world 100% — so we start small and strict,
> and trust and amounts grow gradually.

## Open questions for the operator

- **Who grants the reviewer role** and by what procedure (an initial set of reviewers
  until full decentralization)?
- Is an **external coordinator/partner** needed to confirm work for those recipients
  who have no wallet (as in the third payment method in
  [`ESCROW-TARGETED-DISBURSEMENT.md`](ESCROW-TARGETED-DISBURSEMENT.md))?
- Starting values: how many reviewers are needed, the dispute-period length, the share
  of random re-checks, starting amount limits. Until real money enters, this is set on
  the test network and approved by vote.

See also the "OPERATOR INPUT NEEDED" section in [`../../PROGRESS.md`](../../PROGRESS.md).

---

## Technical section — for developers

Below is the formal part for those who will write the contracts and AI helpers:
terminology, the task's path step by step (state machine), the exact payout condition,
and a sketch of the contract interface. All of this is a statement of intent for the
**test network**, not a final contract. The AI helpers here only count and reconcile,
they do not decide (Article 9).

### Terminology (plain word → technical term)

| In the text above | Technical term |
|---|---|
| One-off task | bounty |
| Staged work | milestone |
| Money frozen for the task | escrow (lock) |
| Payout condition | release condition |
| Protection against rigging and fake accounts | anti-Sybil (Sybil-resistance) |
| Personal, non-transferable participant badge | soulbound badge (`votingUnits=1`/person) |
| A reviewer stakes reputation | skin in the game |
| Dispute period | dispute window |
| Emergency stop | circuit breaker / `pause()` |
| How a contract learns about the real world | the oracle problem |
| File fingerprint | hash (IPFS manifest, [`../../governance/ipfs/`](../../governance/ipfs/)) |

### Contribution lifecycle (state machine)

```
   OPEN ──► ASSIGNED ──► SUBMITTED ──► UNDER_REVIEW ──► VALIDATED ──► DISPUTE_WINDOW ──► RELEASED → (to worker)
   (task     (reward      (result +      (≥N            (evidence       (open window       (payout once
    pub-      locked in    evidence       validators     accepted)       to challenge)      window expires)
    lished)   escrow)      submitted)     + Fairness/        │                │
                  │             │           Audit AI)        │                ▼
                  ▼             ▼              │             ▼            DISPUTED ──► MEDIATION
              CANCELLED      EXPIRED        REJECTED ─────────┴──────────────┘            │
            (pulled before  (deadline    (not confirmed → reward                          ▼
             submission)     passed)      returns to the pool)                      UPHELD / REVERSED
                  │             │                                                (payout confirmed /
                  ▼             ▼                                                 reversed, validators'
            reward returns to the W pool                                          reputation recomputed)
```

- **OPEN** — a task with acceptance criteria and a reward range is published.
- **ASSIGNED** — a worker is assigned, the reward is **locked** in escrow.
- **SUBMITTED** — the result is submitted with evidence (three pillars above).
- **UNDER_REVIEW** — collective review + Fairness/Audit AI (signal anomalies).
- **VALIDATED** — ≥N independent validators confirmed (staking reputation).
- **DISPUTE_WINDOW** — an open window to challenge.
- **RELEASED** — once the window passes without a dispute, escrow pays the worker; a
  public event is emitted, a record goes to the registry.
- **DISPUTED → MEDIATION → UPHELD/REVERSED** — transparent dispute resolution.
- **REJECTED / EXPIRED / CANCELLED** — the reward **returns to the pool**, it is not
  "lost" and does not move outside the rules.

### Release condition

```
release  ⟺  (fact confirmed)  ∧  (≥ N independent validators)  ∧  (dispute window expired with no active dispute)
```

where **fact confirmed** is the applicable set of pillars (for work "for a person",
Pillar 1 — the recipient's signature — is mandatory; for digital work — Pillar 3). Any
movement of funds **emits an event** and **enters the registry** — the payout can be
recomputed and reproduced (Art. 3). Failing any of the three conditions leaves the
payout locked; on timeout the reward returns to the pool.

### Contract interface sketch (Solidity pseudocode, for TESTNET)

The same role model as [`Treasury.sol`](../../contracts/contracts/Treasury.sol) and
[`Disbursement.sol`](../../contracts/contracts/Disbursement.sol): only `executor`
= Timelock moves funds, `guardian` only pauses.

```solidity
// Pseudocode — a statement of intent, not the final contract.
interface IContributionEscrow {
    // Publish a task with criteria and a reward range (W from REWARDS-MODEL).
    function openTask(bytes32 taskId, uint256 rewardMin, uint256 rewardMax, bytes32 criteriaHash) external;

    // Assign a worker and LOCK the reward in escrow.
    function assign(bytes32 taskId, address worker, uint256 lockedReward) external;

    // Submit the result: artifact hashes (files private), reference to evidence.
    function submit(bytes32 taskId, bytes32[] calldata artifactHashes) external;

    // Confirmation by the aid recipient (two-sided fact) — signature/coordinator.
    function confirmByRecipient(bytes32 taskId) external;

    // A validator confirms AND STAKES reputation (loses it on fraud let through).
    function validate(bytes32 taskId, bool approve) external; // records the reputation stake

    // Open/raise a dispute within the dispute window.
    function dispute(bytes32 taskId, bytes32 reasonHash) external;

    // Unlock the payout ONLY when the release condition holds.
    function release(bytes32 taskId) external; // emits Released(taskId, worker, amount)

    // Return the reward to the pool if the work is unconfirmed / the deadline passed.
    function refundToPool(bytes32 taskId) external;

    // Emergency pause under collective control (circuit breaker).
    function pause() external;
}
```

Implementation requirements (from [`ANTI-ABUSE.md`](ANTI-ABUSE.md) and
[`REWARDS-MODEL.md`](REWARDS-MODEL.md)):

- `release` executes **only** when `confirm ∧ (validators ≥ N) ∧ (dispute window
  expired)`; no single address unlocks a payout alone.
- A worker cannot validate their own task; a validator does not approve their own
  reward.
- The reward size comes from the [`REWARDS-MODEL.md`](REWARDS-MODEL.md) range
  (stream W); reputation is only a multiplier and does not break the ceiling.
- All branches (`assign`/`submit`/`validate`/`release`/`refund`/`pause`/`dispute`)
  emit public events; the registry and on-chain match.
- Extend the registry schema with task/contribution fields (`task_id`, `worker`,
  `validators`, `artifact_hashes`, `dispute_window`) so the record and on-chain agree
  (as done for `disbursement.schema.json`).
- Full test coverage + a testnet run (Polygon Amoy, see LAUNCH.md) "to green". No
  mainnet/real funds without an audit and the operator's approval.

---

See also: [`REWARDS-MODEL.md`](REWARDS-MODEL.md) ·
[`ESCROW-TARGETED-DISBURSEMENT.md`](ESCROW-TARGETED-DISBURSEMENT.md) ·
[`ANTI-ABUSE.md`](ANTI-ABUSE.md) · [`GOVERNANCE.md`](GOVERNANCE.md) ·
[`PRIORITIES.md`](PRIORITIES.md) · [`CONSTITUTION.md`](CONSTITUTION.md)
