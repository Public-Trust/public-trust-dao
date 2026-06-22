#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Audit AI-агент — Public Trust DAO (Этап 6, модуль 1/8).

СЛУЖЕБНЫЙ МОДУЛЬ, НЕ ОРГАН ВЛАСТИ (Конституция, ст. 9).
Агент НИЧЕГО не двигает и ничем не владеет: он только ПРОВЕРЯЕТ целостность и
прозрачность governance-слоя и докладывает «зелёно/красно». Вся власть — у
голосования сообщества и Safe-мультисига; ИИ лишь помогает соблюдать конституцию.

Что делает: объединяет четыре уже существующих рельс-валидатора в один аудит-прогон
и связывает каждую проверку со статьёй конституции, которую она защищает:

  • registry.py  verify  → реестр решений (hash-chain) ........... ст. 3 (открытость)
  • ipfs_manifest.py verify → IPFS-манифест (CID + sha256) ....... ст. 3 (неизменяемость)
  • safe_config.py verify → Safe multisig 3-из-5 (testnet) ....... ст. 2/4 (нет владельца)
  • snapshot_config.py verify → off-chain «1 чел = 1 голос» ...... ст. 2 (не плутократия)

Опционально (--with-contracts): прогон тестов смарт-контрактов (требует Node/npm).

Вывод:
  • человекочитаемый отчёт в stdout (✓/✗ по каждой проверке + привязка к статье);
  • при --json — машиночитаемый отчёт (для CI и других агентов);
  • код возврата 0, если все проверки прошли, иначе 1.

Зависимостей нет — только стандартная библиотека (детерминированно в любом CI).
TESTNET-ONLY: агент не трогает реальные средства/ключи и не выходит в сеть.
"""

import argparse
import json
import os
import subprocess
import sys

# Корень репозитория = на уровень выше каталога ai-agents/.
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "scripts")
CONTRACTS = os.path.join(ROOT, "contracts")

# Каждая проверка явно привязана к статье конституции, которую она защищает, —
# аудит должен объяснять НЕ ТОЛЬКО «прошло/нет», но и «что именно это гарантирует».
CHECKS = [
    {
        "key": "registry",
        "title": "Реестр решений (hash-chain, append-only)",
        "guards": "ст. 3 — открытость и проверяемость; неизменяемость записей",
        "cmd": [sys.executable, os.path.join(SCRIPTS, "registry.py"), "verify"],
    },
    {
        "key": "ipfs",
        "title": "IPFS-манифест ключевых документов (CID + sha256)",
        "guards": "ст. 3 — содержимое и опубликованные CID не расходятся незаметно",
        "cmd": [sys.executable, os.path.join(SCRIPTS, "ipfs_manifest.py"), "verify"],
    },
    {
        "key": "safe",
        "title": "Safe multisig 3-из-5 (testnet, без приватных ключей)",
        "guards": "ст. 2/4 — никто не владеет казной единолично; рельс TESTNET-FIRST",
        "cmd": [sys.executable, os.path.join(SCRIPTS, "safe_config.py"), "verify"],
    },
    {
        "key": "snapshot",
        "title": "Snapshot off-chain «1 человек = 1 голос»",
        "guards": "ст. 2 — не плутократия (вес голоса не по балансу токена); анти-Сивилла",
        "cmd": [sys.executable, os.path.join(SCRIPTS, "snapshot_config.py"), "verify"],
    },
]

CONTRACTS_CHECK = {
    "key": "contracts",
    "title": "Тесты смарт-контрактов (Hardhat, in-process сеть)",
    "guards": "ст. 4/7 — конституционные свойства казны/escrow/управления в коде",
    "cmd": ["npm", "test", "--silent"],
    "cwd": CONTRACTS,
}


def run_check(check):
    """Запускает одну проверку, возвращает dict с результатом (без исключений наверх)."""
    cwd = check.get("cwd", ROOT)
    try:
        proc = subprocess.run(
            check["cmd"],
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=600,
        )
        code = proc.returncode
        output = proc.stdout.strip()
        status = "pass" if code == 0 else "fail"
    except FileNotFoundError as exc:
        code, output, status = 127, f"команда не найдена: {exc}", "error"
    except subprocess.TimeoutExpired:
        code, output, status = 124, "таймаут проверки (600с)", "error"
    return {
        "key": check["key"],
        "title": check["title"],
        "guards": check["guards"],
        "status": status,
        "exit_code": code,
        "output": output,
    }


def main(argv):
    parser = argparse.ArgumentParser(
        description="Audit AI-агент Public Trust DAO: единый аудит governance-целостности."
    )
    parser.add_argument(
        "--with-contracts",
        action="store_true",
        help="дополнительно прогнать тесты смарт-контрактов (требует Node/npm в contracts/).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="вывести машиночитаемый JSON-отчёт вместо человекочитаемого.",
    )
    args = parser.parse_args(argv[1:])

    checks = list(CHECKS)
    if args.with_contracts:
        checks.append(CONTRACTS_CHECK)

    results = [run_check(c) for c in checks]
    all_pass = all(r["status"] == "pass" for r in results)
    passed = sum(1 for r in results if r["status"] == "pass")

    report = {
        "agent": "audit",
        "role": "служебный модуль, не орган власти (Конституция, ст. 9)",
        "verdict": "green" if all_pass else "red",
        "passed": passed,
        "total": len(results),
        "checks": results,
    }

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0 if all_pass else 1

    # Человекочитаемый отчёт.
    print("=" * 70)
    print("AUDIT AI-АГЕНТ — Public Trust DAO")
    print("Служебный модуль (ст. 9): проверяет, не правит. Ничего не двигает.")
    print("=" * 70)
    for r in results:
        mark = {"pass": "✓", "fail": "✗", "error": "⚠"}[r["status"]]
        print(f"\n{mark} [{r['key']}] {r['title']}")
        print(f"    защищает: {r['guards']}")
        if r["status"] != "pass":
            for line in r["output"].splitlines():
                print(f"    | {line}")
    print("\n" + "-" * 70)
    verdict = "ЗЕЛЁНО ✓" if all_pass else "КРАСНО ✗"
    print(f"ИТОГ: {verdict}  ({passed}/{len(results)} проверок прошли)")
    print("-" * 70)
    if not all_pass:
        print("Аудит нашёл нарушение целостности/рельс. Это сигнал сообществу,")
        print("а не действие: агент не исправляет и не распоряжается — решает голосование.")
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
