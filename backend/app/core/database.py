from collections.abc import Iterator
from contextlib import contextmanager

import psycopg
from psycopg import Connection

from app.core.config import get_settings


@contextmanager
def get_connection() -> Iterator[Connection]:
    settings = get_settings()
    with psycopg.connect(settings.database_url) as conn:
        yield conn


def ping_database() -> str:
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("select version()")
            row = cursor.fetchone()
            if row is None:
                raise RuntimeError("Database version query returned no rows.")
            return str(row[0])
