# Postgres healthcheck

## check inside server container

```bash
docker compose exec server sh
echo "$DB_HOST $DB_PORT $DB_USER"
pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER"
```
