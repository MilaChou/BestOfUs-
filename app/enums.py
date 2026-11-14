"""Fixed lists of values shared by ideas, the activity catalog and filters."""

from enum import StrEnum


class TimeOfDay(StrEnum):
    MORNING = "morning"
    DAY = "day"
    EVENING = "evening"
    NIGHT = "night"


class Format(StrEnum):
    HOME = "home"  # посидеть дома
    WALK = "walk"  # прогулка
    FOOD = "food"  # поесть где-то
    ACTIVE = "active"  # активный отдых: каток, боулинг
    CULTURE = "culture"  # кино, музей, театр
    TRIP = "trip"  # поездка, выезд за город
    OTHER = "other"


class Cuisine(StrEnum):
    RUSSIAN = "russian"
    GEORGIAN = "georgian"
    ITALIAN = "italian"
    FRENCH = "french"
    JAPANESE = "japanese"
    CHINESE = "chinese"
    KOREAN = "korean"
    VIETNAMESE = "vietnamese"
    THAI = "thai"
    INDIAN = "indian"
    MEXICAN = "mexican"
    AMERICAN = "american"
    OTHER = "other"


class Budget(StrEnum):
    FREE = "free"  # бесплатно
    LOW = "low"  # ₽
    MEDIUM = "medium"  # ₽₽
    HIGH = "high"  # ₽₽₽


# Cheapest first, so "up to ₽₽" means every budget up to that position.
BUDGET_ORDER = list(Budget)
