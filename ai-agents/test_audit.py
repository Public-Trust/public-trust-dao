#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест-инвариант для Audit-агента — Public Trust DAO (Этап 6, стандарт качества).

Audit — единственный из восьми агентов, у которого долго не было собственного
тест-инварианта (см. ROADMAP, идея сессий 24/32). Этот файл закрывает пробел:
доказывает, что Audit СВОДИТ вердикт честно, а не «зелёный по умолчанию».

Что доказываем:
  1. Кирпичик `run_check`:
       • команда exit=0  → status "pass";
       • команда exit=1  → status "fail";
       • несуществующая команда → status "error" (а не молча «pass»).
  2. Сведение вердикта `main`:
       • все проверки прошли → verdict green, exit 0;
       • любая проверка fail → verdict red,  exit 1;
       • любая проверка error (упала/не найдена) → verdict red, exit 1
         (Audit НЕ зеленеет при молчаливом отказе проверки).
  3. Интеграция с НАСТОЯЩИМИ рельс-валидаторами (самое ценное):
       • на настоящем репозитории дефолтный набор проверок → green
         (нет ложного «красного» на здоровом дереве);
       • если подсунуть реально нарушенный governance-артефакт
         (Safe-конфиг с mainnet chain_id; Snapshot-конфиг с плутократической
         стратегией), настоящий валидатор краснеет, и Audit это поднимает в red.

Метод: грузим `audit_agent.py` как изолированный модуль и подменяем у него
список `CHECKS` (как `test_run_all.py` подменяет `AGENTS`/`TESTS`). Часть 3
строит ОТРАВЛЕННЫЕ КОПИИ настоящих конфигов во временном файле и направляет на
них настоящие `scripts/safe_config.py` / `scripts/snapshot_config.py`.

Только стандартная библиотека. Сети нет. Реальные конфиги репозитория НЕ
изменяются — поломки живут лишь во временных копиях.
"""

import contextlib
import copy
import importlib.util
import io
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SCRIPTS = os.path.join(ROOT, "scripts")

PASSED = 0
FAILED = 0


def check(name, cond):
    global PASSED, FAILED
    if cond:
        PASSED += 1
        print(f"  ✓ {name}")
    else:
        FAILED += 1
        print(f"  ✗ {name}")


def load_audit():
    """Импортирует audit_agent.py как изолированный модуль (свежие глобальные)."""
    spec = importlib.util.spec_from_file_location(
        "audit_agent_under_test", os.path.join(HERE, "audit_agent.py")
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def py_check(key, code, exit_code):
    """Синтетическая проверка: python -c <code>; sys.exit(exit_code)."""
    return {
        "key": key,
        "title": f"синтетическая проверка {key}",
        "guards": "тест",
        "cmd": [sys.executable, "-c", f"{code}\nimport sys; sys.exit({exit_code})"],
    }


def real_check(key, script, *extra):
    """Проверка, вызывающая НАСТОЯЩИЙ валидатор из scripts/ (с доп. аргументами)."""
    return {
        "key": key,
        "title": f"настоящий валидатор {script}",
        "guards": "рельсы",
        "cmd": [sys.executable, os.path.join(SCRIPTS, script), "verify", *extra],
    }


def run_main(mod, argv):
    """Запускает mod.main(argv), глуша stdout; возвращает код возврата."""
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        code = mod.main(["audit_agent.py"] + argv)
    return code, buf.getvalue()


def verdict_of(mod, argv):
    """Прогоняет main с --json и возвращает (exit_code, verdict)."""
    code, out = run_main(mod, argv + ["--json"])
    try:
        verdict = json.loads(out)["verdict"]
    except (ValueError, KeyError):
        verdict = "<нет JSON>"
    return code, verdict


def write_json(path, obj):
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=2)


def main():
    print("ТЕСТ-ИНВАРИАНТ AUDIT — доказываем, что красное сводится в красное, "
          "зелёное не ложно-падает")

    mod = load_audit()

    # --- Часть 1: кирпичик run_check ---
    print("\n[run_check: отдельные случаи]")
    p = mod.run_check(py_check("ok", "pass", 0))
    check("exit=0 → status pass", p["status"] == "pass" and p["exit_code"] == 0)

    f = mod.run_check(py_check("bad", "pass", 1))
    check("exit=1 → status fail", f["status"] == "fail")

    e = mod.run_check({
        "key": "missing", "title": "нет такой команды", "guards": "тест",
        "cmd": ["definitely-not-a-real-command-xyz-ptd"],
    })
    check("несуществующая команда → status error (не pass)", e["status"] == "error")

    # --- Часть 2: сведение вердикта main (синтетические проверки) ---
    print("\n[main: сведение общего вердикта на синтетике]")

    mod.CHECKS = [py_check("a", "pass", 0), py_check("b", "pass", 0)]
    code, verdict = verdict_of(mod, [])
    check("все проверки прошли → green, exit 0", verdict == "green" and code == 0)

    mod.CHECKS = [py_check("a", "pass", 0), py_check("b", "pass", 1)]
    code, verdict = verdict_of(mod, [])
    check("одна проверка fail → red, exit 1", verdict == "red" and code == 1)

    mod.CHECKS = [
        py_check("a", "pass", 0),
        {"key": "x", "title": "падение", "guards": "тест",
         "cmd": ["definitely-not-a-real-command-xyz-ptd"]},
    ]
    code, verdict = verdict_of(mod, [])
    check("проверка-ошибка (упала) валит вердикт → red, exit 1 "
          "(не зелёный по умолчанию)", verdict == "red" and code == 1)

    # --- Часть 3: интеграция с НАСТОЯЩИМИ валидаторами ---
    print("\n[main: настоящие рельс-валидаторы на здоровом и отравленном дереве]")

    # 3a. Дефолтный набор на настоящем репозитории — не должен ложно краснеть.
    mod.CHECKS = [
        real_check("safe", "safe_config.py"),
        real_check("snapshot", "snapshot_config.py"),
    ]
    code, verdict = verdict_of(mod, [])
    check("настоящие safe+snapshot на здоровом репо → green", verdict == "green")

    tmp = tempfile.mkdtemp(prefix="audit-test-")
    try:
        # 3b. Safe-конфиг с mainnet chain_id — нарушение рельса TESTNET-FIRST.
        with open(os.path.join(ROOT, "governance", "safe", "safe.config.json"),
                  encoding="utf-8") as fh:
            safe_cfg = json.load(fh)
        bad_safe = copy.deepcopy(safe_cfg)
        bad_safe["network"]["chain_id"] = 1          # Ethereum mainnet — запрещено
        bad_safe["network"]["is_testnet"] = True     # маскировка не должна помочь
        bad_safe_path = os.path.join(tmp, "bad_safe.json")
        write_json(bad_safe_path, bad_safe)

        mod.CHECKS = [real_check("safe", "safe_config.py", bad_safe_path)]
        code, verdict = verdict_of(mod, [])
        check("Safe с mainnet chain_id → настоящий валидатор краснеет, Audit red",
              verdict == "red" and code == 1)

        # 3c. Snapshot-конфиг с плутократической стратегией — нарушение «1 чел = 1 голос».
        with open(os.path.join(ROOT, "governance", "snapshot", "space.json"),
                  encoding="utf-8") as fh:
            snap_cfg = json.load(fh)
        bad_snap = copy.deepcopy(snap_cfg)
        for strat in bad_snap["settings"]["strategies"]:
            strat["name"] = "erc20-balance-of"       # вес по балансу токена — плутократия
        bad_snap_path = os.path.join(tmp, "bad_snapshot.json")
        write_json(bad_snap_path, bad_snap)

        mod.CHECKS = [real_check("snapshot", "snapshot_config.py", bad_snap_path)]
        code, verdict = verdict_of(mod, [])
        check("Snapshot с плутократической стратегией → валидатор краснеет, Audit red",
              verdict == "red" and code == 1)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print(f"\nИТОГ: {PASSED} прошли, {FAILED} провалились")
    return 0 if FAILED == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
