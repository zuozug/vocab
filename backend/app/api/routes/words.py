from fastapi import APIRouter, HTTPException, Query, status

from app.schemas.word import WordCreate, WordListResponse, WordRead, WordUpdate
from app.services import word_service
from app.services.errors import ConflictError, NotFoundError

router = APIRouter(prefix="/api/words", tags=["words"])


@router.get("", response_model=WordListResponse)
def list_words(
    keyword: str | None = Query(default=None, min_length=1),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> WordListResponse:
    return word_service.list_words(keyword=keyword, limit=limit, offset=offset)


@router.post("", response_model=WordRead, status_code=status.HTTP_201_CREATED)
def create_word(payload: WordCreate) -> WordRead:
    try:
        return word_service.create_word(payload)
    except ConflictError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.get("/{word_id}", response_model=WordRead)
def get_word(word_id: int) -> WordRead:
    try:
        return word_service.get_word(word_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.put("/{word_id}", response_model=WordRead)
def update_word(word_id: int, payload: WordUpdate) -> WordRead:
    try:
        return word_service.update_word(word_id, payload)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ConflictError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.delete("/{word_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_word(word_id: int) -> None:
    try:
        word_service.delete_word(word_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
