#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест-инвариант для Documentation-агента — Public Trust DAO.

Доказывает, что Documentation РАБОТАЕТ (а не «зелёный по умолчанию»): на КАЖДОЕ
расхождение документации (нет пары RU↔EN, нет/битый переключатель языка, битая
относительная ссылка) он обязан вернуть «красно» (exit=1), а на чистой
двуязычной документации — «зелёно» (exit=0), без ложных срабатываний (в т.ч.
служебные одноязычные файлы и внешние ссылки/код-блоки не должны его ронять).

Метод: строим временный «мини-репозиторий» из набора .md (без git — агент сам
переходит на обход дерева) и подсовываем то корректные, то «отравленные» версии;
запускаем агент через --root и проверяем вердикт по --json. Только стандартная
библиотека. Сети нет.
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
AGENT = os.path.join(HERE, "documentation_agent.py")

PASSED = 0
FAILED = 0

# Корректный минимальный двуязычный мини-репозиторий: README пара, docs пара,
# все относительные ссылки резолвятся, переключатели на месте и ведут к паре.
GOOD_FILES = {
    "README.md": (
        "[Русский] · [English](README.en.md)\n\n"
        "# Заголовок\n\nСм. [доки](docs/A.md).\n"
    ),
    "README.en.md": (
        "[Русский](README.md) · [English]\n\n"
        "# Title\n\nSee [docs](docs/en/A.md).\n"
    ),
    "docs/A.md": "[Русский] · [English](en/A.md)\n\n# A (RU)\n",
    "docs/en/A.md": "[Русский](../A.md) · [English]\n\n# A (EN)\n",
}


def check(name, cond):
    global PASSED, FAILED
    if cond:
        PASSED += 1
        print(f"  ✓ {name}")
    else:
        FAILED += 1
        print(f"  ✗ {name}")


def make_repo(tmp, files):
    """Создаёт мини-репо из словаря {относительный путь: содержимое}."""
    for rel, content in files.items():
        full = os.path.join(tmp, rel)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w", encoding="utf-8") as fh:
            fh.write(content)


def run_agent(tmp):
    proc = subprocess.run(
        [sys.executable, AGENT, "--root", tmp, "--json"],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
    )
    try:
        report = json.loads(proc.stdout)
    except ValueError:
        report = {"_raw": proc.stdout}
    return proc.returncode, report


def status_of(report, key):
    for c in report.get("checks", []):
        if c["key"] == key:
            return c["status"]
    return None


def scenario(title, files, expect_green, expect_fail_key=None):
    print(f"\n[{title}]")
    tmp = tempfile.mkdtemp(prefix="doc-test-")
    try:
        make_repo(tmp, files)
        code, report = run_agent(tmp)
        if expect_green:
            check("вердикт green / exit=0", report.get("verdict") == "green" and code == 0)
        else:
            check("вердикт red / exit=1", report.get("verdict") == "red" and code == 1)
            if expect_fail_key:
                check(f"провалена именно проверка '{expect_fail_key}'",
                      status_of(report, expect_fail_key) == "fail")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def without(key):
    f = dict(GOOD_FILES)
    f.pop(key)
    return f


def replace(key, content):
    f = dict(GOOD_FILES)
    f[key] = content
    return f


def add(rel, content):
    f = dict(GOOD_FILES)
    f[rel] = content
    return f


def main():
    print("ТЕСТ-ИНВАРИАНТ DOCUMENTATION — доказываем, что красное ловится, зелёное не ложно-падает")

    # 1. Корректная двуязычная документация → зелёно.
    scenario("корректный двуязычный репозиторий", dict(GOOD_FILES), expect_green=True)

    # 2. Нет EN-зеркала для docs/A.md → bilingual-pairs красный.
    scenario("нет docs/en/A.md (нет пары)", without("docs/en/A.md"),
             expect_green=False, expect_fail_key="bilingual-pairs")

    # 3. Нет RU-оригинала (есть только EN) → bilingual-pairs красный.
    scenario("нет README.md (только EN)", without("README.md"),
             expect_green=False, expect_fail_key="bilingual-pairs")

    # 4. Нет переключателя языка (первая строка — заголовок) → language-switcher красный.
    scenario("README.md без переключателя",
             replace("README.md", "# Заголовок\n\nСм. [доки](docs/A.md).\n"),
             expect_green=False, expect_fail_key="language-switcher")

    # 5. Переключатель ведёт не на парный файл → language-switcher красный.
    scenario("переключатель ведёт на чужой файл",
             replace("README.md",
                     "[Русский] · [English](docs/A.md)\n\n# Заголовок\n"),
             expect_green=False, expect_fail_key="language-switcher")

    # 6. EN-файл с RU-видом переключателя (перепутаны стороны) → language-switcher красный.
    scenario("EN-файл с переключателем RU-вида",
             replace("README.en.md",
                     "[Русский] · [English](README.md)\n\n# Title\n"),
             expect_green=False, expect_fail_key="language-switcher")

    # 7. Битая относительная ссылка в теле → link-integrity красный.
    scenario("битая относительная ссылка",
             replace("docs/A.md",
                     "[Русский] · [English](en/A.md)\n\n# A\n\n[нет](nope.md)\n"),
             expect_green=False, expect_fail_key="link-integrity")

    # 8. Внешние ссылки (http/mailto/#) и блок кода с `](` не должны ронять → зелёно.
    scenario("внешние ссылки и код-блок не ломают",
             replace("docs/A.md",
                     "[Русский] · [English](en/A.md)\n\n# A\n\n"
                     "[сайт](https://example.org) · [почта](mailto:a@b.co) · [якорь](#тут)\n\n"
                     "```\nпример: [текст](этого-файла-нет.md)\n```\n"),
             expect_green=True)

    # 9. Служебный одноязычный файл (PROGRESS.md) без пары → НЕ должен ронять (зелёно).
    scenario("служебный PROGRESS.md без пары игнорируется",
             add("PROGRESS.md", "# Прогресс\n\nвнутренний журнал, одноязычный by design\n"),
             expect_green=True)

    # 10. Зато НЕ-служебный одноязычный файл в корне без пары → bilingual-pairs красный.
    scenario("обычный GUIDE.md без пары ловится",
             add("GUIDE.md", "[Русский] · [English](GUIDE.en.md)\n\n# Гайд\n"),
             expect_green=False, expect_fail_key="bilingual-pairs")

    print(f"\nИТОГ: {PASSED} прошли, {FAILED} провалились")
    return 0 if FAILED == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
