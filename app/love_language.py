"""The love language test: statements, scoring and tips.

Each statement is rated from 1 ("совсем не про меня") to 5 ("это точно про меня").
There are 4 statements per language, so a language scores 4–20 points,
shown as 0–100 %. A person can have several leading languages: every language
within 10 % of the top one counts as leading.
"""

from dataclasses import dataclass

from app.enums import LoveLanguage

WORDS, TIME, GIFTS, SERVICE, TOUCH = (
    LoveLanguage.WORDS,
    LoveLanguage.TIME,
    LoveLanguage.GIFTS,
    LoveLanguage.SERVICE,
    LoveLanguage.TOUCH,
)

SCALE_MIN, SCALE_MAX = 1, 5
LEADING_GAP_PERCENT = 10


@dataclass(frozen=True)
class Question:
    id: int
    text: str
    language: LoveLanguage


# Mixed order on purpose, so the languages aren't obvious while answering.
# fmt: off
QUESTIONS: list[Question] = [
    Question(1, "Мне очень приятно, когда партнёр говорит, что гордится мной.", WORDS),
    Question(2, "Лучший вечер для меня — когда мы вдвоём и никто не отвлекается на телефон.", TIME),
    Question(3, "Я храню даже маленькие подарки и записки от партнёра.", GIFTS),
    Question(4, "Если партнёр берёт на себя какое-то моё дело, я чувствую заботу.", SERVICE),
    Question(5, "Мне важно держаться за руки или обниматься, когда мы рядом.", TOUCH),
    Question(6, "Сообщение «я думаю о тебе» среди дня может поднять мне настроение.", WORDS),
    Question(7, "Мне грустно, если мы долго не проводим время только вдвоём.", TIME),
    Question(8, "Когда партнёр приносит что-то «просто так, увидел и вспомнил о тебе», это много для меня значит.", GIFTS),
    Question(9, "Приготовленный для меня ужин говорит о любви больше, чем слова.", SERVICE),
    Question(10, "Объятие после тяжёлого дня помогает мне лучше любых разговоров.", TOUCH),
    Question(11, "Мне обидно, когда мои старания не замечают и не хвалят.", WORDS),
    Question(12, "Совместные прогулки и разговоры по душам — то, что сближает меня больше всего.", TIME),
    Question(13, "Я расстраиваюсь, если партнёр забывает про подарок на важную дату.", GIFTS),
    Question(14, "Мне приятно, когда партнёр помогает, даже если я не просил(а) об этом.", SERVICE),
    Question(15, "Когда партнёр случайно касается меня или гладит по спине, я чувствую близость.", TOUCH),
    Question(16, "Я перечитываю тёплые сообщения от партнёра.", WORDS),
    Question(17, "Для меня важнее провести день вместе, чем получить дорогой подарок.", TIME),
    Question(18, "Подарок, выбранный с вниманием к моим вкусам, показывает, как хорошо меня знают.", GIFTS),
    Question(19, "Меня раздражает, когда обещают помочь, но не делают.", SERVICE),
    Question(20, "Мне не хватает партнёра, когда мы долго не обнимаемся.", TOUCH),
]
# fmt: on

QUESTION_IDS = {q.id for q in QUESTIONS}


@dataclass(frozen=True)
class LanguageInfo:
    title: str
    description: str
    how_to_show: str  # advice for the partner


INFO: dict[LoveLanguage, LanguageInfo] = {
    WORDS: LanguageInfo(
        "Слова поддержки",
        "Любовь чувствуется через слова: комплименты, благодарность, признания.",
        "Говори, за что ценишь, пиши тёплые сообщения, хвали за старания — даже за мелочи.",
    ),
    TIME: LanguageInfo(
        "Время вместе",
        "Любовь — это внимание и время только для двоих.",
        "Планируй свидания, убирай телефон во время разговоров, просто будь рядом.",
    ),
    GIFTS: LanguageInfo(
        "Подарки",
        "Любовь видна в символах внимания: важна не цена, а то, что о тебе подумали.",
        "Приноси мелочи «просто так», помни важные даты, загляни в вишлист.",
    ),
    SERVICE: LanguageInfo(
        "Помощь делом",
        "Любовь — это поступки: помочь, взять на себя, облегчить жизнь.",
        "Сделай дело из списка планов за партнёра, приготовь ужин, выполняй обещанное.",
    ),
    TOUCH: LanguageInfo(
        "Прикосновения",
        "Любовь ощущается через близость: объятия, касания, держаться за руки.",
        "Обнимай чаще, держи за руку на прогулке, садись ближе.",
    ),
}


def score(answers: dict[int, int]) -> dict[str, int]:
    """Answers {question id: 1–5} -> percent per language {"words": 75, ...}."""
    per_language = len(QUESTIONS) // len(LoveLanguage)
    lowest, highest = per_language * SCALE_MIN, per_language * SCALE_MAX
    totals = {language: 0 for language in LoveLanguage}
    for question in QUESTIONS:
        totals[question.language] += answers[question.id]
    return {
        language.value: round((total - lowest) * 100 / (highest - lowest))
        for language, total in totals.items()
    }


def leading(scores: dict[str, int]) -> list[LoveLanguage]:
    """Every language within LEADING_GAP_PERCENT of the top one, strongest first."""
    top = max(scores.values())
    return [
        LoveLanguage(language)
        for language, percent in sorted(scores.items(), key=lambda kv: -kv[1])
        if percent >= top - LEADING_GAP_PERCENT
    ]


assert len(QUESTION_IDS) == len(QUESTIONS), "question ids must be unique"
assert all(
    sum(q.language == language for q in QUESTIONS) == len(QUESTIONS) // len(LoveLanguage)
    for language in LoveLanguage
), "every language needs the same number of questions"
