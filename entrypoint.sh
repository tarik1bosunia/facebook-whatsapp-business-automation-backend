#!/bin/sh

# Exit immediately if a command exits with a non-zero status
set -e

echo "Starting entrypoint with DJANGO_ENV=${DJANGO_ENV:-production}"

# Wait for Postgres to be ready (uses env from compose)
# -n "$DB_HOST" checks if the variable DB_HOST is non-empty.
# This loop runs a maximum of 30 times
for i in $(seq 1 30); do

  # This checks if Postgres is ready for connections.
  if pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" >/dev/null 2>&1; then
    echo "✅ Postgres is ready."
    
    # This command IMMEDIATELY exits the loop.
    break
  fi
  
  # This line only runs if pg_isready fails.
  echo "… still waiting ($i/30)"
  sleep 2
done

# Make and apply migrations
echo "makemigrations"
python manage.py makemigrations --noinput

if [ "$DJANGO_ENV" = "development" ]; then
  echo "migrate (dev safe mode: --fake-initial)"
  python manage.py migrate --fake-initial
else
  echo "migrate (production)"
  python manage.py migrate
fi

# Seed data (idempotent)
echo "seeding..."
python manage.py create_initial_users || true
python manage.py seed_products || true
python manage.py seed_promotions || true
python manage.py seed_faqs || true
python manage.py seed_aimodels || true


# Collect static only in prod
if [ "$DJANGO_ENV" = "production" ]; then
  echo "📂 collectstatic"
  python manage.py collectstatic --noinput
fi

# Start server
if [ "$DJANGO_ENV" = "development" ]; then
  echo "runserver (dev)"
  exec python manage.py runserver 0.0.0.0:8000
else
  echo "gunicorn (prod)"
  exec gunicorn facebook_business_automation.asgi:application \
    -k uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --workers $(($(nproc) * 2 + 1)) \
    --log-level=info
fi
# Workers, it will be =  number of CPU cores × 2 + 1: