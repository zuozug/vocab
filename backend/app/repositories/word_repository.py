from typing import Any

from psycopg import Connection
from psycopg.rows import dict_row

from app.schemas.word import WordCreate, WordUpdate


def _build_word(rows: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not rows:
        return None

    first = rows[0]
    word = {
        "id": first["word_id"],
        "spelling": first["spelling"],
        "created_at": first["word_created_at"],
        "updated_at": first["word_updated_at"],
        "senses": [],
    }
    senses: dict[int, dict[str, Any]] = {}

    for row in rows:
        sense_id = row["sense_id"]
        if sense_id is None:
            continue

        sense = senses.get(sense_id)
        if sense is None:
            sense = {
                "id": sense_id,
                "part_of_speech": row["part_of_speech"],
                "created_at": row["sense_created_at"],
                "updated_at": row["sense_updated_at"],
                "meanings": [],
            }
            senses[sense_id] = sense
            word["senses"].append(sense)

        meaning_id = row["meaning_id"]
        if meaning_id is not None:
            sense["meanings"].append(
                {
                    "id": meaning_id,
                    "definition": row["definition"],
                    "created_at": row["meaning_created_at"],
                    "updated_at": row["meaning_updated_at"],
                }
            )

    return word


def get_word(conn: Connection, word_id: int) -> dict[str, Any] | None:
    with conn.cursor(row_factory=dict_row) as cursor:
        cursor.execute(
            """
            select
                w.id as word_id,
                w.spelling,
                w.created_at as word_created_at,
                w.updated_at as word_updated_at,
                ws.id as sense_id,
                ws.part_of_speech::text as part_of_speech,
                ws.created_at as sense_created_at,
                ws.updated_at as sense_updated_at,
                m.id as meaning_id,
                m.definition,
                m.created_at as meaning_created_at,
                m.updated_at as meaning_updated_at
            from word w
            left join word_sense ws on ws.word_id = w.id
            left join meaning m on m.sense_id = ws.id
            where w.id = %s
            order by ws.id, m.id
            """,
            (word_id,),
        )
        return _build_word(list(cursor.fetchall()))


def list_words(
    conn: Connection,
    *,
    keyword: str | None,
    limit: int,
    offset: int,
) -> tuple[list[dict[str, Any]], int]:
    where = ""
    params: list[Any] = []
    if keyword:
        where = "where spelling ilike %s"
        params.append(f"%{keyword}%")

    with conn.cursor() as cursor:
        cursor.execute(f"select count(*) from word {where}", params)
        total = int(cursor.fetchone()[0])

        cursor.execute(
            f"select id from word {where} order by spelling asc, id asc limit %s offset %s",
            [*params, limit, offset],
        )
        ids = [row[0] for row in cursor.fetchall()]

    return [word for word_id in ids if (word := get_word(conn, word_id)) is not None], total


def create_word(conn: Connection, payload: WordCreate) -> dict[str, Any]:
    with conn.cursor() as cursor:
        cursor.execute(
            "insert into word(spelling) values (%s) returning id",
            (payload.spelling,),
        )
        word_id = int(cursor.fetchone()[0])

        _insert_senses(cursor, word_id, payload.senses)

        cursor.execute("insert into review_state(word_id) values (%s)", (word_id,))

    word = get_word(conn, word_id)
    if word is None:
        raise RuntimeError("Created word could not be loaded.")
    return word


def update_word(conn: Connection, word_id: int, payload: WordUpdate) -> dict[str, Any] | None:
    with conn.cursor() as cursor:
        cursor.execute(
            "update word set spelling = %s where id = %s returning id",
            (payload.spelling, word_id),
        )
        row = cursor.fetchone()
        if row is None:
            return None

        cursor.execute(
            "delete from meaning where sense_id in (select id from word_sense where word_id = %s)",
            (word_id,),
        )
        cursor.execute("delete from word_sense where word_id = %s", (word_id,))
        _insert_senses(cursor, word_id, payload.senses)
        cursor.execute(
            "insert into review_state(word_id) values (%s) on conflict (word_id) do nothing",
            (word_id,),
        )

    return get_word(conn, word_id)


def delete_word(conn: Connection, word_id: int) -> bool:
    with conn.cursor() as cursor:
        cursor.execute(
            "delete from meaning where sense_id in (select id from word_sense where word_id = %s)",
            (word_id,),
        )
        cursor.execute("delete from word_sense where word_id = %s", (word_id,))
        cursor.execute("delete from review_state where word_id = %s", (word_id,))
        cursor.execute("delete from word where id = %s returning id", (word_id,))
        return cursor.fetchone() is not None


def _insert_senses(cursor: Any, word_id: int, senses: list[Any]) -> None:
    for sense in senses:
        cursor.execute(
            """
            insert into word_sense(word_id, part_of_speech)
            values (%s, %s::part_of_speech_enum)
            returning id
            """,
            (word_id, sense.part_of_speech),
        )
        sense_id = int(cursor.fetchone()[0])
        for definition in sense.meanings:
            cursor.execute(
                "insert into meaning(sense_id, definition) values (%s, %s)",
                (sense_id, definition),
            )
