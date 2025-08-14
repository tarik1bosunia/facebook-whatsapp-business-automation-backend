# Full Reset Guide for Django + PostgreSQL + Docker on Ubuntu VPS

If you want to completely reset your Django + Postgres + Docker setup on your Ubuntu VPS, follow these steps.

---

## 1️⃣ SSH into your VPS

```bash
ssh username@your_vps_ip
```

---

## 2️⃣ Go to your project directory

```bash
cd /path/to/your/project
```

---

## 3️⃣ Delete all migration files except `__init__.py`

```bash
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc" -delete
```

---

## 4️⃣ Stop and remove containers + volumes (DB wipe)

```bash
docker compose down -v
```

⚠ **Warning:** This removes your Postgres database volume — all data will be lost.

---

## 5️⃣ Rebuild containers

```bash
docker compose up -d --build
```

---

## 6️⃣ Create fresh migrations

```bash
docker compose run --rm server python manage.py makemigrations
```

---

## 7️⃣ Apply migrations

```bash
docker compose run --rm server python manage.py migrate
```

---

✅ **Now you have:**

- A **fresh DB**
- **Fresh migrations**
- **Clean state** with no leftover tables or migration conflicts

---

## Easy Option

put the  reset_django_db.sh in project root directory where docker compse and run following comands

```bash
chmod +x reset_django_db.sh
./reset_django_db.sh
```
