[Русский](../GLOSSARY.md) · [English]

# GLOSSARY — PUBLIC TRUST DAO

> Key project terms in **plain language**. The goal is to make the documents
> understandable not only to technical people. If you hit an unfamiliar word in
> some document, it is most likely explained here.
>
> Derived from [`CONSTITUTION.md`](CONSTITUTION.md),
> [`PRINCIPLES.md`](PRINCIPLES.md), [`GOVERNANCE.md`](GOVERNANCE.md),
> [`PRIORITIES.md`](PRIORITIES.md) and [`ANTI-ABUSE.md`](ANTI-ABUSE.md).
>
> Registered as a decision in the public registry:
> [`governance/registry/`](../../governance/registry/) (record `PTD-0033`).

---

## How to use

Terms are grouped by meaning: **basics**, **governance and voting**, **money and
aid**, **transparency and verifiability**, **safety**, **personhood
verification**. Within each group they go
from general to specific. Each term has a short, "for a non-technical person"
definition and, where relevant, a link to the normative document where it is
formally fixed.

> If a term feels too technical, that's fine: what matters is grasping the
> **idea**, not the implementation. The project's core thought is simple: **a
> shared, transparent aid fund that nobody owns single-handedly.**

---

## Basics

**Public Trust DAO.**
An open community and infrastructure for **transparent mutual aid**. Not a
company, not a fund with an owner, not an investment product. See
[`MANIFESTO.md`](MANIFESTO.md).

**DAO (decentralized autonomous organization).**
A way to organize without a boss or owner: the rules are written openly (in the
constitution text and in code), and decisions are made by the community through
voting, not by one person. "Decentralized" = power is not in one pair of hands.
"Autonomous" = it runs by rules agreed in advance, not by a director's will.

**Public good.**
Something everyone uses and that nobody owns personally (like clean air or an
open road). The project is a public good, **NOT an investment**: putting
something in here does not and cannot promise a return. See
[`PRINCIPLES.md`](PRINCIPLES.md).

**Constitution.**
The project's main rulebook, by articles: who we are, what is forbidden, how
decisions are made. The project's highest law. See
[`CONSTITUTION.md`](CONSTITUTION.md).

**Manifesto.**
A short statement of the project's meaning and values — "why we exist." See
[`MANIFESTO.md`](MANIFESTO.md).

**Guardrails (safety guardrails).**
Hard boundaries the project never crosses under any circumstances: testnet only
until an audit, no private keys in open code, no promises of returns, no
concentration of power. To break a guardrail is to break the project's rules.
See [`PRINCIPLES.md`](PRINCIPLES.md), [`ANTI-ABUSE.md`](ANTI-ABUSE.md).

**The "NOT an investment / NOT a pyramid" disclaimer.**
A mandatory honest caveat next to any call to action: the project does not make
a profit, does not pay for recruiting people, does not guarantee returns. It
protects people from false expectations — it is not a formality.

---

## Governance and voting

**Governance.**
How the community makes decisions: who can propose, how people vote, how a
decision is executed. See [`GOVERNANCE.md`](GOVERNANCE.md).

**"1 person = 1 vote."**
The base principle: your vote's weight depends on you being a **human
participant**, not on how much money or how many tokens you hold. A vote cannot
be bought, sold, or accumulated. The opposite is plutocracy (see below).

**Plutocracy.**
The power of money: "whoever has more tokens has more votes." The project
**forbids** this — which is exactly why vote weight is capped and does not depend
on balance.

**Soulbound badge (a non-transferable participant badge).**
A digital mark that says "this is a verified, unique participant." "Soulbound" =
"bound to the soul": it **cannot be transferred, sold, or gifted**. That is why
voting rights cannot be bought up. Implemented in the
[`Reputation.sol`](../../contracts/contracts/Reputation.sol) contract.

**Reputation.**
Accumulated recognition for verifiable contribution. It can slightly increase
vote weight, but only within a hard cap — so no new "elite" can emerge. It never
grants the right to dispose of money.

**Sybil resistance.**
A "Sybil attack" is when one person creates many fake accounts to gain many
votes. The defense confirms that behind each vote there is one **unique living
human**. Importantly, confirming uniqueness **does not grant power** over money —
"uniqueness ≠ power." See [`GOVERNANCE.md`](GOVERNANCE.md).

**Quorum.**
The minimum number of votes without which a decision does not count as adopted
(so that important matters are not decided quietly by two people).

**Snapshot (off-chain voting).**
A venue where the community **discusses and signals** through voting without
paying network fees. Snapshot itself **does not move money** — it shows the
community's will. See [`governance/snapshot/`](../../governance/snapshot/).

**Proposal.**
A formally framed question put to a vote: what is proposed, why, how it relates
to the constitution and priorities, and the "for/against" options.

---

## Money and aid

**Treasury.**
The community's shared wallet that aid flows from. Nobody disposes of it
single-handedly — funds move only after a passed vote. The
[`Treasury.sol`](../../contracts/contracts/Treasury.sol) contract.

**Multisignature / multisig, the "3 of 5" scheme.**
A wallet managed by several people together: to do anything, signatures from at
least 3 of 5 guardians are required. One person can neither take the funds nor
freeze everything alone. See [`governance/safe/`](../../governance/safe/).

**Guardian (a human role).**
One of the trusted people whose signature participates in the multisig. A
guardian is an **ordinary participant** (1 vote), not an owner; they execute the
will of the vote, they do not run the project.

**Targeted disbursement / escrow.**
The core aid principle: **"we don't hand out cash — we pay the need directly to
the provider."** For example, with housing aid the money goes straight to the
landlord, not to a personal account — so aid cannot be redirected away from its
purpose. Described in
[`ESCROW-TARGETED-DISBURSEMENT.md`](ESCROW-TARGETED-DISBURSEMENT.md), implemented
in [`Disbursement.sol`](../../contracts/contracts/Disbursement.sol).

**Provider.**
Whoever the targeted payment goes to directly (a landlord, a pharmacy, a service
provider), rather than the aid recipient.

**Staged payments.**
Aid is given not as one lump sum but in parts (tranches) — this lowers the risk
of abuse and allows stopping if something goes wrong. See
[`ANTI-ABUSE.md`](ANTI-ABUSE.md).

**Distribution priority.**
The rule for whom to help first when funds are scarcer than needs: a threat to
life and basic survival first, less urgent things later. Fixed by an explicit
scale in [`PRIORITIES.md`](PRIORITIES.md).

**Appeal.**
The right to challenge a decision (for example, a denial of aid or a sanction).
Every restrictive decision must have a path of appeal that is reviewed by
**people**, not by one person and not by an AI. See
[`ANTI-ABUSE.md`](ANTI-ABUSE.md).

**Collective review.**
An aid request is confirmed not by one person but by several independently — so
that nobody can single-handedly "push through" a payment.

---

## Transparency and verifiability

**Registry (decision registry).**
An open log of all significant project decisions. Each entry has a number
(`PTD-XXXX`). Anyone can see what was decided and when. See
[`governance/registry/`](../../governance/registry/).

**Hash-chain (chain of hashes / immutability of records).**
Each registry entry is "sealed" with a fingerprint (a hash) and references the
fingerprint of the previous one. If someone alters an old entry after the fact,
the fingerprints stop matching and the tampering is immediately visible. This is
how history cannot be rewritten in secret.

**Hash (sha256).**
A short "digital fingerprint" of a file or text. The slightest change in content
completely changes the fingerprint — which is why a hash proves the data was not
swapped.

**IPFS (distributed storage).**
A way to store files such that a file's address is computed **from its content**.
Download a file by its address and you can verify yourself that it is exactly
that file. See [`governance/ipfs/`](../../governance/ipfs/).

**CID (content identifier, a content-based address).**
A file's address in IPFS, computed from its content. Change the file and the CID
changes. So you cannot slip in a forgery under the same CID.

**On-chain / off-chain.**
"On-chain" — recorded in the public blockchain, verifiable by everyone and
immutable. "Off-chain" — outside the blockchain (for example, a Snapshot
discussion). Money moves only on-chain and only after a passed vote.

---

## Safety and technology

**Smart contract.**
A program in the blockchain that enforces rules automatically and equally for
everyone — you cannot "ask it for an exception." In the project the contracts
are the treasury, the targeted disbursements, the voting, and the participant
badge. See [`contracts/`](../../contracts/).

**Testnet and Mainnet.**
Testnet is a "practice" network with fake coins for testing. Mainnet is the real
network with real money. **The project's guardrail:** everything is built and
tested only on testnet; real funds come only after an independent audit and an
explicit human decision.

**Private key / seed phrase.**
A secret that gives full control over a wallet (like the password to a safe).
Such secrets are **never stored in the project's open code** — this is a hard
safety guardrail.

**Audit (of contracts).**
An independent review of the smart-contract code by specialists, looking for
errors and vulnerabilities before any real funds enter the system. Without an
audit, real money is not launched.

**Timelock (delayed execution).**
A mandatory delay between "the decision is adopted" and "the decision is
executed." This is a window to spot an error or abuse and, if needed, stop it.
The [`Timelock.sol`](../../contracts/contracts/Timelock.sol) contract.

**Governor (the voting contract).**
The contract that runs on-chain voting: it accepts proposals, counts votes by the
"1 person = 1 vote" rule, and passes an adopted decision to execution through the
Timelock. It does not move money itself. The
[`Governor.sol`](../../contracts/contracts/Governor.sol) contract.

**Emergency pause.**
The ability to temporarily **stop** operations under a threat (the guardian
role). Importantly, a pause only stops — it **does not allow moving funds** or
directing them anywhere. "Safety ≠ power."

**AI agents (service modules).**
Helper programs that automatically check that the project follows its own rules
(for example: whether there are secrets in the code, whether distribution is
fair, whether the "1 person = 1 vote" principle is preserved). **AI serves but
does not rule:** an agent only raises a signal; people make the decisions
(Article 9 of the constitution). See [`ai-agents/`](../../ai-agents/).

---

## Personhood verification — a real human behind an account

These words appear in the document
[«Making sure there's a real living person behind an account — without surveillance»](IDENTITY-VERIFICATION.md).
Its core idea is simple: the fund needs **one real person = one account** (otherwise
one trickster grabs a hundred votes and receives aid a hundred times under different
names), yet the fund **does not collect faces or dossiers** on people and **does not
surveil** them.

**Protection from manipulation and fake accounts (technically — "Sybil-attack
resistance").**
Measures that prevent one person from creating many fake accounts to inflate votes
or receive aid several times under different names. In this project this is done
**without surveillance** — see
[`IDENTITY-VERIFICATION.md`](IDENTITY-VERIFICATION.md).

**Confirmation that you are a living, unique human (proof-of-personhood).**
A check that there is **one real living person** behind an account — not a bot and
not the same person's tenth account. Importantly, this verifies the **fact** that
"the person is real and singular," not a record of **who exactly** that person is.
Ready-made services for such checks already exist in the world; the fund offers a
choice of several, including ones where a face is not needed at all.

**Liveness check.**
A way to make sure that the camera/service is facing **a living person right now**,
not a photo, a recording, or a mask. The fund receives only a "yes/no" answer; the
photo or video itself **never reaches** the fund's infrastructure.

**Proof without disclosure (zero-knowledge).**
A way to prove a statement — for example "I am a unique person" or "I am over 18" —
**without revealing the data itself** (neither a document, nor a birth date, nor a
face). Only the result ("yes, eligible") goes into the shared log, not personal
details.

**One-time "already registered" marker (nullifier).**
A short technical marker that tells the system "**this person is already here**"
**without revealing who it is**. It is precisely what lets the rule "one person =
one account" hold without linking an account to a real identity.

**Vouching by living people (web-of-trust, the fallback without a camera).**
If a person has no smartphone or internet, or does not want to show their face, they
can be confirmed by the **vouching of several already-verified participants or
guardians**. This is a mandatory fallback — without it the fund would cut off
exactly the most vulnerable (refugees, people without documents). Those who vouch
put their reputation at stake if they confirm an invented person.

---

## If it still doesn't make sense

That's normal — the project is deliberately built in the open, and any term can
be clarified. The most important things to keep in mind are three:

1. **This is help for people, not a way to earn.** Not an investment, not a pyramid.
2. **Nobody owns the fund single-handedly** — the community decides, the code executes.
3. **Everything is open and verifiable** — documents, decisions, code, money flows.

Missing a term? That's a good reason to propose adding it via
[`CONTRIBUTING.en.md`](../../CONTRIBUTING.en.md).
