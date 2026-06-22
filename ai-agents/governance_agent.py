#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Governance AI-агент — Public Trust DAO (Этап 6, модуль 7/8).

СЛУЖЕБНЫЙ МОДУЛЬ, НЕ ОРГАН ВЛАСТИ (Конституция, ст. 9).
Агент НИКОГДА не голосует, ничего не вносит и ничем не распоряжается: он только
ПРОВЕРЯЕТ, что конфигурация управления (жизненный цикл предложения) построена по
конституции, и докладывает «зелёно/красно». Вся власть — у голосования
верифицированных людей и Safe-мультисига; ИИ лишь помогает соблюдать рельсы (ст. 9).

Зачем: курс управления (docs/GOVERNANCE.md) описывает жизненный цикл предложения
словами — «1 человек = 1 голос», ограниченный СРОК голосования, off-chain сигнал
вместо распоряжения средствами, привязка распределения к PRIORITIES/ANTI-ABUSE,
поправки к конституции под супербольшинство, исполнение через мультисиг «3-из-5»
(не единоличный владелец). Этот агент превращает эти правила в МАШИННУЮ проверку
конкретных артефактов управления (governance/snapshot/space.json,
governance/safe/safe.config.json), чтобы конфигурация не разъезжалась с
конституцией молча.

Что делает (read-only, по JSON-конфигам управления, без сети):

  A. Snapshot — жизненный цикл предложения (governance/snapshot/space.json)
     • one-person-one-vote → стратегия голоса = «ticket» value=1, без плутократии . ст. 2 / зпт №5
     • timed-vote         → задержка и срок голосования заданы и положительны ...... GOVERNANCE §7
     • off-chain-signal   → off_chain_signaling=true и все типы binding=false ........ ст. 4 / §5
     • proposal-binding   → типы про деньги/конституцию привязаны к нужным докам ... ст. 5 / §7–§8

  B. Исполнение — мультисиг (governance/safe/safe.config.json)
     • multisig-not-sole  → порог ≥2 и < числа владельцев (нет единоличной власти) . ст. 5 / §5

  C. Целостность (оба конфига)
     • lifecycle-links    → все doc-ссылки конфигов ведут к существующим файлам .... ст. 3

Вывод:
  • человекочитаемый отчёт в stdout (✓/✗ по каждой проверке + привязка к статье);
  • при --json — машиночитаемый отчёт (для CI и других агентов);
  • код возврата 0, если все проверки прошли, иначе 1.

«Красный» — это СИГНАЛ сообществу (повод для решения людей), а не действие: агент
сам ничего не правит и не голосует.

Зависимостей нет — только стандартная библиотека (детерминированно в любом CI).
TESTNET-ONLY: агент не трогает реальные средства/ключи и не выходит в сеть.
"""

import argparse
import json
import os
import sys

# Корень репозитория = на уровень выше каталога ai-agents/.
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SNAPSHOT_SPACE = "governance/snapshot/space.json"
SAFE_CONFIG = "governance/safe/safe.config.json"

# Допустимая стратегия голоса: «один человек — один голос». Любая стратегия,
# взвешивающая голос по балансу токена/монеты, превратила бы фонд во «власть
# денег» — это запрещено (CONSTITUTION ст. 2, запрет №5).
PLUTOCRATIC_MARKERS = (
    "erc20", "erc721", "erc1155", "balance-of", "balance",
    "delegation", "delegate", "token-weighted", "whitelist-weighted",
)

# Типы предложений, затрагивающие распределение/конституцию, обязаны явно
# привязываться к нормативным документам (агент/Safe не решают это сами).
REQUIRED_TYPE_BINDINGS = {
    # ключ типа → (обязательные doc-ссылки, обязательные флаги)
    "disbursement-direction": {
        "links": ["docs/PRIORITIES.md", "docs/ANTI-ABUSE.md"],
        "flags": {},
    },
    "constitution-amendment": {
        "links": ["docs/CONSTITUTION.md"],
        "flags": {"requires_supermajority": True},
    },
}


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


def collect_strategies(settings):
    """Собирает все объявленные стратегии голоса: верхнего уровня и из validation."""
    out = []
    out.extend(settings.get("strategies", []) or [])
    validation = settings.get("validation", {}) or {}
    params = validation.get("params", {}) or {}
    out.extend(params.get("strategies", []) or [])
    return out


# ---- Проверки. Каждая возвращает (status, violations[list]). ----

def check_one_person_one_vote(space):
    """Стратегия голоса = «ticket» value=1; ни одной плутократической стратегии."""
    violations = []
    settings = space.get("settings", {}) or {}
    strategies = collect_strategies(settings)
    if not strategies:
        violations.append({"record": SNAPSHOT_SPACE,
                           "problem": "не объявлено ни одной стратегии голоса"})
    for st in strategies:
        name = str(st.get("name", "")).lower()
        params = st.get("params", {}) or {}
        if any(m in name for m in PLUTOCRATIC_MARKERS):
            violations.append({
                "record": SNAPSHOT_SPACE,
                "problem": f"плутократическая стратегия голоса '{st.get('name')}' "
                           f"(вес по балансу запрещён, ст. 2 / запрет №5)",
            })
            continue
        if name != "ticket":
            violations.append({
                "record": SNAPSHOT_SPACE,
                "problem": f"стратегия голоса '{st.get('name')}' — ожидалась 'ticket' "
                           f"(1 человек = 1 голос)",
            })
            continue
        if params.get("value") != 1:
            violations.append({
                "record": SNAPSHOT_SPACE,
                "problem": f"стратегия 'ticket' с value={params.get('value')} — "
                           f"должно быть value=1 (равный вес голоса)",
            })
    return ("pass" if not violations else "fail"), violations


def check_timed_vote(space):
    """У голосования задан положительный срок (delay и period > 0)."""
    violations = []
    voting = (space.get("settings", {}) or {}).get("voting", {}) or {}
    for field in ("delay", "period"):
        val = voting.get(field)
        if not isinstance(val, int) or isinstance(val, bool) or val <= 0:
            violations.append({
                "record": SNAPSHOT_SPACE,
                "problem": f"voting.{field}={val!r} — должен быть положительным "
                           f"(ограниченный срок голосования, GOVERNANCE §7)",
            })
    return ("pass" if not violations else "fail"), violations


def check_off_chain_signal(space):
    """Snapshot — палата сигнала: off_chain_signaling=true и типы не исполняют сами."""
    violations = []
    if space.get("off_chain_signaling") is not True:
        violations.append({
            "record": SNAPSHOT_SPACE,
            "problem": "off_chain_signaling должен быть true (Snapshot не двигает "
                       "средства; исполнение — через Safe/Timelock после голосования)",
        })
    for pt in space.get("proposal_types", []) or []:
        if pt.get("binding") is not False:
            violations.append({
                "record": SNAPSHOT_SPACE,
                "problem": f"тип предложения '{pt.get('key')}' binding="
                           f"{pt.get('binding')!r} — off-chain сигнал не исполняет "
                           f"сам (должно быть false)",
            })
    return ("pass" if not violations else "fail"), violations


def check_proposal_binding(space):
    """Типы предложений про деньги/конституцию привязаны к нормативным докам и флагам."""
    violations = []
    types_by_key = {pt.get("key"): pt for pt in (space.get("proposal_types", []) or [])}
    for key, req in REQUIRED_TYPE_BINDINGS.items():
        pt = types_by_key.get(key)
        if pt is None:
            violations.append({
                "record": SNAPSHOT_SPACE,
                "problem": f"нет типа предложения '{key}' (требуется для привязки "
                           f"распределения/конституции к голосованию)",
            })
            continue
        links = pt.get("links", []) or []
        for needed in req["links"]:
            if needed not in links:
                violations.append({
                    "record": SNAPSHOT_SPACE,
                    "problem": f"тип '{key}' не ссылается на {needed} "
                               f"(привязка к конституции/приоритетам обязательна)",
                })
        for flag, expected in req["flags"].items():
            if pt.get(flag) != expected:
                violations.append({
                    "record": SNAPSHOT_SPACE,
                    "problem": f"тип '{key}': {flag}={pt.get(flag)!r}, ожидалось "
                               f"{expected!r} (поправка к конституции — супербольшинство, ст. 10)",
                })
    return ("pass" if not violations else "fail"), violations


def check_multisig_not_sole(safe):
    """Исполнительный мультисиг: порог ≥2 и строго меньше числа владельцев."""
    violations = []
    cfg = safe.get("safe", {}) or {}
    threshold = cfg.get("threshold")
    owners = cfg.get("owners_required")
    if not isinstance(threshold, int) or isinstance(threshold, bool):
        violations.append({"record": SAFE_CONFIG,
                           "problem": f"safe.threshold={threshold!r} — должно быть целым числом"})
        return "fail", violations
    if not isinstance(owners, int) or isinstance(owners, bool):
        violations.append({"record": SAFE_CONFIG,
                           "problem": f"safe.owners_required={owners!r} — должно быть целым числом"})
        return "fail", violations
    if threshold < 2:
        violations.append({
            "record": SAFE_CONFIG,
            "problem": f"порог threshold={threshold} < 2 — допускает единоличное "
                       f"распоряжение средствами (запрещено: никто не владеет один, ст. 5)",
        })
    if threshold > owners:
        violations.append({
            "record": SAFE_CONFIG,
            "problem": f"порог threshold={threshold} > владельцев {owners} — "
                       f"мультисиг неработоспособен",
        })
    if threshold == owners:
        violations.append({
            "record": SAFE_CONFIG,
            "problem": f"порог threshold={threshold} = числу владельцев {owners} — "
                       f"единогласие даёт каждому право вето (хрупко; "
                       f"GOVERNANCE §5 предполагает 3-из-5)",
        })
    return ("pass" if not violations else "fail"), violations


def check_lifecycle_links(root, configs):
    """Все doc-ссылки конфигов управления ведут к существующему файлу/каталогу."""
    violations = []
    for rel, data in configs:
        for target in iter_doc_links(data):
            full = os.path.join(root, target)
            if not os.path.exists(full):
                violations.append({
                    "record": rel,
                    "problem": f"ссылка управления ведёт в никуда → {target!r}",
                })
    return ("pass" if not violations else "fail"), violations


def iter_doc_links(data):
    """Все строковые doc-ссылки из links{} и proposal_types[].links[] конфига."""
    out = []
    links = data.get("links", {}) or {}
    for val in links.values():
        if isinstance(val, str) and val.startswith(("docs/", "governance/")):
            out.append(val)
    for pt in data.get("proposal_types", []) or []:
        for val in pt.get("links", []) or []:
            if isinstance(val, str):
                out.append(val)
    return out


CHECKS = [
    {
        "key": "one-person-one-vote",
        "title": "Голос = «ticket» value=1, без плутократических стратегий",
        "guards": "ст. 2 + запрет №5 — право голоса даёт уникальность человека, а не деньги",
        "scope": "snapshot",
        "fn": "opov",
    },
    {
        "key": "timed-vote",
        "title": "У голосования задан положительный срок (delay и period)",
        "guards": "GOVERNANCE §7 — голосование идёт «кворум+срок», окно ограничено во времени",
        "scope": "snapshot",
        "fn": "timed",
    },
    {
        "key": "off-chain-signal",
        "title": "Snapshot — off-chain сигнал, типы предложений не исполняют сами",
        "guards": "ст. 4 + GOVERNANCE §5 — Snapshot обсуждает, исполняет Safe/Timelock после голосования",
        "scope": "snapshot",
        "fn": "offchain",
    },
    {
        "key": "proposal-binding",
        "title": "Типы про деньги/конституцию привязаны к PRIORITIES/ANTI-ABUSE/CONSTITUTION",
        "guards": "ст. 5 + GOVERNANCE §7–§8 — распределение и поправки идут строго в рамках норм",
        "scope": "snapshot",
        "fn": "binding",
    },
    {
        "key": "multisig-not-sole",
        "title": "Исполнительный мультисиг: порог ≥2 и меньше числа владельцев",
        "guards": "ст. 5 + GOVERNANCE §5 — никто не распоряжается средствами единолично",
        "scope": "safe",
        "fn": "multisig",
    },
    {
        "key": "lifecycle-links",
        "title": "Все doc-ссылки конфигов управления ведут к существующему файлу",
        "guards": "ст. 3 — проверяемость: жизненный цикл привязан к реальным докам, не к битым",
        "scope": "both",
        "fn": "links",
    },
]


def run(root):
    """Прогоняет все проверки. Возвращает report dict."""
    space, space_err = read_json(root, SNAPSHOT_SPACE)
    safe, safe_err = read_json(root, SAFE_CONFIG)

    # Если конфиг не читается — соответствующие проверки падают с понятной причиной.
    def load_fail(rel, err):
        return "fail", [{"record": rel, "problem": err}]

    if space_err:
        opov = timed = offchain = binding = load_fail(SNAPSHOT_SPACE, space_err)
    else:
        opov = check_one_person_one_vote(space)
        timed = check_timed_vote(space)
        offchain = check_off_chain_signal(space)
        binding = check_proposal_binding(space)

    if safe_err:
        multisig = load_fail(SAFE_CONFIG, safe_err)
    else:
        multisig = check_multisig_not_sole(safe)

    configs = []
    if not space_err:
        configs.append((SNAPSHOT_SPACE, space))
    if not safe_err:
        configs.append((SAFE_CONFIG, safe))
    if space_err or safe_err:
        # Целостность ссылок проверяем по тому, что прочиталось; недостающий
        # конфиг уже отражён в провале своих проверок.
        links = check_lifecycle_links(root, configs)
        if space_err:
            links[1].append({"record": SNAPSHOT_SPACE, "problem": space_err})
            links = ("fail", links[1])
        if safe_err:
            links[1].append({"record": SAFE_CONFIG, "problem": safe_err})
            links = ("fail", links[1])
    else:
        links = check_lifecycle_links(root, configs)

    results = {
        "opov": opov, "timed": timed, "offchain": offchain,
        "binding": binding, "multisig": multisig, "links": links,
    }

    checks = []
    for spec in CHECKS:
        status, violations = results[spec["fn"]]
        checks.append({
            "key": spec["key"],
            "title": spec["title"],
            "guards": spec["guards"],
            "scope": spec["scope"],
            "status": status,
            "violations": violations,
        })

    all_pass = all(c["status"] == "pass" for c in checks)
    passed = sum(1 for c in checks if c["status"] == "pass")
    return {
        "agent": "governance",
        "role": "служебный модуль, не орган власти (Конституция, ст. 9); НЕ голосует",
        "verdict": "green" if all_pass else "red",
        "passed": passed,
        "total": len(checks),
        "artifacts": {"snapshot_space": SNAPSHOT_SPACE, "safe_config": SAFE_CONFIG},
        "checks": checks,
    }


def main(argv):
    parser = argparse.ArgumentParser(
        description="Governance AI-агент Public Trust DAO: жизненный цикл предложения "
                    "(голос/срок/off-chain/привязка к конституции/мультисиг). НЕ голосует."
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
    print("GOVERNANCE AI-АГЕНТ — Public Trust DAO")
    print("Служебный модуль (ст. 9): проверяет конфигурацию управления. НЕ голосует,")
    print("ничего не вносит и ничем не распоряжается. Находка = сигнал, не действие.")
    print("=" * 70)
    print(f"Snapshot-конфиг: {report['artifacts']['snapshot_space']}")
    print(f"Safe-конфиг:     {report['artifacts']['safe_config']}")
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
        print("Governance нашёл расхождение конфигурации управления с конституцией")
        print("(вес голоса / срок / исполнение / привязка к нормам / мультисиг). Это")
        print("сигнал сообществу, а не действие: агент не правит конфиг и не голосует.")
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
