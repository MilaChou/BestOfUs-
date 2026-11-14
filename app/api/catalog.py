from fastapi import APIRouter

from app.catalog import ACTIVITIES, CatalogActivity
from app.enums import Budget, Cuisine, Format, TimeOfDay
from app.schemas.idea import CatalogActivityRead
from app.suggest import Filters

router = APIRouter(prefix="/catalog", tags=["catalog"])


@router.get("/activities", response_model=list[CatalogActivityRead])
def list_activities(
    time_of_day: TimeOfDay | None = None,
    format: Format | None = None,
    cuisine: Cuisine | None = None,
    max_budget: Budget | None = None,
) -> list[CatalogActivity]:
    """The built-in catalog that «Подкинь идею» falls back to. Open to everyone."""
    filters = Filters(time_of_day, format, cuisine, max_budget)
    return [a for a in ACTIVITIES if filters.matches(a)]
