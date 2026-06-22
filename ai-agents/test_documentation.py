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


def _is_soft(report, key):
    for c in report.get("checks", []):
        if c["key"] == key:
            return c.get("soft") is True
    return False


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

    # 11. Мягкая проверка глоссария: неполный глоссарий ПРЕДУПРЕЖДАЕТ, но НЕ роняет
    #     вердикт (это ключевое свойство soft-проверки).
    glossary_partial = dict(GOOD_FILES)
    glossary_partial["docs/GLOSSARY.md"] = (
        "[Русский] · [English](en/GLOSSARY.md)\n\n# Глоссарий\n\n"
        "**DAO (ДАО).**\nОпределение.\n"  # есть только один ключевой термин
    )
    glossary_partial["docs/en/GLOSSARY.md"] = (
        "[Русский](../GLOSSARY.md) · [English]\n\n# Glossary\n\n"
        "**DAO (decentralized autonomous organization).**\nDefinition.\n"
    )
    print("\n[мягкая проверка: неполный глоссарий предупреждает, но НЕ роняет вердикт]")
    tmp = tempfile.mkdtemp(prefix="doc-test-")
    try:
        make_repo(tmp, glossary_partial)
        code, report = run_agent(tmp)
        check("вердикт остаётся green / exit=0 (soft не блокирует)",
              report.get("verdict") == "green" and code == 0)
        check("glossary-coverage == warn при неполном глоссарии",
              status_of(report, "glossary-coverage") == "warn")
        check("счётчик предупреждений > 0", report.get("warnings", 0) > 0)
        check("проверка помечена soft", _is_soft(report, "glossary-coverage"))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # 12. Без глоссария вовсе — мягкая проверка молчит (pass), вердикт green.
    print("\n[мягкая проверка: без глоссария не предупреждает (нечего линтовать)]")
    tmp = tempfile.mkdtemp(prefix="doc-test-")
    try:
        make_repo(tmp, dict(GOOD_FILES))
        code, report = run_agent(tmp)
        check("glossary-coverage == pass без глоссария",
              status_of(report, "glossary-coverage") == "pass")
        check("предупреждений нет", report.get("warnings", 0) == 0)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # 13. Мягкая проверка «нет мёртвых статей»: статья глоссария, чей термин не
    #     встречается НИГДЕ в корпусе → ПРЕДУПРЕЖДАЕТ, но НЕ роняет вердикт.
    dead_article = dict(GOOD_FILES)
    dead_article["docs/GLOSSARY.md"] = (
        "[Русский] · [English](en/GLOSSARY.md)\n\n# Глоссарий\n\n"
        "**Квантовая запутанность (quantum entanglement).**\n"
        "Термин, которого нет ни в одном документе.\n"
    )
    dead_article["docs/en/GLOSSARY.md"] = (
        "[Русский](../GLOSSARY.md) · [English]\n\n# Glossary\n\n"
        "**Quantum entanglement.**\nA term used nowhere.\n"
    )
    print("\n[мягкая проверка: мёртвая статья глоссария предупреждает, но НЕ роняет вердикт]")
    tmp = tempfile.mkdtemp(prefix="doc-test-")
    try:
        make_repo(tmp, dead_article)
        code, report = run_agent(tmp)
        check("вердикт остаётся green / exit=0 (soft не блокирует)",
              report.get("verdict") == "green" and code == 0)
        check("glossary-no-dead == warn для мёртвой статьи",
              status_of(report, "glossary-no-dead") == "warn")
        check("счётчик предупреждений > 0", report.get("warnings", 0) > 0)
        check("проверка помечена soft", _is_soft(report, "glossary-no-dead"))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # 14. Живая статья (термин встречается в корпусе) → glossary-no-dead pass.
    #     «docs» есть в ссылках README → термин используется → не мёртвая.
    live_article = dict(GOOD_FILES)
    live_article["docs/GLOSSARY.md"] = (
        "[Русский] · [English](en/GLOSSARY.md)\n\n# Глоссарий\n\n"
        "**Документация (docs).**\nТо, что лежит в каталоге docs.\n"
    )
    live_article["docs/en/GLOSSARY.md"] = (
        "[Русский](../GLOSSARY.md) · [English]\n\n# Glossary\n\n"
        "**Documentation (docs).**\nWhat lives under docs.\n"
    )
    print("\n[мягкая проверка: живая статья (термин используется) не предупреждает]")
    tmp = tempfile.mkdtemp(prefix="doc-test-")
    try:
        make_repo(tmp, live_article)
        code, report = run_agent(tmp)
        check("glossary-no-dead == pass для живой статьи",
              status_of(report, "glossary-no-dead") == "pass")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # 15. Мягкая проверка якорей: ссылка на несуществующий раздел того же файла
    #     → anchor-integrity ПРЕДУПРЕЖДАЕТ, но НЕ роняет вердикт.
    broken_anchor = replace(
        "docs/A.md",
        "[Русский] · [English](en/A.md)\n\n# A (RU)\n\n"
        "См. [раздел](#нет-такого-раздела).\n",
    )
    print("\n[мягкая проверка: битый якорь #section предупреждает, но НЕ роняет вердикт]")
    tmp = tempfile.mkdtemp(prefix="doc-test-")
    try:
        make_repo(tmp, broken_anchor)
        code, report = run_agent(tmp)
        check("вердикт остаётся green / exit=0 (soft не блокирует)",
              report.get("verdict") == "green" and code == 0)
        check("anchor-integrity == warn для битого якоря",
              status_of(report, "anchor-integrity") == "warn")
        check("счётчик предупреждений > 0", report.get("warnings", 0) > 0)
        check("проверка помечена soft", _is_soft(report, "anchor-integrity"))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # 16. Верный якорь на заголовок того же файла → anchor-integrity pass.
    #     «# A (RU)» → слаг «a-ru» (нижний регистр, скобки вырезаны, пробел → дефис).
    good_anchor = replace(
        "docs/A.md",
        "[Русский] · [English](en/A.md)\n\n# A (RU)\n\n"
        "См. [раздел](#a-ru).\n",
    )
    print("\n[мягкая проверка: верный якорь #section не предупреждает]")
    tmp = tempfile.mkdtemp(prefix="doc-test-")
    try:
        make_repo(tmp, good_anchor)
        code, report = run_agent(tmp)
        check("anchor-integrity == pass для верного якоря",
              status_of(report, "anchor-integrity") == "pass")
        check("предупреждений нет", report.get("warnings", 0) == 0)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # 17. Кросс-файловый якорь FILE.md#section: верный ведёт к заголовку другого
    #     файла (pass), битый — предупреждает (warn). Битый ФАЙЛ при этом не наша
    #     забота (его ловит блокирующая link-integrity), а вот живой файл с мёртвым
    #     якорем ловим именно здесь.
    cross_ok = replace(
        "README.md",
        "[Русский] · [English](README.en.md)\n\n# Заголовок\n\n"
        "См. [раздел A](docs/A.md#a-ru).\n",
    )
    print("\n[мягкая проверка: кросс-файловый якорь FILE.md#section, верный → pass]")
    tmp = tempfile.mkdtemp(prefix="doc-test-")
    try:
        make_repo(tmp, cross_ok)
        code, report = run_agent(tmp)
        check("anchor-integrity == pass для верного кросс-файлового якоря",
              status_of(report, "anchor-integrity") == "pass")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    cross_bad = replace(
        "README.md",
        "[Русский] · [English](README.en.md)\n\n# Заголовок\n\n"
        "См. [раздел A](docs/A.md#такого-раздела-нет).\n",
    )
    print("\n[мягкая проверка: кросс-файловый якорь на мёртвый раздел → warn, вердикт green]")
    tmp = tempfile.mkdtemp(prefix="doc-test-")
    try:
        make_repo(tmp, cross_bad)
        code, report = run_agent(tmp)
        check("вердикт остаётся green (soft не блокирует)",
              report.get("verdict") == "green" and code == 0)
        check("anchor-integrity == warn для битого кросс-файлового якоря",
              status_of(report, "anchor-integrity") == "warn")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # 18. Повторяющиеся заголовки: как на GitHub, второй одинаковый слаг → «-1».
    #     Ссылка на «#раздел-1» должна быть валидной (второй «# Раздел»).
    dup_headings = replace(
        "docs/A.md",
        "[Русский] · [English](en/A.md)\n\n# Раздел\n\nтекст\n\n# Раздел\n\n"
        "См. [второй](#раздел-1) и [первый](#раздел).\n",
    )
    print("\n[мягкая проверка: повторяющиеся заголовки → якорь «-1» валиден (как у GitHub)]")
    tmp = tempfile.mkdtemp(prefix="doc-test-")
    try:
        make_repo(tmp, dup_headings)
        code, report = run_agent(tmp)
        check("anchor-integrity == pass (и #раздел, и #раздел-1 существуют)",
              status_of(report, "anchor-integrity") == "pass")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # --- Мягкая проверка constitutional-prohibitions (запрещённые обещания) ----
    # Логика: запрещённое ОБЕЩАНИЕ без отрицания рядом → warn (вердикт не падает);
    #         наши дисклеймеры/перечни запретов с отрицанием → pass, без тревоги.

    def prohib_repo(readme_body, en_body=None):
        """Мини-репо GOOD_FILES, но с подменённым телом README (RU и опц. EN)."""
        f = dict(GOOD_FILES)
        f["README.md"] = ("[Русский] · [English](README.en.md)\n\n# Заголовок\n\n"
                          + readme_body + "\n")
        if en_body is not None:
            f["README.en.md"] = ("[Русский](README.md) · [English]\n\n# Title\n\n"
                                 + en_body + "\n")
        return f

    # 19. Прямое обещание доходности в публичном тексте → warn, вердикт green.
    print("\n[мягкая проверка: обещание доходности без отрицания → warn, вердикт green]")
    tmp = tempfile.mkdtemp(prefix="doc-test-")
    try:
        make_repo(tmp, prohib_repo("Инвестируй и получи гарантированный доход 20% в месяц!"))
        code, report = run_agent(tmp)
        check("вердикт остаётся green / exit=0 (soft не блокирует)",
              report.get("verdict") == "green" and code == 0)
        check("constitutional-prohibitions == warn для обещания дохода",
              status_of(report, "constitutional-prohibitions") == "warn")
        check("счётчик предупреждений > 0", report.get("warnings", 0) > 0)
        check("проверка помечена soft", _is_soft(report, "constitutional-prohibitions"))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # 20. Плата за привлечение людей (реферал) на английском → warn.
    print("\n[мягкая проверка: referral-обещание (EN) → warn]")
    tmp = tempfile.mkdtemp(prefix="doc-test-")
    try:
        make_repo(tmp, prohib_repo("Текст.",
                                   en_body="Join our referral program and earn a bonus."))
        code, report = run_agent(tmp)
        check("constitutional-prohibitions == warn для referral",
              status_of(report, "constitutional-prohibitions") == "warn")
        check("вердикт остаётся green", report.get("verdict") == "green")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # 21. Наш дисклеймер «это НЕ инвестиция, НЕ пирамида» → отрицание рядом → pass.
    print("\n[мягкая проверка: дисклеймер «НЕ инвестиция/НЕ пирамида» → pass, без ложной тревоги]")
    tmp = tempfile.mkdtemp(prefix="doc-test-")
    try:
        make_repo(tmp, prohib_repo(
            "Это НЕ инвестиция и НЕ финансовая пирамида. Мы не обещаем доходность.",
            en_body="This is NOT an investment, NOT a pyramid. We do not promise returns."))
        code, report = run_agent(tmp)
        check("constitutional-prohibitions == pass для дисклеймера",
              status_of(report, "constitutional-prohibitions") == "pass")
        check("предупреждений нет", report.get("warnings", 0) == 0)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # 22. Перечень запретов «Запрещается: обещать доходность …» → запрет рядом → pass.
    print("\n[мягкая проверка: перечень запретов «Запрещается: …» → pass]")
    tmp = tempfile.mkdtemp(prefix="doc-test-")
    try:
        make_repo(tmp, prohib_repo(
            "Запрещается: обещать доходность, строить пирамиду, платить за "
            "привлечение людей (рефералы)."))
        code, report = run_agent(tmp)
        check("constitutional-prohibitions == pass для перечня запретов",
              status_of(report, "constitutional-prohibitions") == "pass")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # 23. Запрещённое обещание в витрине web/*.html (не только .md) → warn.
    print("\n[мягкая проверка: запрещённое обещание в web/*.html → warn]")
    tmp = tempfile.mkdtemp(prefix="doc-test-")
    try:
        files = dict(GOOD_FILES)
        files["web/index.html"] = (
            "<!doctype html><html><body>"
            "<p>Гарантированная прибыль каждый месяц — приведи друга!</p>"
            "</body></html>\n")
        make_repo(tmp, files)
        code, report = run_agent(tmp)
        check("constitutional-prohibitions == warn для web/*.html",
              status_of(report, "constitutional-prohibitions") == "warn")
        check("вердикт остаётся green", report.get("verdict") == "green")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print(f"\nИТОГ: {PASSED} прошли, {FAILED} провалились")
    return 0 if FAILED == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
