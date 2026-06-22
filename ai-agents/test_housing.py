#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест-инвариант для Housing-агента — Public Trust DAO.

Доказывает, что Housing РАБОТАЕТ (а не «зелёный по умолчанию»): на КАЖДОЕ
отклонение от модели целевого расхода жилья он обязан вернуть «красно» (exit=1),
а на корректных контракте+нормативе+записях — «зелёно» (exit=0), без ложных
срабатываний.

Метод: строим временный «мини-репозиторий» (contracts/contracts/Disbursement.sol +
docs/PRIORITIES.md + governance/registry/) и подсовываем то корректные, то
«отравленные» версии контракта/записей; запускаем агент через --root и проверяем
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
AGENT = os.path.join(HERE, "housing_agent.py")

PASSED = 0
FAILED = 0

# Корректный мини-контракт целевого escrow: транш только поставщику кейса,
# поставщик фиксирован, refund в казну, потолок транша, guardian только ставит
# паузу. Комментарий с «provider» — чтобы заодно проверить вырезание комментариев.
GOOD_SOL = """// SPDX-License-Identifier: AGPL-3.0-or-later
pragma solidity 0.8.24;

/// @notice Целевой escrow: release уходит ТОЛЬКО на provider кейса.
contract Disbursement {
    address public executor;
    address public guardian;
    address payable public treasury;
    uint256 public maxRelease;
    bool public paused;

    struct Case { address payable provider; uint256 amount; uint256 released; }
    mapping(uint256 => Case) public cases;
    uint256 public caseCount;

    modifier onlyExecutor() { require(msg.sender == executor, "x"); _; }
    modifier onlyGuardian() { require(msg.sender == guardian, "g"); _; }
    modifier whenNotPaused() { require(!paused, "p"); _; }

    function open(bytes32 caseId, uint8 priorityLevel, address payable provider, uint256 amount, bytes32 registryRef)
        external onlyExecutor whenNotPaused returns (uint256 id)
    {
        id = ++caseCount;
        cases[id] = Case({ provider: provider, amount: amount, released: 0 });
    }

    function release(uint256 id, uint256 amount) external onlyExecutor whenNotPaused {
        Case storage c = cases[id];
        require(amount <= maxRelease, "lim");
        c.released += amount;
        (bool ok, ) = c.provider.call{value: amount}("");
        require(ok, "t");
    }

    function refund(uint256 id) external onlyExecutor {
        Case storage c = cases[id];
        uint256 remaining = c.amount - c.released;
        (bool ok, ) = treasury.call{value: remaining}("");
        require(ok, "r");
    }

    function pause() external onlyGuardian { paused = true; }
    function unpause() external onlyGuardian { paused = false; }
}
"""

# Минимальный машиночитаемый блок приоритетов — housing_loss = уровень 2.
GOOD_PRIORITIES = """# PRIORITIES (тест)

```json
{
  "priorities": [
    { "level": 1, "key": "life_threat",  "label": "Угроза жизни" },
    { "level": 2, "key": "housing_loss", "label": "Угроза потери жилья" },
    { "level": 3, "key": "medical",      "label": "Медицинская помощь" }
  ]
}
```
"""

# Корректная жилищная запись — должна давать «зелёно».
GOOD_RECORD = {
    "case_id": "TEST-HOUSING-0001",
    "priority_level": 2,
    "category": "housing",
    "provider": "0x" + "a" * 40,
    "escrow_id": 1,
    "amount": "100.00",
    "asset": "TEST-MATIC",
    "network": "polygon-amoy",
}


def check(name, cond):
    global PASSED, FAILED
    if cond:
        PASSED += 1
        print(f"  ✓ {name}")
    else:
        FAILED += 1
        print(f"  ✗ {name}")


def make_repo(tmp, sol, priorities_md, records):
    """Создаёт контракт, PRIORITIES.md и реестр с жилищными записями из records."""
    os.makedirs(os.path.join(tmp, "contracts", "contracts"))
    with open(os.path.join(tmp, "contracts", "contracts", "Disbursement.sol"), "w", encoding="utf-8") as fh:
        fh.write(sol)
    os.makedirs(os.path.join(tmp, "docs"))
    with open(os.path.join(tmp, "docs", "PRIORITIES.md"), "w", encoding="utf-8") as fh:
        fh.write(priorities_md)
    reg = os.path.join(tmp, "governance", "registry", "records")
    os.makedirs(reg)
    entries = []
    for i, payload in enumerate(records):
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


def scenario(title, sol, records, expect_green, expect_fail_key=None,
             priorities_md=GOOD_PRIORITIES):
    print(f"\n[{title}]")
    tmp = tempfile.mkdtemp(prefix="housing-test-")
    try:
        make_repo(tmp, sol, priorities_md, records)
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


def rec(**changes):
    """Копия GOOD_RECORD с заменами/удалениями (значение None удаляет ключ)."""
    p = copy.deepcopy(GOOD_RECORD)
    for k, v in changes.items():
        if v is None:
            p.pop(k, None)
        else:
            p[k] = v
    return p


def main():
    print("ТЕСТ-ИНВАРИАНТ HOUSING — доказываем, что красное ловится, зелёное не ложно-падает")

    # 1. Корректные контракт + запись → зелёно.
    scenario("корректный контракт + жилищная запись", GOOD_SOL, [rec()], expect_green=True)

    # --- Part A: инварианты контракта целевого escrow ---

    # 2. release принимает адрес получателя → release-to-provider-only красный.
    bad = GOOD_SOL.replace(
        "function release(uint256 id, uint256 amount) external onlyExecutor whenNotPaused {\n"
        "        Case storage c = cases[id];\n"
        "        require(amount <= maxRelease, \"lim\");\n"
        "        c.released += amount;\n"
        "        (bool ok, ) = c.provider.call{value: amount}(\"\");",
        "function release(uint256 id, uint256 amount, address payable to) external onlyExecutor whenNotPaused {\n"
        "        Case storage c = cases[id];\n"
        "        require(amount <= maxRelease, \"lim\");\n"
        "        c.released += amount;\n"
        "        (bool ok, ) = to.call{value: amount}(\"\");",
    )
    scenario("release с адресом-параметром", bad, [rec()],
             expect_green=False, expect_fail_key="release-to-provider-only")

    # 3. Появился setProvider (.provider =) → provider-fixed красный.
    bad = GOOD_SOL.replace(
        "    function pause() external onlyGuardian { paused = true; }",
        "    function setProvider(uint256 id, address payable p) external onlyExecutor { cases[id].provider = p; }\n"
        "    function pause() external onlyGuardian { paused = true; }",
    )
    scenario("добавлен setProvider", bad, [rec()],
             expect_green=False, expect_fail_key="provider-fixed")

    # 4. refund шлёт поставщику, а не в казну → refund-to-treasury красный.
    bad = GOOD_SOL.replace(
        "        (bool ok, ) = treasury.call{value: remaining}(\"\");",
        "        (bool ok, ) = c.provider.call{value: remaining}(\"\");",
    )
    scenario("refund получателю вместо казны", bad, [rec()],
             expect_green=False, expect_fail_key="refund-to-treasury")

    # 5. Снят потолок транша → tranche-limit красный.
    bad = GOOD_SOL.replace('        require(amount <= maxRelease, "lim");\n', "")
    scenario("снят maxRelease в release", bad, [rec()],
             expect_green=False, expect_fail_key="tranche-limit")

    # 6. release стал onlyGuardian → guardian-cannot-move красный.
    bad = GOOD_SOL.replace(
        "function release(uint256 id, uint256 amount) external onlyExecutor whenNotPaused {",
        "function release(uint256 id, uint256 amount) external onlyGuardian whenNotPaused {",
    )
    scenario("release под guardian (власть над средствами)", bad, [rec()],
             expect_green=False, expect_fail_key="guardian-cannot-move")

    # --- Part B: проверки жилищных записей реестра ---

    # 7. Нет escrow_id → targeted-escrow красный.
    scenario("жилищная запись без escrow_id", GOOD_SOL, [rec(escrow_id=None)],
             expect_green=False, expect_fail_key="targeted-escrow")

    # 8. Битый адрес поставщика → provider-onchain красный.
    scenario("provider не валидный адрес", GOOD_SOL, [rec(provider="0xNOPE")],
             expect_green=False, expect_fail_key="provider-onchain")

    # 9. Нулевой адрес поставщика → provider-onchain красный.
    scenario("provider нулевой адрес", GOOD_SOL, [rec(provider="0x" + "0" * 40)],
             expect_green=False, expect_fail_key="provider-onchain")

    # 10. Неверный приоритет у housing → category-priority красный.
    scenario("category=housing, но priority_level=5", GOOD_SOL, [rec(priority_level=5)],
             expect_green=False, expect_fail_key="category-priority")

    # 11. Запись чужой категории (medical) → не трогаем (0 жилищных) → зелёно.
    non_housing = rec(category="medical", priority_level=3)
    scenario("не-жилищная запись игнорируется", GOOD_SOL, [non_housing], expect_green=True)

    # 12. Пустой реестр (нет жилищных записей) → зелёно, без ложного падения.
    print("\n[пустой реестр (нет жилищных записей)]")
    tmp = tempfile.mkdtemp(prefix="housing-test-")
    try:
        make_repo(tmp, GOOD_SOL, GOOD_PRIORITIES, [])
        code, report = run_agent(tmp)
        check("вердикт green / exit=0", report.get("verdict") == "green" and code == 0)
        check("проверено 0 жилищных записей", report.get("housing_records_checked") == 0)
        check("уровень приоритета жилья прочитан = 2", report.get("housing_priority_level") == 2)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print(f"\nИТОГ: {PASSED} прошли, {FAILED} провалились")
    return 0 if FAILED == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
