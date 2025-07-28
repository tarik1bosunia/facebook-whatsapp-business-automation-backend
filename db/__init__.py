import psycopg
from django.conf import settings
async def get_async_connection():
    dsn = (
        f"host={settings.DATABASES['default']['HOST']} "
        f"port={settings.DATABASES['default']['PORT']} "
        f"dbname={settings.DATABASES['default']['NAME']} "
        f"user={settings.DATABASES['default']['USER']} "
        f"password={settings.DATABASES['default']['PASSWORD']}"
    )
    return await psycopg.AsyncConnection.connect(dsn)
