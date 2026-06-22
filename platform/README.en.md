[Русский](README.md) · [English]

# Public Trust DAO platform (Next.js)

**In plain words.** This is the fund's working application — the place where a
person can ask for help, see the open record of decisions, vote as an equal, and
check the state of the shared treasury. We build it step by step: each finished
screen appears on the site right away.

This is a **public good, not an investment.** No promised returns, no pyramid,
and no payment for bringing in people. Everything is on a **test network** for
now, with no real money.

## Why Next.js and "static export"

The platform is written in **Next.js (React)** — a full foundation for building a
large application. For now we build it as a **set of plain files** (static
export, `next export`) so it can be hosted for free on GitHub Pages without a
paid server. The architecture is still complete: when a server is needed, the
same code can run as a server by turning off static export.

## Finished screens

- **Home** — mission, the "public good, not an investment" disclaimer, and a
  showcase of upcoming screens.
- **Connect a wallet** (`/wallet/`) — a person connects a wallet (such as
  MetaMask) with a clear explanation of what it is and why, sees their public
  address and network, and can disconnect. No money moves when connecting; if a
  main network with real money is selected, the screen honestly warns that the
  fund works only on a test network.
- **Apply for help** (`/apply/`) — a calm, anonymous form ordered by need
  severity, with a required direct-spend field (the fund pays the need directly).
  Until the contracts run on a test network, it builds a verifiable application
  draft right in the browser (copy/save) — nothing is sent outside.
- **Open record** (`/journal/`) — a list of all the fund's decisions, newest
  first, with a filter by record type and a search. Tamper protection is
  explained in plain words (records linked by fingerprints), the overall journal
  fingerprint is shown, and each record links to its full file in the repository.
  The data travels with the platform as a snapshot of the open registry
  (`lib/journal-data.json`) — nothing is loaded from outside.
- **Voting** (`/voting/`) — the core rule in plain words: one person, one vote; a
  vote cannot be bought or sold. A list of proposals; on an open one you can vote
  "For" / "Against" / "Abstain", and a vote always weighs one. Until the contracts
  run on a test network, the vote is built as a verifiable draft right in the
  browser (copy/save/change) and kept only with the person; the proposals shown are
  demonstrations, and nothing leaves the browser.
- **Treasury window** (`/treasury/`) — the state of the shared treasury in plain
  words and view-only: how much in total, how much is in the untouchable reserve,
  how much goes to direct help for people (always at least 70% of the distributable
  remainder) and to a modest thank-you for work (under a cap); a clear composition
  bar, a "how well the fund is provided for" level, and the latest movements
  (incoming and targeted payments). Nothing can be spent from here; until the
  contracts run on a test network the state is a demonstration, amounts are in test
  units, and nothing is loaded from outside.
- **Identity check** (`/identity/`) — in plain words, how the fund makes sure there
  is one real, living person behind a participant, without surveillance and without
  collecting faces into a database. Two layers: how much checking is needed (depends
  on the action — browsing needs no check, applying needs a light "a living person"
  check, voting and receiving help need a strict uniqueness check) and which method
  to use (a circle of acquaintances with no biometrics / a passport of many signals /
  a "liveness" check by an external service / a mandatory fallback — vouching by
  living people). A hard boundary: "uniqueness is not power over money." Until
  verification runs, the choice stays as a checkable note in the browser with no
  personal data — nothing leaves it.

This completes the series of value screens planned by the operator (INBOX #34).

## Transparency rails (followed literally)

- **No third-party trackers, ads, or analytics.** Zero requests to other
  people's servers.
- **System fonts** — nothing loaded from outside.
- **Dependencies pinned** to exact versions (supply-chain safety), minimal
  number of packages.
- **Next.js telemetry off** (`NEXT_TELEMETRY_DISABLED=1`).
- **Bilingual RU↔EN** right in the interface (toggle in the header).
- **Accessibility:** skip-to-content link, visible focus rings, light and dark
  themes, respect for `prefers-reduced-motion`.

## Run locally (for developers)

```bash
cd platform
npm install
npm run dev      # dev mode at http://localhost:3000
npm run build    # static export into out/
```

`npm run typecheck` — type checking without a build.

To publish under a GitHub Pages subpath, set the base path:

```bash
NEXT_PUBLIC_BASE_PATH=/public-trust-dao npm run build
```

## Build and check

The host currently lacks disk space for `node_modules`, so the build is verified
by the GitHub Actions workflow
[`.github/workflows/platform.yml`](../.github/workflows/platform.yml): it installs
dependencies, checks types, and builds the static site on GitHub's servers.
Pages publishing will be wired up separately, once we start moving people from
the showcase site [`web/`](../web/) to the platform.

## Structure

```
platform/
  app/            screens and the shared shell (layout, globals.css)
    wallet/       the "Connect a wallet" screen
    apply/        the "Apply for help" screen
    journal/      the "Open record" screen
    voting/       the "Voting" screen
    treasury/     the "Treasury window" screen
    identity/     the "Identity check" screen
  components/     shared UI parts (header, footer, language/theme provider)
  lib/            bilingual texts (i18n) and data layers (wallet.ts, application.ts,
                  journal.ts, voting.ts, treasury.ts, identity.ts) + a snapshot of the registry (journal-data.json)
  next.config.mjs build settings (static export)
  package.json    dependencies (exact versions)
```

**Layer separation** (groundwork for a future server): screens (`app/`) and
shared UI (`components/`) are kept apart from data and blockchain (`lib/`). For
example, `lib/wallet.ts` is plain wallet access via the EIP-1193 standard with no
third-party libraries; the screen only uses it. This lets us later plug in real
contracts or a server side without rewriting the interface.

See also: [`docs/PRODUCT-INTERFACES.md`](../docs/en/PRODUCT-INTERFACES.md) — the
order of interfaces (web → Telegram → mobile).
