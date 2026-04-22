import pytest
from pydantic import ValidationError

from app.schemas.review import ReviewAnswerRequest
from app.services.review_service import _correct_answers, _is_correct_answer


def test_review_answer_request_normalizes_answer() -> None:
    payload = ReviewAnswerRequest.model_validate(
        {
            "word_id": 1,
            "mode": "zh_to_en",
            "answer": " Record ",
        }
    )

    assert payload.answer == "Record"


def test_review_answer_request_rejects_blank_answer() -> None:
    with pytest.raises(ValidationError):
        ReviewAnswerRequest.model_validate(
            {
                "word_id": 1,
                "mode": "zh_to_en",
                "answer": " ",
            }
        )


def test_zh_to_en_answer_ignores_case() -> None:
    assert _is_correct_answer("record", ["Record"], "zh_to_en")


def test_en_to_zh_answer_requires_all_parts_of_speech_and_definitions() -> None:
    correct_answers = ["n 记录", "v 记录", "n 猫", "n 狗"]

    assert _is_correct_answer("n 记录 v 记录 n 猫 狗", correct_answers, "en_to_zh")


def test_en_to_zh_answer_order_does_not_matter() -> None:
    correct_answers = ["n 记录", "v 记录", "n 猫", "n 狗"]

    assert _is_correct_answer("v 记录 n 狗 猫 记录", correct_answers, "en_to_zh")


def test_en_to_zh_answer_rejects_missing_definition() -> None:
    correct_answers = ["n 记录", "v 记录", "n 猫", "n 狗"]

    assert not _is_correct_answer("n 记录 v 记录 n 猫", correct_answers, "en_to_zh")


def test_en_to_zh_answer_rejects_wrong_part_of_speech() -> None:
    correct_answers = ["n 记录", "v 记录", "n 猫", "n 狗"]

    assert not _is_correct_answer("n 记录 记录 猫 狗", correct_answers, "en_to_zh")


def test_en_to_zh_answer_rejects_definition_without_part_of_speech() -> None:
    assert not _is_correct_answer("记录", ["n 记录"], "en_to_zh")


def test_en_to_zh_correct_answers_include_part_of_speech() -> None:
    word = {
        "spelling": "record",
        "meanings": [
            {"part_of_speech": "n", "definition": "记录"},
            {"part_of_speech": "v", "definition": "记录"},
        ],
    }

    assert _correct_answers(word, "en_to_zh") == ["n 记录", "v 记录"]
