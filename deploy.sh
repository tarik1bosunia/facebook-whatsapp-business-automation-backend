#!/bin/bash

set -e  # Exit immediately on error
set -o pipefail

echo "📦 Pulling latest code..."
git pull origin main

echo "🧼 Cleaning up old containers..."
docker compose down

echo "🚀 Building and launching containers..."
docker compose up -d --build

echo "⌛ Waiting for server to be healthy..."
sleep 15  # Give some time for healthchecks to run

# Optionally check health endpoint before running next steps
if ! curl -f http://localhost:8000/health/ >/dev/null 2>&1; then
  echo "❌ Server healthcheck failed. Exiting..."
  exit 1
fi

echo "🗃️ Running migrations inside container..."
docker compose exec server python manage.py migrate --noinput

echo "👤 Creating initial users, seeding data..."
docker compose exec server python manage.py create_initial_users || true
docker compose exec server python manage.py seed_products || true
docker compose exec server python manage.py seed_promotions || true
docker compose exec server python manage.py seed_faqs || true

echo "🎨 Collecting static files..."
docker compose exec server python manage.py collectstatic --noinput

echo "✅ Deployment complete!"
