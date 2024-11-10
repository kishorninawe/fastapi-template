#! /usr/bin/env sh
set -e

export APP_MODULE="${APP_MODULE:-app.main:app}"
export GUNICORN_CONF="${GUNICORN_CONF:-/app/scripts/gunicorn_conf.py}"
export WORKER_CLASS="${WORKER_CLASS:-uvicorn.workers.UvicornWorker}"

PRE_START_PATH="${PRE_START_PATH:-/app/scripts/prestart.sh}"
echo "Checking for script in $PRE_START_PATH"
if [ -f "$PRE_START_PATH" ]; then
    echo "Running script $PRE_START_PATH"
    . "$PRE_START_PATH"
else
    echo "No script found at $PRE_START_PATH"
fi

# Start Gunicorn
exec gunicorn -k "$WORKER_CLASS" -c "$GUNICORN_CONF" "$APP_MODULE"