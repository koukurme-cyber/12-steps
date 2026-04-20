import asyncio
from datetime import datetime

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

BOT_TOKEN = "ВСТАВЬТЕ_СЮДА_ТОКЕН"

SCHEDULE = {
    0: [
        ("15:00", "Выход", "ВДА", "м. Технологический институт, ул. Егорова, 11, цоколь, «Хаски»"),
        ("18:30", "ЮТА", "UAA", "адрес уточняйте на uaarus.ru"),
        ("18:45", "Путь к себе", "CoDA", "Б. Подъяческая, 34"),
        ("19:00", "Подруги", "ВДА", "м. Владимирская/Достоевская, Щербаков пер., 12, ДЦ Владимирский"),
        ("19:00", "Феникс", "ВДА", "2-я линия В.О., 3"),
        ("19:00", "Небо на Обводном", "CoDA", "наб. Обводного канала, 116"),
        ("20:15", "Замысел", "UAA", "ул. Ефимова, 6"),
        ("20:20", "Невская", "ВДА", "м. Ломоносовская, пер. Челиева, 10Б"),
    ],
    1: [
        ("16:00", "Чёрная речка", "ВДА", "м. Чёрная речка, Сестрорецкая ул., 2"),
        ("17:30", "Лотос", "ВДА", "м. Ленинский пр., Трамвайный пр., 12к2, 5 эт., ком. 33"),
        ("18:45", "Вместе", "ВДА", "м. Технологический институт, 1-я Красноармейская ул., 11"),
        ("18:45", "Черта", "ВДА", "Пискарёвский пр., 25"),
        ("19:00", "Взрослые девочки", "ВДА", "13-я линия В.О., 2, кв. 46"),
        ("19:00", "Единство Невский проспект", "UAA", "ул. Садовая, 11, 3 эт., зал 11, код #3239"),
        ("19:00", "Небо на Обводном", "CoDA", "наб. Обводного канала, 116"),
        ("19:00", "Петрополис", "АНЗ", "м. Чкаловская, ул. Колпинская, 27, Малый зал"),
        ("19:10", "Путь к себе", "CoDA", "Б. Подъяческая, 34"),
        ("20:15", "Замысел", "UAA", "ул. Ефимова, 6"),
        ("20:20", "Небо на Блюхера", "CoDA", "пр. Маршала Блюхера, 9 корп. 2, м. Лесная"),
    ],
    2: [
        ("17:00", "13 линия", "ВДА", "13-я линия В.О., 2, кв. 46"),
        ("18:00", "Солнечная сторона", "ВДА", "м. Чернышевская, ул. Радищева, 30"),
        ("19:00", "Здравствуй, Я!", "ВДА", "наб. Обводного канала, 116, ауд. 121"),
        ("19:00", "Прометей", "ВДА", "м. Московская/Пр. Славы, пр. Славы, 4"),
        ("19:00", "Феникс", "ВДА", "2-я линия В.О., 3"),
        ("19:10", "Путь к себе", "CoDA", "Б. Подъяческая, 34"),
        ("19:15", "Ручей", "ВДА", "м. Чкаловская, ул. Колпинская, 27"),
        ("20:15", "Замысел", "UAA", "ул. Ефимова, 6"),
        ("20:20", "Небо на В.О.", "CoDA", "наб. Лейтенанта Шмидта, 39, м. Василеостровская"),
        ("20:20", "Тепло (Азария)", "ВДА", "Б. Подъяческая, 34, вход со двора"),
        ("21:30", "ЮТА", "UAA", "адрес уточняйте на uaarus.ru"),
    ],
    3: [
        ("18:00", "Свобода смысла", "ВДА", "ул. Ефимова, 6"),
        ("18:45", "Черта", "ВДА", "Пискарёвский пр., 25"),
        ("19:00", "Эфир", "ВДА", "м. Московская, ул. Варшавская, 122, каб. 10"),
        ("19:00", "PRO ЖИЗНЬ", "CoDA", "ул. Казанская, 52, м. Сенная/Садовая/Спасская"),
        ("19:00", "Небо на Обводном", "CoDA", "наб. Обводного канала, 116"),
        ("20:00", "Тепло (Азария)", "ВДА", "Б. Подъяческая, 34, вход со двора"),
        ("20:15", "Замысел", "UAA", "ул. Ефимова, 6"),
        ("20:20", "Небо на Блюхера", "CoDA", "пр. Маршала Блюхера, 9 корп. 2"),
    ],
    4: [
        ("18:10", "Ручей", "ВДА", "м. Чкаловская, ул. Колпинская, 27"),
        ("18:30", "ЮТА", "UAA", "адрес уточняйте на uaarus.ru"),
        ("19:00", "Феникс", "ВДА", "2-я линия В.О., 3"),
        ("19:00", "Тепло (Азария)", "ВДА", "Б. Подъяческая, 34, вход со двора"),
        ("19:00", "Любящий родитель", "ВДА", "наб. Обводного канала, 116"),
        ("19:00", "Небо на Обводном", "CoDA", "наб. Обводного канала, 116"),
        ("19:00", "Солнечная", "CoDA", "Инженерная ул., 6, бизнес-центр, 2 этаж, каб. 14"),
        ("20:15", "Замысел", "UAA", "ул. Ефимова, 6"),
        ("20:20", "Путь к себе", "CoDA", "Б. Подъяческая, 34"),
    ],
    5: [
        ("11:00", "Взрослые девочки", "ВДА", "13-я линия В.О., 2, кв. 46"),
        ("13:00", "13 линия", "ВДА", "13-я линия В.О., 2, кв. 46"),
        ("13:00", "Петрополис", "АНЗ", "м. Чкаловская, ул. Колпинская, 27, Малый зал"),
        ("14:00", "Свобода смысла", "ВДА", "ул. Ефимова, 6"),
        ("15:00", "Солнечная", "CoDA", "Инженерная ул., 6, бизнес-центр, 2 этаж, каб. 14"),
        ("16:00", "Говори, доверяй, чувствуй", "ВДА", "пр. Энгельса, 132"),
        ("17:00", "Парнас", "ВДА", "6-й Верхний пер., 12Б, 5 эт., оф. 2"),
        ("18:15", "AdA (Abused Anonymus)", "ВДА", "ул. Миргородская, 1Д"),
        ("18:30", "ЮТА", "UAA", "адрес уточняйте на uaarus.ru"),
        ("19:00", "Солнечная сторона", "ВДА", "м. Чернышевская, ул. Радищева, 30"),
        ("19:00", "Феникс", "ВДА", "2-я линия В.О., 3"),
        ("20:15", "Замысел", "UAA", "ул. Ефимова, 6"),
    ],
    6: [
        ("11:00", "Взрослые девочки", "ВДА", "13-я линия В.О., 2, кв. 46"),
        ("12:00", "Мост", "CoDA", "г. Красное Село, ул. Массальского, 3"),
        ("13:00", "Черта", "ВДА", "Пискарёвский пр., 25"),
        ("14:30", "Практика «Любящий родитель»", "ВДА", "в рамках группы «Черта»"),
        ("15:00", "Воскресенье", "ВДА", "м. Автово, ул. Маршала Захарова, 13, п. 3, цоколь"),
        ("15:10", "Феникс", "ВДА", "2-я линия В.О., 3"),
        ("16:30", "Все свободны", "ВДА", "м. Чернышевская, ул. Таврическая, 5"),
        ("17:00", "проСВЕТ", "ВДА", "Выборгское ш., 15 (ТЦ «Авеню»), м. Пр. Просвещения"),
        ("17:00", "Небо на В.О.", "CoDA", "наб. Лейтенанта Шмидта, 39"),
        ("18:00", "Прометей", "ВДА", "м. Московская/Пр. Славы, пр. Славы, 4"),
        ("18:30", "Путь к себе", "CoDA", "Б. Подъяческая, 34"),
        ("19:00", "Единство Невский проспект", "UAA", "ул. Садовая, 11, 3 эт., зал 11, код #3239"),
        ("19:30", "PRO ЖИЗНЬ", "CoDA", "ул. Казанская, 52"),
        ("20:15", "Замысел", "UAA", "ул. Ефимова, 6"),
    ],
}

DAYS = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]

MENU_KB = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Сегодня"), KeyboardButton(text="Полное расписание")],
        [KeyboardButton(text="ВДА"), KeyboardButton(text="CoDA")],
        [KeyboardButton(text="UAA"), KeyboardButton(text="АНЗ")],
        [KeyboardButton(text="ВДА неделя"), KeyboardButton(text="CoDA неделя")],
        [KeyboardButton(text="UAA неделя"), KeyboardButton(text="АНЗ неделя")],
    ],
    resize_keyboard=True
)

def format_entries(entries):
    return "\n".join(f"{t} — {n} [{k}] — {a}" for t, n, k, a in entries)

def split_text(text, limit=3800):
    parts = []
    while len(text) > limit:
        cut = text.rfind("\n", 0, limit)
        if cut == -1:
            cut = limit
        parts.append(text[:cut].strip())
        text = text[cut:].lstrip("\n")
    if text.strip():
        parts.append(text.strip())
    return parts

def full_schedule():
    parts = []
    for i, day_name in enumerate(DAYS):
        parts.append(f"{day_name}:\n{format_entries(SCHEDULE[i])}")
    return "\n\n".join(parts)

def weekly_by_type(kind):
    kind = kind.upper()
    parts = []
    for i, day_name in enumerate(DAYS):
        entries = [e for e in SCHEDULE[i] if e[2].upper() == kind]
        if entries:
            parts.append(f"{day_name}:\n{format_entries(entries)}")
    return "\n\n".join(parts) if parts else f"По типу [{kind}] записей нет."

async def send_long(message: Message, text: str):
    for part in split_text(text):
        await message.answer(part)

dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "Привет! Я бот с расписанием групп.\n\n"
        "Выбери команду на клавиатуре ниже:",
        reply_markup=MENU_KB
    )

@dp.message(Command("menu"))
async def cmd_menu(message: Message):
    await message.answer("Выбирай команду:", reply_markup=MENU_KB)

@dp.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "Команды бота:\n\n"
        "/menu — меню кнопками\n"
        "/today — группы на сегодня\n"
        "/vda — ВДА на сегодня\n"
        "/coda — CoDA на сегодня\n"
        "/uaa — UAA на сегодня\n"
        "/anz — АНЗ на сегодня\n"
        "/vda_week — ВДА за неделю\n"
        "/coda_week — CoDA за неделю\n"
        "/uaa_week — UAA за неделю\n"
        "/anz_week — АНЗ за неделю\n"
        "/full — полное расписание на неделю",
        reply_markup=MENU_KB
    )

@dp.message(Command("today"))
async def cmd_today(message: Message):
    day = datetime.now().weekday()
    await send_long(message, "Группы на сегодня:\n\n" + format_entries(SCHEDULE.get(day, [])))

@dp.message(Command("vda"))
async def cmd_vda(message: Message):
    day = datetime.now().weekday()
    entries = [e for e in SCHEDULE.get(day, []) if e[2].upper() == "ВДА"]
    await send_long(message, "ВДА на сегодня:\n\n" + format_entries(entries) if entries else "Сегодня групп ВДА нет.")

@dp.message(Command("coda"))
async def cmd_coda(message: Message):
    day = datetime.now().weekday()
    entries = [e for e in SCHEDULE.get(day, []) if e[2].upper() == "CODA"]
    await send_long(message, "CoDA на сегодня:\n\n" + format_entries(entries) if entries else "Сегодня групп CoDA нет.")

@dp.message(Command("uaa"))
async def cmd_uaa(message: Message):
    day = datetime.now().weekday()
    entries = [e for e in SCHEDULE.get(day, []) if e[2].upper() == "UAA"]
    await send_long(message, "UAA на сегодня:\n\n" + format_entries(entries) if entries else "Сегодня групп UAA нет.")

@dp.message(Command("anz"))
async def cmd_anz(message: Message):
    day = datetime.now().weekday()
    entries = [e for e in SCHEDULE.get(day, []) if e[2].upper() == "АНЗ"]
    await send_long(message, "АНЗ на сегодня:\n\n" + format_entries(entries) if entries else "Сегодня групп АНЗ нет.")

@dp.message(Command("vda_week"))
async def cmd_vda_week(message: Message):
    await send_long(message, "ВДА за неделю:\n\n" + weekly_by_type("ВДА"))

@dp.message(Command("coda_week"))
async def cmd_coda_week(message: Message):
    await send_long(message, "CoDA за неделю:\n\n" + weekly_by_type("CoDA"))

@dp.message(Command("uaa_week"))
async def cmd_uaa_week(message: Message):
    await send_long(message, "UAA за неделю:\n\n" + weekly_by_type("UAA"))

@dp.message(Command("anz_week"))
async def cmd_anz_week(message: Message):
    await send_long(message, "АНЗ за неделю:\n\n" + weekly_by_type("АНЗ"))

@dp.message(Command("full"))
async def cmd_full(message: Message):
    await send_long(message, "Полное расписание на неделю:\n\n" + full_schedule())

async def main():
    bot = Bot(token=BOT_TOKEN)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
