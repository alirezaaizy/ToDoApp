#!/usr/bin/env bash
set -Eeuo pipefail

# پیش‌فرض‌ها (اگر در .env نبودند)
: "${POSTGRES_HOST:=db}"
: "${POSTGRES_PORT:=5432}"
: "${DJANGO_ENV:=dev}"            # dev | prod
: "${DJANGO_COLLECTSTATIC:=0}"    # 0 | 1
: "${RUN_MIGRATIONS:=1}"          # فقط در prod لحاظ می‌شود
: "${WEB_CONCURRENCY:=3}"         # تعداد ورکرهای Gunicorn
: "${WAIT_FOR_DB_TIMEOUT:=60}"    # ثانیه

echo "Waiting for PostgreSQL at ${POSTGRES_HOST}:${POSTGRES_PORT} (timeout: ${WAIT_FOR_DB_TIMEOUT}s)..."
for i in $(seq 1 "${WAIT_FOR_DB_TIMEOUT}"); do
  if nc -z "${POSTGRES_HOST}" "${POSTGRES_PORT}" 2>/dev/null; then
    echo "PostgreSQL is up."
    break
  fi
  sleep 1
  if [ "$i" -eq "${WAIT_FOR_DB_TIMEOUT}" ]; then
    echo "ERROR: PostgreSQL did not become available within ${WAIT_FOR_DB_TIMEOUT}s." >&2
    exit 1
  fi
done

# حالت اجرا
if [ "${DJANGO_ENV}" = "prod" ]; then
  # فقط در prod: مهاجرت و کالکت‌استاتیک (در صورت نیاز)
  if [ -f "manage.py" ] && [ "${RUN_MIGRATIONS}" = "1" ]; then
    echo "Running migrations (prod)..."
    python manage.py migrate --noinput
  else
    echo "Skipping migrations (RUN_MIGRATIONS=${RUN_MIGRATIONS})."
  fi

  if [ -f "manage.py" ] && [ "${DJANGO_COLLECTSTATIC}" = "1" ]; then
    echo "Collecting static files (prod)..."
    python manage.py collectstatic --noinput
  fi

  echo "Starting Gunicorn (prod, workers=${WEB_CONCURRENCY})..."
  exec gunicorn core.wsgi:application --bind 0.0.0.0:8000 --workers "${WEB_CONCURRENCY}"
else
  echo "Starting Django dev server (no migrations)..."
  exec "$@"
fi
