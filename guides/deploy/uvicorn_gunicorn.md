# Choosing Between Uvicorn and Gunicorn+UvicornWorker for Django ASGI

When deploying Django with ASGI (Channels, async views, WebSockets), you have two main options:

---

## Option 1: **Uvicorn Only** (Simpler)

### Pros
- Lightweight and fewer moving parts
- Directly supports ASGI (no WSGI compatibility hacks)
- Ideal for real-time apps (e.g., WebSockets)

### Cons
- Lacks some advanced Gunicorn features (prefork model, graceful reloads)

**Best if:**  
Your application is fully async and you don’t need Gunicorn’s process management.

---

## Option 2: **Gunicorn + UvicornWorker** (Hybrid)

### Pros
- Gunicorn manages multiple Uvicorn workers
- Better process management, graceful reloads, built-in logging
- Easier scaling (especially behind Nginx or in Docker)

### Cons
- Slightly more overhead
- More complex configuration (must use `-k uvicorn.workers.UvicornWorker`)

**Best if:**  
You need multi-process scaling or run under heavy production load.

---

## Recommendation

- **Most production setups**: Use **Gunicorn + UvicornWorker**  
  (Keeps Gunicorn’s robustness with ASGI support via UvicornWorker)
- **Simpler deployments or microservices**: Use **Uvicorn only**


```bash
exec gunicorn your_project.asgi:application \
    -k uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --log-level=info
```