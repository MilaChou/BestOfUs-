"""Filtering shared by the couple's ideas and the built-in catalog."""

from dataclasses import dataclass
from typing import Protocol

from app.enums import BUDGET_ORDER, Budget, Cuisine, Format, TimeOfDay


class Taggable(Protocol):
    """Anything with the tags we filter on: an Idea or a CatalogActivity."""

    format: Format
    cuisine: Cuisine | None
    budget: Budget | None
    times_of_day: list[str] | tuple[TimeOfDay, ...]


@dataclass
class Filters:
    time_of_day: TimeOfDay | None = None
    format: Format | None = None
    cuisine: Cuisine | None = None
    max_budget: Budget | None = None

    def matches(self, item: Taggable) -> bool:
        if self.format is not None and item.format != self.format:
            return False
        if self.cuisine is not None and item.cuisine != self.cuisine:
            return False
        # No times set on an idea means "any time".
        if (
            self.time_of_day is not None
            and item.times_of_day
            and self.time_of_day not in item.times_of_day
        ):
            return False
        # No budget set on an idea means "we don't know yet" — don't hide it.
        if (
            self.max_budget is not None
            and item.budget is not None
            and BUDGET_ORDER.index(item.budget) > BUDGET_ORDER.index(self.max_budget)
        ):
            return False
        return True
