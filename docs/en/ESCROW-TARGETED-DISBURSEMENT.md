[Русский](../ESCROW-TARGETED-DISBURSEMENT.md) · [English]

# HOW THE FUND PAYS FOR NEED DIRECTLY — so that aid actually arrives

> This document explains **the core principle of aid: the fund does not hand out
> cash — it pays for the need directly to whoever provides the service** — the
> landlord, the pharmacy, the food supplier. That way there is no need to beg the
> person for receipts and proof afterwards: it is visible immediately and forever
> that the money went exactly toward housing, medicine or food.
>
> First in plain words, technical details for developers below.
>
> The document rests on [`CONSTITUTION.md`](CONSTITUTION.md) (articles 4, 5, 7),
> [`PRIORITIES.md`](PRIORITIES.md) (who we help first) and
> [`ANTI-ABUSE.md`](ANTI-ABUSE.md) (protection from fraud). It is a description of
> the rules for the future disbursement contracts (Stage 5) and for the "Audit",
> "Guardian" and "Fairness" AI helpers (Stage 6).
>
> **Important about safety.** Everything below works for now **only on a test
> network and on paper** — without real money. The fund will start distributing real
> funds only after an independent code review, separate consent and under a shared
> wallet where any payout needs the signatures of at least 3 of 5 living guardians
> (article 4.4).

---

## The main idea — in plain words

The core thought in one line:

> **We do not give money — we pay for the need. And anyone can verify it.**

Imagine a person needs to pay rent. We could give them the money and then ask
"bring a receipt, prove you spent it on housing". That is bad: a receipt is easy to
fake, constant checks humiliate the person, and the temptation to spend it elsewhere
does not go away.

The fund does it differently:

1. **The money goes straight to whoever provides the service.** Not into the
   person's hands, but directly to the landlord, the pharmacy, the food store. The
   aid recipient physically cannot divert that money to something else.
2. **Confirmation is built in by itself.** The open ledger shows forever: who was
   paid, how much, for what and when. No separate "prove you spent it right" — that
   is already visible from the payment itself.
3. **This is not surveillance of the person.** What is open is the **payment** (to
   whom and for what), not the person's identity, documents or history. You can see
   that rent was paid — but not who exactly received it or why they are in trouble.
4. **If something falls through, the money returns to the common fund**, instead of
   being lost or staying in someone's hands.
5. **For long-term help we pay in parts.** For long-term rent — month by month, not
   the whole sum up front. If the situation changes, we can stop at any step.

In short: aid reaches its goal because the fund pays for it directly; there is
nothing to skim because no cash is handed out; and there is no surveillance because
what is open is the payment, not the person.

### Three ways to pay for a need

Depending on the situation, the fund pays for a need in one of three ways:

- **Payment with a temporary hold (the main way).** The money is set aside for a
  specific case and can only go to that one service provider. Until the service is
  confirmed the money is frozen; if the deal falls through, it returns to the fund.
- **Direct payment to a verified provider.** If the provider is already on the list
  of verified ones (for example a known pharmacy or landlord), the payment goes
  through right away, without a hold — faster for one-off payments.
- **Off-network payment with proof.** Sometimes the payment goes the ordinary way (a
  bank, cash through a trusted partner). Then the fact of payment is anchored
  provably: the provider confirms receipt, and the invoice or contract stays
  private, but its "fingerprint" goes into the open ledger — it cannot be forged
  after the fact.

---

## How this is tied to the fund's rules

Every requirement here is not invented but follows from the constitution and the
protection rules:

| Rule | Source | How it works here |
|---|---|---|
| Help those who need it most first | [`PRIORITIES.md`](PRIORITIES.md) | Threat of losing housing is reviewed faster, but checks are not skipped |
| Pay in parts | [`ANTI-ABUSE.md`](ANTI-ABUSE.md) | For long-term rent — month by month, not all up front |
| A cap on large sums | [`ANTI-ABUSE.md`](ANTI-ABUSE.md) | Limit per provider per period; more than that — stricter review |
| No one decides alone | [`ANTI-ABUSE.md`](ANTI-ABUSE.md) | A large payment is confirmed by several independent people; no one can approve a payment to themselves |
| Everything is visible | CONSTITUTION art. 3 | Every payment is written to the open ledger |
| No sole power over money | CONSTITUTION art. 2 | No one does a payout, refund or pause alone |
| Emergency stop | [`ANTI-ABUSE.md`](ANTI-ABUSE.md) | Payouts can be frozen temporarily on suspicion — yet even so no one withdraws money to themselves |
| Right to appeal | [`ANTI-ABUSE.md`](ANTI-ABUSE.md) | A refusal or a dispute has a clear appeal path |
| Privacy of the person | CONSTITUTION art. 3 | Publicly — only a case number and the fact of payment, without personal data |

---

## What is open and what stays private

| Open (the payment is visible) | Private (never published) |
|---|---|
| Case number (without a name) | Name, contacts, address of the person |
| Need category and urgency | Diagnosis, situation details |
| Amount and currency | Passport/document scans (only their "fingerprint") |
| Who was paid (the provider) | — |
| Date and status | — |
| "Fingerprint" of the invoice/contract | The invoice/contract itself |

This follows directly from the principle: the **operation** is verifiable, not the
person.

---

## How to explain this to people

- "We do not give money — we pay for housing. And anyone can verify it."
- "Aid reaches its goal instead of dissolving — every payment is visible in the open
  ledger."
- "There is nothing to skim: no cash is handed out."
- "This is not surveillance: you can see that rent was paid, but not your documents
  or personal history."
- "If the deal fell through, the money returns to the common fund, it is not lost."

The prohibitions are honored literally ([`PRINCIPLES.md`](PRINCIPLES.md)): nowhere do
we promise income or profit — this is payment for need, a public good, **not an
investment**.

---

## Open questions for the operator

- **Who maintains the list of verified providers** (landlords, pharmacies) and by
  what procedure are they verified? This is a critical trust point for the "direct
  payment" way.
- Is an **off-network partner** (a legal entity / foundation) needed to pay
  providers without a wallet (the "off-network payment" way)? If so — how do we
  formalize its accountability.
- Confirmation of the test network choice (Polygon Amoy) for the prototype.

See also the "NEEDED FROM THE OPERATOR" section in [`../../PROGRESS.md`](../../PROGRESS.md).

---

## Technical section — for developers

This collects the terms, diagrams and specifications that the main text replaced with
plain words. It is material for those who will write the smart contracts (Stage 5)
and the AI helpers (Stage 6).

### Three models of targeted spending (terminology)

The ways from the "plain" part in development language:

- **The "payment with a hold" way** = a targeted **escrow** contract (model A, the
  main one). Funds are locked in the contract and released (`release`) only to the
  provider's address; `refund` returns them to the treasury.
- **The "direct payment" way** = a targeted whitelist transfer (**earmarked
  transfer**, model B). The contract transfers only to whitelisted addresses of the
  right category (`housing`/`medical`/`food`). Safety rests on the quality of the
  whitelist (see open questions).
- **The "off-network payment" way** = **verified-receipt** (model C, a bridge to
  off-chain). The provider signs a confirmation (a wallet signature / a partner
  multisig), or the invoice/contract is hashed and the hash goes into the IPFS
  manifest and the decision registry (`governance/registry/`); the document itself
  stays private.

All three are TESTNET-first. Real funds only after an independent audit, a 3-of-5
multisig and a separate operator approval.

### Lifecycle of a targeted payout (state machine)

```
REQUESTED ──► UNDER_REVIEW ──► APPROVED ──► ESCROWED ──► RELEASED → (to provider)
                  │                │            │
                  ▼                ▼            ▼
               REJECTED         (appeal)     REFUNDED → (to treasury)
                  │                            │
                  ▼                            ▼
               APPEAL ◄───────────────────  DISPUTED
```

- **REQUESTED** — a request with a pseudonymous `case_id`, need category and priority.
- **UNDER_REVIEW** — collective review (several independent reviewers / multisig);
  Fairness/Audit AI flag anomalies but **do not decide** (article 9).
- **APPROVED** — the decision and its rationale are written to the public registry.
- **ESCROWED** — funds are locked, the provider's address is fixed.
- **RELEASED** — transfer to the provider (a tranche or the full sum), a public
  event (`event`) is emitted for audit.
- **REFUNDED** — return to the treasury if the service was not rendered.
- **DISPUTED / APPEAL** — the appeal path ([`ANTI-ABUSE.md`](ANTI-ABUSE.md) §6).

### Mapping to the protection rules (technically)

| Requirement | Source | Implementation |
|---|---|---|
| Need priority | [`PRIORITIES.md`](PRIORITIES.md) | Housing = level 2; speeds up review, does not disable checks |
| Staged payments | ANTI-ABUSE §1 | Monthly escrow tranches instead of an advance |
| Limits | ANTI-ABUSE §2 | Limit per address/period; excess → enhanced review |
| Collective review | ANTI-ABUSE §3 | Approval above the limit — multisig; cannot approve your own payout |
| Publicity | CONSTITUTION art. 3, PRINCIPLES prohibition №6 | All branches emit events; the decision registry is public |
| No sole control | CONSTITUTION art. 2, PRINCIPLES prohibition №5 | Release/refund/pause — only under collective control |
| Circuit breaker (emergency stop) | ANTI-ABUSE §8 | Pause payouts on an incident, with no right for one person to withdraw funds |
| Appeals | ANTI-ABUSE §6 | DISPUTED/APPEAL states |
| Applicant privacy | CONSTITUTION art. 3 | On-chain only `case_id` and the fact; no personal data |

### Sketch of the contract interface (Solidity pseudocode, for TESTNET)

```solidity
// Pseudocode — a specification of intent, not the final contract.
interface ITargetedDisbursement {
    // Service providers by category (housing/medical/food...).
    function isWhitelistedProvider(address provider, uint8 category) external view returns (bool);

    // Open a targeted escrow: funds will go ONLY to this provider.
    function open(bytes32 caseId, uint8 priorityLevel, address provider, uint256 amount) external returns (uint256 id);

    // A tranche to the provider (staged payments). Requires collective approval above the limit.
    function release(uint256 id, uint256 amount) external; // emits Released(id, provider, amount)

    // Return to the treasury if the service was not rendered.
    function refund(uint256 id) external;                   // emits Refunded(id, treasury, amount)

    // Emergency pause under collective control (circuit breaker).
    function pause() external;
}
```

Implementation requirements (from [`ANTI-ABUSE.md`](ANTI-ABUSE.md)):

- `release` above the limit **must** go through multisig/collective review.
- No address can approve its own payout single-handedly.
- All branches (`open`/`release`/`refund`/`pause`) emit public events.
- Extend `governance/registry/disbursement.schema.json` with `provider`, `category`,
  `escrow_id`, `tranche` fields — so that the decision registry and on-chain match.
- Full test coverage + a run on a testnet (Polygon Amoy proposed in LAUNCH.md) "to
  green". No mainnet/real funds without an audit and operator approval.
