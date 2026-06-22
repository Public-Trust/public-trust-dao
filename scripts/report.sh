#!/usr/bin/env bash
# Telegram reporter — шлёт отчёт о сессии строителя.
# Использование: ./scripts/report.sh "текст"   ИЛИ   echo "текст" | ./scripts/report.sh
set -uo pipefail
cd "$(dirname "$0")/.." || exit 1

# Подгрузить секреты из .env (не в git)
set -a; [ -f .env ] && . ./.env; set +a

MSG="${1:-$(cat)}"

if [ -z "${TELEGRAM_BOT_TOKEN:-}" ] || [ -z "${TELEGRAM_CHAT_ID:-}" ]; then
  echo "[report] TELEGRAM_BOT_TOKEN/CHAT_ID не заданы — пропуск" >&2
  exit 0
fi

# Телеграм лимит 4096 символов — режем
MSG="${MSG:0:4000}"

curl -sS -m 20 -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
  --data-urlencode "chat_id=${TELEGRAM_CHAT_ID}" \
  --data-urlencode "text=${MSG}" \
  -d "disable_web_page_preview=true" \
  -o /dev/null -w "[report] http %{http_code}\n"
