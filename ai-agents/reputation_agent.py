#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Reputation AI-агент — Public Trust DAO (Этап 6, модуль 4/8).

СЛУЖЕБНЫЙ МОДУЛЬ, НЕ ОРГАН ВЛАСТИ (Конституция, ст. 9).
Агент НИЧЕГО не двигает и ничем не владеет: он только ПРОВЕРЯЕТ, что модель
«один человек — один голос» сохранена В КОДЕ и в настройках голосования, и
докладывает «зелёно/красно». Вся власть — у голосования сообщества; ИИ лишь
помогает соблюдать конституцию (ст. 9).

Что делает: read-only статический разбор ончейн-контракта репутации
(`contracts/contracts/Reputation.sol`) и офчейн-настроек Snapshot
(`governance/snapshot/space.json`). Проверяет инварианты «1 человек = 1 голос»
по docs/GOVERNANCE.md §2–§3:

  • soulbound        → у бейджа нет функций перевода (голос не продать) .... ст. 2 §2
  • bounded-weight   → вес = 0 / 1 + min(points, cap), коридор [1..1+cap] ... ст. 2 §2
  • no-funds         → слой репутации не двигает средства («уникальность ≠
                       власть») ............................................. ст. 9 §3
  • roles-separated  → verifier только выдаёт/отзывает бейдж, governor только
                       правит параметры; ни одна роль не двигает казну ...... §3
  • off-chain-equal  → стратегия Snapshot = равный «ticket» value=1, НЕ
                       плутократия по балансу токена; допуск только участников. §2 §4

Почему так: «1 человек = 1 голос» — это конституционный запрет №5 «власть денег»
(ст. 2). Если бы бейдж можно было передать/купить или вес зависел от баланса —
возник бы рынок голосов и плутократия. Агент доказывает, что это невозможно
ПО ПОСТРОЕНИЮ (нет функций перевода, вес жёстко ограничен потолком, стратегия
голоса равная), а не «на словах в документации».

Вывод:
  • человекочитаемый отчёт в stdout (✓/✗ по каждой проверке + привязка к статье);
  • при --json — машиночитаемый отчёт (для CI и других агентов, в т.ч. Audit);
  • код возврата 0, если все инварианты целы, иначе 1.

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

REPUTATION_SOL = os.path.join("contracts", "contracts", "Reputation.sol")
SNAPSHOT_SPACE = os.path.join("governance", "snapshot", "space.json")

# Функции перевода ERC-20/721/1155: их НЕ должно быть у soulbound-бейджа —
# иначе голос можно продать/подарить/скупить (GOVERNANCE.md §2 «НЕ продаваемое право»).
TRANSFER_FUNCS = (
    "transfer", "transferFrom", "safeTransferFrom", "approve",
    "setApprovalForAll", "permit",
)

# Признаки движения средств: их НЕ должно быть в слое репутации — он лишь
# подтверждает уникальность, но не распоряжается казной (GOVERNANCE.md §3).
FUND_MOVE_PATTERNS = (
    (r"\bpayable\b", "payable (приём/перевод эфира)"),
    (r"\.transfer\s*\(", ".transfer( (перевод средств)"),
    (r"\.send\s*\(", ".send( (перевод средств)"),
    (r"\.call\s*\{", ".call{value...} (низкоуровневый перевод)"),
    (r"\bselfdestruct\s*\(", "selfdestruct (вывод баланса)"),
    (r"address\s*\(\s*this\s*\)\s*\.balance", "address(this).balance (учёт казны)"),
    (r"\bmsg\.value\b", "msg.value (приём эфира)"),
)

# Плутократические стратегии Snapshot: вес голоса по балансу токена/монеты.
# Их допуск превратил бы фонд во «власть денег» (ст. 2). Список синхронен
# с scripts/snapshot_config.py.
PLUTOCRATIC_STRATEGIES = {
    "erc20-balance-of", "erc20-votes", "erc20-with-balance", "balance-of",
    "erc721", "erc721-with-multiplier", "erc1155-balance-of",
    "delegation", "erc20-balance-of-delegation", "multichain",
    "comp-like-votes", "uni",
}
# Равновесные стратегии: ровно 1 голос на допущенный адрес, независимо от баланса.
EQUAL_STRATEGIES = {"ticket", "one-person-one-vote"}


def strip_solidity_comments(src):
    """Убирает // и /* */ комментарии — чтобы не ловить упоминания в тексте.

    Например, в Reputation.sol есть комментарий «У контракта НЕТ функций
    transfer/approve/transferFrom» — без вырезания комментариев проверка
    soulbound ложно бы краснела на собственном пояснении.
    """
    # Блочные комментарии.
    src = re.sub(r"/\*.*?\*/", " ", src, flags=re.DOTALL)
    # Строчные комментарии.
    src = re.sub(r"//[^\n]*", " ", src)
    return src


# ---- Проверки. Каждая возвращает (ok: bool, findings: list[str]). ----

def check_soulbound(code, _space):
    """1. У бейджа нет ни одной функции перевода (голос непередаваем)."""
    findings = []
    for fn in TRANSFER_FUNCS:
        # Объявление функции: function <name> ( ... — только как имя функции.
        if re.search(r"\bfunction\s+" + re.escape(fn) + r"\s*\(", code):
            findings.append(
                f"найдена функция перевода '{fn}' — бейдж стал бы передаваемым "
                "(голос можно было бы продать/скупить)"
            )
    return (not findings), findings


def _function_body(code, fn):
    """Возвращает тело функции fn по балансу фигурных скобок (или None).

    Регуляркой `.*?` тело не вырезать: первая же внутренняя `}` (конец `if`)
    оборвала бы захват. Поэтому считаем скобки от открывающей `{`.
    """
    m = re.search(r"\bfunction\s+" + re.escape(fn) + r"\s*\([^)]*\)[^{;]*\{", code)
    if not m:
        return None
    i = m.end()  # позиция сразу после открывающей `{`
    depth = 1
    while i < len(code) and depth:
        if code[i] == "{":
            depth += 1
        elif code[i] == "}":
            depth -= 1
        i += 1
    return code[m.end():i - 1]


def check_bounded_weight(code, _space):
    """2. votingUnits даёт вес в коридоре [1..1+cap]; не участник → 0."""
    findings = []
    body = _function_body(code, "votingUnits")
    if body is None:
        return False, ["в Reputation.sol не найдена функция votingUnits"]
    if "return 0" not in body.replace(" ", "") and "return0" not in body.replace(" ", ""):
        findings.append("votingUnits не возвращает 0 для не-участника (нет «return 0»)")
    if "reputationCap" not in body:
        findings.append("votingUnits не ограничивает бонус потолком reputationCap")
    # База голоса = ровно 1 (плюс ограниченный бонус). Ищем «1 +» / «1+».
    if not re.search(r"\breturn\s+1\s*\+", body):
        findings.append("votingUnits не строит вес как «1 + бонус» (базовый голос ≠ 1)")
    # Бонус должен клампиться к потолку (bonus > cap → bonus = cap).
    if not re.search(r">\s*reputationCap", body):
        findings.append("votingUnits не зажимает бонус к потолку (нет «> reputationCap»)")
    return (not findings), findings


def check_no_funds(code, _space):
    """3. Слой репутации не двигает средства («уникальность ≠ власть»)."""
    findings = []
    for pattern, human in FUND_MOVE_PATTERNS:
        if re.search(pattern, code):
            findings.append(f"в контракте репутации есть движение средств: {human}")
    return (not findings), findings


def _modifier_on(code, fn):
    """Возвращает текст сигнатуры функции fn (от 'function' до '{') или None."""
    m = re.search(
        r"\bfunction\s+" + re.escape(fn) + r"\s*\([^)]*\)([^{;]*)\{",
        code, flags=re.DOTALL,
    )
    return m.group(1) if m else None


def check_roles_separated(code, _space):
    """4. verifier выдаёт/отзывает бейдж; governor правит параметры; роли не смешаны."""
    findings = []
    # Оба модификатора должны существовать.
    if not re.search(r"\bmodifier\s+onlyVerifier\b", code):
        findings.append("нет модификатора onlyVerifier")
    if not re.search(r"\bmodifier\s+onlyGovernor\b", code):
        findings.append("нет модификатора onlyGovernor")
    # Выдача/отзыв уникальности — только verifier.
    for fn in ("mint", "revoke"):
        sig = _modifier_on(code, fn)
        if sig is None:
            findings.append(f"не найдена функция {fn}")
        elif "onlyVerifier" not in sig:
            findings.append(f"{fn} должна быть onlyVerifier (выдача/отзыв уникальности)")
    # Параметры/роли — только governor (голосованием), не verifier.
    for fn in ("setReputation", "setReputationCap", "setVerifier", "setGovernor"):
        sig = _modifier_on(code, fn)
        if sig is None:
            findings.append(f"не найдена функция {fn}")
        else:
            if "onlyGovernor" not in sig:
                findings.append(f"{fn} должна быть onlyGovernor (параметр управления)")
            if "onlyVerifier" in sig:
                findings.append(f"{fn} помечена onlyVerifier — смешение ролей (verifier правит параметры)")
    return (not findings), findings


def _iter_strategies(settings):
    """Все стратегии из settings.strategies и validation.params.strategies."""
    out = list(settings.get("strategies", []) or [])
    val = settings.get("validation", {}) or {}
    out.extend((val.get("params", {}) or {}).get("strategies", []) or [])
    return out


def check_off_chain_equal(_code, space):
    """5. Snapshot голосует равным «ticket value=1», не плутократией; допуск участникам."""
    findings = []
    if space is None:
        return False, ["не удалось прочитать governance/snapshot/space.json"]
    settings = space.get("settings", {}) or {}
    strategies = _iter_strategies(settings)
    if not strategies:
        findings.append("в space.json не задано ни одной стратегии голосования")
    for st in strategies:
        name = str(st.get("name", "")).lower()
        if name in PLUTOCRATIC_STRATEGIES:
            findings.append(f"плутократическая стратегия '{name}' — вес по балансу токена (запрет ст. 2)")
        elif name in EQUAL_STRATEGIES:
            value = (st.get("params", {}) or {}).get("value")
            if value != 1:
                findings.append(f"равновесная стратегия '{name}' с value={value!r} (ожидается 1 — «1 человек = 1 голос»)")
        else:
            findings.append(f"неизвестная стратегия '{name}' — не доказана равновесность голоса")
    # Голосуют только верифицированные участники (иначе атака Сивиллы = власть).
    if (settings.get("filters", {}) or {}).get("onlyMembers") is not True:
        findings.append("filters.onlyMembers != true — голосовать смогут не только верифицированные участники")
    return (not findings), findings


CHECKS = [
    {
        "key": "soulbound",
        "title": "Бейдж непередаваем (нет функций перевода) — голос не продать",
        "guards": "ст. 2 / GOVERNANCE §2 — право голоса не продаётся и не скупается",
        "needs": "sol",
        "fn": check_soulbound,
    },
    {
        "key": "bounded-weight",
        "title": "Вес голоса в коридоре [1..1+cap]; не участник → 0",
        "guards": "ст. 2 / GOVERNANCE §2 — «1 человек = 1 голос», власть денег невозможна (запрет №5)",
        "needs": "sol",
        "fn": check_bounded_weight,
    },
    {
        "key": "no-funds",
        "title": "Слой репутации не двигает средства",
        "guards": "ст. 9 / GOVERNANCE §3 — «уникальность ≠ власть»; ИИ/роли не распоряжаются казной",
        "needs": "sol",
        "fn": check_no_funds,
    },
    {
        "key": "roles-separated",
        "title": "verifier подтверждает уникальность, governor правит параметры (роли не смешаны)",
        "guards": "GOVERNANCE §3 — кто подтверждает человека, тот не правит управление, и наоборот",
        "needs": "sol",
        "fn": check_roles_separated,
    },
    {
        "key": "off-chain-equal",
        "title": "Snapshot голосует равным «ticket» value=1 (не плутократия), допуск только участникам",
        "guards": "ст. 2 / GOVERNANCE §2,§4 — офчейн-сигнал тоже «1 человек = 1 голос»",
        "needs": "space",
        "fn": check_off_chain_equal,
    },
]


def run(root):
    """Прогоняет все инварианты. Возвращает report dict."""
    sol_path = os.path.join(root, REPUTATION_SOL)
    space_path = os.path.join(root, SNAPSHOT_SPACE)

    code = None
    code_err = None
    try:
        with open(sol_path, encoding="utf-8") as fh:
            code = strip_solidity_comments(fh.read())
    except OSError as exc:
        code_err = f"не удалось прочитать {REPUTATION_SOL}: {exc}"

    space = None
    space_err = None
    try:
        with open(space_path, encoding="utf-8") as fh:
            space = json.load(fh)
    except (OSError, json.JSONDecodeError) as exc:
        space_err = f"не удалось прочитать {SNAPSHOT_SPACE}: {exc}"

    checks = []
    for spec in CHECKS:
        if spec["needs"] == "sol" and code is None:
            checks.append(_err_check(spec, code_err))
            continue
        if spec["needs"] == "space" and space is None:
            checks.append(_err_check(spec, space_err))
            continue
        ok, findings = spec["fn"](code, space)
        checks.append({
            "key": spec["key"],
            "title": spec["title"],
            "guards": spec["guards"],
            "status": "pass" if ok else "fail",
            "findings": findings,
        })

    all_pass = all(c["status"] == "pass" for c in checks)
    passed = sum(1 for c in checks if c["status"] == "pass")
    return {
        "agent": "reputation",
        "role": "служебный модуль, не орган власти (Конституция, ст. 9)",
        "verdict": "green" if all_pass else "red",
        "passed": passed,
        "total": len(checks),
        "checks": checks,
    }


def _err_check(spec, message):
    return {
        "key": spec["key"],
        "title": spec["title"],
        "guards": spec["guards"],
        "status": "error",
        "findings": [message or "источник для проверки недоступен"],
    }


def main(argv):
    parser = argparse.ArgumentParser(
        description="Reputation AI-агент Public Trust DAO: проверка модели «1 человек = 1 голос»."
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
    print("REPUTATION AI-АГЕНТ — Public Trust DAO")
    print("Служебный модуль (ст. 9): проверяет «1 человек = 1 голос», не правит. Ничего не двигает.")
    print("=" * 70)
    for c in report["checks"]:
        mark = {"pass": "✓", "fail": "✗", "error": "⚠"}[c["status"]]
        print(f"\n{mark} [{c['key']}] {c['title']}")
        print(f"    защищает: {c['guards']}")
        for fnd in c["findings"]:
            print(f"    | {fnd}")
    print("\n" + "-" * 70)
    verdict = "ЗЕЛЁНО ✓" if all_pass else "КРАСНО ✗"
    print(f"ИТОГ: {verdict}  ({report['passed']}/{report['total']} инвариантов целы)")
    print("-" * 70)
    if not all_pass:
        print("Reputation нашёл угрозу модели «1 человек = 1 голос». Это сигнал сообществу,")
        print("а не действие: агент не исправляет и не распоряжается — решает голосование.")
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
