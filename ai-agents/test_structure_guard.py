#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест-инвариант стража структуры (structure_guard).

Доказывает, что страж РЕАЛЬНО ловит «красное», а не «зелёный по умолчанию»:
на отравленных временных каталогах он краснеет (агент без теста; осиротевший
тест; агент с локальной копией разбора Solidity), а на чистом каталоге — зелёный.
Плюс «сторож-регресс»: на настоящем каталоге ai-agents/ страж сейчас зелёный
(если кто-то добавит агента без теста или скопирует разбор .sol — этот тест
покраснеет и завалит CI).

Запуск: `python3 ai-agents/test_structure_guard.py` — код возврата 0/1.
Зависимостей нет — только стандартная библиотека.
"""

import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import structure_guard  # noqa: E402

passed = 0
failed = 0


def check(name, cond):
    global passed, failed
    if cond:
        passed += 1
        print(f"  ✓ {name}")
    else:
        failed += 1
        print(f"  ✗ {name}")


def _write(d, name, text=""):
    with open(os.path.join(d, name), "w", encoding="utf-8") as fh:
        fh.write(text)


def _status(report, key):
    for c in report["checks"]:
        if c["key"] == key:
            return c["status"]
    return None


# --- Чистый каталог: всё зелёное -----------------------------------------
print("чистый каталог:")
with tempfile.TemporaryDirectory() as d:
    _write(d, "foo_agent.py", "from solidity_scan import strip_solidity_comments\n")
    _write(d, "test_foo.py")
    _write(d, "solidity_scan.py", "def strip_solidity_comments(s):\n    return s\n")
    _write(d, "test_solidity_scan.py")
    rep = structure_guard.run(d)
    check("вердикт зелёный", rep["verdict"] == "green")
    check("все 3 проверки прошли", rep["passed"] == rep["total"] == 3)
    check("агент с импортом из solidity_scan НЕ краснит sol-проверку",
          _status(rep, "sol-parsing-centralized") == "pass")

# --- Агент без парного теста: красное на agents-have-invariants ----------
print("агент без теста:")
with tempfile.TemporaryDirectory() as d:
    _write(d, "bar_agent.py")
    rep = structure_guard.run(d)
    check("вердикт красный", rep["verdict"] == "red")
    check("agents-have-invariants провалена", _status(rep, "agents-have-invariants") == "fail")

# --- Осиротевший тест: красное на no-orphan-tests ------------------------
print("осиротевший тест:")
with tempfile.TemporaryDirectory() as d:
    _write(d, "test_ghost.py")
    rep = structure_guard.run(d)
    check("вердикт красный", rep["verdict"] == "red")
    check("no-orphan-tests провалена", _status(rep, "no-orphan-tests") == "fail")

# test_<x>.py со ссылкой на <x>.py (не агент) — не сирота.
print("тест на не-агентный модуль:")
with tempfile.TemporaryDirectory() as d:
    _write(d, "helper.py")
    _write(d, "test_helper.py")
    rep = structure_guard.run(d)
    check("helper.py закрывает test_helper.py (не сирота)",
          _status(rep, "no-orphan-tests") == "pass")

# --- Локальная копия разбора .sol: красное на sol-parsing-centralized ----
print("локальная копия разбора .sol:")
with tempfile.TemporaryDirectory() as d:
    _write(d, "baz_agent.py", "def strip_solidity_comments(src):\n    return src\n")
    _write(d, "test_baz.py")
    rep = structure_guard.run(d)
    check("вердикт красный", rep["verdict"] == "red")
    check("sol-parsing-centralized провалена", _status(rep, "sol-parsing-centralized") == "fail")

# Все централизованные помощники ловятся как локальные копии.
print("все централизованные помощники ловятся:")
for helper in structure_guard.CENTRALIZED_SOLIDITY_HELPERS:
    with tempfile.TemporaryDirectory() as d:
        _write(d, "qux_agent.py", "def {}(x):\n    return x\n".format(helper))
        _write(d, "test_qux.py")
        rep = structure_guard.run(d)
        check("'{}' пойман как локальная копия".format(helper),
              _status(rep, "sol-parsing-centralized") == "fail")

# Импорт того же имени — НЕ срабатывает (импорт ≠ переопределение).
print("импорт помощника не считается копией:")
with tempfile.TemporaryDirectory() as d:
    _write(d, "imp_agent.py", "from solidity_scan import function_body\n")
    _write(d, "test_imp.py")
    rep = structure_guard.run(d)
    check("импорт function_body не краснит sol-проверку",
          _status(rep, "sol-parsing-centralized") == "pass")

# --- Сторож-регресс: настоящий каталог ai-agents/ сейчас зелёный ----------
print("настоящий каталог ai-agents/:")
real = structure_guard.run()
check("реальный репозиторий: вердикт зелёный", real["verdict"] == "green")
check("реальный репозиторий: 3/3 проверок прошли", real["passed"] == real["total"] == 3)

# --- Итог ----------------------------------------------------------------
print()
print(f"ИТОГ: {passed} прошли, {failed} провалились")
sys.exit(0 if failed == 0 else 1)
