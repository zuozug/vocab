from fastapi import APIRouter, HTTPException, Query, status

from app.schemas.review import (
    ReviewAnswerRequest,
    ReviewAnswerResponse,
    ReviewMode,
    ReviewNextResponse,
)
from app.services import review_service
from app.services.errors import NotFoundError

router = APIRouter(prefix="/api/reviews", tags=["reviews"])


@router.get("/next", response_model=ReviewNextResponse)
def get_next_reviews(
    mode: ReviewMode = Query(default="zh_to_en"),
    limit: int = Query(default=10, ge=1, le=100),
) -> ReviewNextResponse:
    return review_service.get_next_reviews(mode=mode, limit=limit)


@router.post("/answer", response_model=ReviewAnswerResponse)
def submit_answer(payload: ReviewAnswerRequest) -> ReviewAnswerResponse:
    try:
        return review_service.submit_answer(payload)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
