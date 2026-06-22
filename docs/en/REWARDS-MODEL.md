[Русский](../REWARDS-MODEL.md) · [English]

# HOW THE FUND SPLITS MONEY: AID AND REWARD — PUBLIC TRUST DAO

> This document explains **how the fund decides how much money goes to aid for
> those in need, and how much goes as a thank-you to the people who make that aid
> possible.** Plain words first; technical detail for developers below.
>
> It rests on [`CONSTITUTION.md`](CONSTITUTION.md) (Art. 5 "fair distribution",
> Art. 6 "reward", Art. 7 "abuse protection"), [`PRINCIPLES.md`](PRINCIPLES.md)
> (what the fund may never promise), [`PRIORITIES.md`](PRIORITIES.md) (who we help
> first), [`ANTI-ABUSE.md`](ANTI-ABUSE.md). Linked to
> [`SUPPORT-MODEL.md`](SUPPORT-MODEL.md),
> [`ESCROW-TARGETED-DISBURSEMENT.md`](ESCROW-TARGETED-DISBURSEMENT.md),
> [`GOVERNANCE.md`](GOVERNANCE.md).
>
> The document controls no money itself — it describes the rules for future
> smart-contract programs (Stage 5) and for the "Fairness" and "Audit" AI helpers.
>
> Registered as a decision in the public registry:
> [`governance/registry/`](../../governance/registry/) (record `PTD-0038`).
>
> **About safety.** All rules below work for now **only on the test network and in
> calculation** — with no real money. The fund will start distributing real funds
> only after an independent code review, separate approval, and under a shared
> wallet where any payout needs the signatures of at least 3 of 5 living guardians
> (Art. 4.4).

---

## The main idea — in plain words

Picture a shared wallet that donations flow into.

1. **First we set aside an untouchable reserve.** A cushion for aid already begun,
   so it is surely seen through, and for the unexpected.
2. **Of the rest, the larger part always goes to those who need it most** — first
   save a life, keep a person from becoming homeless, treat illness, feed.
3. **The smaller part is a "thank-you"** to those who make aid possible: writing
   code, reviewing applications, mediating disputes, volunteering.
4. **When money is scarce, almost everything goes to aid**, and the "thank-you" is
   symbolic (gratitude, a mark of recognition). **When there is more money**, aid
   widens and the "thank-you" grows. But the thank-you for labor is **never more
   than a third** of the distributable money: the fund exists for those in need,
   not for salaries.
5. **We pay not fixed sums but within reasonable ranges** — as much as it really
   costs to close a need, or as much as the work fairly deserves.
6. **Every payout is checked by at least two independent people** (no one approves
   their own), plus AI helpers recompute and cross-check it. Everything is visible
   in an open journal, and any decision can be appealed.

The master rule everything follows from:

> **Need first. Thank-you second — for the labor that closes that need.**

## Three separate streams of money

The fund distinguishes three **different** kinds of payout. They must not be mixed:
each has its own purpose, its own proofs, and its own bounds.

| Stream | To whom | For what | In what form |
|---|---|---|---|
| **Aid to those in need** | people who need support | closing a verified need: housing, medical, food, etc. | paid directly to the provider (e.g. rent to the landlord), **not cash in hand** |
| **Thank-you for work** | those doing real labor | code, ops, mediation, review, audit | payment for a verified amount of work |
| **Thank-you for volunteering** | volunteers | one-off, irregular help | usually recognition and a mark of gratitude, sometimes a small payment |

**Aid is not a reward,** and it ranks above both kinds of thank-you. Thank-you for
work and volunteering exists only because the fund cannot run without people's
labor; but they **never** compete with basic need for the same coin on equal
footing — need is served first.

There is a **forbidden "fourth stream"** — pay for bringing someone in (referrals,
a "bring a donor or applicant" bonus). It is not and cannot be in the fund — it is
directly forbidden by the constitution (Art. 6.2, prohibition #4 of
[`PRINCIPLES.md`](PRINCIPLES.md)), because it leads to a pyramid.

## How the wallet is split: aid above thank-you

The logic is simple, and it is also the main safeguard:

- First an **untouchable reserve** is set aside. It protects already-open staged
  aid cases from being "eaten" by new payouts.
- The rest is split into **money for aid** and **money for thank-you for labor**.
- **The better funded the fund is, the more visible the thank-you** — but only
  within a hard ceiling. When money is scarce the thank-you nearly vanishes and
  almost everything goes to need.
- **The thank-you ceiling cannot be raised by an ordinary vote.** By default all
  kinds of thank-you together take no more than a third — so **aid always keeps at
  least 70%**. A vote can lower that share (e.g. "everything to aid now"), but
  cannot raise it above the ceiling. This is the machine encoding of "need above
  reward".

What it looks like in practice:

| When the fund has… | To thank-you | To aid | What it means |
|---|---|---|---|
| very little money | nearly 0% | nearly all | we help only by the most urgent priorities (life / housing / treatment / food); thank-you is symbolic |
| modest | a small share | the larger part | basic need + the most critical fund work |
| good | a visible share | the larger part | aid is wider, thank-you within normal ranges |
| a surplus | up to the ceiling (≈ a third) | at least 70% | wide aid + visible but bounded thank-you |

Within the aid money, everything is distributed **strictly by the order of
priorities** ([`PRIORITIES.md`](PRIORITIES.md)): when tight, only the topmost,
urgent levels are served; with more money, aid reaches less urgent needs too. No
"urgent" status switches off the abuse safeguards
([`ANTI-ABUSE.md`](ANTI-ABUSE.md)).

## How much is actually paid: ranges, not fixed sums

Within each stream a concrete amount is a **reasonable band**, not one frozen
figure. This lets the fund adapt to circumstances and stay verifiable.

**Aid to those in need.** The payout is the smallest of three: how much it actually
costs to close the need at the provider; how much the per-case limit allows; how
much is currently available for that priority level. Aid goes **in stages** (see
[`ESCROW-TARGETED-DISBURSEMENT.md`](ESCROW-TARGETED-DISBURSEMENT.md)): each tranche
is tied to a confirmed step, any unspent remainder returns to the treasury, not to
the recipient. Money is **not handed out as cash** — it is paid directly to a
verified provider. The size looks at the **real need**, not "equal shares for all":
giving enough for housing to keep from becoming homeless is exactly what fairness
is (Art. 5.2 — help people become self-reliant).

**Thank-you for work.** Each task has a **published value band** (e.g. by
difficulty: small / medium / large / very large) — not one figure. Reviewers pick
the concrete sum within the band by volume and quality. When the fund is tight it
is the lower edge of the band or zero ("thank you, but the treasury is treating
need now"); when there is a surplus, higher in the band, but no more than what is
allotted to thank-you. **Reputation is only an auxiliary multiplier** to one's
position within the band: it gives no right to a payout on its own and does not
break the band ceiling. Reputation cannot be bought or transferred. No one approves
their own reward.

**Thank-you for volunteering.** By default this is **recognition, not a salary**: a
mark of gratitude, a journal entry, sometimes a small payment. When money is
scarce — strictly without money: volunteering is valuable in itself and must not
drain aid. Proofs and review are the same as for work, but lighter, for one-off
actions.

## How we confirm that need and work are real

Every payout in any stream must be **reproducible and verifiable** — otherwise the
fund turns into "trust me" handouts, which the constitution does not allow (Art. 3,
Art. 7).

**Proofs.**
- *Need:* an application under a pseudonym (no personal data in the public part)
  and confirmation from the provider (invoice, contract, estimate); if needed, a
  domain reviewer's confirmation. The person's identity is protected: the fact and
  amount of aid are public, their story is not.
- *Work:* a verifiable result (e.g. merged code, an ops log, a mediation protocol,
  an audit report) signed by the author with a link to the task.
- *Volunteering:* evidence of the action — a report plus confirmation from at least
  one aid recipient or coordinator.

**Collective review — no one acting alone.** A significant payout is confirmed by
**at least two independent reviewers**. A reviewer cannot approve their own payout
and cannot be the author of the reviewed work (Art. 7,
[`ANTI-ABUSE.md`](ANTI-ABUSE.md)). Protection against fakery and fake accounts comes
from a **personal non-transferable member's mark** (one person = one vote,
[`GOVERNANCE.md`](GOVERNANCE.md)): you cannot "clone" yourself to fake approvals or
grab many "volunteer" payouts.

**AI computes and checks, but does not decide.** The "Fairness" helper
([`../../ai-agents/fairness_agent.py`](../../ai-agents/fairness_agent.py))
recomputes each payout against these rules and the order of priorities: is the
priority correct, are the limits and the appeal window in place, are there at least
two confirmations, is staging respected, has no personal data leaked. The "Audit"
helper ([`../../ai-agents/audit_agent.py`](../../ai-agents/audit_agent.py)) checks
that each payout has a journal record and that it matches the movement of money on
the blockchain. Any AI conclusion is a **signal to people, not power** (Art. 9): it
can halt a payout for review, but pays out and freezes nothing itself.

**Open journal and appeals.** **Every** payout becomes a record in the public
journal [`governance/registry/`](../../governance/registry/) (records cannot be
altered after the fact) and is reflected on the blockchain — anyone can recompute
the amount by these rules and verify it. Every refusal or disputed payout has a
**transparent appeal** (see [`../../governance/mediation/`](../../governance/mediation/)
and [`ANTI-ABUSE.md`](ANTI-ABUSE.md) §6) — decided by people, not by AI and not by
a single person.

## Who changes the settings

All the "dials" of this model (reserve size, the share for thank-you, task
difficulty, etc.) are **under community vote**, not in the manual control of a
single operator. Changing a setting is a proposal that passes a vote and executes
**with a delay for review** (so an error can be noticed and challenged in time).

But **the hard boundaries cannot be raised by an ordinary vote.** These are: the
thank-you ceiling (aid always ≥ 70%), the untouchability of the reserve, and the
full ban on pay for bringing people in. These boundaries are the constitutional
core; they can be changed only by a special procedure (Art. 10) and without
violating the immutable foundation (Art. 10.2).

## Hard boundaries (in brief)

- **Need above thank-you.** Aid always gets at least 70% of the distributable
  money; when tight, almost all of it.
- **Thank-you never depends on recruiting people** (Art. 6.2). There is no referral
  pay in the model, and that ban is immutable.
- **Reputation is only an auxiliary multiplier.** It grants no right to a payout,
  breaks no ceiling, is not bought, is not transferred.
- **Limits, staging, and public reports** apply to every stream; urgency speeds
  things up but never switches off the safeguards ([`ANTI-ABUSE.md`](ANTI-ABUSE.md)).
- **No one approves themselves.** At least two independent reviewers; AI computes
  and signals but controls no money (Art. 9).
- **Everything is verifiable.** Each payout is a journal record plus a movement on
  the blockchain, recomputable by this model; every refusal has an appeal.
- **Test network first.** Real money only after audit, approval, and under a shared
  wallet 3-of-5 (Art. 4.4).

## Link to the plan

- **Stage 5 (contracts):** these rules go into a distribution program over the
  treasury ([`Treasury.sol`](../../contracts/contracts/Treasury.sol) /
  [`Disbursement.sol`](../../contracts/contracts/Disbursement.sol)); the thank-you
  ceiling and the referral ban are immutable constants, the rest of the settings
  change only by a vote with a delay. This is the next concrete step.
- **AI helpers:** add to "Fairness" a check that a payout is recomputable by this
  model and falls within the allowed ranges.
- **What the community still has to decide** (by vote, not by the agent): the
  starting reserve and thank-you shares, the difficulty classes and bands for work,
  whether to enable smoothing of one-off donation spikes. Until real funds enter,
  all of this is calibrated on the test network and approved by the community.

---

## Technical section — for developers

> Below are the exact formulas and machine-readable parameters. They are for those
> who write the contracts and AI helpers. You do not need them to understand the
> idea — everything important is already said above in plain words.

### T.1. Distributable budget and reserve

In a settlement period the treasury does not give away everything it holds. First a
non-reducible buffer `B_min` is reserved, and only the surplus above it forms the
distributable budget `D`:

```
D = max(0, balance − B_min)
```

`B_min` is a governed parameter; it protects already-open staged aid cases.

### T.2. Treasury health index `h`

Adaptivity is driven by a single normalized number `h ∈ [0, 1]` — how funded the
treasury is relative to its buffer target `B_target`:

```
h = clamp( (balance − B_min) / B_target , 0, 1 )
```

`h ≈ 0` — scarcity regime (bootstrap). `h ≈ 1` — abundance regime. Extension: `h`
may be multiplied by an inflow-stability factor across several periods so a one-off
donation spike does not inflate rewards (governed, off by default).

### T.3. Reward share under a hard ceiling

The distributable budget `D` splits into an aid pool and a reward pool. The
reward-pool share `ρ` (work and volunteering together) grows linearly with `h`, but
never exceeds the constitutional ceiling:

```
ρ = ρ_min + (ρ_max − ρ_min) · h            # reward share
H_pool = (1 − ρ) · D                       # aid pool
R_pool = ρ · D                             # reward pool (W + V)
```

Hard constraint (a rail, not overridable by a vote):

```
0 ≤ ρ_min ≤ ρ_max ≤ ρ_cap
```

`ρ_cap` is the constitutional ceiling on the reward share (default `0.30`: even in
the richest regime ≥ 70% of the distributable budget goes to aid). A vote may lower
`ρ_min`/`ρ_max` down to 0, but cannot raise them above `ρ_cap`.

Regime illustration (values are illustrative defaults):

| Regime | `h` | `ρ` | Aid |
|---|---|---|---|
| Scarcity (bootstrap) | ~0.0 | `ρ_min` ≈ 0–5% | ~95–100% |
| Lean | ~0.25 | ~8% | ~92% |
| Healthy | ~0.6 | ~18% | ~82% |
| Abundance | ~1.0 | `ρ_max` ≤ `ρ_cap`=30% | ≥ 70% |

### T.4. Splitting the reward pool into work and volunteering

```
W_pool = w_work · R_pool          # work/contribution
V_pool = (1 − w_work) · R_pool    # volunteering
```

`w_work ∈ [0,1]` is governed (by default work takes the larger share).

### T.5. Accrual sizes

- **Aid (H):** tranche = `min`(verified cost of the need at the provider; the
  per-case/period limit; the available `H_pool` for that priority level). Staged;
  remainder returns to the treasury.
- **Work (W):** a band by difficulty classes `S/M/L/XL`, scaled by `h`. Reputation
  is a multiplier `m_rep ∈ [1 .. 1+rep_cap]` to the position in the band; it
  creates no right to a payout and breaks no ceiling (consistent with `votingUnits`
  in [`Reputation.sol`](../../contracts/contracts/Reputation.sol)).
- **Volunteering (V):** from `V_pool`; non-monetary at `h≈0`.

### T.6. Machine-readable parameters (for contracts and Fairness AI)

The aid `level` is taken from [`PRIORITIES.md`](PRIORITIES.md). The values are
illustrative defaults with the bounds within which a vote may move them; the final
values are approved by the community before any real funds enter. The keys
(`B_min`, `rho_min`, …) are stable for the code; `governed:false` is a rail,
untouched by an ordinary vote.

```json
{
  "rewards_model": {
    "version": "0.1.0-draft",
    "treasury": {
      "reserve_buffer_min":  { "key": "B_min",    "governed": true,  "note": "non-reducible reserve; protects open cases" },
      "buffer_target":       { "key": "B_target", "governed": true,  "note": "buffer target for normalizing h" },
      "inflow_stability":    { "key": "s",        "governed": true,  "default": false, "note": "smooths one-off donation spikes" }
    },
    "split": {
      "reward_share_min":    { "key": "rho_min",  "default": 0.00, "min": 0.00, "max": 0.30, "governed": true },
      "reward_share_max":    { "key": "rho_max",  "default": 0.20, "min": 0.00, "max": 0.30, "governed": true },
      "reward_share_cap":    { "key": "rho_cap",  "value": 0.30,  "governed": false, "note": "constitutional ceiling: aid always ≥ 70%" },
      "work_share":          { "key": "w_work",   "default": 0.70, "min": 0.00, "max": 1.00, "governed": true }
    },
    "reputation": {
      "multiplier_cap":      { "key": "rep_cap",  "default": 1.0, "min": 0.0, "max": 2.0, "governed": true,
                               "note": "reputation is an auxiliary multiplier to position in a band, not a right to a payout" }
    },
    "validation": {
      "min_reviewers":       { "key": "k",        "default": 2,   "min": 2,  "governed": true },
      "self_approval":       { "value": "forbidden", "governed": false },
      "referral_rewards":    { "value": "forbidden", "governed": false, "note": "Art. 6.2 — never" },
      "appeal_required":     { "value": true,        "governed": false }
    }
  }
}
```

### T.7. Changing the parameters

Changing a parameter is a `parameter-change` proposal in
[`governance/snapshot/space.json`](../../governance/snapshot/space.json) → executed
via the `Timelock` (a delay for review, [`GOVERNANCE.md`](GOVERNANCE.md) §4–§7). The
hard ceilings (`ρ_cap`, the non-reducible buffer, the referral ban) are
`governed:false`: changed only by the Art. 10 procedure, without violating the
immutable core (Art. 10.2).

---

See also: [`PRIORITIES.md`](PRIORITIES.md) · [`ANTI-ABUSE.md`](ANTI-ABUSE.md) ·
[`ESCROW-TARGETED-DISBURSEMENT.md`](ESCROW-TARGETED-DISBURSEMENT.md) ·
[`SUPPORT-MODEL.md`](SUPPORT-MODEL.md) · [`GOVERNANCE.md`](GOVERNANCE.md) ·
[`CONSTITUTION.md`](CONSTITUTION.md)
