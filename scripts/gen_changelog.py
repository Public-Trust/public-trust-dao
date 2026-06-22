#!/usr/bin/env python3
"""Собрать понятную ленту изменений (CHANGELOG) из публичного реестра решений.

Простыми словами: каждое значимое действие фонда уже записано в открытый
журнал решений (governance/registry/). Но журнал — это набор отдельных
JSON-файлов, по которым человеку неудобно листать «что и когда менялось».
Этот скрипт берёт тот же журнал и раскладывает его в одну читаемую ленту
по датам — чтобы любой человек с одного взгляда видел историю проекта.

Лента — производный, удобочитаемый файл. Источник правды остаётся реестр
(он сцеплен отпечатками и проверяется `scripts/registry.py verify`); если
лента и реестр разойдутся, права лента — пересобрать: `gen_changelog.py`.

Лента двуязычна: CHANGELOG.md (русский) и CHANGELOG.en.md (английский).
Тексты записей берутся дословно из реестра — а он ведётся на русском как на
языке-первоисточнике, поэтому в EN-ленте обрамление английское, а строки
записей повторяют каноничный русский реестр (об этом честно сказано вверху).

Запуск из корня репозитория:
    python3 scripts/gen_changelog.py            # пересобрать обе ленты
    python3 scripts/gen_changelog.py --check    # проверить свежесть (для CI)

Зависимостей нет — только стандартная библиотека Python.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "governance" / "registry" / "index.json"
TARGET_RU = ROOT / "CHANGELOG.md"
TARGET_EN = ROOT / "CHANGELOG.en.md"

# Человеческие названия видов записи (ключи — типы из scripts/registry.py).
TYPE_LABELS = {
    "ru": {
        "genesis": "открытие реестра",
        "decision": "решение",
        "disbursement": "выплата",
        "governance": "управление",
        "audit": "аудит",
        "appeal": "апелляция",
        "reputation": "репутация",
        "note": "заметка",
    },
    "en": {
        "genesis": "registry opened",
        "decision": "decision",
        "disbursement": "disbursement",
        "governance": "governance",
        "audit": "audit",
        "appeal": "appeal",
        "reputation": "reputation",
        "note": "note",
    },
}


def headline(summary: str, limit: int = 180) -> str:
    """Короткий заголовок записи: название записи до первого тире-разделителя.

    Записи реестра почти всегда устроены «Тема: название — подробности», где
    название отделено длинным тире. Берём текст до первого « — »; если тире нет
    (короткие ранние записи), берём весь текст. Точку как границу предложения НЕ
    используем — в русском она ломается об сокращения («См.», «напр.»). Длинный
    заголовок аккуратно подрезаем по границе слова.
    """
    s = " ".join((summary or "").split())
    i = s.find(" — ")
    head = (s[:i] if i != -1 else s).strip()
    if len(head) > limit:
        head = head[:limit].rsplit(" ", 1)[0].strip() + "…"
    return head.strip(" .:—-")


def date_of(entry: dict) -> str:
    ts = entry.get("timestamp") or ""
    return ts[:10] if len(ts) >= 10 else "—"


def grouped_by_date(entries: list[dict]) -> list[tuple[str, list[dict]]]:
    """Сгруппировать записи по дате; даты — новые сверху, внутри — по seq вниз."""
    by_date: dict[str, list[dict]] = {}
    for e in entries:
        by_date.setdefault(date_of(e), []).append(e)
    out = []
    for day in sorted(by_date, reverse=True):
        rows = sorted(by_date[day], key=lambda e: e.get("seq", 0), reverse=True)
        out.append((day, rows))
    return out


def render(index: dict, lang: str) -> str:
    entries = index.get("entries", [])
    count = index.get("count")
    head_hash = index.get("head_hash") or ""
    labels = TYPE_LABELS[lang]

    lines: list[str] = []
    if lang == "ru":
        lines += [
            "[Русский] · [English](CHANGELOG.en.md)",
            "",
            "# Лента изменений — Public Trust DAO",
            "",
            "> **Не редактировать вручную.** Этот файл собирается из публичного "
            "реестра решений\n"
            "> скриптом `scripts/gen_changelog.py`. Пересобрать: "
            "`python3 scripts/gen_changelog.py`.",
            "",
            "## Главное — простыми словами",
            "",
            "Это история проекта одним списком: что и когда было решено и сделано. "
            "Каждая строка — одно значимое действие фонда, уже записанное в открытый "
            "журнал решений. Здесь они просто сложены по датам, новые сверху, чтобы "
            "удобно было читать.",
            "",
            "- **Источник правды — не этот файл, а сам журнал.** Записи журнала "
            "сцеплены отпечатками (изменить прошлое незаметно нельзя) и проверяются "
            "командой `python3 scripts/registry.py verify`.",
            "- **Каждую строку можно открыть целиком** — ссылка ведёт на полную "
            "запись в [реестре решений](governance/registry/records/).",
            "- **Лента собирается машинально** из "
            "[`governance/registry/index.json`](governance/registry/index.json) — "
            "ничего не дописывается от руки.",
            "",
            f"Всего записей: **{count}**. "
            f"Текущий отпечаток журнала: `{head_hash}`.",
            "",
            "---",
            "",
        ]
        intro_link = "Полная запись"
    else:
        lines += [
            "[Русский](CHANGELOG.md) · [English]",
            "",
            "# Changelog — Public Trust DAO",
            "",
            "> **Do not edit by hand.** This file is built from the public decision "
            "record\n"
            "> by `scripts/gen_changelog.py`. Rebuild: "
            "`python3 scripts/gen_changelog.py`.",
            "",
            "## In short — plain words",
            "",
            "This is the project's history as one list: what was decided and done, "
            "and when. Each line is one significant action of the fund, already "
            "written into the open decision record. Here they are simply stacked by "
            "date, newest first, for easy reading.",
            "",
            "- **The source of truth is the record itself, not this file.** Record "
            "entries are chained by fingerprints (the past can't be changed "
            "unnoticed) and are checked with `python3 scripts/registry.py verify`.",
            "- **Every line opens in full** — the link leads to the complete entry "
            "in the [decision registry](governance/registry/records/).",
            "- **The feed is generated mechanically** from "
            "[`governance/registry/index.json`](governance/registry/index.json) — "
            "nothing is written by hand.",
            "- **Entry text is verbatim from the registry,** which is kept in Russian "
            "as the source language; so the wording of each line below mirrors the "
            "canonical Russian record.",
            "",
            f"Total entries: **{count}**. "
            f"Current record fingerprint: `{head_hash}`.",
            "",
            "---",
            "",
        ]
        intro_link = "Full entry"

    for day, rows in grouped_by_date(entries):
        lines.append(f"## {day}")
        lines.append("")
        for e in rows:
            rid = e.get("id", "—")
            typ = labels.get(e.get("type", ""), e.get("type", ""))
            head = headline(e.get("summary", ""))
            rel = e.get("file", "")
            link = f"governance/registry/{rel}" if rel else ""
            label = intro_link
            if link:
                lines.append(f"- **{rid}** ({typ}) — {head}. [{label}]({link})")
            else:
                lines.append(f"- **{rid}** ({typ}) — {head}.")
        lines.append("")

    return "\n".join(lines).rstrip("\n") + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Собрать ленту изменений из реестра решений"
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="только проверить свежесть лент (ничего не записывать; для CI)",
    )
    args = parser.parse_args()

    if not SOURCE.exists():
        print(f"НЕТ ИСТОЧНИКА: {SOURCE}", file=sys.stderr)
        return 2

    index = json.loads(SOURCE.read_text(encoding="utf-8"))
    outputs = {TARGET_RU: render(index, "ru"), TARGET_EN: render(index, "en")}

    if args.check:
        stale = []
        for path, rendered in outputs.items():
            current = path.read_text(encoding="utf-8") if path.exists() else ""
            if current != rendered:
                stale.append(path.name)
        if stale:
            print(
                "Лента изменений устарела (%s) — запустите: "
                "python3 scripts/gen_changelog.py" % ", ".join(stale),
                file=sys.stderr,
            )
            return 1
        print(f"Лента изменений свежая: {index.get('count')} записей.")
        return 0

    for path, rendered in outputs.items():
        path.write_text(rendered, encoding="utf-8")
    print(
        f"Лента изменений собрана: {index.get('count')} записей → "
        f"{TARGET_RU.name} + {TARGET_EN.name}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
