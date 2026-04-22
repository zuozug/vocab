from collections import Counter

from app.core.database import get_connection
from app.repositories import review_repository
from app.schemas.review import (
    ReviewAnswerRequest,
    ReviewAnswerResponse,
    ReviewMode,
    ReviewNextResponse,
    ReviewWordRead,
)
from app.services.errors import NotFoundError


PART_OF_SPEECH_VALUES = {"n", "v", "adj", "adv", "prep", "pron", "conj", "interj", "num", "art"}


def get_next_reviews(mode: ReviewMode, limit: int) -> ReviewNextResponse:
    with get_connection() as conn:
        review_repository.apply_proficiency_decay(conn)
        words = review_repository.list_next_words(conn, limit=limit)

    return ReviewNextResponse(
        mode=mode,
        items=[ReviewWordRead.model_validate(word) for word in words],
    )


def submit_answer(payload: ReviewAnswerRequest) -> ReviewAnswerResponse:
    with get_connection() as conn:
        target = review_repository.get_answer_target(conn, payload.word_id)
        if target is None:
            raise NotFoundError("Word not found.")

        correct_answers = _correct_answers(target, payload.mode)
        is_correct = _is_correct_answer(payload.answer, correct_answers, payload.mode)
        updated_state = review_repository.update_review_state(
            conn,
            word_id=payload.word_id,
            is_correct=is_correct,
        )

    return ReviewAnswerResponse(
        word_id=payload.word_id,
        mode=payload.mode,
        is_correct=is_correct,
        correct_answers=correct_answers,
        proficiency=updated_state["proficiency"],
        last_reviewed_at=updated_state["last_reviewed_at"],
    )


def _correct_answers(word: dict, mode: ReviewMode) -> list[str]:
    if mode == "zh_to_en":
        return [word["spelling"]]
    return [
        f"{meaning['part_of_speech']} {meaning['definition']}" for meaning in word["meanings"]
    ]


def _is_correct_answer(answer: str, correct_answers: list[str], mode: ReviewMode) -> bool:
    if mode == "zh_to_en":
        normalized_answer = answer.casefold()
        return any(normalized_answer == item.casefold() for item in correct_answers)

    submitted_items = _parse_en_to_zh_answer(answer)
    if submitted_items is None:
        return False

    correct_items = _parse_en_to_zh_answer(" ".join(correct_answers))
    return submitted_items == correct_items


def _parse_en_to_zh_answer(answer: str) -> Counter[tuple[str, str]] | None:
    current_part_of_speech: str | None = None
    parsed: Counter[tuple[str, str]] = Counter()

    for token in answer.split():
        if token in PART_OF_SPEECH_VALUES:
            current_part_of_speech = token
            continue
        if current_part_of_speech is None:
            return None
        parsed[(current_part_of_speech, token)] += 1

    return parsed if parsed else None
