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

  4. Триггер-пути воркфлоу включают `ai-agents/**`. Даже если воркфлоу зовёт
     `run_all.py --with-tests`, он бесполезен, когда не СРАБАТЫВАЕТ на изменение
     агента. Если в `on.push.paths` (и `on.pull_request.paths`) нет `ai-agents/**`,
     правка агента не запустит сборку — и покрытие обходится ещё раньше, на уровне
     триггера, чем на уровне команды (#5). Эта проверка смотрит сами блоки путей.

  5. CI-воркфлоу содержит ВСЕ обязательные шаги (единый список команд). Полные
     списки `AGENTS`/`TESTS` бесполезны, если сам файл
     `.github/workflows/ai-agents.yml` не запускает нужных команд: покрытие
     обходится уже на уровне CI (проверка #3 «зелёная», а в сборке ничего не
     прогоняется). Вместо россыпи почти одинаковых проверок «зовёт ли воркфлоу
     команду X» держим ОДИН список обязательных команд воркфлоу
     (`REQUIRED_WORKFLOW_COMMANDS`) и краснеем при пропаже любой из них. Сейчас в
     списке две команды: `run_all.py --with-tests` (прогоняет всех агентов и их
     тест-инварианты; без `--with-tests` тесты не исполняются, агенты в обход) и
     `test_run_all.py` (собственный тест-инвариант мета-агента: доказывает, что
     сведение «красное→красное» исправно — иначе сводка могла бы тихо рапортовать
     «зелено» при красном агенте). Добавил обязательный шаг CI — допиши строку в
     список, и страж проследит, что его не забыли: новый шаг нельзя обойти, не
     размножая код проверок.

  6. У КАЖДОЙ обязательной команды CI — свой шаг `run:`. Проверка #5 видит
     команду «где угодно» в файле — включая комментарий или название шага. Эта
     смотрит сами тела шагов `run:` и требует, чтобы каждая обязательная команда
     запускалась отдельным шагом и не делила его с другой. Иначе провал одной
     маскирует другую: в одном `run:` с `&&` вторая команда не исполнится после
     падения первой, а оставшаяся лишь в комментарии не исполняется вовсе. Свой
     шаг — свой код возврата, свой провал на виду.

  7. (МЯГКАЯ) У шага `run:` обязательной команды есть человеческое `- name:`.
     Развитие #6 в сторону читаемости: если у шага нет имени, в логах GitHub
     Actions упавший шаг показывается голой командой, а не по-человечески
     («Прогнать всех агентов»). Это НЕ ломает покрытие, поэтому проверка лишь
     ПРЕДУПРЕЖДАЕТ (severity=soft) — не валит CI, а подсказывает улучшить
     читаемость ради людей, для которых строится фонд (ст. 3 «понятность»).

  8. (МЯГКАЯ) Шаги `run:` не делят одинаковое `- name:`. Развитие #7: имя у
     шага есть, но если два шага носят ОДНО имя, в логах GitHub Actions их не
     различить — упавший шаг читается двусмысленно. Тоже лишь ПРЕДУПРЕЖДАЕТ
     (severity=soft), а не валит CI.

  9. (МЯГКАЯ) У шага с `- name:` есть тело `run:`/`uses:` (не пустой шаг).
     Развитие #8 в сторону честности карты шагов: если элемент списка несёт
     `- name:`, но НИ `run:`, НИ `uses:`, это почти всегда опечатка отступа —
     тело шага «выпало» из него, и шаг ничего не делает, хотя в интерфейсе
     GitHub Actions выглядит настоящим. Тоже лишь ПРЕДУПРЕЖДАЕТ (severity=soft):
     реальный пропуск обязательной команды поймают hard-проверки выше, а эта
     бережёт читаемость карты CI ради людей (ст. 3 «понятность»).

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

# Путь CI-воркфлоу (от корня репозитория, т.е. от родителя каталога агентов),
# который ОБЯЗАН прогонять мета-агента run_all.py с тест-инвариантами.
CI_WORKFLOW_REL = os.path.join(".github", "workflows", "ai-agents.yml")

# Glob, который ОБЯЗАН стоять в триггер-путях воркфлоу, чтобы правка любого
# файла каталога агентов запускала CI (иначе покрытие обходится на уровне триггера).
AGENTS_GLOB = "ai-agents/**"

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


def _yaml_list_under(text, keypath):
    """Достаёт список значений (`- "..."`) под цепочкой ключей YAML по отступам.

    Разбираем текстом (без сторонних зависимостей): идём по `keypath`
    (например, ("on", "push", "paths")), на каждом шаге находим ключ строго
    глубже предыдущего по отступу, в конце собираем элементы списка `- ...`
    глубже последнего ключа. Возвращает list строк или None, если путь не найден.
    Достаточно для блочного YAML наших воркфлоу (не инлайн `on: [push]`)."""
    lines = text.splitlines()
    idx = 0
    parent_indent = -1
    for depth, key in enumerate(keypath):
        found = False
        while idx < len(lines):
            line = lines[idx]
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                idx += 1
                continue
            indent = len(line) - len(line.lstrip())
            if depth > 0 and indent <= parent_indent:
                # Вышли из родительского блока, не встретив ключ.
                return None
            if (not stripped.startswith("- ") and ":" in stripped
                    and stripped.split(":", 1)[0].strip() == key):
                parent_indent = indent
                idx += 1
                found = True
                break
            idx += 1
        if not found:
            return None
    items = []
    while idx < len(lines):
        line = lines[idx]
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            idx += 1
            continue
        indent = len(line) - len(line.lstrip())
        if indent <= parent_indent:
            break
        if stripped.startswith("- "):
            items.append(stripped[2:].strip().strip('"').strip("'"))
        idx += 1
    return items


def check_trigger_paths_include_agents(agents_dir):
    """on.push.paths и on.pull_request.paths воркфлоу обязаны содержать ai-agents/**.

    ci-has-required-steps сторожит, что воркфлоу ЗОВЁТ обязательные команды. Но
    вызов бесполезен, если воркфлоу не СРАБАТЫВАЕТ на правку агента: без `ai-agents/**`
    в триггер-путях изменение в каталоге агентов не запустит CI, и покрытие
    обходится ещё раньше — на уровне триггера, а не команды. Эта проверка читает
    сами блоки путей push и pull_request."""
    repo_root = os.path.dirname(os.path.abspath(agents_dir.rstrip("/")))
    wf_path = os.path.join(repo_root, CI_WORKFLOW_REL)
    if not os.path.isfile(wf_path):
        return [{
            "item": CI_WORKFLOW_REL,
            "problem": "CI-воркфлоу не найден — триггеры некому проверить (правка агента не запустит CI)",
        }]
    try:
        with open(wf_path, "r", encoding="utf-8") as fh:
            text = fh.read()
    except OSError as exc:
        return [{"item": CI_WORKFLOW_REL, "problem": "не удалось прочитать файл: {}".format(exc)}]

    violations = []
    for trigger in ("push", "pull_request"):
        paths = _yaml_list_under(text, ("on", trigger, "paths"))
        where = "on.{}.paths".format(trigger)
        if paths is None:
            violations.append({
                "item": where,
                "problem": "блок путей отсутствует — изменение в ai-agents/ не запустит CI по этому триггеру",
            })
        elif AGENTS_GLOB not in paths:
            violations.append({
                "item": where,
                "problem": "не содержит '{}' — правка агента не запустит CI (покрытие обходится на уровне триггера)".format(AGENTS_GLOB),
            })
    return violations


# Команды, которые ОБЯЗАН содержать CI-воркфлоу. Единый список вместо россыпи
# почти одинаковых проверок «зовёт ли воркфлоу команду X»: добавил обязательный
# шаг CI — допиши сюда строку, и страж проследит, что его не забыли. Каждый
# элемент: ключ-метка, regex для поиска по строкам воркфлоу и человеческое «зачем».
# `\b` перед `run_all` не даёт спутать мета-агента с test_run_all.py (там перед
# 'run_all' стоит словесный символ '_'), так что это разные обязательные команды.
REQUIRED_WORKFLOW_COMMANDS = (
    {
        "key": "run_all.py --with-tests",
        "pattern": r"\brun_all\.py\b.*--with-tests",
        "why": "прогоняет всех агентов и их тест-инварианты одним мета-агентом; "
               "без --with-tests тесты не исполняются, а если run_all не зовётся вовсе "
               "— агенты идут в обход общего прогона (покрытие обходится на уровне CI)",
    },
    {
        "key": "test_run_all.py",
        "pattern": r"\btest_run_all\.py\b",
        "why": "собственный тест-инвариант мета-агента: доказывает, что сведение "
               "run_all исправно (красное→красное); без него поломку сводки "
               "«зелено при красном агенте» никто не поймает",
    },
)


def check_ci_has_required_steps(agents_dir):
    """CI-воркфлоу обязан содержать КАЖДУЮ команду из REQUIRED_WORKFLOW_COMMANDS.

    Обобщение прежних точечных проверок «CI зовёт run_all.py --with-tests» и «CI
    зовёт test_run_all.py»: вместо отдельной функции на каждую команду держим
    ОДИН список обязательных команд воркфлоу и краснеем при пропаже любой. Так
    новый обязательный шаг CI нельзя забыть — достаточно дописать строку в
    список, не размножая почти одинаковый код проверок.

    Воркфлоу ищем от КОРНЯ репозитория (родитель каталога агентов). Его отсутствие
    здесь — нарушение (обязательные шаги CI некому прогонять), в отличие от
    отсутствия самого run_all.py в run-all-covers-all (там это громко валит другие
    шаги CI само)."""
    repo_root = os.path.dirname(os.path.abspath(agents_dir.rstrip("/")))
    wf_path = os.path.join(repo_root, CI_WORKFLOW_REL)
    if not os.path.isfile(wf_path):
        return [{
            "item": CI_WORKFLOW_REL,
            "problem": "CI-воркфлоу не найден — обязательные шаги CI некому прогонять (покрытие обходится на уровне CI)",
        }]
    try:
        with open(wf_path, "r", encoding="utf-8") as fh:
            lines = fh.read().splitlines()
    except OSError as exc:
        return [{"item": CI_WORKFLOW_REL, "problem": "не удалось прочитать файл: {}".format(exc)}]

    violations = []
    for cmd in REQUIRED_WORKFLOW_COMMANDS:
        if not any(re.search(cmd["pattern"], ln) for ln in lines):
            violations.append({
                "item": cmd["key"],
                "problem": "обязательная команда CI отсутствует в воркфлоу ({})".format(cmd["why"]),
            })
    return violations


def _workflow_run_steps_named(text):
    """Возвращает шаги `run:` воркфлоу как пары (name, body) в порядке появления.

    body — значение ключа `run:`: либо инлайн (`run: cmd` / `- run: cmd`), либо
    блочный скаляр (`run: |` с последующими строками глубже отступа ключа). name —
    значение ключа `name:` ТОГО ЖЕ шага списка (или None, если у шага нет имени).
    Берём ИМЕННО тела команд, а не весь файл: команда, упомянутая лишь в
    комментарии или в названии шага (`- name: ... run_all ...`), в body не попадёт —
    значит она не запускается, и страж это заметит. Имя же нужно отдельной мягкой
    проверке, чтобы провал шага читался в логах по-человечески. Разбор текстовый,
    без сторонних зависимостей (достаточно для блочного YAML наших воркфлоу)."""
    lines = text.splitlines()
    steps = []
    i = 0
    n = len(lines)
    pending_name = None
    while i < n:
        line = lines[i]
        item = re.match(r"^(\s*)-\s+(.*)$", line)
        if item:
            # Новый элемент списка — забываем имя предыдущего шага и нормализуем
            # содержимое `- key: value` так, будто ключ стоит на своей колонке.
            pending_name = None
            content_line = " " * (len(item.group(1)) + 2) + item.group(2)
        else:
            content_line = line

        nm = re.match(r"^\s*name:\s*(.*)$", content_line)
        if nm:
            pending_name = nm.group(1).strip().strip('"').strip("'") or None
            i += 1
            continue

        rm = re.match(r"^(\s*)run:\s*(.*)$", content_line)
        if not rm:
            i += 1
            continue
        indent = len(rm.group(1))
        rest = rm.group(2)
        if rest and not rest.startswith(("|", ">")):
            # Инлайн-команда в той же строке.
            steps.append((pending_name, rest))
            i += 1
            continue
        # Блочный скаляр: собираем последующие строки глубже отступа ключа.
        body = []
        i += 1
        while i < n:
            l = lines[i]
            if l.strip() == "":
                body.append("")
                i += 1
                continue
            if len(l) - len(l.lstrip()) <= indent:
                break
            body.append(l)
            i += 1
        steps.append((pending_name, "\n".join(body)))
    return steps


def _workflow_run_steps(text):
    """Тела всех шагов `run:` воркфлоу (в порядке появления). Тонкая обёртка над
    `_workflow_run_steps_named`, когда имя шага неважно."""
    return [body for _name, body in _workflow_run_steps_named(text)]


def _workflow_step_items(text):
    """Элементы списка `- ...` воркфлоу как пары (keys, name).

    keys — множество имён ключей ВЕРХНЕГО уровня элемента (`name`, `run`, `uses`,
    `with`, …), включая ключ в самой строке `- key: value`; name — значение ключа
    `name:` (или None). Считаем только ключи на «колонке шага» (отступ `-` плюс 2),
    чтобы вложенные ключи (например, параметры под `with:`) не путались с `run`/
    `uses` самого шага. Бесключевые элементы списка (`- "ai-agents/**"` в `paths:`)
    дают пустой keys и сюда не мешают. Текстовый разбор по отступам, без сторонних
    зависимостей — достаточно для блочного YAML наших воркфлоу."""
    lines = text.splitlines()
    n = len(lines)
    items = []
    i = 0
    while i < n:
        m = re.match(r"^(\s*)-\s+(\S.*)$", lines[i])
        if not m:
            i += 1
            continue
        item_indent = len(m.group(1))
        key_col = item_indent + 2
        # Сегменты ключей шага: первый — на самой строке `- key: …`, остальные —
        # последующие строки ровно на колонке шага (глубже — это вложенность).
        segments = [m.group(2)]
        i += 1
        while i < n:
            l = lines[i]
            stripped = l.strip()
            if stripped == "" or stripped.startswith("#"):
                i += 1
                continue
            indent = len(l) - len(l.lstrip())
            if indent <= item_indent:
                break
            if indent == key_col:
                segments.append(stripped)
            i += 1
        keys = set()
        name = None
        for seg in segments:
            km = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", seg)
            if not km:
                continue
            keys.add(km.group(1))
            if km.group(1) == "name" and name is None:
                name = km.group(2).strip().strip('"').strip("'") or None
        items.append((keys, name))
    return items


def check_ci_required_cmd_own_step(agents_dir):
    """Каждая обязательная команда CI запускается СВОИМ отдельным шагом `run:`.

    ci-has-required-steps подтверждает, что команда ЕСТЬ где-то в файле — но «где
    угодно» включает комментарии и названия шагов, а две команды могли бы делить
    один шаг. Тогда провал одной маскирует другую: в одном `run:` с `&&` вторая
    не исполнится после падения первой, а команда, оставшаяся лишь в комментарии,
    не исполняется вовсе. Эта проверка смотрит САМИ тела шагов `run:` и требует,
    чтобы каждая обязательная команда (а) реально запускалась хотя бы одним шагом
    run: и (б) не делила шаг с другой обязательной командой — у каждой свой шаг,
    свой код возврата, свой провал на виду."""
    repo_root = os.path.dirname(os.path.abspath(agents_dir.rstrip("/")))
    wf_path = os.path.join(repo_root, CI_WORKFLOW_REL)
    if not os.path.isfile(wf_path):
        return [{
            "item": CI_WORKFLOW_REL,
            "problem": "CI-воркфлоу не найден — обязательным командам негде иметь свой шаг run:",
        }]
    try:
        with open(wf_path, "r", encoding="utf-8") as fh:
            text = fh.read()
    except OSError as exc:
        return [{"item": CI_WORKFLOW_REL, "problem": "не удалось прочитать файл: {}".format(exc)}]

    steps = _workflow_run_steps(text)
    # Для каждого шага run: — какие обязательные команды он запускает.
    matched_per_step = [
        [cmd["key"] for cmd in REQUIRED_WORKFLOW_COMMANDS if re.search(cmd["pattern"], body)]
        for body in steps
    ]
    violations = []
    # (а) каждая обязательная команда запускается хотя бы одним шагом run:.
    for cmd in REQUIRED_WORKFLOW_COMMANDS:
        if not any(cmd["key"] in keys for keys in matched_per_step):
            violations.append({
                "item": cmd["key"],
                "problem": "не запускается ни одним шагом run: (есть лишь в комментарии/названии шага или отсутствует — провал не будет замечен)",
            })
    # (б) ни один шаг run: не делит две и более обязательных команды.
    seen = set()
    for keys in matched_per_step:
        if len(keys) >= 2:
            shared = " + ".join(keys)
            if shared not in seen:
                seen.add(shared)
                violations.append({
                    "item": shared,
                    "problem": "обязательные команды делят один шаг run: — провал одной маскирует другую (дай каждой свой шаг)",
                })
    return violations


def check_ci_step_has_name(agents_dir):
    """МЯГКАЯ проверка: у шага run: обязательной команды CI есть человеческое `- name:`.

    ci-required-cmd-own-step уже требует, чтобы каждая обязательная команда шла
    своим шагом run:. Эта проверка идёт на шаг дальше и заботится о ЧИТАЕМОСТИ
    логов: если у такого шага нет `- name:`, в интерфейсе GitHub Actions упавший
    шаг показывается голой командой (`python3 ai-agents/run_all.py --with-tests`),
    а не по-человечески («Прогнать всех агентов»). Для людей, ради которых
    строится фонд (ст. 3 «понятность»), осмысленное имя шага важно.

    Это мягкая проверка (severity=soft): её нарушение НЕ валит CI — отсутствие
    имени не ломает покрытие, лишь ухудшает читаемость. Поэтому она лишь
    предупреждает, не краснит вердикт. Отсутствие самого воркфлоу здесь молчим:
    об этом громко рапортуют обязательные (hard) проверки выше."""
    repo_root = os.path.dirname(os.path.abspath(agents_dir.rstrip("/")))
    wf_path = os.path.join(repo_root, CI_WORKFLOW_REL)
    if not os.path.isfile(wf_path):
        return []
    try:
        with open(wf_path, "r", encoding="utf-8") as fh:
            text = fh.read()
    except OSError:
        return []

    steps = _workflow_run_steps_named(text)
    violations = []
    for cmd in REQUIRED_WORKFLOW_COMMANDS:
        for name, body in steps:
            if re.search(cmd["pattern"], body):
                if not name:
                    violations.append({
                        "item": cmd["key"],
                        "problem": "шаг run: без '- name:' — в логах GitHub Actions провал читается голой командой, а не по-человечески (дай шагу осмысленное имя)",
                    })
                break  # имя проверяем у первого шага, который запускает команду
    return violations


def check_ci_step_name_unique(agents_dir):
    """МЯГКАЯ проверка: два шага run: CI не делят одинаковое `- name:`.

    Развитие ci-step-has-name: имя у шага уже есть (#7), но если ДВА шага run:
    носят ОДНО И ТО ЖЕ имя, в интерфейсе GitHub Actions их не различить — упавший
    шаг читается двусмысленно («какой именно „Прогон агентов“ из двух?»). Эта
    проверка собирает имена всех шагов run: и предупреждает о любом, которое
    встречается дважды и более. Безымянные шаги пропускаем — о них заботится
    ci-step-has-name.

    Это мягкая проверка (severity=soft): её нарушение НЕ валит CI — повтор имени
    не ломает покрытие, лишь ухудшает читаемость логов. Отсутствие самого
    воркфлоу здесь молчим: об этом громко рапортуют обязательные проверки выше."""
    repo_root = os.path.dirname(os.path.abspath(agents_dir.rstrip("/")))
    wf_path = os.path.join(repo_root, CI_WORKFLOW_REL)
    if not os.path.isfile(wf_path):
        return []
    try:
        with open(wf_path, "r", encoding="utf-8") as fh:
            text = fh.read()
    except OSError:
        return []

    steps = _workflow_run_steps_named(text)
    order = []
    counts = {}
    for name, _body in steps:
        if not name:
            continue
        if name not in counts:
            order.append(name)
        counts[name] = counts.get(name, 0) + 1
    violations = []
    for name in order:  # порядок первого появления — детерминированно
        if counts[name] > 1:
            violations.append({
                "item": name,
                "problem": "это имя делят {} шага run: — в логах GitHub Actions их не различить (дай каждому шагу уникальное имя)".format(counts[name]),
            })
    return violations


def check_ci_step_has_body(agents_dir):
    """МЯГКАЯ проверка: у шага с `- name:` есть тело `run:`/`uses:` (не пустой шаг).

    Развитие ci-step-name-unique в сторону ЧЕСТНОСТИ карты шагов CI. Если в списке
    шагов встречается элемент с `- name:`, но БЕЗ `run:` и без `uses:`, это почти
    всегда опечатка отступа: тело шага случайно «выпало» из него (тело стало
    дочерним к предыдущему шагу или ушло на уровень выше). Такой шаг ничего не
    делает, но в интерфейсе GitHub Actions выглядит настоящим — человек думает,
    что команда запускается, а её нет, и зелёная сборка обманчиво «покрывает» шаг.

    Это мягкая проверка (severity=soft): её нарушение НЕ валит CI — за реальный
    пропуск обязательной команды краснеют hard-проверки выше (ci-required-cmd-own-step
    заметит, что команда не запускается ни одним шагом run:). Эта лишь
    предупреждает, что карта шагов перестала быть честной, ради читаемости для
    людей (ст. 3 «понятность»). Отсутствие самого воркфлоу здесь молчим: о нём
    громко рапортуют обязательные проверки выше."""
    repo_root = os.path.dirname(os.path.abspath(agents_dir.rstrip("/")))
    wf_path = os.path.join(repo_root, CI_WORKFLOW_REL)
    if not os.path.isfile(wf_path):
        return []
    try:
        with open(wf_path, "r", encoding="utf-8") as fh:
            text = fh.read()
    except OSError:
        return []

    violations = []
    for keys, name in _workflow_step_items(text):
        if "name" in keys and "run" not in keys and "uses" not in keys:
            violations.append({
                "item": name or "(без имени)",
                "problem": "шаг с '- name:' без 'run:'/'uses:' — пустой шаг (вероятно опечатка отступа: тело выпало из шага и команда не запускается)",
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
    {
        "key": "trigger-paths-include-agents",
        "title": "Триггер-пути воркфлоу включают ai-agents/**",
        "guards": "ст. 3 — покрытие нельзя обойти и на уровне триггера: правка агента запускает CI",
        "fn": check_trigger_paths_include_agents,
    },
    {
        "key": "ci-has-required-steps",
        "title": "CI-воркфлоу содержит все обязательные шаги (единый список команд)",
        "guards": "ст. 3 — обязательный шаг CI нельзя забыть: один список команд вместо россыпи почти одинаковых проверок",
        "fn": check_ci_has_required_steps,
    },
    {
        "key": "ci-required-cmd-own-step",
        "title": "Каждой обязательной команде CI — свой шаг run:",
        "guards": "ст. 3 — провал одной обязательной команды не маскирует другую: у каждой свой шаг и свой код возврата",
        "fn": check_ci_required_cmd_own_step,
    },
    {
        "key": "ci-step-has-name",
        "title": "У шага run: обязательной команды CI есть человеческое имя",
        "guards": "ст. 3 — провал шага в логах GitHub Actions читается по-человечески, а не голой командой",
        "fn": check_ci_step_has_name,
        "severity": "soft",  # мягкая: предупреждает, не валит CI
    },
    {
        "key": "ci-step-name-unique",
        "title": "Шаги run: CI не делят одинаковое имя",
        "guards": "ст. 3 — упавший шаг в логах GitHub Actions читается однозначно: у каждого своё имя",
        "fn": check_ci_step_name_unique,
        "severity": "soft",  # мягкая: предупреждает, не валит CI
    },
    {
        "key": "ci-step-has-body",
        "title": "Шаг с именем не пустой (есть тело run:/uses:)",
        "guards": "ст. 3 — карта шагов CI честна: именованный шаг реально что-то делает, а не выглядит настоящим из-за опечатки отступа",
        "fn": check_ci_step_has_body,
        "severity": "soft",  # мягкая: предупреждает, не валит CI
    },
)


def run(agents_dir=AGENTS_DIR):
    """Прогоняет все структурные проверки каталога ai-agents/. Возвращает report dict."""
    checks = []
    for spec in CHECKS:
        soft = spec.get("severity") == "soft"
        try:
            violations = spec["fn"](agents_dir)
            # Мягкая проверка при нарушении лишь ПРЕДУПРЕЖДАЕТ (warn), не валит CI;
            # обязательная (по умолчанию) — краснит (fail).
            status = "pass" if not violations else ("warn" if soft else "fail")
        except OSError as exc:
            violations = [{"item": "-", "problem": "ошибка чтения каталога: {}".format(exc)}]
            status = "error"
        checks.append({
            "key": spec["key"],
            "title": spec["title"],
            "guards": spec["guards"],
            "severity": "soft" if soft else "hard",
            "status": status,
            "violations": violations,
        })

    # Вердикт краснеет только от обязательных нарушений; warn мягкой проверки —
    # предупреждение, оно не валит сборку (и не ломает согласованность с кодом возврата).
    hard_fail = any(c["status"] in ("fail", "error") for c in checks)
    passed = sum(1 for c in checks if c["status"] == "pass")
    warnings = sum(1 for c in checks if c["status"] == "warn")
    return {
        "agent": "structure_guard",
        "role": "служебный модуль, не орган власти (Конституция, ст. 9)",
        "verdict": "red" if hard_fail else "green",
        "passed": passed,
        "warnings": warnings,
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
        mark = {"pass": "✓", "fail": "✗", "warn": "⚠", "error": "‼"}[c["status"]]
        soft = " (мягкая)" if c.get("severity") == "soft" else ""
        print("\n{} [{}]{} {}".format(mark, c["key"], soft, c["title"]))
        print("    защищает: {}".format(c["guards"]))
        for v in c["violations"]:
            print("    | {}: {}".format(v["item"], v["problem"]))
    print("\n" + "-" * 70)
    verdict = "ЗЕЛЁНО ✓" if all_pass else "КРАСНО ✗"
    tail = ""
    if report.get("warnings"):
        tail = ", предупреждений: {}".format(report["warnings"])
    print("ИТОГ: {}  ({}/{} проверок прошли{})".format(verdict, report["passed"], report["total"], tail))
    print("-" * 70)
    if not all_pass:
        print("Страж нашёл нарушение стандарта качества. Это сигнал сообществу,")
        print("а не действие: модуль не исправляет и ничем не распоряжается.")
    elif report.get("warnings"):
        print("Есть мягкие предупреждения (не валят сборку): см. ⚠ выше. Это")
        print("подсказка к улучшению читаемости, а не нарушение стандарта.")
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
