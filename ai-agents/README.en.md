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
| **Fairness** | Checks fairness of distribution per [`PRIORITIES.md`](../docs/en/PRIORITIES.md): is priority respected, is there bias/discrimination. | ⏳ planned |
| **Reputation** | Computes/validates voting weights per [`GOVERNANCE.md`](../docs/en/GOVERNANCE.md) §2–§3: "1 person = 1 vote", soulbound, "uniqueness ≠ power". | ⏳ planned |
| **Housing** | Domain helper for housing cases (escrow paying the provider directly per [`ESCROW-TARGETED-DISBURSEMENT.md`](../docs/en/ESCROW-TARGETED-DISBURSEMENT.md)). | ⏳ planned |
| **Governance** | Helps with the proposal lifecycle (format, quorum, timing, ties to the constitution); does not vote itself. | ⏳ planned |
| **Mediator** | Assists with disputes/appeals per [`ANTI-ABUSE.md`](../docs/en/ANTI-ABUSE.md) — structures, does not decide. | ⏳ planned |
| **Documentation** | Watches RU↔EN sync, link integrity, freshness of the repo map. | ⏳ planned |

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

## Rails (for all agents in this directory)

- No private keys/secrets/real funds; no mainnet.
- Read-only with respect to funds and rights; a finding is a signal, not an action.
- Open, reproducible code; no network and no third-party dependencies where possible.
- Applicant privacy (no personal data).
- Bilingual RU↔EN documentation in the same commit.
