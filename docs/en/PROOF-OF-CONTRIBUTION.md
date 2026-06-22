[Русский](../PROOF-OF-CONTRIBUTION.md) · [English]

# PROOF OF CONTRIBUTION AND ESCROW CONTRACTS — PUBLIC TRUST DAO

> Normative design document. It describes how the fund **creates paid work through
> helping people** and how it **provably confirms that the work was done** before
> unlocking a reward. Derived from [`CONSTITUTION.md`](CONSTITUTION.md) (Art. 5
> "fair distribution", Art. 6 "reward for contribution", Art. 7 "abuse protection",
> Art. 9 "the role of AI"), [`PRINCIPLES.md`](PRINCIPLES.md) (constitutional
> prohibitions), [`ANTI-ABUSE.md`](ANTI-ABUSE.md). Closely linked to
> [`REWARDS-MODEL.md`](REWARDS-MODEL.md) (where the reward size comes from),
> [`ESCROW-TARGETED-DISBURSEMENT.md`](ESCROW-TARGETED-DISBURSEMENT.md) (the same
> escrow mechanics for aid to those in need) and [`GOVERNANCE.md`](GOVERNANCE.md)
> (who validates and who changes parameters).
>
> This is a **specification** for the reward/escrow smart contracts (Stage 5) and
> for the Fairness / Audit / Reputation AI (Stage 6). The document itself moves no
> funds.
>
> Registered as a decision in the public registry:
> [`governance/registry/`](../../governance/registry/) (record `PTD-0039`).
>
> **Safety rail.** Everything below is **on testnet and in calculations**. Real
> funds enter escrow only after an independent audit, explicit approval, and under
> a 3-of-5 live-steward Safe multisig (Art. 4.4). We start with small amounts and
> strict checks, and scale as trust accumulates.

---

## 0. Vision: work is born from helping

The fund is not just a cashbox for those in need. Helping people **creates work**
in itself: someone has to review the request, arrange things with a provider, drive
the delivery, repair, write the intake code, mediate a dispute, reconcile a report.
This work can be **paid** — and then the fund becomes a source of honest jobs inside
a public good, not merely a handout. Someone helped yesterday can perform a paid task
for the fund tomorrow — which is exactly growing self-reliance (Art. 5.2).

But the moment work is paid, a **central trust problem** appears:

> **How does a contract become sure the work was actually done in the real world
> before it pays?**

This is the classic **oracle problem**: the blockchain does not "see" the real
world. It reliably stores and executes rules, but it does not by itself know whether
the medicine really reached the grandmother, whether the apartment was really
cleaned, whether the report is truthful. A bridge is needed between the "real fact"
and the "on-chain payout", and that bridge is the most vulnerable spot of any such
system. We do not hide this weakness — we build protection around it (Section 7).

## 1. Anatomy of a contribution (what "work" means here)

Every paid job is framed as a **task with acceptance criteria** — no "we'll pay if
we like it". Two formats:

| Format | What it is | When used |
|---|---|---|
| **Bounty** | a one-off task with a fixed reward range and clear "done" criteria | discrete work: repair, transport, translate a document, close an issue |
| **Milestone** | large work split into stages; the reward is split per stage | long-running: developing a module, operationally running a direction |

Life path: a task is **published** with acceptance criteria and a reward range from
[`REWARDS-MODEL.md`](REWARDS-MODEL.md) (stream **W**) → a worker is **assigned** → at
that moment the escrow contract **locks** the reward (reserved, but paid to no one
yet) → the worker submits the result with evidence → validation runs → the contract
**unlocks** the payout only when the release condition is met (Section 5).

Locking the reward at assignment matters: the worker sees the money really exists
and is reserved for their task (no "we promise to pay later"), and the fund sees the
funds will not move without confirmation.

## 2. Proof of execution — three layers, not "on word"

The fact of completion is confirmed by a **combination** of evidence. The more money
and the closer the work is to the real (off-chain) world, the more layers are required.

### Layer 1. Two-sided confirmation (recipient's signature)

If the work is done **for a specific person** (delivered medicine, helped with a
move), the fact is confirmed by the one **for whom** it was done:

- the aid recipient **signs** a confirmation ("yes, this was done for me") — a wallet
  signature, or confirmation via a trusted coordinator / partner multisig for those
  without a wallet;
- this is a **two-sided** fact: the worker claimed "done" and the recipient confirmed
  "received". One side alone is not enough.

### Layer 2. Artifacts (hash in IPFS, file private)

Verifiable traces of the work:

- documents/photos/receipts/acts are **hashed**, the hash goes into the IPFS manifest
  ([`../../governance/ipfs/`](../../governance/ipfs/)) and into the registry record;
  **the file itself stays private**, only its fingerprint is public;
- this enforces privacy (Art. 3): provable that an artifact existed and was unchanged,
  while personal data and photos are not published.

### Layer 3. Automatic verification (for on-chain work)

If the work is digital and machine-checkable, the proof is **automatic and
objective**:

- code: a merged pull request + green tests/CI (as in this very repository —
  `.github/workflows/`); the merge and passing checks are visible to all;
- computation/report: a reproducible script whose result anyone can recompute.

Here the oracle problem is almost absent — a machine checks a machine. So it is
sensible for the fund's first paid tasks to be exactly the digital/verifiable kind.

## 3. Validation: collective review + AI + reputation at stake

The evidence from Section 2 is **checked by people and AI together** — and the
reviewers **risk their reputation**.

**Collective review (no one alone):**

- the result is confirmed by **≥ N independent validators** (default N ≥ 2, a
  governed parameter, [`REWARDS-MODEL.md`](REWARDS-MODEL.md) §5.1);
- a validator **cannot** review their own work and cannot approve their own reward
  (Art. 7, [`ANTI-ABUSE.md`](ANTI-ABUSE.md));
- anti-Sybil: both the worker and the validators hold a non-transferable soulbound
  badge (`votingUnits=1` per person, [`GOVERNANCE.md`](GOVERNANCE.md) §2–§3); one
  person cannot play both the worker and all the reviewers.

**Validators STAKE reputation (skin in the game):**

- by approving work, a validator puts their reputation on the line; if it later
  surfaces that they let fraud through, **they lose reputation** (and with it the
  multiplier on future rewards and their trust weight). This turns "rubber-stamping"
  into a real risk;
- reputation here is an **auxiliary** honesty tool: it **cannot be bought** and
  cannot be transferred, it is only a multiplier (see
  [`Reputation.sol`](../../contracts/contracts/Reputation.sol) and
  [`REWARDS-MODEL.md`](REWARDS-MODEL.md) §3.2), not a right to vote with money.

**The role of AI (it counts and signals, it does not decide — Art. 9):**

- **Fairness AI** ([`../../ai-agents/fairness_agent.py`](../../ai-agents/fairness_agent.py))
  recomputes the reward per [`REWARDS-MODEL.md`](REWARDS-MODEL.md) and checks the
  safeguards (range, limits, ≥N validators, dispute window);
- **Audit AI** ([`../../ai-agents/audit_agent.py`](../../ai-agents/audit_agent.py))
  reconciles that the payout has a registry record and matches an on-chain event;
- **anomaly detection**: repeating pairs "same worker ↔ same recipient", spikes,
  templated confirmations are flagged as a **signal** for stronger manual review, but
  the AI **itself pays nothing and blocks nothing**.

**Dispute window and appeal:**

- after validation a **dispute window** opens: within a set period any member may
  challenge the payout, attaching a reason;
- a dispute goes to transparent mediation ([`../../governance/mediation/`](../../governance/mediation/),
  [`ANTI-ABUSE.md`](ANTI-ABUSE.md)); people decide, not the AI and not one person;
- any rejection/sanction also has an appeal.

## 4. Contribution lifecycle (state machine)

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
- **SUBMITTED** — the result is submitted with evidence (Section 2).
- **UNDER_REVIEW** — collective review + Fairness/Audit AI (signal anomalies).
- **VALIDATED** — ≥N independent validators confirmed (staking reputation).
- **DISPUTE_WINDOW** — an open window to challenge.
- **RELEASED** — once the window passes without a dispute, escrow pays the worker; a
  public event is emitted, a record goes to the registry.
- **DISPUTED → MEDIATION → UPHELD/REVERSED** — transparent dispute resolution.
- **REJECTED / EXPIRED / CANCELLED** — the reward **returns to the pool**, it is not
  "lost" and does not move outside the rules.

## 5. Release condition

Escrow unlocks the payout to the worker **only** when all of the following hold
simultaneously:

```
release  ⟺  (fact confirmed)  ∧  (≥ N independent validators)  ∧  (dispute window expired with no active dispute)
```

where **fact confirmed** is the applicable set of layers from Section 2 (for work
"for a person" Layer 1 — the recipient's signature — is mandatory; for digital work —
Layer 3). Any movement of funds **emits an event** and **enters the registry** — the
payout can be recomputed and reproduced (Art. 3). Failing any of the three conditions
leaves the payout locked; on timeout the reward returns to the pool.

## 6. Anti-fraud: how we defend against deception

| Threat | Defense |
|---|---|
| **Collusion "volunteer = needy"** (confirming one's own work) | anti-Sybil (soulbound badge, 1 person = 1 badge); worker ≠ validator ≠ recipient; detection of repeating worker↔recipient pairs |
| **Fictitious work** | two-sided confirmation + artifacts (hash) + ≥N independent validators; for digital work — auto-verification |
| **A validator "rubber-stamps" approvals** | the validator **stakes reputation**: fraud let through → loss of reputation/multiplier |
| **Inflating volumes** | per-worker/period limits ([`ANTI-ABUSE.md`](ANTI-ABUSE.md)); excess → stronger review; reward is from a range, not unbounded |
| **Buying influence** | reputation cannot be bought or transferred; vote weight is 1 person = 1 vote ([`GOVERNANCE.md`](GOVERNANCE.md)) |
| **Targeted validator collusion** | **random spot re-checks** of a share of payouts by an independent review; the dispute window is open to all |
| **Need queued behind salaries** | constitutional priority: aid to those in need (stream H) always outranks reward (stream W), ceiling `ρ_cap` ([`REWARDS-MODEL.md`](REWARDS-MODEL.md) §2) |

## 7. Honest about the weak spot (the oracle problem)

We do not claim the real world can be verified 100% automatically. **It cannot.** Any
system that pays for off-chain work ultimately relies on human confirmation, and that
can be faked by collusion. Our bet is not a "perfect truth detector" but a **layered
defense + an economy of honesty**:

- a **combination** of independent signals (recipient confirmation + independent
  validators + artifacts + anomaly detection) — you would have to fool all of them at
  once;
- an **economy of reputation**: lies and negligence cost a validator their reputation,
  while honesty accumulates it (reputation = a multiplier on future rewards, not money);
- **starting with small amounts and strict checks**, expanding limits and easing only
  **as trust accumulates** for a participant/direction;
- **prioritizing verifiable (digital) work** at the start, where the oracle problem is
  minimal, and adding off-chain tasks cautiously;
- **everything in the open**: every payout is reproducible from the registry and
  on-chain; random audits and an open dispute window make collusion risky and visible.

This does not remove the risk entirely — it makes deception expensive, slow, and
visible, and honest participation profitable and simple.

## 8. Privacy: what is public and what is not

| Public (on-chain / registry) | Private (never public) |
|---|---|
| Task ID, acceptance criteria, reward range | — |
| Pseudonymous worker / `case_id` identifier | Name, contacts, identity of worker and recipient |
| Fact of recipient confirmation (flag/signature) | The recipient's personal data and history |
| **Hash** of artifacts (documents/photos/receipts) | The artifacts themselves (files stay private) |
| Validators' votes and their reputation stakes | — |
| Amount, status, events, date | — |

What is verifiable is **the work and its payment**, not people's identities (Art. 3 +
privacy).

## 9. What this means for Stage 5 (contracts)

A sketch of the contribution-escrow interface (Solidity pseudocode, for TESTNET; the
same role model as [`Treasury.sol`](../../contracts/contracts/Treasury.sol) and
[`Disbursement.sol`](../../contracts/contracts/Disbursement.sol) — only `executor`
= Timelock moves funds, `guardian` only pauses):

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

    // Unlock the payout ONLY when the release condition holds (Section 5).
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

## 10. In plain words

> The fund does not only hand out aid — it **creates honest work** around that aid.
> Work is paid, but **not on word**: the money is set aside for the task in advance,
> and to receive it you must prove the work was done — through confirmation by the one
> it was done for, photos/receipts (visible as a "fingerprint" but not published), and
> a check by several independent people. The reviewers **risk their reputation**:
> miss a fraud and you lose trust. There is time to challenge any payout. And all of
> it is in the open: anyone can recompute who got paid, for what, and how much. We
> admit honestly: a machine cannot verify the real world 100% — so we start small and
> strict, and trust and amounts grow gradually.

## 11. Open questions for the operator

- **Who grants the validator role** and by what procedure (an initial set of reviewers
  until full decentralization)?
- Is an **off-chain coordinator/partner** needed to confirm work for those recipients
  who have no wallet (akin to Model C in
  [`ESCROW-TARGETED-DISBURSEMENT.md`](ESCROW-TARGETED-DISBURSEMENT.md))?
- Starting values: `N` (number of validators), dispute-window length, the share of
  random re-checks, starting amount limits. Until real funds enter, this is calibrated
  on testnet and approved by vote.

See also the "OPERATOR INPUT NEEDED" section in [`../../PROGRESS.md`](../../PROGRESS.md).

---

See also: [`REWARDS-MODEL.md`](REWARDS-MODEL.md) ·
[`ESCROW-TARGETED-DISBURSEMENT.md`](ESCROW-TARGETED-DISBURSEMENT.md) ·
[`ANTI-ABUSE.md`](ANTI-ABUSE.md) · [`GOVERNANCE.md`](GOVERNANCE.md) ·
[`PRIORITIES.md`](PRIORITIES.md) · [`CONSTITUTION.md`](CONSTITUTION.md)
