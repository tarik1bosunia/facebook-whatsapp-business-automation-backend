#!/bin/bash
set -e

echo "🚀 Resetting Django + PostgreSQL + Docker setup..."

# Step 1: Delete all migration files except __init__.py
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc" -delete

# Step 2: Stop and remove containers + volumes
docker compose down -v

# Step 3: Rebuild containers
docker compose up -d --build

# Step 4: Create fresh migrations
docker compose run --rm server python manage.py makemigrations

# Step 5: Apply migrations
docker compose run --rm server python manage.py migrate

echo "✅ Reset complete!"

