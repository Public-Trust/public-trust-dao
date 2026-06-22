#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mediator AI-агент — Public Trust DAO (Этап 6, модуль 8/8 — последний).

СЛУЖЕБНЫЙ МОДУЛЬ, НЕ ОРГАН ВЛАСТИ (Конституция, ст. 9.2).
Mediator СТРУКТУРИРУЕТ споры и апелляции, но НИКОГДА НЕ РЕШАЕТ их: он только
ПРОВЕРЯЕТ, что процесс обжалования (docs/ANTI-ABUSE.md, механизм №6 «Апелляции»)
построен по конституции — у каждой санкции есть прозрачный путь обжалования,
решают независимые ЛЮДИ (а не ИИ и не один человек), сроки ограничены, никто не
пересматривает собственное решение — и докладывает «зелёно/красно». Сам агент
ничего не решает, никого не наказывает и никого не оправдывает.

Зачем: ANTI-ABUSE.md описывает право на апелляцию словами («у участника есть
прозрачный путь обжалования отказа/санкции»). Этот агент превращает право в
МАШИННУЮ проверку конкретного артефакта — governance/mediation/dispute-process.json
(жизненный цикл спора/апелляции), — чтобы процесс не разъехался с конституцией
молча: чтобы какую-нибудь санкцию не сделали необжалуемой, чтобы решение
апелляции не отдали ИИ или одному лицу, чтобы апелляцию не рассматривал тот же,
кто вынес санкцию, и чтобы сроки рассмотрения были заданы и конечны.

Что делает (read-only, по JSON-конфигу процесса, без сети):

  • appeal-for-every-sanction → каждая каноническая санкция ANTI-ABUSE (отказ в
    выплате, репутационная санкция, временная заморозка, исключение) присутствует,
    appealable=true и ведёт к существующей точке входа апелляции ........ §6 ANTI-ABUSE
  • mediator-not-decider     → ни одну РЕШАЮЩУЮ стадию (role=decide) не решает
    ИИ/автомат или один человек: decider — люди, min_deciders ≥ 2; Mediator
    допустим только на не-решающих стадиях (structure/record) ........... ст. 9.2 / §3
  • independent-review       → апелляцию решает НЕ тот, кто вынес санкцию
    (первая решающая стадия от точки входа decider ≠ issued_by) ......... §3 ANTI-ABUSE
  • valid-lifecycle         → корректный жизненный цикл: ровно одна начальная
    стадия, есть терминальная, все переходы next ведут к объявленным стадиям,
    у не-терминальной есть переходы, у терминальной их нет, все достижимы .. ст. 3
  • bounded-timelines       → у каждой не-терминальной стадии задан положительный
    срок (апелляция не зависает навсегда) .............................. ст. 3 / §6
  • process-links           → все doc-ссылки конфига ведут к существующим файлам . ст. 3

Вывод:
  • человекочитаемый отчёт в stdout (✓/✗ по каждой проверке + привязка к статье);
  • при --json — машиночитаемый отчёт (для CI и других агентов);
  • код возврата 0, если все проверки прошли, иначе 1.

«Красный» — это СИГНАЛ сообществу (повод для решения людей), а не действие: агент
сам не правит процесс и не решает споры.

Зависимостей нет — только стандартная библиотека (детерминированно в любом CI).
TESTNET-ONLY: агент не трогает реальные средства/ключи и не выходит в сеть.
"""

import argparse
import json
import os
import sys

# Корень репозитория = на уровень выше каталога ai-agents/.
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DISPUTE_PROCESS = "governance/mediation/dispute-process.json"

# Канонические санкции из docs/ANTI-ABUSE.md, у которых ОБЯЗАН быть путь
# обжалования (механизм №6 «Апелляции» прикрывает отказы и санкции №7–№9).
REQUIRED_SANCTIONS = (
    "disbursement-rejection",  # обжалование отказа в помощи/выплате
    "reputation-sanction",     # №7 репутационные санкции
    "temporary-freeze",        # №8 временные ограничения
    "exclusion",               # №9 исключение участника
)

# Маркеры «решателя», запрещённого на РЕШАЮЩЕЙ стадии: ИИ/автомат/сам медиатор.
# Право решать спор принадлежит людям, а не алгоритму (Конституция ст. 9.2).
NON_HUMAN_DECIDER_MARKERS = (
    "ai", "agent", "bot", "mediator", "algorithm", "automated", "oracle", "model",
)


def read_json(root, rel):
    """Читает JSON-файл. Возвращает (data, error|None)."""
    full = os.path.join(root, rel)
    if not os.path.exists(full):
        return None, f"файл не найден: {rel}"
    try:
        with open(full, encoding="utf-8") as fh:
            return json.load(fh), None
    except (OSError, ValueError) as exc:
        return None, f"не читается/не парсится {rel}: {exc}"


def stages_by_key(process):
    return {s.get("key"): s for s in (process.get("stages", []) or [])}


def first_deciding_stage(process, entry_key):
    """Идёт от точки входа по первой ветке next до первой role=='decide'.

    Возвращает стадию-решателя или None (если решающей стадии нет / цикл / обрыв).
    """
    stages = stages_by_key(process)
    seen = set()
    cur = entry_key
    while cur is not None and cur not in seen:
        seen.add(cur)
        stage = stages.get(cur)
        if stage is None:
            return None
        if stage.get("role") == "decide":
            return stage
        nxt = stage.get("next", []) or []
        cur = nxt[0] if nxt else None
    return None


# ---- Проверки. Каждая возвращает (status, violations[list]). ----

def check_appeal_for_every_sanction(process):
    """У каждой канонической санкции есть обжалование к существующей стадии входа."""
    violations = []
    stages = stages_by_key(process)
    by_key = {s.get("key"): s for s in (process.get("sanctions", []) or [])}
    for key in REQUIRED_SANCTIONS:
        s = by_key.get(key)
        if s is None:
            violations.append({"record": DISPUTE_PROCESS,
                               "problem": f"нет санкции '{key}' — у неё должен быть "
                                          f"путь обжалования (ANTI-ABUSE §6)"})
            continue
        if s.get("appealable") is not True:
            violations.append({"record": DISPUTE_PROCESS,
                               "problem": f"санкция '{key}' appealable="
                                          f"{s.get('appealable')!r} — обжалование "
                                          f"обязательно (ANTI-ABUSE §6)"})
        entry = s.get("appeal_entry")
        if entry not in stages:
            violations.append({"record": DISPUTE_PROCESS,
                               "problem": f"санкция '{key}': appeal_entry={entry!r} "
                                          f"не ведёт к объявленной стадии"})
    return ("pass" if not violations else "fail"), violations


def check_mediator_not_decider(process):
    """Решающую стадию решают ЛЮДИ (≥2), не ИИ/автомат и не один человек."""
    violations = []
    for stage in (process.get("stages", []) or []):
        if stage.get("role") != "decide":
            continue
        key = stage.get("key")
        decider = str(stage.get("decider", "")).lower()
        if not decider:
            violations.append({"record": DISPUTE_PROCESS,
                               "problem": f"решающая стадия '{key}' без decider"})
            continue
        if any(m in decider for m in NON_HUMAN_DECIDER_MARKERS):
            violations.append({
                "record": DISPUTE_PROCESS,
                "problem": f"решающую стадию '{key}' решает '{stage.get('decider')}' — "
                           f"спор решают ЛЮДИ, не ИИ/медиатор/автомат (ст. 9.2)",
            })
        md = stage.get("min_deciders")
        if not isinstance(md, int) or isinstance(md, bool) or md < 2:
            violations.append({
                "record": DISPUTE_PROCESS,
                "problem": f"решающая стадия '{key}': min_deciders={md!r} — нужно ≥2 "
                           f"(коллективная проверка, никто единолично; ANTI-ABUSE §3)",
            })
    return ("pass" if not violations else "fail"), violations


def check_independent_review(process):
    """Апелляцию решает не тот, кто вынес санкцию (первая решающая ≠ issued_by)."""
    violations = []
    for s in (process.get("sanctions", []) or []):
        key = s.get("key")
        issued_by = s.get("issued_by")
        entry = s.get("appeal_entry")
        deciding = first_deciding_stage(process, entry)
        if deciding is None:
            violations.append({
                "record": DISPUTE_PROCESS,
                "problem": f"санкция '{key}': от точки входа '{entry}' не достижима "
                           f"ни одна решающая стадия (некому рассмотреть апелляцию)",
            })
            continue
        if issued_by is not None and deciding.get("decider") == issued_by:
            violations.append({
                "record": DISPUTE_PROCESS,
                "problem": f"санкция '{key}': апелляцию решает тот же '{issued_by}', "
                           f"кто вынес санкцию — нужен независимый рассмотритель (§3)",
            })
    return ("pass" if not violations else "fail"), violations


def check_valid_lifecycle(process):
    """Корректный конечный автомат: один старт, есть терминал, переходы целы, всё достижимо."""
    violations = []
    stages = process.get("stages", []) or []
    by_key = stages_by_key(process)
    if not stages:
        violations.append({"record": DISPUTE_PROCESS, "problem": "не объявлено ни одной стадии"})
        return "fail", violations

    initials = [s.get("key") for s in stages if s.get("initial") is True]
    if len(initials) != 1:
        violations.append({"record": DISPUTE_PROCESS,
                           "problem": f"начальных стадий (initial=true) должно быть ровно "
                                      f"1, найдено {len(initials)}: {initials}"})
    terminals = [s.get("key") for s in stages if s.get("terminal") is True]
    if not terminals:
        violations.append({"record": DISPUTE_PROCESS,
                           "problem": "нет ни одной терминальной стадии (terminal=true) — "
                                      "спор не может завершиться"})

    for s in stages:
        key = s.get("key")
        nxt = s.get("next", []) or []
        if s.get("terminal") is True:
            if nxt:
                violations.append({"record": DISPUTE_PROCESS,
                                   "problem": f"терминальная стадия '{key}' имеет переходы "
                                              f"next={nxt} — у конца их быть не должно"})
        else:
            if not nxt:
                violations.append({"record": DISPUTE_PROCESS,
                                   "problem": f"не-терминальная стадия '{key}' без next — "
                                              f"тупик (спор застрянет)"})
            for t in nxt:
                if t not in by_key:
                    violations.append({"record": DISPUTE_PROCESS,
                                       "problem": f"стадия '{key}' ссылается на "
                                                  f"несуществующую стадию '{t}'"})

    # Достижимость из начальной стадии (по объявленным переходам).
    if len(initials) == 1:
        reachable = set()
        frontier = [initials[0]]
        while frontier:
            cur = frontier.pop()
            if cur in reachable or cur not in by_key:
                continue
            reachable.add(cur)
            frontier.extend(by_key[cur].get("next", []) or [])
        for s in stages:
            if s.get("key") not in reachable:
                violations.append({"record": DISPUTE_PROCESS,
                                   "problem": f"стадия '{s.get('key')}' недостижима от "
                                              f"начальной '{initials[0]}'"})
    return ("pass" if not violations else "fail"), violations


def check_bounded_timelines(process):
    """У каждой не-терминальной стадии задан положительный срок (срок конечен)."""
    violations = []
    for s in (process.get("stages", []) or []):
        if s.get("terminal") is True:
            continue
        key = s.get("key")
        d = s.get("deadline_seconds")
        if not isinstance(d, int) or isinstance(d, bool) or d <= 0:
            violations.append({
                "record": DISPUTE_PROCESS,
                "problem": f"стадия '{key}': deadline_seconds={d!r} — нужен "
                           f"положительный срок (апелляция не должна зависать; ст. 3 / §6)",
            })
    return ("pass" if not violations else "fail"), violations


def check_process_links(root, process):
    """Все doc-ссылки конфига ведут к существующему файлу/каталогу."""
    violations = []
    links = process.get("links", {}) or {}
    targets = [v for v in links.values()
               if isinstance(v, str) and v.startswith(("docs/", "governance/"))]
    for s in (process.get("sanctions", []) or []):
        src = s.get("source")
        if isinstance(src, str) and src.startswith(("docs/", "governance/")):
            targets.append(src)
    for target in targets:
        if not os.path.exists(os.path.join(root, target)):
            violations.append({"record": DISPUTE_PROCESS,
                               "problem": f"ссылка процесса ведёт в никуда → {target!r}"})
    return ("pass" if not violations else "fail"), violations


CHECKS = [
    {
        "key": "appeal-for-every-sanction",
        "title": "У каждой санкции ANTI-ABUSE есть путь обжалования",
        "guards": "ANTI-ABUSE §6 — у участника есть прозрачный путь обжалования отказа/санкции",
        "fn": "appeals",
    },
    {
        "key": "mediator-not-decider",
        "title": "Спор решают люди (≥2), не ИИ/медиатор/автомат и не один человек",
        "guards": "ст. 9.2 + ANTI-ABUSE §3 — ИИ не орган власти; решает коллектив людей",
        "fn": "notdecider",
    },
    {
        "key": "independent-review",
        "title": "Апелляцию рассматривает не тот, кто вынес санкцию",
        "guards": "ANTI-ABUSE §3 — независимая проверка; нельзя пересматривать своё решение",
        "fn": "independent",
    },
    {
        "key": "valid-lifecycle",
        "title": "Корректный жизненный цикл спора (старт/терминал/переходы/достижимость)",
        "guards": "ст. 3 — проверяемость: процесс — целостный автомат без тупиков и сирот",
        "fn": "lifecycle",
    },
    {
        "key": "bounded-timelines",
        "title": "У каждой не-терминальной стадии задан положительный срок",
        "guards": "ст. 3 + ANTI-ABUSE §6 — апелляция рассматривается в конечный срок, не зависает",
        "fn": "timelines",
    },
    {
        "key": "process-links",
        "title": "Все doc-ссылки процесса ведут к существующему файлу",
        "guards": "ст. 3 — процесс привязан к реальным нормам, ссылки не битые",
        "fn": "links",
    },
]


def run(root):
    """Прогоняет все проверки. Возвращает report dict."""
    process, err = read_json(root, DISPUTE_PROCESS)

    if err:
        fail = ("fail", [{"record": DISPUTE_PROCESS, "problem": err}])
        results = {k: fail for k in
                   ("appeals", "notdecider", "independent", "lifecycle", "timelines", "links")}
    else:
        results = {
            "appeals": check_appeal_for_every_sanction(process),
            "notdecider": check_mediator_not_decider(process),
            "independent": check_independent_review(process),
            "lifecycle": check_valid_lifecycle(process),
            "timelines": check_bounded_timelines(process),
            "links": check_process_links(root, process),
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
        "agent": "mediator",
        "role": "служебный модуль, не орган власти (Конституция, ст. 9.2); структурирует "
                "споры/апелляции, НЕ решает их",
        "verdict": "green" if all_pass else "red",
        "passed": passed,
        "total": len(checks),
        "artifacts": {"dispute_process": DISPUTE_PROCESS},
        "checks": checks,
    }


def main(argv):
    parser = argparse.ArgumentParser(
        description="Mediator AI-агент Public Trust DAO: проверяет процесс споров/"
                    "апелляций (обжалуемость санкций, решают люди, независимость, "
                    "сроки, целостность). СТРУКТУРИРУЕТ, НЕ решает."
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
    print("MEDIATOR AI-АГЕНТ — Public Trust DAO")
    print("Служебный модуль (ст. 9.2): проверяет процесс споров/апелляций.")
    print("СТРУКТУРИРУЕТ, НЕ решает. Находка = сигнал сообществу, а не действие.")
    print("=" * 70)
    print(f"Артефакт процесса: {report['artifacts']['dispute_process']}")
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
        print("Mediator нашёл расхождение процесса обжалования с конституцией")
        print("(необжалуемая санкция / спор решает ИИ или один / самопересмотр /")
        print("тупик в цикле / нет срока / битая ссылка). Это сигнал сообществу, а не")
        print("действие: агент не правит процесс и не решает споры сам.")
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
