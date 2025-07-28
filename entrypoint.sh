#!/bin/sh

# Exit immediately if a command exits with a non-zero status
set -e

echo "Starting entrypoint script with DJANGO_ENV=$DJANGO_ENV"

# Run database migrations
python manage.py makemigrations --noinput
python manage.py migrate

python manage.py create_initial_users || true
python manage.py seed_products || true
python manage.py seed_promotions || true
python manage.py seed_faqs || true

# Collect static files (if in production)
if [ "$DJANGO_ENV" = "production" ]; then
    echo "Collecting static files..."
    python manage.py collectstatic --noinput
fi

# Start server based on environment
if [ "$DJANGO_ENV" = "development" ]; then
    echo "Running development server..."
    exec python manage.py runserver 0.0.0.0:8000
else
    echo "Starting Gunicorn..."
    exec gunicorn your_project.asgi:application \
        -k uvicorn.workers.UvicornWorker \
        --bind 0.0.0.0:8000 \
        --workers 3 \
        --log-level=info
fi