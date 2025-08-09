# Using `docker compose run --rm`

## What it Means

The command:

```bash
docker compose run --rm <service> <command>
```

**Explanation**:
- **`run`** → Starts a new **one-off container** from the service definition in your `docker-compose.yml`.
- **`--rm`** → Automatically **removes** the container after the command finishes, preventing stopped containers from piling up.
- **`<service>`** → The **service name** from your `docker-compose.yml` (not the container name).
- **`<command>`** → The shell command to run inside that container.

---

## Example

```bash
docker compose run --rm server python manage.py makemigrations
docker compose run --rm server python manage.py migrate
```

### Steps Performed:
1. Create a **temporary container** based on the `server` service.
2. Run the Django management command inside it.
3. Remove the container automatically when done.

---

## When to Use

- **Use `exec`** when the service is **already running**:
  ```bash
  docker compose exec server python manage.py migrate
  ```

- **Use `run`** when:
  - The service is **not running**, or
  - It **fails to start** (e.g., migration errors).
  - You need to run a one-off command without starting the full stack.

---

## Our Case

In this conversation:
- The Django service name was `server`.
- The main container wouldn't start due to a migration error about a new `city` field.
- Solution: Run migrations using `docker compose run --rm` to bypass the startup crash.

Example:

```bash
docker compose run --rm server python manage.py makemigrations
docker compose run --rm server python manage.py migrate
docker compose up -d
```

This fixed the schema issue, allowing the container to start normally.
