#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест-инвариант для Run-All (мета-агента) — Public Trust DAO.

Доказывает, что мета-агент СВОДИТ вердикты верно (а не «зелёный по умолчанию»):
  • агент, вернувший green/exit=0 → засчитывается зелёным;
  • агент, вернувший red/exit=1 → красный;
  • агент, упавший без валидного JSON → красный (а не «пропущен/зелён»);
  • аномалия «verdict=green, но exit_code!=0» → красный (агент сломан);
  • общий вердикт green ТОЛЬКО если все агенты (и тесты, если включены) зелёные;
  • тест-инварианты прогоняются лишь при --with-tests и тоже валят общий вердикт.

Метод: подменяем у модуля `run_all` каталог агентов (`AGENTS_DIR`) и списки
`AGENTS`/`TESTS` на набор фейковых скриптов с заранее известным поведением, затем
проверяем и кирпичики (`run_agent`/`run_test`), и общий вердикт через `main()`.
Только стандартная библиотека. Сети нет. Фейковые скрипты ничего не делают, кроме
печати фиксированного результата.
"""

import contextlib
import importlib.util
import io
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))

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


def load_run_all():
    """Импортирует run_all.py как изолированный модуль (свежие глобальные на тест)."""
    spec = importlib.util.spec_from_file_location(
        "run_all_under_test", os.path.join(HERE, "run_all.py")
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# Фабрики содержимого фейковых агентов/тестов: печатают фиксированный результат.
def fake_agent(verdict, passed, total, exit_code):
    return (
        "import json, sys\n"
        f"print(json.dumps({{'agent':'fake','verdict':{verdict!r},"
        f"'passed':{passed},'total':{total},'checks':[]}}))\n"
        f"sys.exit({exit_code})\n"
    )


FAKE_BROKEN = "import sys\nprint('это не JSON: агент упал')\nsys.exit(1)\n"


def fake_test(exit_code):
    return f"import sys\nsys.exit({exit_code})\n"


def write(tmp, name, content):
    with open(os.path.join(tmp, name), "w", encoding="utf-8") as fh:
        fh.write(content)


def run_main(mod, argv):
    """Запускает mod.main(argv), глуша stdout; возвращает код возврата."""
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        code = mod.main(["run_all.py"] + argv)
    return code


def main():
    global FAILED
    print("ТЕСТ-ИНВАРИАНТ RUN-ALL — доказываем, что красное сводится в красное, зелёное не ложно-падает")

    tmp = tempfile.mkdtemp(prefix="runall-test-")
    try:
        write(tmp, "green_agent.py", fake_agent("green", 2, 2, 0))
        write(tmp, "red_agent.py", fake_agent("red", 1, 2, 1))
        write(tmp, "broken_agent.py", FAKE_BROKEN)
        write(tmp, "incons_agent.py", fake_agent("green", 2, 2, 1))  # аномалия
        write(tmp, "pass_test.py", fake_test(0))
        write(tmp, "fail_test.py", fake_test(1))

        mod = load_run_all()
        mod.AGENTS_DIR = tmp  # перенаправляем поиск скриптов агентов на temp

        # --- Кирпичик run_agent: каждый случай судится верно ---
        print("\n[run_agent: отдельные случаи]")
        g = mod.run_agent({"key": "g", "script": "green_agent.py", "guards": ""}, False)
        check("green/exit0 → verdict green", g["verdict"] == "green" and g["passed"] == 2)

        r = mod.run_agent({"key": "r", "script": "red_agent.py", "guards": ""}, False)
        check("red/exit1 → verdict red", r["verdict"] == "red")

        b = mod.run_agent({"key": "b", "script": "broken_agent.py", "guards": ""}, False)
        check("не-JSON (упал) → verdict red", b["verdict"] == "red")
        check("вывод упавшего агента сохранён", "не JSON" in b["output"])

        inc = mod.run_agent({"key": "i", "script": "incons_agent.py", "guards": ""}, False)
        check("green+exit!=0 (аномалия) → verdict red", inc["verdict"] == "red")

        # --- Кирпичик run_test: по коду возврата ---
        print("\n[run_test: по коду возврата]")
        tp = mod.run_test("pass_test.py")
        check("exit0 → green", tp["verdict"] == "green")
        tf = mod.run_test("fail_test.py")
        check("exit1 → red", tf["verdict"] == "red")

        # --- Общий вердикт через main() ---
        print("\n[main: сведение общего вердикта]")

        mod.AGENTS = [
            {"key": "a", "script": "green_agent.py", "guards": ""},
            {"key": "b", "script": "green_agent.py", "guards": ""},
        ]
        mod.TESTS = []
        check("все агенты зелёные → exit 0", run_main(mod, ["--json"]) == 0)

        mod.AGENTS = [
            {"key": "a", "script": "green_agent.py", "guards": ""},
            {"key": "b", "script": "red_agent.py", "guards": ""},
        ]
        check("один агент красный → exit 1", run_main(mod, ["--json"]) == 1)

        mod.AGENTS = [
            {"key": "a", "script": "green_agent.py", "guards": ""},
            {"key": "b", "script": "broken_agent.py", "guards": ""},
        ]
        check("упавший агент валит общий вердикт → exit 1", run_main(mod, ["--json"]) == 1)

        # Тесты: красный test валит вердикт ТОЛЬКО при --with-tests.
        mod.AGENTS = [{"key": "a", "script": "green_agent.py", "guards": ""}]
        mod.TESTS = ["fail_test.py"]
        check("красный тест без --with-tests НЕ влияет → exit 0",
              run_main(mod, ["--json"]) == 0)
        check("красный тест с --with-tests валит → exit 1",
              run_main(mod, ["--with-tests", "--json"]) == 1)

        mod.TESTS = ["pass_test.py"]
        check("зелёный тест с --with-tests не ложно-падает → exit 0",
              run_main(mod, ["--with-tests", "--json"]) == 0)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print(f"\nИТОГ: {PASSED} прошли, {FAILED} провалились")
    return 0 if FAILED == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
