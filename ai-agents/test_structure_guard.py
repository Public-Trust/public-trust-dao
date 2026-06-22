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


def _run_all(agent_scripts, test_files):
    """Минимальный run_all.py с заданными списками AGENTS/TESTS (для проверки покрытия)."""
    agents = "".join('    {{"script": "{}"}},\n'.format(s) for s in agent_scripts)
    tests = "".join('    "{}",\n'.format(t) for t in test_files)
    return "AGENTS = [\n{}]\nTESTS = [\n{}]\n".format(agents, tests)


def _write_workflow(repo_root, run_line="python3 ai-agents/run_all.py --with-tests"):
    """Кладёт .github/workflows/ai-agents.yml с заданной командой запуска (для ci-calls-run-all)."""
    wf_dir = os.path.join(repo_root, ".github", "workflows")
    os.makedirs(wf_dir, exist_ok=True)
    with open(os.path.join(wf_dir, "ai-agents.yml"), "w", encoding="utf-8") as fh:
        fh.write("jobs:\n  agents:\n    steps:\n      - run: {}\n".format(run_line))


# --- Чистый каталог: всё зелёное -----------------------------------------
# Раскладываем как настоящий репозиторий: repo/ai-agents + repo/.github/...,
# чтобы проверка ci-calls-run-all нашла воркфлоу там, где он бывает в жизни.
print("чистый каталог:")
with tempfile.TemporaryDirectory() as repo:
    d = os.path.join(repo, "ai-agents")
    os.makedirs(d)
    _write(d, "foo_agent.py", "from solidity_scan import strip_solidity_comments\n")
    _write(d, "test_foo.py")
    _write(d, "solidity_scan.py", "def strip_solidity_comments(s):\n    return s\n")
    _write(d, "test_solidity_scan.py")
    _write(d, "run_all.py", _run_all(["foo_agent.py"], ["test_foo.py", "test_solidity_scan.py"]))
    _write_workflow(repo)
    rep = structure_guard.run(d)
    check("вердикт зелёный", rep["verdict"] == "green")
    check("все 5 проверок прошли", rep["passed"] == rep["total"] == 5)
    check("агент с импортом из solidity_scan НЕ краснит sol-проверку",
          _status(rep, "sol-parsing-centralized") == "pass")
    check("run_all покрывает агента и тесты → run-all-covers-all зелёная",
          _status(rep, "run-all-covers-all") == "pass")
    check("воркфлоу зовёт run_all --with-tests → ci-calls-run-all зелёная",
          _status(rep, "ci-calls-run-all") == "pass")

# --- Агент не включён в AGENTS run_all: красное на run-all-covers-all -----
print("агент в обход run_all:")
with tempfile.TemporaryDirectory() as d:
    _write(d, "foo_agent.py")
    _write(d, "test_foo.py")
    # run_all НЕ упоминает foo_agent.py — агент прошёл бы в обход общего прогона.
    _write(d, "run_all.py", _run_all([], ["test_foo.py"]))
    rep = structure_guard.run(d)
    check("вердикт красный", rep["verdict"] == "red")
    check("run-all-covers-all провалена (агент не покрыт)",
          _status(rep, "run-all-covers-all") == "fail")

# --- Тест не включён в TESTS run_all: красное на run-all-covers-all -------
print("тест в обход run_all:")
with tempfile.TemporaryDirectory() as d:
    _write(d, "foo_agent.py")
    _write(d, "test_foo.py")
    # run_all покрывает агента, но не его тест-инвариант.
    _write(d, "run_all.py", _run_all(["foo_agent.py"], []))
    rep = structure_guard.run(d)
    check("вердикт красный", rep["verdict"] == "red")
    check("run-all-covers-all провалена (тест не покрыт)",
          _status(rep, "run-all-covers-all") == "fail")

# --- Висячая ссылка run_all на исчезнувший файл: красное ------------------
print("висячая ссылка run_all:")
with tempfile.TemporaryDirectory() as d:
    _write(d, "foo_agent.py")
    _write(d, "test_foo.py")
    # run_all ссылается на удалённый ghost_agent.py / test_ghost.py.
    _write(d, "run_all.py", _run_all(["foo_agent.py", "ghost_agent.py"],
                                     ["test_foo.py", "test_ghost.py"]))
    rep = structure_guard.run(d)
    check("вердикт красный", rep["verdict"] == "red")
    check("run-all-covers-all провалена (висячая ссылка)",
          _status(rep, "run-all-covers-all") == "fail")

# --- Отсутствует run_all.py: проверка неприменима, не краснит ложно -------
print("нет run_all.py — проверка неприменима:")
with tempfile.TemporaryDirectory() as d:
    _write(d, "foo_agent.py")
    _write(d, "test_foo.py")
    rep = structure_guard.run(d)
    check("без run_all.py run-all-covers-all не краснит (нечего покрывать)",
          _status(rep, "run-all-covers-all") == "pass")

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

# --- Проверка ci-calls-run-all: воркфлоу обязан звать run_all --with-tests --
# Воркфлоу зовёт run_all --with-tests → зелёная.
print("воркфлоу зовёт run_all --with-tests:")
with tempfile.TemporaryDirectory() as repo:
    d = os.path.join(repo, "ai-agents")
    os.makedirs(d)
    _write(d, "foo_agent.py")
    _write(d, "test_foo.py")
    _write(d, "run_all.py", _run_all(["foo_agent.py"], ["test_foo.py"]))
    _write_workflow(repo, "python3 ai-agents/run_all.py --with-tests")
    rep = structure_guard.run(d)
    check("ci-calls-run-all зелёная", _status(rep, "ci-calls-run-all") == "pass")

# Воркфлоу вовсе не найден → красное.
print("воркфлоу не найден:")
with tempfile.TemporaryDirectory() as repo:
    d = os.path.join(repo, "ai-agents")
    os.makedirs(d)
    _write(d, "foo_agent.py")
    _write(d, "test_foo.py")
    _write(d, "run_all.py", _run_all(["foo_agent.py"], ["test_foo.py"]))
    rep = structure_guard.run(d)
    check("вердикт красный", rep["verdict"] == "red")
    check("ci-calls-run-all провалена (нет воркфлоу)", _status(rep, "ci-calls-run-all") == "fail")

# Воркфлоу есть, но run_all не зовёт вовсе (отдельные agent-команды) → красное.
print("воркфлоу зовёт агентов в обход run_all:")
with tempfile.TemporaryDirectory() as repo:
    d = os.path.join(repo, "ai-agents")
    os.makedirs(d)
    _write(d, "foo_agent.py")
    _write(d, "test_foo.py")
    _write(d, "run_all.py", _run_all(["foo_agent.py"], ["test_foo.py"]))
    _write_workflow(repo, "python3 ai-agents/foo_agent.py")
    rep = structure_guard.run(d)
    check("вердикт красный", rep["verdict"] == "red")
    check("ci-calls-run-all провалена (run_all не зовётся)", _status(rep, "ci-calls-run-all") == "fail")

# Воркфлоу зовёт run_all, но без --with-tests → красное (тесты не прогоняются).
print("воркфлоу зовёт run_all без --with-tests:")
with tempfile.TemporaryDirectory() as repo:
    d = os.path.join(repo, "ai-agents")
    os.makedirs(d)
    _write(d, "foo_agent.py")
    _write(d, "test_foo.py")
    _write(d, "run_all.py", _run_all(["foo_agent.py"], ["test_foo.py"]))
    _write_workflow(repo, "python3 ai-agents/run_all.py")
    rep = structure_guard.run(d)
    check("вердикт красный", rep["verdict"] == "red")
    check("ci-calls-run-all провалена (нет --with-tests)", _status(rep, "ci-calls-run-all") == "fail")

# test_run_all.py НЕ считается вызовом мета-агента (его одного мало).
print("воркфлоу зовёт только test_run_all.py:")
with tempfile.TemporaryDirectory() as repo:
    d = os.path.join(repo, "ai-agents")
    os.makedirs(d)
    _write(d, "foo_agent.py")
    _write(d, "test_foo.py")
    _write(d, "run_all.py", _run_all(["foo_agent.py"], ["test_foo.py"]))
    _write_workflow(repo, "python3 ai-agents/test_run_all.py")
    rep = structure_guard.run(d)
    check("ci-calls-run-all провалена (test_run_all.py ≠ запуск run_all)",
          _status(rep, "ci-calls-run-all") == "fail")

# --- Сторож-регресс: настоящий каталог ai-agents/ сейчас зелёный ----------
print("настоящий каталог ai-agents/:")
real = structure_guard.run()
check("реальный репозиторий: вердикт зелёный", real["verdict"] == "green")
check("реальный репозиторий: 5/5 проверок прошли", real["passed"] == real["total"] == 5)

# --- Итог ----------------------------------------------------------------
print()
print(f"ИТОГ: {passed} прошли, {failed} провалились")
sys.exit(0 if failed == 0 else 1)
