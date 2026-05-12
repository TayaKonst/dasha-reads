import asyncio
import os

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy import delete

load_dotenv()

from models import Attempt, Exercise, Session  # noqa: E402


EXERCISES = [
    # ─── Level 0: Letters ───────────────────────────────────────────────────
    {"level": 0, "type": "letter", "question_data": {"display": "К", "hint": "Как кот", "image": "🐱"},
     "correct_answer": "К", "options": ["К", "Г", "Х", "Р"]},
    {"level": 0, "type": "letter", "question_data": {"display": "М", "hint": "Как мама", "image": "👩"},
     "correct_answer": "М", "options": ["М", "Н", "П", "Б"]},
    {"level": 0, "type": "letter", "question_data": {"display": "С", "hint": "Как солнце", "image": "☀️"},
     "correct_answer": "С", "options": ["С", "З", "Ш", "Щ"]},
    {"level": 0, "type": "letter", "question_data": {"display": "Б", "hint": "Как бабочка", "image": "🦋"},
     "correct_answer": "Б", "options": ["Б", "П", "В", "Д"]},
    {"level": 0, "type": "letter", "question_data": {"display": "А", "hint": "Как арбуз", "image": "🍉"},
     "correct_answer": "А", "options": ["А", "О", "У", "Я"]},
    {"level": 0, "type": "letter", "question_data": {"display": "О", "hint": "Как облако", "image": "☁️"},
     "correct_answer": "О", "options": ["О", "А", "У", "Э"]},
    {"level": 0, "type": "letter", "question_data": {"display": "Р", "hint": "Как рыба", "image": "🐟"},
     "correct_answer": "Р", "options": ["Р", "Л", "Н", "М"]},
    {"level": 0, "type": "letter", "question_data": {"display": "Л", "hint": "Как лиса", "image": "🦊"},
     "correct_answer": "Л", "options": ["Л", "Р", "Н", "М"]},
    {"level": 0, "type": "letter", "question_data": {"display": "Т", "hint": "Как тигр", "image": "🐯"},
     "correct_answer": "Т", "options": ["Т", "Д", "П", "Б"]},
    {"level": 0, "type": "letter", "question_data": {"display": "Д", "hint": "Как дом", "image": "🏠"},
     "correct_answer": "Д", "options": ["Д", "Т", "Б", "В"]},
    {"level": 0, "type": "letter", "question_data": {"display": "Ш", "hint": "Как шапка", "image": "🧢"},
     "correct_answer": "Ш", "options": ["Ш", "Щ", "С", "Ж"]},
    {"level": 0, "type": "letter", "question_data": {"display": "У", "hint": "Как утка", "image": "🦆"},
     "correct_answer": "У", "options": ["У", "Ю", "О", "А"]},
    {"level": 0, "type": "letter", "question_data": {"display": "И", "hint": "Как игра", "image": "🎮"},
     "correct_answer": "И", "options": ["И", "Й", "Е", "Ы"]},
    {"level": 0, "type": "letter", "question_data": {"display": "Н", "hint": "Как нос", "image": "👃"},
     "correct_answer": "Н", "options": ["Н", "М", "Л", "Р"]},
    {"level": 0, "type": "letter", "question_data": {"display": "В", "hint": "Как волк", "image": "🐺"},
     "correct_answer": "В", "options": ["В", "Б", "Д", "Ф"]},

    # ─── Level 1: Syllables ─────────────────────────────────────────────────
    {"level": 1, "type": "syllable", "question_data": {"syllable": "МА", "image": "🐱", "question": "Какой слог ты видишь?"},
     "correct_answer": "МА", "options": ["МА", "МО", "МУ", "МЫ"]},
    {"level": 1, "type": "syllable", "question_data": {"syllable": "МО", "image": "🌊", "question": "Какой слог ты видишь?"},
     "correct_answer": "МО", "options": ["МО", "МА", "МЕ", "МУ"]},
    {"level": 1, "type": "syllable", "question_data": {"syllable": "МУ", "image": "🐄", "question": "Какой слог ты видишь?"},
     "correct_answer": "МУ", "options": ["МУ", "НУ", "БУ", "ДУ"]},
    {"level": 1, "type": "syllable", "question_data": {"syllable": "СА", "image": "🌸", "question": "Какой слог ты видишь?"},
     "correct_answer": "СА", "options": ["СА", "ЗА", "ША", "СО"]},
    {"level": 1, "type": "syllable", "question_data": {"syllable": "СО", "image": "🥤", "question": "Какой слог ты видишь?"},
     "correct_answer": "СО", "options": ["СО", "СА", "СУ", "ЗО"]},
    {"level": 1, "type": "syllable", "question_data": {"syllable": "РА", "image": "🦀", "question": "Какой слог ты видишь?"},
     "correct_answer": "РА", "options": ["РА", "РО", "ЛА", "НА"]},
    {"level": 1, "type": "syllable", "question_data": {"syllable": "РО", "image": "🌹", "question": "Какой слог ты видишь?"},
     "correct_answer": "РО", "options": ["РО", "РА", "РУ", "ЛО"]},
    {"level": 1, "type": "syllable", "question_data": {"syllable": "ЛА", "image": "🦁", "question": "Какой слог ты видишь?"},
     "correct_answer": "ЛА", "options": ["ЛА", "РА", "НА", "ЛО"]},
    {"level": 1, "type": "syllable", "question_data": {"syllable": "НА", "image": "🧴", "question": "Какой слог ты видишь?"},
     "correct_answer": "НА", "options": ["НА", "МА", "ЛА", "НО"]},
    {"level": 1, "type": "syllable", "question_data": {"syllable": "ТА", "image": "🐢", "question": "Какой слог ты видишь?"},
     "correct_answer": "ТА", "options": ["ТА", "ДА", "ТО", "КА"]},
    {"level": 1, "type": "syllable", "question_data": {"syllable": "КА", "image": "🦆", "question": "Какой слог ты видишь?"},
     "correct_answer": "КА", "options": ["КА", "ГА", "ТА", "КО"]},
    {"level": 1, "type": "syllable", "question_data": {"syllable": "БА", "image": "🥁", "question": "Какой слог ты видишь?"},
     "correct_answer": "БА", "options": ["БА", "ПА", "ВА", "БО"]},
    {"level": 1, "type": "syllable", "question_data": {"syllable": "ДА", "image": "✅", "question": "Какой слог ты видишь?"},
     "correct_answer": "ДА", "options": ["ДА", "ТА", "ДО", "НА"]},
    {"level": 1, "type": "syllable", "question_data": {"syllable": "ВА", "image": "🛁", "question": "Какой слог ты видишь?"},
     "correct_answer": "ВА", "options": ["ВА", "ФА", "БА", "ВО"]},
    {"level": 1, "type": "syllable", "question_data": {"syllable": "ПА", "image": "👨", "question": "Какой слог ты видишь?"},
     "correct_answer": "ПА", "options": ["ПА", "БА", "МА", "ПО"]},

    # ─── Level 2: Words ─────────────────────────────────────────────────────
    {"level": 2, "type": "word", "question_data": {"display": "рыба", "scheme_key": "рыба", "image": "🐟"},
     "correct_answer": "🐟", "options": ["🐟", "🐱", "🐶", "🐸"]},
    {"level": 2, "type": "word", "question_data": {"display": "кот", "scheme_key": "кот", "image": "🐱"},
     "correct_answer": "🐱", "options": ["🐱", "🐶", "🐰", "🐟"]},
    {"level": 2, "type": "word", "question_data": {"display": "дом", "scheme_key": "дом", "image": "🏠"},
     "correct_answer": "🏠", "options": ["🏠", "🌳", "🚗", "⛺"]},
    {"level": 2, "type": "word", "question_data": {"display": "мама", "scheme_key": "мама", "image": "👩"},
     "correct_answer": "👩", "options": ["👩", "👨", "👧", "👦"]},
    {"level": 2, "type": "word", "question_data": {"display": "папа", "scheme_key": "папа", "image": "👨"},
     "correct_answer": "👨", "options": ["👨", "👩", "👴", "👦"]},
    {"level": 2, "type": "word", "question_data": {"display": "молоко", "scheme_key": "молоко", "image": "🥛"},
     "correct_answer": "🥛", "options": ["🥛", "🍵", "🧃", "🍶"]},
    {"level": 2, "type": "word", "question_data": {"display": "книга", "scheme_key": "книга", "image": "📚"},
     "correct_answer": "📚", "options": ["📚", "✏️", "📝", "🖊️"]},
    {"level": 2, "type": "word", "question_data": {"display": "яблоко", "scheme_key": "яблоко", "image": "🍎"},
     "correct_answer": "🍎", "options": ["🍎", "🍊", "🍋", "🍇"]},
    {"level": 2, "type": "word", "question_data": {"display": "ёжик", "scheme_key": "ёжик", "image": "🦔"},
     "correct_answer": "🦔", "options": ["🦔", "🐿️", "🐭", "🐇"]},
    {"level": 2, "type": "word", "question_data": {"display": "слон", "scheme_key": "слон", "image": "🐘"},
     "correct_answer": "🐘", "options": ["🐘", "🦏", "🦛", "🐪"]},
    {"level": 2, "type": "word", "question_data": {"display": "утка", "scheme_key": "утка", "image": "🦆"},
     "correct_answer": "🦆", "options": ["🦆", "🐧", "🦅", "🐦"]},
    {"level": 2, "type": "word", "question_data": {"display": "лиса", "scheme_key": "лиса", "image": "🦊"},
     "correct_answer": "🦊", "options": ["🦊", "🐺", "🦝", "🐱"]},
    {"level": 2, "type": "word", "question_data": {"display": "роза", "scheme_key": "роза", "image": "🌹"},
     "correct_answer": "🌹", "options": ["🌹", "🌻", "🌷", "🌸"]},
    {"level": 2, "type": "word", "question_data": {"display": "зима", "scheme_key": "зима", "image": "❄️"},
     "correct_answer": "❄️", "options": ["❄️", "☀️", "🍂", "🌸"]},
    {"level": 2, "type": "word", "question_data": {"display": "лето", "scheme_key": "лето", "image": "☀️"},
     "correct_answer": "☀️", "options": ["☀️", "❄️", "🌧️", "🍂"]},

    # ─── Level 3: Sentences ─────────────────────────────────────────────────
    {"level": 3, "type": "sentence", "question_data": {"sentence": "Кот пьёт молоко.", "question": "Что делает кот?"},
     "correct_answer": "Пьёт молоко", "options": ["Пьёт молоко", "Ест рыбу", "Спит на диване", "Играет с мячом"]},
    {"level": 3, "type": "sentence", "question_data": {"sentence": "Мама читает книгу.", "question": "Что делает мама?"},
     "correct_answer": "Читает книгу", "options": ["Читает книгу", "Варит суп", "Спит", "Поёт песню"]},
    {"level": 3, "type": "sentence", "question_data": {"sentence": "Папа едет на машине.", "question": "На чём едет папа?"},
     "correct_answer": "На машине", "options": ["На машине", "На велосипеде", "На поезде", "Пешком"]},
    {"level": 3, "type": "sentence", "question_data": {"sentence": "Даша рисует солнце.", "question": "Что рисует Даша?"},
     "correct_answer": "Солнце", "options": ["Солнце", "Домик", "Кошку", "Цветок"]},
    {"level": 3, "type": "sentence", "question_data": {"sentence": "Собака бежит в парке.", "question": "Где бежит собака?"},
     "correct_answer": "В парке", "options": ["В парке", "Дома", "В школе", "В магазине"]},
    {"level": 3, "type": "sentence", "question_data": {"sentence": "Птица сидит на ветке.", "question": "Где сидит птица?"},
     "correct_answer": "На ветке", "options": ["На ветке", "На земле", "В гнезде", "На крыше"]},
    {"level": 3, "type": "sentence", "question_data": {"sentence": "Рыба плывёт в реке.", "question": "Где плывёт рыба?"},
     "correct_answer": "В реке", "options": ["В реке", "В море", "В пруду", "В аквариуме"]},
    {"level": 3, "type": "sentence", "question_data": {"sentence": "Дети играют в снегу.", "question": "Где играют дети?"},
     "correct_answer": "В снегу", "options": ["В снегу", "В песке", "В воде", "Дома"]},
    {"level": 3, "type": "sentence", "question_data": {"sentence": "Бабочка летит к цветку.", "question": "Куда летит бабочка?"},
     "correct_answer": "К цветку", "options": ["К цветку", "К дереву", "К дому", "К реке"]},
    {"level": 3, "type": "sentence", "question_data": {"sentence": "Бабушка варит суп.", "question": "Что делает бабушка?"},
     "correct_answer": "Варит суп", "options": ["Варит суп", "Печёт пирог", "Поливает цветы", "Читает книгу"]},
    {"level": 3, "type": "sentence", "question_data": {"sentence": "Ёжик нашёл грибок.", "question": "Что нашёл ёжик?"},
     "correct_answer": "Грибок", "options": ["Грибок", "Яблоко", "Ягоду", "Шишку"]},
    {"level": 3, "type": "sentence", "question_data": {"sentence": "Солнце светит ярко.", "question": "Как светит солнце?"},
     "correct_answer": "Ярко", "options": ["Ярко", "Слабо", "Не светит", "Мигает"]},
    {"level": 3, "type": "sentence", "question_data": {"sentence": "Малыш спит в кроватке.", "question": "Где спит малыш?"},
     "correct_answer": "В кроватке", "options": ["В кроватке", "На диване", "На полу", "В кресле"]},
    {"level": 3, "type": "sentence", "question_data": {"sentence": "Лиса бегает по лесу.", "question": "Кто бегает по лесу?"},
     "correct_answer": "Лиса", "options": ["Лиса", "Волк", "Заяц", "Медведь"]},
    {"level": 3, "type": "sentence", "question_data": {"sentence": "Дождь капает на землю.", "question": "Что капает на землю?"},
     "correct_answer": "Дождь", "options": ["Дождь", "Снег", "Роса", "Град"]},
]


async def main():
    from sqlalchemy import select, func
    from sqlalchemy.ext.asyncio import AsyncSession

    engine = create_async_engine(os.getenv("DATABASE_URL"), connect_args={"statement_cache_size": 0})
    async with AsyncSession(engine) as session:
        count = (await session.execute(select(func.count()).select_from(Exercise))).scalar()
        if count and count >= len(EXERCISES):
            print(f"Already have {count} exercises, skipping seed")
            await engine.dispose()
            return
        await session.execute(delete(Attempt))
        await session.execute(delete(Session))
        await session.execute(delete(Exercise))
        session.add_all([Exercise(**e) for e in EXERCISES])
        await session.commit()
    await engine.dispose()
    print(f"Seeded {len(EXERCISES)} exercises")


if __name__ == "__main__":
    asyncio.run(main())
