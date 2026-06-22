#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Guardian AI-агент — Public Trust DAO (Этап 6, модуль 2/8).

СЛУЖЕБНЫЙ МОДУЛЬ, НЕ ОРГАН ВЛАСТИ (Конституция, ст. 9).
Guardian НИЧЕГО не двигает, ничем не владеет и ничего не правит сам: он только
СКАНИРУЕТ репозиторий на нарушение рельс безопасности и докладывает «зелёно/красно».
Находка — это СИГНАЛ сообществу (и красный CI), а не действие.

Чем отличается от Audit-агента: Audit проверяет ЦЕЛОСТНОСТЬ governance-артефактов,
запуская их валидаторы (реестр/IPFS/Safe/Snapshot). Guardian — это ОТДЕЛЬНЫЙ явный
сканер РЕЛЬС БЕЗОПАСНОСТИ по ВСЕМУ дереву репозитория (а не по конкретному конфигу):
обобщает и распространяет на весь репозиторий проверки секретов/mainnet, которые в
`safe_config.py`/`snapshot_config.py` касались только одного файла.

Проверяет (по git-отслеживаемым файлам — то, что реально опубликовано):

  1. secrets-tracked  — ни один секрет/ключ не закоммичен (.env, *.key, *.pem,
     keystore/, wallet*.json, *_private*, файлы состояния пульса) ... рельс «секреты не в репо»
  2. gitignore-guards — .gitignore прикрывает .env и logs/ (пульс/состояние) ... рельс «секреты не в репо»
  3. no-mainnet       — ни в одном JSON-конфиге нет mainnet chain_id .......... рельс TESTNET-FIRST
  4. no-key-material  — в тексте нет приватных ключей (64-hex вне hash-полей,
     присваивание private key/mnemonic/seed) ........................... ст. 2/4, рельс TESTNET-FIRST

Вывод:
  • человекочитаемый отчёт в stdout (✓/✗ по каждой проверке + что защищает + находки);
  • при --json — машиночитаемый отчёт (для CI и других агентов, в т.ч. Audit);
  • код возврата 0, если все рельсы целы, иначе 1.

Зависимостей нет — только стандартная библиотека + git (для списка файлов).
TESTNET-ONLY: агент не трогает реальные средства/ключи и не выходит в сеть.
"""

import argparse
import json
import os
import re
import subprocess
import sys

# Корень репозитория = на уровень выше каталога ai-agents/.
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# --- рельс TESTNET-FIRST: mainnet chain_id запрещены (синхронно с safe_config.py) ---
MAINNET_CHAIN_IDS = {1, 10, 56, 100, 137, 8453, 42161, 43114, 250, 324, 59144, 534352}

# --- подозрение на приватный ключ: ровно 64 hex как отдельный токен (с 0x или без) ---
PRIVKEY_RE = re.compile(r"(?<![0-9a-fA-F])(?:0x)?([0-9a-fA-F]{64})(?![0-9a-fA-F])")

# Имя JSON-поля/метки перед токеном на той же строке (для отсева легитимных хэшей).
LABEL_RE = re.compile(r'["\']?([A-Za-z0-9_]+)["\']?\s*[:=]')
WORD_RE = re.compile(r"[A-Za-z0-9_]+")

# Легитимные хэш-поля: их значение — это sha256/CID/отпечаток, а НЕ ключ.
# Совпадение по подстроке покрывает head_hash, prev_hash, manifest_fingerprint_sha256 и т.п.
HASH_HINTS = ("hash", "sha", "cid", "fingerprint", "digest", "checksum", "commit", "integrity")

# Присваивание реального секрета: слово-секрет, затем `:`/`=`, затем непустое значение.
SECRET_ASSIGN_RE = re.compile(
    r"(private[_\- ]?key|mnemonic|seed[_\- ]?phrase|secret[_\- ]?key)\s*[:=]\s*(\S.*)$",
    re.IGNORECASE,
)
# Значения, которые НЕ являются утечкой (ссылки на окружение, плейсхолдеры, пусто).
# Многоточие (`...`/`…`) — явный плейсхолдер в прозе/документации (напр. `0x...`):
# настоящий приватный ключ — это 64 hex без точек, поэтому такое значение не утечка.
PLACEHOLDER_RE = re.compile(
    r"(process\.env|os\.environ|getenv|\$\{|<[^>]*>|null|none|true|false"
    r"|\"\"|''|\(\s*$|\[|\.\.\.|…)",
    re.IGNORECASE,
)

# Закоммиченные пути, которых быть НЕ должно (секреты/ключи/состояние пульса).
FORBIDDEN_PATH_RE = re.compile(
    r"(^|/)("
    r"\.env(\..*)?"          # .env, .env.local …
    r"|.*\.key"              # приватные ключи
    r"|.*\.pem"
    r"|.*\.keystore"
    r"|id_rsa.*"
    r"|.*\.mnemonic"
    r"|wallet.*\.json"       # экспорт кошелька
    r"|.*_private.*"
    r"|secrets.*"
    r"|session\.count"       # состояние пульса
    r")$",
    re.IGNORECASE,
)
# Исключения из FORBIDDEN: примеры-шаблоны без секретов допустимы.
ALLOWED_PATH_RE = re.compile(r"\.env\.example$|\.example$", re.IGNORECASE)

# Расширения, которые сканируем на текстовые секреты (бинарь/большие лок-файлы пропускаем).
SKIP_SCAN_NAMES = {"package-lock.json"}
SKIP_SCAN_EXT = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".pdf", ".woff", ".woff2"}

# Тест-инварианты самих агентов (ai-agents/test_*.py) — это «фабрики отравленных
# фикстур»: они НАМЕРЕННО собирают фейковые секреты (строки вида private_key/64-hex)
# из сгенерированных значений (`"e" * 64`), чтобы доказать, что сканеры ловят их во
# ВРЕМЕННЫХ репозиториях. Реальных ключей в этих файлах нет by design, поэтому
# текстовый скан их пропускает — иначе Guardian ложно краснеет на собственном тесте.
SKIP_KEYSCAN_RE = re.compile(r"(^|/)ai-agents/test_[A-Za-z0-9_]+\.py$")


def tracked_files():
    """Git-отслеживаемые файлы (то, что реально опубликовано). node_modules не трекается."""
    out = subprocess.run(
        ["git", "ls-files"], cwd=ROOT, stdout=subprocess.PIPE, text=True, check=True
    ).stdout
    return [p for p in out.splitlines() if p.strip()]


def looks_like_hash_line(line, start):
    """True, если 64-hex токен на этой строке — это значение хэш-поля (sha256/CID/…).

    Сначала пробуем точный признак — метка вида `head_hash:`/`sha256=`.
    Затем — более широкий: любой словесный токен в префиксе содержит хэш-подсказку
    (покрывает разметку без `:`/`=`, напр. HTML `<b>head_hash</b>`/`class="hash"`).
    Настоящий приватный ключ так не подписывают, поэтому ложных пропусков это не даёт.
    """
    prefix = line[:start]
    labels = LABEL_RE.findall(prefix)
    if labels:
        last = labels[-1].lower()
        if any(h in last for h in HASH_HINTS):
            return True
    for tok in WORD_RE.findall(prefix):
        low = tok.lower()
        if any(h in low for h in HASH_HINTS):
            return True
    return False


def check_secrets_tracked(files):
    """1. Ни один секрет/ключ/файл состояния не должен быть закоммичен."""
    hits = []
    for f in files:
        name = f.rsplit("/", 1)[-1]
        if ALLOWED_PATH_RE.search(f):
            continue
        if FORBIDDEN_PATH_RE.search("/" + f) or FORBIDDEN_PATH_RE.search(name):
            hits.append(f)
    findings = [f"закоммичен подозрительный путь: {h}" for h in sorted(set(hits))]
    return findings


def check_gitignore_guards(files):
    """2. .gitignore прикрывает секреты и состояние пульса (.env, logs/)."""
    findings = []
    gi = os.path.join(ROOT, ".gitignore")
    if not os.path.exists(gi):
        return ["нет корневого .gitignore — секреты/логи могут попасть в репо"]
    with open(gi, "r", encoding="utf-8") as fh:
        text = fh.read()
    if not re.search(r"(^|\n)\s*\*?\.env", text):
        findings.append(".gitignore не прикрывает .env")
    if not re.search(r"(^|\n)\s*logs/", text):
        findings.append(".gitignore не прикрывает logs/ (состояние пульса)")
    return findings


def _walk_chain_ids(obj, path="$"):
    """Рекурсивно собирает значения полей chain_id/chainId с их путём."""
    found = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k.lower().replace("-", "").replace("_", "") == "chainid":
                found.append((f"{path}.{k}", v))
            found.extend(_walk_chain_ids(v, f"{path}.{k}"))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            found.extend(_walk_chain_ids(v, f"{path}[{i}]"))
    return found


def check_no_mainnet(files):
    """3. Ни в одном JSON-конфиге нет mainnet chain_id (рельс TESTNET-FIRST)."""
    findings = []
    for f in files:
        if not f.endswith(".json") or f.rsplit("/", 1)[-1] in SKIP_SCAN_NAMES:
            continue
        try:
            with open(os.path.join(ROOT, f), "r", encoding="utf-8") as fh:
                data = json.load(fh)
        except (ValueError, OSError):
            continue
        for where, val in _walk_chain_ids(data):
            if isinstance(val, int) and val in MAINNET_CHAIN_IDS:
                findings.append(f"{f} {where} = {val} — это mainnet (запрещён рельсами)")
    return findings


def check_no_key_material(files):
    """4. В тексте нет приватных ключей: 64-hex вне хэш-полей + присваивание секрета."""
    findings = []
    for f in files:
        name = f.rsplit("/", 1)[-1]
        ext = os.path.splitext(name)[1].lower()
        if name in SKIP_SCAN_NAMES or ext in SKIP_SCAN_EXT:
            continue
        if SKIP_KEYSCAN_RE.search("/" + f):
            continue  # тест-инвариант агента: фабрика фейковых фикстур, не утечка
        full = os.path.join(ROOT, f)
        try:
            with open(full, "r", encoding="utf-8", errors="strict") as fh:
                lines = fh.readlines()
        except (OSError, UnicodeDecodeError):
            continue  # бинарь/нечитаемое — пропускаем
        for n, line in enumerate(lines, 1):
            for m in PRIVKEY_RE.finditer(line):
                if looks_like_hash_line(line, m.start()):
                    continue  # это sha256/CID/отпечаток, не ключ
                findings.append(f"{f}:{n} 64-hex вне хэш-поля — похоже на приватный ключ")
            am = SECRET_ASSIGN_RE.search(line)
            if am:
                value = am.group(2).strip().strip(",").strip()
                if value and not PLACEHOLDER_RE.search(value):
                    findings.append(
                        f"{f}:{n} присваивание секрета ({am.group(1)}) реальным значением"
                    )
    return findings


CHECKS = [
    {
        "key": "secrets-tracked",
        "title": "Секреты/ключи не закоммичены в репозиторий",
        "guards": "рельс «секреты никогда в репо»; ст. 6 — но без утечки приватного",
        "fn": check_secrets_tracked,
    },
    {
        "key": "gitignore-guards",
        "title": ".gitignore прикрывает .env и состояние пульса (logs/)",
        "guards": "рельс «секреты не в репо»; пульс неприкосновенен",
        "fn": check_gitignore_guards,
    },
    {
        "key": "no-mainnet",
        "title": "Ни в одном JSON-конфиге нет mainnet chain_id",
        "guards": "рельс TESTNET-FIRST — никаких mainnet/реальных средств",
        "fn": check_no_mainnet,
    },
    {
        "key": "no-key-material",
        "title": "В тексте нет приватных ключей/сид-фраз",
        "guards": "ст. 2/4 — нет владельца с ключом от реальных денег; TESTNET-FIRST",
        "fn": check_no_key_material,
    },
]


def main(argv):
    parser = argparse.ArgumentParser(
        description="Guardian AI-агент Public Trust DAO: сканер рельс безопасности по всему репо."
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="вывести машиночитаемый JSON-отчёт вместо человекочитаемого.",
    )
    args = parser.parse_args(argv[1:])

    try:
        files = tracked_files()
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        print(f"Guardian: не удалось получить список файлов git: {exc}", file=sys.stderr)
        return 1

    results = []
    for check in CHECKS:
        findings = check["fn"](files)
        results.append(
            {
                "key": check["key"],
                "title": check["title"],
                "guards": check["guards"],
                "status": "pass" if not findings else "fail",
                "findings": findings,
            }
        )

    all_pass = all(r["status"] == "pass" for r in results)
    passed = sum(1 for r in results if r["status"] == "pass")

    report = {
        "agent": "guardian",
        "role": "служебный модуль, не орган власти (Конституция, ст. 9)",
        "scanned_files": len(files),
        "verdict": "green" if all_pass else "red",
        "passed": passed,
        "total": len(results),
        "checks": results,
    }

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0 if all_pass else 1

    print("=" * 70)
    print("GUARDIAN AI-АГЕНТ — Public Trust DAO")
    print("Служебный модуль (ст. 9): сканирует рельсы, не правит. Ничего не двигает.")
    print(f"Просканировано git-отслеживаемых файлов: {len(files)}")
    print("=" * 70)
    for r in results:
        mark = "✓" if r["status"] == "pass" else "✗"
        print(f"\n{mark} [{r['key']}] {r['title']}")
        print(f"    защищает: {r['guards']}")
        for fnd in r["findings"]:
            print(f"    | {fnd}")
    print("\n" + "-" * 70)
    verdict = "ЗЕЛЁНО ✓" if all_pass else "КРАСНО ✗"
    print(f"ИТОГ: {verdict}  ({passed}/{len(results)} рельс целы)")
    print("-" * 70)
    if not all_pass:
        print("Guardian нашёл нарушение рельс безопасности. Это сигнал сообществу,")
        print("а не действие: агент не исправляет и не распоряжается — решает человек/голосование.")
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
