[Русский](../ANTI-ABUSE.md) · [English]

# HOW THE FUND IS PROTECTED FROM FRAUD AND THEFT — PUBLIC TRUST DAO

> This document explains **how the shared wallet is protected: what stops someone
> from stealing money, tricking it out by fraud, or spending it on the wrong
> person**. Plain words first, technical requirements for developers below.
>
> The document derives from [`CONSTITUTION.md`](CONSTITUTION.md) (article 7,
> "protection from abuse") and [`MANIFESTO.md`](MANIFESTO.md). Linked with
> [`PRIORITIES.md`](PRIORITIES.md) (who we help first),
> [`PRINCIPLES.md`](PRINCIPLES.md) (what the fund may not promise),
> [`REWARDS-MODEL.md`](REWARDS-MODEL.md), [`GOVERNANCE.md`](GOVERNANCE.md).
>
> The document itself does not move any money — it is a description of the rules
> for future contract programs (treasury, payouts, reputation) and for the
> "Audit", "Guardian" and "Fairness" AI helpers.
>
> **Important on safety.** All the rules below work, for now, **only on a test
> network and in calculations** — with no real money. The fund will begin
> distributing real funds only after an independent code review, separate
> consent, and under a shared wallet where every payout needs the signatures of
> at least 3 of 5 living guardians (article 4.4).

---

## The main idea — in plain words

The core idea in one line:

> **We build the system so that being honest pays off more than cheating.**

The money in the shared wallet is other people's — donated to help people. So
the protection rests not on trust ("he's a good person") but on simple rules that
work by themselves:

1. **We pay out not the whole sum at once, but in parts** — as it is confirmed
   that help actually reaches the person. If something goes wrong, you can stop
   at any step, not after everything is already gone.
2. **Large sums have a limiter.** A big payout cannot be made quietly: the larger
   the sum, the stricter the check.
3. **No single person decides alone.** A significant payout must be confirmed by
   several independent people. No one can approve a payout to themselves.
4. **Everything is visible.** Every movement of money is written into an open
   journal — anyone can check where the funds went and why.
5. **There is an emergency stop.** If suspicious activity is noticed, payouts can
   be temporarily frozen pending review — but even with the emergency stop no
   single person can withdraw money to themselves.
6. **Merit helps, but gives no power over money and never overrides who needs it
   most.** A good reputation speeds up trust, but it cannot be bought, cannot be
   earned by "bring a friend", and is never placed above real need.
7. **Everyone has the right to appeal.** If a person is denied or sanctioned,
   there is a clear path to appeal — not "we decided, that's it".

In short: stealing does not pay (you get caught and everyone sees), much cannot
be conned out (paid in parts, checked by several people), and the wallet cannot
be captured (no one has sole power over the money).

## Exactly what protects the wallet

Nine pillars of protection — in plain words:

1. **Payout in parts.** Large aid goes in tranches tied to confirmed steps, not
   as one sum up front.
2. **Limits.** There is a cap on the amount per address per period; to exceed it
   you need enhanced verification.
3. **Verification by several people.** Significant decisions are confirmed not by
   one person but by several independent ones (or a shared wallet with several
   signatures).
4. **Open reports.** All wallet operations are published and readable.
5. **Outside review (audit).** Regular internal review and an independent
   external one; before real money enters — a mandatory security code review
   (constitution article 4.4).
6. **Right to appeal.** A participant has a transparent path to contest a denial
   or sanction.
7. **Sanctions for violations via reputation.** Violations lower reputation
   (see below).
8. **Temporary freeze.** Suspicious activity leads to a temporary suspension of
   payouts pending review.
9. **Exclusion.** Repeated or gross violations lead to exclusion of the
   participant through a transparent procedure.

## About reputation (a participant's merit)

Reputation is **only a helper**. It makes it easier to trust proven people faster,
but it **never overrides the rule "first comes the one who needs it most"**
([`PRIORITIES.md`](PRIORITIES.md), rule 3).

What goes into reputation:

- how long the person has participated;
- what tasks they completed;
- whom they helped and how;
- absence of violations;
- recommendations from other participants.

Hard limits (this is law, not a wish):

- reputation **cannot be bought** and cannot be transferred for money;
- reputation **does not depend in any way on how many people you brought in** —
  this fund pays nothing at all for "invitations" (prohibition No. 4 in
  [`PRINCIPLES.md`](PRINCIPLES.md), protection against pyramid schemes);
- reputation **gives no power over money** — it is a weight of trust in the work,
  not a right to dispose of the wallet.

---

## Technical section — for developers

This section translates the rules above into requirements for smart contracts and
AI agents. Terms here are given as-is — it is addressed to those who write code.

### Smart-contract requirements

- Payouts above the limit **must** pass collective verification through a shared
  wallet with several signatures (multisig).
- No address may approve its own payout single-handedly.
- All payout branches emit public events for audit and for the link to the public
  decision registry.
- A pause/freeze ("emergency stop", circuit breaker) under collective control
  must exist to respond to an incident — **with no single person able to withdraw
  funds** (the pause only stops, it does not move money).
- No logic may reward the number of invited addresses (pyramid-scheme ban).

These properties are already built into the `Treasury.sol` and `Disbursement.sol`
contracts (the `executor` role moves funds, `guardian` only sets the pause, the
`maxRelease` cap, an event on every movement) — see [`contracts/`](../../contracts/).

### AI-agent requirements

AI here is an **advisor, not an authority**: any of its decisions is a
recommendation for people and contracts, not a final verdict (constitution
article 9).

- **Audit AI** — watches operations, flags anomalies for human reviewers (does
  not block or pay out by itself).
- **Guardian AI** — checks that actions do not contradict the constitution and
  the direct prohibitions.
- **Fairness AI** — ensures the priority of need is respected and there is no
  discrimination or favoritism.
