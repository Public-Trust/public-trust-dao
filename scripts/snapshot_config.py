#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Public Trust DAO — валидатор конфига off-chain пространства голосования (Snapshot).

Проверяет governance/snapshot/space.json против схемы И против РЕЛЬС:
  • off_chain_signaling=true (голос — сигнал, средства Snapshot не двигает);
  • только testnet (network.is_testnet=true, chain_id из allow-list testnet, без "mainnet");
  • «1 человек = 1 голос»: стратегии — только равновесные (ticket, value=1);
    запрещены плутократические стратегии (взвешивание по балансу токена/монеты);
  • анти-Сивилла: голосование закрыто для не-верифицированных (onlyMembers / validation),
    чтобы 1-человек-1-голос имел смысл;
  • тип голосования — из разрешённого набора (не денежно-взвешенный);
  • в конфиге НЕТ приватных ключей/сид-фраз/секретов (64-hex, mnemonic, private key, seed);
  • согласованность статуса (deployed-testnet ⇒ ENS/id/controller заполнены и кворум>0).

Без сторонних зависимостей (как и остальной инструментарий репо).
Использование:
  python3 scripts/snapshot_config.py verify [путь_к_конфигу]
Выход: 0 — всё чисто; 1 — есть нарушения.
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SNAP_DIR = os.path.join(ROOT, "governance", "snapshot")
DEFAULT_CONFIG = os.path.join(SNAP_DIR, "space.json")
DEFAULT_SCHEMA = os.path.join(SNAP_DIR, "schema", "snapshot-space.schema.json")

ADDR_RE = re.compile(r"^0x[0-9a-fA-F]{40}$")
# Подозрение на приватный ключ: 64 hex-символа (с 0x или без), как отдельный токен.
PRIVKEY_RE = re.compile(r"(?<![0-9a-fA-F])(?:0x)?[0-9a-fA-F]{64}(?![0-9a-fA-F])")
SECRET_WORDS = ("private key", "privatekey", "mnemonic", "seed phrase", "secretkey", "private_key")

# Сети mainnet — запрещены рельсами (TESTNET-FIRST).
MAINNET_CHAIN_IDS = {"1", "10", "56", "100", "137", "8453", "42161", "43114", "250", "324", "59144", "534352"}
# Известные testnet chain_id (allow-list). Polygon Amoy=80002, Sepolia=11155111, и т.п.
TESTNET_CHAIN_IDS = {"80002", "11155111", "17000", "421614", "11155420", "84532", "80001", "5", "97", "43113", "534351"}

# Равновесные стратегии: каждый допущенный адрес = 1 голос. Только они допустимы.
EQUAL_WEIGHT_STRATEGIES = {"ticket"}
# Плутократические маркеры в имени стратегии — вес по балансу/деньгам. Запрещены.
PLUTOCRATIC_MARKERS = ("balance", "erc20", "erc721", "erc1155", "delegation", "token", "coin", "quadratic", "staked", "lp-")
# Разрешённые типы голосования (равный вес сохраняется при любом из них).
ALLOWED_VOTING_TYPES = {"single-choice", "approval", "ranked-choice", "basic", "weighted", "custom"}


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
    if isinstance(inst, list):
        if "minItems" in schema and len(inst) < schema["minItems"]:
            errs.append(f"{path}: меньше minItems {schema['minItems']}")
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
    settings = cfg.get("settings", {})
    space = cfg.get("space", {})

    # 1. Голос — сигнал, средства Snapshot не двигает.
    if cfg.get("off_chain_signaling") is not True:
        errs.append("РЕЛЬС: off_chain_signaling должно быть true (голосование off-chain не двигает средства).")

    # 2. TESTNET-FIRST.
    if net.get("is_testnet") is not True:
        errs.append("РЕЛЬС: network.is_testnet должно быть true (TESTNET-FIRST, mainnet запрещён).")
    cid = str(net.get("chain_id"))
    if cid in MAINNET_CHAIN_IDS:
        errs.append(f"РЕЛЬС: chain_id={cid} — это mainnet. Запрещено (только testnet).")
    elif cid not in TESTNET_CHAIN_IDS:
        errs.append(f"РЕЛЬС: chain_id={cid} нет в allow-list testnet — добавь явно, чтобы исключить mainnet по ошибке.")
    if "mainnet" in str(net.get("name", "")).lower():
        errs.append("РЕЛЬС: имя сети содержит 'mainnet'.")
    # сеть в settings (для snapshot) не должна указывать на mainnet
    if str(settings.get("network")) in MAINNET_CHAIN_IDS:
        errs.append(f"РЕЛЬС: settings.network={settings.get('network')} — mainnet. Запрещено.")

    # 3. «1 человек = 1 голос» — только равновесные стратегии, без плутократии.
    strategies = settings.get("strategies", [])
    if not strategies:
        errs.append("РЕЛЬС: нет стратегий голосования — нельзя задать '1 человек = 1 голос'.")
    for i, st in enumerate(strategies):
        nm = str(st.get("name", "")).lower()
        if any(m in nm for m in PLUTOCRATIC_MARKERS):
            errs.append(f"РЕЛЬС: стратегия[{i}] '{nm}' взвешивает голос по балансу/деньгам — плутократия запрещена (ст. 2, запрет №5).")
        elif nm not in EQUAL_WEIGHT_STRATEGIES:
            errs.append(f"РЕЛЬС: стратегия[{i}] '{nm}' не из разрешённых равновесных {sorted(EQUAL_WEIGHT_STRATEGIES)} — каждый адрес должен иметь ровно 1 голос.")
        val = st.get("params", {}).get("value")
        if val is not None and val != 1:
            errs.append(f"РЕЛЬС: стратегия[{i}] params.value={val} ≠ 1 — голос должен быть равным для всех.")

    # 4. Анти-Сивилла: голосование закрыто для не-верифицированных.
    filters = settings.get("filters", {})
    vote_val = settings.get("voteValidation", {})
    validation = settings.get("validation", {})
    gated = (
        filters.get("onlyMembers") is True
        or filters.get("minScore", 0) >= 1
        or (str(vote_val.get("name", "")).lower() not in ("", "any"))
        or (str(validation.get("name", "")).lower() not in ("", "any"))
        or bool(settings.get("members"))
    )
    if not gated:
        errs.append("РЕЛЬС: голосование не ограничено верифицированными участниками (нужно onlyMembers/minScore/validation) — иначе '1 человек = 1 голос' уязвимо к Сивилле.")

    # 5. Тип голосования — из разрешённого набора (не денежно-взвешенный).
    vtype = str(settings.get("voting", {}).get("type", "")).lower()
    if vtype and vtype not in ALLOWED_VOTING_TYPES:
        errs.append(f"РЕЛЬС: тип голосования '{vtype}' не из {sorted(ALLOWED_VOTING_TYPES)}.")

    # 6. Никаких приватных ключей/секретов в конфиге.
    low = raw_text.lower()
    for w in SECRET_WORDS:
        if w in low:
            errs.append(f"РЕЛЬС: в конфиге встречается '{w}' — секреты/ключи не хранятся в репо.")
    for m in PRIVKEY_RE.findall(raw_text):
        errs.append(f"РЕЛЬС: найдена 64-hex строка ({m[:10]}…) — похоже на приватный ключ. Удалить из репо.")

    # 7. Согласованность статуса.
    if cfg.get("status") == "deployed-testnet":
        for f in ("ens", "id", "controller"):
            if not space.get(f):
                errs.append(f"РЕЛЬС: статус deployed-testnet, но space.{f} не заполнен.")
        if settings.get("voting", {}).get("quorum", 0) <= 0:
            errs.append("РЕЛЬС: статус deployed-testnet, но кворум не задан (>0).")

    return errs


def verify(config_path, schema_path):
    cfg = load_json(config_path)
    schema = load_json(schema_path)
    with open(config_path, "r", encoding="utf-8") as fh:
        raw = fh.read()

    errs = schema_errors(cfg, schema)
    errs += rail_errors(cfg, raw)

    if errs:
        print(f"[snapshot] ✗ нарушений: {len(errs)}", file=sys.stderr)
        for e in errs:
            print("  - " + e, file=sys.stderr)
        return 1

    status = cfg.get("status")
    strat = ", ".join(s.get("name", "?") for s in cfg.get("settings", {}).get("strategies", []))
    space_note = "идентификаторы не заполнены (черновик — ждём оператора)" \
        if not cfg.get("space", {}).get("id") else f"space={cfg['space']['id']}"
    print(f"[snapshot] ✓ конфиг валиден: off-chain '1 человек = 1 голос' "
          f"(стратегии: {strat}) на {cfg['network']['name']} (testnet), статус={status}, {space_note}.")
    return 0


def main(argv):
    args = argv[1:]
    cmd = args[0] if args else "verify"
    if cmd != "verify":
        print("использование: snapshot_config.py verify [путь_к_конфигу]", file=sys.stderr)
        return 2
    config_path = args[1] if len(args) > 1 else DEFAULT_CONFIG
    return verify(config_path, DEFAULT_SCHEMA)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
