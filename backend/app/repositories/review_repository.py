from typing import Any

from psycopg import Connection
from psycopg.rows import dict_row


SECONDS_PER_DAY = 86_400


def apply_proficiency_decay(conn: Connection) -> int:
    with conn.cursor() as cursor:
        cursor.execute(
            """
            update review_state
            set
                proficiency = greatest(proficiency - elapsed_days, 0),
                last_decay_applied_at = last_decay_applied_at + elapsed_days * interval '1 day'
            from (
                select
                    word_id,
                    floor(extract(epoch from (now() - last_decay_applied_at)) / %s)::int
                        as elapsed_days
                from review_state
                where proficiency > 0
            ) decay
            where review_state.word_id = decay.word_id
                and decay.elapsed_days > 0
            """,
            (SECONDS_PER_DAY,),
        )
        return cursor.rowcount


def list_next_words(conn: Connection, *, limit: int) -> list[dict[str, Any]]:
    with conn.cursor(row_factory=dict_row) as cursor:
        cursor.execute(
            """
            select
                w.id as word_id,
                w.spelling,
                rs.proficiency,
                rs.last_reviewed_at,
                ws.part_of_speech::text as part_of_speech,
                m.id as meaning_id,
                m.definition
            from (
                select w.id
                from word w
                join review_state rs on rs.word_id = w.id
                order by rs.proficiency asc, rs.last_reviewed_at asc, w.id asc
                limit %s
            ) selected
            join word w on w.id = selected.id
            join review_state rs on rs.word_id = w.id
            left join word_sense ws on ws.word_id = w.id
            left join meaning m on m.sense_id = ws.id
            order by rs.proficiency asc, rs.last_reviewed_at asc, w.id asc, ws.id asc, m.id asc
            """,
            (limit,),
        )
        return _build_review_words(list(cursor.fetchall()))


def get_answer_target(conn: Connection, word_id: int) -> dict[str, Any] | None:
    with conn.cursor(row_factory=dict_row) as cursor:
        cursor.execute(
            """
            select
                w.id as word_id,
                w.spelling,
                rs.proficiency,
                rs.last_reviewed_at,
                ws.part_of_speech::text as part_of_speech,
                m.id as meaning_id,
                m.definition
            from word w
            join review_state rs on rs.word_id = w.id
            left join word_sense ws on ws.word_id = w.id
            left join meaning m on m.sense_id = ws.id
            where w.id = %s
            order by ws.id asc, m.id asc
            """,
            (word_id,),
        )
        words = _build_review_words(list(cursor.fetchall()))
        return words[0] if words else None


def update_review_state(conn: Connection, *, word_id: int, is_correct: bool) -> dict[str, Any]:
    with conn.cursor(row_factory=dict_row) as cursor:
        if is_correct:
            cursor.execute(
                """
                update review_state
                set
                    proficiency = proficiency + 1,
                    last_reviewed_at = now(),
                    last_decay_applied_at = now()
                where word_id = %s
                returning proficiency, last_reviewed_at
                """,
                (word_id,),
            )
        else:
            cursor.execute(
                """
                update review_state
                set
                    proficiency = greatest(proficiency - 2, 0),
                    last_reviewed_at = now(),
                    last_decay_applied_at = now()
                where word_id = %s
                returning proficiency, last_reviewed_at
                """,
                (word_id,),
            )

        row = cursor.fetchone()
        if row is None:
            raise RuntimeError("Review state could not be updated.")
        return dict(row)


def _build_review_words(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    words: list[dict[str, Any]] = []
    by_id: dict[int, dict[str, Any]] = {}
    seen_meanings: set[int] = set()

    for row in rows:
        word_id = row["word_id"]
        word = by_id.get(word_id)
        if word is None:
            word = {
                "word_id": word_id,
                "spelling": row["spelling"],
                "proficiency": row["proficiency"],
                "last_reviewed_at": row["last_reviewed_at"],
                "meanings": [],
            }
            by_id[word_id] = word
            words.append(word)

        meaning_id = row["meaning_id"]
        if meaning_id is not None and meaning_id not in seen_meanings:
            word["meanings"].append(
                {
                    "id": meaning_id,
                    "part_of_speech": row["part_of_speech"],
                    "definition": row["definition"],
                }
            )
            seen_meanings.add(meaning_id)

    return words
