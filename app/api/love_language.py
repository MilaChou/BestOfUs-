from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.api.deps import CurrentUser
from app.database import DbSession
from app.enums import LoveLanguage
from app.love_language import INFO, QUESTIONS, leading, score
from app.models import LoveLanguageResult, User
from app.schemas.love_language import (
    LanguageScore,
    LanguageTip,
    QuestionRead,
    ResultRead,
    TestAnswers,
    TestRead,
)

router = APIRouter(prefix="/love-language", tags=["love language"])


def to_read(result: LoveLanguageResult) -> ResultRead:
    ordered = sorted(result.scores.items(), key=lambda kv: -kv[1])
    scores = [
        LanguageScore(language=lang, title=INFO[LoveLanguage(lang)].title, percent=percent)
        for lang, percent in ordered
    ]
    top = leading(result.scores)
    tips = [
        LanguageTip(
            language=lang,
            title=INFO[lang].title,
            description=INFO[lang].description,
            how_to_show=INFO[lang].how_to_show,
        )
        for lang in top
    ]
    return ResultRead(scores=scores, leading=top, tips=tips, taken_at=result.taken_at)


def result_of(user: User, db: DbSession) -> LoveLanguageResult | None:
    return db.scalar(select(LoveLanguageResult).where(LoveLanguageResult.user_id == user.id))


@router.get("/test", response_model=TestRead)
def get_test() -> TestRead:
    """The 20 statements to rate. Which language each belongs to is not shown."""
    return TestRead(questions=[QuestionRead(id=q.id, text=q.text) for q in QUESTIONS])


@router.post("/test", response_model=ResultRead)
def submit_test(data: TestAnswers, user: CurrentUser, db: DbSession) -> ResultRead:
    """Send all answers, get your result. Taking it again replaces the old result."""
    scores = score(data.answers)
    result = result_of(user, db)
    if result is None:
        result = LoveLanguageResult(user_id=user.id, scores=scores)
        db.add(result)
    else:
        result.scores = scores
    db.commit()
    db.refresh(result)
    return to_read(result)


@router.get("/me", response_model=ResultRead)
def my_result(user: CurrentUser, db: DbSession) -> ResultRead:
    result = result_of(user, db)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Take the test first")
    return to_read(result)


@router.get("/partner", response_model=ResultRead)
def partner_result(user: CurrentUser, db: DbSession) -> ResultRead:
    """The partner's languages and how to show them love."""
    if user.partner is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="You have no partner yet")
    result = result_of(user.partner, db)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Your partner hasn't taken the test yet"
        )
    return to_read(result)
