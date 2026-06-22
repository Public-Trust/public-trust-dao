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

Next in line: apply for help → open record → voting → treasury window → identity
check.

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
  components/     shared UI parts (header, footer, language/theme provider)
  lib/            bilingual texts (i18n) and the blockchain layer (wallet.ts)
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
