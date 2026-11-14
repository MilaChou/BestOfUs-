"""Built-in gift catalog for "Что подарить?".

Two parts:
- GIFTS — the same for everyone, plain data like the activity catalog.
- personalized_gifts(profile) — made on the fly from the partner's profile
  ("любимые цветы: пионы" -> "Букет: пионы").

`allergy_sensitive` marks gifts where the partner's allergies matter
(flowers, food, cosmetics); suggestions for them carry a reminder.
"""

from dataclasses import dataclass

from app.enums import Budget, GiftType
from app.models.user import Profile


@dataclass(frozen=True)
class CatalogGift:
    id: str
    title: str
    description: str
    gift_type: GiftType
    budget: Budget
    allergy_sensitive: bool = False
    personalized: bool = False
    hint: str | None = None  # why it was suggested, for personalized gifts


HOME, TOGETHER, HOBBY, JOY = GiftType.HOME, GiftType.TOGETHER, GiftType.HOBBY, GiftType.SMALL_JOY
EXP, BEAUTY, CLOTHES, TECH, FOOD = (
    GiftType.EXPERIENCE,
    GiftType.BEAUTY,
    GiftType.CLOTHES,
    GiftType.TECH,
    GiftType.FOOD,
)
FREE, LOW, MID, HIGH = Budget.FREE, Budget.LOW, Budget.MEDIUM, Budget.HIGH
ALLERGY = True

# fmt: off
GIFTS: list[CatalogGift] = [
    # Своими руками — бесплатно
    CatalogGift("letter", "Письмо от руки", "Написать, за что ты любишь партнёра. Такое хранят годами.", JOY, FREE),
    CatalogGift("coupon-book", "Книжка купонов", "«Завтрак в постель», «Массаж», «Я выбираю фильм» — каждый купон можно обменять.", TOGETHER, FREE),
    CatalogGift("playlist", "Плейлист «Наши песни»", "Собрать песни, связанные с вашими моментами, и придумать обложку.", JOY, FREE),
    CatalogGift("video-card", "Видео-открытка", "Смонтировать ролик из ваших фото и видео за всё время.", JOY, FREE),
    CatalogGift("treasure-hunt", "Квест по квартире", "Записки с подсказками, а в конце — сюрприз.", TOGETHER, FREE),
    # Дёшево — до 2 000 ₽
    CatalogGift("puzzle", "Пазл на 1000 деталей", "Собирать вместе пару вечеров под музыку.", TOGETHER, LOW),
    CatalogGift("small-board-game", "Компактная настольная игра на двоих", "Например, «Codenames Дуэт» или «Патчворк».", TOGETHER, LOW),
    CatalogGift("photo-mug", "Кружка с вашим фото", "Каждое утро — напоминание о вас.", HOME, LOW),
    CatalogGift("candle", "Ароматическая свеча", "Для уютных вечеров.", HOME, LOW, ALLERGY),
    CatalogGift("photo-album", "Альбом для общих фото", "Распечатать любимые снимки и подписать каждый.", HOME, LOW),
    CatalogGift("warm-socks", "Смешные тёплые носки", "Мелочь, которая точно пригодится зимой.", CLOTHES, LOW),
    CatalogGift("chocolate", "Шоколад ручной работы", "Набор необычных вкусов.", FOOD, LOW, ALLERGY),
    CatalogGift("tea-set", "Набор хорошего чая", "Несколько сортов на пробу.", FOOD, LOW, ALLERGY),
    CatalogGift("bath-bombs", "Бомбочки для ванны", "Для спа-вечера дома.", BEAUTY, LOW, ALLERGY),
    CatalogGift("hand-cream", "Крем для рук с любимым запахом", "Особенно кстати в холодное время.", BEAUTY, LOW, ALLERGY),
    CatalogGift("flowers", "Букет цветов", "Просто так, без повода — так даже приятнее.", JOY, LOW, ALLERGY),
    CatalogGift("sketchbook", "Скетчбук и хорошие карандаши", "Даже если человек «не умеет рисовать».", HOBBY, LOW),
    CatalogGift("signed-book", "Книга с подписью", "Любимая книга — твоя или та, которую давно хотел(а) прочитать партнёр. С пожеланием на первой странице.", HOBBY, LOW),
    CatalogGift("power-bank", "Компактный пауэрбанк", "Чтобы телефон не садился в самый нужный момент.", TECH, LOW),
    CatalogGift("cinema-tickets", "Билеты в кино на последний ряд", "И большой попкорн в придачу.", EXP, LOW),
    # Средне — 2 000–10 000 ₽
    CatalogGift("big-board-game", "Большая настольная игра", "На долгие вечера вдвоём или с друзьями.", TOGETHER, MID),
    CatalogGift("quest-room", "Квест-комната на двоих", "Проверить, какая вы команда.", TOGETHER, MID),
    CatalogGift("cooking-class", "Кулинарный мастер-класс на двоих", "Научиться готовить что-то новое вместе.", TOGETHER, MID, ALLERGY),
    CatalogGift("blanket", "Мягкий плед", "Для кино-вечеров под одним пледом.", HOME, MID),
    CatalogGift("star-projector", "Ночник-проектор звёздного неба", "Звёзды на потолке спальни.", HOME, MID),
    CatalogGift("star-map", "Карта звёздного неба в день вашей встречи", "Постер с тем, как выглядело небо в ваш день.", HOME, MID),
    CatalogGift("pajamas", "Уютная пижама", "Можно парные.", CLOTHES, MID),
    CatalogGift("scarf", "Тёплый шарф", "Мягкий, из хорошей шерсти.", CLOTHES, MID),
    CatalogGift("perfume-minis", "Набор миниатюр парфюма", "Чтобы найти свой аромат.", BEAUTY, MID, ALLERGY),
    CatalogGift("skincare-set", "Набор уходовой косметики", "Маски, сыворотки и всё для спа-вечера.", BEAUTY, MID, ALLERGY),
    CatalogGift("massage-certificate", "Сертификат на массаж", "Час полного расслабления.", EXP, MID),
    CatalogGift("pottery-class", "Гончарный мастер-класс на двоих", "Слепить друг другу по кружке.", EXP, MID),
    CatalogGift("concert-tickets", "Билеты на концерт", "Любимого исполнителя или кого-то нового.", EXP, MID),
    CatalogGift("headphones", "Беспроводные наушники", "Для музыки в дороге.", TECH, MID),
    CatalogGift("smart-speaker", "Умная колонка", "Музыка, будильник и таймер для готовки.", TECH, MID),
    CatalogGift("coffee-kit", "Набор для заваривания кофе", "Аэропресс или воронка и пачка хорошего зерна.", FOOD, MID),
    CatalogGift("cheese-box", "Сырная тарелка с дополнениями", "Сыры, мёд, орехи — для вечера вдвоём.", FOOD, MID, ALLERGY),
    CatalogGift("hobby-kit", "Набор для нового хобби", "Вышивка, свечи, мыло или эпоксидная смола.", HOBBY, MID),
    CatalogGift("watercolor", "Хорошие акварельные краски", "Для тех, кто любит рисовать.", HOBBY, MID),
    # Дорого — от 10 000 ₽
    CatalogGift("weekend-trip", "Поездка на выходные", "Короткое путешествие в другой город.", EXP, HIGH),
    CatalogGift("spa-for-two", "СПА-день на двоих", "Бассейн, сауна и массаж.", EXP, HIGH),
    CatalogGift("balloon-flight", "Полёт на воздушном шаре", "Впечатление на всю жизнь.", EXP, HIGH),
    CatalogGift("tasting-dinner", "Ужин с дегустационным меню", "В ресторане, куда давно хотели сходить.", FOOD, HIGH, ALLERGY),
    CatalogGift("jewelry", "Украшение", "Кулон, браслет или серьги.", CLOTHES, HIGH),
    CatalogGift("watch", "Часы", "Классика, которая напоминает о тебе каждый раз.", CLOTHES, HIGH),
    CatalogGift("perfume", "Любимый парфюм", "Полноразмерный флакон.", BEAUTY, HIGH, ALLERGY),
    CatalogGift("anc-headphones", "Наушники с шумоподавлением", "Тишина в метро и самолёте.", TECH, HIGH),
    CatalogGift("e-reader", "Электронная книга", "Целая библиотека в кармане.", TECH, HIGH),
    CatalogGift("instant-camera", "Фотоаппарат моментальной печати", "Фото сразу в руках.", TECH, HIGH),
    CatalogGift("hobby-course", "Курс по хобби", "Фотография, танцы, гончарное дело — то, о чём партнёр давно мечтает.", HOBBY, HIGH),
]
# fmt: on

GIFTS_BY_ID: dict[str, CatalogGift] = {g.id: g for g in GIFTS}
assert len(GIFTS_BY_ID) == len(GIFTS), "gift catalog ids must be unique"


# (profile field, id, title template, description, type, budget, allergy, hint label)
_PERSONAL_RULES = [
    ("favorite_flowers", "personal-flowers", "Букет: {}", "Любимые цветы — точно в цель.", JOY, LOW, True, "любимые цветы"),
    ("favorite_drink", "personal-drink", "Всё для любимого напитка: {}", "Хороший набор или красивая посуда к нему.", FOOD, LOW, True, "любимый напиток"),
    ("favorite_food", "personal-food", "Ужин с любимой едой: {}", "Приготовить самому или заказать из лучшего места.", FOOD, MID, True, "любимая еда"),
    ("favorite_color", "personal-color", "Плед или кружка любимого цвета: {}", "Вещь для дома, которая будет радовать.", HOME, LOW, False, "любимый цвет"),
    ("ring_size", "personal-ring", "Кольцо — размер {}", "Размер уже известен, осталось выбрать.", CLOTHES, HIGH, False, "размер кольца"),
    ("clothing_size_top", "personal-hoodie", "Худи или свитер — размер {}", "Уютная вещь, размер точно подойдёт.", CLOTHES, MID, False, "размер одежды"),
    ("shoe_size", "personal-slippers", "Домашние тапочки — размер {}", "Мягкие и тёплые.", CLOTHES, LOW, False, "размер обуви"),
]  # fmt: skip


def personalized_gifts(profile: Profile | None) -> list[CatalogGift]:
    """Gifts made from what the partner filled in their profile."""
    if profile is None:
        return []
    gifts = []
    for field, gift_id, title, description, gift_type, budget, allergy, label in _PERSONAL_RULES:
        value = getattr(profile, field)
        if value:
            gifts.append(
                CatalogGift(
                    id=gift_id,
                    title=title.format(value),
                    description=description,
                    gift_type=gift_type,
                    budget=budget,
                    allergy_sensitive=allergy,
                    personalized=True,
                    hint=f"Из профиля: {label} — {value}",
                )
            )
    return gifts
