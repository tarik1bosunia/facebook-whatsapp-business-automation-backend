#!/bin/sh

# Exit immediately if a command exits with a non-zero status
set -e

echo "Starting entrypoint script with DJANGO_ENV=$DJANGO_ENV"

# Wait for the database to be ready (optional, but good for robustness in Docker)
echo "Waiting for database..."
sleep 5

# Run database migrations
python manage.py makemigrations --noinput
python manage.py migrate

python manage.py create_initial_users || true
python manage.py seed_products || true
python manage.py seed_promotions || true
python manage.py seed_faqs || true
python manage.py seed_aimodels || true

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
    exec gunicorn facebook_business_automation.asgi:application \
        -k uvicorn.workers.UvicornWorker \
        --bind 0.0.0.0:8000 \
        --workers 3 \
        --log-level=info
fi
# Workers where I write 3 , it will be =  number of CPU cores × 2 + 1:
# --workers $(($(nproc) * 2 + 1))