from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class TestInfo(BaseModel):
    __test__ = False

    id: str
    title: str
    subtitle: str
    questions_count: int
    my_leading: list[str] = Field(description="Titles of my leading categories, empty if not taken")


class QuestionRead(BaseModel):
    id: int
    a: str
    b: str


class TestRead(BaseModel):
    __test__ = False

    id: str
    title: str
    prompt: str
    questions: list[QuestionRead]


class TestAnswers(BaseModel):
    __test__ = False

    answers: dict[int, Literal["a", "b"]] = Field(
        description="Question id -> chosen statement, 'a' or 'b'. Answer every question."
    )


class CategoryScore(BaseModel):
    key: str
    title: str
    points: int
    max: int
    percent: int


class Advice(BaseModel):
    key: str
    title: str
    description: str
    advice: str


class ResultRead(BaseModel):
    test_id: str
    title: str
    scores: list[CategoryScore]  # strongest first
    leading: list[str]  # category keys; more than one only on a tie
    advice_title: str
    advice: list[Advice]  # for the leading categories
    taken_at: datetime
