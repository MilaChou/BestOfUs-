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


class GiftType(StrEnum):
    HOME = "home"  # для дома
    TOGETHER = "together"  # провести время вместе
    HOBBY = "hobby"  # для хобби
    SMALL_JOY = "small_joy"  # приятная мелочь
    EXPERIENCE = "experience"  # впечатление: билеты, мастер-класс
    BEAUTY = "beauty"  # уход и красота
    CLOTHES = "clothes"  # одежда и аксессуары
    TECH = "tech"  # техника
    FOOD = "food"  # вкусное


class WishPriority(StrEnum):
    BURNING = "burning"  # 🔥 очень хочу
    NICE = "nice"  # 🙂 было бы классно
    MAYBE = "maybe"  # ✨ не обязательно, но приятно


def budget_for_price(price: int | None) -> Budget | None:
    """Rubles -> budget level. 0 = своими руками, <2 000 = дёшево,
    2 000–9 999 = средне, от 10 000 = дорого. No price -> unknown."""
    if price is None:
        return None
    if price == 0:
        return Budget.FREE
    if price < 2_000:
        return Budget.LOW
    if price < 10_000:
        return Budget.MEDIUM
    return Budget.HIGH


class TaskCategory(StrEnum):
    SHOPPING = "shopping"  # покупки
    HOME = "home"  # дом
    HEALTH = "health"  # здоровье
    MONEY = "money"  # деньги, счета
    ERRANDS = "errands"  # дела: документы, записи
    OTHER = "other"


class LoveLanguage(StrEnum):
    WORDS = "words"  # слова поддержки
    TIME = "time"  # время вместе
    GIFTS = "gifts"  # подарки
    SERVICE = "service"  # помощь делом
    TOUCH = "touch"  # прикосновения
