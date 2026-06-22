#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fairness AI-агент — Public Trust DAO (Этап 6, модуль 3/8).

СЛУЖЕБНЫЙ МОДУЛЬ, НЕ ОРГАН ВЛАСТИ (Конституция, ст. 9).
Агент НИЧЕГО не двигает и ничем не владеет: он только ПРОВЕРЯЕТ справедливость
распределения по нормам и докладывает «зелёно/красно». Вся власть — у голосования
сообщества и Safe-мультисига; ИИ лишь помогает соблюдать конституцию (ст. 9).

Что делает: проходит по записям публичного реестра типа `disbursement`
(governance/registry/) и проверяет КАЖДУЮ выплату на соответствие нормам
справедливого распределения и антизлоупотребления:

  • priority-valid    → уровень приоритета входит в шкалу PRIORITIES.md ... ст. 5
  • safeguards        → приоритет НЕ отключает антизлоупотребление ........ ст. 7
  • collective-review → выплату подтверждает не один человек .............. ст. 7
  • staged-payments   → поэтапность валидна (транш index из of) ........... ст. 7
  • applicant-privacy → в записи нет персональных данных заявителя ........ ст. 5/6

Ключевая идея «приоритет — по характеру нужды, а не по личности» (PRIORITIES,
правило 3): шкала приоритетов читается ПРЯМО из docs/PRIORITIES.md (а не зашита в
код) — так заодно проверяется, что код и норматив не разошлись.

Вывод:
  • человекочитаемый отчёт в stdout (✓/✗ по каждой проверке + привязка к статье);
  • при --json — машиночитаемый отчёт (для CI и других агентов);
  • код возврата 0, если все проверки прошли, иначе 1.

«Красный» — это СИГНАЛ сообществу (повод для решения людей), а не действие: агент
сам ничего не исправляет и ничем не распоряжается.

Зависимостей нет — только стандартная библиотека (детерминированно в любом CI).
TESTNET-ONLY: агент не трогает реальные средства/ключи и не выходит в сеть.
"""

import argparse
import json
import os
import re
import sys

# Корень репозитория = на уровень выше каталога ai-agents/.
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Пороги антизлоупотребления (минимумы по ANTI-ABUSE.md).
MIN_APPROVALS = 2      # коллективная проверка: не один человек (§3)
MIN_APPEAL_DAYS = 1    # у участника должно быть окно апелляции (§6)

# Ключи-маркеры персональных данных: их НЕ должно быть в записи (только
# псевдонимный case_id). Дух конституции о достоинстве и приватности.
PERSONAL_KEY_MARKERS = (
    "name", "surname", "firstname", "lastname", "fullname", "patronymic",
    "email", "mail", "phone", "tel", "passport", "ssn", "national_id",
    "dob", "birth", "home_address", "residential", "selfie", "photo", "face",
)
# Допустимые ключи, которые СОДЕРЖАТ маркер, но не являются перс. данными
# (например, "network" содержит "...e", "tel"? нет). Точечные исключения.
PERSONAL_KEY_ALLOW = ("network",)  # на будущее: технические поля-исключения

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")


def load_priority_levels(priorities_path):
    """Читает допустимые уровни приоритета ПРЯМО из docs/PRIORITIES.md.

    Возвращает set целых уровней (например {1..10}). Источник истины — норматив,
    а не зашитый в код список: так код и документ доказуемо не разошлись.
    """
    with open(priorities_path, encoding="utf-8") as fh:
        text = fh.read()
    # Берём первый ```json ... ``` блок, в котором есть "priorities".
    for block in re.findall(r"```json\s*(.*?)```", text, flags=re.DOTALL):
        if '"priorities"' in block:
            data = json.loads(block)
            return {int(p["level"]) for p in data["priorities"]}
    raise ValueError("в PRIORITIES.md не найден машиночитаемый блок priorities")


def load_disbursements(registry_dir):
    """Возвращает список (id, payload) для всех записей type=disbursement по индексу."""
    index_path = os.path.join(registry_dir, "index.json")
    with open(index_path, encoding="utf-8") as fh:
        index = json.load(fh)
    out = []
    for entry in index.get("entries", []):
        if entry.get("type") != "disbursement":
            continue
        rec_path = os.path.join(registry_dir, entry["file"])
        with open(rec_path, encoding="utf-8") as fh:
            record = json.load(fh)
        out.append((entry.get("id", rec_path), record.get("payload", {})))
    return out


def _walk_strings(value):
    """Рекурсивно отдаёт все строковые значения внутри payload."""
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for v in value.values():
            yield from _walk_strings(v)
    elif isinstance(value, list):
        for v in value:
            yield from _walk_strings(v)


def _walk_keys(value):
    """Рекурсивно отдаёт все ключи словарей внутри payload."""
    if isinstance(value, dict):
        for k, v in value.items():
            yield k
            yield from _walk_keys(v)
    elif isinstance(value, list):
        for v in value:
            yield from _walk_keys(v)


# ---- Проверки одной записи. Каждая возвращает (ok: bool, problem: str|None). ----

def check_priority_valid(payload, levels):
    lvl = payload.get("priority_level")
    if lvl in levels:
        return True, None
    return False, f"priority_level={lvl!r} вне шкалы PRIORITIES.md {sorted(levels)}"


def check_safeguards(payload, _levels):
    checks = payload.get("checks", {})
    problems = []
    if checks.get("limit_ok") is not True:
        problems.append("limit_ok != true (лимиты не подтверждены)")
    if checks.get("collective_review") is not True:
        problems.append("collective_review != true")
    days = checks.get("appeal_window_days")
    if not isinstance(days, int) or days < MIN_APPEAL_DAYS:
        problems.append(f"appeal_window_days={days!r} < {MIN_APPEAL_DAYS} (нет окна апелляции)")
    return (not problems), ("; ".join(problems) if problems else None)


def check_collective_review(payload, _levels):
    approvals = payload.get("approvals", [])
    distinct = {a for a in approvals if isinstance(a, str)}
    if len(distinct) < MIN_APPROVALS:
        return False, (f"approvals={approvals!r}: меньше {MIN_APPROVALS} независимых "
                       "подтверждений (единоличное одобрение запрещено)")
    return True, None


def check_staged(payload, _levels):
    stage = payload.get("stage", {})
    idx, of = stage.get("index"), stage.get("of")
    if not isinstance(idx, int) or not isinstance(of, int):
        return False, f"stage index/of не целые: {stage!r}"
    if of < 1 or idx < 1 or idx > of:
        return False, f"нарушена поэтапность: index={idx}, of={of} (нужно 1<=index<=of)"
    return True, None


def check_privacy(payload, _levels):
    problems = []
    for key in _walk_keys(payload):
        kl = key.lower()
        if kl in PERSONAL_KEY_ALLOW:
            continue
        for marker in PERSONAL_KEY_MARKERS:
            if marker in kl:
                problems.append(f"поле '{key}' похоже на персональные данные ({marker})")
                break
    for s in _walk_strings(payload):
        if EMAIL_RE.search(s):
            problems.append(f"значение содержит e-mail-подобную строку: {s!r}")
    return (not problems), ("; ".join(problems) if problems else None)


# Реестр проверок: каждая привязана к статье конституции, которую защищает.
RECORD_CHECKS = [
    {
        "key": "priority-valid",
        "title": "Уровень приоритета входит в шкалу PRIORITIES.md",
        "guards": "ст. 5 — приоритет по характеру нужды (1..10), а не по личности",
        "fn": check_priority_valid,
    },
    {
        "key": "safeguards",
        "title": "Приоритет не отключает антизлоупотребление (лимит/проверка/апелляция)",
        "guards": "ст. 7 — высокий приоритет ускоряет, но не отменяет защиту (PRIORITIES, правило 2)",
        "fn": check_safeguards,
    },
    {
        "key": "collective-review",
        "title": "Выплату подтверждает не один человек",
        "guards": "ст. 7 — коллективная проверка; нельзя одобрить выплату единолично (ANTI-ABUSE §3)",
        "fn": check_collective_review,
    },
    {
        "key": "staged-payments",
        "title": "Поэтапность валидна (транш index из of)",
        "guards": "ст. 7 — дробление снижает риск (ANTI-ABUSE §1)",
        "fn": check_staged,
    },
    {
        "key": "applicant-privacy",
        "title": "В записи нет персональных данных заявителя",
        "guards": "ст. 5/6 — достоинство и приватность; только псевдонимный case_id",
        "fn": check_privacy,
    },
]


def run(root):
    """Прогоняет все проверки по всем disbursement-записям. Возвращает report dict."""
    registry_dir = os.path.join(root, "governance", "registry")
    priorities_path = os.path.join(root, "docs", "PRIORITIES.md")

    errors = []
    try:
        levels = load_priority_levels(priorities_path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        levels = None
        errors.append(f"не удалось прочитать шкалу приоритетов: {exc}")

    records = []
    try:
        records = load_disbursements(registry_dir)
    except (OSError, KeyError, json.JSONDecodeError) as exc:
        errors.append(f"не удалось прочитать реестр выплат: {exc}")

    checks = []
    for spec in RECORD_CHECKS:
        violations = []
        if levels is None and spec["key"] == "priority-valid":
            status = "error"
        else:
            for rid, payload in records:
                ok, problem = spec["fn"](payload, levels)
                if not ok:
                    violations.append({"record": rid, "problem": problem})
            status = "pass" if not violations else "fail"
        checks.append({
            "key": spec["key"],
            "title": spec["title"],
            "guards": spec["guards"],
            "status": status,
            "violations": violations,
        })

    if errors:
        # Ошибка чтения нормативов/реестра — это «красный» (нельзя подтвердить справедливость).
        checks.append({
            "key": "inputs",
            "title": "Чтение нормативов и реестра",
            "guards": "ст. 3 — данные для проверки доступны и читаемы",
            "status": "error",
            "violations": [{"record": "-", "problem": e} for e in errors],
        })

    all_pass = all(c["status"] == "pass" for c in checks)
    passed = sum(1 for c in checks if c["status"] == "pass")
    return {
        "agent": "fairness",
        "role": "служебный модуль, не орган власти (Конституция, ст. 9)",
        "verdict": "green" if all_pass else "red",
        "passed": passed,
        "total": len(checks),
        "disbursements_checked": len(records),
        "priority_levels": sorted(levels) if levels else None,
        "checks": checks,
    }


def main(argv):
    parser = argparse.ArgumentParser(
        description="Fairness AI-агент Public Trust DAO: проверка справедливости распределения."
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
    print("FAIRNESS AI-АГЕНТ — Public Trust DAO")
    print("Служебный модуль (ст. 9): проверяет справедливость, не правит. Ничего не двигает.")
    print("=" * 70)
    print(f"Проверено записей о выплатах (disbursement): {report['disbursements_checked']}")
    if report["priority_levels"]:
        print(f"Шкала приоритетов из PRIORITIES.md: {report['priority_levels']}")
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
        print("Fairness нашёл нарушение справедливости/защиты. Это сигнал сообществу,")
        print("а не действие: агент не исправляет и не распоряжается — решает голосование.")
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
