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
  • glossary-coverage → ключевые термины проекта описаны в глоссарии ........ ст. 3/6
    (МЯГКАЯ проверка: только предупреждает, не роняет вердикт — чтобы глоссарий
     не отставал от документов; PTD-0040)

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

# Глоссарий проекта (RU-оригинал и EN-зеркало). На нём держится мягкая проверка
# «термин определён»: правило понятного языка (PTD-0040, ст. 3/6) требует, чтобы
# непонятные технические слова были объяснены простыми словами именно здесь.
GLOSSARY_RU = "docs/GLOSSARY.md"
GLOSSARY_EN = "docs/en/GLOSSARY.md"

# Жирный заголовок статьи глоссария: строка, начинающаяся с **...** (термин).
BOLD_HEAD_RE = re.compile(r"^\*\*.+?\*\*", re.MULTILINE)

# Ключевые технические термины, которые проект ОБЯЗУЕТСЯ объяснять простым языком
# в глоссарии (ст. 3 «понятность», ст. 6 «объяснимость», правило PTD-0040). Для
# каждого — как он выглядит в статье глоссария на RU и на EN (подстрока в жирном
# заголовке, регистр игнорируется). Если статьи нет — мягкое предупреждение, чтобы
# глоссарий не отставал от документов. Список заведомо консервативный (только то,
# что реально встречается в нормативных документах) — расширяется по мере роста
# корпуса, отдельным решением.
KEY_TERMS = [
    {"id": "DAO", "ru": "dao", "en": "dao"},
    {"id": "escrow / целевой расход", "ru": "escrow", "en": "escrow"},
    {"id": "мультисиг (multisig)", "ru": "мультисиг", "en": "multisig"},
    {"id": "казна (treasury)", "ru": "казна", "en": "treasury"},
    {"id": "хранитель (guardian)", "ru": "хранитель", "en": "guardian"},
    {"id": "кворум (quorum)", "ru": "кворум", "en": "quorum"},
    {"id": "предложение (proposal)", "ru": "предложение", "en": "proposal"},
    {"id": "Snapshot", "ru": "snapshot", "en": "snapshot"},
    {"id": "Timelock", "ru": "timelock", "en": "timelock"},
    {"id": "Governor", "ru": "governor", "en": "governor"},
    {"id": "governance", "ru": "governance", "en": "governance"},
    {"id": "репутация (reputation)", "ru": "репутация", "en": "reputation"},
    {"id": "soulbound-бейдж", "ru": "soulbound", "en": "soulbound"},
    {"id": "защита от Сивиллы (Sybil)", "ru": "сивилл", "en": "sybil"},
    {"id": "IPFS", "ru": "ipfs", "en": "ipfs"},
    {"id": "CID", "ru": "cid", "en": "cid"},
    {"id": "hash-chain", "ru": "hash-chain", "en": "hash-chain"},
    {"id": "смарт-контракт (smart contract)", "ru": "смарт-контракт", "en": "smart contract"},
    {"id": "testnet / mainnet", "ru": "testnet", "en": "testnet"},
    {"id": "приватный ключ (private key)", "ru": "приватный ключ", "en": "private key"},
    {"id": "аудит (audit)", "ru": "аудит", "en": "audit"},
    {"id": "реестр решений (registry)", "ru": "реестр", "en": "registry"},
    {"id": "рельсы (guardrails)", "ru": "рельсы", "en": "guardrails"},
    {"id": "апелляция (appeal)", "ru": "апелляция", "en": "appeal"},
    {"id": "поэтапные выплаты (staged payments)", "ru": "поэтапные выплаты", "en": "staged payments"},
    {"id": "поставщик (provider)", "ru": "поставщик", "en": "provider"},
]


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


def glossary_headings_blob(text):
    """Склеивает жирные заголовки статей глоссария в один blob (нижний регистр)."""
    return "\n".join(BOLD_HEAD_RE.findall(text)).lower()


def check_glossary_coverage(root, existing):
    """МЯГКАЯ проверка: ключевой технический термин имеет статью в глоссарии (RU+EN).

    Не блокирует (статус pass/warn, в вердикт не входит) — только предупреждает,
    чтобы глоссарий не отставал от документов (ст. 3/6, правило PTD-0040). Если
    глоссария нет (например, мини-репозиторий в тесте) — проверять нечего → pass.
    """
    if GLOSSARY_RU not in existing or GLOSSARY_EN not in existing:
        return "pass", []
    ru_blob = glossary_headings_blob(read_text(root, GLOSSARY_RU))
    en_blob = glossary_headings_blob(read_text(root, GLOSSARY_EN))
    violations = []
    for term in KEY_TERMS:
        missing = []
        if term["ru"] not in ru_blob:
            missing.append("RU")
        if term["en"] not in en_blob:
            missing.append("EN")
        if missing:
            violations.append({
                "record": GLOSSARY_RU if "RU" in missing else GLOSSARY_EN,
                "problem": (f"ключевой термин «{term['id']}» не описан в глоссарии "
                            f"({', '.join(missing)}) — глоссарий отстаёт от документов"),
            })
    return ("pass" if not violations else "warn"), violations


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
    {
        "key": "glossary-coverage",
        "title": "Ключевые технические термины описаны в глоссарии (RU+EN)",
        "guards": "ст. 3/6 — понятность/объяснимость (PTD-0040); МЯГКАЯ — предупреждает, не блокирует",
        "fn": "coverage",
        "soft": True,
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
    cov_status, cov_v = check_glossary_coverage(root, existing)

    results = {
        "pairs": (pairs_status, pairs_v),
        "switcher": (switch_status, switch_v),
        "links": (links_status, links_v),
        "coverage": (cov_status, cov_v),
    }

    checks = []
    for spec in CHECKS:
        status, violations = results[spec["fn"]]
        checks.append({
            "key": spec["key"],
            "title": spec["title"],
            "guards": spec["guards"],
            "status": status,
            "soft": spec.get("soft", False),
            "violations": violations,
        })

    # Вердикт — ТОЛЬКО по блокирующим проверкам. Мягкие (soft) проверки лишь
    # предупреждают: они не делают вердикт «красным» и не меняют код возврата.
    blocking = [c for c in checks if not c["soft"]]
    all_pass = all(c["status"] == "pass" for c in blocking)
    passed = sum(1 for c in blocking if c["status"] == "pass")
    warnings = sum(len(c["violations"]) for c in checks if c["soft"])
    return {
        "agent": "documentation",
        "role": "служебный модуль, не орган власти (Конституция, ст. 9)",
        "verdict": "green" if all_pass else "red",
        "passed": passed,
        "total": len(blocking),
        "warnings": warnings,
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
        mark = {"pass": "✓", "fail": "✗", "error": "⚠", "warn": "⚠"}[c["status"]]
        soft = "  (мягкая — не влияет на вердикт)" if c.get("soft") else ""
        print(f"\n{mark} [{c['key']}] {c['title']}{soft}")
        print(f"    защищает: {c['guards']}")
        for v in c["violations"]:
            print(f"    | {v['record']}: {v['problem']}")
    print("\n" + "-" * 70)
    verdict = "ЗЕЛЁНО ✓" if all_pass else "КРАСНО ✗"
    warn_n = report.get("warnings", 0)
    warn_note = f"; предупреждений (мягких): {warn_n}" if warn_n else ""
    print(f"ИТОГ: {verdict}  ({report['passed']}/{report['total']} блокирующих проверок прошли{warn_note})")
    print("-" * 70)
    if warn_n:
        print("Есть мягкие предупреждения (глоссарий отстаёт от документов): это")
        print("повод дополнить глоссарий, но НЕ ошибка — вердикт остаётся прежним.")
    if not all_pass:
        print("Documentation нашёл расхождение в документации (нет пары / битый")
        print("переключатель / битая ссылка). Это сигнал сообществу, а не действие:")
        print("агент не дописывает переводы и не правит ссылки — это делают люди.")
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
