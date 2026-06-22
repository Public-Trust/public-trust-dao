[Русский](SECURITY.md) · [English]

# Security Policy — Public Trust DAO

Public Trust DAO is a **public good, NOT an investment**. This project is about
**the safety of a shared wallet, not power over it**. Responsible vulnerability
reporting is therefore part of the mission itself: far better that a friendly
person find a flaw and report it privately than that someone exploit it.

This file is the canonical security policy (GitHub recognizes it and surfaces the
"Report a vulnerability" button / the "Security" tab). It complements
[`CODE_OF_CONDUCT.en.md`](CODE_OF_CONDUCT.en.md) (breaking the safety rails =
breaking the code) and the automated
[Guardian agent](ai-agents/guardian_agent.py), which machine-checks the rails on
every push.

Unfamiliar technical words from this document are explained in plain language in the
[glossary](docs/en/GLOSSARY.md) — the "Safety and technology" group.

---

## Current project status (matters for severity)

The project is at the **bootstrap / TESTNET-first** stage:

- **there are no real funds in the system** — the [`contracts/`](contracts/) are
  tested only on the in-process/test network, no mainnet and no real money;
- **there are no private keys holding real funds**, and none must ever live in
  the repository (see the rails below);
- the address for receiving real support is **not published** and will not appear
  until an independent audit, a community decision, and a 3-of-5 Safe multisig of
  living people (see [`docs/SUPPORT-MODEL.md`](docs/SUPPORT-MODEL.md)).

This means: today a vulnerability cannot lead to theft of real funds — but it
**can undermine trust and verifiability**, which for a public good matters no
less. Report findings just as seriously: whatever is not fixed on testnet will
leak into mainnet.

## What counts as a vulnerability

Report it if you found:

- **A smart-contract bug** in [`contracts/`](contracts/) that breaks the encoded
  constitutional properties: a way to move funds around the `executor`/the vote,
  bypass the per-release cap (`maxRelease`), redirect a targeted disbursement
  away from the provider, bypass the Timelock delay, bypass the guardian veto,
  break "one person = one vote" / the soulbound badge, etc.
- **A bypass of the safety rails**: a way to slip a mainnet config, real funds,
  or private keys past the validators
  ([`scripts/safe_config.py`](scripts/safe_config.py),
  [`scripts/snapshot_config.py`](scripts/snapshot_config.py), the Guardian agent).
- **A secret leak**: a committed key, token, seed phrase, pulse state file, or
  any other secret in the repository history.
- **An attack on verifiability**: a way to silently tamper with a public registry
  record ([`governance/registry/`](governance/registry/)) or the IPFS manifest so
  that `verify` does not notice it; a hash-chain desync.
- **An issue on the public site** [`web/`](web/): injection, leakage of visitor
  data, a hidden outbound request/tracker (the site must send nothing about the
  visitor — that is a transparency requirement).
- **A supply-chain/CI problem**: a way to slip malicious code through a workflow,
  or a dependency that makes the build unsafe/unverifiable.

## What is NOT a vulnerability (via this channel)

- "What if someone deploys this to mainnet with real money" — that is explicitly
  forbidden by the rails and not done; the scenario is already accounted for
  (TESTNET-first).
- Promises of yield / a pyramid / pay-for-recruitment — that breaks the
  **principles** ([`docs/PRINCIPLES.md`](docs/PRINCIPLES.md)) and the code, not
  technical security; report such things via an issue or
  [`CODE_OF_CONDUCT.en.md`](CODE_OF_CONDUCT.en.md).
- Typos, broken relative links, translation issues — a regular issue (forms in
  [`.github/ISSUE_TEMPLATE/`](.github/ISSUE_TEMPLATE/)).
- Spam, phishing third-party sites impersonating the project — tell the operator,
  but it is outside our code.

If you are unsure whether something is a vulnerability, report it privately and
we will sort it out.

## How to report (privately)

**The main rule: do not publish working exploitation steps in a public issue/PR.**
Privately first, give time to fix.

1. **If GitHub Security Advisories is enabled** — click "Report a vulnerability"
   on the repository's **Security** tab (a private advisory draft).
2. **Private email.** A permanent `security@` address will be published once the
   project's official mail is set up (see
   [`docs/en/EMAIL-SETUP.md`](docs/en/EMAIL-SETUP.md)). Until then, escalation is
   handled by the project's human operators/guardians.
3. **The "safety rail" form** in [`.github/ISSUE_TEMPLATE/`](.github/ISSUE_TEMPLATE/)
   — for NON-sensitive rail observations (no working exploits).

In your report, where possible state: what you found, where (file/contract/line),
how to reproduce, which constitutional property it breaks, and why it matters.
**Never attach anyone's personal data or real secrets** — test values are enough
for a demonstration.

## What to expect after reporting

- **Acknowledgment of receipt** within a reasonable time (goal: a few days;
  precise SLAs will arrive with the official mail and a standing guardian team).
- **Assessment and dialogue** — we will investigate, reproduce, and agree on
  severity.
- **A fix and coordinated disclosure**: fix first, then publish the gist. The fix
  and the fact of the finding are recorded in the public decisions registry
  (without details that are dangerous before the fix, and without the reporter's
  identity if they prefer not to be named).
- **Recognition.** With your consent we will thank you in an acknowledgments
  section. There is no monetary reward — this is a public good, not a commercial
  bug bounty; the value of the contribution is recognized, but **a contribution ≠
  power over the treasury** ([`AUTHORS.en.md`](AUTHORS.en.md)).

## Safe harbor for security research

We welcome good-faith security research and **will not pursue** you for it as long
as you:

- work only with the public code, a test/local network, and **test** values — no
  real funds, no mainnet;
- do not touch infrastructure not described in this repository (the host, other
  projects, the pulse/`.env`/`logs/` — those are not a research target);
- do not violate people's privacy: do not extract or publish personal data of
  applicants or participants;
- give reasonable time to fix before public disclosure.

## Future-proofing (including against future quantum computers)

**In plain words.** Today's locks (the digital signatures used to confirm payments
and identity) are sound. But one day very powerful "quantum" computers may appear
that could, in theory, pick some of these locks. There is no real threat yet —
specialists estimate it is years away. But attackers have a "harvest now, decrypt
later" trick (hoarding other people's data now to crack it later, once the
hardware allows). So it is reasonable to prepare now — **without harming the
launch**.

Our stance is honest and free of hype: we do **not** drag heavy
"quantum-resistant" cryptography into the smart contracts right now (on a
blockchain it is still immature, expensive, and would stall the launch with no
real benefit). Instead we **lay the foundation** so the switch is easy when the
time comes:

1. **Swappable locks (the main thing in our power).** We design the system so the
   signature/encryption method can be replaced in the future without rebuilding
   the whole project — like changing a lock without breaking the door. This is the
   most important decision, and it is entirely up to us.
2. **Nothing secret on the blockchain — only facts and fingerprints.** We already
   do this: personal data never goes on-chain (see
   ["Identity verification without surveillance"](docs/en/IDENTITY-VERIFICATION.md)
   and ["Signed and traceable"](docs/en/ACCOUNTABILITY.md)). With no secrets in
   the public chain, there is almost nothing to crack later — the "harvest now,
   decrypt later" trick is largely defused.
3. **Today — modern strong standards, keys held by the person.** The key stays
   with its owner (on a hardware wallet where possible) and can always be rotated.
   The fewer of other people's secrets the fund holds, the less there is to lose.
4. **For our own parts — prepare the migration in advance.** Where the stack is
   entirely ours (data storage, correspondence with applicants), we can migrate to
   quantum-resistant standards ourselves once they mature. Where we depend on
   someone else's network (Ethereum/Polygon), we move with it: when they enable
   protection, so do we.
5. **Watch and switch when it matures.** This is a living task: track the readiness
   of the standards and what the networks do, and switch on time — not earlier (so
   as not to stall the launch) and not later (so as not to fall behind).

In short: **the point is flexibility, not a race.** We build so that swapping a
lock is easy, and we keep only non-secret things in the public chain.

### Protecting the fund's money (the treasury) — what actually guards the funds

This is the main reason the section exists: how the **shared wallet's money** is
protected — both today and against future quantum computers.

- **Several keys held by different people (3-of-5 multisig).** Moving funds
  requires signatures from several independent guardians, not one. A single stolen
  or cracked key decides nothing — you would have to compromise several people at
  once. That raises the bar both today and in a quantum future (cracking one key
  is far easier than several at once). See [`governance/safe/`](governance/safe/)
  (the 3-of-5 Safe mock-up).
- **The ability to "migrate" the treasury (the main future-proofing hook).** We
  design the treasury so the funds can be moved to a new, quantum-resistant wallet
  or contract once the network offers such signatures. The money is **not locked**
  into a scheme that cannot be upgraded; a migration path is provided in advance.
  Upgradeability matters more than today's specific algorithm.
- **Rotating and revoking guardian keys without losing funds.** If a guardian's
  key is compromised or a person leaves, their signature can be replaced/revoked
  while the money stays put. The set of signers changes; the treasury does not.
- **A cold reserve.** The bulk of the money sits in "cold" (offline) storage, with
  only a working minimum on the "hot" address for current disbursements. The less
  often the main public key appears on the network, the smaller the surface for a
  future attack.
- **Follow the network.** When Ethereum/Polygon enable quantum-resistant
  signatures and smart accounts, we migrate the treasury onto them. Until then —
  multisig, key hygiene, cold reserve.

**Honest about priority.** The quantum threat is years away. The real threats to
the money **today** are code bugs, key theft, and social engineering. So protecting
the funds means, first of all, **an independent contract audit + a 3-of-5 multisig
+ key hygiene** — and quantum resistance is a "future" layer delivered through
swappability and migration that **does not delay the launch**. Related to
[the constitution, art. 4 (treasury)](docs/en/CONSTITUTION.md),
[the support model](docs/en/SUPPORT-MODEL.md), and
[targeted disbursement](docs/en/ESCROW-TARGETED-DISBURSEMENT.md).

<details>
<summary><b>Technical section — for developers</b></summary>

- **Crypto-agility as a mandatory design requirement.** Signature and hash
  algorithms are not hard-wired: abstract them behind an interface/scheme version
  so they can be replaced without migrating the entire state. For future on-chain
  parts — bake in a signature-scheme version field and an upgrade path via a vote +
  Timelock (like any `parameter-change`), not a hardcode.
- **"Harvest-now, decrypt-later" threat model.** Mitigated because on-chain we
  publish only predicates/hashes/nullifiers, not ciphertexts with private payloads.
  Long-lived secrets never enter the public immutable layer.
- **Target standards (NIST PQC), once mature for our stack:** ML-KEM (Kyber) for
  key exchange, ML-DSA (Dilithium) and SPHINCS+ for signatures. Hash functions
  (SHA-2/256, used by the registry and the IPFS manifest) are Grover-resistant at
  current lengths — the priority for replacement is asymmetric signatures, not
  hashes.
- **Dependence on L1/L2.** We do not change Ethereum/Polygon transaction
  signatures (ECDSA/EdDSA) — that is up to the networks themselves; our path is a
  wallet abstraction layer and readiness to accept PQC signatures once the network
  supports them (e.g. via account abstraction). Until then — hardware wallets, key
  rotation, minimal secrets held by the fund.
- **Where this already holds:** [`docs/en/IDENTITY-VERIFICATION.md`](docs/en/IDENTITY-VERIFICATION.md)
  (only facts/ZK on-chain), [`docs/en/ACCOUNTABILITY.md`](docs/en/ACCOUNTABILITY.md)
  (on-chain — only a fingerprint, not PII), [`docs/en/GOVERNANCE.md`](docs/en/GOVERNANCE.md)
  (any setting change goes through a vote + Timelock, which is exactly the path for
  enabling a new signature scheme).

</details>

## Constitutional security rails

These rails are honored literally and machine-checked (Guardian agent + CI):

- **TESTNET-first.** No mainnet deployments and no real funds. Real money into
  the contracts — only after an independent audit, a community decision, and a
  3-of-5 Safe multisig of living people.
- **No private keys/secrets in the repository** (`.env` is in `.gitignore`).
- **No one owns it alone:** funds are moved only by the executor following a
  passed vote; the guardian only sets an emergency pause/veto but does not direct
  funds ("safety ≠ power").
- **Everything is verifiable:** code, documents, decisions are public; the
  integrity of the registry and the manifest can be checked by anyone (see
  [`web/transparency.en.html`](web/transparency.en.html)).

## Scope

- The `main` branch of this repository.
- The smart contracts [`contracts/contracts/`](contracts/contracts/) and the
  deploy scripts/tests.
- The rail validators and AI agents [`ai-agents/`](ai-agents/),
  [`scripts/`](scripts/).
- The public site [`web/`](web/) and the CI workflows
  [`.github/workflows/`](.github/workflows/).

Out of scope: the agent's heartbeat/pulse (`scripts/loop.sh`, `report.sh`,
`.env`, `logs/`) — that is operator infrastructure, not a subject of public
research.

## Related documents

- [`CODE_OF_CONDUCT.en.md`](CODE_OF_CONDUCT.en.md) — breaking the rails = breaking the code.
- [`docs/en/ANTI-ABUSE.md`](docs/en/ANTI-ABUSE.md) — abuse protection and the appeal path.
- [`docs/en/PRINCIPLES.md`](docs/en/PRINCIPLES.md) — principles and literal prohibitions.
- [`docs/en/EMAIL-SETUP.md`](docs/en/EMAIL-SETUP.md) — plan for the official mail (`security@`).
- [Guardian agent](ai-agents/guardian_agent.py) — machine-checks the rails on every push.

---

© Public Trust DAO and contributors. Texts — CC-BY-SA-4.0, code — AGPL-3.0.
This is a public good, **not an investment**.
