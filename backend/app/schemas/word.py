from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator

PartOfSpeech = Literal["n", "v", "adj", "adv", "prep", "pron", "conj", "interj", "num", "art"]


class WordSenseInput(BaseModel):
    part_of_speech: PartOfSpeech
    meanings: list[str] = Field(min_length=1)

    @field_validator("meanings")
    @classmethod
    def normalize_meanings(cls, value: list[str]) -> list[str]:
        meanings = [item.strip() for item in value]
        if any(not item for item in meanings):
            raise ValueError("meaning definition cannot be empty")
        if len(set(meanings)) != len(meanings):
            raise ValueError("meaning definitions cannot be duplicated in one sense")
        return meanings


class WordCreate(BaseModel):
    spelling: str = Field(min_length=1, max_length=128)
    senses: list[WordSenseInput] = Field(min_length=1)

    @field_validator("spelling")
    @classmethod
    def normalize_spelling(cls, value: str) -> str:
        spelling = value.strip()
        if not spelling:
            raise ValueError("spelling cannot be empty")
        return spelling

    @model_validator(mode="after")
    def validate_unique_senses(self) -> "WordCreate":
        parts = [sense.part_of_speech for sense in self.senses]
        if len(set(parts)) != len(parts):
            raise ValueError("part_of_speech cannot be duplicated in one word")
        return self


class WordUpdate(WordCreate):
    pass


class MeaningRead(BaseModel):
    id: int
    definition: str
    created_at: datetime
    updated_at: datetime


class WordSenseRead(BaseModel):
    id: int
    part_of_speech: PartOfSpeech
    meanings: list[MeaningRead]
    created_at: datetime
    updated_at: datetime


class WordRead(BaseModel):
    id: int
    spelling: str
    senses: list[WordSenseRead]
    created_at: datetime
    updated_at: datetime


class WordListResponse(BaseModel):
    items: list[WordRead]
    total: int
    limit: int
    offset: int
