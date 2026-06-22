#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест-инвариант для Fairness-агента — Public Trust DAO.

Доказывает, что Fairness РАБОТАЕТ (а не «зелёный по умолчанию»): на КАЖДОЕ
нарушение справедливости/защиты он обязан вернуть «красно» (exit=1), а на чистой
корректной выплате — «зелёно» (exit=0), без ложных срабатываний.

Метод: строим временный «мини-репозиторий» (docs/PRIORITIES.md с тем же
машиночитаемым блоком + governance/registry/index.json с записями) и подсовываем
то корректные, то «отравленные» disbursement-записи; запускаем агент через
--root и проверяем вердикт по --json. Только стандартная библиотека. Сети нет.
"""

import copy
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
AGENT = os.path.join(HERE, "fairness_agent.py")

PASSED = 0
FAILED = 0

# Минимальный машиночитаемый блок приоритетов — как в docs/PRIORITIES.md.
PRIORITIES_MD = """# PRIORITIES (тест)

```json
{
  "priorities": [
    { "level": 1,  "key": "life_threat",  "label": "Угроза жизни" },
    { "level": 2,  "key": "housing_loss", "label": "Угроза потери жилья" },
    { "level": 3,  "key": "medical",      "label": "Медицинская помощь" },
    { "level": 10, "key": "public_good",  "label": "Долгосрочная общественная польза" }
  ]
}
```
"""

# Корректная базовая выплата — должна давать «зелёно».
GOOD_PAYLOAD = {
    "case_id": "TEST-CASE-0001",
    "priority_level": 2,
    "amount": "100.00",
    "asset": "TEST-MATIC",
    "network": "polygon-amoy",
    "stage": {"index": 1, "of": 3},
    "approvals": ["guardian-ai:ok", "keeper-quorum:3of5", "snapshot:demo"],
    "checks": {"limit_ok": True, "collective_review": True, "appeal_window_days": 7},
}


def check(name, cond):
    global PASSED, FAILED
    if cond:
        PASSED += 1
        print(f"  ✓ {name}")
    else:
        FAILED += 1
        print(f"  ✗ {name}")


def make_repo(tmp, payloads):
    """Создаёт docs/PRIORITIES.md и реестр с disbursement-записями из payloads."""
    os.makedirs(os.path.join(tmp, "docs"))
    with open(os.path.join(tmp, "docs", "PRIORITIES.md"), "w", encoding="utf-8") as fh:
        fh.write(PRIORITIES_MD)
    reg = os.path.join(tmp, "governance", "registry", "records")
    os.makedirs(reg)
    entries = []
    for i, payload in enumerate(payloads):
        rid = f"PTD-{i:04d}"
        fname = f"records/{i:04d}-disb.json"
        with open(os.path.join(tmp, "governance", "registry", fname), "w", encoding="utf-8") as fh:
            json.dump({"id": rid, "type": "disbursement", "payload": payload}, fh)
        entries.append({"seq": i, "id": rid, "type": "disbursement", "file": fname})
    with open(os.path.join(tmp, "governance", "registry", "index.json"), "w", encoding="utf-8") as fh:
        json.dump({"count": len(entries), "entries": entries}, fh)


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


def scenario(title, payload, expect_green, expect_fail_key=None):
    """Один сценарий: payload (одна запись), ожидаемый вердикт."""
    print(f"\n[{title}]")
    tmp = tempfile.mkdtemp(prefix="fairness-test-")
    try:
        make_repo(tmp, [payload])
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


def mutate(**changes):
    """Копия GOOD_PAYLOAD с заменами верхнего уровня."""
    p = copy.deepcopy(GOOD_PAYLOAD)
    p.update(changes)
    return p


def main():
    print("ТЕСТ-ИНВАРИАНТ FAIRNESS — доказываем, что красное ловится, зелёное не ложно-падает")

    # 1. Корректная выплата → зелёно.
    scenario("корректная выплата", mutate(), expect_green=True)

    # 2. Приоритет вне шкалы → priority-valid красный.
    scenario("priority_level=99 (вне шкалы)", mutate(priority_level=99),
             expect_green=False, expect_fail_key="priority-valid")

    # 3. Лимиты не подтверждены → safeguards красный.
    scenario("limit_ok=false",
             mutate(checks={"limit_ok": False, "collective_review": True, "appeal_window_days": 7}),
             expect_green=False, expect_fail_key="safeguards")

    # 4. Нет окна апелляции → safeguards красный.
    scenario("appeal_window_days=0",
             mutate(checks={"limit_ok": True, "collective_review": True, "appeal_window_days": 0}),
             expect_green=False, expect_fail_key="safeguards")

    # 5. Единоличное одобрение → collective-review красный.
    scenario("одно подтверждение (единолично)", mutate(approvals=["keeper:only-one"]),
             expect_green=False, expect_fail_key="collective-review")

    # 6. Сломана поэтапность → staged-payments красный.
    scenario("stage index>of", mutate(stage={"index": 4, "of": 3}),
             expect_green=False, expect_fail_key="staged-payments")

    # 7. Персональные данные (имя) → applicant-privacy красный.
    scenario("в записи есть applicant_name", mutate(applicant_name="Иван Иванов"),
             expect_green=False, expect_fail_key="applicant-privacy")

    # 8. Персональные данные (e-mail в значении) → applicant-privacy красный.
    scenario("в записи есть e-mail", mutate(contact="ivan@example.com"),
             expect_green=False, expect_fail_key="applicant-privacy")

    # 9. Пустой реестр (нет выплат) → зелёно (нечего нарушать), без ложного падения.
    print("\n[пустой реестр выплат]")
    tmp = tempfile.mkdtemp(prefix="fairness-test-")
    try:
        make_repo(tmp, [])
        code, report = run_agent(tmp)
        check("вердикт green / exit=0", report.get("verdict") == "green" and code == 0)
        check("проверено 0 выплат", report.get("disbursements_checked") == 0)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print(f"\nИТОГ: {PASSED} прошли, {FAILED} провалились")
    return 0 if FAILED == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
