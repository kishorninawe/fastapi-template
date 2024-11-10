#! /usr/bin/env sh
set -e

export APP_MODULE="${APP_MODULE:-app.main:app}"

export HOST="${HOST:-0.0.0.0}"
export PORT="${PORT:-80}"
export LOG_LEVEL="${LOG_LEVEL:-info}"

PRE_START_PATH="${PRE_START_PATH:-/app/scripts/prestart.sh}"
echo "Checking for script in $PRE_START_PATH"
if [ -f "$PRE_START_PATH" ]; then
    echo "Running script $PRE_START_PATH"
    . "$PRE_START_PATH"
else
    echo "No script found at $PRE_START_PATH"
fi

# Start Uvicorn with live reload
exec uvicorn --reload --host $HOST --port $PORT --log-level $LOG_LEVEL "$APP_MODULE"