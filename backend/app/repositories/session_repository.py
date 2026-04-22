from typing import Any

from psycopg import Connection
from psycopg.rows import dict_row


def create_session(conn: Connection) -> dict[str, Any]:
    with conn.cursor(row_factory=dict_row) as cursor:
        cursor.execute(
            """
            insert into study_session(started_at)
            values (now())
            returning id, started_at, ended_at, reviewed_word_count, duration_seconds
            """
        )
        return dict(cursor.fetchone())


def finish_session(
    conn: Connection,
    *,
    session_id: int,
    reviewed_word_count: int,
) -> dict[str, Any] | None:
    with conn.cursor(row_factory=dict_row) as cursor:
        cursor.execute(
            """
            update study_session
            set
                ended_at = now(),
                reviewed_word_count = %s,
                duration_seconds = greatest(
                    floor(extract(epoch from (now() - started_at)))::int,
                    0
                )
            where id = %s
            returning id, started_at, ended_at, reviewed_word_count, duration_seconds
            """,
            (reviewed_word_count, session_id),
        )
        row = cursor.fetchone()
        return dict(row) if row is not None else None


def get_session(conn: Connection, session_id: int) -> dict[str, Any] | None:
    with conn.cursor(row_factory=dict_row) as cursor:
        cursor.execute(
            """
            select id, started_at, ended_at, reviewed_word_count, duration_seconds
            from study_session
            where id = %s
            """,
            (session_id,),
        )
        row = cursor.fetchone()
        return dict(row) if row is not None else None


def list_sessions(conn: Connection, *, limit: int, offset: int) -> tuple[list[dict[str, Any]], int]:
    with conn.cursor(row_factory=dict_row) as cursor:
        cursor.execute("select count(*) as total from study_session")
        total = int(cursor.fetchone()["total"])

        cursor.execute(
            """
            select id, started_at, ended_at, reviewed_word_count, duration_seconds
            from study_session
            order by coalesce(ended_at, started_at) desc, id desc
            limit %s offset %s
            """,
            (limit, offset),
        )
        return [dict(row) for row in cursor.fetchall()], total
