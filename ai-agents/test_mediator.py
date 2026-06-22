#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест-инвариант для Mediator-агента — Public Trust DAO.

Доказывает, что Mediator РАБОТАЕТ (а не «зелёный по умолчанию»): на КАЖДОЕ
отклонение процесса споров/апелляций от конституции (необжалуемая санкция; спор
решает ИИ/медиатор; один человек вместо коллектива; самопересмотр — апелляцию
решает автор санкции; тупик/сирота/нет терминала в цикле; нулевой срок; битая
ссылка) он обязан вернуть «красно» (exit=1), а на корректном процессе —
«зелёно» (exit=0), без ложных срабатываний.

Метод: строим временный «мини-репозиторий» с
governance/mediation/dispute-process.json и доками, на которые он ссылается;
подсовываем то корректную, то «отравленную» версию; запускаем агент через --root
и проверяем вердикт по --json. Только стандартная библиотека. Сети нет.
"""

import copy
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
AGENT = os.path.join(HERE, "mediator_agent.py")

PASSED = 0
FAILED = 0

# Доки/файлы, на которые ссылается корректный процесс (содержимое не важно —
# агент проверяет лишь существование цели).
GOOD_DOCS = [
    "docs/ANTI-ABUSE.md",
    "docs/CONSTITUTION.md",
    "docs/PRIORITIES.md",
    "governance/registry/README.md",
    "governance/mediation/README.md",
]

GOOD_PROCESS = {
    "version": "test",
    "kind": "dispute-appeal-process",
    "role": "Mediator структурирует, не решает",
    "spec": "docs/ANTI-ABUSE.md",
    "off_chain_signaling": True,
    "sanctions": [
        {"key": "disbursement-rejection", "source": "docs/ANTI-ABUSE.md",
         "appealable": True, "issued_by": "disbursement-reviewers", "appeal_entry": "intake"},
        {"key": "reputation-sanction", "source": "docs/ANTI-ABUSE.md",
         "appealable": True, "issued_by": "reputation-process", "appeal_entry": "intake"},
        {"key": "temporary-freeze", "source": "docs/ANTI-ABUSE.md",
         "appealable": True, "issued_by": "guardian-council", "appeal_entry": "intake"},
        {"key": "exclusion", "source": "docs/ANTI-ABUSE.md",
         "appealable": True, "issued_by": "guardian-council", "appeal_entry": "intake"},
    ],
    "stages": [
        {"key": "intake", "initial": True, "role": "structure",
         "decider": "mediator-agent", "deadline_seconds": 259200, "next": ["review"]},
        {"key": "review", "role": "decide", "decider": "independent-reviewers",
         "min_deciders": 2, "deadline_seconds": 604800, "next": ["resolved", "escalation"]},
        {"key": "escalation", "role": "decide", "decider": "guardian-council",
         "min_deciders": 3, "deadline_seconds": 1209600, "next": ["resolved"]},
        {"key": "resolved", "terminal": True, "role": "record"},
    ],
    "links": {
        "anti_abuse": "docs/ANTI-ABUSE.md",
        "constitution": "docs/CONSTITUTION.md",
        "priorities": "docs/PRIORITIES.md",
        "registry": "governance/registry/README.md",
        "readme": "governance/mediation/README.md",
    },
}


def check(name, cond):
    global PASSED, FAILED
    if cond:
        PASSED += 1
        print(f"  ✓ {name}")
    else:
        FAILED += 1
        print(f"  ✗ {name}")


def make_repo(tmp, process):
    for rel in GOOD_DOCS:
        full = os.path.join(tmp, rel)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w", encoding="utf-8") as fh:
            fh.write("# stub\n")
    full = os.path.join(tmp, "governance/mediation/dispute-process.json")
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as fh:
        json.dump(process, fh, ensure_ascii=False, indent=2)


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


def scenario(title, process, expect_green, expect_fail_key=None):
    print(f"\n[{title}]")
    tmp = tempfile.mkdtemp(prefix="med-test-")
    try:
        make_repo(tmp, process)
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


def mut(fn):
    p = copy.deepcopy(GOOD_PROCESS)
    fn(p)
    return p


def get_stage(p, key):
    for s in p["stages"]:
        if s["key"] == key:
            return s
    return None


def get_sanction(p, key):
    for s in p["sanctions"]:
        if s["key"] == key:
            return s
    return None


def main():
    print("ТЕСТ-ИНВАРИАНТ MEDIATOR — доказываем, что красное ловится, зелёное не ложно-падает")

    # 1. Корректный процесс → зелёно.
    scenario("корректный процесс споров/апелляций", GOOD_PROCESS, expect_green=True)

    # 2. Санкция стала необжалуемой → appeal-for-every-sanction красный.
    scenario("санкция appealable=false",
             mut(lambda p: get_sanction(p, "exclusion").update(appealable=False)),
             expect_green=False, expect_fail_key="appeal-for-every-sanction")

    # 3. Нет канонической санкции вовсе → appeal-for-every-sanction красный.
    scenario("нет санкции temporary-freeze",
             mut(lambda p: p["sanctions"].remove(get_sanction(p, "temporary-freeze"))),
             expect_green=False, expect_fail_key="appeal-for-every-sanction")

    # 4. appeal_entry ведёт в несуществующую стадию → appeal-for-every-sanction красный.
    scenario("appeal_entry в никуда",
             mut(lambda p: get_sanction(p, "exclusion").update(appeal_entry="ghost")),
             expect_green=False, expect_fail_key="appeal-for-every-sanction")

    # 5. Решающую стадию решает ИИ → mediator-not-decider красный.
    scenario("решающую стадию решает ИИ-агент",
             mut(lambda p: get_stage(p, "review").update(decider="mediator-ai")),
             expect_green=False, expect_fail_key="mediator-not-decider")

    # 6. Решает один человек (min_deciders=1) → mediator-not-decider красный.
    scenario("спор решает один (min_deciders=1)",
             mut(lambda p: get_stage(p, "review").update(min_deciders=1)),
             expect_green=False, expect_fail_key="mediator-not-decider")

    # 7. Самопересмотр: апелляцию решает автор санкции → independent-review красный.
    scenario("самопересмотр (decider == issued_by)",
             mut(lambda p: get_sanction(p, "exclusion").update(issued_by="independent-reviewers")),
             expect_green=False, expect_fail_key="independent-review")

    # 8. Тупик: у не-терминальной стадии нет next → valid-lifecycle красный.
    scenario("тупик (review без next)",
             mut(lambda p: get_stage(p, "review").update(next=[])),
             expect_green=False, expect_fail_key="valid-lifecycle")

    # 9. Переход в несуществующую стадию → valid-lifecycle красный.
    scenario("переход в несуществующую стадию",
             mut(lambda p: get_stage(p, "review").update(next=["resolved", "ghost"])),
             expect_green=False, expect_fail_key="valid-lifecycle")

    # 10. Нет терминальной стадии → valid-lifecycle красный.
    scenario("нет терминала",
             mut(lambda p: get_stage(p, "resolved").update(terminal=False, next=["review"])),
             expect_green=False, expect_fail_key="valid-lifecycle")

    # 11. Две начальные стадии → valid-lifecycle красный.
    scenario("две начальные стадии",
             mut(lambda p: get_stage(p, "review").update(initial=True)),
             expect_green=False, expect_fail_key="valid-lifecycle")

    # 12. Нулевой срок у стадии → bounded-timelines красный.
    scenario("deadline_seconds=0",
             mut(lambda p: get_stage(p, "review").update(deadline_seconds=0)),
             expect_green=False, expect_fail_key="bounded-timelines")

    # 13. Битая doc-ссылка процесса → process-links красный.
    scenario("битая doc-ссылка процесса",
             mut(lambda p: p["links"].update(constitution="docs/NOPE.md")),
             expect_green=False, expect_fail_key="process-links")

    # 14. Отсутствует сам dispute-process.json → не «зеленеет по умолчанию».
    print("\n[нет dispute-process.json вовсе]")
    tmp = tempfile.mkdtemp(prefix="med-test-")
    try:
        make_repo(tmp, GOOD_PROCESS)
        os.remove(os.path.join(tmp, "governance/mediation/dispute-process.json"))
        code, report = run_agent(tmp)
        check("вердикт red / exit=1", report.get("verdict") == "red" and code == 1)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print(f"\nИТОГ: {PASSED} прошли, {FAILED} провалились")
    return 0 if FAILED == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
