| Feature           | **Daphne**            | **Uvicorn**                        | **Hypercorn**                        |
| ----------------- | --------------------- | ---------------------------------- | ------------------------------------ |
| Developed by      | Django Channels team  | Encode (FastAPI creators)          | Quart team (async Flask)             |
| ASGI support      | ✅ Full                | ✅ Full                             | ✅ Full                               |
| HTTP/1 + HTTP/2   | ✅ Yes                 | ✅ Yes (limited HTTP/2)             | ✅ Yes (including HTTP/3)             |
| WebSocket support | ✅ Yes                 | ✅ Yes                              | ✅ Yes                                |
| Speed             | 🟡 Okay (pure Python) | 🟢 Fast (uvloop + httptools)       | 🟢 Fast (supports multiple backends) |
| TLS/SSL           | ❌ External only       | ❌ External only                    | ✅ Built-in                           |
| Multiprocessing   | ❌ Not built-in        | ❌ Not built-in                     | ✅ Yes                                |
| ASGI lifespan     | ✅ Yes                 | ✅ Yes                              | ✅ Yes                                |
| Production-ready? | 🟡 For Channels       | 🟢 Yes (w/ Gunicorn or standalone) | 🟢 Yes                               |
