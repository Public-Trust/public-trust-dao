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
  • тест-инварианты прогоняются лишь при --with-tests и тоже валят общий вердикт;
  • страж структуры (structure_guard.py): его hard-«красное» валит общий вердикт,
    а мягкие предупреждения (warnings) — НЕ валят, но выводятся числом в сводке;
    отсутствие стража в каталоге неприменимо (не влияет на вердикт).

Метод: подменяем у модуля `run_all` каталог агентов (`AGENTS_DIR`) и списки
`AGENTS`/`TESTS` на набор фейковых скриптов с заранее известным поведением, затем
проверяем и кирпичики (`run_agent`/`run_test`), и общий вердикт через `main()`.
Только стандартная библиотека. Сети нет. Фейковые скрипты ничего не делают, кроме
печати фиксированного результата.
"""

import contextlib
import importlib.util
import io
import json
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


def fake_guard(verdict, passed, total, warnings, exit_code, checks=None):
    """Фейковый страж структуры: печатает отчёт того же вида, что structure_guard.py.

    `checks` — необязательный список проверок (как в реальном страже: dict с
    `key`/`title`/`severity`/`status`/`violations`), чтобы тест мог проверить вывод
    самих строк мягких предупреждений. По умолчанию пуст (поведение как раньше)."""
    checks = checks if checks is not None else []
    return (
        "import json, sys\n"
        f"print(json.dumps({{'agent':'structure_guard','verdict':{verdict!r},"
        f"'passed':{passed},'total':{total},'warnings':{warnings},"
        f"'checks':{checks!r}}}))\n"
        f"sys.exit({exit_code})\n"
    )


def write(tmp, name, content):
    with open(os.path.join(tmp, name), "w", encoding="utf-8") as fh:
        fh.write(content)


def run_main(mod, argv):
    """Запускает mod.main(argv), глуша stdout; возвращает код возврата."""
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        code = mod.main(["run_all.py"] + argv)
    return code


def run_main_capture(mod, argv):
    """Как run_main, но возвращает (код возврата, перехваченный stdout)."""
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        code = mod.main(["run_all.py"] + argv)
    return code, buf.getvalue()


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

        # --- Кирпичик run_guard: страж структуры ---
        # До сих пор structure_guard.py в tmp НЕ было → run_guard неприменим.
        print("\n[run_guard: страж структуры]")
        check("стража нет в каталоге → None (неприменимо, не валит)",
              mod.run_guard() is None)

        guard_path = os.path.join(tmp, "structure_guard.py")
        write(tmp, "structure_guard.py", fake_guard("green", 8, 10, 2, 0))
        gg = mod.run_guard()
        check("страж green/exit0 → verdict green, warnings проброшены",
              gg["verdict"] == "green" and gg["warnings"] == 2)

        write(tmp, "structure_guard.py", fake_guard("red", 5, 10, 0, 1))
        check("страж red/exit1 → verdict red", mod.run_guard()["verdict"] == "red")

        write(tmp, "structure_guard.py", fake_guard("green", 8, 10, 0, 1))  # аномалия
        check("страж green+exit!=0 (аномалия) → verdict red",
              mod.run_guard()["verdict"] == "red")

        # --- Страж в общем вердикте через main() ---
        print("\n[main: страж структуры в общем вердикте]")
        mod.AGENTS = [{"key": "a", "script": "green_agent.py", "guards": ""}]
        mod.TESTS = ["pass_test.py"]

        # Мягкие предупреждения стража НЕ валят сборку, но выводятся в сводке.
        write(tmp, "structure_guard.py", fake_guard("green", 7, 10, 3, 0))
        code, out = run_main_capture(mod, ["--with-tests"])
        check("страж с мягкими предупреждениями НЕ валит общий вердикт → exit 0", code == 0)
        check("сводка выводит число мягких предупреждений стража",
              "мягких предупреждений стража: 3" in out)

        # Сводка показывает не только ЧИСЛО, но и сами СТРОКИ предупреждений
        # (какая проверка, какой шаг) — чтобы объяснять без запуска стража.
        warn_checks = [
            {
                "key": "ci-step-has-name",
                "title": "У шага run: есть человеческое имя",
                "severity": "soft", "status": "warn",
                "violations": [{"item": "шаг #2 (run: python3 ...)",
                                "problem": "нет name:"}],
            },
            {
                "key": "agents-have-invariants",  # hard-проверка pass — не предупреждение
                "title": "...", "severity": "hard", "status": "pass",
                "violations": [],
            },
        ]
        write(tmp, "structure_guard.py", fake_guard("green", 9, 10, 1, 0, warn_checks))
        code, out = run_main_capture(mod, ["--with-tests"])
        check("страж с предупреждениями+деталями НЕ валит → exit 0", code == 0)
        check("сводка показывает сами строки предупреждений (item)",
              "шаг #2 (run: python3 ...)" in out)
        check("сводка показывает текст предупреждения (problem)", "нет name:" in out)
        check("сводка привязывает предупреждение к ключу проверки",
              "ci-step-has-name" in out)
        check("guard_warning_lines собирает только warn-проверки (hard-pass пропущен)",
              [l for l in mod.guard_warning_lines(mod.run_guard())
               if "agents-have-invariants" in l] == []
              and any("шаг #2" in l for l in mod.guard_warning_lines(mod.run_guard())))

        # Предупреждения есть (warnings>0), но детализации в checks нет → откат на
        # отсылку к стражу (обратная совместимость), сборка по-прежнему зелёная.
        write(tmp, "structure_guard.py", fake_guard("green", 7, 10, 3, 0))
        code, out = run_main_capture(mod, ["--with-tests"])
        check("предупреждения без деталей → отсылка к стражу, exit 0",
              code == 0 and "python3 ai-agents/structure_guard.py" in out)
        check("guard_warning_lines пуст, когда checks без warn", mod.guard_warning_lines(mod.run_guard()) == [])

        # --- Статус-артефакт (--status-out): машиночитаемый светофор ---
        print("\n[--status-out: машиночитаемый статус-светофор]")
        status_path = os.path.join(tmp, "status.json")
        mod.AGENTS = [
            {"key": "audit", "script": "green_agent.py", "guards": "g1"},
            {"key": "guardian", "script": "green_agent.py", "guards": "g2"},
        ]
        mod.TESTS = ["pass_test.py"]
        write(tmp, "structure_guard.py", fake_guard("green", 10, 10, 0, 0))

        # Файл НЕ пишется без флага.
        if os.path.exists(status_path):
            os.remove(status_path)
        run_main(mod, ["--with-tests", "--json"])
        check("без --status-out файл не создаётся", not os.path.exists(status_path))

        # Зелёный прогон пишет валидный, структурно полный артефакт.
        code = run_main(mod, ["--with-tests", "--json", "--status-out", status_path])
        check("--status-out пишет файл, exit не сломан", code == 0 and os.path.exists(status_path))
        with open(status_path, encoding="utf-8") as fh:
            st = json.load(fh)
        check("статус: схема версионирована", st.get("schema_version") == mod.STATUS_SCHEMA_VERSION)
        check("статус: общий вердикт green", st.get("verdict") == "green")
        check("статус: счёт агентов сведён", st["agents"] == {"green": 2, "total": 2})
        check("статус: счёт тестов сведён", st["tests"] == {"green": 1, "total": 1})
        check("статус: сводка стража с предупреждениями",
              st["guard"]["verdict"] == "green" and st["guard"]["warnings"] == 0)
        check("статус: по строке на каждого агента с ключом и вердиктом",
              [a["key"] for a in st["agent_status"]] == ["audit", "guardian"]
              and all(a["verdict"] == "green" for a in st["agent_status"]))

        # Артефакт ДЕТЕРМИНИРОВАН: повторный прогон при том же состоянии даёт
        # побайтово тот же файл (в git «грязнеет» только при смене вердикта/счёта).
        with open(status_path, "rb") as fh:
            first = fh.read()
        run_main(mod, ["--with-tests", "--json", "--status-out", status_path])
        with open(status_path, "rb") as fh:
            second = fh.read()
        check("артефакт детерминирован (нет времени по стенным часам)", first == second)

        # Красный прогон ТОЖЕ пишет артефакт (индикатор честно показывает красный свет).
        mod.AGENTS = [
            {"key": "audit", "script": "green_agent.py", "guards": "g1"},
            {"key": "guardian", "script": "red_agent.py", "guards": "g2"},
        ]
        code = run_main(mod, ["--with-tests", "--json", "--status-out", status_path])
        with open(status_path, encoding="utf-8") as fh:
            st_red = json.load(fh)
        check("красный прогон пишет артефакт с verdict=red, exit 1",
              code == 1 and st_red["verdict"] == "red" and st_red["agents"]["green"] == 1)

        # build_status без стража (None) → guard=None, не падает.
        rep_no_guard = {"verdict": "green", "agents_green": 1, "agents_total": 1,
                        "tests_green": 0, "tests_total": 0, "guard_warning_lines": [],
                        "agents": [{"key": "x", "verdict": "green", "passed": 1, "total": 1}],
                        "guard": None}
        check("build_status терпит отсутствие стража (guard=None)",
              mod.build_status(rep_no_guard)["guard"] is None)

        # Hard-«красное» стража валит общий вердикт наравне с агентами.
        mod.AGENTS = [{"key": "a", "script": "green_agent.py", "guards": ""}]
        mod.TESTS = ["pass_test.py"]
        write(tmp, "structure_guard.py", fake_guard("red", 5, 10, 0, 1))
        check("страж hard-red валит общий вердикт → exit 1",
              run_main(mod, ["--with-tests", "--json"]) == 1)

        # Стража убрали — снова неприменим, общий вердикт зелёный.
        os.remove(guard_path)
        check("стража нет → не влияет на вердикт (агент+тест зелёные) → exit 0",
              run_main(mod, ["--with-tests", "--json"]) == 0)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print(f"\nИТОГ: {PASSED} прошли, {FAILED} провалились")
    return 0 if FAILED == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
