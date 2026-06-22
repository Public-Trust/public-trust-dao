[Русский](../EMAIL-SETUP.md) · [English]

# PROJECT EMAIL — PUBLIC TRUST DAO

> ✅ **Active address (updated).** The project's official public contact is
> **fedorgrigorev@proton.me** (option B, ProtonMail). This is a **temporary starter
> address** until mail on the project's own domain is set up (planned —
> `founder@publictrustdao.org`, see §5). Confirmed by the operator for publication;
> placed in `README` (RU/EN), on the website (`web/`), in `AUTHORS`, and as the
> reply address for outreach.

> Instructions and ready-made copy for the project's official email: what the
> options are, what to choose, how to set it up, and how to reply. Derived from
> [`PRINCIPLES.md`](PRINCIPLES.md) and [`PROMOTION.md`](PROMOTION.md).
>
> Registered as a decision in the public registry:
> [`governance/registry/`](../../governance/registry/) (record `PTD-0011`).
>
> **Safety rail.** The builder agent does NOT create external accounts itself
> (email signup requires a phone/captcha and access to secrets). This document is
> a "ready-to-click" draft: the agent prepares the choice, a step-by-step guide
> and reply templates; **the operator personally registers the mailbox and stores
> the password.** Passwords/tokens/keys — NEVER in the repository (see `.gitignore`).

---

## 0. Why the project needs email

- **A point of contact.** So that people, press, prospective guardians and
  partners can write to a clear address — not to some individual's DMs.
- **Trust and transparency.** A public address means the project isn't hiding.
  This directly supports the mission (public good, everything open).
- **Technical needs.** Signing up for Snapshot / an IPFS pinner / the GitHub
  organization, account recovery, notifications — all tie to a project mailbox,
  not the founder's personal one.
- **Separation of roles.** Project email ≠ a person's email. This upholds the
  "no owner" principle: the mailbox belongs to the project and is handed over
  with the role, rather than leaving with the person.

---

## 1. Rails (read BEFORE setup)

1. **No promises of returns in correspondence.** Same prohibitions as in
   [`PRINCIPLES.md`](PRINCIPLES.md): not an investment, not a pyramid, no profit
   guarantees. The reply templates below already comply.
2. **The password stays with the operator (and a backup with guardians by
   decision).** Not in the repo, not in chats, not with the AI agent. A password
   manager is best.
3. **Enable 2FA** (two-factor authentication) right at creation.
4. **Do not publish other people's personal data.** Applications and personal
   messages are private (see the "public/private" table in
   [`ESCROW-TARGETED-DISBURSEMENT.md`](ESCROW-TARGETED-DISBURSEMENT.md)).
5. **Minimize third-party services.** The mail provider is the only external
   dependency; do not connect trackers/analytics/marketing mailings to the box.
6. **Transferability.** Access must be recoverable without one specific person
   (backup codes with several guardians) — the mailbox belongs to the project,
   not to an individual.

---

## 2. Options (comparison)

Priority recommendation: **Option A (own domain + mail) → B (ProtonMail on their
domain) → C (Gmail/other)**. An own domain is best for longevity and trust; you
can start with B and migrate to A without changing the address if the domain is
bought in advance.

| Criterion | A. Own domain + mail | B. ProtonMail (@proton.me) | C. Gmail/regular |
|---|---|---|---|
| Address | `hello@<domain>` | `publictrustdao@proton.me` | `...@gmail.com` |
| Trust/brand | high (own domain) | medium | low for a "fund" |
| Privacy | depends on provider | high (encryption, Switzerland) | low (scanning) |
| Address migration | not needed (domain is yours) | requires changing address | requires changing address |
| Cost | domain ~$10–15/yr + mail | free / ~$4/mo Plus | free |
| Custom domain | yes | yes (paid plan) | yes (Workspace, paid) |
| Complexity | medium | low | low |

**Conclusion for a public good focused on transparency and applicant privacy:**
optimal is **A** (own domain) with mail via a privacy-respecting provider
(ProtonMail/Mailbox.org/Migadu). If you need to start today and free — **B**
(ProtonMail), then attach a domain to Proton once purchased.

> The specific domain and final choice are the operator's. The agent gave
> recommendations; buying the domain and registering the box (phone/payment) is
> done by a human.

---

## 3. Which addresses to create

Start with one or two, expand as needed (can be aliases to a single box):

| Address | Purpose |
|---|---|
| `hello@` (or `info@`) | general inbox: people's questions, press, general |
| `guardians@` | contact with mission guardians (internal coordination) |
| `security@` | vulnerability/abuse reports (responsible disclosure) |
| `press@` | media requests (optional, alias to `hello@`) |

Minimum to start: **`hello@`**. The rest are aliases, to avoid spawning boxes.

---

## 4. Step-by-step guide for the operator

### Option B (quick start, ProtonMail) — recommended first step

1. Open proton.me → Create account → choose `publictrustdao` (or an agreed name).
2. Set a **strong password**, save it in a password manager. Note the backup code.
3. Enable **2FA** (Settings → Account → Security → Two-factor authentication).
4. Put the boilerplate from §6 below into the email signature.
5. Tell the agent (via `comms/INBOX.md`) the address itself (no password!) — the
   agent will place it into the README/site/contact copy.

### Option A (own domain) — for longevity

1. Buy a domain from a registrar (Namecheap/Porkbun/Cloudflare Registrar).
   Domain name suggestions are in §5.
2. Set up mail with a provider supporting custom domains
   (ProtonMail Plus / Mailbox.org / Migadu / Fastmail).
3. Add the provider's DNS records at the registrar: **MX**, **SPF** (TXT),
   **DKIM** (TXT/CNAME), **DMARC** (TXT) — the provider gives ready values.
   This protects against forged mail sent in the project's name.
4. Enable **2FA**, save the password and backup codes (backup — with several
   guardians, see rail §1.6).
5. Create the aliases from §3 on the main box.
6. Tell the agent the address — the agent will place it into the repository.

> ⚠️ DNS records (domain, IP, MX hosts) are public by nature and may be committed
> as infrastructure documentation. **Passwords/secrets/tokens — no.**

---

## 5. Mailbox/domain name ideas

Mailbox (Option B): `publictrustdao@proton.me`, `public.trust.dao@proton.me`,
`publictrust.dao@proton.me`.

Domain (Option A): `publictrust.org`, `public-trust.org`, `publictrustdao.org`,
`publictrust.foundation`. The **`.org`** zone fits a public good.

> Domain availability and the final choice are checked/decided by the operator.

---

## 6. Email signature (boilerplate)

Put into the mailbox signature. Aligned with
[`PRINCIPLES.md`](PRINCIPLES.md) and [`PROMOTION.md`](PROMOTION.md).

```
Public Trust DAO — a community-governed public good.
Transparent by default: code, documents and decisions are open.
This is NOT an investment, NOT a pyramid; we promise no returns.
Repository: https://github.com/Public-Trust/public-trust-dao
```

---

## 7. Reply templates (EN)

Ready replies to typical letters. The operator adapts them to the specific
message. All templates are pre-checked against the constitutional prohibitions.

### 7.1. General reply "what is this project"

```
Hello!

Public Trust DAO is a public good: a transparent mutual-aid fund governed by a
community rather than a single person. We help in a targeted way (for example,
paying a need directly to the provider), and all decisions and operations are
open and verifiable.

Important: this is NOT an investment and NOT a way to earn money. We promise no
returns and pay nothing for recruiting people. The project is currently at an
early stage (testnet, no real funds in circulation).

Learn more and verify everything yourself:
https://github.com/Public-Trust/public-trust-dao

Best regards,
the Public Trust DAO team
```

### 7.2. Reply to press / interview request

```
Hello, thank you for your interest!

In short: Public Trust DAO is an open, community-governed mutual-aid fund (a
public good, not an investment). All documentation, the constitution and the
decision registry are public in the repository:
https://github.com/Public-Trust/public-trust-dao

We're glad to answer questions in writing. Please send a list of questions and
deadlines — we'll prepare careful answers (we avoid any wording about "returns"
or "investment", since this is a public project).

Best regards,
the Public Trust DAO team
```

### 7.3. Reply "how to help / how to participate"

```
Hello!

Thank you for wanting to help. Right now the best contribution is non-financial:
review the code and documents, suggest improvements, tell people about the
project honestly (as a public good, not as an investment).

We do NOT raise funds from private individuals and promise no returns. When
verifiable ways to participate appear (after an audit and the launch of community
governance), we will describe them openly in the repository.

Repository and plan: https://github.com/Public-Trust/public-trust-dao

Best regards,
the Public Trust DAO team
```

### 7.4. Reply to a vulnerability/abuse report (`security@`)

```
Hello, thank you for the responsible report!

We take the project's security and integrity seriously. Please describe the issue
in detail (what, where, how to reproduce). Do not publish details publicly before
we have a chance to respond.

We will review the report and reply. We record all significant fixes and
decisions in the project's public registry.

Best regards,
the Public Trust DAO team
```

---

## 8. What the agent does once it has the address

As soon as the operator reports the address (via `comms/INBOX.md`, WITHOUT a
password), the agent:

1. Places the contact into `README.md` / `README.en.md` and on the site (`web/`).
2. Adds the `security@` address to the responsible-disclosure section (if any).
3. Registers the fact "contact activated" as a separate registry record.
4. Keeps the reply copy in sync with the principles.

**Status (done):** the operator confirmed the address **fedorgrigorev@proton.me** —
the contact is placed in `README` (RU/EN), on the website, in `AUTHORS`, and in
outreach; registered as a registry entry. This is a temporary starter address; once
a domain is purchased it will be replaced by a domain address (see §5) without losing
history.

---

## 9. Open questions for the operator

- Choose the option: **A (own domain)** or **B (ProtonMail)** for the start.
- If A — agree on the domain (suggestions in §5) and who pays/holds it.
- Confirm who stores the access backup codes (≥2 guardians recommended).
- Report the final address to the agent — without a password — for placement.
