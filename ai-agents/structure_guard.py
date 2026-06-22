#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Structure-Guard — Public Trust DAO (Этап 6, страж стандартов качества AI-агентов).

СЛУЖЕБНЫЙ МОДУЛЬ, НЕ ОРГАН ВЛАСТИ (Конституция, ст. 9).
Ничего не правит и ничем не распоряжается — он только СМОТРИТ на сам каталог
`ai-agents/` и проверяет, что в нём по-прежнему соблюдены стандарты качества,
которые мы установили в Этапе 6, но которые до сих пор держались «на честном
слове» (никакая автоматика их не стерегла):

  1. У КАЖДОГО агента есть тест-инвариант. Для каждого `*_agent.py` обязан
     существовать парный `test_<имя>.py`. Иначе агент мог бы оказаться «зелёным
     по умолчанию» — без доказательства, что он реально ловит «красное». Именно
     такой пробел был у Audit, пока в сессии 33 не дописали `test_audit.py`.

  2. Разбор Solidity не размножается копиями. Лёгкий текстовый разбор `.sol`
     (вырезание комментариев, извлечение тела/сигнатуры функции) живёт в ОДНОМ
     общем модуле `solidity_scan.py`. Ни один `*_agent.py` не должен заводить
     СВОЮ локальную копию этих помощников (`strip_solidity_comments`,
     `function_body`, `function_signature`, `has_function`) — иначе копии тихо
     разойдутся в логике, и контрактные агенты начнут проверять по-разному. Их
     надо ИМПОРТИРОВАТЬ из общего модуля, а не переопределять.

  3. Общий прогон `run_all.py` покрывает всех. Каждый существующий `*_agent.py`
     обязан быть в списке `AGENTS` мета-агента `run_all.py`, а каждый `test_*.py`
     — в списке `TESTS` (и наоборот: run_all не должен ссылаться на исчезнувший
     файл). Иначе новый агент или тест-инвариант можно было бы завести в ОБХОД
     общего прогона CI — и он бы тихо не проверялся, создавая ложное «всё зелено».

Заодно ловим «осиротевшие» тесты: для каждого `test_*.py` должен существовать
исходный модуль, который он проверяет (`<имя>_agent.py` или `<имя>.py`) — чтобы
тест-файл не остался висеть после переименования/удаления модуля.

Зачем это нужно: стандарт «у каждого агента — инвариант» и устранённое
дублирование разбора `.sol` — это качество Этапа 6, добытое трудом нескольких
сессий. Без машинного стража эти стандарты можно нечаянно нарушить и не заметить.
Этот модуль превращает их в проверку, которая валит CI при регрессе.

Запуск:
  python3 ai-agents/structure_guard.py            # человекочитаемый отчёт
  python3 ai-agents/structure_guard.py --json      # машиночитаемый отчёт
Код возврата 0, если стандарты соблюдены, иначе 1. «Красно» = сигнал сообществу,
а не действие: страж ничего не исправляет и ничем не распоряжается.

Зависимостей нет — только стандартная библиотека (детерминированно в любом CI).
TESTNET-ONLY: не трогает реальные средства/ключи и не выходит в сеть.
"""

import argparse
import json
import os
import re
import sys

AGENTS_DIR = os.path.dirname(os.path.abspath(__file__))

# Помощники разбора Solidity, которые обязаны жить только в solidity_scan.py.
# Никакой `*_agent.py` не должен переопределять их у себя — только импортировать.
CENTRALIZED_SOLIDITY_HELPERS = (
    "strip_solidity_comments",
    "function_body",
    "function_signature",
    "has_function",
)


def _list_py(agents_dir):
    """Имена всех .py-файлов в каталоге (без подкаталогов и __pycache__)."""
    return sorted(
        name for name in os.listdir(agents_dir)
        if name.endswith(".py") and os.path.isfile(os.path.join(agents_dir, name))
    )


def _agent_stem(filename):
    """audit_agent.py -> audit (имя без суффикса _agent.py)."""
    return filename[: -len("_agent.py")]


def check_agents_have_invariants(agents_dir):
    """Каждый *_agent.py обязан иметь парный test_<имя>.py."""
    files = set(_list_py(agents_dir))
    violations = []
    for name in sorted(files):
        if not name.endswith("_agent.py"):
            continue
        expected = "test_{}.py".format(_agent_stem(name))
        if expected not in files:
            violations.append({
                "item": name,
                "problem": "нет парного тест-инварианта {} (агент был бы «зелёным по умолчанию»)".format(expected),
            })
    return violations


def check_no_orphan_tests(agents_dir):
    """Каждый test_*.py обязан указывать на существующий модуль (<имя>_agent.py или <имя>.py)."""
    files = set(_list_py(agents_dir))
    violations = []
    for name in sorted(files):
        if not name.startswith("test_") or not name.endswith(".py"):
            continue
        stem = name[len("test_"): -len(".py")]
        candidates = ("{}_agent.py".format(stem), "{}.py".format(stem))
        if not any(c in files for c in candidates):
            violations.append({
                "item": name,
                "problem": "осиротевший тест: нет ни {}, ни {}".format(*candidates),
            })
    return violations


def check_sol_parsing_centralized(agents_dir):
    """Ни один *_agent.py не должен заводить локальную копию помощников разбора .sol."""
    files = _list_py(agents_dir)
    violations = []
    for name in files:
        if not name.endswith("_agent.py"):
            continue
        try:
            with open(os.path.join(agents_dir, name), "r", encoding="utf-8") as fh:
                code = fh.read()
        except OSError as exc:
            violations.append({"item": name, "problem": "не удалось прочитать файл: {}".format(exc)})
            continue
        for helper in CENTRALIZED_SOLIDITY_HELPERS:
            # Локальное определение функции (def name(...)) — а не импорт из общего модуля.
            if re.search(r"^\s*def\s+" + re.escape(helper) + r"\b", code, re.MULTILINE):
                violations.append({
                    "item": name,
                    "problem": "локально переопределяет '{}' — импортируй из solidity_scan.py, не копируй".format(helper),
                })
    return violations


def _parse_run_all(code):
    """Достаёт из исходника run_all.py множество скриптов AGENTS и список TESTS.

    Разбираем текстом (не импортируя и не исполняя файл): находим блоки
    `AGENTS = [ ... ]` и `TESTS = [ ... ]` (закрывающая `]` — в начале строки) и
    вытаскиваем имена. Из AGENTS берём значения ключа `script`, из TESTS — строки
    с именами `*.py`. Возвращает (scripts:set, tests:set)."""
    scripts = set()
    tests = set()
    m = re.search(r"AGENTS\s*=\s*\[(.*?)\n\]", code, re.DOTALL)
    if m:
        scripts = set(re.findall(r'"script"\s*:\s*"([^"]+)"', m.group(1)))
    m = re.search(r"TESTS\s*=\s*\[(.*?)\n\]", code, re.DOTALL)
    if m:
        tests = set(re.findall(r'"([^"]+\.py)"', m.group(1)))
    return scripts, tests


def check_run_all_covers_all(agents_dir):
    """Каждый *_agent.py — в AGENTS run_all.py, каждый test_*.py — в TESTS (и наоборот)."""
    files = set(_list_py(agents_dir))
    violations = []
    if "run_all.py" not in files:
        # Без мета-агента покрывать нечем: его отсутствие громко завалит другие
        # шаги CI само по себе. Считаем проверку неприменимой, не краснея.
        return violations
    try:
        with open(os.path.join(agents_dir, "run_all.py"), "r", encoding="utf-8") as fh:
            code = fh.read()
    except OSError as exc:
        return [{"item": "run_all.py", "problem": "не удалось прочитать файл: {}".format(exc)}]

    scripts, tests = _parse_run_all(code)
    # Каждый агент должен реально прогоняться общим run_all.
    for name in sorted(files):
        if name.endswith("_agent.py") and name not in scripts:
            violations.append({
                "item": name,
                "problem": "не включён в AGENTS списка run_all.py (агент в обход общего прогона CI)",
            })
    # Каждый тест-инвариант должен прогоняться run_all --with-tests.
    for name in sorted(files):
        if name.startswith("test_") and name.endswith(".py") and name not in tests:
            violations.append({
                "item": name,
                "problem": "не включён в TESTS списка run_all.py (тест в обход общего прогона CI)",
            })
    # И наоборот: run_all не должен ссылаться на исчезнувший файл.
    for ref in sorted(scripts):
        if ref not in files:
            violations.append({
                "item": ref,
                "problem": "AGENTS run_all.py ссылается на несуществующий скрипт (висячая ссылка)",
            })
    for ref in sorted(tests):
        if ref not in files:
            violations.append({
                "item": ref,
                "problem": "TESTS run_all.py ссылается на несуществующий тест (висячая ссылка)",
            })
    return violations


CHECKS = (
    {
        "key": "agents-have-invariants",
        "title": "У каждого агента есть тест-инвариант",
        "guards": "ст. 9 / стандарт Этапа 6 — агент доказывает, что ловит «красное», а не «зелёный по умолчанию»",
        "fn": check_agents_have_invariants,
    },
    {
        "key": "no-orphan-tests",
        "title": "Нет осиротевших тест-файлов",
        "guards": "ст. 3 — тест соответствует существующему модулю (карта каталога честна)",
        "fn": check_no_orphan_tests,
    },
    {
        "key": "sol-parsing-centralized",
        "title": "Разбор Solidity не размножается копиями",
        "guards": "ст. 3/6 — один источник истины solidity_scan.py, агенты проверяют одинаково",
        "fn": check_sol_parsing_centralized,
    },
    {
        "key": "run-all-covers-all",
        "title": "Общий прогон run_all.py покрывает всех агентов и все тесты",
        "guards": "ст. 3 — ни один агент/тест не заводится в обход общего прогона CI",
        "fn": check_run_all_covers_all,
    },
)


def run(agents_dir=AGENTS_DIR):
    """Прогоняет все структурные проверки каталога ai-agents/. Возвращает report dict."""
    checks = []
    for spec in CHECKS:
        try:
            violations = spec["fn"](agents_dir)
            status = "pass" if not violations else "fail"
        except OSError as exc:
            violations = [{"item": "-", "problem": "ошибка чтения каталога: {}".format(exc)}]
            status = "error"
        checks.append({
            "key": spec["key"],
            "title": spec["title"],
            "guards": spec["guards"],
            "status": status,
            "violations": violations,
        })

    all_pass = all(c["status"] == "pass" for c in checks)
    passed = sum(1 for c in checks if c["status"] == "pass")
    return {
        "agent": "structure_guard",
        "role": "служебный модуль, не орган власти (Конституция, ст. 9)",
        "verdict": "green" if all_pass else "red",
        "passed": passed,
        "total": len(checks),
        "agents_dir": os.path.basename(agents_dir.rstrip("/")),
        "checks": checks,
    }


def main(argv):
    parser = argparse.ArgumentParser(
        description="Structure-Guard Public Trust DAO: стандарты качества каталога ai-agents/."
    )
    parser.add_argument(
        "--dir", default=AGENTS_DIR,
        help="каталог агентов (по умолчанию — каталог самого скрипта).",
    )
    parser.add_argument(
        "--json", action="store_true",
        help="вывести машиночитаемый JSON-отчёт вместо человекочитаемого.",
    )
    args = parser.parse_args(argv[1:])

    report = run(args.dir)
    all_pass = report["verdict"] == "green"

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0 if all_pass else 1

    print("=" * 70)
    print("STRUCTURE-GUARD — Public Trust DAO")
    print("Служебный модуль (ст. 9): стережёт стандарты качества ai-agents/, не правит.")
    print("=" * 70)
    for c in report["checks"]:
        mark = {"pass": "✓", "fail": "✗", "error": "⚠"}[c["status"]]
        print("\n{} [{}] {}".format(mark, c["key"], c["title"]))
        print("    защищает: {}".format(c["guards"]))
        for v in c["violations"]:
            print("    | {}: {}".format(v["item"], v["problem"]))
    print("\n" + "-" * 70)
    verdict = "ЗЕЛЁНО ✓" if all_pass else "КРАСНО ✗"
    print("ИТОГ: {}  ({}/{} проверок прошли)".format(verdict, report["passed"], report["total"]))
    print("-" * 70)
    if not all_pass:
        print("Страж нашёл нарушение стандарта качества. Это сигнал сообществу,")
        print("а не действие: модуль не исправляет и ничем не распоряжается.")
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
