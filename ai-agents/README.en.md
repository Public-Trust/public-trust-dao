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
| **Guardian** | Watches the safety rails: no private keys/secrets in the repo, no mainnet/real funds, no TESTNET-first violations. | ⏳ planned |
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

## Rails (for all agents in this directory)

- No private keys/secrets/real funds; no mainnet.
- Read-only with respect to funds and rights; a finding is a signal, not an action.
- Open, reproducible code; no network and no third-party dependencies where possible.
- Applicant privacy (no personal data).
- Bilingual RU↔EN documentation in the same commit.
