from psycopg import errors

from app.core.database import get_connection
from app.repositories import word_repository
from app.schemas.word import WordCreate, WordListResponse, WordRead, WordUpdate
from app.services.errors import ConflictError, NotFoundError


def list_words(keyword: str | None, limit: int, offset: int) -> WordListResponse:
    with get_connection() as conn:
        items, total = word_repository.list_words(
            conn,
            keyword=keyword.strip() if keyword else None,
            limit=limit,
            offset=offset,
        )

    return WordListResponse(
        items=[WordRead.model_validate(item) for item in items],
        total=total,
        limit=limit,
        offset=offset,
    )


def get_word(word_id: int) -> WordRead:
    with get_connection() as conn:
        word = word_repository.get_word(conn, word_id)

    if word is None:
        raise NotFoundError("Word not found.")
    return WordRead.model_validate(word)


def create_word(payload: WordCreate) -> WordRead:
    try:
        with get_connection() as conn:
            word = word_repository.create_word(conn, payload)
    except errors.UniqueViolation as exc:
        raise ConflictError("Word spelling already exists.") from exc

    return WordRead.model_validate(word)


def update_word(word_id: int, payload: WordUpdate) -> WordRead:
    try:
        with get_connection() as conn:
            word = word_repository.update_word(conn, word_id, payload)
    except errors.UniqueViolation as exc:
        raise ConflictError("Word spelling already exists.") from exc

    if word is None:
        raise NotFoundError("Word not found.")
    return WordRead.model_validate(word)


def delete_word(word_id: int) -> None:
    with get_connection() as conn:
        deleted = word_repository.delete_word(conn, word_id)

    if not deleted:
        raise NotFoundError("Word not found.")
