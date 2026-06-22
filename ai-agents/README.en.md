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
| **Governance** | Helps with the proposal lifecycle (format, quorum, timing, ties to the constitution); does not vote itself. | ✅ framework (`governance_agent.py`) |
| **Mediator** | Structures disputes/appeals per [`ANTI-ABUSE.md`](../docs/en/ANTI-ABUSE.md) §6 (appealability of sanctions, people decide, independence, deadlines) — structures, **does not decide**. | ✅ scaffold (`mediator_agent.py`) |
| **Documentation** | Watches RU↔EN bilinguality (a pair + a language switcher for every public doc) and the integrity of relative links across all `.md`. | ✅ scaffold (`documentation_agent.py`) |

We build them one by one, "to green", with no token stubs. The scaffold opens with
**Audit** — useful right away: one command checks the whole governance layer.
The 8/8 scaffold is complete; on top of it sits the service **Run-All meta-agent**
(`run_all.py`), a single entry point that runs all eight and folds them into one
verdict (see the "Run-All meta-agent" section below).

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

A **test invariant** [`test_audit.py`](test_audit.py) proves that Audit **folds the
verdict honestly, not "green by default"**: a check with `exit=1` yields `fail`, a
crashed/missing command yields `error` (not a silent "pass"), and any `fail`/`error`
turns the overall verdict `red`. Beyond synthetics it feeds the real rail validators a
genuinely broken governance artifact (a Safe config with a mainnet `chain_id`; a
Snapshot config with a plutocratic strategy) in a temporary copy and proves Audit
raises it to "red", while staying "green" on the healthy repository.

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
Documentation (+test) + Governance (+test) + Mediator (+test) on every push/PR.

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
| `anchor-integrity` *(soft)* | a link anchor `FILE.md#section` (and `#section` within the same file) points to a real heading (GitHub-style slug) | Art. 3 — verifiability; links don't rot when sections are renamed |
| `glossary-coverage` *(soft)* | key technical terms (DAO, escrow, multisig, …) have an entry in the glossary (RU+EN) | Art. 3/6 — clarity/explainability (`PTD-0040`) |
| `glossary-no-dead` *(soft)* | every glossary entry's term is actually used in at least one normative document (inverse of `glossary-coverage`) | Art. 3/6 — clarity/explainability (`PTD-0040`) |
| `constitutional-prohibitions` *(soft)* | public texts (`.md` + the `web/*.html` storefront) make no forbidden promises: yield/profit, investment/pyramid, pay-to-recruit (referrals) — our own "this is NOT an investment" disclaimers and prohibition lists do not count as violations | Art. 3/6 + `PRINCIPLES.md` "Constitutional prohibitions" for public texts |

> The `glossary-coverage` and `glossary-no-dead` checks are **soft**: they only warn
> (so the glossary neither falls behind the documents nor grows stale) and **never
> turn the verdict red** — green stays green. The number of warnings is shown in the
> report (`warnings` field). `glossary-no-dead` is deliberately conservative (a term
> is searched by many keys: the main phrase, parenthetical variants, individual
> significant words) — it would rather stay silent than raise a false alarm.

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

## Governance agent — what it does and how to run it

`governance_agent.py` turns the **proposal lifecycle** from
[`GOVERNANCE.md`](../docs/en/GOVERNANCE.md) into a machine check: so the governance
configuration cannot drift away from the constitution silently. Read-only over two
governance JSON configs
([`governance/snapshot/space.json`](../governance/snapshot/space.json) and
[`governance/safe/safe.config.json`](../governance/safe/safe.config.json)), no
network. It **does NOT vote, submit, or move anything.**

| Check | What it requires | What it guards |
|-------|------------------|----------------|
| `one-person-one-vote` | vote strategy = `ticket` value=1; not a single plutocratic (balance-weighted) one | Art. 2 + ban #5 — the vote comes from a person's uniqueness, not money |
| `timed-vote` | the vote has a positive duration (`delay` and `period` > 0) | GOVERNANCE §7 — "quorum + term", a time-bounded window |
| `off-chain-signal` | `off_chain_signaling=true` and every proposal type `binding=false` | Art. 4 + §5 — Snapshot discusses; Safe/Timelock executes after the vote |
| `proposal-binding` | money/constitution proposal types are tied to the right docs and flags | Art. 5 + §7–§8 — disbursement and amendments stay strictly within the norms |
| `multisig-not-sole` | Safe threshold ≥2 and strictly below the number of owners | Art. 5 + §5 — no one moves funds single-handedly (3-of-5) |
| `lifecycle-links` | every `docs/`-/`governance/` link in the configs resolves to an existing file | Art. 3 — verifiability: the lifecycle is tied to real docs |

**Type binding** (`proposal-binding`): the `disbursement-direction` type must link
[`PRIORITIES.md`](../docs/en/PRIORITIES.md) **and** [`ANTI-ABUSE.md`](../docs/en/ANTI-ABUSE.md);
the `constitution-amendment` type must link [`CONSTITUTION.md`](../docs/en/CONSTITUTION.md)
**and** carry `requires_supermajority=true` (a constitutional amendment requires a
supermajority, Art. 10).

```bash
python3 ai-agents/governance_agent.py          # human-readable report
python3 ai-agents/governance_agent.py --json    # machine-readable (for CI/other agents)
```

Exit code `0` — the governance configuration is consistent with the constitution;
`1` — a discrepancy was found (a **signal** to the community, not an action: the
agent does not edit the config or vote).

The **invariant test** [`test_governance.py`](test_governance.py) proves that
Governance works rather than being "green by default": for every deviation
(balance-weighted vote, `ticket` value≠1, plutocracy hidden in `validation`, a
zero duration, a `binding=true` type, disbursement/amendment without ties to the
norms, a multisig threshold `=1` or `=owner count`, a broken link, a missing
`space.json` altogether) the agent must return "red", and on correct configs —
"green" with no false positives (26/26). CI runs Governance (+test) in the same
workflow.

## Mediator agent — what it does and how to run it

`mediator_agent.py` turns the **right to appeal** (mechanism #6 "Appeals" of
[`ANTI-ABUSE.md`](../docs/en/ANTI-ABUSE.md)) into a machine check: so the transparent
path to contest a rejection/sanction does not stay a slogan and cannot drift away
from the constitution silently. Read-only over the process artifact
[`governance/mediation/dispute-process.json`](../governance/mediation/dispute-process.json),
no network. **The Mediator structures the dispute but NEVER decides it** (art. 9.2):
independent people decide; the agent only checks the shape of the process and reports.

| Check | What it requires | What it guards |
|-------|------------------|----------------|
| `appeal-for-every-sanction` | every canonical sanction (rejection, reputation, freeze, exclusion) has an appeal to an existing stage | §6 — a transparent path to contest a rejection/sanction |
| `mediator-not-decider` | deciding stages are run by people (`min_deciders` ≥2), not AI/mediator/automation and not one person | art. 9.2 + §3 — the AI is not an organ of power; a collective decides |
| `independent-review` | the first deciding stage from the entry has `decider` ≠ the sanction's `issued_by` | §3 — independence; you cannot review your own decision |
| `valid-lifecycle` | exactly one start, a terminal exists, transitions resolve, no dead ends/orphans, all reachable | art. 3 — verifiability: a coherent state machine |
| `bounded-timelines` | every non-terminal stage has `deadline_seconds` > 0 | art. 3 + §6 — an appeal never hangs forever |
| `process-links` | every `docs/`-/`governance/` link in the process resolves to an existing file | art. 3 — tied to real norms |

**Lifecycle** (artifact): `intake` (intake, structured by the Mediator) → `review`
(≥2 independent reviewers decide) → `escalation` (guardian council ≥3) → `resolved`
(terminal, recorded in the registry). Deciding rests only with people and only
collectively; the Mediator agent is allowed solely on non-deciding stages.

```bash
python3 ai-agents/mediator_agent.py          # human-readable report
python3 ai-agents/mediator_agent.py --json    # machine-readable (for CI/other agents)
```

Exit code `0` — the appeal process is consistent with the constitution; `1` — a
discrepancy was found (a **signal** to the community, not an action: the agent does
not edit the process or decide disputes).

The **invariant test** [`test_mediator.py`](test_mediator.py) proves that Mediator
works rather than being "green by default": for every deviation (a non-appealable/
missing sanction, an `appeal_entry` to nowhere, a dispute decided by AI or one
person, self-review `decider==issued_by`, a dead end/nonexistent transition/no
terminal/two start stages, a zero deadline, a broken link, a missing
`dispute-process.json` altogether) the agent must return "red", and on a correct
process — "green" with no false positives (26/26). CI runs Mediator (+test) in the
same workflow. **This closes the scaffold of all eight AI agents (8/8).**

## Run-All meta-agent — a single entry point

Once the scaffold of all eight agents is complete, you want one command that runs
them all and folds them into a single verdict. That is `run_all.py` — a **service
meta-module** (Art. 9): it checks nothing on the merits itself and certainly
disposes of nothing; it only launches the eight and collects their `--json` reports
into an overall "green/red".

Why:

- **a local self-check in one command** instead of eight manual runs;
- **CI collapses from ~15 steps to two** (`--with-tests` runs both the agents and
  their test invariants);
- **a machine-readable summary** (`--json`) for dashboards and other agents.

```bash
# Run all eight agents and fold into one verdict (standard library only):
python3 ai-agents/run_all.py

# Also run the agents' test invariants (test_*.py — "red is really caught"):
python3 ai-agents/run_all.py --with-tests

# Pass smart-contract tests through to Audit (requires Node/npm):
python3 ai-agents/run_all.py --with-contracts

# Machine-readable report:
python3 ai-agents/run_all.py --json

# Write a compact machine-readable "status traffic-light" to a file artifact:
python3 ai-agents/run_all.py --with-tests --status-out governance/status/run_all_status.json
```

Exit code `0` — all green; `1` — at least one agent (or a test invariant under
`--with-tests`) is red. The meta-agent treats an agent as "red" not only by its
verdict but on any anomaly too — invalid JSON (the agent crashed) or a mismatch
"verdict=green but exit code ≠ 0". "Red" is a **signal**, not an action: the
meta-agent fixes nothing.

Beyond the eight agents the meta-agent also runs the **structure guard**
([`structure_guard.py`](structure_guard.py), see below) and shows it as a separate
line in the summary — `guard 10/10, guard soft warnings: N`. Its hard "red" (a
breach of a required quality standard) fails the overall verdict alongside the
agents, while its **soft warnings** (severity=soft — e.g. a CI step without a
human-readable name) are surfaced as a count AND **line by line** (under the guard
line, a list `⚠ [check] step: problem`) and do **not** fail the build: this way the
operator's summary keeps the readability hints, explains them without a separate
guard run, yet does not turn red over them. In `--json` the same lines live under
the `guard_warning_lines` key. If the guard is absent from the directory, the line
is hidden and it does not affect the verdict.

The **`--status-out PATH`** flag additionally writes a compact machine-readable
**"status traffic-light"** to a file artifact (helper `build_status`): the overall
verdict, agent/test scores, the guard summary (count and lines of soft warnings)
and one line per agent. The artifact is **deterministic** — no wall-clock time, so
in git it only goes "dirty" when the verdict/score changes; the `schema_version`
field versions the format. The canonical artifact lives at
[`governance/status/run_all_status.json`](../governance/status/) (with a bilingual
README) — the basis for a public status indicator with no external services. It is
written on any verdict, including `red` (the indicator honestly shows a red light too).

The **test invariant** [`test_run_all.py`](test_run_all.py) proves the folding
works rather than being "green by default": on fake agents (green/red/crashed/
anomalous), fake tests and a fake guard (soft warnings do not fail, hard "red"
fails, an absent guard is not applicable; the warning lines themselves are shown
under the guard line; the status artifact is written deterministically and on a red
verdict too) it checks that red really folds into red and green does not
fail falsely (39/39). CI runs `test_run_all.py` + `run_all.py
--with-tests` — two steps instead of fifteen.

## Structure-Guard — keeps the directory's quality standards

By Stage 6 we set quality standards, but until now nothing guarded them
automatically — they could be broken by accident and go unnoticed.
`structure_guard.py` turns them into a machine check (Art. 9 — a service module
that fixes nothing):

| Check | What it guards |
|-------|----------------|
| `agents-have-invariants` | Every `*_agent.py` has a paired `test_<name>.py` — an agent proves it catches "red" rather than being "green by default" (this is the gap that was closed for Audit in session 33). |
| `no-orphan-tests` | Every `test_*.py` has a source module (`<name>_agent.py` or `<name>.py`) — a test file does not linger after a rename/removal. |
| `sol-parsing-centralized` | No `*_agent.py` keeps a local copy of the Solidity-parsing helpers (`strip_solidity_comments`/`function_body`/…) — they are imported from the shared [`solidity_scan.py`](solidity_scan.py), not duplicated (or the copies silently drift). |
| `run-all-covers-all` | Every `*_agent.py` is in the `AGENTS` list of the meta-agent [`run_all.py`](run_all.py), and every `test_*.py` is in the `TESTS` list (and vice versa: no dangling references) — a new agent or test cannot be added bypassing the shared CI run. |
| `trigger-paths-include-agents` | The workflow trigger paths (`on.push.paths` and `on.pull_request.paths`) contain `ai-agents/**` — otherwise editing an agent would not start CI, and coverage is bypassed even earlier, at the trigger level rather than the command. |
| `ci-has-required-steps` | The workflow [`.github/workflows/ai-agents.yml`](../.github/workflows/ai-agents.yml) contains every command from the single list of required CI steps (`REQUIRED_WORKFLOW_COMMANDS`): currently `run_all.py --with-tests` (runs all agents and their test invariants — without `--with-tests` or if bypassed they would not run) and `test_run_all.py` (proves the fold into one verdict works: red→red). Generalizes the former pinpoint checks `ci-calls-run-all` and `ci-runs-test-run-all`: a new required CI step is one line in the list, with no proliferation of near-identical checks. |
| `ci-required-cmd-own-step` | Every required command has its OWN dedicated `run:` step. The check above sees a command "anywhere" in the file — including a comment or a step name; this one inspects the `run:` step bodies themselves and requires each command to (a) actually run in at least one step and (b) not share a step with another. Otherwise a failure of one masks the other: in a single `run:` joined by `&&` the second command never runs after the first fails, and one left only in a comment never runs at all. Its own step — its own exit code, its own failure in plain sight. |
| `ci-step-has-name` *(soft — warns, does not fail CI)* | The `run:` step of a required command has a human-readable `- name:`. An extension of the previous check toward readability: without a name a failed step is shown in the GitHub Actions logs as a bare command (`python3 ai-agents/run_all.py --with-tests`) rather than in plain words ("Run all agents"). This does not break coverage, so the check only **warns** (severity=soft) and does not turn the verdict red — a hint to improve readability for people (Art. 3 "clarity"). |
| `ci-step-name-unique` *(soft — warns, does not fail CI)* | Two `run:` steps do not carry the SAME `- name:`. An extension of the previous check: a step does have a name, but if it repeats, a failed step reads ambiguously in the GitHub Actions logs ("which of the two same-named ones?"). It also only **warns** (severity=soft) and does not turn the verdict red. Unnamed steps are skipped — those are `ci-step-has-name`'s concern. |
| `ci-step-has-body` *(soft — warns, does not fail CI)* | A step with `- name:` has a body `run:`/`uses:` (it is not empty). An extension of the previous check toward an honest step map: if a list item carries `- name:` but NEITHER `run:` NOR `uses:`, it is almost always an indentation typo — the step body "fell out" of it, so the step does nothing while still looking real in the GitHub Actions UI. It also only **warns** (severity=soft): an actual missing required command is caught by the hard checks above, while this one keeps the CI step map readable for people (Art. 3 "clarity"). |
| `issue-form-labels-defined` | Every label referenced by an issue form (`labels:` in [`.github/ISSUE_TEMPLATE/*.yml`](../.github/ISSUE_TEMPLATE) — `bug`/`idea`/`governance`/`safety`) is defined in the label catalogue [`.github/labels.yml`](../.github/labels.yml). Previously the colour and description of those labels lived only in GitHub settings, set by hand — not reproducible. Now the source of truth is an open file, and the guard goes red if a form references a label missing from the catalogue (set by hand / a typo). The violation names exactly the missing label and the form. |

```bash
python3 ai-agents/structure_guard.py          # human-readable report
python3 ai-agents/structure_guard.py --json    # machine-readable report
```

The **test invariant** [`test_structure_guard.py`](test_structure_guard.py) proves
on poisoned temporary directories (an agent without a test; an orphan test; an
agent with a local copy of `.sol` parsing; an agent/test bypassing `run_all`; a
dangling `run_all` reference; the workflow missing `run_all --with-tests` or
`test_run_all.py`; two commands sharing one `run:` step; a command only in a
comment; trigger paths missing `ai-agents/**`; a `run:` step without `- name:`,
two steps with the same `- name:`, and a named step without a `run:`/`uses:`
body — softly warn, do not fail) that the guard
really turns red (and on the soft checks only warns), while a clean directory
stays green (89/89). It is included in
`run_all --with-tests`, so adding an agent without a test, a copy of `.sol`
parsing, an agent/test that bypasses the shared CI run, dropping `ai-agents/**`
from the workflow triggers, or removing any required workflow command turns it red.

The `run_all` meta-agent now **runs the guard too** and shows it as a separate
line in the summary: a hard "red" fails the overall verdict, while its soft
warnings appear as `guard soft warnings: N` and, below it, a line-by-line list
`⚠ [check] step: problem` — so the warnings are visible and explained in the
operator's summary without failing the build.

## Rails (for all agents in this directory)

- No private keys/secrets/real funds; no mainnet.
- Read-only with respect to funds and rights; a finding is a signal, not an action.
- Open, reproducible code; no network and no third-party dependencies where possible.
- Applicant privacy (no personal data).
- Bilingual RU↔EN documentation in the same commit.
