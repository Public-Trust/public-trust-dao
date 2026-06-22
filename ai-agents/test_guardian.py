#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест-инвариант для Guardian-агента — Public Trust DAO.

Доказывает, что Guardian РАБОТАЕТ (а не «зелёный по умолчанию»): на КАЖДОЕ
нарушение рельс безопасности он обязан вернуть «красно» (exit=1), а на чистом
дереве — «зелёно» (exit=0), и при этом НЕ ложно-срабатывать на легитимных
sha256-хэшах реестра/манифеста.

Метод: строим временный git-репозиторий, кладём в него копию guardian_agent.py
и подсовываем то чистые, то «отравленные» файлы; запускаем агент как подпроцесс и
проверяем вердикт по --json. Только стандартная библиотека + git. Сети нет.
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
AGENT = os.path.join(HERE, "guardian_agent.py")

PASSED = 0
FAILED = 0


def check(name, cond):
    global PASSED, FAILED
    if cond:
        PASSED += 1
        print(f"  ✓ {name}")
    else:
        FAILED += 1
        print(f"  ✗ {name}")


def git(repo, *args):
    subprocess.run(["git", *args], cwd=repo, check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def make_repo(tmp):
    """Минимальный чистый репозиторий с тем же расположением агента (ai-agents/)."""
    os.makedirs(os.path.join(tmp, "ai-agents"))
    shutil.copy(AGENT, os.path.join(tmp, "ai-agents", "guardian_agent.py"))
    # Чистые «легитимные» артефакты: .gitignore + sha256-хэши в реестре (НЕ ключи).
    with open(os.path.join(tmp, ".gitignore"), "w", encoding="utf-8") as fh:
        fh.write(".env\n*.env\nlogs/\n__pycache__/\n")
    os.makedirs(os.path.join(tmp, "governance"))
    legit_hash = "a" * 64  # 64-hex как значение поля hash — это хэш, не ключ
    with open(os.path.join(tmp, "governance", "index.json"), "w", encoding="utf-8") as fh:
        json.dump({"head_hash": legit_hash,
                   "entries": [{"hash": "b" * 64, "prev_hash": "c" * 64}],
                   "network": {"chain_id": 80002}}, fh)
    git(tmp, "init")
    git(tmp, "add", "-A")
    git(tmp, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-m", "init")


def run_agent(tmp):
    """Запускает Guardian в репо tmp, возвращает (exit_code, report_dict)."""
    proc = subprocess.run(
        [sys.executable, os.path.join(tmp, "ai-agents", "guardian_agent.py"), "--json"],
        cwd=tmp, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
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


def add_tracked(tmp, relpath, content):
    full = os.path.join(tmp, relpath)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as fh:
        fh.write(content)
    git(tmp, "add", "-f", relpath)
    git(tmp, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-m", "x")


def scenario(title, mutate, expect_green, expect_fail_key=None):
    """Готовит свежий репо, мутирует его, проверяет вердикт."""
    print(f"\n[{title}]")
    tmp = tempfile.mkdtemp(prefix="guardian-test-")
    try:
        make_repo(tmp)
        if mutate:
            mutate(tmp)
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


def main():
    print("ТЕСТ-ИНВАРИАНТ GUARDIAN — доказываем, что красное ловится, зелёное не ложно-падает")

    # 1. Чистое дерево (с легитимными sha256-хэшами) → зелёно, без ложных срабатываний.
    scenario("чистое дерево + sha256-хэши реестра (не ключи)", None, expect_green=True)

    # 2. Закоммичен .env → secrets-tracked красный.
    scenario("закоммичен .env с секретом",
             lambda t: add_tracked(t, ".env", "TOKEN=abc123\n"),
             expect_green=False, expect_fail_key="secrets-tracked")

    # 3. Закоммичен приватный ключ-файл → secrets-tracked красный.
    scenario("закоммичен deploy.key",
             lambda t: add_tracked(t, "deploy.key", "keymaterial\n"),
             expect_green=False, expect_fail_key="secrets-tracked")

    # 4. mainnet chain_id в конфиге → no-mainnet красный.
    scenario("mainnet chain_id=1 в конфиге",
             lambda t: add_tracked(t, "net.json", '{"network":{"chainId":1}}'),
             expect_green=False, expect_fail_key="no-mainnet")

    # 5. 64-hex вне хэш-поля → no-key-material красный.
    scenario("64-hex приватный ключ в .txt",
             lambda t: add_tracked(t, "notes.txt", "key " + "d" * 64 + "\n"),
             expect_green=False, expect_fail_key="no-key-material")

    # 6. Присваивание private_key реальным значением → no-key-material красный.
    scenario("private_key: <реальное значение>",
             lambda t: add_tracked(t, "conf.yml", 'private_key: 0x' + "e" * 64 + "\n"),
             expect_green=False, expect_fail_key="no-key-material")

    # 7. Удалён .env из .gitignore → gitignore-guards красный.
    def break_gitignore(t):
        with open(os.path.join(t, ".gitignore"), "w", encoding="utf-8") as fh:
            fh.write("__pycache__/\n")  # нет .env и нет logs/
        git(t, "add", "-A")
        git(t, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-m", "x")
    scenario("в .gitignore нет .env/logs", break_gitignore,
             expect_green=False, expect_fail_key="gitignore-guards")

    # 8. process.env-ссылка НЕ считается утечкой (нет ложного срабатывания).
    scenario("private_key из окружения (process.env) — не утечка",
             lambda t: add_tracked(t, "hardhat.js", "accounts: process.env.PRIVATE_KEY\n"),
             expect_green=True)

    # 9. Тест-инвариант самого агента (ai-agents/test_*.py) — это фабрика фейковых
    #    фикстур: его текст НЕ сканируется (иначе Guardian ложно краснеет на своём
    #    же тесте). Та же «отрава» в обычном файле — обязана ловиться (сценарий 6).
    scenario("отравленная фикстура внутри ai-agents/test_x.py — пропускается",
             lambda t: add_tracked(t, "ai-agents/test_x.py",
                                   'add_tracked(t, "c.yml", "private_key: 0x" + "e" * 64)\n'),
             expect_green=True)

    # 10. Плейсхолдер-многоточие в прозе/документации (`private_key: 0x...`) — НЕ утечка
    #     (настоящий ключ — 64 hex без точек). Иначе доки, обсуждающие ключи, ложно красят.
    scenario("плейсхолдер private_key: 0x... в документации — не утечка",
             lambda t: add_tracked(t, "NOTES.md", "пример строки `private_key: 0x...`\n"),
             expect_green=True)

    # 11. head_hash, показанный в HTML-разметке (`<b>head_hash</b>...class="hash"`),
    #     — это значение хэш-поля, а НЕ приватный ключ. Подсказка хэша лежит в разметке
    #     без `:`/`=`, поэтому label-эвристики мало — нужен разбор словесных токенов
    #     префикса. Регрессия на ложное срабатывание Guardian на странице прозрачности.
    scenario("head_hash в HTML (class=\"hash\") — не утечка",
             lambda t: add_tracked(t, "page.html",
                                   '<span class="fact"><b>head_hash</b>'
                                   '<span class="hash">' + "f" * 64 + "</span></span>\n"),
             expect_green=True)

    print(f"\nИТОГ: {PASSED} прошли, {FAILED} провалились")
    return 0 if FAILED == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
