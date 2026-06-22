#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест-инвариант для Governance-агента — Public Trust DAO.

Доказывает, что Governance РАБОТАЕТ (а не «зелёный по умолчанию»): на КАЖДОЕ
отклонение конфигурации управления от конституции (плутократический вес голоса,
нулевой/отрицательный срок голосования, off-chain тип, который «исполняет сам»,
тип про деньги/конституцию без привязки к нормам, единоличный/сломанный порог
мультисига, битая doc-ссылка) он обязан вернуть «красно» (exit=1), а на
корректных конфигах — «зелёно» (exit=0), без ложных срабатываний.

Метод: строим временный «мини-репозиторий» с governance/snapshot/space.json,
governance/safe/safe.config.json и доками, на которые они ссылаются; подсовываем
то корректные, то «отравленные» версии; запускаем агент через --root и проверяем
вердикт по --json. Только стандартная библиотека. Сети нет.
"""

import copy
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
AGENT = os.path.join(HERE, "governance_agent.py")

PASSED = 0
FAILED = 0

# Доки, на которые ссылается корректный конфиг (содержимое не важно — агент
# проверяет лишь существование файла-цели).
GOOD_DOCS = [
    "docs/GOVERNANCE.md",
    "docs/CONSTITUTION.md",
    "docs/PRIORITIES.md",
    "docs/ANTI-ABUSE.md",
    "governance/safe/README.md",
    "governance/snapshot/README.md",
    "governance/registry/README.md",
]

GOOD_SPACE = {
    "off_chain_signaling": True,
    "settings": {
        "strategies": [
            {"name": "ticket", "network": "80002", "params": {"symbol": "VOICE", "value": 1}}
        ],
        "validation": {
            "name": "basic",
            "params": {
                "minScore": 1,
                "strategies": [
                    {"name": "ticket", "network": "80002", "params": {"symbol": "VOICE", "value": 1}}
                ],
            },
        },
        "voting": {"delay": 86400, "period": 432000, "quorum": 0, "type": "single-choice"},
    },
    "proposal_types": [
        {"key": "signal", "binding": False},
        {
            "key": "disbursement-direction",
            "binding": False,
            "links": ["docs/PRIORITIES.md", "docs/ANTI-ABUSE.md"],
        },
        {"key": "parameter-change", "binding": False},
        {
            "key": "constitution-amendment",
            "binding": False,
            "requires_supermajority": True,
            "links": ["docs/CONSTITUTION.md"],
        },
        {"key": "phase-transition", "binding": False},
    ],
    "links": {
        "governance_spec": "docs/GOVERNANCE.md",
        "constitution": "docs/CONSTITUTION.md",
        "priorities": "docs/PRIORITIES.md",
        "anti_abuse": "docs/ANTI-ABUSE.md",
        "registry": "governance/registry/README.md",
        "readme": "governance/snapshot/README.md",
    },
}

GOOD_SAFE = {
    "safe": {"version": "1.4.1", "threshold": 3, "owners_required": 5, "owners": []},
    "links": {
        "governance_spec": "docs/GOVERNANCE.md",
        "constitution": "docs/CONSTITUTION.md",
        "anti_abuse": "docs/ANTI-ABUSE.md",
        "readme": "governance/safe/README.md",
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


def make_repo(tmp, space, safe):
    """Создаёт мини-репо: доки + два конфига управления."""
    for rel in GOOD_DOCS:
        full = os.path.join(tmp, rel)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w", encoding="utf-8") as fh:
            fh.write("# stub\n")
    for rel, data in (
        ("governance/snapshot/space.json", space),
        ("governance/safe/safe.config.json", safe),
    ):
        full = os.path.join(tmp, rel)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=2)


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


def scenario(title, space, safe, expect_green, expect_fail_key=None):
    print(f"\n[{title}]")
    tmp = tempfile.mkdtemp(prefix="gov-test-")
    try:
        make_repo(tmp, space, safe)
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


def space_mut(fn):
    """Глубокая копия корректного space с применённой мутацией fn(space)."""
    s = copy.deepcopy(GOOD_SPACE)
    fn(s)
    return s


def safe_mut(fn):
    s = copy.deepcopy(GOOD_SAFE)
    fn(s)
    return s


def set_type(space, key, **kv):
    for pt in space["proposal_types"]:
        if pt["key"] == key:
            pt.update(kv)


def main():
    print("ТЕСТ-ИНВАРИАНТ GOVERNANCE — доказываем, что красное ловится, зелёное не ложно-падает")

    # 1. Корректные конфиги управления → зелёно.
    scenario("корректные конфиги управления", GOOD_SPACE, GOOD_SAFE, expect_green=True)

    # 2. Плутократическая стратегия (вес по балансу) → one-person-one-vote красный.
    def plutocracy(s):
        s["settings"]["strategies"] = [
            {"name": "erc20-balance-of", "params": {"address": "0x0", "decimals": 18}}
        ]
    scenario("вес голоса по балансу токена", space_mut(plutocracy), GOOD_SAFE,
             expect_green=False, expect_fail_key="one-person-one-vote")

    # 3. ticket с value != 1 → one-person-one-vote красный.
    def weighted_ticket(s):
        s["settings"]["strategies"][0]["params"]["value"] = 5
    scenario("ticket value=5 (неравный вес)", space_mut(weighted_ticket), GOOD_SAFE,
             expect_green=False, expect_fail_key="one-person-one-vote")

    # 4. Плутократия, спрятанная в validation.params.strategies → ловится.
    def plutocracy_validation(s):
        s["settings"]["validation"]["params"]["strategies"] = [
            {"name": "erc721", "params": {}}
        ]
    scenario("плутократия в validation", space_mut(plutocracy_validation), GOOD_SAFE,
             expect_green=False, expect_fail_key="one-person-one-vote")

    # 5. Нулевой срок голосования → timed-vote красный.
    def zero_period(s):
        s["settings"]["voting"]["period"] = 0
    scenario("period=0 (нет срока)", space_mut(zero_period), GOOD_SAFE,
             expect_green=False, expect_fail_key="timed-vote")

    # 6. off_chain_signaling=false → off-chain-signal красный.
    def not_offchain(s):
        s["off_chain_signaling"] = False
    scenario("off_chain_signaling=false", space_mut(not_offchain), GOOD_SAFE,
             expect_green=False, expect_fail_key="off-chain-signal")

    # 7. Тип предложения «исполняет сам» (binding=true) → off-chain-signal красный.
    def binding_type(s):
        set_type(s, "signal", binding=True)
    scenario("тип binding=true (исполняет сам)", space_mut(binding_type), GOOD_SAFE,
             expect_green=False, expect_fail_key="off-chain-signal")

    # 8. disbursement-direction без привязки к ANTI-ABUSE → proposal-binding красный.
    def unbound_disbursement(s):
        set_type(s, "disbursement-direction", links=["docs/PRIORITIES.md"])
    scenario("распределение без ANTI-ABUSE", space_mut(unbound_disbursement), GOOD_SAFE,
             expect_green=False, expect_fail_key="proposal-binding")

    # 9. Поправка к конституции без супербольшинства → proposal-binding красный.
    def no_supermajority(s):
        set_type(s, "constitution-amendment", requires_supermajority=False)
    scenario("поправка без супербольшинства", space_mut(no_supermajority), GOOD_SAFE,
             expect_green=False, expect_fail_key="proposal-binding")

    # 10. Нет типа constitution-amendment вовсе → proposal-binding красный.
    def drop_amendment(s):
        s["proposal_types"] = [pt for pt in s["proposal_types"]
                               if pt["key"] != "constitution-amendment"]
    scenario("нет типа constitution-amendment", space_mut(drop_amendment), GOOD_SAFE,
             expect_green=False, expect_fail_key="proposal-binding")

    # 11. Единоличный порог мультисига (threshold=1) → multisig-not-sole красный.
    def sole(s):
        s["safe"]["threshold"] = 1
    scenario("threshold=1 (единоличная власть)", GOOD_SPACE, safe_mut(sole),
             expect_green=False, expect_fail_key="multisig-not-sole")

    # 12. Порог = числу владельцев (единогласие/вето) → multisig-not-sole красный.
    def unanimity(s):
        s["safe"]["threshold"] = 5
    scenario("threshold=owners (единогласие)", GOOD_SPACE, safe_mut(unanimity),
             expect_green=False, expect_fail_key="multisig-not-sole")

    # 13. Битая doc-ссылка в конфиге → lifecycle-links красный.
    def broken_link(s):
        s["links"]["constitution"] = "docs/NOPE.md"
    scenario("битая doc-ссылка конфига", space_mut(broken_link), GOOD_SAFE,
             expect_green=False, expect_fail_key="lifecycle-links")

    # 14. Отсутствует сам space.json (агент не должен «зеленеть по умолчанию»).
    print("\n[нет space.json вовсе]")
    tmp = tempfile.mkdtemp(prefix="gov-test-")
    try:
        make_repo(tmp, GOOD_SPACE, GOOD_SAFE)
        os.remove(os.path.join(tmp, "governance/snapshot/space.json"))
        code, report = run_agent(tmp)
        check("вердикт red / exit=1", report.get("verdict") == "red" and code == 1)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print(f"\nИТОГ: {PASSED} прошли, {FAILED} провалились")
    return 0 if FAILED == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
