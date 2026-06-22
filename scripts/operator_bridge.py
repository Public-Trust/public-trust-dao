#!/usr/bin/env python3
# ============================================================================
# PUBLIC TRUST DAO — мост двусторонней связи Оператор <-> Контур через Telegram.
#
# Ловит сообщения оператора боту (long-poll getUpdates), на каждое запускает
# claude-турн В РЕПО с памятью диалога (--resume <session_id>), отвечает в
# Telegram и пишет ВЕСЬ обмен в comms/operator-thread.md (коммит+пуш в репо).
# Указания оператора попадают в comms/INBOX.md — строитель берёт их приоритетом.
#
# Официальный headless-паттерн (claude -p / --resume / --output-format json).
# ⛔ Это ПУЛЬС-инфраструктура: агент-строитель её НЕ редактирует.
# ============================================================================
import os, sys, json, time, subprocess, urllib.parse, urllib.request, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

# --- .env ---
env = {}
try:
    for line in open(".env"):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            env[k] = v
except FileNotFoundError:
    pass
BOT = env.get("TELEGRAM_BOT_TOKEN", "")
CHAT = str(env.get("TELEGRAM_CHAT_ID", ""))
os.environ["GH_TOKEN"] = env.get("GITHUB_TOKEN", os.environ.get("GH_TOKEN", ""))
os.environ["IS_SANDBOX"] = "1"               # claude bypassPermissions под root
os.environ["PATH"] = "/root/.local/bin:" + os.environ.get("PATH", "")
os.environ.setdefault("HOME", "/root")

if not BOT or not CHAT:
    print("[bridge] нет TELEGRAM_BOT_TOKEN/CHAT_ID — выход", flush=True)
    sys.exit(1)

API = f"https://api.telegram.org/bot{BOT}"
os.makedirs("comms", exist_ok=True)
os.makedirs("logs", exist_ok=True)
OFFSET_F = "logs/operator_offset"
SID_F = "logs/operator_session"
THREAD = "comms/operator-thread.md"
INBOX = "comms/INBOX.md"
MODEL = "claude-opus-4-8"
TURN_TIMEOUT = 600

MANDATE = (
    "Ты — голос автономного контура Public Trust DAO в приватном Telegram-чате с "
    "оператором (основателем проекта). Отвечай ПО-РУССКИ, кратко, по делу, без воды.\n"
    "У тебя есть доступ к репозиторию проекта в текущей папке. Отвечай ПРАВДИВО на "
    "основе РЕАЛЬНОГО состояния: смотри `git log --oneline`, PROGRESS.md, DECISIONS.md, "
    "файлы репо. НЕ выдумывай, не строй догадок — измерь и ответь фактом.\n"
    "Если оператор даёт указание/приоритет/правку курса для стройки — допиши его пунктом "
    "в `comms/INBOX.md` (создай если нет; формат: '- [ ] <указание оператора>'), чтобы "
    "агент-строитель выполнил в ближайшую сессию, и подтверди оператору, что записал.\n"
    "⛔ НЕ трогай scripts/loop.sh, scripts/report.sh, scripts/operator_bridge.py, systemd-"
    "сервисы, .env, logs/ — это пульс/секреты. Не делай git push сам (мост сам коммитит "
    "переписку). Соблюдай рельсы: TESTNET-first, без реальных денег и приватных ключей, "
    "всё открыто. Это общественное благо, НЕ инвестиция."
)


def http(method, params, timeout):
    data = urllib.parse.urlencode(params).encode()
    req = urllib.request.Request(f"{API}/{method}", data=data)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)


def send(text):
    text = text or "(пустой ответ)"
    # Telegram лимит 4096 — режем на куски
    for i in range(0, len(text), 3900):
        try:
            http("sendMessage", {"chat_id": CHAT, "text": text[i:i + 3900],
                                 "disable_web_page_preview": "true"}, 30)
        except Exception as e:
            print(f"[bridge] send err: {e}", flush=True)


def now():
    return datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def run_turn(text):
    """Запустить claude-турн с памятью диалога. Возвращает (result, session_id)."""
    sid = None
    if os.path.exists(SID_F):
        sid = open(SID_F).read().strip() or None
    cmd = ["claude", "-p", text,
           "--output-format", "json",
           "--permission-mode", "bypassPermissions",
           "--model", MODEL,
           "--append-system-prompt", MANDATE,
           "--allowedTools", "Bash", "Read", "Grep", "Glob", "Write", "Edit", "WebFetch", "WebSearch"]
    if sid:
        cmd += ["--resume", sid]
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=TURN_TIMEOUT)
    except subprocess.TimeoutExpired:
        return ("⏳ Думал дольше лимита и прервался. Переформулируй или спроси короче.", sid)
    out = p.stdout.strip()
    try:
        d = json.loads(out)
        res = d.get("result") or "(нет ответа)"
        new_sid = d.get("session_id")
        if new_sid:
            open(SID_F, "w").write(new_sid)
        return (res, new_sid or sid)
    except Exception:
        tail = (out or p.stderr or "")[-500:]
        return (f"⚠️ Не разобрал ответ движка. rc={p.returncode}. Хвост: {tail}", sid)


def git_persist(ts, op_text, reply):
    if not os.path.exists(THREAD):
        open(THREAD, "w").write(
            "# Переписка оператора с контуром Public Trust DAO\n\n"
            "Открытый публичный журнал диалога оператора (основателя) с автономным "
            "контуром. Ведётся автоматически мостом `scripts/operator_bridge.py`.\n")
    with open(THREAD, "a") as f:
        f.write(f"\n---\n\n### [{ts}] 🧑 Оператор\n{op_text}\n\n### [{ts}] 🤖 Контур\n{reply}\n")
    for cmd in (["git", "add", "comms/"],
                ["git", "pull", "--rebase", "origin", "main"],
                ["git", "commit", "-q", "-m", f"comms: обмен с оператором {ts}"],
                ["git", "push", "origin", "HEAD:main"]):
        try:
            subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        except Exception as e:
            print(f"[bridge] git {cmd[1]} err: {e}", flush=True)


def main():
    offset = int(open(OFFSET_F).read().strip()) if os.path.exists(OFFSET_F) else 0
    print(f"[bridge] старт, offset={offset}", flush=True)
    while True:
        try:
            res = http("getUpdates", {"timeout": 50, "offset": offset}, 70)
        except Exception as e:
            print(f"[bridge] getUpdates err: {e}", flush=True)
            time.sleep(5)
            continue
        for u in res.get("result", []):
            offset = u["update_id"] + 1
            open(OFFSET_F, "w").write(str(offset))
            msg = u.get("message") or u.get("edited_message")
            if not msg:
                continue
            if str(msg.get("chat", {}).get("id")) != CHAT:
                continue
            text = msg.get("text") or msg.get("caption")
            if not text:
                continue
            ts = now()
            print(f"[bridge] {ts} op: {text[:80]}", flush=True)
            send("…думаю")
            reply, _ = run_turn(text)
            send(reply)
            git_persist(ts, text, reply)
        time.sleep(1)


if __name__ == "__main__":
    main()
