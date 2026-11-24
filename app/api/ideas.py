import random
from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, HTTPException, Query, status
from sqlalchemy import func, select

from app.api.deps import CurrentCouple, CurrentUser
from app.catalog import ACTIVITIES, ACTIVITIES_BY_ID
from app.database import DbSession
from app.enums import BUDGET_ORDER, Budget, Cuisine, Format, NotificationType, TimeOfDay
from app.models import Couple, Idea, IdeaWant
from app.notifications import notify_partner
from app.schemas.idea import (
    CatalogActivityRead,
    IdeaCreate,
    IdeaDone,
    IdeaRead,
    IdeaUpdate,
    Suggestion,
)
from app.suggest import Filters

router = APIRouter(prefix="/couple/ideas", tags=["ideas"])


def get_couple_idea(idea_id: int, couple: Couple, db: DbSession) -> Idea:
    """The idea, but only if it belongs to this couple — otherwise 404."""
    idea = db.get(Idea, idea_id)
    if idea is None or idea.couple_id != couple.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Idea not found")
    return idea


def notify_idea_added(db: DbSession, background: BackgroundTasks, user, idea: Idea) -> None:
    notify_partner(
        db,
        background,
        user,
        NotificationType.IDEA_ADDED,
        "Новая идея",
        f"«{idea.title}»",
        {"idea_id": idea.id},
    )


@router.get("", response_model=list[IdeaRead])
def list_ideas(
    couple: CurrentCouple,
    db: DbSession,
    format: Format | None = None,
    is_done: bool | None = None,
    max_budget: Budget | None = None,
    both_want: bool | None = None,
) -> list[Idea]:
    """The couple's ideas: not done first, newest first. All filters are optional."""
    stmt = select(Idea).where(Idea.couple_id == couple.id)
    if format is not None:
        stmt = stmt.where(Idea.format == format)
    if is_done is not None:
        stmt = stmt.where(Idea.is_done == is_done)
    if max_budget is not None:
        allowed = BUDGET_ORDER[: BUDGET_ORDER.index(max_budget) + 1]
        stmt = stmt.where(Idea.budget.in_(allowed) | Idea.budget.is_(None))
    if both_want is not None:
        wanted_by_two = (
            select(IdeaWant.idea_id).group_by(IdeaWant.idea_id).having(func.count() >= 2)
        )
        condition = Idea.id.in_(wanted_by_two)
        stmt = stmt.where(condition if both_want else ~condition)
    stmt = stmt.order_by(Idea.is_done, Idea.created_at.desc(), Idea.id.desc())
    return list(db.scalars(stmt))


@router.post("", response_model=IdeaRead, status_code=status.HTTP_201_CREATED)
def create_idea(
    data: IdeaCreate,
    user: CurrentUser,
    couple: CurrentCouple,
    db: DbSession,
    background: BackgroundTasks,
) -> Idea:
    # The author obviously wants it, so their ❤️ is there from the start.
    idea = Idea(**data.model_dump(), couple=couple, author_id=user.id)
    idea.wants.append(IdeaWant(user_id=user.id))
    db.add(idea)
    db.flush()
    notify_idea_added(db, background, user, idea)
    db.commit()
    db.refresh(idea)
    return idea


@router.get("/suggest", response_model=Suggestion)
def suggest(
    couple: CurrentCouple,
    db: DbSession,
    time_of_day: TimeOfDay | None = None,
    format: Format | None = None,
    cuisine: Cuisine | None = None,
    max_budget: Budget | None = None,
    exclude_ideas: Annotated[list[int] | None, Query()] = None,
    exclude_catalog: Annotated[list[str] | None, Query()] = None,
) -> Suggestion:
    """«Подкинь идею»: one random activity for the chosen filters.

    The couple's own not-done ideas come first. Only when none of them match,
    an activity from the built-in catalog is suggested. For "ещё", send the ids
    you've already been shown in exclude_ideas / exclude_catalog.
    """
    filters = Filters(time_of_day, format, cuisine, max_budget)
    skip_ideas, skip_catalog = set(exclude_ideas or []), set(exclude_catalog or [])

    own = db.scalars(select(Idea).where(Idea.couple_id == couple.id, Idea.is_done.is_(False)))
    ideas = [i for i in own if i.id not in skip_ideas and filters.matches(i)]
    if ideas:
        return Suggestion(source="idea", idea=IdeaRead.model_validate(random.choice(ideas)))

    already_saved = set(
        db.scalars(
            select(Idea.catalog_id).where(Idea.couple_id == couple.id, Idea.catalog_id.is_not(None))
        )
    )
    activities = [
        a
        for a in ACTIVITIES
        if a.id not in skip_catalog and a.id not in already_saved and filters.matches(a)
    ]
    if activities:
        activity = CatalogActivityRead.model_validate(random.choice(activities))
        return Suggestion(source="catalog", activity=activity)

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Nothing matches these filters — try fewer of them",
    )


@router.post(
    "/from-catalog/{catalog_id}", response_model=IdeaRead, status_code=status.HTTP_201_CREATED
)
def save_from_catalog(
    catalog_id: str,
    user: CurrentUser,
    couple: CurrentCouple,
    db: DbSession,
    background: BackgroundTasks,
) -> Idea:
    """Liked a suggestion from the catalog? Save it to your own ideas."""
    activity = ACTIVITIES_BY_ID.get(catalog_id)
    if activity is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such activity")
    exists = db.scalar(
        select(Idea.id).where(Idea.couple_id == couple.id, Idea.catalog_id == catalog_id)
    )
    if exists is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="This activity is already in your ideas"
        )

    idea = Idea(
        couple=couple,
        author_id=user.id,
        catalog_id=activity.id,
        title=activity.title,
        description=activity.description,
        format=activity.format,
        cuisine=activity.cuisine,
        budget=activity.budget,
        times_of_day=list(activity.times_of_day),
    )
    idea.wants.append(IdeaWant(user_id=user.id))
    db.add(idea)
    db.flush()
    notify_idea_added(db, background, user, idea)
    db.commit()
    db.refresh(idea)
    return idea


@router.get("/{idea_id}", response_model=IdeaRead)
def read_idea(idea_id: int, couple: CurrentCouple, db: DbSession) -> Idea:
    return get_couple_idea(idea_id, couple, db)


@router.patch("/{idea_id}", response_model=IdeaRead)
def update_idea(idea_id: int, data: IdeaUpdate, couple: CurrentCouple, db: DbSession) -> Idea:
    idea = get_couple_idea(idea_id, couple, db)
    changes = data.model_dump(exclude_unset=True)

    new_format = changes.get("format", idea.format)
    if "cuisine" in changes:
        new_cuisine = changes["cuisine"]
    else:
        # Moving an idea out of "food" drops the cuisine instead of failing.
        new_cuisine = idea.cuisine if new_format == Format.FOOD else None
    if new_cuisine is not None and new_format != Format.FOOD:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="cuisine can be set only when format is 'food'",
        )

    for field, value in changes.items():
        setattr(idea, field, value)
    idea.cuisine = new_cuisine
    db.commit()
    db.refresh(idea)
    return idea


@router.delete("/{idea_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_idea(idea_id: int, couple: CurrentCouple, db: DbSession) -> None:
    db.delete(get_couple_idea(idea_id, couple, db))
    db.commit()


@router.post("/{idea_id}/done", response_model=IdeaRead)
def mark_done(idea_id: int, data: IdeaDone, couple: CurrentCouple, db: DbSession) -> Idea:
    """Mark as done, optionally with a 1–5 rating and a short review."""
    idea = get_couple_idea(idea_id, couple, db)
    idea.is_done = True
    idea.done_at = datetime.now(UTC)
    idea.rating = data.rating
    idea.review = data.review
    db.commit()
    db.refresh(idea)
    return idea


@router.post("/{idea_id}/undone", response_model=IdeaRead)
def mark_undone(idea_id: int, couple: CurrentCouple, db: DbSession) -> Idea:
    idea = get_couple_idea(idea_id, couple, db)
    idea.is_done = False
    idea.done_at = idea.rating = idea.review = None
    db.commit()
    db.refresh(idea)
    return idea


@router.post("/{idea_id}/want", response_model=IdeaRead)
def want(
    idea_id: int,
    user: CurrentUser,
    couple: CurrentCouple,
    db: DbSession,
    background: BackgroundTasks,
) -> Idea:
    """«Хочу тоже!» ❤️ Pressing it twice changes nothing."""
    idea = get_couple_idea(idea_id, couple, db)
    if user.id not in idea.wanted_by:
        idea.wants.append(IdeaWant(user_id=user.id))
        both = len(idea.wants) >= 2
        title = "Вы оба этого хотите!" if both else "Хочет тоже!"
        notify_partner(
            db,
            background,
            user,
            NotificationType.IDEA_WANTED,
            title,
            f"«{idea.title}»",
            {"idea_id": idea.id},
        )
        db.commit()
        db.refresh(idea)
    return idea


@router.delete("/{idea_id}/want", response_model=IdeaRead)
def unwant(idea_id: int, user: CurrentUser, couple: CurrentCouple, db: DbSession) -> Idea:
    idea = get_couple_idea(idea_id, couple, db)
    idea.wants = [w for w in idea.wants if w.user_id != user.id]
    db.commit()
    db.refresh(idea)
    return idea
