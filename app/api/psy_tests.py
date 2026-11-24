from fastapi import APIRouter, BackgroundTasks, HTTPException, status
from sqlalchemy import select

from app.api.deps import CurrentUser
from app.database import DbSession
from app.enums import NotificationType
from app.models import TestResult, User
from app.notifications import notify_partner
from app.psy_tests import TESTS, PsyTest, leading, score
from app.schemas.psy_test import (
    Advice,
    CategoryScore,
    QuestionRead,
    ResultRead,
    TestAnswers,
    TestInfo,
    TestRead,
)

router = APIRouter(prefix="/tests", tags=["tests"])


def get_test(test_id: str) -> PsyTest:
    test = TESTS.get(test_id)
    if test is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such test")
    return test


def result_of(user: User, test: PsyTest, db: DbSession) -> TestResult | None:
    return db.scalar(
        select(TestResult).where(TestResult.user_id == user.id, TestResult.test_id == test.id)
    )


def to_read(test: PsyTest, result: TestResult) -> ResultRead:
    titles = {c.key: c for c in test.categories}
    top = leading(result.scores)
    ordered = sorted(test.categories, key=lambda c: -result.scores.get(c.key, 0))
    return ResultRead(
        test_id=test.id,
        title=test.title,
        scores=[
            CategoryScore(
                key=c.key,
                title=c.title,
                points=result.scores.get(c.key, 0),
                max=test.max_points,
                percent=round(result.scores.get(c.key, 0) * 100 / test.max_points),
            )
            for c in ordered
        ],
        leading=top,
        advice_title=test.advice_title,
        advice=[
            Advice(
                key=k,
                title=titles[k].title,
                description=titles[k].description,
                advice=titles[k].advice,
            )
            for k in top
        ],
        taken_at=result.taken_at,
    )


@router.get("", response_model=list[TestInfo])
def list_tests(user: CurrentUser, db: DbSession) -> list[TestInfo]:
    """All tests, with my leading result if I've taken it."""
    infos = []
    for test in TESTS.values():
        result = result_of(user, test, db)
        titles = {c.key: c.title for c in test.categories}
        infos.append(
            TestInfo(
                id=test.id,
                title=test.title,
                subtitle=test.subtitle,
                questions_count=len(test.questions),
                my_leading=[titles[k] for k in leading(result.scores)] if result else [],
            )
        )
    return infos


@router.get("/{test_id}", response_model=TestRead)
def read_test(test_id: str) -> TestRead:
    """The questions: two statements each. Which category each belongs to is not shown."""
    test = get_test(test_id)
    return TestRead(
        id=test.id,
        title=test.title,
        prompt=test.prompt,
        questions=[QuestionRead(id=q.id, a=q.a_text, b=q.b_text) for q in test.questions],
    )


@router.post("/{test_id}", response_model=ResultRead)
def submit(
    test_id: str,
    data: TestAnswers,
    user: CurrentUser,
    db: DbSession,
    background: BackgroundTasks,
) -> ResultRead:
    """Send all answers, get the result. Taking it again replaces the old result."""
    test = get_test(test_id)
    expected = {q.id for q in test.questions}
    if set(data.answers) != expected:
        missing = sorted(expected - set(data.answers))
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"Answer every question exactly once (missing: {missing})",
        )

    points = score(test, data.answers)
    result = result_of(user, test, db)
    if result is None:
        result = TestResult(user_id=user.id, test_id=test.id, scores=points)
        db.add(result)
    else:
        result.scores = points
    notify_partner(
        db,
        background,
        user,
        NotificationType.LOVE_LANGUAGE_DONE,
        test.title,
        "тест пройден — посмотри результат",
        {"screen": "test_partner", "test": test.id},
    )
    db.commit()
    db.refresh(result)
    return to_read(test, result)


@router.get("/{test_id}/me", response_model=ResultRead)
def my_result(test_id: str, user: CurrentUser, db: DbSession) -> ResultRead:
    test = get_test(test_id)
    result = result_of(user, test, db)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Take the test first")
    return to_read(test, result)


@router.get("/{test_id}/partner", response_model=ResultRead)
def partner_result(test_id: str, user: CurrentUser, db: DbSession) -> ResultRead:
    test = get_test(test_id)
    if user.partner is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="You have no partner yet")
    result = result_of(user.partner, test, db)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Your partner hasn't taken the test yet"
        )
    return to_read(test, result)
