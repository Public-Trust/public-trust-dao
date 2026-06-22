#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест-инвариант для Reputation-агента — Public Trust DAO.

Доказывает, что Reputation РАБОТАЕТ (а не «зелёный по умолчанию»): на КАЖДУЮ
угрозу модели «1 человек = 1 голос» он обязан вернуть «красно» (exit=1), а на
корректных контракте+настройках — «зелёно» (exit=0), без ложных срабатываний.

Метод: строим временный «мини-репозиторий» (contracts/contracts/Reputation.sol +
governance/snapshot/space.json) и подсовываем то корректные, то «отравленные»
версии; запускаем агент через --root и проверяем вердикт по --json. Только
стандартная библиотека. Сети нет.
"""

import copy
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
AGENT = os.path.join(HERE, "reputation_agent.py")

PASSED = 0
FAILED = 0

# Корректный мини-контракт репутации: soulbound, вес [1..1+cap], роли разделены,
# средства не двигает. Содержит комментарий с «transfer/approve» — чтобы заодно
# проверить, что агент вырезает комментарии и не краснеет на пояснении.
GOOD_SOL = """// SPDX-License-Identifier: AGPL-3.0-or-later
pragma solidity 0.8.24;

/// @notice Soulbound: НЕТ функций transfer/approve/transferFrom by design.
contract Reputation {
    address public verifier;
    address public governor;
    uint256 public reputationCap;
    mapping(address => bool) public isMember;
    mapping(address => uint256) public reputationPoints;

    modifier onlyVerifier() { require(msg.sender == verifier, "v"); _; }
    modifier onlyGovernor() { require(msg.sender == governor, "g"); _; }

    function mint(address account, bytes32 ref) external onlyVerifier {
        isMember[account] = true;
    }
    function revoke(address account, bytes32 ref) external onlyVerifier {
        isMember[account] = false;
    }
    function setReputation(address account, uint256 points, bytes32 ref) external onlyGovernor {
        reputationPoints[account] = points;
    }
    function setReputationCap(uint256 next) external onlyGovernor {
        reputationCap = next;
    }
    function setVerifier(address next) external onlyGovernor { verifier = next; }
    function setGovernor(address next) external onlyGovernor { governor = next; }

    function votingUnits(address account) external view returns (uint256) {
        if (!isMember[account]) {
            return 0;
        }
        uint256 bonus = reputationPoints[account];
        if (bonus > reputationCap) {
            bonus = reputationCap;
        }
        return 1 + bonus;
    }
}
"""

# Корректные настройки Snapshot: равный «ticket» value=1, допуск только участникам.
GOOD_SPACE = {
    "settings": {
        "strategies": [
            {"name": "ticket", "network": "80002", "params": {"symbol": "VOICE", "value": 1}}
        ],
        "filters": {"onlyMembers": True, "minScore": 1},
        "validation": {
            "name": "basic",
            "params": {
                "strategies": [
                    {"name": "ticket", "network": "80002", "params": {"symbol": "VOICE", "value": 1}}
                ]
            },
        },
    }
}


def check(name, cond):
    global PASSED, FAILED
    if cond:
        PASSED += 1
        print(f"  ✓ {name}")
    else:
        FAILED += 1
        print(f"  ✗ {name}")


def make_repo(tmp, sol, space):
    """Создаёт contracts/contracts/Reputation.sol и governance/snapshot/space.json."""
    sol_dir = os.path.join(tmp, "contracts", "contracts")
    os.makedirs(sol_dir)
    with open(os.path.join(sol_dir, "Reputation.sol"), "w", encoding="utf-8") as fh:
        fh.write(sol)
    sp_dir = os.path.join(tmp, "governance", "snapshot")
    os.makedirs(sp_dir)
    with open(os.path.join(sp_dir, "space.json"), "w", encoding="utf-8") as fh:
        json.dump(space, fh, ensure_ascii=False)


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


def scenario(title, sol, space, expect_green, expect_fail_key=None):
    print(f"\n[{title}]")
    tmp = tempfile.mkdtemp(prefix="reputation-test-")
    try:
        make_repo(tmp, sol, space)
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


def space_with(**settings_changes):
    """Копия GOOD_SPACE с заменами в settings."""
    s = copy.deepcopy(GOOD_SPACE)
    s["settings"].update(settings_changes)
    return s


def main():
    print("ТЕСТ-ИНВАРИАНТ REPUTATION — доказываем, что красное ловится, зелёное не ложно-падает")

    # 1. Корректные контракт+настройки → зелёно (и комментарий с «transfer» не краснит).
    scenario("корректные контракт и настройки", GOOD_SOL, GOOD_SPACE, expect_green=True)

    # 2. Добавлена функция перевода → soulbound красный (голос стал бы товаром).
    transferable = GOOD_SOL.replace(
        "    function votingUnits",
        "    function transfer(address to, uint256 id) external { isMember[to] = true; }\n\n    function votingUnits",
    )
    scenario("добавлена function transfer", transferable, GOOD_SPACE,
             expect_green=False, expect_fail_key="soulbound")

    # 3. Вес без потолка (без клампа к cap) → bounded-weight красный.
    uncapped = GOOD_SOL.replace(
        """        uint256 bonus = reputationPoints[account];
        if (bonus > reputationCap) {
            bonus = reputationCap;
        }
        return 1 + bonus;""",
        "        return 1 + reputationPoints[account];",
    )
    scenario("вес без потолка reputationCap", uncapped, GOOD_SPACE,
             expect_green=False, expect_fail_key="bounded-weight")

    # 4. Вес по балансу (нет «return 0» для не-участника, база ≠ 1) → bounded-weight красный.
    balance_weight = GOOD_SOL.replace(
        """        if (!isMember[account]) {
            return 0;
        }
        uint256 bonus = reputationPoints[account];
        if (bonus > reputationCap) {
            bonus = reputationCap;
        }
        return 1 + bonus;""",
        "        return reputationPoints[account];",
    )
    scenario("вес = баланс репутации (плутократия)", balance_weight, GOOD_SPACE,
             expect_green=False, expect_fail_key="bounded-weight")

    # 5. Контракт двигает средства (payable + .transfer) → no-funds красный.
    moves_funds = GOOD_SOL.replace(
        "    function votingUnits",
        "    function withdraw(address payable to) external onlyGovernor { to.transfer(1); }\n\n    function votingUnits",
    )
    scenario("слой репутации двигает средства", moves_funds, GOOD_SPACE,
             expect_green=False, expect_fail_key="no-funds")

    # 6. Смешение ролей: verifier правит параметры → roles-separated красный.
    mixed_roles = GOOD_SOL.replace(
        "    function setReputationCap(uint256 next) external onlyGovernor {",
        "    function setReputationCap(uint256 next) external onlyVerifier {",
    )
    scenario("verifier правит параметры (смешение ролей)", mixed_roles, GOOD_SPACE,
             expect_green=False, expect_fail_key="roles-separated")

    # 7. Плутократическая стратегия Snapshot (вес по балансу токена) → off-chain-equal красный.
    pluto = copy.deepcopy(GOOD_SPACE)
    pluto["settings"]["strategies"] = [
        {"name": "erc20-balance-of", "network": "80002", "params": {"address": "0x0", "decimals": 18}}
    ]
    scenario("Snapshot: erc20-balance-of (плутократия)", GOOD_SOL, pluto,
             expect_green=False, expect_fail_key="off-chain-equal")

    # 8. ticket с value!=1 → off-chain-equal красный (не «1 человек = 1 голос»).
    weighted_ticket = copy.deepcopy(GOOD_SPACE)
    weighted_ticket["settings"]["strategies"] = [
        {"name": "ticket", "network": "80002", "params": {"symbol": "VOICE", "value": 5}}
    ]
    scenario("Snapshot: ticket value=5", GOOD_SOL, weighted_ticket,
             expect_green=False, expect_fail_key="off-chain-equal")

    # 9. Допуск не только участникам (onlyMembers=false) → off-chain-equal красный.
    open_vote = space_with(filters={"onlyMembers": False, "minScore": 0})
    scenario("Snapshot: onlyMembers=false", GOOD_SOL, open_vote,
             expect_green=False, expect_fail_key="off-chain-equal")

    print(f"\nИТОГ: {PASSED} прошли, {FAILED} провалились")
    return 0 if FAILED == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
