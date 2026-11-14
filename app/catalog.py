"""Built-in catalog of activities for "Подкинь идею".

It is used when the couple's own ideas don't match the chosen filters.
This is plain data in code, not a database table: it is the same for
everyone and changes only together with the app. To add an activity,
add a line to ACTIVITIES — the id must be unique and never change,
because saved ideas remember it.
"""

from dataclasses import dataclass

from app.enums import Budget, Cuisine, Format, TimeOfDay

M, D, E, N = TimeOfDay.MORNING, TimeOfDay.DAY, TimeOfDay.EVENING, TimeOfDay.NIGHT


@dataclass(frozen=True)
class CatalogActivity:
    id: str
    title: str
    description: str
    format: Format
    budget: Budget
    times_of_day: tuple[TimeOfDay, ...]
    cuisine: Cuisine | None = None


def _a(
    id: str,
    title: str,
    description: str,
    format: Format,
    budget: Budget,
    times: tuple[TimeOfDay, ...],
    cuisine: Cuisine | None = None,
) -> CatalogActivity:
    return CatalogActivity(id, title, description, format, budget, times, cuisine)


H, W, F, A, C, T = Format.HOME, Format.WALK, Format.FOOD, Format.ACTIVE, Format.CULTURE, Format.TRIP
FREE, LOW, MID, HIGH = Budget.FREE, Budget.LOW, Budget.MEDIUM, Budget.HIGH

# fmt: off
ACTIVITIES: list[CatalogActivity] = [
    # Дома
    _a("board-games", "Вечер настольных игр", "Достать любимую игру или скачать новую — и играть до последнего хода.", H, FREE, (E, N)),
    _a("movie-marathon", "Кино-марафон под пледом", "Выбрать трилогию или сериал, сделать попкорн и не вылезать из-под пледа.", H, FREE, (E, N)),
    _a("cook-new-recipe", "Приготовить ужин по новому рецепту", "Найти блюдо, которое никто из вас ещё не готовил, и сделать его вместе.", H, LOW, (E,)),
    _a("breakfast-in-bed", "Завтрак в постель", "Сюрприз с утра: оладьи, кофе и никакой спешки.", H, LOW, (M,)),
    _a("puzzle", "Собрать пазл", "Пазл на 1000 деталей, музыка на фоне и разговоры обо всём.", H, LOW, (D, E)),
    _a("home-spa", "Домашний спа-вечер", "Маски, ванна с пеной, массаж по очереди.", H, LOW, (E,)),
    _a("draw-portraits", "Нарисовать портреты друг друга", "Не важно, умеете ли вы рисовать — важно, как вы будете смеяться.", H, LOW, (D, E)),
    _a("36-questions", "Вечер откровенных вопросов", "Пройти «36 вопросов, чтобы влюбиться» или придумать свои.", H, FREE, (E, N)),
    _a("bake", "Испечь что-нибудь вместе", "Печенье, пирог или кекс — главное, чтобы кухня была в муке.", H, LOW, (D, E)),
    _a("old-photos", "Пересмотреть старые фото", "Открыть галерею за прошлые годы и вспомнить, как всё начиналось.", H, FREE, (E, N)),
    _a("karaoke-home", "Домашнее караоке", "Включить караоке на YouTube и петь любимые песни во весь голос.", H, FREE, (E,)),
    _a("pillow-fort", "Шалаш из подушек", "Построить крепость из одеял и смотреть мультики изнутри.", H, FREE, (E, N)),
    _a("lazy-morning", "Ленивое утро", "Кофе, тихая музыка, никаких планов и никакой спешки.", H, FREE, (M,)),
    # Прогулка
    _a("park-coffee", "Прогулка по парку с кофе", "Взять кофе с собой и пройти любимый маршрут или найти новый.", W, LOW, (M, D)),
    _a("sunrise", "Встретить рассвет", "Проснуться пораньше и посмотреть, как просыпается город.", W, FREE, (M,)),
    _a("night-walk", "Ночная прогулка по городу", "Пустые улицы, фонари и разговоры, которые днём не случаются.", W, FREE, (N,)),
    _a("new-streets", "Улицы, где вы ещё не были", "Выбрать на карте район, куда никогда не заходили, и просто гулять.", W, FREE, (D, E)),
    _a("picnic", "Пикник в парке", "Плед, бутерброды, фрукты — и полдня никуда не торопиться.", W, LOW, (D,)),
    _a("photo-hunt", "Фотоохота", "Выбрать тему (например, «всё жёлтое») и за час сделать 20 снимков.", W, FREE, (D,)),
    _a("sunset", "Посмотреть закат", "Найти высокую точку или набережную и проводить солнце.", W, FREE, (E,)),
    _a("waterside", "Прогулка у воды", "Набережная, пруд или река — посидеть, покормить уток.", W, FREE, (D,)),
    _a("stargazing", "Смотреть на звёзды", "Уехать туда, где темно, взять плед и найти Большую Медведицу.", W, FREE, (N,)),
    # Поесть где-то
    _a("new-coffee-shop", "Завтрак в новой кофейне", "Найти кофейню, где вы ещё не были, и начать с неё день.", F, LOW, (M,)),
    _a("georgian", "Хинкали и хачапури", "Грузинский ресторан, большой стол и много сыра.", F, MID, (D, E), Cuisine.GEORGIAN),
    _a("russian", "Блины и пельмени", "Русская кухня: борщ, пельмени и блины со сметаной.", F, LOW, (D, E), Cuisine.RUSSIAN),
    _a("italian", "Паста и пицца", "Итальянский ресторан: поделить пиццу и попробовать пасты друг друга.", F, MID, (D, E), Cuisine.ITALIAN),
    _a("french-bistro", "Ужин во французском бистро", "Романтический вечер: свечи, вино и десерт на двоих.", F, HIGH, (E,), Cuisine.FRENCH),
    _a("sushi", "Суши и роллы", "Взять большой сет и попробовать то, что ещё не пробовали.", F, MID, (D, E, N), Cuisine.JAPANESE),
    _a("ramen", "Рамен", "Маленькая раменная и две огромные горячие миски.", F, LOW, (D, E, N), Cuisine.JAPANESE),
    _a("peking-duck", "Утка по-пекински", "Китайский ресторан и утка, которую разделывают прямо при вас.", F, HIGH, (E,), Cuisine.CHINESE),
    _a("dim-sum", "Димсамы", "Заказать много разных и пробовать всё по очереди.", F, MID, (D, E), Cuisine.CHINESE),
    _a("korean-bbq", "Корейское барбекю", "Жарить мясо самим прямо на столе.", F, HIGH, (E,), Cuisine.KOREAN),
    _a("pho", "Фо бо", "Вьетнамское кафе и горячий суп с травами.", F, LOW, (D, E), Cuisine.VIETNAMESE),
    _a("tom-yum", "Том ям", "Тайская кухня — острая, кислая и яркая.", F, MID, (D, E), Cuisine.THAI),
    _a("curry", "Индийское карри", "Карри, лепёшки наан и ласси.", F, MID, (D, E), Cuisine.INDIAN),
    _a("tacos", "Тако и начос", "Мексиканская кухня, гуакамоле и что-нибудь острое.", F, LOW, (E, N), Cuisine.MEXICAN),
    _a("burgers", "Бургеры", "Найти лучшие бургеры в городе и устроить дегустацию.", F, LOW, (D, E, N), Cuisine.AMERICAN),
    _a("food-tour", "Гастро-тур", "Три заведения за вечер — в каждом по одному блюду.", F, MID, (E,)),
    _a("desserts", "Кондитерская", "Только десерты, никакого основного блюда.", F, LOW, (D,)),
    _a("late-dinner", "Поздний ужин", "Круглосуточное кафе, когда весь город уже спит.", F, LOW, (N,)),
    # Активный отдых
    _a("skating", "Каток", "Держаться за руки, падать и смеяться.", A, LOW, (D, E)),
    _a("bowling", "Боулинг", "Сыграть пару партий — проигравший выбирает следующее свидание.", A, MID, (E, N)),
    _a("bikes", "Велосипеды или самокаты", "Взять в прокате и уехать по набережной.", A, LOW, (M, D)),
    _a("climbing", "Скалодром", "Страховать друг друга и лезть всё выше.", A, MID, (D, E)),
    _a("escape-room", "Квест-комната", "Выбраться за 60 минут и проверить, какая вы команда.", A, MID, (D, E)),
    _a("trampolines", "Батутный парк", "Почувствовать себя детьми на целый час.", A, LOW, (D,)),
    _a("morning-run", "Утренняя пробежка или йога", "Начать день вместе и с энергией.", A, FREE, (M,)),
    _a("karting", "Картинг", "Выяснить, кто из вас лучше водит.", A, MID, (D, E)),
    _a("pool", "Бассейн", "Поплавать, а потом в сауну.", A, LOW, (M, D, E)),
    # Культура
    _a("cinema", "Кино", "Билеты на последний ряд и большой попкорн.", C, LOW, (E, N)),
    _a("museum", "Музей или выставка", "Выбрать выставку, на которую никто из вас не пошёл бы один.", C, LOW, (D,)),
    _a("theatre", "Театр или стендап", "Нарядиться и выйти в свет.", C, MID, (E,)),
    _a("concert", "Концерт", "Живая музыка — любимая группа или кто-то новый.", C, MID, (E,)),
    _a("workshop", "Мастер-класс", "Керамика, рисование или свечи — сделать что-то своими руками.", C, MID, (D, E)),
    _a("city-tour", "Экскурсия по своему городу", "Узнать о своём городе то, чего вы не знали.", C, LOW, (D,)),
    # Поездки
    _a("countryside", "Поездка за город", "Сесть на электричку и выйти на незнакомой станции.", T, LOW, (M, D)),
    _a("weekend-city", "Выходные в другом городе", "Короткое путешествие на два дня.", T, HIGH, (M, D)),
    _a("cabin", "Домик за городом", "Снять домик с баней или камином на сутки.", T, HIGH, (D, E)),
    _a("camping", "Поход с палаткой", "Костёр, звёзды и ночь на природе.", T, LOW, (D, E, N)),
]
# fmt: on

ACTIVITIES_BY_ID: dict[str, CatalogActivity] = {a.id: a for a in ACTIVITIES}
assert len(ACTIVITIES_BY_ID) == len(ACTIVITIES), "catalog ids must be unique"
