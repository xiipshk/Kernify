#!/bin/bash
# Ежедневный вызов: выбирает (при необходимости) задачу дня и заполняет неделю вперёд.
# Идемпотентно: уже выбранные даты не меняются.
set -euo pipefail
cd "$(dirname "$0")/.."

export PATH="$HOME/homebrew/bin:$PATH"
mkdir -p logs

if [ -x venv/bin/python ]; then
    PY=venv/bin/python
else
    PY=python3
fi

"$PY" manage.py set_daily_challenge --days 7 >> logs/daily_challenge.log 2>&1
