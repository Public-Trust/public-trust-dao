#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест-инвариант общего помощника solidity_scan.

Доказывает, что лёгкий разбор Solidity ведёт себя так, как на него
рассчитывают контрактные агенты (Reputation/Housing): комментарии вырезаются
(иначе пояснения в коде дают ложные срабатывания), функция находится по ИМЕНИ
(а не как подстрока), а тело извлекается по балансу скобок (а не до первой `}`).

Запуск: `python3 ai-agents/test_solidity_scan.py` — код возврата 0/1.
Зависимостей нет — только стандартная библиотека.
"""

import os
import sys

# Модуль лежит рядом — добавим каталог агента в путь (как при запуске агента).
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from solidity_scan import (  # noqa: E402
    strip_solidity_comments,
    has_function,
    function_signature,
    function_body,
)

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


# --- strip_solidity_comments ---------------------------------------------
print("strip_solidity_comments:")
check(
    "строчный // комментарий вырезан",
    "transfer" not in strip_solidity_comments("uint x; // нет функции transfer\n"),
)
check(
    "блочный /* */ комментарий вырезан (многострочный)",
    "approve" not in strip_solidity_comments("a;\n/* нет\nфункции approve */\nb;"),
)
check(
    "реальный код вне комментария сохранён",
    "function votingUnits" in strip_solidity_comments(
        "// пояснение\nfunction votingUnits() public {}"
    ),
)

# Ключевой сценарий контрактных агентов: пояснение в комментарии не должно
# выдавать себя за объявление функции перевода.
_soulbound_src = (
    "// У контракта НЕТ функций transfer/approve/transferFrom by design\n"
    "contract Reputation { function mint(address a) external {} }"
)
_clean = strip_solidity_comments(_soulbound_src)
print("has_function:")
check(
    "transfer из комментария НЕ считается объявлением функции",
    not has_function(_clean, "transfer"),
)
check("реальная функция mint найдена", has_function(_clean, "mint"))
check(
    "подстрока в имени не даёт ложного совпадения",
    not has_function("function transferFrom() {}", "transfer"),
)

# --- function_body: баланс скобок, а не первая `}` -----------------------
print("function_body:")
_body_src = (
    "function votingUnits(address a) public view returns (uint) {\n"
    "    if (!isMember[a]) { return 0; }\n"
    "    return 1 + min(points[a], cap);\n"
    "}\n"
)
_body = function_body(_body_src, "votingUnits")
check("тело функции извлечено", _body is not None)
check("тело включает return 0 из вложенного блока", "return 0" in _body)
check("тело включает финальный return (не оборвано на первой `}`)", "1 + min" in _body)
check("несуществующая функция → None", function_body(_body_src, "nope") is None)

# --- function_signature --------------------------------------------------
print("function_signature:")
_sig = function_signature("function release(uint id) external onlyExecutor {", "release")
check("сигнатура найдена", _sig is not None)
check("params содержит параметр", "uint id" in _sig["params"])
check("modifiers содержит модификатор видимости/доступа", "onlyExecutor" in _sig["modifiers"])
check("несуществующая функция → None", function_signature("x;", "release") is None)

# --- Итог ----------------------------------------------------------------
print()
print(f"ИТОГ: {passed} прошли, {failed} провалились")
sys.exit(0 if failed == 0 else 1)
