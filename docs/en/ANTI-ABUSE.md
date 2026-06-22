[Русский](../ANTI-ABUSE.md) · [English]

# ANTI-ABUSE — PUBLIC TRUST DAO

> Normative document. Derived from [`CONSTITUTION.md`](CONSTITUTION.md)
> (article 7) and [`MANIFESTO.md`](MANIFESTO.md). A specification for smart
> contracts (treasury, payouts, reputation, audit) and for Audit / Guardian /
> Fairness AI.
>
> **Core principle: the system must make honesty more profitable than fraud.**

## Protection mechanisms

1. **Phased payouts** — large aid is disbursed in tranches tied to confirmed
   milestones, rather than as a single sum paid in advance.
2. **Limits** — caps on the payout amount per address/period; exceeding them
   requires enhanced verification.
3. **Collective verification** — significant decisions are confirmed by several
   independent reviewers / multisig, not by a single person.
4. **Public reports** — all treasury operations are published and readable.
5. **Audit** — regular internal and independent external audit; before real
   funds enter — a mandatory security audit (constitution article 4.4).
6. **Appeals** — a participant has a transparent path to appeal a
   denial/sanction.
7. **Reputational sanctions** — violations lower reputation (see below).
8. **Temporary restrictions** — suspicious activity leads to a temporary freeze
   of payouts pending verification.
9. **Exclusion of participants** — repeated/gross violations lead to exclusion
   through a transparent procedure.

## Reputation system

Reputation is **only auxiliary** and does not override the priority of need
([`PRIORITIES.md`](PRIORITIES.md), rule 3). Taken into account:

- time of participation;
- completed tasks;
- help given to other people;
- absence of violations;
- community recommendations;
- duration of participation.

Reputation is not bought, not transferred for money, and does not depend on
recruiting new participants (prohibition No. 4 in [`PRINCIPLES.md`](PRINCIPLES.md)).

## Smart-contract requirements

- Payouts above the limit **must** pass through multisig/collective
  verification.
- No address may approve its own payout single-handedly.
- All payout branches emit public events for audit.
- A pause/freeze (circuit breaker) under collective control must exist to
  respond to an incident — with no single person able to withdraw funds.
- No logic may reward the number of invited addresses.

## AI-agent requirements

- **Audit AI** — monitors operations, flags anomalies for human reviewers
  (does not block or pay out by itself).
- **Guardian AI** — checks that actions comply with the constitution and the
  prohibitions.
- **Fairness AI** — ensures the priority is respected and there is no
  discrimination/favoritism.
- Any AI decision is a recommendation for people/contracts, not final authority
  (constitution article 9).
