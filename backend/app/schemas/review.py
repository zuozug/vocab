from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator

from app.schemas.word import PartOfSpeech

ReviewMode = Literal["zh_to_en", "en_to_zh"]


class ReviewMeaningRead(BaseModel):
    id: int
    part_of_speech: PartOfSpeech
    definition: str


class ReviewWordRead(BaseModel):
    word_id: int
    spelling: str
    meanings: list[ReviewMeaningRead]
    proficiency: int
    last_reviewed_at: datetime


class ReviewNextResponse(BaseModel):
    mode: ReviewMode
    items: list[ReviewWordRead]


class ReviewAnswerRequest(BaseModel):
    word_id: int
    mode: ReviewMode
    answer: str = Field(min_length=1)

    @field_validator("answer")
    @classmethod
    def normalize_answer(cls, value: str) -> str:
        answer = value.strip()
        if not answer:
            raise ValueError("answer cannot be empty")
        return answer


class ReviewAnswerResponse(BaseModel):
    word_id: int
    mode: ReviewMode
    is_correct: bool
    correct_answers: list[str]
    proficiency: int
    last_reviewed_at: datetime
