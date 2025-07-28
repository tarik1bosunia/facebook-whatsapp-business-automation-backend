# 1. Get PostgreSQL Database URL
A standard PostgreSQL connection URL format is:
```
postgresql://USER:PASSWORD@HOST:PORT/NAME
```
## Where to Find It:
### 1. Local Development:
```
postgresql://postgres:yourpassword@localhost:5432/yourdbname
```
### 2 Cloud Providers:

AWS RDS: Check RDS dashboard → Connectivity & security

Heroku: heroku config:get DATABASE_URL

DigitalOcean: Control Panel → Databases → Connection Details

Azure: Portal → Database → Connection strings

### From Existing Django Settings:
```python
from django.conf import settings
DATABASE_URL = f"postgresql://{settings.DATABASES['default']['USER']}:{settings.DATABASES['default']['PASSWORD']}@{settings.DATABASES['default']['HOST']}:{settings.DATABASES['default']['PORT']}/{settings.DATABASES['default']['NAME']}"
```

# 2. Configure Django to Use DATABASE_URL
## Install Required Packages:
```sh
pip install dj-database-url psycopg2-binary
```
## In settings.py:
```python
import dj_database_url
from decouple import config

# .env file should contain:
# DATABASE_URL=postgresql://user:pass@host:port/dbname

DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL'),
        conn_max_age=600,
        conn_health_checks=True,
    )
}
```
# 3. For LangChain Memory (PostgresChatMessageHistory)
## Install:
```sh
pip install langchain-postgres
```
## Configuration:
```sh
from langchain_community.chat_message_histories import PostgresChatMessageHistory

def get_message_history(session_id):
    return PostgresChatMessageHistory(
        session_id=session_id,
        connection_string=settings.DATABASE_URL,
        table_name="chat_message_history"  # custom table name
    )

```

# Full Production Example
## .env file:
```text
DATABASE_URL=postgresql://myuser:mypassword@myhost:5432/mydb?sslmode=require
```
## settings.py:
```python
DATABASES = {
    'default': {
        **dj_database_url.config(),
        'DISABLE_SERVER_SIDE_CURSORS': True,  # For large resultsets
        'OPTIONS': {
            'connect_timeout': 5,
            'application_name': 'myapp_prod'
        }
    }
}
```

# This setup provides:

- Environment-based configuration
- Connection pooling
- SSL security
- Health checks
- Production-ready timeouts