from app.core.database import get_connection
from app.repositories import session_repository
from app.schemas.session import (
    StudySessionCreateResponse,
    StudySessionListResponse,
    StudySessionRead,
)
from app.services.errors import NotFoundError


def create_session() -> StudySessionCreateResponse:
    with get_connection() as conn:
        session = session_repository.create_session(conn)

    return StudySessionCreateResponse.model_validate(session)


def finish_session(session_id: int, reviewed_word_count: int) -> StudySessionRead:
    with get_connection() as conn:
        session = session_repository.finish_session(
            conn,
            session_id=session_id,
            reviewed_word_count=reviewed_word_count,
        )

    if session is None:
        raise NotFoundError("Study session not found.")
    return StudySessionRead.model_validate(session)


def get_session(session_id: int) -> StudySessionRead:
    with get_connection() as conn:
        session = session_repository.get_session(conn, session_id)

    if session is None:
        raise NotFoundError("Study session not found.")
    return StudySessionRead.model_validate(session)


def list_sessions(limit: int, offset: int) -> StudySessionListResponse:
    with get_connection() as conn:
        items, total = session_repository.list_sessions(conn, limit=limit, offset=offset)

    return StudySessionListResponse(
        items=[StudySessionRead.model_validate(item) for item in items],
        total=total,
        limit=limit,
        offset=offset,
    )
