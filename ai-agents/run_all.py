#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Run-All (мета-агент) — Public Trust DAO (Этап 6, консолидация каркаса 8/8).

СЛУЖЕБНЫЙ МОДУЛЬ, НЕ ОРГАН ВЛАСТИ (Конституция, ст. 9).
Сам ничего не проверяет по существу и тем более ничем не распоряжается —
он только ЗАПУСКАЕТ восемь уже существующих служебных агентов и СВОДИТ их
`--json`-отчёты в один общий вердикт «зелёно/красно». Вся власть — у голосования
сообщества и Safe-мультисига; ИИ лишь помогает соблюдать конституцию.

Зачем он нужен:
  • единая точка входа вместо восьми ручных команд (локальный self-check одним вызовом);
  • в CI ~15 отдельных шагов сводятся к одному (`run_all.py --with-tests`);
  • машиночитаемая сводка (`--json`) для дашбордов и других агентов.

Восемь агентов (каркас Этапа 6):
  • audit         — целостность governance-слоя (реестр/IPFS/Safe/Snapshot) .. ст. 3/2/4
  • guardian      — рельсы безопасности по всему репо (нет ключей/секретов/mainnet) ст. 9
  • fairness      — справедливость распределения (PRIORITIES/ANTI-ABUSE) ....... ст. 5/6/7
  • reputation    — «1 человек = 1 голос» в коде (soulbound, вес [1..1+cap]) .... ст. 2
  • housing       — целевой escrow жилья в коде (транш только поставщику) ....... ст. 5
  • documentation — двуязычность RU↔EN + целостность ссылок .................... ст. 3/6
  • governance    — жизненный цикл предложения в конфигах управления (не голосует) ст. 4/5
  • mediator      — процесс споров/апелляций (структурирует, не решает) ........ ст. 9.2

Флаги:
  • --with-contracts — пробросить в Audit прогон тестов смарт-контрактов (нужен Node/npm);
  • --with-tests     — дополнительно прогнать тест-инварианты агентов (`test_*.py`):
                       доказывают, что «красное реально ловится» (а не «зелёно по умолчанию»);
  • --json           — машиночитаемый JSON-отчёт вместо человекочитаемого.

Код возврата 0, если ВСЁ зелёно, иначе 1. «Красно» = сигнал сообществу, а не действие:
мета-агент ничего не исправляет и ничем не распоряжается.

Зависимостей нет — только стандартная библиотека (детерминированно в любом CI).
TESTNET-ONLY: не трогает реальные средства/ключи и не выходит в сеть.
"""

import argparse
import json
import os
import subprocess
import sys

# Корень репозитория = на уровень выше каталога ai-agents/.
AGENTS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(AGENTS_DIR)

# Порядок намеренный: сначала целостность и рельсы (audit/guardian), затем
# справедливость и модель голоса, затем профильные/процессные агенты.
AGENTS = [
    {"key": "audit",         "script": "audit_agent.py",         "guards": "ст. 3/2/4 — целостность governance-слоя"},
    {"key": "guardian",      "script": "guardian_agent.py",      "guards": "ст. 9 — рельсы безопасности по всему репо"},
    {"key": "fairness",      "script": "fairness_agent.py",      "guards": "ст. 5/6/7 — справедливость распределения"},
    {"key": "reputation",    "script": "reputation_agent.py",    "guards": "ст. 2 — «1 человек = 1 голос» в коде"},
    {"key": "housing",       "script": "housing_agent.py",       "guards": "ст. 5 — целевой escrow жилья в коде"},
    {"key": "documentation", "script": "documentation_agent.py", "guards": "ст. 3/6 — двуязычность RU↔EN + ссылки"},
    {"key": "governance",    "script": "governance_agent.py",    "guards": "ст. 4/5 — жизненный цикл предложения"},
    {"key": "mediator",      "script": "mediator_agent.py",      "guards": "ст. 9.2 — процесс споров/апелляций"},
]

# Тест-инварианты (доказывают, что красное ловится). Покрыты все восемь агентов,
# общий помощник разбора Solidity (`solidity_scan.py`), на который опираются
# контрактные агенты Reputation/Housing, страж структуры каталога
# (`structure_guard.py`) и сам этот мета-агент (`run_all.py`): «у каждого агента
# есть тест» + «разбор .sol не копируется» + «ничто не проходит в обход прогона».
# Полнота этого списка стережётся проверкой `run-all-covers-all` в structure_guard.
TESTS = [
    "test_audit.py",
    "test_guardian.py",
    "test_fairness.py",
    "test_reputation.py",
    "test_housing.py",
    "test_documentation.py",
    "test_governance.py",
    "test_mediator.py",
    "test_solidity_scan.py",
    "test_structure_guard.py",
    "test_run_all.py",
]


def _run(cmd):
    """Запускает подпроцесс, возвращает (exit_code, stdout). Без исключений наверх."""
    try:
        proc = subprocess.run(
            cmd,
            cwd=ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=900,
        )
        return proc.returncode, proc.stdout.strip()
    except FileNotFoundError as exc:
        return 127, f"команда не найдена: {exc}"
    except subprocess.TimeoutExpired:
        return 124, "таймаут (900с)"


def run_agent(agent, with_contracts):
    """Запускает одного агента с --json и разбирает его отчёт."""
    cmd = [sys.executable, os.path.join(AGENTS_DIR, agent["script"]), "--json"]
    if agent["key"] == "audit" and with_contracts:
        cmd.append("--with-contracts")
    code, out = _run(cmd)

    result = {
        "key": agent["key"],
        "guards": agent["guards"],
        "exit_code": code,
        "verdict": "red",
        "passed": None,
        "total": None,
        "output": "",
    }
    # Разбираем JSON-отчёт агента. Несовпадение вердикта и кода возврата — само
    # по себе аномалия (агент сломан), и мы считаем это «красным».
    try:
        report = json.loads(out)
        result["verdict"] = report.get("verdict", "red")
        result["passed"] = report.get("passed")
        result["total"] = report.get("total")
        result["checks"] = report.get("checks", [])
        if result["verdict"] == "green" and code != 0:
            result["verdict"] = "red"
            result["output"] = "несогласованность: verdict=green, но exit_code!=0"
    except (ValueError, TypeError):
        # Агент не вернул валидный JSON (упал/ошибся) — это «красный» сигнал.
        result["verdict"] = "red"
        result["output"] = out
    return result


def run_test(script):
    """Запускает один тест-инвариант, судит по коду возврата."""
    code, out = _run([sys.executable, os.path.join(AGENTS_DIR, script)])
    return {
        "key": script,
        "exit_code": code,
        "verdict": "green" if code == 0 else "red",
        "output": "" if code == 0 else out,
    }


def main(argv):
    parser = argparse.ArgumentParser(
        description="Мета-агент Public Trust DAO: прогнать всех восемь агентов и свести в один вердикт."
    )
    parser.add_argument(
        "--with-contracts",
        action="store_true",
        help="пробросить в Audit прогон тестов смарт-контрактов (требует Node/npm).",
    )
    parser.add_argument(
        "--with-tests",
        action="store_true",
        help="дополнительно прогнать тест-инварианты агентов (test_*.py).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="вывести машиночитаемый JSON-отчёт вместо человекочитаемого.",
    )
    args = parser.parse_args(argv[1:])

    agent_results = [run_agent(a, args.with_contracts) for a in AGENTS]
    test_results = [run_test(t) for t in TESTS] if args.with_tests else []

    agents_green = sum(1 for r in agent_results if r["verdict"] == "green")
    tests_green = sum(1 for r in test_results if r["verdict"] == "green")
    all_green = (
        agents_green == len(agent_results)
        and tests_green == len(test_results)
    )

    report = {
        "agent": "run_all",
        "role": "служебный мета-модуль, не орган власти (Конституция, ст. 9)",
        "verdict": "green" if all_green else "red",
        "agents_green": agents_green,
        "agents_total": len(agent_results),
        "tests_green": tests_green,
        "tests_total": len(test_results),
        "agents": agent_results,
        "tests": test_results,
    }

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0 if all_green else 1

    # Человекочитаемый отчёт.
    print("=" * 70)
    print("RUN-ALL (МЕТА-АГЕНТ) — Public Trust DAO")
    print("Прогоняет всех восемь служебных агентов и сводит в один вердикт.")
    print("Служебный модуль (ст. 9): проверяет, не правит. Ничего не двигает.")
    print("=" * 70)
    print("\nАГЕНТЫ:")
    for r in agent_results:
        mark = "✓" if r["verdict"] == "green" else "✗"
        score = ""
        if r["passed"] is not None and r["total"] is not None:
            score = f"  ({r['passed']}/{r['total']})"
        print(f"\n{mark} [{r['key']}]{score}")
        print(f"    защищает: {r['guards']}")
        if r["verdict"] != "green":
            for line in (r["output"] or "(нет вывода)").splitlines():
                print(f"    | {line}")

    if test_results:
        print("\nТЕСТ-ИНВАРИАНТЫ (доказывают, что красное реально ловится):")
        for r in test_results:
            mark = "✓" if r["verdict"] == "green" else "✗"
            print(f"\n{mark} [{r['key']}]")
            if r["verdict"] != "green":
                for line in (r["output"] or "(нет вывода)").splitlines():
                    print(f"    | {line}")

    print("\n" + "-" * 70)
    verdict = "ЗЕЛЁНО ✓" if all_green else "КРАСНО ✗"
    summary = f"агенты {agents_green}/{len(agent_results)}"
    if test_results:
        summary += f", тесты {tests_green}/{len(test_results)}"
    print(f"ИТОГ: {verdict}  ({summary})")
    print("-" * 70)
    if not all_green:
        print("Сводный прогон нашёл нарушение. Это сигнал сообществу, а не действие:")
        print("мета-агент ничего не исправляет и ничем не распоряжается — решает голосование.")
    return 0 if all_green else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
