#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Public Trust DAO — детерминированный IPFS-манифест ключевых документов
(Этап 3, прозрачность — часть 2/2).

Идея прозрачности: у каждого нормативного документа DAO должен быть постоянный,
content-addressed идентификатор (IPFS CID), который вычисляется ИЗ САМОГО
СОДЕРЖИМОГО и проверяется кем угодно БЕЗ доверия к нам и БЕЗ аккаунта пиннера.

Ключевой факт: для файла, который помещается в один блок (<= 256 KiB при
дефолтном чанкере IPFS), `ipfs add --cid-version=1 --raw-leaves=true` даёт
CIDv1 с кодеком `raw` (0x55), мультихеш которого — это просто sha2-256 от байт
файла. Значит CID можно посчитать локально, без демона IPFS и без аккаунта.
Аккаунт пиннера (web3.storage / Pinata / nft.storage) нужен ТОЛЬКО для
persistence (чтобы блок жил в сети) — но не для вычисления и проверки CID.

Этот инструмент:
  * собирает детерминированный список ключевых документов;
  * считает для каждого размер, sha256 и IPFS CIDv1 (raw, single-block);
  * пишет `governance/ipfs/manifest.json` (отсортировано, воспроизводимо);
  * умеет `verify` для CI: пересчитывает и сверяет с манифестом на диске.

Зависимостей нет (только стандартная библиотека) — verify всегда «в зелёное»
в любом окружении и в CI. Воспроизводимо кем угодно.

Подкоманды:
    build           — пересобрать manifest.json из текущего содержимого файлов
    verify          — пересчитать и сверить с manifest.json (exit!=0 при сбое)
    pin-commands    — напечатать точные команды пиннинга для оператора
"""
import argparse
import base64
import hashlib
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IPFS_DIR = os.path.join(ROOT, "governance", "ipfs")
MANIFEST_PATH = os.path.join(IPFS_DIR, "manifest.json")

# Дефолтный размер чанка IPFS. Файлы крупнее требуют UnixFS/dag-pb разбиения,
# и тогда одноблочный raw-leaf CID НЕ применим — мы это явно отмечаем, чтобы
# никогда не опубликовать неверный CID.
IPFS_CHUNK = 262144  # 256 KiB

# Детерминированный набор ключевых документов (относительные пути от корня репо).
# docs/*.md подхватываются автоматически (сортировка по имени) — новые
# нормативные доки попадают в манифест без правки кода; плюс машиночитаемый
# индекс реестра решений.
def key_files():
    docs_dir = os.path.join(ROOT, "docs")
    docs = sorted(
        os.path.join("docs", n)
        for n in os.listdir(docs_dir)
        if n.endswith(".md")
    )
    extra = ["governance/registry/index.json"]
    return docs + extra


def cidv1_raw(data: bytes) -> str:
    """CIDv1, кодек raw (0x55), мультихеш sha2-256, multibase base32 (lower).

    Эквивалентно `ipfs add --cid-version=1 --raw-leaves=true` для файла,
    помещающегося в один блок. Проверяемо независимо.
    """
    digest = hashlib.sha256(data).digest()
    multihash = bytes([0x12, 0x20]) + digest          # sha2-256, длина 32
    cid_bytes = bytes([0x01, 0x55]) + multihash        # version 1, codec raw
    b32 = base64.b32encode(cid_bytes).decode("ascii").lower().rstrip("=")
    return "b" + b32


def entry_for(rel_path: str) -> dict:
    abs_path = os.path.join(ROOT, rel_path)
    with open(abs_path, "rb") as f:
        data = f.read()
    single_block = len(data) <= IPFS_CHUNK
    return {
        "path": rel_path,
        "bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        # CID валиден как одноблочный raw-leaf только если файл влезает в чанк.
        "cid": cidv1_raw(data) if single_block else None,
        "cid_kind": "raw-leaf-v1" if single_block else "needs-unixfs-chunking",
        "single_block": single_block,
    }


def build_manifest() -> dict:
    files = []
    for rel in key_files():
        abs_path = os.path.join(ROOT, rel)
        if not os.path.exists(abs_path):
            raise SystemExit("ОШИБКА: ключевой файл отсутствует: %s" % rel)
        files.append(entry_for(rel))
    files.sort(key=lambda e: e["path"])

    # Отпечаток всего набора: sha256 от канонического JSON списка (path+cid+sha256).
    fingerprint_src = json.dumps(
        [{"path": e["path"], "sha256": e["sha256"], "cid": e["cid"]} for e in files],
        sort_keys=True, separators=(",", ":"), ensure_ascii=False,
    ).encode("utf-8")

    return {
        "project": "Public Trust DAO",
        "kind": "ipfs-content-manifest",
        "version": 1,
        "spec": (
            "CIDv1, codec=raw(0x55), multihash=sha2-256, multibase=base32. "
            "Эквивалент `ipfs add --cid-version=1 --raw-leaves=true` для "
            "одноблочных файлов (<=256 KiB). Вычисляется и проверяется из "
            "содержимого, без аккаунта пиннера."
        ),
        "verify": "python3 scripts/ipfs_manifest.py verify",
        "files": files,
        "manifest_fingerprint_sha256": hashlib.sha256(fingerprint_src).hexdigest(),
    }


def write_manifest(manifest: dict) -> None:
    os.makedirs(IPFS_DIR, exist_ok=True)
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")


def cmd_build(_args) -> int:
    manifest = build_manifest()
    write_manifest(manifest)
    print("manifest собран: %d файлов" % len(manifest["files"]))
    for e in manifest["files"]:
        flag = "" if e["single_block"] else "  [!! не одноблочный — CID не вычислен]"
        print("  %-40s %s%s" % (e["path"], e["cid"] or "-", flag))
    print("manifest_fingerprint_sha256: %s" % manifest["manifest_fingerprint_sha256"])
    return 0


def cmd_verify(_args) -> int:
    if not os.path.exists(MANIFEST_PATH):
        print("ОШИБКА: %s не найден — запусти `build`" % MANIFEST_PATH, file=sys.stderr)
        return 1
    with open(MANIFEST_PATH, encoding="utf-8") as f:
        on_disk = json.load(f)
    expected = build_manifest()

    ok = True
    by_path = {e["path"]: e for e in on_disk.get("files", [])}
    for e in expected["files"]:
        rec = by_path.get(e["path"])
        if rec is None:
            print("РАССИНХРОН: файла нет в манифесте: %s" % e["path"], file=sys.stderr)
            ok = False
            continue
        for field in ("bytes", "sha256", "cid", "single_block"):
            if rec.get(field) != e[field]:
                print("РАССИНХРОН: %s.%s: манифест=%r, факт=%r"
                      % (e["path"], field, rec.get(field), e[field]), file=sys.stderr)
                ok = False
    expected_paths = {e["path"] for e in expected["files"]}
    for p in by_path:
        if p not in expected_paths:
            print("РАССИНХРОН: лишний файл в манифесте: %s" % p, file=sys.stderr)
            ok = False
    if on_disk.get("manifest_fingerprint_sha256") != expected["manifest_fingerprint_sha256"]:
        print("РАССИНХРОН: manifest_fingerprint_sha256 не совпал", file=sys.stderr)
        ok = False

    if ok:
        print("OK: manifest совпадает с содержимым файлов (%d записей)"
              % len(expected["files"]))
        return 0
    print("СБОЙ: manifest рассинхронизирован — запусти `build` и закоммить",
          file=sys.stderr)
    return 1


def cmd_pin_commands(_args) -> int:
    manifest = build_manifest()
    print("# Команды пиннинга для оператора (нужен аккаунт пиннера + токен в .env).")
    print("# CID ниже уже вычислены локально и проверяемы — пиннинг лишь даёт")
    print("# persistence. После пиннинга CID обязан совпасть с этими значениями.\n")
    print("# Вариант A — IPFS Kubo (локальный демон), сверка CID:")
    for e in manifest["files"]:
        if e["single_block"]:
            print("ipfs add --cid-version=1 --raw-leaves=true --quiet %s"
                  "   # ожидаем: %s" % (e["path"], e["cid"]))
    print("\n# Вариант B — пиннинг-сервис (web3.storage / Pinata / nft.storage):")
    print("#   загрузить те же файлы, токен брать из .env (НЕ коммитить).")
    print("#   Полученные CID обязаны совпасть со значениями в manifest.json.")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="IPFS content-manifest ключевых документов")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("build", help="пересобрать manifest.json")
    sub.add_parser("verify", help="сверить manifest.json с содержимым (CI)")
    sub.add_parser("pin-commands", help="напечатать команды пиннинга для оператора")
    args = parser.parse_args(argv)

    return {
        "build": cmd_build,
        "verify": cmd_verify,
        "pin-commands": cmd_pin_commands,
    }[args.cmd](args)


if __name__ == "__main__":
    raise SystemExit(main())
