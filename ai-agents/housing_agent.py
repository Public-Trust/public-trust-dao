#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Housing AI-агент — Public Trust DAO (Этап 6, модуль 5/8).

СЛУЖЕБНЫЙ МОДУЛЬ, НЕ ОРГАН ВЛАСТИ (Конституция, ст. 9).
Агент НИЧЕГО не двигает и ничем не владеет: он только ПРОВЕРЯЕТ, что жилищная
помощь устроена по модели целевого расхода — «помощь не выдаётся на руки, она
оплачивается напрямую поставщику услуги (арендодателю)» — и докладывает
«зелёно/красно». Вся власть — у голосования сообщества и Safe-мультисига; ИИ лишь
помогает соблюдать конституцию (ст. 9).

Профильный помощник по жилищным кейсам. Нормативная основа —
docs/ESCROW-TARGETED-DISBURSEMENT.md (производный от CONSTITUTION ст. 3/4/5/7,
PRIORITIES.md «жильё = уровень 2», ANTI-ABUSE.md).

Read-only статический разбор делится на две части.

A. Контракт целевого escrow (contracts/contracts/Disbursement.sol) —
   доказываем, что модель «оплачиваем напрямую поставщику» заложена В КОД:

  • release-to-provider-only → release(id, amount) НЕ принимает адрес получателя;
                               транш уходит строго на c.provider кейса .... ст. 5
  • provider-fixed           → адрес поставщика фиксируется в open и не
                               переназначается (нет setProvider/.provider=) . ст. 5
  • refund-to-treasury       → refund возвращает остаток В КАЗНУ, не
                               получателю (услуга не оказана → не потеряно) . ст. 7
  • tranche-limit            → потолок одного транша maxRelease в release
                               (поэтапные выплаты/лимиты) .......... ANTI-ABUSE §1–§2
  • guardian-cannot-move     → денежные ветви только у executor; guardian
                               (пауза) средства не двигает («безопасность ≠
                               власть») ..................................... ст. 2/9

B. Записи реестра жилищных выплат (category == "housing"):

  • targeted-escrow      → у жилищной записи есть provider + escrow_id
                           (привязка к on-chain escrow, не «наличка на руки») . ст. 3/5
  • provider-onchain     → provider — валидный ненулевой on-chain адрес ....... ст. 5
  • category-priority    → у category=housing уровень = «housing_loss» из
                           PRIORITIES.md (приоритет по характеру нужды) ........ ст. 5

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

DISBURSEMENT_SOL = os.path.join("contracts", "contracts", "Disbursement.sol")
PRIORITIES_MD = os.path.join("docs", "PRIORITIES.md")
REGISTRY_DIR = os.path.join("governance", "registry")

# Категория целевого расхода, за которую отвечает этот профильный агент.
HOUSING_CATEGORY = "housing"
# Ключ приоритета жилья в PRIORITIES.md (содержит "housing"); уровень читается из
# документа, а не зашит в код — так код и норматив доказуемо не расходятся.
HOUSING_PRIORITY_MARKER = "housing"

# Денежные операции Solidity: их не должно быть в ветвях паузы guardian.
FUND_MOVE_PATTERNS = (
    (r"\.transfer\s*\(", ".transfer("),
    (r"\.send\s*\(", ".send("),
    (r"\.call\s*\{", ".call{value...}"),
    (r"\bselfdestruct\s*\(", "selfdestruct"),
)

# Валидный 20-байтовый адрес и нулевой адрес (получатель не может быть нулём).
ADDR_RE = re.compile(r"^0x[0-9a-fA-F]{40}$")
ZERO_ADDR = "0x" + "0" * 40


def strip_solidity_comments(src):
    """Убирает // и /* */ комментарии, чтобы не ловить упоминания в пояснениях."""
    src = re.sub(r"/\*.*?\*/", " ", src, flags=re.DOTALL)
    src = re.sub(r"//[^\n]*", " ", src)
    return src


def _function_sig(code, fn):
    """Сигнатура функции fn (между именем и '{'): модификаторы + параметры, или None."""
    m = re.search(
        r"\bfunction\s+" + re.escape(fn) + r"\s*\(([^)]*)\)([^{;]*)\{",
        code, flags=re.DOTALL,
    )
    if not m:
        return None
    return {"params": m.group(1), "modifiers": m.group(2)}


def _function_body(code, fn):
    """Тело функции fn по балансу фигурных скобок (или None)."""
    m = re.search(r"\bfunction\s+" + re.escape(fn) + r"\s*\([^)]*\)[^{;]*\{", code)
    if not m:
        return None
    i = m.end()
    depth = 1
    while i < len(code) and depth:
        if code[i] == "{":
            depth += 1
        elif code[i] == "}":
            depth -= 1
        i += 1
    return code[m.end():i - 1]


def load_housing_priority_level(priorities_path):
    """Читает уровень приоритета жилья ПРЯМО из docs/PRIORITIES.md (по ключу housing*)."""
    with open(priorities_path, encoding="utf-8") as fh:
        text = fh.read()
    for block in re.findall(r"```json\s*(.*?)```", text, flags=re.DOTALL):
        if '"priorities"' in block:
            data = json.loads(block)
            for p in data["priorities"]:
                if HOUSING_PRIORITY_MARKER in str(p.get("key", "")).lower():
                    return int(p["level"])
            raise ValueError("в PRIORITIES.md нет приоритета с ключом *housing*")
    raise ValueError("в PRIORITIES.md не найден машиночитаемый блок priorities")


def load_housing_records(registry_dir):
    """Возвращает (id, payload) для записей type=disbursement с category=housing."""
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
        payload = record.get("payload", {})
        if payload.get("category") == HOUSING_CATEGORY:
            out.append((entry.get("id", rec_path), payload))
    return out


# ---- Проверки контракта (Part A). Каждая → (ok: bool, findings: list[str]). ----

def check_release_to_provider_only(code, _ctx):
    """release(id, amount) не принимает адрес получателя; транш идёт на c.provider."""
    findings = []
    sig = _function_sig(code, "release")
    body = _function_body(code, "release")
    if sig is None or body is None:
        return False, ["в Disbursement.sol не найдена функция release"]
    if re.search(r"\baddress\b", sig["params"]):
        findings.append(
            "release принимает параметр-адрес — получателя можно подменить "
            "(должны передаваться только id и сумма, адрес берётся из кейса)"
        )
    if not re.search(r"\bc\.provider\b\.call\s*\{\s*value", body) and \
       not re.search(r"\bc\.provider\.call\{value", body.replace(" ", "")):
        findings.append("release не отправляет транш на c.provider (целевой адрес кейса)")
    return (not findings), findings


def check_provider_fixed(code, _ctx):
    """Адрес поставщика фиксируется в open и не переназначается."""
    findings = []
    if re.search(r"\.provider\s*=", code):
        findings.append("есть переназначение .provider — адрес поставщика не фиксирован")
    if _function_sig(code, "setProvider") is not None:
        findings.append("найдена функция setProvider — поставщика можно сменить после open")
    # Поставщик действительно задаётся при открытии кейса.
    open_body = _function_body(code, "open")
    if open_body is None:
        findings.append("не найдена функция open (где фиксируется поставщик)")
    elif "provider" not in open_body:
        findings.append("open не фиксирует provider в кейсе")
    return (not findings), findings


def check_refund_to_treasury(code, _ctx):
    """refund возвращает остаток в казну (treasury), а не получателю/поставщику."""
    findings = []
    body = _function_body(code, "refund")
    if body is None:
        return False, ["в Disbursement.sol не найдена функция refund"]
    compact = body.replace(" ", "")
    if "treasury.call{value" not in compact:
        findings.append("refund не возвращает средства на treasury (.call{value} на казну)")
    if "provider.call{value" in compact:
        findings.append("refund отправляет средства поставщику — возврат должен идти В КАЗНУ")
    return (not findings), findings


def check_tranche_limit(code, _ctx):
    """release ограничивает один транш потолком maxRelease (поэтапность/лимиты)."""
    findings = []
    body = _function_body(code, "release")
    if body is None:
        return False, ["в Disbursement.sol не найдена функция release"]
    if "maxRelease" not in body:
        findings.append("release не сверяется с maxRelease (нет потолка транша)")
    elif not re.search(r"<=\s*maxRelease", body):
        findings.append("release не ограничивает сумму потолком (нет «amount <= maxRelease»)")
    return (not findings), findings


def check_guardian_cannot_move(code, _ctx):
    """Денежные ветви — только executor; guardian (пауза) средства не двигает."""
    findings = []
    # Денежные функции обязаны быть onlyExecutor и НЕ onlyGuardian.
    for fn in ("open", "release", "refund"):
        sig = _function_sig(code, fn)
        if sig is None:
            findings.append(f"не найдена функция {fn}")
            continue
        if "onlyExecutor" not in sig["modifiers"]:
            findings.append(f"{fn} не помечена onlyExecutor (двигать средства может не только исполнитель)")
        if "onlyGuardian" in sig["modifiers"]:
            findings.append(f"{fn} помечена onlyGuardian — guardian получил бы власть над средствами")
    # Ветви паузы — только onlyGuardian и без движения средств.
    for fn in ("pause", "unpause"):
        sig = _function_sig(code, fn)
        body = _function_body(code, fn)
        if sig is None or body is None:
            findings.append(f"не найдена функция {fn}")
            continue
        if "onlyGuardian" not in sig["modifiers"]:
            findings.append(f"{fn} не помечена onlyGuardian")
        for pattern, human in FUND_MOVE_PATTERNS:
            if re.search(pattern, body):
                findings.append(f"{fn} двигает средства ({human}) — пауза не должна распоряжаться казной")
    return (not findings), findings


# ---- Проверки записей реестра (Part B). Каждая → (ok, findings). ----

def check_targeted_escrow(records, _level):
    """У каждой жилищной записи есть provider и escrow_id (привязка к on-chain escrow)."""
    findings = []
    for rid, payload in records:
        if not payload.get("provider"):
            findings.append(f"{rid}: нет поля provider (жильё оплачивается напрямую поставщику)")
        if not isinstance(payload.get("escrow_id"), int):
            findings.append(f"{rid}: нет escrow_id (нет привязки к on-chain целевому escrow)")
    return (not findings), findings


def check_provider_onchain(records, _level):
    """provider — валидный ненулевой 20-байтовый адрес."""
    findings = []
    for rid, payload in records:
        provider = payload.get("provider")
        if provider is None:
            continue  # пустой provider ловит targeted-escrow
        if not isinstance(provider, str) or not ADDR_RE.match(provider):
            findings.append(f"{rid}: provider={provider!r} — не валидный on-chain адрес (0x + 40 hex)")
        elif provider.lower() == ZERO_ADDR:
            findings.append(f"{rid}: provider — нулевой адрес (средства ушли бы в никуда)")
    return (not findings), findings


def check_category_priority(records, level):
    """У category=housing уровень приоритета = «housing_loss» из PRIORITIES.md."""
    findings = []
    if level is None:
        return False, ["не удалось прочитать уровень приоритета жилья из PRIORITIES.md"]
    for rid, payload in records:
        lvl = payload.get("priority_level")
        if lvl != level:
            findings.append(
                f"{rid}: category=housing, но priority_level={lvl!r} (ожидается {level} "
                "= «housing_loss» из PRIORITIES.md; приоритет по характеру нужды)"
            )
    return (not findings), findings


CONTRACT_CHECKS = [
    {
        "key": "release-to-provider-only",
        "title": "Транш уходит строго поставщику кейса (release без адреса-параметра)",
        "guards": "ст. 5 / ESCROW §2 — помощь оплачивается напрямую поставщику, не «на руки»",
        "fn": check_release_to_provider_only,
    },
    {
        "key": "provider-fixed",
        "title": "Адрес поставщика фиксируется в open и не переназначается",
        "guards": "ст. 5 / ESCROW §3 — единственный возможный получатель задан заранее",
        "fn": check_provider_fixed,
    },
    {
        "key": "refund-to-treasury",
        "title": "refund возвращает остаток в казну, а не получателю",
        "guards": "ст. 7 / ESCROW §2 — услуга не оказана → средства не теряются, идут в фонд",
        "fn": check_refund_to_treasury,
    },
    {
        "key": "tranche-limit",
        "title": "Потолок одного транша maxRelease (поэтапные выплаты)",
        "guards": "ANTI-ABUSE §1–§2 — крупное дробится на транши, лимит снижает риск",
        "fn": check_tranche_limit,
    },
    {
        "key": "guardian-cannot-move",
        "title": "Средства двигает только executor; guardian лишь ставит паузу",
        "guards": "ст. 2/9 — «безопасность ≠ власть»; никто не распоряжается казной единолично",
        "fn": check_guardian_cannot_move,
    },
]

RECORD_CHECKS = [
    {
        "key": "targeted-escrow",
        "title": "Жилищная запись привязана к целевому escrow (provider + escrow_id)",
        "guards": "ст. 3/5 / ESCROW §2 — оплата напрямую поставщику, видна в реестре",
        "fn": check_targeted_escrow,
    },
    {
        "key": "provider-onchain",
        "title": "provider — валидный ненулевой on-chain адрес",
        "guards": "ст. 5 / ESCROW §5 — публичен адрес получателя-поставщика, не личность",
        "fn": check_provider_onchain,
    },
    {
        "key": "category-priority",
        "title": "У category=housing уровень = «housing_loss» из PRIORITIES.md",
        "guards": "ст. 5 / PRIORITIES — приоритет по характеру нужды (жильё), а не по личности",
        "fn": check_category_priority,
    },
]


def _err_check(spec, message):
    return {
        "key": spec["key"],
        "title": spec["title"],
        "guards": spec["guards"],
        "status": "error",
        "findings": [message or "источник для проверки недоступен"],
    }


def run(root):
    """Прогоняет инварианты контракта и проверки жилищных записей. Возвращает report."""
    sol_path = os.path.join(root, DISBURSEMENT_SOL)
    priorities_path = os.path.join(root, PRIORITIES_MD)
    registry_dir = os.path.join(root, REGISTRY_DIR)

    code = None
    code_err = None
    try:
        with open(sol_path, encoding="utf-8") as fh:
            code = strip_solidity_comments(fh.read())
    except OSError as exc:
        code_err = f"не удалось прочитать {DISBURSEMENT_SOL}: {exc}"

    level = None
    level_err = None
    try:
        level = load_housing_priority_level(priorities_path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        level_err = f"не удалось прочитать приоритет жилья: {exc}"

    records = []
    records_err = None
    try:
        records = load_housing_records(registry_dir)
    except (OSError, KeyError, json.JSONDecodeError) as exc:
        records_err = f"не удалось прочитать реестр выплат: {exc}"

    checks = []

    # Part A — контракт.
    for spec in CONTRACT_CHECKS:
        if code is None:
            checks.append(_err_check(spec, code_err))
            continue
        ok, findings = spec["fn"](code, None)
        checks.append({
            "key": spec["key"], "title": spec["title"], "guards": spec["guards"],
            "status": "pass" if ok else "fail", "findings": findings,
        })

    # Part B — записи реестра.
    for spec in RECORD_CHECKS:
        if records_err is not None:
            checks.append(_err_check(spec, records_err))
            continue
        if spec["key"] == "category-priority" and level is None:
            checks.append(_err_check(spec, level_err))
            continue
        ok, findings = spec["fn"](records, level)
        checks.append({
            "key": spec["key"], "title": spec["title"], "guards": spec["guards"],
            "status": "pass" if ok else "fail", "findings": findings,
        })

    all_pass = all(c["status"] == "pass" for c in checks)
    passed = sum(1 for c in checks if c["status"] == "pass")
    return {
        "agent": "housing",
        "role": "служебный модуль, не орган власти (Конституция, ст. 9)",
        "verdict": "green" if all_pass else "red",
        "passed": passed,
        "total": len(checks),
        "housing_records_checked": len(records),
        "housing_priority_level": level,
        "checks": checks,
    }


def main(argv):
    parser = argparse.ArgumentParser(
        description="Housing AI-агент Public Trust DAO: целевой escrow жилищной помощи."
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
    print("HOUSING AI-АГЕНТ — Public Trust DAO")
    print("Служебный модуль (ст. 9): проверяет целевой escrow жилья, не правит. Ничего не двигает.")
    print("=" * 70)
    print("Главный принцип: помощь не выдаётся на руки — она оплачивается напрямую поставщику.")
    print(f"Проверено жилищных записей (category=housing): {report['housing_records_checked']}")
    if report["housing_priority_level"] is not None:
        print(f"Приоритет жилья из PRIORITIES.md (housing_loss): {report['housing_priority_level']}")
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
        print("Housing нашёл отклонение от модели целевого расхода. Это сигнал сообществу,")
        print("а не действие: агент не исправляет и не распоряжается — решает голосование.")
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
