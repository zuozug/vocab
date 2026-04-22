from datetime import datetime

from pydantic import BaseModel, Field


class StudySessionCreateResponse(BaseModel):
    id: int
    started_at: datetime
    ended_at: datetime | None
    reviewed_word_count: int
    duration_seconds: int | None


class StudySessionFinishRequest(BaseModel):
    reviewed_word_count: int = Field(ge=0)


class StudySessionRead(BaseModel):
    id: int
    started_at: datetime
    ended_at: datetime | None
    reviewed_word_count: int
    duration_seconds: int | None


class StudySessionListResponse(BaseModel):
    items: list[StudySessionRead]
    total: int
    limit: int
    offset: int
