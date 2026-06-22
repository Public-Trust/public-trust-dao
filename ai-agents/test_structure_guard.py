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


def _write_workflow(repo_root, run_line="python3 ai-agents/run_all.py --with-tests",
                    push_paths=("ai-agents/**",), pull_request_paths=("ai-agents/**",),
                    test_line="python3 ai-agents/test_run_all.py"):
    """Кладёт .github/workflows/ai-agents.yml с заданной командой запуска и триггер-путями.

    push_paths/pull_request_paths управляют блоками `on.*.paths` (для проверки
    trigger-paths-include-agents); None означает «блок триггера вовсе отсутствует».
    test_line — отдельный шаг прогона test_run_all.py (входит в обязательные
    команды списка ci-has-required-steps); None означает «этого шага нет». По
    умолчанию оба блока содержат ai-agents/**, есть и шаг test_run_all.py, и
    run_all --with-tests — воркфлоу зелёный по обеим CI-проверкам
    (trigger-paths-include-agents и ci-has-required-steps)."""
    wf_dir = os.path.join(repo_root, ".github", "workflows")
    os.makedirs(wf_dir, exist_ok=True)
    parts = ["on:\n"]
    if push_paths is not None:
        parts.append("  push:\n    paths:\n")
        parts += ['      - "{}"\n'.format(p) for p in push_paths]
    if pull_request_paths is not None:
        parts.append("  pull_request:\n    paths:\n")
        parts += ['      - "{}"\n'.format(p) for p in pull_request_paths]
    parts.append("jobs:\n  agents:\n    steps:\n")
    # У шагов есть человеческое `- name:` → мягкая проверка ci-step-has-name
    # по умолчанию зелёная (отдельные сценарии без имени проверяются ниже).
    if test_line is not None:
        parts.append("      - name: тест мета-агента\n        run: {}\n".format(test_line))
    parts.append("      - name: прогон всех агентов\n        run: {}\n".format(run_line))
    with open(os.path.join(wf_dir, "ai-agents.yml"), "w", encoding="utf-8") as fh:
        fh.write("".join(parts))


def _write_raw_workflow(repo_root, yaml_text):
    """Кладёт .github/workflows/ai-agents.yml с дословным содержимым yaml_text.

    Нужен для точных сценариев ci-required-cmd-own-step, где важна сама форма
    шагов run: (две команды в одном блоке; команда лишь в комментарии)."""
    wf_dir = os.path.join(repo_root, ".github", "workflows")
    os.makedirs(wf_dir, exist_ok=True)
    with open(os.path.join(wf_dir, "ai-agents.yml"), "w", encoding="utf-8") as fh:
        fh.write(yaml_text)


# --- Чистый каталог: всё зелёное -----------------------------------------
# Раскладываем как настоящий репозиторий: repo/ai-agents + repo/.github/...,
# чтобы проверка ci-has-required-steps нашла воркфлоу там, где он бывает в жизни.
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
    check("все 10 проверок прошли", rep["passed"] == rep["total"] == 10)
    check("предупреждений нет (у шагов есть имена)", rep["warnings"] == 0)
    check("у шагов run: есть имена → ci-step-has-name зелёная",
          _status(rep, "ci-step-has-name") == "pass")
    check("имена шагов различны → ci-step-name-unique зелёная",
          _status(rep, "ci-step-name-unique") == "pass")
    check("именованные шаги имеют тело run: → ci-step-has-body зелёная",
          _status(rep, "ci-step-has-body") == "pass")
    check("агент с импортом из solidity_scan НЕ краснит sol-проверку",
          _status(rep, "sol-parsing-centralized") == "pass")
    check("run_all покрывает агента и тесты → run-all-covers-all зелёная",
          _status(rep, "run-all-covers-all") == "pass")
    check("триггер-пути содержат ai-agents/** → trigger-paths-include-agents зелёная",
          _status(rep, "trigger-paths-include-agents") == "pass")
    check("воркфлоу содержит оба обязательных шага → ci-has-required-steps зелёная",
          _status(rep, "ci-has-required-steps") == "pass")
    check("у каждой команды свой шаг run: → ci-required-cmd-own-step зелёная",
          _status(rep, "ci-required-cmd-own-step") == "pass")

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

# --- Проверка ci-has-required-steps: воркфлоу обязан содержать все команды списка --
# (обобщает прежние ci-calls-run-all и ci-runs-test-run-all единым списком команд)
# Воркфлоу содержит оба обязательных шага → зелёная.
print("воркфлоу содержит run_all --with-tests и test_run_all.py:")
with tempfile.TemporaryDirectory() as repo:
    d = os.path.join(repo, "ai-agents")
    os.makedirs(d)
    _write(d, "foo_agent.py")
    _write(d, "test_foo.py")
    _write(d, "run_all.py", _run_all(["foo_agent.py"], ["test_foo.py"]))
    _write_workflow(repo, "python3 ai-agents/run_all.py --with-tests")
    rep = structure_guard.run(d)
    check("ci-has-required-steps зелёная", _status(rep, "ci-has-required-steps") == "pass")

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
    check("ci-has-required-steps провалена (нет воркфлоу)",
          _status(rep, "ci-has-required-steps") == "fail")
    check("trigger-paths-include-agents провалена (нет воркфлоу)",
          _status(rep, "trigger-paths-include-agents") == "fail")

# Воркфлоу есть, но run_all не зовёт вовсе (отдельные agent-команды) → красное.
# (test_line=None убирает и шаг test_run_all.py — пропущены ОБЕ обязательные команды.)
print("воркфлоу зовёт агентов в обход run_all:")
with tempfile.TemporaryDirectory() as repo:
    d = os.path.join(repo, "ai-agents")
    os.makedirs(d)
    _write(d, "foo_agent.py")
    _write(d, "test_foo.py")
    _write(d, "run_all.py", _run_all(["foo_agent.py"], ["test_foo.py"]))
    _write_workflow(repo, "python3 ai-agents/foo_agent.py", test_line=None)
    rep = structure_guard.run(d)
    check("вердикт красный", rep["verdict"] == "red")
    check("ci-has-required-steps провалена (run_all не зовётся)",
          _status(rep, "ci-has-required-steps") == "fail")

# Воркфлоу зовёт run_all, но без --with-tests → красное (тесты не прогоняются).
# (test_line=None, чтобы изолировать пропажу именно run_all --with-tests.)
print("воркфлоу зовёт run_all без --with-tests:")
with tempfile.TemporaryDirectory() as repo:
    d = os.path.join(repo, "ai-agents")
    os.makedirs(d)
    _write(d, "foo_agent.py")
    _write(d, "test_foo.py")
    _write(d, "run_all.py", _run_all(["foo_agent.py"], ["test_foo.py"]))
    _write_workflow(repo, "python3 ai-agents/run_all.py", test_line=None)
    rep = structure_guard.run(d)
    check("вердикт красный", rep["verdict"] == "red")
    check("ci-has-required-steps провалена (нет --with-tests)",
          _status(rep, "ci-has-required-steps") == "fail")

# test_run_all.py есть, но run_all --with-tests НЕ зовётся → красное (одной команды мало).
print("воркфлоу зовёт только test_run_all.py:")
with tempfile.TemporaryDirectory() as repo:
    d = os.path.join(repo, "ai-agents")
    os.makedirs(d)
    _write(d, "foo_agent.py")
    _write(d, "test_foo.py")
    _write(d, "run_all.py", _run_all(["foo_agent.py"], ["test_foo.py"]))
    _write_workflow(repo, "python3 ai-agents/test_run_all.py")
    rep = structure_guard.run(d)
    check("ci-has-required-steps провалена (нет run_all --with-tests, хоть test_run_all.py есть)",
          _status(rep, "ci-has-required-steps") == "fail")

# --- Проверка trigger-paths-include-agents: триггеры обязаны ловить ai-agents/** --
# push.paths без ai-agents/** → красное (правка агента не запустит CI).
print("push.paths без ai-agents/**:")
with tempfile.TemporaryDirectory() as repo:
    d = os.path.join(repo, "ai-agents")
    os.makedirs(d)
    _write(d, "foo_agent.py")
    _write(d, "test_foo.py")
    _write(d, "run_all.py", _run_all(["foo_agent.py"], ["test_foo.py"]))
    _write_workflow(repo, push_paths=("docs/PRIORITIES.md",), pull_request_paths=("ai-agents/**",))
    rep = structure_guard.run(d)
    check("вердикт красный", rep["verdict"] == "red")
    check("trigger-paths-include-agents провалена (push без ai-agents/**)",
          _status(rep, "trigger-paths-include-agents") == "fail")

# pull_request.paths без ai-agents/** → красное.
print("pull_request.paths без ai-agents/**:")
with tempfile.TemporaryDirectory() as repo:
    d = os.path.join(repo, "ai-agents")
    os.makedirs(d)
    _write(d, "foo_agent.py")
    _write(d, "test_foo.py")
    _write(d, "run_all.py", _run_all(["foo_agent.py"], ["test_foo.py"]))
    _write_workflow(repo, push_paths=("ai-agents/**",), pull_request_paths=("**/*.md",))
    rep = structure_guard.run(d)
    check("вердикт красный", rep["verdict"] == "red")
    check("trigger-paths-include-agents провалена (pull_request без ai-agents/**)",
          _status(rep, "trigger-paths-include-agents") == "fail")

# Блок триггера вовсе отсутствует (нет push) → красное.
print("push-триггер отсутствует:")
with tempfile.TemporaryDirectory() as repo:
    d = os.path.join(repo, "ai-agents")
    os.makedirs(d)
    _write(d, "foo_agent.py")
    _write(d, "test_foo.py")
    _write(d, "run_all.py", _run_all(["foo_agent.py"], ["test_foo.py"]))
    _write_workflow(repo, push_paths=None, pull_request_paths=("ai-agents/**",))
    rep = structure_guard.run(d)
    check("вердикт красный", rep["verdict"] == "red")
    check("trigger-paths-include-agents провалена (нет блока push.paths)",
          _status(rep, "trigger-paths-include-agents") == "fail")

# Оба блока содержат ai-agents/** среди прочих путей → зелёная.
print("оба триггера содержат ai-agents/** среди прочих путей:")
with tempfile.TemporaryDirectory() as repo:
    d = os.path.join(repo, "ai-agents")
    os.makedirs(d)
    _write(d, "foo_agent.py")
    _write(d, "test_foo.py")
    _write(d, "run_all.py", _run_all(["foo_agent.py"], ["test_foo.py"]))
    _write_workflow(repo,
                    push_paths=("ai-agents/**", "docs/PRIORITIES.md", "**/*.md"),
                    pull_request_paths=("scripts/registry.py", "ai-agents/**"))
    rep = structure_guard.run(d)
    check("trigger-paths-include-agents зелёная (ai-agents/** есть в обоих)",
          _status(rep, "trigger-paths-include-agents") == "pass")

# Единый список различает команды по отдельности: run_all --with-tests есть, а
# test_run_all.py пропущен → красное ровно по пропавшей команде, не по всему.
print("воркфлоу не зовёт test_run_all.py (есть только run_all --with-tests):")
with tempfile.TemporaryDirectory() as repo:
    d = os.path.join(repo, "ai-agents")
    os.makedirs(d)
    _write(d, "foo_agent.py")
    _write(d, "test_foo.py")
    _write(d, "run_all.py", _run_all(["foo_agent.py"], ["test_foo.py"]))
    _write_workflow(repo, "python3 ai-agents/run_all.py --with-tests", test_line=None)
    rep = structure_guard.run(d)
    check("вердикт красный", rep["verdict"] == "red")
    check("ci-has-required-steps провалена (нет шага test_run_all.py)",
          _status(rep, "ci-has-required-steps") == "fail")
    # Нарушение указывает ровно на пропавшую команду, а run_all --with-tests не в списке нарушений.
    items = [v["item"] for c in rep["checks"] if c["key"] == "ci-has-required-steps"
             for v in c["violations"]]
    check("нарушение названо командой test_run_all.py", "test_run_all.py" in items)
    check("run_all.py --with-tests НЕ среди нарушений (он на месте)",
          "run_all.py --with-tests" not in items)

# Воркфлоу содержит обе обязательные команды → проверка зелёная.
print("воркфлоу содержит обе обязательные команды:")
with tempfile.TemporaryDirectory() as repo:
    d = os.path.join(repo, "ai-agents")
    os.makedirs(d)
    _write(d, "foo_agent.py")
    _write(d, "test_foo.py")
    _write(d, "run_all.py", _run_all(["foo_agent.py"], ["test_foo.py"]))
    _write_workflow(repo)  # дефолт: оба шага присутствуют
    rep = structure_guard.run(d)
    check("ci-has-required-steps зелёная (обе команды на месте)",
          _status(rep, "ci-has-required-steps") == "pass")

# Список обязательных команд непуст — иначе проверка была бы пустышкой.
check("REQUIRED_WORKFLOW_COMMANDS непуст",
      len(structure_guard.REQUIRED_WORKFLOW_COMMANDS) >= 2)

# --- Проверка ci-required-cmd-own-step: у каждой команды свой шаг run: -----
# _write_workflow по умолчанию даёт каждой команде ОТДЕЛЬНЫЙ `- run:` → зелёная.
print("у каждой обязательной команды свой шаг run::")
with tempfile.TemporaryDirectory() as repo:
    d = os.path.join(repo, "ai-agents")
    os.makedirs(d)
    _write(d, "foo_agent.py")
    _write(d, "test_foo.py")
    _write(d, "run_all.py", _run_all(["foo_agent.py"], ["test_foo.py"]))
    _write_workflow(repo)  # два отдельных шага
    rep = structure_guard.run(d)
    check("ci-required-cmd-own-step зелёная (у каждой команды свой шаг)",
          _status(rep, "ci-required-cmd-own-step") == "pass")

# Две обязательные команды в ОДНОМ шаге run: |  → провал одной маскирует другую.
print("две команды делят один шаг run::")
SHARED_STEP_WF = (
    'on:\n  push:\n    paths:\n      - "ai-agents/**"\n'
    '  pull_request:\n    paths:\n      - "ai-agents/**"\n'
    'jobs:\n  agents:\n    steps:\n'
    '      - run: |\n'
    '          python3 ai-agents/test_run_all.py\n'
    '          python3 ai-agents/run_all.py --with-tests\n'
)
with tempfile.TemporaryDirectory() as repo:
    d = os.path.join(repo, "ai-agents")
    os.makedirs(d)
    _write(d, "foo_agent.py")
    _write(d, "test_foo.py")
    _write(d, "run_all.py", _run_all(["foo_agent.py"], ["test_foo.py"]))
    _write_raw_workflow(repo, SHARED_STEP_WF)
    rep = structure_guard.run(d)
    # Обе команды присутствуют в файле → старая проверка не видит проблемы...
    check("ci-has-required-steps зелёная (обе команды в файле есть)",
          _status(rep, "ci-has-required-steps") == "pass")
    # ...а новая ловит, что они делят один шаг.
    check("ci-required-cmd-own-step провалена (команды делят шаг run:)",
          _status(rep, "ci-required-cmd-own-step") == "fail")
    check("вердикт красный", rep["verdict"] == "red")

# Команда есть ТОЛЬКО в комментарии → запущена не будет; старая проверка её
# «видит» (ищет по всем строкам), новая — нет (смотрит тела шагов run:).
print("обязательная команда лишь в комментарии:")
COMMENT_ONLY_WF = (
    'on:\n  push:\n    paths:\n      - "ai-agents/**"\n'
    '  pull_request:\n    paths:\n      - "ai-agents/**"\n'
    'jobs:\n  agents:\n    steps:\n'
    '      # TODO: вернуть python3 ai-agents/run_all.py --with-tests\n'
    '      - run: python3 ai-agents/test_run_all.py\n'
)
with tempfile.TemporaryDirectory() as repo:
    d = os.path.join(repo, "ai-agents")
    os.makedirs(d)
    _write(d, "foo_agent.py")
    _write(d, "test_foo.py")
    _write(d, "run_all.py", _run_all(["foo_agent.py"], ["test_foo.py"]))
    _write_raw_workflow(repo, COMMENT_ONLY_WF)
    rep = structure_guard.run(d)
    check("ci-has-required-steps зелёная (команда есть в комментарии)",
          _status(rep, "ci-has-required-steps") == "pass")
    check("ci-required-cmd-own-step провалена (команда не запускается шагом run:)",
          _status(rep, "ci-required-cmd-own-step") == "fail")
    items = [v["item"] for c in rep["checks"] if c["key"] == "ci-required-cmd-own-step"
             for v in c["violations"]]
    check("нарушение названо командой run_all.py --with-tests",
          "run_all.py --with-tests" in items)
    check("test_run_all.py НЕ среди нарушений (он в своём шаге run:)",
          "test_run_all.py" not in items)

# Блочный скаляр run: | с РАЗНЫМИ командами в разных шагах → зелёная.
print("две команды в раздельных блоках run: | :")
SEP_BLOCKS_WF = (
    'on:\n  push:\n    paths:\n      - "ai-agents/**"\n'
    '  pull_request:\n    paths:\n      - "ai-agents/**"\n'
    'jobs:\n  agents:\n    steps:\n'
    '      - name: тест мета-агента\n'
    '        run: |\n'
    '          python3 ai-agents/test_run_all.py\n'
    '      - name: прогон всех\n'
    '        run: |\n'
    '          python3 ai-agents/run_all.py --with-tests\n'
)
with tempfile.TemporaryDirectory() as repo:
    d = os.path.join(repo, "ai-agents")
    os.makedirs(d)
    _write(d, "foo_agent.py")
    _write(d, "test_foo.py")
    _write(d, "run_all.py", _run_all(["foo_agent.py"], ["test_foo.py"]))
    _write_raw_workflow(repo, SEP_BLOCKS_WF)
    rep = structure_guard.run(d)
    check("ci-required-cmd-own-step зелёная (раздельные блоки run: |)",
          _status(rep, "ci-required-cmd-own-step") == "pass")

# --- Мягкая проверка ci-step-has-name: шаг без `- name:` лишь предупреждает --
# Шаги run: без имени → warn, но вердикт остаётся зелёным (мягкая проверка).
print("шаги run: без `- name:` (мягкая проверка предупреждает, не валит):")
NO_NAME_WF = (
    'on:\n  push:\n    paths:\n      - "ai-agents/**"\n'
    '  pull_request:\n    paths:\n      - "ai-agents/**"\n'
    'jobs:\n  agents:\n    steps:\n'
    '      - run: python3 ai-agents/test_run_all.py\n'
    '      - run: python3 ai-agents/run_all.py --with-tests\n'
)
with tempfile.TemporaryDirectory() as repo:
    d = os.path.join(repo, "ai-agents")
    os.makedirs(d)
    _write(d, "foo_agent.py")
    _write(d, "test_foo.py")
    _write(d, "run_all.py", _run_all(["foo_agent.py"], ["test_foo.py"]))
    _write_raw_workflow(repo, NO_NAME_WF)
    rep = structure_guard.run(d)
    check("ci-step-has-name предупреждает (status=warn)",
          _status(rep, "ci-step-has-name") == "warn")
    check("вердикт ОСТАЁТСЯ зелёным (мягкая проверка не валит CI)",
          rep["verdict"] == "green")
    check("ровно одна предупреждающая проверка", rep["warnings"] == 1)
    items = [v["item"] for c in rep["checks"] if c["key"] == "ci-step-has-name"
             for v in c["violations"]]
    check("предупреждение названо обеими командами (оба шага без имени)",
          len(items) == 2 and "run_all.py --with-tests" in items and "test_run_all.py" in items)
    # Согласованность: зелёный вердикт ⇒ код возврата 0.
    check("код возврата 0 при зелёном вердикте с предупреждениями",
          structure_guard.main(["structure_guard", "--dir", d, "--json"]) == 0)

# Смешанный случай: один шаг с именем, другой без → предупреждение только о безымянном.
print("один шаг с именем, другой без:")
MIXED_NAME_WF = (
    'on:\n  push:\n    paths:\n      - "ai-agents/**"\n'
    '  pull_request:\n    paths:\n      - "ai-agents/**"\n'
    'jobs:\n  agents:\n    steps:\n'
    '      - name: Тест мета-агента\n'
    '        run: python3 ai-agents/test_run_all.py\n'
    '      - run: python3 ai-agents/run_all.py --with-tests\n'
)
with tempfile.TemporaryDirectory() as repo:
    d = os.path.join(repo, "ai-agents")
    os.makedirs(d)
    _write(d, "foo_agent.py")
    _write(d, "test_foo.py")
    _write(d, "run_all.py", _run_all(["foo_agent.py"], ["test_foo.py"]))
    _write_raw_workflow(repo, MIXED_NAME_WF)
    rep = structure_guard.run(d)
    check("ci-step-has-name предупреждает (есть безымянный шаг)",
          _status(rep, "ci-step-has-name") == "warn")
    check("вердикт зелёный", rep["verdict"] == "green")
    items = [v["item"] for c in rep["checks"] if c["key"] == "ci-step-has-name"
             for v in c["violations"]]
    check("предупреждение только о безымянной команде run_all.py --with-tests",
          items == ["run_all.py --with-tests"])

# Блочные скаляры с именами → ci-step-has-name зелёная (имя берётся из того же шага).
print("блочные скаляры с именами → ci-step-has-name зелёная:")
with tempfile.TemporaryDirectory() as repo:
    d = os.path.join(repo, "ai-agents")
    os.makedirs(d)
    _write(d, "foo_agent.py")
    _write(d, "test_foo.py")
    _write(d, "run_all.py", _run_all(["foo_agent.py"], ["test_foo.py"]))
    _write_raw_workflow(repo, SEP_BLOCKS_WF)  # оба шага с `- name:`
    rep = structure_guard.run(d)
    check("ci-step-has-name зелёная (у блочных шагов есть имена)",
          _status(rep, "ci-step-has-name") == "pass")
    check("разные имена → ci-step-name-unique зелёная",
          _status(rep, "ci-step-name-unique") == "pass")
    check("предупреждений нет", rep["warnings"] == 0)

# --- Мягкая проверка ci-step-name-unique: повтор имени лишь предупреждает --
# Два шага run: носят ОДНО имя → warn, но вердикт остаётся зелёным.
print("два шага run: делят одинаковое имя (мягкая проверка предупреждает, не валит):")
DUP_NAME_WF = (
    'on:\n  push:\n    paths:\n      - "ai-agents/**"\n'
    '  pull_request:\n    paths:\n      - "ai-agents/**"\n'
    'jobs:\n  agents:\n    steps:\n'
    '      - name: Прогон\n'
    '        run: python3 ai-agents/test_run_all.py\n'
    '      - name: Прогон\n'
    '        run: python3 ai-agents/run_all.py --with-tests\n'
)
with tempfile.TemporaryDirectory() as repo:
    d = os.path.join(repo, "ai-agents")
    os.makedirs(d)
    _write(d, "foo_agent.py")
    _write(d, "test_foo.py")
    _write(d, "run_all.py", _run_all(["foo_agent.py"], ["test_foo.py"]))
    _write_raw_workflow(repo, DUP_NAME_WF)
    rep = structure_guard.run(d)
    check("ci-step-name-unique предупреждает (status=warn)",
          _status(rep, "ci-step-name-unique") == "warn")
    check("вердикт ОСТАЁТСЯ зелёным (мягкая проверка не валит CI)",
          rep["verdict"] == "green")
    items = [v["item"] for c in rep["checks"] if c["key"] == "ci-step-name-unique"
             for v in c["violations"]]
    check("предупреждение названо повторяющимся именем 'Прогон' (один раз)",
          items == ["Прогон"])
    # У обоих шагов есть имя → ci-step-has-name зелёная (повтор — забота новой проверки).
    check("ci-step-has-name зелёная (имена у шагов есть)",
          _status(rep, "ci-step-has-name") == "pass")
    # Согласованность: зелёный вердикт ⇒ код возврата 0.
    check("код возврата 0 при зелёном вердикте с предупреждением о повторе имени",
          structure_guard.main(["structure_guard", "--dir", d, "--json"]) == 0)

# Безымянные шаги не считаются «повторяющими» друг друга (это забота ci-step-has-name).
print("безымянные шаги не краснят ci-step-name-unique:")
with tempfile.TemporaryDirectory() as repo:
    d = os.path.join(repo, "ai-agents")
    os.makedirs(d)
    _write(d, "foo_agent.py")
    _write(d, "test_foo.py")
    _write(d, "run_all.py", _run_all(["foo_agent.py"], ["test_foo.py"]))
    _write_raw_workflow(repo, NO_NAME_WF)  # оба шага без `- name:`
    rep = structure_guard.run(d)
    check("ci-step-name-unique зелёная (имён нет — нечему повторяться)",
          _status(rep, "ci-step-name-unique") == "pass")

# --- Мягкая проверка ci-step-has-body: пустой именованный шаг предупреждает --
# Шаг с `- name:`, но без `run:`/`uses:` (выпавшее тело) → warn, вердикт зелёный.
print("именованный шаг без тела run:/uses: (мягкая проверка предупреждает, не валит):")
EMPTY_STEP_WF = (
    'on:\n  push:\n    paths:\n      - "ai-agents/**"\n'
    '  pull_request:\n    paths:\n      - "ai-agents/**"\n'
    'jobs:\n  agents:\n    steps:\n'
    '      - name: тест мета-агента\n'
    '        run: python3 ai-agents/test_run_all.py\n'
    '      - name: прогон всех агентов\n'
    '        run: python3 ai-agents/run_all.py --with-tests\n'
    '      - name: забытый шаг\n'  # опечатка отступа: тело выпало, шаг пустой
)
with tempfile.TemporaryDirectory() as repo:
    d = os.path.join(repo, "ai-agents")
    os.makedirs(d)
    _write(d, "foo_agent.py")
    _write(d, "test_foo.py")
    _write(d, "run_all.py", _run_all(["foo_agent.py"], ["test_foo.py"]))
    _write_raw_workflow(repo, EMPTY_STEP_WF)
    rep = structure_guard.run(d)
    check("ci-step-has-body предупреждает (status=warn)",
          _status(rep, "ci-step-has-body") == "warn")
    check("вердикт ОСТАЁТСЯ зелёным (мягкая проверка не валит CI)",
          rep["verdict"] == "green")
    items = [v["item"] for c in rep["checks"] if c["key"] == "ci-step-has-body"
             for v in c["violations"]]
    check("предупреждение только о пустом шаге 'забытый шаг'", items == ["забытый шаг"])
    # Рабочие шаги с телом run: НЕ попадают в нарушения.
    check("шаги с телом run: не помечены пустыми", "прогон всех агентов" not in items)
    # Согласованность: зелёный вердикт ⇒ код возврата 0.
    check("код возврата 0 при зелёном вердикте с предупреждением о пустом шаге",
          structure_guard.main(["structure_guard", "--dir", d, "--json"]) == 0)

# Шаг с `- name:` и телом `uses:` (а не run:) — НЕ пустой → ci-step-has-body зелёная.
print("именованный шаг с телом uses: не считается пустым:")
USES_STEP_WF = (
    'on:\n  push:\n    paths:\n      - "ai-agents/**"\n'
    '  pull_request:\n    paths:\n      - "ai-agents/**"\n'
    'jobs:\n  agents:\n    steps:\n'
    '      - name: получить код\n'
    '        uses: actions/checkout@v4\n'
    '      - name: тест мета-агента\n'
    '        run: python3 ai-agents/test_run_all.py\n'
    '      - name: прогон всех агентов\n'
    '        run: python3 ai-agents/run_all.py --with-tests\n'
)
with tempfile.TemporaryDirectory() as repo:
    d = os.path.join(repo, "ai-agents")
    os.makedirs(d)
    _write(d, "foo_agent.py")
    _write(d, "test_foo.py")
    _write(d, "run_all.py", _run_all(["foo_agent.py"], ["test_foo.py"]))
    _write_raw_workflow(repo, USES_STEP_WF)
    rep = structure_guard.run(d)
    check("ci-step-has-body зелёная (uses: — это тело шага)",
          _status(rep, "ci-step-has-body") == "pass")
    check("предупреждений нет", rep["warnings"] == 0)

# Бесключевые элементы списка (пути в `on.*.paths`) не считаются пустыми шагами.
print("элементы paths не путаются с пустыми шагами:")
with tempfile.TemporaryDirectory() as repo:
    d = os.path.join(repo, "ai-agents")
    os.makedirs(d)
    _write(d, "foo_agent.py")
    _write(d, "test_foo.py")
    _write(d, "run_all.py", _run_all(["foo_agent.py"], ["test_foo.py"]))
    # дефолтный воркфлоу: в paths по `- "ai-agents/**"`, оба шага run: с именами и телом
    _write_workflow(repo)
    rep = structure_guard.run(d)
    check("ci-step-has-body зелёная (пути в paths — не пустые шаги)",
          _status(rep, "ci-step-has-body") == "pass")

# --- Сторож-регресс: настоящий каталог ai-agents/ сейчас зелёный ----------
print("настоящий каталог ai-agents/:")
real = structure_guard.run()
check("реальный репозиторий: вердикт зелёный", real["verdict"] == "green")
check("реальный репозиторий: 10/10 проверок прошли", real["passed"] == real["total"] == 10)
check("реальный репозиторий: предупреждений нет (имена шагов CI есть, уникальны, шаги не пусты)",
      real["warnings"] == 0)

# --- Итог ----------------------------------------------------------------
print()
print(f"ИТОГ: {passed} прошли, {failed} провалились")
sys.exit(0 if failed == 0 else 1)
