from fastapi import APIRouter, HTTPException, Query, status

from app.schemas.session import (
    StudySessionCreateResponse,
    StudySessionFinishRequest,
    StudySessionListResponse,
    StudySessionRead,
)
from app.services import session_service
from app.services.errors import NotFoundError

router = APIRouter(prefix="/api/study-sessions", tags=["study-sessions"])


@router.get("", response_model=StudySessionListResponse)
def list_sessions(
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> StudySessionListResponse:
    return session_service.list_sessions(limit=limit, offset=offset)


@router.post("", response_model=StudySessionCreateResponse, status_code=status.HTTP_201_CREATED)
def create_session() -> StudySessionCreateResponse:
    return session_service.create_session()


@router.get("/{session_id}", response_model=StudySessionRead)
def get_session(session_id: int) -> StudySessionRead:
    try:
        return session_service.get_session(session_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("/{session_id}/finish", response_model=StudySessionRead)
def finish_session(session_id: int, payload: StudySessionFinishRequest) -> StudySessionRead:
    try:
        return session_service.finish_session(
            session_id=session_id,
            reviewed_word_count=payload.reviewed_word_count,
        )
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
