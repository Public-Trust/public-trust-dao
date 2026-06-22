[Русский](README.md) · [English]

# Public decision registry — Public Trust DAO

This is a **public, verifiable, tamper-evident** journal of the DAO's decisions
and operations. It implements the constitutional principles of **transparency**
and **immutability of records**
([`docs/CONSTITUTION.md`](../../docs/en/CONSTITUTION.md),
[`docs/PRINCIPLES.md`](../../docs/en/PRINCIPLES.md)) — even before IPFS pinning
(the next step of Stage 3).

> This is part of the public-good infrastructure. The registry is **not** a
> financial instrument and does **not** promise returns. The disbursement
> records in the examples are test (testnet) ones, with no real funds.

## How it works: a hash-chain

Each record is a separate JSON file in [`records/`](records/). Records are
**append-only** and **cryptographically chained**:

- every record has a `prev_hash` — the sha256 of the previous record;
- the genesis record (`seq=0`) has `prev_hash` = 64 zeros;
- a record's `hash` = sha256 of its **canonical form without the `hash` field**.

Changing any old record changes its `hash`, breaks the `prev_hash` of the next
one — and `verify` detects this immediately. History cannot be rewritten
unnoticed.

### Canonical form (reproducible by anyone)

```
canonical = json.dumps(record_without_hash_field,
                        sort_keys=True,
                        separators=(",", ":"),
                        ensure_ascii=False)
hash = sha256(canonical.encode("utf-8")).hexdigest()
```

Anyone can independently recompute the hashes and verify the integrity of the
whole chain.

## Record structure

The envelope is described by the schema
[`schema/record.schema.json`](schema/record.schema.json):

| field | meaning |
|-------|---------|
| `seq` | monotonic number starting at 0 |
| `id` | stable identifier, e.g. `PTD-0001` |
| `type` | `genesis`/`decision`/`disbursement`/`governance`/`audit`/`appeal`/`reputation`/`note` |
| `timestamp` | moment in UTC, ISO-8601 (`…Z`) |
| `actor` | who initiated it (role/agent/keeper), **without applicants' personal data** |
| `summary` | short human-readable description |
| `refs` | references: constitution articles, Snapshot proposals, tx hashes, IPFS CIDs |
| `payload` | type-specific data (per-type schemas in [`schema/`](schema/)) |
| `prev_hash` | sha256 of the previous record |
| `hash` | sha256 of this record's canonical form |

The payload for `disbursement` (fund distribution) is described by
[`schema/disbursement.schema.json`](schema/disbursement.schema.json) and reflects
the requirements of [`docs/PRIORITIES.md`](../../docs/en/PRIORITIES.md) and
[`docs/ANTI-ABUSE.md`](../../docs/en/ANTI-ABUSE.md): need priority, staged
payments, limits, collective review, an appeal window.

## Privacy

Applicants' personal data does **not** enter the registry. Only pseudonymous
`case_id`s and verifiable references. Transparency of operations ≠ exposure of
the people being helped.

## Tool: `scripts/registry.py`

No third-party dependencies (Python standard library only) — so the check runs
identically locally and in CI.

```bash
# verify the schema, hash-chain, and index (exit!=0 on any problem)
python3 scripts/registry.py verify

# append a record (seq, prev_hash, hash are computed automatically)
python3 scripts/registry.py append \
  --type decision \
  --id PTD-0003 --slug short-slug \
  --summary "Short description" \
  --actor "role/agent" \
  --timestamp "2026-06-22T12:00:00Z" \
  --ref "docs/CONSTITUTION.md" \
  --payload /path/to/payload.json

# rebuild index.json from the records
python3 scripts/registry.py reindex
```

The machine-readable index is [`index.json`](index.json): `count`, `head_hash`,
and the list of records. `head_hash` is the "fingerprint" of the whole registry
at a given moment; it is convenient to pin in IPFS and publish.

## Guarantee in CI

The workflow
[`.github/workflows/registry.yml`](../../.github/workflows/registry.yml) runs
`verify` on every push/PR. Any history tampering or index desync fails the
build — registry integrity is checked automatically and publicly.

## Current records

`0000` genesis · `0001` example decision · `0002` example staged test
disbursement. Records marked `[ПРИМЕР]` (EXAMPLE) demonstrate the format and are
not real operations.
