#!/usr/bin/env bash
# ============================================================================
# PUBLIC TRUST DAO — ПУЛЬС автономного строителя.
# Петля: запускает claude -p с мандатом BUILDER.md, после каждой сессии
# измеряет РЕАЛЬНЫЕ коммиты (git, не самоотчёт агента) и шлёт отчёт в Telegram.
#
# ⛔ ЭТОТ ФАЙЛ И systemd-сервис АГЕНТ-СТРОИТЕЛЬ НЕ ТРОГАЕТ. Сломает = умрёт.
#    Мандат правится в BUILDER.md, не здесь.
# ============================================================================
set -uo pipefail
cd "$(dirname "$0")/.." || exit 1
ROOT="$(pwd)"

# --- секреты / окружение -----------------------------------------------------
set -a; [ -f .env ] && . ./.env; set +a
export GH_TOKEN="${GITHUB_TOKEN:-${GH_TOKEN:-}}"
export PATH="/root/.local/bin:$PATH"
export HOME="${HOME:-/root}"
export IS_SANDBOX="${IS_SANDBOX:-1}"   # claude разрешает bypassPermissions под root только при этом флаге

# git auth через env (токен НЕ пишется в .git/config, читается из GH_TOKEN при push)
git config credential.helper '!f() { echo "username=x-access-token"; echo "password=${GH_TOKEN}"; }; f' 2>/dev/null || true

mkdir -p logs

# счётчик сессий (не в git)
NFILE="logs/session.count"
[ -f "$NFILE" ] || echo 0 > "$NFILE"

SLEEP_BETWEEN="${PTD_SLEEP:-10}"
SESSION_TIMEOUT="${PTD_TIMEOUT:-1800}"

echo "[loop] старт пульса $(date -u +%FT%TZ)"

while true; do
  N=$(( $(cat "$NFILE" 2>/dev/null || echo 0) + 1 ))
  echo "$N" > "$NFILE"
  TS=$(date -u +%FT%TZ)
  LOG="logs/session-$(date -u +%Y%m%d-%H%M%S)-$N.log"

  BEFORE=$(git rev-parse HEAD 2>/dev/null || echo none)
  echo "[loop] === сессия #$N $TS === лог: $LOG"

  # --- рабочая сессия строителя ---------------------------------------------
  timeout "$SESSION_TIMEOUT" claude -p "$(cat BUILDER.md)" \
      --permission-mode bypassPermissions \
      --model claude-opus-4-8 \
      --allowedTools Bash Edit Write Read WebFetch WebSearch Glob Grep \
      >> "$LOG" 2>&1
  RC=$?

  AFTER=$(git rev-parse HEAD 2>/dev/null || echo none)

  # --- ИЗМЕРЕННЫЙ отчёт (по git, не по словам агента) -----------------------
  NEXT=$(grep -m1 -A1 -i 'следующий шаг' PROGRESS.md 2>/dev/null | tail -1 | sed 's/^[[:space:]-]*//' | cut -c1-200)
  if [ "$BEFORE" != "$AFTER" ] && [ "$AFTER" != "none" ]; then
    COMMITS=$(git log --oneline "${BEFORE}..${AFTER}" 2>/dev/null | head -15)
    NCOM=$(git rev-list --count "${BEFORE}..${AFTER}" 2>/dev/null || echo '?')
    ./scripts/report.sh "🟢 PTD сессия #$N — $NCOM коммит(ов) (rc=$RC)
${COMMITS}

Дальше: ${NEXT:-—}
repo: https://github.com/Public-Trust/public-trust-dao/commits/main"
  else
    TAIL=$(tail -3 "$LOG" 2>/dev/null | tr '\n' ' ' | cut -c1-300)
    ./scripts/report.sh "🟡 PTD сессия #$N — без новых коммитов (rc=$RC)
Дальше: ${NEXT:-—}
хвост лога: ${TAIL}"
  fi

  echo "[loop] сессия #$N завершена rc=$RC, sleep ${SLEEP_BETWEEN}s"
  sleep "$SLEEP_BETWEEN"
done
