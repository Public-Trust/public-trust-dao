#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Public Trust DAO — валидатор конфига Safe multisig (тестовая казна).

Проверяет governance/safe/safe.config.json против схемы И против РЕЛЬС безопасности:
  • только testnet (is_testnet=true, chain_id из allow-list testnet, имя сети без "mainnet");
  • схема 3-из-5 (threshold=3, owners_required=5) и строгое большинство (2*threshold>owners);
  • адреса валидны (0x + 40 hex); владельцы заполнены полностью или вовсе пусты (черновик);
  • в конфиге НЕТ приватных ключей/сид-фраз/секретов (64-hex, mnemonic, private key, secret, seed);
  • согласованность статуса (deployed-testnet ⇒ адрес Safe и 5 владельцев заполнены).

Без сторонних зависимостей (как и остальной инструментарий репо).
Использование:
  python3 scripts/safe_config.py verify [путь_к_конфигу]
Выход: 0 — всё чисто; 1 — есть нарушения.
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAFE_DIR = os.path.join(ROOT, "governance", "safe")
DEFAULT_CONFIG = os.path.join(SAFE_DIR, "safe.config.json")
DEFAULT_SCHEMA = os.path.join(SAFE_DIR, "schema", "safe-config.schema.json")

ADDR_RE = re.compile(r"^0x[0-9a-fA-F]{40}$")
# Подозрение на приватный ключ: 64 hex-символа (с 0x или без), как отдельный токен.
PRIVKEY_RE = re.compile(r"(?<![0-9a-fA-F])(?:0x)?[0-9a-fA-F]{64}(?![0-9a-fA-F])")
SECRET_WORDS = ("private key", "privatekey", "mnemonic", "seed phrase", "secretkey", "private_key")

# Сети mainnet — запрещены рельсами (TESTNET-FIRST). Имена/ID для явного отлова.
MAINNET_CHAIN_IDS = {1, 10, 56, 100, 137, 8453, 42161, 43114, 250, 324, 59144, 534352}
# Известные testnet chain_id (allow-list). Polygon Amoy=80002, Sepolia=11155111, и т.п.
TESTNET_CHAIN_IDS = {80002, 11155111, 17000, 421614, 11155420, 84532, 80001, 5, 97, 43113, 534351}


def load_json(path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


# --- минимальный валидатор JSON-схемы (подмножество draft-07, нужное здесь) ---
def schema_errors(inst, schema, path="$"):
    errs = []
    t = schema.get("type")
    types = t if isinstance(t, list) else ([t] if t else [])

    def ok_type(name):
        return {
            "object": isinstance(inst, dict),
            "array": isinstance(inst, list),
            "string": isinstance(inst, str),
            "integer": isinstance(inst, int) and not isinstance(inst, bool),
            "number": isinstance(inst, (int, float)) and not isinstance(inst, bool),
            "boolean": isinstance(inst, bool),
            "null": inst is None,
        }.get(name, True)

    if types and not any(ok_type(x) for x in types):
        errs.append(f"{path}: тип {type(inst).__name__} не из {types}")
        return errs

    if inst is None:
        return errs
    if "enum" in schema and inst not in schema["enum"]:
        errs.append(f"{path}: значение {inst!r} не из enum {schema['enum']}")
    if isinstance(inst, str):
        if "pattern" in schema and not re.search(schema["pattern"], inst):
            errs.append(f"{path}: не соответствует pattern {schema['pattern']}")
        if "minLength" in schema and len(inst) < schema["minLength"]:
            errs.append(f"{path}: короче minLength {schema['minLength']}")
    if isinstance(inst, int) and not isinstance(inst, bool):
        if "minimum" in schema and inst < schema["minimum"]:
            errs.append(f"{path}: меньше minimum {schema['minimum']}")
    if isinstance(inst, dict):
        for req in schema.get("required", []):
            if req not in inst:
                errs.append(f"{path}: отсутствует обязательное поле '{req}'")
        props = schema.get("properties", {})
        for k, v in inst.items():
            if k in props:
                errs.extend(schema_errors(v, props[k], f"{path}.{k}"))
            elif schema.get("additionalProperties") is False:
                errs.append(f"{path}: лишнее поле '{k}'")
    if isinstance(inst, list):
        item_schema = schema.get("items")
        if item_schema:
            for i, it in enumerate(inst):
                errs.extend(schema_errors(it, item_schema, f"{path}[{i}]"))
    return errs


def rail_errors(cfg, raw_text):
    """Проверки РЕЛЬС безопасности — поверх схемы."""
    errs = []
    net = cfg.get("network", {})
    safe = cfg.get("safe", {})

    # 1. TESTNET-FIRST.
    if net.get("is_testnet") is not True:
        errs.append("РЕЛЬС: network.is_testnet должно быть true (TESTNET-FIRST, mainnet запрещён).")
    cid = net.get("chain_id")
    if cid in MAINNET_CHAIN_IDS:
        errs.append(f"РЕЛЬС: chain_id={cid} — это mainnet. Запрещено (только testnet).")
    elif cid not in TESTNET_CHAIN_IDS:
        errs.append(f"РЕЛЬС: chain_id={cid} нет в allow-list testnet — добавь явно, чтобы исключить mainnet по ошибке.")
    if "mainnet" in str(net.get("name", "")).lower():
        errs.append("РЕЛЬС: имя сети содержит 'mainnet'.")

    # 2. Схема 3-из-5 и строгое большинство.
    thr, req = safe.get("threshold"), safe.get("owners_required")
    if thr != 3 or req != 5:
        errs.append(f"РЕЛЬС: ожидается 3-из-5 (threshold=3, owners_required=5), получено {thr}-из-{req}.")
    if isinstance(thr, int) and isinstance(req, int):
        if thr * 2 <= req:
            errs.append(f"РЕЛЬС: порог {thr} не строгое большинство из {req} (2*порог должно быть > числа владельцев).")
        if thr > req:
            errs.append("РЕЛЬС: порог больше числа владельцев — Safe неисполним.")

    # 3. Адреса владельцев: пусто (черновик) или ровно owners_required валидных.
    owners = safe.get("owners", [])
    if owners and len(owners) != req:
        errs.append(f"РЕЛЬС: владельцев {len(owners)}, а требуется {req} (заполняй все 5 или оставь пустым в черновике).")
    for i, a in enumerate(owners):
        if not ADDR_RE.match(str(a)):
            errs.append(f"РЕЛЬС: owners[{i}] '{a}' не валидный адрес 0x+40hex.")
    if len(set(a.lower() for a in owners)) != len(owners):
        errs.append("РЕЛЬС: адреса владельцев повторяются — нужны 5 разных хранителей.")

    tmpl = cfg.get("owners_template", [])
    if len(tmpl) != req:
        errs.append(f"РЕЛЬС: owners_template должен описывать {req} ролей, а их {len(tmpl)}.")

    # 4. Никаких приватных ключей/секретов в конфиге.
    low = raw_text.lower()
    for w in SECRET_WORDS:
        if w in low:
            errs.append(f"РЕЛЬС: в конфиге встречается '{w}' — секреты/ключи не хранятся в репо.")
    for m in PRIVKEY_RE.findall(raw_text):
        errs.append(f"РЕЛЬС: найдена 64-hex строка ({m[:10]}…) — похоже на приватный ключ. Удалить из репо.")

    # 5. Согласованность статуса.
    status = cfg.get("status")
    if status == "deployed-testnet":
        if not safe.get("address"):
            errs.append("РЕЛЬС: статус deployed-testnet, но не указан адрес Safe.")
        if len(owners) != req:
            errs.append("РЕЛЬС: статус deployed-testnet, но владельцы не заполнены полностью.")
    return errs


def verify(config_path, schema_path):
    cfg = load_json(config_path)
    schema = load_json(schema_path)
    with open(config_path, "r", encoding="utf-8") as fh:
        raw = fh.read()

    errs = schema_errors(cfg, schema)
    errs += rail_errors(cfg, raw)

    if errs:
        print(f"[safe] ✗ нарушений: {len(errs)}", file=sys.stderr)
        for e in errs:
            print("  - " + e, file=sys.stderr)
        return 1

    status = cfg.get("status")
    owners = cfg.get("safe", {}).get("owners", [])
    note = "адреса не заполнены (черновик — ждём оператора)" if not owners else f"{len(owners)} владельцев"
    print(f"[safe] ✓ конфиг валиден: 3-из-5 на {cfg['network']['name']} "
          f"(chain_id={cfg['network']['chain_id']}, testnet), статус={status}, {note}.")
    return 0


def main(argv):
    args = argv[1:]
    cmd = args[0] if args else "verify"
    if cmd != "verify":
        print("использование: safe_config.py verify [путь_к_конфигу]", file=sys.stderr)
        return 2
    config_path = args[1] if len(args) > 1 else DEFAULT_CONFIG
    return verify(config_path, DEFAULT_SCHEMA)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
