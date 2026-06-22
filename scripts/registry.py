#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Public Trust DAO — инструмент публичного реестра решений (Этап 3, прозрачность).

Реестр — это публичный, проверяемый, защищённый от подмены append-only журнал
решений и операций DAO. Реализует конституционный принцип «неизменяемость
записей» (LAUNCH.md / docs/CONSTITUTION.md) ещё до IPFS-пиннинга: каждая запись
ссылается на sha256-хеш предыдущей (hash-chain), поэтому изменение любой старой
записи ломает всю цепочку и сразу заметно при проверке.

Зависимостей нет (только стандартная библиотека) — поэтому verify всегда
запускается «в зелёное» в любом окружении и в CI.

Канонический вид записи для хеширования (документирован в README реестра):
    json.dumps(record_без_поля_hash, sort_keys=True,
               separators=(",", ":"), ensure_ascii=False)
и затем sha256 от UTF-8 байт. Воспроизводимо кем угодно.

Подкоманды:
    verify            — проверить схему, цепочку хешей и индекс (exit!=0 при сбое)
    append            — добавить новую запись (считает seq, prev_hash, hash)
    reindex           — пересобрать index.json из записей
"""
import argparse
import hashlib
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REG = os.path.join(ROOT, "governance", "registry")
RECORDS_DIR = os.path.join(REG, "records")
SCHEMA_DIR = os.path.join(REG, "schema")
INDEX_PATH = os.path.join(REG, "index.json")

ZERO_HASH = "0" * 64
RECORD_TYPES = [
    "genesis", "decision", "disbursement", "governance",
    "audit", "appeal", "reputation", "note",
]


# ---------- канонизация и хеш ----------

def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False)


def record_hash(record):
    body = {k: v for k, v in record.items() if k != "hash"}
    return hashlib.sha256(canonical(body).encode("utf-8")).hexdigest()


# ---------- мини-валидатор JSON Schema (подмножество draft-07) ----------

def schema_errors(instance, schema, path="$"):
    errs = []
    t = schema.get("type")
    if t:
        ok = {
            "object": dict, "array": list, "string": str,
            "integer": int, "number": (int, float), "boolean": bool,
        }[t]
        if t == "integer" and isinstance(instance, bool):
            errs.append(f"{path}: ожидался integer, получен boolean")
            return errs
        if not isinstance(instance, ok):
            errs.append(f"{path}: ожидался {t}, получен {type(instance).__name__}")
            return errs
    if "enum" in schema and instance not in schema["enum"]:
        errs.append(f"{path}: значение {instance!r} не из enum {schema['enum']}")
    if "const" in schema and instance != schema["const"]:
        errs.append(f"{path}: значение {instance!r} != const {schema['const']!r}")
    if isinstance(instance, str):
        if "pattern" in schema and not re.search(schema["pattern"], instance):
            errs.append(f"{path}: не соответствует pattern {schema['pattern']}")
        if "minLength" in schema and len(instance) < schema["minLength"]:
            errs.append(f"{path}: короче minLength {schema['minLength']}")
    if isinstance(instance, (int, float)) and not isinstance(instance, bool):
        if "minimum" in schema and instance < schema["minimum"]:
            errs.append(f"{path}: меньше minimum {schema['minimum']}")
        if "maximum" in schema and instance > schema["maximum"]:
            errs.append(f"{path}: больше maximum {schema['maximum']}")
    if isinstance(instance, dict):
        for req in schema.get("required", []):
            if req not in instance:
                errs.append(f"{path}: отсутствует обязательное поле '{req}'")
        props = schema.get("properties", {})
        for key, val in instance.items():
            if key in props:
                errs.extend(schema_errors(val, props[key], f"{path}.{key}"))
            elif schema.get("additionalProperties") is False:
                errs.append(f"{path}: недопустимое поле '{key}'")
    if isinstance(instance, list):
        item_schema = schema.get("items")
        if item_schema:
            for i, item in enumerate(instance):
                errs.extend(schema_errors(item, item_schema, f"{path}[{i}]"))
        if "minItems" in schema and len(instance) < schema["minItems"]:
            errs.append(f"{path}: меньше minItems {schema['minItems']}")
    return errs


# ---------- загрузка ----------

def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def record_files():
    if not os.path.isdir(RECORDS_DIR):
        return []
    files = [f for f in os.listdir(RECORDS_DIR) if f.endswith(".json")]
    return sorted(files)


def load_records():
    recs = []
    for fn in record_files():
        recs.append((fn, load_json(os.path.join(RECORDS_DIR, fn))))
    recs.sort(key=lambda x: x[1].get("seq", -1))
    return recs


# ---------- verify ----------

def cmd_verify(_args):
    schema = load_json(os.path.join(SCHEMA_DIR, "record.schema.json"))
    recs = load_records()
    errors = []

    if not recs:
        print("[registry] записей нет — нечего проверять (это нормально для пустого реестра)")
        return 0

    prev_hash = ZERO_HASH
    for i, (fn, rec) in enumerate(recs):
        # схема
        for e in schema_errors(rec, schema):
            errors.append(f"{fn}: схема: {e}")
        # тип
        if rec.get("type") not in RECORD_TYPES:
            errors.append(f"{fn}: неизвестный type={rec.get('type')!r}")
        # монотонный непрерывный seq с нуля
        if rec.get("seq") != i:
            errors.append(f"{fn}: seq={rec.get('seq')} ожидался {i}")
        # хеш-цепочка
        if rec.get("prev_hash") != prev_hash:
            errors.append(f"{fn}: prev_hash не совпал (ожидался {prev_hash[:12]}…)")
        expected = record_hash(rec)
        if rec.get("hash") != expected:
            errors.append(f"{fn}: hash подделан/устарел (пересчитан {expected[:12]}…)")
        # genesis
        if i == 0 and rec.get("type") != "genesis":
            errors.append(f"{fn}: первая запись должна быть type=genesis")
        prev_hash = rec.get("hash")

    # индекс
    if os.path.exists(INDEX_PATH):
        idx = load_json(INDEX_PATH)
        if idx.get("count") != len(recs):
            errors.append(f"index.json: count={idx.get('count')} != {len(recs)}")
        if idx.get("head_hash") != recs[-1][1].get("hash"):
            errors.append("index.json: head_hash не совпадает с последней записью")
    else:
        errors.append("index.json отсутствует")

    if errors:
        print(f"[registry] ✗ НАЙДЕНО {len(errors)} проблем(ы):")
        for e in errors:
            print("  -", e)
        return 1
    print(f"[registry] ✓ цепочка цела: {len(recs)} запис(ей), "
          f"head={recs[-1][1]['hash'][:12]}…")
    return 0


# ---------- append ----------

def cmd_append(args):
    payload = load_json(args.payload) if args.payload else {}
    recs = load_records()
    seq = len(recs)
    prev_hash = recs[-1][1]["hash"] if recs else ZERO_HASH
    rec = {
        "seq": seq,
        "id": args.id or f"PTD-{seq:04d}",
        "type": args.type,
        "timestamp": args.timestamp,
        "actor": args.actor,
        "summary": args.summary,
        "refs": args.ref or [],
        "payload": payload,
        "prev_hash": prev_hash,
    }
    rec["hash"] = record_hash(rec)

    schema = load_json(os.path.join(SCHEMA_DIR, "record.schema.json"))
    errs = schema_errors(rec, schema)
    if errs:
        print("[registry] ✗ запись не прошла схему, не пишу:")
        for e in errs:
            print("  -", e)
        return 1

    os.makedirs(RECORDS_DIR, exist_ok=True)
    slug = re.sub(r"[^a-z0-9]+", "-", (args.slug or args.type).lower()).strip("-")
    fn = f"{seq:04d}-{slug}.json"
    path = os.path.join(RECORDS_DIR, fn)
    with open(path, "w", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False, indent=2) + "\n")
    print(f"[registry] + {fn}  hash={rec['hash'][:12]}…")
    reindex()
    return 0


# ---------- reindex ----------

def reindex():
    recs = load_records()
    idx = {
        "registry": "Public Trust DAO — публичный реестр решений",
        "spec": "hash-chain append-only; см. governance/registry/README.md",
        "count": len(recs),
        "head_hash": recs[-1][1]["hash"] if recs else ZERO_HASH,
        "entries": [
            {
                "seq": r["seq"], "id": r["id"], "type": r["type"],
                "timestamp": r["timestamp"], "summary": r["summary"],
                "hash": r["hash"], "file": f"records/{fn}",
            }
            for fn, r in recs
        ],
    }
    with open(INDEX_PATH, "w", encoding="utf-8") as f:
        f.write(json.dumps(idx, ensure_ascii=False, indent=2) + "\n")
    print(f"[registry] index.json обновлён: {len(recs)} запис(ей)")


def cmd_reindex(_args):
    reindex()
    return 0


def main():
    p = argparse.ArgumentParser(description="Public Trust DAO registry tool")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("verify", help="проверить схему, цепочку хешей и индекс")
    sub.add_parser("reindex", help="пересобрать index.json")

    a = sub.add_parser("append", help="добавить запись")
    a.add_argument("--type", required=True, choices=RECORD_TYPES)
    a.add_argument("--summary", required=True)
    a.add_argument("--actor", required=True)
    a.add_argument("--timestamp", required=True, help="ISO-8601 UTC, напр. 2026-06-22T00:00:00Z")
    a.add_argument("--id", default=None)
    a.add_argument("--slug", default=None)
    a.add_argument("--ref", action="append", help="ссылка (можно несколько раз)")
    a.add_argument("--payload", default=None, help="путь к JSON-файлу полезной нагрузки")

    args = p.parse_args()
    fn = {"verify": cmd_verify, "append": cmd_append, "reindex": cmd_reindex}[args.cmd]
    sys.exit(fn(args))


if __name__ == "__main__":
    main()
