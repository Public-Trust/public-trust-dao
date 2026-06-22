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

    # 14b. Мягкая проверка симметрии глоссария: RU и EN разошлись по числу статей
    #      → glossary-symmetry ПРЕДУПРЕЖДАЕТ, но НЕ роняет вердикт.
    asym = dict(GOOD_FILES)
    asym["docs/GLOSSARY.md"] = (
        "[Русский] · [English](en/GLOSSARY.md)\n\n# Глоссарий\n\n"
        "**Документация (docs).**\nТо, что лежит в каталоге docs.\n\n"
        "**Реестр (registry).**\nЖурнал решений в каталоге governance.\n"  # 2 статьи
    )
    asym["docs/en/GLOSSARY.md"] = (
        "[Русский](../GLOSSARY.md) · [English]\n\n# Glossary\n\n"
        "**Documentation (docs).**\nWhat lives under docs.\n"  # 1 статья — забыли перенести
    )
    print("\n[мягкая проверка: RU/EN глоссарии разошлись по объёму → warn, вердикт green]")
    tmp = tempfile.mkdtemp(prefix="doc-test-")
    try:
        make_repo(tmp, asym)
        code, report = run_agent(tmp)
        check("вердикт остаётся green / exit=0 (soft не блокирует)",
              report.get("verdict") == "green" and code == 0)
        check("glossary-symmetry == warn при разном числе статей",
              status_of(report, "glossary-symmetry") == "warn")
        check("счётчик предупреждений > 0", report.get("warnings", 0) > 0)
        check("проверка помечена soft", _is_soft(report, "glossary-symmetry"))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # 14c. Симметричные глоссарии (равное число статей) → glossary-symmetry pass.
    sym = dict(GOOD_FILES)
    sym["docs/GLOSSARY.md"] = (
        "[Русский] · [English](en/GLOSSARY.md)\n\n# Глоссарий\n\n"
        "**Документация (docs).**\nТо, что лежит в каталоге docs.\n\n"
        "**Реестр (registry).**\nЖурнал решений в каталоге governance.\n"
    )
    sym["docs/en/GLOSSARY.md"] = (
        "[Русский](../GLOSSARY.md) · [English]\n\n# Glossary\n\n"
        "**Documentation (docs).**\nWhat lives under docs.\n\n"
        "**Registry.**\nThe decisions log under governance.\n"
    )
    print("\n[мягкая проверка: симметричные глоссарии (равно статей) не предупреждают]")
    tmp = tempfile.mkdtemp(prefix="doc-test-")
    try:
        make_repo(tmp, sym)
        code, report = run_agent(tmp)
        check("glossary-symmetry == pass для равного числа статей",
              status_of(report, "glossary-symmetry") == "pass")
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

    # --- Мягкие проверки «См. также» платформы (see-also-targets / -present) ----
    # Логика: карты RELATED/RELATED_ACTIONS в SeeAlso.tsx и тексты t.learn/t.screens
    # в lib/i18n.ts не должны разъезжаться молча — битый адрес или экран без
    # <SeeAlso/> ПРЕДУПРЕЖДАЮТ (warn), но вердикт не роняют (soft).

    # Корректный минимальный платформенный набор: карта ссылается только на адреса,
    # которые есть в i18n, и каждый экран-источник рисует <SeeAlso/>.
    PLATFORM_GOOD = {
        "platform/lib/i18n.ts": (
            "export const ru = {\n"
            "  screens: [\n"
            '    { title: "Заявка", href: "/apply/" },\n'
            '    { title: "Голос", href: "/voting/" },\n'
            "  ],\n"
            "  learn: [\n"
            '    { title: "Манифест", href: "/manifesto/" },\n'
            '    { title: "Как решаем", href: "/governance/" },\n'
            "  ],\n"
            "};\n"
        ),
        "platform/components/SeeAlso.tsx": (
            "const RELATED: Record<string, string[]> = {\n"
            '  "/manifesto/": ["/governance/"],\n'
            '  "/governance/": ["/manifesto/"],\n'
            "};\n"
            "const RELATED_ACTIONS: Record<string, string[]> = {\n"
            '  "/governance/": ["/voting/"],\n'
            "};\n"
            "export default function SeeAlso() { return null; }\n"
        ),
        "platform/app/manifesto/page.tsx": (
            "// зеркало docs/MANIFESTO.md\n"
            'export default function P() { return <SeeAlso slug="/manifesto/" />; }\n'
        ),
        "platform/app/governance/page.tsx": (
            "// зеркало docs/GOVERNANCE.md\n"
            'export default function P() { return <SeeAlso slug="/governance/" />; }\n'
        ),
    }

    def with_platform(extra):
        f = dict(GOOD_FILES)
        f.update(PLATFORM_GOOD)
        f.update(extra)
        return f

    # 24. Корректная платформа → обе проверки pass, вердикт green, без тревог.
    print("\n[мягкие проверки: корректная карта «См. также» → pass, без предупреждений]")
    tmp = tempfile.mkdtemp(prefix="doc-test-")
    try:
        make_repo(tmp, with_platform({}))
        code, report = run_agent(tmp)
        check("вердикт green / exit=0", report.get("verdict") == "green" and code == 0)
        check("see-also-targets == pass", status_of(report, "see-also-targets") == "pass")
        check("see-also-present == pass", status_of(report, "see-also-present") == "pass")
        check("предупреждений нет", report.get("warnings", 0) == 0)
        check("see-also-targets помечена soft", _is_soft(report, "see-also-targets"))
        check("see-also-present помечена soft", _is_soft(report, "see-also-present"))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # 25. Адрес в RELATED ведёт на экран, которого нет в t.learn → targets warn.
    print("\n[мягкая проверка: висячий адрес RELATED → see-also-targets warn, вердикт green]")
    tmp = tempfile.mkdtemp(prefix="doc-test-")
    try:
        broken = with_platform({
            "platform/components/SeeAlso.tsx": (
                "const RELATED: Record<string, string[]> = {\n"
                '  "/manifesto/": ["/nonexistent/"],\n'
                "};\n"
                "const RELATED_ACTIONS: Record<string, string[]> = {\n"
                "};\n"
                "export default function SeeAlso() { return null; }\n"
            ),
        })
        make_repo(tmp, broken)
        code, report = run_agent(tmp)
        check("вердикт остаётся green / exit=0 (soft не блокирует)",
              report.get("verdict") == "green" and code == 0)
        check("see-also-targets == warn для висячего адреса",
              status_of(report, "see-also-targets") == "warn")
        check("счётчик предупреждений > 0", report.get("warnings", 0) > 0)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # 26. Значение RELATED_ACTIONS не из t.screens → targets warn.
    print("\n[мягкая проверка: действие-ссылка не из t.screens → see-also-targets warn]")
    tmp = tempfile.mkdtemp(prefix="doc-test-")
    try:
        broken = with_platform({
            "platform/components/SeeAlso.tsx": (
                "const RELATED: Record<string, string[]> = {\n"
                '  "/manifesto/": ["/governance/"],\n'
                '  "/governance/": ["/manifesto/"],\n'
                "};\n"
                "const RELATED_ACTIONS: Record<string, string[]> = {\n"
                '  "/governance/": ["/manifesto/"],\n'  # /manifesto/ — объяснение, не рабочий экран
                "};\n"
                "export default function SeeAlso() { return null; }\n"
            ),
        })
        make_repo(tmp, broken)
        code, report = run_agent(tmp)
        check("вердикт остаётся green", report.get("verdict") == "green")
        check("see-also-targets == warn (адрес-действие не из t.screens)",
              status_of(report, "see-also-targets") == "warn")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # 27. Экран есть в карте, но его page.tsx не рисует <SeeAlso/> → present warn.
    print("\n[мягкая проверка: экран без <SeeAlso/> → see-also-present warn, вердикт green]")
    tmp = tempfile.mkdtemp(prefix="doc-test-")
    try:
        broken = with_platform({
            "platform/app/governance/page.tsx": (
                "export default function P() { return <main>без блока ссылок</main>; }\n"
            ),
        })
        make_repo(tmp, broken)
        code, report = run_agent(tmp)
        check("вердикт остаётся green / exit=0 (soft не блокирует)",
              report.get("verdict") == "green" and code == 0)
        check("see-also-present == warn для экрана без <SeeAlso/>",
              status_of(report, "see-also-present") == "warn")
        check("счётчик предупреждений > 0", report.get("warnings", 0) > 0)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # 28. Экран из карты вообще без файла page.tsx → present warn.
    print("\n[мягкая проверка: экран карты без файла страницы → see-also-present warn]")
    tmp = tempfile.mkdtemp(prefix="doc-test-")
    try:
        broken = dict(GOOD_FILES)
        broken.update(PLATFORM_GOOD)
        broken.pop("platform/app/governance/page.tsx")  # файла страницы нет
        make_repo(tmp, broken)
        code, report = run_agent(tmp)
        check("вердикт остаётся green", report.get("verdict") == "green")
        check("see-also-present == warn для отсутствующей страницы",
              status_of(report, "see-also-present") == "warn")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # 29. Без файлов платформы вовсе — обе проверки молчат (pass), вердикт green.
    print("\n[мягкие проверки: без платформы не предупреждают (нечего линтовать)]")
    tmp = tempfile.mkdtemp(prefix="doc-test-")
    try:
        make_repo(tmp, dict(GOOD_FILES))
        code, report = run_agent(tmp)
        check("see-also-targets == pass без платформы",
              status_of(report, "see-also-targets") == "pass")
        check("see-also-present == pass без платформы",
              status_of(report, "see-also-present") == "pass")
        check("mirror-doc-link == pass без платформы",
              status_of(report, "mirror-doc-link") == "pass")
        check("предупреждений нет", report.get("warnings", 0) == 0)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # --- Мягкая проверка mirror-doc-link: экран-зеркало ссылается на свой док ----
    # Логика: экраны-зеркала (manifesto/governance/…) пересказывают нормативный
    # документ из docs/. Если экран есть, но ссылки на первоисточник нет —
    # ПРЕДУПРЕЖДЕНИЕ (warn), вердикт не роняем (soft).

    # 30. Корректная платформа (страницы ссылаются на docs/) → mirror pass, soft.
    print("\n[мягкая проверка: экраны-зеркала ссылаются на docs/ → mirror-doc-link pass]")
    tmp = tempfile.mkdtemp(prefix="doc-test-")
    try:
        make_repo(tmp, with_platform({}))
        code, report = run_agent(tmp)
        check("mirror-doc-link == pass", status_of(report, "mirror-doc-link") == "pass")
        check("mirror-doc-link помечена soft", _is_soft(report, "mirror-doc-link"))
        check("вердикт green / exit=0", report.get("verdict") == "green" and code == 0)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # 31. У экрана-зеркала пропала ссылка на свой нормативный док → mirror warn.
    print("\n[мягкая проверка: зеркало без ссылки на docs/ → mirror-doc-link warn, вердикт green]")
    tmp = tempfile.mkdtemp(prefix="doc-test-")
    try:
        broken = with_platform({
            "platform/app/governance/page.tsx": (
                "// пересказ есть, а ссылки на первоисточник нет\n"
                'export default function P() { return <SeeAlso slug="/governance/" />; }\n'
            ),
        })
        make_repo(tmp, broken)
        code, report = run_agent(tmp)
        check("вердикт остаётся green / exit=0 (soft не блокирует)",
              report.get("verdict") == "green" and code == 0)
        check("mirror-doc-link == warn для зеркала без ссылки на docs/",
              status_of(report, "mirror-doc-link") == "warn")
        check("счётчик предупреждений > 0", report.get("warnings", 0) > 0)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # 32. Экрана-зеркала из карты вообще нет (страница не заведена) → mirror молчит.
    print("\n[мягкая проверка: отсутствующий экран-зеркало не вызывает ложную тревогу]")
    tmp = tempfile.mkdtemp(prefix="doc-test-")
    try:
        partial = dict(GOOD_FILES)
        partial.update(PLATFORM_GOOD)
        partial.pop("platform/app/governance/page.tsx")  # экран ещё не заведён
        make_repo(tmp, partial)
        code, report = run_agent(tmp)
        check("mirror-doc-link == pass (нет файла → нечего сверять)",
              status_of(report, "mirror-doc-link") == "pass")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # --- Мягкая проверка mirror-doc-coverage: t.learn ⊆ MIRROR_DOCS -------------
    # Логика (обратная к mirror-doc-link): набор экранов-зеркал задаёт витрина
    # t.learn в lib/i18n.ts. Если завели новый экран-объяснение (добавили в t.learn),
    # но в карту MIRROR_DOCS внести забыли — mirror-doc-link его молча пропустит.
    # mirror-doc-coverage это ловит ПРЕДУПРЕЖДЕНИЕМ (warn), вердикт не роняет (soft).

    # 32a. Корректная платформа (t.learn = manifesto/governance, оба в карте) → pass.
    print("\n[мягкая проверка: t.learn целиком в MIRROR_DOCS → mirror-doc-coverage pass]")
    tmp = tempfile.mkdtemp(prefix="doc-test-")
    try:
        make_repo(tmp, with_platform({}))
        code, report = run_agent(tmp)
        check("mirror-doc-coverage == pass",
              status_of(report, "mirror-doc-coverage") == "pass")
        check("mirror-doc-coverage помечена soft",
              _is_soft(report, "mirror-doc-coverage"))
        check("вердикт green / exit=0", report.get("verdict") == "green" and code == 0)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # 32b. В t.learn появился экран, которого нет в MIRROR_DOCS → coverage warn.
    print("\n[мягкая проверка: новый экран в t.learn без MIRROR_DOCS → mirror-doc-coverage warn, вердикт green]")
    tmp = tempfile.mkdtemp(prefix="doc-test-")
    try:
        broken = with_platform({
            "platform/lib/i18n.ts": (
                "export const ru = {\n"
                "  screens: [\n"
                '    { title: "Заявка", href: "/apply/" },\n'
                '    { title: "Голос", href: "/voting/" },\n'
                "  ],\n"
                "  learn: [\n"
                '    { title: "Манифест", href: "/manifesto/" },\n'
                '    { title: "Как решаем", href: "/governance/" },\n'
                '    { title: "Новое объяснение", href: "/newscreen/" },\n'  # не в MIRROR_DOCS
                "  ],\n"
                "};\n"
            ),
        })
        make_repo(tmp, broken)
        code, report = run_agent(tmp)
        check("вердикт остаётся green / exit=0 (soft не блокирует)",
              report.get("verdict") == "green" and code == 0)
        check("mirror-doc-coverage == warn для экрана вне MIRROR_DOCS",
              status_of(report, "mirror-doc-coverage") == "warn")
        check("счётчик предупреждений > 0", report.get("warnings", 0) > 0)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # 32c. Без файла i18n платформы — проверять нечего → pass, без тревог.
    print("\n[мягкая проверка: без lib/i18n.ts mirror-doc-coverage молчит (pass)]")
    tmp = tempfile.mkdtemp(prefix="doc-test-")
    try:
        make_repo(tmp, GOOD_FILES)  # платформы вообще нет
        code, report = run_agent(tmp)
        check("mirror-doc-coverage == pass (нет i18n → нечего сверять)",
              status_of(report, "mirror-doc-coverage") == "pass")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # --- Мягкая проверка see-also-symmetric: связь «См. также» взаимна ----------
    # Логика: если экран A ведёт на B в RELATED, человек ждёт обратный путь B→A.
    # Односторонняя связь ПРЕДУПРЕЖДАЕТ (warn), вердикт не роняет (soft). Несимметрия
    # допустима (хабы), поэтому только сигнал. Касается лишь RELATED (объяснение↔
    # объяснение); RELATED_ACTIONS односторонняя по смыслу и не проверяется.

    # 33. Симметричная карта RELATED → see-also-symmetric pass, soft, без тревог.
    print("\n[мягкая проверка: симметричная карта «См. также» → see-also-symmetric pass]")
    tmp = tempfile.mkdtemp(prefix="doc-test-")
    try:
        make_repo(tmp, with_platform({}))
        code, report = run_agent(tmp)
        check("see-also-symmetric == pass", status_of(report, "see-also-symmetric") == "pass")
        check("see-also-symmetric помечена soft", _is_soft(report, "see-also-symmetric"))
        check("вердикт green / exit=0", report.get("verdict") == "green" and code == 0)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # 34. Односторонняя связь A→B без B→A → see-also-symmetric warn, вердикт green.
    print("\n[мягкая проверка: односторонняя связь «См. также» → see-also-symmetric warn, вердикт green]")
    tmp = tempfile.mkdtemp(prefix="doc-test-")
    try:
        broken = with_platform({
            "platform/components/SeeAlso.tsx": (
                "const RELATED: Record<string, string[]> = {\n"
                '  "/manifesto/": ["/governance/"],\n'  # ведёт на governance
                '  "/governance/": [],\n'               # а обратно — нет
                "};\n"
                "const RELATED_ACTIONS: Record<string, string[]> = {\n"
                "};\n"
                "export default function SeeAlso() { return null; }\n"
            ),
        })
        make_repo(tmp, broken)
        code, report = run_agent(tmp)
        check("вердикт остаётся green / exit=0 (soft не блокирует)",
              report.get("verdict") == "green" and code == 0)
        check("see-also-symmetric == warn для односторонней связи",
              status_of(report, "see-also-symmetric") == "warn")
        check("счётчик предупреждений > 0", report.get("warnings", 0) > 0)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # 35. RELATED_ACTIONS односторонняя — это норма, симметрию не нарушает.
    print("\n[мягкая проверка: односторонняя RELATED_ACTIONS не считается несимметрией]")
    tmp = tempfile.mkdtemp(prefix="doc-test-")
    try:
        ok = with_platform({
            "platform/components/SeeAlso.tsx": (
                "const RELATED: Record<string, string[]> = {\n"
                '  "/manifesto/": ["/governance/"],\n'
                '  "/governance/": ["/manifesto/"],\n'   # RELATED симметрична
                "};\n"
                "const RELATED_ACTIONS: Record<string, string[]> = {\n"
                '  "/governance/": ["/voting/"],\n'      # действие односторонне — это норма
                "};\n"
                "export default function SeeAlso() { return null; }\n"
            ),
        })
        make_repo(tmp, ok)
        code, report = run_agent(tmp)
        check("see-also-symmetric == pass (действия не считаются)",
              status_of(report, "see-also-symmetric") == "pass")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # 36. Без файлов платформы — проверка молчит (pass), вердикт green.
    print("\n[мягкая проверка: без платформы see-also-symmetric не предупреждает]")
    tmp = tempfile.mkdtemp(prefix="doc-test-")
    try:
        make_repo(tmp, dict(GOOD_FILES))
        code, report = run_agent(tmp)
        check("see-also-symmetric == pass без платформы",
              status_of(report, "see-also-symmetric") == "pass")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print(f"\nИТОГ: {PASSED} прошли, {FAILED} провалились")
    return 0 if FAILED == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
