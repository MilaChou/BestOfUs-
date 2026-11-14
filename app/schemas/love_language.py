from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from app.enums import LoveLanguage
from app.love_language import QUESTION_IDS, SCALE_MAX, SCALE_MIN


class QuestionRead(BaseModel):
    id: int
    text: str


class TestRead(BaseModel):
    scale: str = f"{SCALE_MIN} — совсем не про меня, {SCALE_MAX} — это точно про меня"
    questions: list[QuestionRead]


class TestAnswers(BaseModel):
    answers: dict[int, int] = Field(
        description="Question id -> rating 1–5. Every question must be answered.",
        examples=[{str(i): 3 for i in range(1, 21)}],
    )

    @field_validator("answers")
    @classmethod
    def check_answers(cls, answers: dict[int, int]) -> dict[int, int]:
        if set(answers) != QUESTION_IDS:
            missing = sorted(QUESTION_IDS - set(answers))
            extra = sorted(set(answers) - QUESTION_IDS)
            raise ValueError(
                f"answer every question exactly once (missing: {missing}, unknown: {extra})"
            )
        if any(not SCALE_MIN <= value <= SCALE_MAX for value in answers.values()):
            raise ValueError(f"every rating must be from {SCALE_MIN} to {SCALE_MAX}")
        return answers


class LanguageScore(BaseModel):
    language: LoveLanguage
    title: str
    percent: int


class LanguageTip(BaseModel):
    language: LoveLanguage
    title: str
    description: str
    how_to_show: str


class ResultRead(BaseModel):
    scores: list[LanguageScore]  # strongest first
    leading: list[LoveLanguage]  # can be more than one
    tips: list[LanguageTip]  # for the leading languages
    taken_at: datetime
