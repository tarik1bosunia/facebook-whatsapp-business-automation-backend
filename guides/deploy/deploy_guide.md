# Django + Celery + Postgres Deployment Guide

This guide explains how to **build your Django Docker image locally, push it to Docker Hub, and deploy it to a VPS** using `docker-compose`.

---

## 1. Prerequisites

### On Local Development Machine
- Docker & Docker Compose installed
- Docker Hub account (or GitHub Container Registry)

### On VPS
- Ubuntu 20.04+ (example)
- Docker & Docker Compose installed:
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install docker.io docker-compose -y
sudo systemctl enable docker --now
```

---

## 2. Build & Push Django Image

### Login to Docker Hub
```bash
docker login
```

### Build Image
```bash
docker build -t yourusername/yourapp:latest .
```

### Push Image to Docker Hub
```bash
docker push yourusername/yourapp:latest
```

---

## 3. Prepare Environment Variables

Create a `.env` file **(don’t commit to Git)**:

```env
# Django settings
DJANGO_SECRET_KEY=your-secret
DJANGO_DEBUG=False
ALLOWED_HOSTS=yourdomain.com,your_vps_ip

# Database
POSTGRES_DB=mydb
POSTGRES_USER=myuser
POSTGRES_PASSWORD=mypassword

# Redis
REDIS_URL=redis://redis:6379/0
```

---

## 4. Production docker-compose.yml

Create `docker-compose.yml`:

```yaml
version: "3.9"

services:
  web:
    image: yourusername/yourapp:latest
    command: gunicorn yourproject.wsgi:application --bind 0.0.0.0:8000
    ports:
      - "8000:8000"
    env_file:
      - .env
    depends_on:
      - db
      - redis

  db:
    image: postgres:15
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7
    ports:
      - "6379:6379"

  celery_worker:
    image: yourusername/yourapp:latest
    command: celery -A yourproject worker -l info
    env_file:
      - .env
    depends_on:
      - db
      - redis

  celery_beat:
    image: yourusername/yourapp:latest
    command: celery -A yourproject beat -l info
    env_file:
      - .env
    depends_on:
      - db
      - redis

volumes:
  postgres_data:
```

---

## 5. Deploy on VPS

### Copy Files
Only send `.env` and `docker-compose.yml` to VPS:

```bash
scp docker-compose.yml .env user@<VPS_IP>:/home/user/app/
```

### Run Containers
```bash
ssh user@<VPS_IP>
cd app
docker-compose pull        # Pull latest Django image + official DB/Redis
docker-compose up -d       # Start all services
```

---

## 6. Apply Migrations & Collect Static

Run commands inside the container:

```bash
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py collectstatic --noinput
docker-compose exec web python manage.py createsuperuser
```

---

## 7. Access Application

- Open `http://<VPS_IP>:8000` or your domain
- Configure Nginx reverse proxy + SSL (optional, see below)

---

## 8. Optional: Add Nginx + SSL

Use Nginx on VPS or add as another container for reverse proxy + HTTPS via Let’s Encrypt.

---

## 9. Updating Deployment

When you push a new image version:

```bash
docker push yourusername/yourapp:latest

ssh user@<VPS_IP>
cd app
docker-compose pull
docker-compose up -d
```

---

## 10. Managing Containers

- Stop containers:
```bash
docker-compose down
```

- View logs:
```bash
docker-compose logs -f
```

- Restart app:
```bash
docker-compose restart web
```

---

## 11. Persisting Data

- Postgres data is stored in Docker volume `postgres_data`
- Safe during redeployments

---

## 12. Security Checklist

- Set `DEBUG=False`
- Add `ALLOWED_HOSTS`
- Use strong `SECRET_KEY`
- Use firewall (allow 80/443 only)
- Use HTTPS (Certbot or Cloudflare)

---

### Next Steps
- Add Nginx + Certbot for domain + SSL
- Set up CI/CD (GitHub Actions) to auto-build and push image
- Add health checks and monitoring
