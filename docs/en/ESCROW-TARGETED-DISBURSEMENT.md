[Русский](../ESCROW-TARGETED-DISBURSEMENT.md) · [English]

# TARGETED USE OF AID AND ESCROW — confirmation model

> Normative project document. Derived from [`CONSTITUTION.md`](CONSTITUTION.md)
> (articles 4, 5, 7), [`PRIORITIES.md`](PRIORITIES.md) and [`ANTI-ABUSE.md`](ANTI-ABUSE.md).
> This is a specification for the disbursement smart contracts (Stage 5) and for the
> Audit / Guardian / Fairness AI (Stage 6).
>
> **Core principle: aid is not handed out as cash — it is paid directly to the
> service provider (the landlord, the pharmacy, the food supplier).**
> Then "proof of targeted use" need not be begged for after the fact —
> it is built into the transaction itself and is permanently visible in the open ledger.

---

## 1. Why this is needed

The question "how do you confirm that the money went to housing and not to something
else?" is central to trust. The classic answer (collecting receipts after cash has
been handed out) is poor: it is easy to forge, it humiliates the person with constant
checks, and it creates a temptation to misuse funds. Our approach turns the problem
around:

- **We don't give money — we pay for the need.** Funds move from the treasury to the
  service provider, bypassing the aid recipient's "hands."
- **Confirmation is built into the transaction.** The amount, the recipient-provider,
  the purpose and the date are recorded forever on the blockchain. Anyone can verify it.
- **This is not surveillance of a person.** What is public is the **transaction** (to
  whom, how much, for what), not the applicant's identity and not their private documents.

This directly answers the constitution: article 3 (openness and verifiability), article 5
(fair distribution by need, with the "threat of losing housing" priority = level 2
in [`PRIORITIES.md`](PRIORITIES.md)), article 7 and [`ANTI-ABUSE.md`](ANTI-ABUSE.md)
(protection against misuse of funds).

---

## 2. Three models of targeted use

All three are TESTNET-first. Real funds — only after an independent audit,
3-of-5 multisig and a separate operator approval (safety rails).

### Model A. Targeted escrow contract (primary)

Funds are locked in a contract and released **only** to the service provider's address.

```
Request approved  →  funds locked in escrow  →  release only to the
                                                 landlord's address
```

- The aid recipient **physically cannot** withdraw the funds as cash to themselves.
- Phasing: for long-term rent — monthly tranches (release on a schedule) rather than
  the full amount up front (the "phased payments" mechanism, [`ANTI-ABUSE.md`](ANTI-ABUSE.md) §1).
- If the service is not rendered / the deal falls through — `refund` returns the funds
  to the treasury (not to the recipient), under collective control.
- This is, in plain words, the "smart contract for rent."

### Model B. Direct earmarked transfer

The contract can transfer only to **whitelisted addresses** of a given category
(for example "housing," "medicine," "food").

- Faster than escrow (no locking phase), suitable for one-off payments to a verified
  provider.
- Security rests on the quality of the whitelist: who adds providers to it and how
  (see the open questions, §7).

### Model C. Verified-receipt (a bridge to the off-chain world)

When a payment physically happens off-chain (a bank, cash via a trusted partner), the
fact of targeted use is recorded provably:

- the landlord/provider **signs** a confirmation of receipt (a wallet signature or a
  partner multisig), **or**
- the invoice/contract is **hashed** and the hash is placed in the IPFS manifest and in
  the decisions registry (`governance/registry/`), while the document itself stays private.

What is public and immutable is **the fact and its fingerprint**, not personal data.

---

## 3. Lifecycle of a targeted payment (state machine)

```
REQUESTED ──► UNDER_REVIEW ──► APPROVED ──► ESCROWED ──► RELEASED → (to provider)
                  │                │            │
                  ▼                ▼            ▼
               REJECTED         (appeal)     REFUNDED → (to treasury)
                  │                            │
                  ▼                            ▼
               APPEAL ◄───────────────────  DISPUTED
```

- **REQUESTED** — a request with a pseudonymous `case_id`, a need category and a priority.
- **UNDER_REVIEW** — collective review (several independent reviewers / multisig);
  Fairness/Audit AI flag anomalies but **do not decide** (article 9).
- **APPROVED** — the decision and its rationale are written into the public registry.
- **ESCROWED** — funds are locked, the provider's address is fixed.
- **RELEASED** — transfer to the provider (a tranche or the full amount), a public event
  is emitted for audit.
- **REFUNDED** — return to the treasury if the service was not rendered.
- **DISPUTED / APPEAL** — a transparent appeals path ([`ANTI-ABUSE.md`](ANTI-ABUSE.md) §6).

---

## 4. Binding to the constitution and anti-abuse

| Requirement | Source | How it is implemented here |
|---|---|---|
| Priority by need | [`PRIORITIES.md`](PRIORITIES.md) | Housing = level 2; speeds up review but does not disable checks |
| Phased payments | ANTI-ABUSE §1 | Monthly escrow tranches instead of an advance |
| Limits | ANTI-ABUSE §2 | Limit per address/period; exceeding it → enhanced review |
| Collective review | ANTI-ABUSE §3 | Approval above the limit — multisig; you cannot approve your own payment |
| Publicity | CONSTITUTION art. 3, PRINCIPLES prohibition №6 | All payment branches emit events; the decisions registry is public |
| No sole control | CONSTITUTION art. 2, PRINCIPLES prohibition №5 | Release/refund/pause — only under collective control |
| Circuit breaker | ANTI-ABUSE §8 | Pause payments during an incident, with no right for one person to withdraw funds |
| Appeals | ANTI-ABUSE §6 | DISPUTED/APPEAL states in the model |
| Applicant privacy | CONSTITUTION art. 3 | On-chain only `case_id` and the fact; no personal data |

---

## 5. Privacy: what is public and what is not

| Public (on-chain / registry) | Private (never made publicly accessible) |
|---|---|
| Pseudonymous `case_id` | Name, contacts, applicant's address |
| Need category and priority | Medical diagnosis, situation details |
| Amount and currency | Scans of passport/documents (only their hash) |
| Provider-recipient's address | — |
| Date, status, events | — |
| Hash of the invoice/contract (IPFS) | The invoice/contract itself |

This is a direct consequence of the principle: the **operation** is verifiable, not the person.

---

## 6. How to explain this to people (in plain language)

- **"We don't hand out money — we pay for housing. And anyone can verify it."**
- "Aid **reaches its target** rather than dissolving — every payment is visible in the
  open registry."
- "No one can skim it off: there is no manual handout of cash — so there is no temptation."
- "This is **not surveillance**: you can see that the rent was paid, but you can't see
  your documents and personal history."
- "If the deal falls through — the money returns to the common fund, it is not lost."

The prohibitions are observed literally ([`PRINCIPLES.md`](PRINCIPLES.md)): nowhere do we
promise income or profit — this is payment for a need, a public good, **not an investment**.

---

## 7. What this means for Stage 5 (contracts)

A sketch of the targeted-payment interface (Solidity pseudocode, for TESTNET):

```solidity
// Pseudocode — a specification of intent, not the final contract.
interface ITargetedDisbursement {
    // Service providers by category (housing/medicine/food...).
    function isWhitelistedProvider(address provider, uint8 category) external view returns (bool);

    // Open a targeted escrow: funds will go ONLY to this provider.
    function open(bytes32 caseId, uint8 priorityLevel, address provider, uint256 amount) external returns (uint256 id);

    // Tranche to the provider (phased payments). Requires collective approval above the limit.
    function release(uint256 id, uint256 amount) external; // emits Released(id, provider, amount)

    // Return to the treasury if the service was not rendered.
    function refund(uint256 id) external;                   // emits Refunded(id, treasury, amount)

    // Emergency pause under collective control (circuit breaker).
    function pause() external;
}
```

Implementation requirements (from [`ANTI-ABUSE.md`](ANTI-ABUSE.md)):

- `release` for an amount above the limit **must** pass through multisig/collective review.
- No single address can approve its own payment unilaterally.
- All branches (`open`/`release`/`refund`/`pause`) emit public events.
- Extend `governance/registry/disbursement.schema.json` with the fields `provider`,
  `category`, `escrow_id`, `tranche` — so that the decisions registry and on-chain match.
- Full test coverage + a testnet run (Polygon Amoy proposed in LAUNCH.md)
  "to green." No mainnet/real funds without an audit and operator approval.

---

## 8. Open questions for the operator

- **Who maintains the provider whitelist** (landlords/pharmacies) and by what procedure
  are they verified? This is a critical point of trust for model B.
- Is an **off-chain partner** (a legal entity/fund) needed to pay providers that do not
  have a wallet (model C)? If so — how do we formalize its accountability.
- Confirmation of the choice of test network (Polygon Amoy) for the escrow prototype.

See also the "NEEDED FROM THE OPERATOR" section in [`PROGRESS.md`](../../PROGRESS.md).
