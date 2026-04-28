import asyncio
import os
import random
from datetime import datetime
from typing import List, Tuple

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import (
    Message,
    CallbackQuery,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

BOT_TOKEN = os.getenv("BOT_TOKEN", "8772449128:AAHgmKD47hnKcvMA17DthpTt5Vyt4mz2r5E")

# ==================== ДАННЫЕ ====================

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

SLOGANS_AND_AFFIRMATIONS = [
    # Девизы ВДА
    "Программа простая, но не лёгкая",
    "Жизнь больше, чем просто выживание",
    "Можно жить по-другому",
    "Только сегодня",
    "Не суетись",
    "Не усложняй",
    "Прогресс, а не совершенство",
    "Первым делом — главное",
    "И эта боль тоже пройдет",
    "Отпусти. Пусти Бога",
    "Стоп — не будь Голодным, Злым, Одиноким и Уставшим",
    "Возвращайтесь снова и снова",
    "Назови, но не обвиняй",
    "Попроси о помощи и прими её",
    "Без чувств нет исцеления",
    
    # Аффирмации
    "Сегодня я люблю и принимаю себя таким, какой я есть",
    "Сегодня я принимаю свои чувства",
    "Сегодня я делюсь своими чувствами",
    "Сегодня я позволяю себе совершать ошибки",
    "Сегодня мне достаточно того, кто я есть",
    "Сегодня я принимаю тебя таким, какой ты есть",
    "Сегодня я позволю жить другим",
    "Сегодня я попрошу мою Высшую Силу о поддержке и руководстве мной",
    "Сегодня я не стану обвинять ни тебя, ни себя",
    "Сегодня я имею право оберегать свои мысли, чувства и заботиться о своём теле",
    "Сегодня я смогу сказать «Нет» без чувства вины",
    "Сегодня я смогу сказать «Да» без чувства стыда",
    "Сегодня я желанный ребёнок любящих родителей",
    
    # "It's okay" аффирмации
    "Нормально знать, кто я есть",
    "Нормально доверять себе",
    "Нормально сказать: я взрослый ребёнок из дисфункциональной семьи",
    "Нормально знать другой способ жить",
    "Нормально отказывать без чувства вины",
    "Нормально дать себе передышку",
    "Нормально плакать от фильма или песни",
    "Мои чувства нормальны, даже если я их только учусь различать",
    "Нормально злиться",
    "Нормально веселиться и праздновать",
    "Нормально мечтать и надеяться",
    "Нормально отделяться с любовью",
    "Нормально заново учиться заботиться о себе",
    "Нормально сказать: я люблю себя",
    "Нормально работать по программе ВДА",
]

TYPE_EMOJI = {
    "ВДА": "🟠",
    "CoDA": "🔵",
    "UAA": "🟢",
    "АНЗ": "🟡",
}

# ==================== ФОРМАТИРОВАНИЕ ====================

def escape_html(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def format_group(time: str, name: str, kind: str, address: str) -> str:
    emoji = TYPE_EMOJI.get(kind, "⚪")
    safe_name = escape_html(name)
    safe_addr = escape_html(address)
    return f"{emoji} <b>{time}</b> — {safe_name} [{kind}]\n   📍 {safe_addr}"


def format_groups(groups: List[Tuple[str, str, str, str]], title: str = "") -> str:
    if not groups:
        return f"<i>{title}</i>\n\nГрупп не найдено."
    
    lines = [f"<b>{title}</b>\n"] if title else []
    lines.extend(format_group(*g) for g in groups)
    return "\n".join(lines)


def split_long_message(text: str, limit: int = 3800) -> List[str]:
    """Разбивает длинное сообщение на части, сохраняя HTML-теги."""
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


# ==================== БИЗНЕС-ЛОГИКА ====================

class ScheduleService:
    @staticmethod
    def get_today() -> Tuple[str, List]:
        day_index = datetime.now().weekday()
        return DAYS[day_index], SCHEDULE.get(day_index, [])
    
    @staticmethod
    def get_by_day(day_index: int) -> Tuple[str, List]:
        if 0 <= day_index <= 6:
            return DAYS[day_index], SCHEDULE.get(day_index, [])
        return "", []
    
    @staticmethod
    def get_by_type(groups: List, kind: str) -> List:
        return [g for g in groups if g[2].upper() == kind.upper()]
    
    @staticmethod
    def get_weekly_by_type(kind: str) -> str:
        kind_upper = kind.upper()
        parts = []
        for i, day_name in enumerate(DAYS):
            entries = ScheduleService.get_by_type(SCHEDULE[i], kind_upper)
            if entries:
                parts.append(format_groups(entries, f"{day_name}:"))
        return "\n\n".join(parts) if parts else f"Групп типа [{kind}] на неделе нет."
    
    @staticmethod
    def get_full_schedule() -> str:
        parts = []
        for i, day_name in enumerate(DAYS):
            entries = sorted(SCHEDULE[i], key=lambda x: x[0])
            if entries:
                parts.append(format_groups(entries, f"{day_name}:"))
        return "\n\n".join(parts)


# ==================== КЛАВИАТУРЫ ====================

def get_menu_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📅 Сегодня"), KeyboardButton(text="📋 Полное расписание")],
            [KeyboardButton(text="🟠 ВДА сегодня"), KeyboardButton(text="🔵 CoDA сегодня")],
            [KeyboardButton(text="🟢 UAA сегодня"), KeyboardButton(text="🟡 АНЗ сегодня")],
            [KeyboardButton(text="📆 Выбрать день"), KeyboardButton(text="💫 Установка на день")],
        ],
        resize_keyboard=True,
    )


def get_days_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Пн", callback_data="day_0"),
                InlineKeyboardButton(text="Вт", callback_data="day_1"),
                InlineKeyboardButton(text="Ср", callback_data="day_2"),
                InlineKeyboardButton(text="Чт", callback_data="day_3"),
            ],
            [
                InlineKeyboardButton(text="Пт", callback_data="day_4"),
                InlineKeyboardButton(text="Сб", callback_data="day_5"),
                InlineKeyboardButton(text="Вс", callback_data="day_6"),
            ],
        ]
    )


# ==================== ОТПРАВКА СООБЩЕНИЙ ====================

async def send_long_message(message: Message, text: str, parse_mode: str = "HTML"):
    """Отправляет длинное сообщение, разбивая его при необходимости."""
    parts = split_long_message(text)
    for part in parts:
        await message.answer(part, parse_mode=parse_mode)


# ==================== ДИСПЕТЧЕР ====================

dp = Dispatcher()


# ==================== КОМАНДЫ ====================

@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "🕊 <b>Добро пожаловать в бот-помощник 12-шагового сообщества!</b>\n\n"
        "Здесь ты найдёшь расписание групп ВДА, CoDA, UAA и АНЗ в Санкт-Петербурге.\n\n"
        "<i>«Жизнь больше, чем просто выживание»</i>\n\n"
        "Выбери действие на клавиатуре или используй команды:",
        parse_mode="HTML",
        reply_markup=get_menu_keyboard(),
    )
    await message.answer(
        "/today — группы на сегодня\n"
        "/full — полное расписание\n"
        "/slogan — установка на день\n"
        "/help — помощь"
    )


@dp.message(Command("today"))
async def cmd_today(message: Message):
    day_name, groups = ScheduleService.get_today()
    text = format_groups(groups, f"📅 Группы на сегодня ({day_name}):")
    await send_long_message(message, text)


@dp.message(Command("full"))
async def cmd_full(message: Message):
    text = "📋 <b>Полное расписание на неделю:</b>\n\n" + ScheduleService.get_full_schedule()
    await send_long_message(message, text)


@dp.message(Command("slogan"))
async def cmd_slogan(message: Message):
    slogan = random.choice(SLOGANS_AND_AFFIRMATIONS)
    await message.answer(
        f"💫 <b>Установка на день:</b>\n\n"
        f"<i>«{escape_html(slogan)}»</i>",
        parse_mode="HTML"
    )


@dp.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "📖 <b>Справка:</b>\n\n"
        "<b>Основные команды:</b>\n"
        "/start — перезапуск бота\n"
        "/today — группы на сегодня\n"
        "/full — полное расписание\n"
        "/slogan — установка на день\n\n"
        "<b>Фильтры по типам:</b>\n"
        "/vda — ВДА сегодня\n"
        "/coda — CoDA сегодня\n"
        "/uaa — UAA сегодня\n"
        "/anz — АНЗ сегодня\n\n"
        "<b>Или используй кнопки меню.</b>",
        parse_mode="HTML",
        reply_markup=get_menu_keyboard(),
    )


# ==================== ФИЛЬТРЫ ПО ТИПАМ ====================

@dp.message(Command("vda"))
async def cmd_vda_today(message: Message):
    _, groups = ScheduleService.get_today()
    filtered = ScheduleService.get_by_type(groups, "ВДА")
    text = format_groups(filtered, "🟠 Группы ВДА сегодня:")
    await send_long_message(message, text)


@dp.message(Command("coda"))
async def cmd_coda_today(message: Message):
    _, groups = ScheduleService.get_today()
    filtered = ScheduleService.get_by_type(groups, "CoDA")
    text = format_groups(filtered, "🔵 Группы CoDA сегодня:")
    await send_long_message(message, text)


@dp.message(Command("uaa"))
async def cmd_uaa_today(message: Message):
    _, groups = ScheduleService.get_today()
    filtered = ScheduleService.get_by_type(groups, "UAA")
    text = format_groups(filtered, "🟢 Группы UAA сегодня:")
    await send_long_message(message, text)


@dp.message(Command("anz"))
async def cmd_anz_today(message: Message):
    _, groups = ScheduleService.get_today()
    filtered = ScheduleService.get_by_type(groups, "АНЗ")
    text = format_groups(filtered, "🟡 Группы АНЗ сегодня:")
    await send_long_message(message, text)


# ==================== КНОПКИ МЕНЮ ====================

@dp.message(F.text == "📅 Сегодня")
async def btn_today(message: Message):
    await cmd_today(message)


@dp.message(F.text == "📋 Полное расписание")
async def btn_full(message: Message):
    await cmd_full(message)


@dp.message(F.text == "🟠 ВДА сегодня")
async def btn_vda(message: Message):
    await cmd_vda_today(message)


@dp.message(F.text == "🔵 CoDA сегодня")
async def btn_coda(message: Message):
    await cmd_coda_today(message)


@dp.message(F.text == "🟢 UAA сегодня")
async def btn_uaa(message: Message):
    await cmd_uaa_today(message)


@dp.message(F.text == "🟡 АНЗ сегодня")
async def btn_anz(message: Message):
    await cmd_anz_today(message)


@dp.message(F.text == "💫 Установка на день")
async def btn_slogan(message: Message):
    await cmd_slogan(message)


@dp.message(F.text == "📆 Выбрать день")
async def btn_choose_day(message: Message):
    await message.answer(
        "📆 Выбери день недели:",
        reply_markup=get_days_keyboard(),
    )


@dp.callback_query(F.data.startswith("day_"))
async def process_day_callback(callback: CallbackQuery):
    await callback.answer()
    day_index = int(callback.data.split("_")[1])
    day_name, groups = ScheduleService.get_by_day(day_index)
    
    if groups:
        text = format_groups(groups, f"📅 {day_name}:")
    else:
        text = f"📅 <b>{day_name}:</b>\n\n<i>В этот день групп нет.</i>"
    
    await send_long_message(callback.message, text)


# ==================== ЗАПУСК ====================

async def main():
    if not BOT_TOKEN:
        print("❌ Ошибка: BOT_TOKEN не задан")
        return
    
    bot = Bot(token=BOT_TOKEN)
    print("✅ Бот запущен")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
