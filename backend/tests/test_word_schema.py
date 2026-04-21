import pytest
from pydantic import ValidationError

from app.schemas.word import WordCreate


def test_word_create_normalizes_input() -> None:
    payload = WordCreate.model_validate(
        {
            "spelling": " record ",
            "senses": [
                {"part_of_speech": "n", "meanings": [" 记录 ", "唱片"]},
                {"part_of_speech": "v", "meanings": ["记录", "录制"]},
            ],
        }
    )

    assert payload.spelling == "record"
    assert payload.senses[0].meanings == ["记录", "唱片"]


def test_word_create_rejects_duplicate_senses() -> None:
    with pytest.raises(ValidationError):
        WordCreate.model_validate(
            {
                "spelling": "record",
                "senses": [
                    {"part_of_speech": "n", "meanings": ["记录"]},
                    {"part_of_speech": "n", "meanings": ["唱片"]},
                ],
            }
        )


def test_word_create_rejects_duplicate_meanings() -> None:
    with pytest.raises(ValidationError):
        WordCreate.model_validate(
            {
                "spelling": "record",
                "senses": [{"part_of_speech": "n", "meanings": ["记录", "记录"]}],
            }
        )
