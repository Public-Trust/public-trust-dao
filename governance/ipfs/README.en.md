[Русский](README.md) · [English]

# IPFS — permanent content-addressed links to key documents

This directory provides **verifiable permanent identifiers (IPFS CIDs)** for the
normative documents of Public Trust DAO. The goal is transparency: every key
document has an identifier computed **from its own content** and verifiable by
anyone **without trusting us** and **without an account**.

## What's here

- `manifest.json` — a deterministic list of key documents with their size,
  `sha256`, and IPFS `CID` (CIDv1). Machine-readable, sorted, reproducible.
- Generator/verifier: [`scripts/ipfs_manifest.py`](../../scripts/ipfs_manifest.py).

The manifest includes all normative docs (`docs/*.md`) and the machine-readable
index of the [decision registry](../registry/) (`governance/registry/index.json`).
The registry index contains `head_hash` — the fingerprint of the entire decision
hash-chain — so a single CID over `index.json` indirectly fixes the whole registry.

## How the CID works (and why it can be trusted)

For a file that fits into a single IPFS block (≤ 256 KiB with the default
chunker), `ipfs add --cid-version=1 --raw-leaves=true` returns a **CIDv1** with
the `raw` codec (0x55), whose multihash is simply **sha2-256** of the file bytes:

```
CIDv1 = multibase_base32( 0x01 0x55 0x12 0x20 <sha256(file_bytes)> )
        (version=1)(codec=raw)(mh=sha2-256)(len=32)
```

Hence two independent ways to verify:

1. **Via IPFS** (if `ipfs`/Kubo is installed):
   ```
   ipfs add --cid-version=1 --raw-leaves=true --quiet docs/CONSTITUTION.md
   ```
   The output must match the `cid` for that file in `manifest.json`.

2. **Without IPFS, by pure recomputation** — `scripts/ipfs_manifest.py` does
   exactly this with the Python standard library (no dependencies):
   ```
   python3 scripts/ipfs_manifest.py verify
   ```
   The command recomputes size/sha256/CID for each file and compares against the
   manifest. Any mismatch (a tampered document or a hand-edited manifest) → a
   non-zero exit code. The same check runs in CI on every push/PR.

Files larger than one block are honestly marked in the manifest as
`single_block: false` / `cid: null` (`cid_kind: needs-unixfs-chunking`) — we
never publish a CID we cannot compute exactly. Right now all key documents are
single-block.

## Pinning (persistence) — needs the operator

Computing and verifying CIDs **does not require** anything beyond the file
content. A pinning account is needed **only** for persistence — so the blocks
actually live on the IPFS network. Once the operator has an account
(web3.storage / Pinata / nft.storage) and a token in `.env` (NOT in the repo),
the pinning commands are:

```
python3 scripts/ipfs_manifest.py pin-commands
```

The CIDs obtained after pinning **must match** the values in `manifest.json` —
otherwise the wrong content was pinned. See the "NEEDS FROM OPERATOR" section in
[`PROGRESS.md`](../../PROGRESS.md).

## Privacy

The manifest contains only **public normative documents** and the registry
index. No personal data of applicants — the registry operates on pseudonymous
`case_id`s (see [`governance/registry/README.md`](../registry/README.md)).
