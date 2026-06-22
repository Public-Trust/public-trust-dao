[Русский](../REWARDS-MODEL.md) · [English]

# REWARD AND DISTRIBUTION MODEL — PUBLIC TRUST DAO

> Normative document. The base **parametric** model of how the fund splits funds
> between aid to those in need and rewards for socially useful contribution.
> Derived from [`CONSTITUTION.md`](CONSTITUTION.md) (Art. 5 "fair distribution",
> Art. 6 "reward", Art. 7 "abuse protection"), [`PRINCIPLES.md`](PRINCIPLES.md)
> (constitutional prohibitions), [`PRIORITIES.md`](PRIORITIES.md),
> [`ANTI-ABUSE.md`](ANTI-ABUSE.md). Linked to [`SUPPORT-MODEL.md`](SUPPORT-MODEL.md),
> [`ESCROW-TARGETED-DISBURSEMENT.md`](ESCROW-TARGETED-DISBURSEMENT.md),
> [`GOVERNANCE.md`](GOVERNANCE.md).
>
> This is a **specification** for the treasury/distribution smart contracts
> (Stage 5) and for Fairness AI / Audit AI. The document itself controls no funds.
>
> Registered as a decision in the public registry:
> [`governance/registry/`](../../governance/registry/) (record `PTD-0038`).
>
> **Safety rail.** All parameters and formulas below are **on testnet and in
> calculation only**. Real funds are distributed only after an independent audit,
> explicit approval, and under a Safe multisig 3-of-5 of living guardians (Art.
> 4.4). Until then the model exists as code, tests, and community-agreed
> coefficients.

---

## 0. Why a parametric model specifically

The constitution sets the **rails** (need above reward; reward never depends on
recruiting people; reputation is only an auxiliary multiplier; limits and public
reports) but it does not set **numbers**. Hard sums ("pay X per task", "give Y to
a person in need") would be harmful: with an empty treasury they would bankrupt
the fund, with a full one they would under-use it. So the model is **adaptive**:
not fixed sums but **ranges and shares** that automatically depend on the state of
the treasury and the inflow of funds, with the coefficients governed by community
vote, not by a manual operator.

The master invariant everything derives from:

> **Need first. Reward second — for the labor that closes that need.**
> When funds are scarce, almost everything goes to basic need of the highest
> priorities and rewards are minimal (down to symbolic/non-monetary). When the
> treasury grows and inflow is stable, aid widens and rewards become more visible —
> but always within a hard ceiling that a vote cannot push upward.

## 1. Three separate streams

The model separates three **different** kinds of accrual. They must not be mixed:
each has its own purpose, its own proofs, and its own bounds.

| Stream | To whom | For what | Form | Constitutional anchor |
|---|---|---|---|---|
| **H — Aid to those in need** | beneficiaries (applicants) | closing a verified need (housing, medical, food…) | **targeted spend** directly to a provider (not "cash in hand") | Art. 5, [`PRIORITIES.md`](PRIORITIES.md), [`ESCROW-TARGETED-DISBURSEMENT.md`](ESCROW-TARGETED-DISBURSEMENT.md) |
| **W — Reward for work/contribution** | contributor-workers | real labor: code, ops, mediation, review, audit | compensation for verified volume | Art. 6, [`ANTI-ABUSE.md`](ANTI-ABUSE.md) |
| **V — Reward for volunteering** | volunteers | one-off / irregular socially useful help | recognition: symbolic/non-monetary or a small rate | Art. 6 |

**Aid (H) is not a reward** and ranks above both reward streams. W and V exist only
because the fund cannot run without people's labor; but they **never** compete with
basic need for the same coin on equal footing — need is served first (Section 2).

The forbidden "fourth stream" is **pay for recruiting people** (referrals, a bonus
for "bring a donor/applicant"). It is not and cannot be in the model (Art. 6.2,
prohibition #4 of [`PRINCIPLES.md`](PRINCIPLES.md)).

## 2. Adaptive budget split (the core)

### 2.1. What is even available to distribute

In a settlement period the treasury **does not give away everything it holds**.
First a **protective buffer** `B_min` is reserved (a non-reducible reserve for
current obligations and contingencies), and only the surplus above it forms the
distributable budget `D`:

```
D = max(0, balance − B_min)
```

The buffer `B_min` is a governed parameter; it protects already-open staged aid
cases from being "eaten" by new accruals.

### 2.2. Treasury health index `h`

Adaptivity is driven by a single normalized number `h ∈ [0, 1]` — how funded the
treasury is relative to its buffer target `B_target` and how stable the inflow is:

```
h = clamp( (balance − B_min) / B_target , 0, 1 )   # fundedness
```

(Extension: `h` may be multiplied by an inflow-stability factor across several
periods so a one-off donation spike does not inflate rewards. This is a governed
parameter, off by default.)

`h ≈ 0` — scarcity regime (bootstrap/lean). `h ≈ 1` — abundance regime.

### 2.3. The reward share grows with `h`, under a hard ceiling

The distributable budget `D` splits into an **aid pool** and a **reward pool**. The
reward-pool share `ρ` (W and V together) **grows linearly with `h`** between two
parameters, but **never** exceeds the constitutional ceiling:

```
ρ = ρ_min + (ρ_max − ρ_min) · h            # reward share
aid    H_pool = (1 − ρ) · D                # aid pool
reward R_pool = ρ · D                      # W + V pool
```

Hard constraint (a rail, not overridable by a vote):

```
0 ≤ ρ_min ≤ ρ_max ≤ ρ_cap
```

— where `ρ_cap` is the **constitutional ceiling on the reward share** (default
`0.30`: even in the richest regime ≥ 70% of the distributable budget goes to aid).
A vote may lower `ρ_min`/`ρ_max` (down to 0 — "everything to aid now") but **cannot
raise them above `ρ_cap`**. This is the machine encoding of "need above reward".

**Regime illustration** (values are illustrative defaults, not final sums):

| Regime | `h` | `ρ` (to reward) | Aid | In practice |
|---|---|---|---|---|
| Scarcity (bootstrap) | ~0.0 | `ρ_min` ≈ 0–5% | ~95–100% | only priorities 1–4 (life/housing/medical/food); W minimal, V symbolic/non-monetary |
| Lean | ~0.25 | ~8% | ~92% | basic need + critical ops; modest rewards |
| Healthy | ~0.6 | ~18% | ~82% | wider aid (priorities 1–8); W in its normal band |
| Abundance | ~1.0 | `ρ_max` ≤ `ρ_cap`=30% | ≥ 70% | wide aid (down to priority 10) + visible but bounded rewards |

Inside the aid pool `H_pool` funds are distributed **strictly by
[`PRIORITIES.md`](PRIORITIES.md)**: in scarcity only the top priority levels are
served; as `h` rises the "depth" of coverage descends to less urgent levels. No
priority level "switches off" the [`ANTI-ABUSE.md`](ANTI-ABUSE.md) safeguards.

### 2.4. Splitting the reward pool into W and V

`R_pool` splits between work and volunteering by a parameter `w_work ∈ [0,1]`:

```
W_pool = w_work · R_pool          # work/contribution
V_pool = (1 − w_work) · R_pool    # volunteering
```

`w_work` is governed (by default work takes the larger share, as it requires
sustained labor; volunteering is by nature one-off and often non-monetary).

## 3. Accrual sizes — ranges, not sums

Within each pool a concrete accrual is a **band**, not a fixed figure. This keeps
the model adaptive and verifiable.

### 3.1. Aid to those in need (H)

- Tranche size = **min of**: (a) the verified cost of the need at the provider;
  (b) the per-case/period limit; (c) the available `H_pool` for that priority level.
- The payout is **staged** (see [`ESCROW-TARGETED-DISBURSEMENT.md`](ESCROW-TARGETED-DISBURSEMENT.md)):
  the tranche is tied to a confirmed milestone; any remainder returns to the
  treasury, not to the recipient.
- Money is **not handed out as cash** — it is paid directly to a verified provider.
- The size targets the **actual need**, not "equal shares": giving enough for
  housing to not become homeless is exactly what fairness is (Art. 5.2 — increase
  self-reliance).

### 3.2. Reward for work (W)

- Each task/contribution has a **published band** of "value" (e.g. by difficulty
  classes `S/M/L/XL`), not a single figure; the concrete accrual is chosen by
  reviewers within the band by volume and quality.
- Bands scale with the index `h`: in scarcity, the lower edge of the band (or 0 —
  "thank you, but the treasury is treating need now"); in abundance, higher in the
  band but under the `W_pool` ceiling.
- **Reputation is only an auxiliary multiplier** `m_rep ∈ [1 .. 1+rep_cap]` to the
  position within the band: it does **not create** a right to a payout and does
  **not break** the band ceiling. Reputation is not bought and not transferred
  (Art. 6, [`ANTI-ABUSE.md`](ANTI-ABUSE.md), consistent with `votingUnits` in
  [`Reputation.sol`](../../contracts/contracts/Reputation.sol)).
- No one approves their own reward (Section 4).

### 3.3. Reward for volunteering (V)

- By default **recognition, not salary**: a badge / thank-you record in the
  registry, an optional small rate from `V_pool`.
- Strictly non-monetary in the scarcity regime (`h≈0`): volunteering is valuable in
  itself and must not drain aid.
- The same proof-and-review logic as W, but lighter for one-off actions.

## 4. Validation: how need and contribution are proven

Every accrual in any stream must be **reproducible and verifiable** — otherwise the
model degrades into trust-based handouts, which the constitution does not allow
(Art. 3, Art. 7).

**Proofs (binding to the subject):**

- **Need (H):** an application with a pseudonymous `case_id` (no personal data in
  the public part), confirmation from the provider (invoice/contract/estimate), and
  if needed a domain reviewer's confirmation. Identity is protected: the fact and
  amount are public, the person's story is not (Art. 3 + applicant privacy).
- **Work (W):** a verifiable artifact (commit/PR, ops log, mediation protocol,
  audit report) signed by the author; a link to the task.
- **Volunteering (V):** evidence of the action (a report + confirmation from ≥1 aid
  recipient or coordinator).

**Collective review (no one acting alone):**

- A significant accrual is confirmed by **≥2 independent reviewers** or a multisig;
  a reviewer **cannot** approve their own accrual and cannot be the author of the
  reviewed work (Art. 7, [`ANTI-ABUSE.md`](ANTI-ABUSE.md)).
- Sybil protection is via the non-transferable member badge (`votingUnits=1` per
  person, [`GOVERNANCE.md`](GOVERNANCE.md) §2–§3): one person cannot clone
  themselves to fake approvals or harvest many "volunteer" accruals.

**Role of AI (computes and checks, does not decide):**

- **Fairness AI** ([`../../ai-agents/fairness_agent.py`](../../ai-agents/fairness_agent.py))
  recomputes each accrual against this model and
  [`PRIORITIES.md`](PRIORITIES.md): is the priority valid, are limits / the appeal
  window intact, are there ≥2 confirmations, is staging respected, is there no
  personal-data leak.
- **Audit AI** ([`../../ai-agents/audit_agent.py`](../../ai-agents/audit_agent.py))
  checks that each accrual has a registry record matching an on-chain event (the
  treasury does not move past the registry).
- Any AI verdict is a **signal to people/contracts, not power** (Art. 9). Going red
  halts for review, but the AI itself neither pays nor freezes funds.

**Public registry and appeals:**

- **Every** accrual (H/W/V) is recorded in [`governance/registry/`](../../governance/registry/)
  (append-only hash-chain) and as an on-chain event — anyone can recompute the
  amount by this model and verify the chain.
- Every refusal/sanction/disputed accrual has a **transparent appeal** (see
  [`../../governance/mediation/`](../../governance/mediation/) and
  [`ANTI-ABUSE.md`](ANTI-ABUSE.md) §6) — decided by people, not by AI and not by a
  single person.

## 5. Who changes the parameters, and how

All model coefficients are **under community vote**, not under the operator's manual
control (this is what "coefficients governed by vote" means). Changing a parameter
is a `parameter-change` proposal in
[`governance/snapshot/space.json`](../../governance/snapshot/space.json) → executed
via the `Timelock` ([`GOVERNANCE.md`](GOVERNANCE.md) §4–§7). The hard ceilings
(`ρ_cap`, the non-reducible buffer, the ban on referral accruals) are the
**constitutional core**: they cannot be raised by an ordinary vote, only through the
Art. 10 procedure, and without violating the immutable core (Art. 10.2).

### 5.1. Machine-readable parameters (for contracts and Fairness AI)

The aid `level` is taken from [`PRIORITIES.md`](PRIORITIES.md). The values below are
**illustrative defaults** with the bounds within which a vote may move them; the
final values are approved by the community before any real funds enter.

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

> The keys (`B_min`, `rho_min`, …) are stable for the code; only the values and
> labels change on translation. `governed:false` is a rail, untouched by an ordinary
> vote.

## 6. Hard boundaries (rails, in brief)

- **Need above reward.** Aid is always ≥ `1 − ρ_cap` (default ≥ 70%) of the
  distributable budget; in scarcity, nearly all of it to aid.
- **Reward never depends on recruiting people** (Art. 6.2). There are no referral
  accruals in the model; the `referral_rewards = forbidden` parameter is immutable.
- **Reputation is only an auxiliary multiplier.** It creates no right to a payout,
  breaks no band ceiling, is not bought, is not transferred.
- **Limits + staging + public reports** apply to every stream; high priority speeds
  up but never switches off the safeguards ([`ANTI-ABUSE.md`](ANTI-ABUSE.md)).
- **No one approves themselves.** ≥2 independent reviewers; AI computes and signals
  but does not control funds (Art. 9).
- **Everything is verifiable.** Each accrual is a registry record + an on-chain
  event, recomputable by this model; every refusal has an appeal.
- **TESTNET-first.** Real funds only after audit, approval, and under Safe 3-of-5
  (Art. 4.4).

## 7. In plain words

> Picture a shared wallet. First, a **untouchable reserve** is set aside so that aid
> already begun is surely seen through. From the rest, **the larger part always goes
> to those who need it most** (first: save a life, prevent homelessness, treat,
> feed), and **the smaller part** is a thank-you to those who make that aid possible
> (writing code, reviewing applications, mediating disputes, volunteering). When the
> wallet is low, nearly everything goes to need and the "thank-you" is symbolic. When
> inflow is stable and there is more, aid widens and the "thank-you" grows — but
> **never** beyond a third: the fund exists for those in need, not for salaries. And
> every coin is in plain view: who got what, for what, and how much — recomputable by
> anyone.

## 8. Link to the plan and open questions

- **Stage 5 (contracts):** the parameters from §5.1 go into a distribution contract
  over [`Treasury.sol`](../../contracts/contracts/Treasury.sol) /
  [`Disbursement.sol`](../../contracts/contracts/Disbursement.sol); `ρ_cap` and
  `referral=forbidden` are immutable constants, the rest are `onlyTimelock` (via
  vote). This is the next concrete step of encoding the model.
- **Fairness/Audit AI:** add a check that "an accrual is recomputable by the
  rewards-model and falls within the §2–§3 corridors" (extension of
  [`fairness_agent.py`](../../ai-agents/fairness_agent.py)).
- **Open questions for the community/operator** (decided by vote, not by the agent):
  the starting values of `B_target`, `ρ_min/ρ_max`, the W difficulty classes and
  bands, whether to enable the inflow-stability factor, the `rep_cap` ceiling. Until
  real funds enter, this is calibrated on testnet and approved by the community.

---

See also: [`PRIORITIES.md`](PRIORITIES.md) · [`ANTI-ABUSE.md`](ANTI-ABUSE.md) ·
[`ESCROW-TARGETED-DISBURSEMENT.md`](ESCROW-TARGETED-DISBURSEMENT.md) ·
[`SUPPORT-MODEL.md`](SUPPORT-MODEL.md) · [`GOVERNANCE.md`](GOVERNANCE.md) ·
[`CONSTITUTION.md`](CONSTITUTION.md)
