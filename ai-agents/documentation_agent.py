#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Documentation AI-агент — Public Trust DAO (Этап 6, модуль 6/8).

СЛУЖЕБНЫЙ МОДУЛЬ, НЕ ОРГАН ВЛАСТИ (Конституция, ст. 9).
Агент НИЧЕГО не двигает и ничем не владеет: он только ПРОВЕРЯЕТ целостность
документации и докладывает «зелёно/красно». Вся власть — у голосования сообщества
и Safe-мультисига; ИИ лишь помогает соблюдать конституцию (ст. 9).

Зачем: указание оператора — вся документация ведётся ПАРАЛЛЕЛЬНО на русском И
английском (RU↔EN), а проект обязан быть ПРОВЕРЯЕМ (ст. 3) и ОТКРЫТ/ПОНЯТЕН
(ст. 6). Этот агент превращает оба правила в машинную проверку, чтобы документы
не разъезжались молча: чтобы у каждого публичного RU-дока было EN-зеркало (и
наоборот), чтобы переключатель языка был на месте, и чтобы ни одна относительная
ссылка не вела «в никуда».

Что делает (read-only, по git-отслеживаемым .md — по тому, что реально
опубликовано):

  • bilingual-pairs   → у каждого публичного дока есть пара RU↔EN ........... ст. 6
  • language-switcher → вверху дока корректный переключатель [RU]·[EN] ...... ст. 6
  • link-integrity    → все относительные ссылки в .md ведут к чему-то ...... ст. 3

Правило пар (выводится из пути, а не зашито пофайлово):
  docs/NAME.md            ↔ docs/en/NAME.md
  <dir>/README.md         ↔ <dir>/README.en.md  (и корневой README.md ↔ README.en.md)
  NAME.md (в корне)       ↔ NAME.en.md           (напр. REPO-STRUCTURE, AUTHORS)
Внутренние/служебные файлы (мандат строителя, переписка с оператором, журналы
прогресса) одноязычны by design и в правило двуязычности НЕ входят — их список
явный (SINGLE_LANG ниже), чтобы агент не падал ложно.

Вывод:
  • человекочитаемый отчёт в stdout (✓/✗ по каждой проверке + привязка к статье);
  • при --json — машиночитаемый отчёт (для CI и других агентов);
  • код возврата 0, если все проверки прошли, иначе 1.

«Красный» — это СИГНАЛ сообществу (повод для решения людей), а не действие: агент
сам ничего не исправляет (не дописывает переводы и не правит ссылки).

Зависимостей нет — только стандартная библиотека (детерминированно в любом CI).
TESTNET-ONLY: агент не трогает реальные средства/ключи и не выходит в сеть.
"""

import argparse
import json
import os
import re
import subprocess
import sys

# Корень репозитория = на уровень выше каталога ai-agents/.
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Одноязычные by design (НЕ требуют EN-зеркала и переключателя): внутренний
# мандат строителя, план, журналы памяти, переписка с оператором. Это рабочая
# кухня контура, а не публичная документация фонда. Сюда же — GitHub-формы
# (шаблон PR): это служебный конфиг платформы с единым файлом, двуязычный ВНУТРИ
# себя (RU+EN в одном теле), а не пара RU↔EN-документов. (Шаблоны issue — .yml,
# в скан .md не попадают вовсе.)
SINGLE_LANG = {
    "BUILDER.md",
    "LAUNCH.md",
    "PROGRESS.md",
    "DECISIONS.md",
    "comms/INBOX.md",
    "comms/operator-thread.md",
    ".github/pull_request_template.md",
}

# Переключатель языка вверху публичного дока. Текущий язык — простой текст в
# скобках, другой — ссылка на парный файл.
SWITCHER_RU_RE = re.compile(r"^\[Русский\]\s*·\s*\[English\]\(([^)]+)\)\s*$")
SWITCHER_EN_RE = re.compile(r"^\[Русский\]\(([^)]+)\)\s*·\s*\[English\]\s*$")

# Ссылки вида [текст](цель). Цель берём «как есть» — потом отфильтруем внешние.
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
# Внешние/неотносительные цели (их целостность не наша забота).
EXTERNAL_PREFIXES = ("http://", "https://", "mailto:", "//", "#")
# Огороженные блоки кода ```...``` вырезаем перед извлечением ссылок — там
# может быть `](` внутри примеров, не являющийся ссылкой.
FENCE_RE = re.compile(r"```.*?```", re.DOTALL)


def git_tracked_md(root):
    """Возвращает отсортированный список git-отслеживаемых .md (относительные пути)."""
    try:
        out = subprocess.run(
            ["git", "-C", root, "ls-files", "*.md"],
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, check=True,
        ).stdout
        files = [line.strip() for line in out.splitlines() if line.strip()]
        if files:
            return sorted(files)
    except (OSError, subprocess.CalledProcessError):
        pass
    # Фолбэк (например, тест без git): обход дерева.
    files = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in (".git", "node_modules")]
        for name in filenames:
            if name.endswith(".md"):
                rel = os.path.relpath(os.path.join(dirpath, name), root)
                files.append(rel.replace(os.sep, "/"))
    return sorted(files)


def is_en_mirror(path):
    """EN-зеркало — это docs/en/** или файл, оканчивающийся на .en.md."""
    return path.startswith("docs/en/") or path.endswith(".en.md")


def expected_en_for_ru(path):
    """По RU-оригиналу вычисляет ожидаемый путь EN-зеркала (правило пар)."""
    if path.startswith("docs/") and not path.startswith("docs/en/"):
        return "docs/en/" + path[len("docs/"):]
    # Везде ещё: NAME.md → NAME.en.md (README.md→README.en.md и т.п.).
    return path[:-len(".md")] + ".en.md"


def expected_ru_for_en(path):
    """По EN-зеркалу вычисляет ожидаемый путь RU-оригинала (обратное правило)."""
    if path.startswith("docs/en/"):
        return "docs/" + path[len("docs/en/"):]
    return path[:-len(".en.md")] + ".md"


def partner_of(path):
    """Возвращает ожидаемый путь парного файла (RU↔EN) для публичного дока."""
    if is_en_mirror(path):
        return expected_ru_for_en(path)
    return expected_en_for_ru(path)


def read_text(root, rel):
    with open(os.path.join(root, rel), encoding="utf-8") as fh:
        return fh.read()


def first_nonempty_line(text):
    for line in text.splitlines():
        if line.strip():
            return line.rstrip()
    return ""


def extract_links(text):
    """Все цели относительных ссылок из markdown (вне блоков кода)."""
    cleaned = FENCE_RE.sub("", text)
    out = []
    for target in LINK_RE.findall(cleaned):
        target = target.strip()
        # Markdown допускает заголовок ссылки: [t](url "title") — отрезаем.
        if " " in target:
            target = target.split(" ", 1)[0]
        out.append(target)
    return out


def is_external(target):
    return target.startswith(EXTERNAL_PREFIXES) or target.startswith("<")


def resolve_link(root, src_rel, target):
    """Резолвит относительную ссылку src→target. Возвращает (ok, resolved_rel)."""
    # Якорь и query отрезаем — проверяем существование самого файла/каталога.
    path = target.split("#", 1)[0].split("?", 1)[0]
    if not path:
        return True, None  # чистый якорь внутри того же файла
    base = os.path.dirname(src_rel)
    joined = os.path.normpath(os.path.join(base, path))
    if joined.startswith(".."):
        return False, joined  # ведёт за пределы репозитория
    full = os.path.join(root, joined)
    return os.path.exists(full), joined


# ---- Проверки. Каждая возвращает (status, violations[list]). ----

def check_bilingual_pairs(root, public_docs, existing):
    """У каждого публичного дока есть существующая пара RU↔EN."""
    violations = []
    for doc in public_docs:
        partner = partner_of(doc)
        if partner not in existing:
            side = "EN-зеркало" if not is_en_mirror(doc) else "RU-оригинал"
            violations.append({
                "record": doc,
                "problem": f"нет парного файла ({side}): ожидался '{partner}'",
            })
    return ("pass" if not violations else "fail"), violations


def check_language_switcher(root, public_docs, existing):
    """Вверху публичного дока — корректный переключатель, ведущий к парному файлу."""
    violations = []
    for doc in public_docs:
        partner = partner_of(doc)
        head = first_nonempty_line(read_text(root, doc))
        rx = SWITCHER_EN_RE if is_en_mirror(doc) else SWITCHER_RU_RE
        m = rx.match(head)
        if not m:
            violations.append({
                "record": doc,
                "problem": f"первая строка не переключатель языка: {head!r}",
            })
            continue
        # Ссылка в переключателе должна резолвиться в парный файл.
        link = m.group(1).strip()
        ok, resolved = resolve_link(root, doc, link)
        if not ok:
            violations.append({"record": doc,
                               "problem": f"ссылка переключателя ведёт в никуда: {link!r}"})
        elif resolved != partner:
            violations.append({
                "record": doc,
                "problem": f"переключатель ведёт на '{resolved}', а пара — '{partner}'",
            })
    return ("pass" if not violations else "fail"), violations


def check_link_integrity(root, all_docs):
    """Каждая относительная ссылка в каждом .md ведёт к существующему файлу/каталогу."""
    violations = []
    for doc in all_docs:
        text = read_text(root, doc)
        for target in extract_links(text):
            if is_external(target):
                continue
            ok, resolved = resolve_link(root, doc, target)
            if not ok:
                violations.append({
                    "record": doc,
                    "problem": f"битая относительная ссылка → {target!r} (→ {resolved})",
                })
    return ("pass" if not violations else "fail"), violations


CHECKS = [
    {
        "key": "bilingual-pairs",
        "title": "У каждого публичного дока есть пара RU↔EN",
        "guards": "ст. 6 — открытость/понятность; указание оператора «вся документация двуязычна»",
        "fn": "pairs",
    },
    {
        "key": "language-switcher",
        "title": "Вверху дока корректный переключатель языка [Русский]·[English]",
        "guards": "ст. 6 — доступность на обоих языках; переключатель ведёт к парному файлу",
        "fn": "switcher",
    },
    {
        "key": "link-integrity",
        "title": "Все относительные ссылки в документации ведут к существующему файлу",
        "guards": "ст. 3 — проверяемость; документ без битых ссылок реально читаем и проверяем",
        "fn": "links",
    },
]


def run(root):
    """Прогоняет все проверки. Возвращает report dict."""
    all_md = git_tracked_md(root)
    existing = set(all_md)
    # Публичные двуязычные доки = всё .md, кроме явно одноязычных служебных.
    public_docs = [p for p in all_md if p not in SINGLE_LANG]

    pairs_status, pairs_v = check_bilingual_pairs(root, public_docs, existing)
    switch_status, switch_v = check_language_switcher(root, public_docs, existing)
    links_status, links_v = check_link_integrity(root, all_md)

    results = {
        "pairs": (pairs_status, pairs_v),
        "switcher": (switch_status, switch_v),
        "links": (links_status, links_v),
    }

    checks = []
    for spec in CHECKS:
        status, violations = results[spec["fn"]]
        checks.append({
            "key": spec["key"],
            "title": spec["title"],
            "guards": spec["guards"],
            "status": status,
            "violations": violations,
        })

    all_pass = all(c["status"] == "pass" for c in checks)
    passed = sum(1 for c in checks if c["status"] == "pass")
    return {
        "agent": "documentation",
        "role": "служебный модуль, не орган власти (Конституция, ст. 9)",
        "verdict": "green" if all_pass else "red",
        "passed": passed,
        "total": len(checks),
        "md_files_total": len(all_md),
        "public_docs_checked": len(public_docs),
        "single_lang_skipped": sorted(SINGLE_LANG & existing),
        "checks": checks,
    }


def main(argv):
    parser = argparse.ArgumentParser(
        description="Documentation AI-агент Public Trust DAO: двуязычность RU↔EN + целостность ссылок."
    )
    parser.add_argument(
        "--root", default=ROOT,
        help="корень репозитория (по умолчанию — на уровень выше ai-agents/).",
    )
    parser.add_argument(
        "--json", action="store_true",
        help="вывести машиночитаемый JSON-отчёт вместо человекочитаемого.",
    )
    args = parser.parse_args(argv[1:])

    report = run(args.root)
    all_pass = report["verdict"] == "green"

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0 if all_pass else 1

    print("=" * 70)
    print("DOCUMENTATION AI-АГЕНТ — Public Trust DAO")
    print("Служебный модуль (ст. 9): проверяет документацию, не правит. Ничего не двигает.")
    print("=" * 70)
    print(f"Всего .md (git-отслеживаемых): {report['md_files_total']}")
    print(f"Публичных доков проверено (двуязычность): {report['public_docs_checked']}")
    print(f"Одноязычных служебных пропущено: {len(report['single_lang_skipped'])}")
    for c in report["checks"]:
        mark = {"pass": "✓", "fail": "✗", "error": "⚠"}[c["status"]]
        print(f"\n{mark} [{c['key']}] {c['title']}")
        print(f"    защищает: {c['guards']}")
        for v in c["violations"]:
            print(f"    | {v['record']}: {v['problem']}")
    print("\n" + "-" * 70)
    verdict = "ЗЕЛЁНО ✓" if all_pass else "КРАСНО ✗"
    print(f"ИТОГ: {verdict}  ({report['passed']}/{report['total']} проверок прошли)")
    print("-" * 70)
    if not all_pass:
        print("Documentation нашёл расхождение в документации (нет пары / битый")
        print("переключатель / битая ссылка). Это сигнал сообществу, а не действие:")
        print("агент не дописывает переводы и не правит ссылки — это делают люди.")
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
