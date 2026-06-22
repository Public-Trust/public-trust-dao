[Русский](README.md) · [English]

# AI agents — Public Trust DAO (Stage 6)

> Derived document. Normative basis: [`CONSTITUTION.md`](../docs/en/CONSTITUTION.md)
> (Art. 9 "Role of artificial intelligence"), [`PRINCIPLES.md`](../docs/en/PRINCIPLES.md),
> [`ANTI-ABUSE.md`](../docs/en/ANTI-ABUSE.md), [`GOVERNANCE.md`](../docs/en/GOVERNANCE.md).
>
> **TESTNET-first.** Agents move nothing and own nothing — they only verify, count
> and report. Anything touching money/keys/mainnet is outside the agents and only
> after audit + operator approval + Safe 3-of-5.

---

## Core principle: AI serves, it does not rule

Constitution, Art. 9: **AI holds no power, owns no funds, serves the mission and helps
uphold the constitution.** AI agents are *service modules, not organs of power*.

This sets hard boundaries for EVERY agent in this directory:

- **read-only with respect to funds.** No agent signs transactions, moves the treasury,
  or grants/revokes voting rights on its own behalf. Only the community vote and the
  Safe multisig (executor of the vote) decide.
- **signal, not action.** A finding (violation, risk, drift) is *shown* to people — the
  agent does not "fix" governance itself. A "red" from an agent is grounds for a
  community decision, not a command to act automatically on funds.
- **verifiability.** Agents are open code with no hidden logic; their outputs are
  reproducible (deterministic, no network access and no third-party dependencies where
  possible).
- **privacy.** Agents never publish applicants' personal data — only pseudonymous
  `case_id` and verifiable references (the constitution's spirit of dignity).

## The eight agents (per Art. 9.2)

| Agent | Purpose | Status |
|-------|---------|--------|
| **Audit** | Verifies integrity and transparency: registry (hash-chain), IPFS manifest, Safe/Snapshot configs, contract tests. One "green/red" for the governance layer. | ✅ scaffold (`audit_agent.py`) |
| **Guardian** | Watches the safety rails: no private keys/secrets in the repo, no mainnet/real funds, no TESTNET-first violations. | ✅ scaffold (`guardian_agent.py`) |
| **Fairness** | Checks fairness of distribution per [`PRIORITIES.md`](../docs/en/PRIORITIES.md): priority respected, limits/collective review/staging/privacy. | ✅ scaffold (`fairness_agent.py`) |
| **Reputation** | Computes/validates voting weights per [`GOVERNANCE.md`](../docs/en/GOVERNANCE.md) §2–§3: "1 person = 1 vote", soulbound, "uniqueness ≠ power". | ✅ scaffold (`reputation_agent.py`) |
| **Housing** | Domain helper for housing cases (escrow paying the provider directly per [`ESCROW-TARGETED-DISBURSEMENT.md`](../docs/en/ESCROW-TARGETED-DISBURSEMENT.md)). | ✅ scaffold (`housing_agent.py`) |
| **Governance** | Helps with the proposal lifecycle (format, quorum, timing, ties to the constitution); does not vote itself. | ⏳ planned |
| **Mediator** | Assists with disputes/appeals per [`ANTI-ABUSE.md`](../docs/en/ANTI-ABUSE.md) — structures, does not decide. | ⏳ planned |
| **Documentation** | Watches RU↔EN bilinguality (a pair + a language switcher for every public doc) and the integrity of relative links across all `.md`. | ✅ scaffold (`documentation_agent.py`) |

We build them one by one, "to green", with no token stubs. The scaffold opens with
**Audit** — useful right away: one command checks the whole governance layer.

## Audit agent — what it does and how to run it

`audit_agent.py` combines the four existing rail validators into a single run and ties
each check to the constitution article it protects:

| Check | Tool | Protects |
|-------|------|----------|
| Decision registry (hash-chain, append-only) | `scripts/registry.py verify` | Art. 3 — openness, immutability of records |
| IPFS manifest (CID + sha256) | `scripts/ipfs_manifest.py verify` | Art. 3 — content and CIDs don't drift silently |
| Safe multisig 3-of-5 (testnet, no keys) | `scripts/safe_config.py verify` | Art. 2/4 — no sole owner; TESTNET-first |
| Snapshot "1 person = 1 vote" | `scripts/snapshot_config.py verify` | Art. 2 — no plutocracy; anti-Sybil |
| *(opt.)* Smart-contract tests | `npm test` in `contracts/` | Art. 4/7 — treasury/escrow/governance properties in code |

Run from the repository root:

```bash
# Base governance-layer audit (Python standard library only, no network):
python3 ai-agents/audit_agent.py

# With smart-contract tests (requires Node/npm in contracts/):
python3 ai-agents/audit_agent.py --with-contracts

# Machine-readable report (for CI and other agents):
python3 ai-agents/audit_agent.py --json
```

Exit code `0` — all green; `1` — a violation was found. "Red" is a **signal**: the
agent fixes nothing and controls nothing; the community decides.

CI [`.github/workflows/ai-agents.yml`](../.github/workflows/ai-agents.yml) runs the
base audit on every push/PR — a public guarantee of governance-layer integrity.

## Guardian agent — what it does and how to run it

`guardian_agent.py` is a dedicated, explicit **safety-rails scanner across the whole
repository tree** (not a single config, as `safe_config.py`/`snapshot_config.py` do).
It walks the git-tracked files (what is actually published) and checks:

| Check | What it catches | Protects |
|-------|-----------------|----------|
| `secrets-tracked` | a committed secret/key (`.env`, `*.key`, `*.pem`, `keystore/`, `wallet*.json`, `*_private*`, pulse-state files) | rail "secrets never in the repo" |
| `gitignore-guards` | whether `.gitignore` covers `.env` and `logs/` (pulse state) | rail "secrets not in the repo"; pulse is untouchable |
| `no-mainnet` | a mainnet `chain_id` in any JSON config | rail TESTNET-first |
| `no-key-material` | private keys in text (64-hex outside hash fields; assigning `private key`/`mnemonic`/`seed` a real value) | Art. 2/4 — no owner holding a key to real money |

To avoid false positives on the registry's and manifest's legitimate `sha256`/CID
values, a 64-hex token counts as a key **only outside** hash fields
(`hash`/`prev_hash`/`sha256`/…), and environment references
(`process.env.PRIVATE_KEY`) are not treated as a leak.

```bash
python3 ai-agents/guardian_agent.py          # human-readable report
python3 ai-agents/guardian_agent.py --json    # machine-readable (for CI/other agents)
```

Exit code `0` — rails intact; `1` — a violation found (this is a **signal**, not an action).

A **test invariant** [`test_guardian.py`](test_guardian.py) proves Guardian works rather
than being "green by default": for every violation (committed `.env`/key, mainnet
`chain_id`, a 64-hex key, a secret assignment, a leaky `.gitignore`) the agent must
return "red", while a clean tree with real sha256 hashes stays "green".

CI [`.github/workflows/ai-agents.yml`](../.github/workflows/ai-agents.yml) runs Audit +
the Guardian test invariant + Guardian itself on every push/PR.

## Fairness agent — what it does and how to run it

`fairness_agent.py` walks the public registry records of type `disbursement`
(`governance/registry/`) and checks EVERY payment against the norms of fair
distribution and anti-abuse. The priority scale is read **directly from**
[`docs/PRIORITIES.md`](../docs/en/PRIORITIES.md) (not hardcoded) — which also proves
the code and the normative document have not drifted apart.

| Check | What it requires | Protects |
|-------|------------------|----------|
| `priority-valid` | priority level is within the 1..10 scale from PRIORITIES.md | Art. 5 — priority by the nature of need, not by identity |
| `safeguards` | priority does NOT switch off anti-abuse: `limit_ok`/`collective_review`/appeal window | Art. 7 — high priority speeds up but never disables protection (PRIORITIES, rule 2) |
| `collective-review` | a payment is confirmed by ≥2 independent reviewers | Art. 7 — no single-person approval of a payment (ANTI-ABUSE §3) |
| `staged-payments` | staging is valid (`1 <= index <= of`) | Art. 7 — splitting reduces risk (ANTI-ABUSE §1) |
| `applicant-privacy` | the record holds no personal data (name/e-mail/phone/…), only the pseudonymous `case_id` | Art. 5/6 — applicant dignity and privacy |

```bash
python3 ai-agents/fairness_agent.py          # human-readable report
python3 ai-agents/fairness_agent.py --json    # machine-readable (for CI/other agents)
```

Exit code `0` — distribution is fair; `1` — a violation was found (this is a
**signal** to the community, not an action: the agent fixes nothing and controls nothing).

A **test invariant** [`test_fairness.py`](test_fairness.py) proves Fairness works rather
than being "green by default": for every violation (priority off the scale, limits/appeal
window removed, single-person approval, broken staging, personal data/e-mail in the
record) the agent must return "red", while a valid payment and an empty registry stay
"green" with no false positives.

CI [`.github/workflows/ai-agents.yml`](../.github/workflows/ai-agents.yml) runs Audit +
Guardian (+test) + Fairness (+test) on every push/PR.

## Reputation agent — what it does and how to run it

`reputation_agent.py` is a read-only static analysis: it proves the
"1 person = 1 vote" model is preserved **in code**
([`contracts/contracts/Reputation.sol`](../contracts/contracts/Reputation.sol)) and
**in the voting settings** ([`governance/snapshot/space.json`](../governance/snapshot/space.json)),
not just "on paper" per [`docs/GOVERNANCE.md`](../docs/en/GOVERNANCE.md) §2–§3.

| Check | What it requires | Protects |
|-------|------------------|----------|
| `soulbound` | the badge has no transfer functions (`transfer`/`approve`/…) — the vote is non-transferable | Art. 2 / §2 — voting right is not for sale and cannot be bought up |
| `bounded-weight` | `votingUnits`: non-member → 0; member → `1 + min(points, cap)`, corridor `[1..1+cap]` | Art. 2 / §2 — power of money is impossible (prohibition #5) |
| `no-funds` | the reputation layer moves no funds (`payable`/`.transfer`/`.call{value}`/…) | Art. 9 / §3 — "uniqueness ≠ power" |
| `roles-separated` | `verifier` only mints/revokes the badge; `governor` only changes parameters; roles not mixed | §3 — whoever confirms a person does not run governance |
| `off-chain-equal` | the Snapshot strategy is the equal `ticket` value=1 (not balance-weighted plutocracy), members-only voting | Art. 2 / §2,§4 — the off-chain signal is also "1 person = 1 vote" |

```bash
python3 ai-agents/reputation_agent.py          # human-readable report
python3 ai-agents/reputation_agent.py --json    # machine-readable (for CI/other agents)
```

Exit code `0` — the voting model is intact; `1` — a threat was found (this is a
**signal** to the community, not an action: the agent fixes nothing and controls nothing).

A **test invariant** [`test_reputation.py`](test_reputation.py) proves Reputation works
rather than being "green by default": for every threat (a transfer function added, weight
without a cap / by balance, the contract moving funds, mixed roles, a plutocratic Snapshot
strategy, `ticket` value≠1, non-members allowed to vote) the agent must return "red", while
a correct contract+settings stay "green" with no false positives (including ignoring
mentions inside comments).

CI [`.github/workflows/ai-agents.yml`](../.github/workflows/ai-agents.yml) runs Audit +
Guardian (+test) + Fairness (+test) + Reputation (+test) + Housing (+test) +
Documentation (+test) on every push/PR.

## Housing agent — what it does and how to run it

`housing_agent.py` is a domain helper for housing cases. Read-only, it proves that the
core targeted-disbursement principle — **"help is not handed out as cash; it pays the
service provider (the landlord) directly"** — is built **into the code**
([`contracts/contracts/Disbursement.sol`](../contracts/contracts/Disbursement.sol)),
not just described in [`docs/ESCROW-TARGETED-DISBURSEMENT.md`](../docs/en/ESCROW-TARGETED-DISBURSEMENT.md);
and it checks housing registry records (`category=housing`).

Part A — targeted-escrow contract invariants:

| Check | What it requires | Protects |
|-------|------------------|----------|
| `release-to-provider-only` | `release(id, amount)` takes no recipient address; the tranche goes strictly to the case's `c.provider` | Art. 5 / ESCROW §2 — pay the provider directly, not "into hand" |
| `provider-fixed` | the provider address is fixed in `open`, never reassigned (no `setProvider`/`.provider =`) | Art. 5 / ESCROW §3 — the only possible recipient is set in advance |
| `refund-to-treasury` | `refund` returns the remainder to `treasury`, not to the recipient/provider | Art. 7 / ESCROW §2 — service not rendered → funds are not lost, go back to the fund |
| `tranche-limit` | `release` caps a single tranche at `maxRelease` | ANTI-ABUSE §1–§2 — staged payments/limits lower risk |
| `guardian-cannot-move` | only `executor` moves funds; `guardian` can only pause (moves no funds) | Art. 2/9 — "safety ≠ power" |

Part B — housing registry records (`category=housing`):

| Check | What it requires | Protects |
|-------|------------------|----------|
| `targeted-escrow` | the record has a `provider` + `escrow_id` (link to the on-chain escrow) | Art. 3/5 / ESCROW §2 — pay the provider directly, visible in the registry |
| `provider-onchain` | `provider` is a valid non-zero `0x`+40 hex address | Art. 5 / ESCROW §5 — the provider address is public, not the person |
| `category-priority` | a `category=housing` level equals "housing_loss" from [`PRIORITIES.md`](../docs/en/PRIORITIES.md) (read from the doc) | Art. 5 — priority by the nature of the need (housing), not by identity |

```bash
python3 ai-agents/housing_agent.py          # human-readable report
python3 ai-agents/housing_agent.py --json    # machine-readable (for CI/other agents)
```

Exit code `0` — the targeted-disbursement model is intact; `1` — a deviation was found
(a **signal** to the community, not an action: the agent fixes nothing and controls nothing).

A **test invariant** [`test_housing.py`](test_housing.py) proves Housing works rather than
being "green by default": for every deviation (release with a recipient parameter, a
`setProvider` added, `refund` to the recipient instead of treasury, the tranche cap removed,
`release` under `guardian`, a record without `escrow_id`, a malformed/zero provider address,
a wrong housing priority) the agent must return "red", while a correct contract+records stay
"green" with no false positives (including ignoring mentions inside comments and non-housing
records).

CI runs Housing (+test) in the same workflow.

## Documentation agent — what it does and how to run it

`documentation_agent.py` turns two project rules into a machine check: the
operator's instruction that **"all documentation is bilingual (RU↔EN)"** and the
constitutional **verifiability** (Art. 3) / **openness** (Art. 6). Read-only over
git-tracked `.md` files (over what is actually published):

| Check | What it requires | What it guards |
|-------|------------------|----------------|
| `bilingual-pairs` | every public doc has an RU↔EN counterpart (pairing rule from the path) | Art. 6 — openness/clarity; "all documentation is bilingual" |
| `language-switcher` | the top of the doc has a correct `[Русский]·[English]` switcher pointing to the paired file | Art. 6 — availability in both languages |
| `link-integrity` | every relative link in `.md` resolves to an existing file/directory | Art. 3 — verifiability; a doc with no broken links is actually readable |

**Pairing rule** (derived from the path, not hardcoded per file):
`docs/NAME.md` ↔ `docs/en/NAME.md`; `<dir>/README.md` ↔ `<dir>/README.en.md`;
a root-level `NAME.md` ↔ `NAME.en.md` (e.g. `REPO-STRUCTURE`, `AUTHORS`).
Single-language internal files (`BUILDER.md`, `LAUNCH.md`, `PROGRESS.md`,
`DECISIONS.md`, `comms/*`) are excluded by design — they are the circuit's
back-office, not the fund's public documentation. External links
(`http`/`mailto`/anchors) and the contents of ```…``` code fences are not part of
the link check — no false positives.

```bash
python3 ai-agents/documentation_agent.py          # human-readable report
python3 ai-agents/documentation_agent.py --json    # machine-readable (for CI/other agents)
```

Exit code `0` — documentation is intact and bilingual; `1` — a discrepancy was
found (a **signal** to the community, not an action: the agent does not write
translations or fix links).

The **invariant test** [`test_documentation.py`](test_documentation.py) proves
that Documentation works rather than being "green by default": for every
discrepancy (no EN mirror, no RU original, a missing/broken/swapped switcher, a
broken relative link) the agent must return "red", and on clean bilingual
documentation — "green" with no false positives (single-language internal files,
external links, and code fences must not trip it). On its first run the agent
immediately caught a real gap — `governance/ipfs/README.md` and
`governance/registry/README.md` had no EN mirrors; they were added (now 8/8).

CI runs Documentation (+test) in the same workflow.

## Rails (for all agents in this directory)

- No private keys/secrets/real funds; no mainnet.
- Read-only with respect to funds and rights; a finding is a signal, not an action.
- Open, reproducible code; no network and no third-party dependencies where possible.
- Applicant privacy (no personal data).
- Bilingual RU↔EN documentation in the same commit.
