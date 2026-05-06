import asyncio
import json
import os
import random
from datetime import datetime, timedelta
from typing import List, Tuple, Optional, Dict, Any

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    KeyboardButton,
)
from aiogram.utils.keyboard import ReplyKeyboardBuilder


BOT_TOKEN = os.getenv("BOT_TOKEN")

SUBSCRIBERS_FILE = "subscribers.json"

# Время ежедневной авторассылки по Москве
DAILY_NOTIFY_HOUR = 9
DAILY_NOTIFY_MINUTE = 0

# Сколько ближайших групп показывать
NEAREST_LIMIT = 5


def moscow_now():
    return datetime.utcnow() + timedelta(hours=3)


metro_stations_cache = []


# ==================== РАСПИСАНИЕ (время, название, тип, метро, адрес) ====================
SCHEDULE = {
    0: [  # Понедельник
        ("09:00", "Небо на Обводном", "CoDA", "м. Балтийская",
         "наб. Обводного канала, 116, храм Воскресения Христова, здание воскресной школы. +7 911 952 7073"),
        ("15:00", "Выход", "ВДА", "м. Технологический институт", "ул. Егорова, 11, цоколь, помещение «Хаски». +7 911 995-25-35, Евгения"),
        ("18:30", "ЮТА", "UAA", "", "адрес уточняйте на uaarus.ru"),
        ("18:45", "Путь к себе", "CoDA", "м. Сенная/Садовая/Спасская", "Б. Подъяческая, 34, РБОО «АЗАРИЯ». +7 911 928 67 10"),
        ("19:00", "Подруги", "ВДА", "м. Владимирская", "Щербаков пер., 12, ДЦ Владимирский. t.me/spb_aca_girls"),
        ("19:00", "Феникс", "ВДА", "м. Василеостровская", "2-я линия В.О., 3, Информационный кабинет. +7 965 787-05-74"),
        ("20:15", "Замысел", "UAA", "м. Сенная/Садовая/Спасская", "ул. Ефимова, 6"),
        ("20:20", "Невская", "ВДА", "м. Ломоносовская", "пер. Челиева, 10Б, Подворье Свято-Троицкого монастыря. +7 911 964-73-58"),
    ],
    1: [  # Вторник
        ("16:00", "Чёрная речка", "ВДА", "м. Чёрная речка", "Сестрорецкая ул., 2, вход через магазин «Рыбалка». t.me/+la-lJbgvZ..."),
        ("17:30", "Лотос", "ВДА", "м. Ленинский проспект", "Трамвайный пр., 12к2, 5 эт., ком. 33. +7 921 904-49-86"),
        ("18:45", "Вместе", "ВДА", "м. Технологический институт", "1-я Красноармейская ул., 11, цоколь. +7 921 633-43-32, Алёна"),
        ("18:45", "Черта", "ВДА", "м. пл. Мужества", "Пискарёвский пр., 25, 4 эт., пом. 5. t.me/+pktT8AlhN..."),
        ("19:00", "Взрослые девочки", "ВДА", "м. Василеостровская", "13-я линия В.О., 2, кв. 46, синяя дверь во дворе. +7 911 156-54-77"),
        ("19:00", "Единство Невский проспект", "UAA", "м. Невский пр.", "ул. Садовая, 11, 3 эт., зал 11, код #3239"),
        ("19:00", "Петрополис", "АНЗ", "м. Чкаловская", "ул. Колпинская, 27, Малый зал"),
        ("19:00", "Небо на Обводном", "CoDA", "м. Балтийская", "наб. Обводного канала, 116. +7 911 952 7073"),
        ("19:10", "Путь к себе", "CoDA", "м. Сенная/Садовая/Спасская", "Б. Подъяческая, 34, РБОО «АЗАРИЯ». +7 911 928 67 10"),
        ("20:15", "Замысел", "UAA", "м. Сенная/Садовая/Спасская", "ул. Ефимова, 6"),
        ("20:20", "Тепло (Азария)", "ВДА", "м. Садовая/Технологический институт", "Б. Подъяческая, 34, вход со двора"),
        ("20:20", "Небо на Блюхера", "CoDA", "м. Лесная", "пр. Маршала Блюхера, 9, корп. 2, храм сщмч. Петра Скипетрова. +7 911 952 7073"),
    ],
    2: [  # Среда
        ("17:00", "13 линия", "ВДА", "м. Василеостровская", "13-я линия В.О., 2, кв. 46. vk.com/club117132895"),
        ("17:00", "Участие на Юго-Западе", "CoDA", "м. Автово", "ул. Маршала Захарова, 13, 3 подъезд, цоколь. +7 981 945 54 37"),
        ("18:00", "Солнечная сторона", "ВДА", "м. Чернышевская", "ул. Радищева, 30, Пространство «Просвет», зал Просвещение. t.me/+qFRjoIzA_..."),
        ("19:00", "Здравствуй, Я!", "ВДА", "м. Балтийская", "наб. Обводного канала, 116, ауд. 121. +7 906 246-56-93, Марина"),
        ("19:00", "Прометей", "ВДА", "м. Пр. Славы", "пр. Славы, 4, 2 эт. +7 911 277-49-11"),
        ("19:00", "Феникс", "ВДА", "м. Василеостровская", "2-я линия В.О., 3. +7 965 787-05-74"),
        ("19:10", "Путь к себе", "CoDA", "м. Сенная/Садовая/Спасская", "Б. Подъяческая, 34, РБОО «АЗАРИЯ». +7 911 928 67 10"),
        ("19:15", "Ручей", "ВДА", "м. Чкаловская", "ул. Колпинская, 27, пространство «Ручей». Рабочее собрание в посл. среду 20:15"),
        ("20:15", "Замысел", "UAA", "м. Сенная/Садовая/Спасская", "ул. Ефимова, 6"),
        ("20:20", "Тепло (Азария)", "ВДА", "м. Садовая/Технологический институт", "Б. Подъяческая, 34, вход со двора"),
        ("20:20", "Небо на В.О.", "CoDA", "м. Василеостровская", "наб. Лейтенанта Шмидта, 39. +7 911 952 7073"),
    ],
    3: [  # Четверг
        ("18:00", "Свобода смысла", "ВДА", "м. Сенная/Садовая/Спасская", "ул. Ефимова, 6, домофон 57, 2 эт. t.me/+b14S_QR3Q..."),
        ("18:45", "Черта", "ВДА", "м. пл. Мужества", "Пискарёвский пр., 25, 4 эт., пом. 5"),
        ("19:00", "Эфир", "ВДА", "м. Московская", "ул. Варшавская, 122, каб. 10. +7 999 037-13-05"),
        ("19:00", "PRO ЖИЗНЬ", "CoDA", "м. Сенная/Садовая/Спасская", "ул. Казанская, 52. +7 911 928 67 10"),
        ("19:00", "Небо на Обводном", "CoDA", "м. Балтийская", "наб. Обводного канала, 116. +7 911 952 7073"),
        ("20:00", "Тепло (Азария)", "ВДА", "м. Садовая/Технологический институт", "Б. Подъяческая, 34, вход со двора"),
        ("20:15", "Замысел", "UAA", "м. Сенная/Садовая/Спасская", "ул. Ефимова, 6"),
        ("20:20", "Небо на Блюхера", "CoDA", "м. Лесная", "пр. Маршала Блюхера, 9, корп. 2. +7 911 952 7073"),
    ],
    4: [  # Пятница
        ("18:10", "Ручей", "ВДА", "м. Чкаловская", "ул. Колпинская, 27, пространство «Ручей»"),
        ("18:30", "ЮТА", "UAA", "", "адрес уточняйте на uaarus.ru"),
        ("19:00", "Феникс", "ВДА", "м. Василеостровская", "2-я линия В.О., 3"),
        ("19:00", "Тепло (Азария)", "ВДА", "м. Садовая/Технологический институт", "Б. Подъяческая, 34, вход со двора"),
        ("19:00", "Любящий родитель", "ВДА", "м. Балтийская", "наб. Обводного канала, 116, Лекционка в храме. +7 952 236 77 44, Валерия"),
        ("19:00", "Сознание Пушкин", "CoDA", "", "г. Пушкин, ул. Магазейная, 22/30, полуподвал. +7 911 711 80 81"),
        ("19:00", "Небо на Обводном", "CoDA", "м. Балтийская", "наб. Обводного канала, 116. +7 911 952 7073"),
        ("19:00", "Солнечная", "CoDA", "м. Невский пр.", "ул. Садовая, 7-9-11, пространство «Ступени», 3 эт., оф. 38, каб. 7"),
        ("20:15", "Замысел", "UAA", "м. Сенная/Садовая/Спасская", "ул. Ефимова, 6"),
        ("20:20", "Путь к себе", "CoDA", "м. Сенная/Садовая/Спасская", "Б. Подъяческая, 34, РБОО «АЗАРИЯ». +7 911 928 67 10"),
    ],
    5: [  # Суббота
        ("11:00", "Взрослые девочки", "ВДА", "м. Василеостровская", "13-я линия В.О., 2, кв. 46. +7 911 156-54-77"),
        ("13:00", "13 линия", "ВДА", "м. Василеостровская", "13-я линия В.О., 2, кв. 46. vk.com/club117132895"),
        ("13:00", "Петрополис", "АНЗ", "м. Чкаловская", "ул. Колпинская, 27, Малый зал"),
        ("14:00", "Свобода смысла", "ВДА", "м. Сенная/Садовая/Спасская", "ул. Ефимова, 6. t.me/+b14S_QR3Q..."),
        ("14:30", "Участие на Юго-Западе", "CoDA", "м. Автово", "ул. Маршала Захарова, 13, 3 подъезд, цоколь. +7 981 945 54 37"),
        ("15:00", "Солнечная", "CoDA", "м. Невский пр.", "Инженерная ул., 6, бизнес-центр, 2 эт., каб. 14"),
        ("16:00", "Говори, доверяй, чувствуй", "ВДА", "м. Пр. Просвещения", "пр. Энгельса, 132, подвал во дворе у «Бристоль». +7 905 274-55-50, Алёна"),
        ("17:00", "Парнас", "ВДА", "м. Парнас", "6-й Верхний пер., 12Б, 5 эт., оф. 2. +7 921 434-05-66"),
        ("18:30", "ЮТА", "UAA", "", "адрес уточняйте на uaarus.ru"),
        ("19:00", "Солнечная сторона", "ВДА", "м. Чернышевская", "ул. Радищева, 30, Пространство «Просвет»"),
        ("19:00", "Феникс", "ВДА", "м. Василеостровская", "2-я линия В.О., 3"),
        ("20:15", "Замысел", "UAA", "м. Сенная/Садовая/Спасская", "ул. Ефимова, 6"),
    ],
    6: [  # Воскресенье
        ("11:00", "Взрослые девочки", "ВДА", "м. Василеостровская", "13-я линия В.О., 2, кв. 46. +7 911 156-54-77"),
        ("12:00", "Мост", "CoDA", "", "г. Красное Село, ул. Массальского, 3. +7 952 236-39-81"),
        ("13:00", "Черта", "ВДА", "м. пл. Мужества", "Пискарёвский пр., 25, 4 эт., пом. 5"),
        ("14:30", "Любящий родитель (практика)", "ВДА", "м. пл. Мужества", "в рамках группы «Черта», Пискарёвский пр., 25"),
        ("15:00", "Воскресенье", "ВДА", "м. Автово", "ул. Маршала Захарова, 13, 3 подъезд, цоколь. +7 918 351-04-44, Елена"),
        ("15:10", "Феникс", "ВДА", "м. Василеостровская", "2-я линия В.О., 3"),
        ("16:30", "Все свободны", "ВДА", "м. Чернышевская", "ул. Таврическая, 5. t.me/vsefree_vda"),
        ("17:00", "проСВЕТ", "ВДА", "м. Пр. Просвещения", "Выборгское ш., 15, ТЦ «Авеню», 3 эт. +7 999 202-91-71"),
        ("17:00", "Небо на В.О.", "CoDA", "м. Василеостровская", "наб. Лейтенанта Шмидта, 39. +7 911 952 7073"),
        ("18:00", "Прометей", "ВДА", "м. Пр. Славы", "пр. Славы, 4, 2 эт. +7 911 277-49-11"),
        ("18:30", "Путь к себе", "CoDA", "м. Сенная/Садовая/Спасская", "Б. Подъяческая, 34. +7 911 928 67 10"),
        ("19:00", "Единство Невский проспект", "UAA", "м. Невский пр.", "ул. Садовая, 11, 3 эт., зал 11, код #3239"),
        ("19:30", "PRO ЖИЗНЬ", "CoDA", "м. Сенная/Садовая/Спасская", "ул. Казанская, 52. +7 911 928 67 10"),
        ("20:15", "Замысел", "UAA", "м. Сенная/Садовая/Спасская", "ул. Ефимова, 6"),
    ],
}

DAYS = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]

SLOGANS_AND_AFFIRMATIONS = [
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

TYPE_TITLES = {
    "ВДА": "🟠 ВДА",
    "CoDA": "🔵 CoDA",
    "UAA": "🟢 UAA",
    "АНЗ": "🟡 АНЗ",
}


# ==================== ПОДПИСЧИКИ ДЛЯ АВТОРАССЫЛКИ ====================
def load_subscribers() -> set[int]:
    if not os.path.exists(SUBSCRIBERS_FILE):
        return set()

    try:
        with open(SUBSCRIBERS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, list):
            return set()

        return {int(chat_id) for chat_id in data}
    except Exception as e:
        print(f"Ошибка чтения файла подписчиков: {e}")
        return set()


def save_subscribers(subscribers: set[int]) -> None:
    try:
        with open(SUBSCRIBERS_FILE, "w", encoding="utf-8") as f:
            json.dump(sorted(list(subscribers)), f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Ошибка записи файла подписчиков: {e}")


def add_subscriber(chat_id: int) -> None:
    subscribers = load_subscribers()

    if chat_id not in subscribers:
        subscribers.add(chat_id)
        save_subscribers(subscribers)


# ==================== ФОРМАТИРОВАНИЕ ====================
def escape_html(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def get_group_key(day_index: int, group_index: int) -> str:
    return f"{day_index}:{group_index}"


def parse_group_key(group_key: str) -> Optional[Tuple[int, int]]:
    try:
        day_index_str, group_index_str = group_key.split(":", 1)
        day_index = int(day_index_str)
        group_index = int(group_index_str)

        if day_index not in SCHEDULE:
            return None

        if group_index < 0 or group_index >= len(SCHEDULE[day_index]):
            return None

        return day_index, group_index
    except Exception:
        return None


def get_group_by_key(group_key: str) -> Optional[Tuple[int, int, Tuple]]:
    parsed = parse_group_key(group_key)

    if not parsed:
        return None

    day_index, group_index = parsed
    return day_index, group_index, SCHEDULE[day_index][group_index]


def get_relative_day_label(group_dt: datetime) -> str:
    now = moscow_now()
    today = now.date()
    group_date = group_dt.date()

    if group_date == today:
        return "Сегодня"

    if group_date == today + timedelta(days=1):
        return "Завтра"

    return DAYS[group_dt.weekday()]


def format_group_short(day_index: int, group_index: int, group: Tuple, show_day: bool = False) -> str:
    time_str, name, kind, metro, _address = group
    emoji = TYPE_EMOJI.get(kind, "⚪")
    day_part = f"{DAYS[day_index]}, " if show_day else ""
    metro_part = f" · {escape_html(metro)}" if metro else ""
    return f"{emoji} <b>{day_part}{time_str}</b> — {escape_html(name)} [{escape_html(kind)}]{metro_part}"


def format_group_details(day_index: int, group_index: int, group: Tuple) -> str:
    time_str, name, kind, metro, address = group
    emoji = TYPE_EMOJI.get(kind, "⚪")

    metro_line = f"\n🚇 <b>Метро:</b> {escape_html(metro)}" if metro else ""

    return (
        f"{emoji} <b>{escape_html(name)}</b>\n\n"
        f"📅 <b>День:</b> {escape_html(DAYS[day_index])}\n"
        f"🕒 <b>Время:</b> {escape_html(time_str)}\n"
        f"👥 <b>Сообщество:</b> {escape_html(kind)}"
        f"{metro_line}\n"
        f"📍 <b>Адрес и пояснения:</b>\n{escape_html(address)}"
    )


def format_group_for_daily(time: str, name: str, kind: str, metro: str, address: str) -> str:
    emoji = TYPE_EMOJI.get(kind, "⚪")
    metro_str = f"   🚇 {escape_html(metro)}\n" if metro else ""

    return (
        f"{emoji} <b>{escape_html(time)}</b> — {escape_html(name)} [{escape_html(kind)}]\n"
        f"{metro_str}"
        f"   📍 {escape_html(address)}"
    )


def split_long_message(text: str, limit: int = 3800) -> List[str]:
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


def build_details_keyboard(day_index: int, group_index: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Подробнее",
                    callback_data=f"detail:{get_group_key(day_index, group_index)}",
                )
            ]
        ]
    )


def build_group_choice_keyboard(items: List[Dict[str, Any]], show_day: bool = False, nearest_mode: bool = False) -> InlineKeyboardMarkup:
    rows = []

    for item in items:
        day_index = item["day_index"]
        group_index = item["group_index"]
        group = item["group"]
        time_str, name, kind, metro, _address = group
        emoji = TYPE_EMOJI.get(kind, "⚪")

        if nearest_mode and "datetime" in item:
            group_dt = item["datetime"]
            day_label = get_relative_day_label(group_dt)
            prefix = f"{day_label}, {time_str}"
        elif show_day:
            prefix = f"{DAYS[day_index][:2]}, {time_str}"
        else:
            prefix = time_str

        metro_part = f" · {metro.replace('м. ', '')}" if metro else ""
        button_text = f"{emoji} {prefix} · {name} [{kind}]{metro_part}"

        if len(button_text) > 64:
            button_text = button_text[:61] + "..."

        rows.append(
            [
                InlineKeyboardButton(
                    text=button_text,
                    callback_data=f"detail:{get_group_key(day_index, group_index)}",
                )
            ]
        )

    return InlineKeyboardMarkup(inline_keyboard=rows)


async def send_long_message(message: Message, text: str, parse_mode: str = "HTML"):
    for part in split_long_message(text):
        await message.answer(part, parse_mode=parse_mode)


async def send_long_message_to_chat(bot: Bot, chat_id: int, text: str, parse_mode: str = "HTML"):
    for part in split_long_message(text):
        await bot.send_message(chat_id, part, parse_mode=parse_mode)
        await asyncio.sleep(0.05)


async def send_group_list_message(
    message: Message,
    items: List[Dict[str, Any]],
    title: str,
    show_day: bool = False,
):
    if not items:
        await message.answer(
            f"<b>{escape_html(title)}</b>

<i>Групп не найдено.</i>",
            parse_mode="HTML",
        )
        return

    if len(items) <= 60:
        await message.answer(
            f"<b>{escape_html(title)}</b>

Выбери группу, чтобы открыть адрес и пояснения:",
            parse_mode="HTML",
            reply_markup=build_group_choice_keyboard(items, show_day=show_day),
        )
        return

    # Защита на случай чрезмерно длинного списка: Telegram ограничивает размер inline-клавиатуры.
    # В обычном расписании этого лимита не будет, но лучше оставить безопасный fallback.
    lines = [f"<b>{escape_html(title)}</b>
"]
    for item in items:
        lines.append(
            format_group_short(
                item["day_index"],
                item["group_index"],
                item["group"],
                show_day=show_day,
            )
        )

    await send_long_message(message, "
".join(lines))


# ==================== БИЗНЕС-ЛОГИКА ====================
class ScheduleService:
    @staticmethod
    def get_today():
        day_index = moscow_now().weekday()
        return day_index, DAYS[day_index], SCHEDULE.get(day_index, [])

    @staticmethod
    def get_by_day(day_index: int):
        if 0 <= day_index <= 6:
            return DAYS[day_index], SCHEDULE.get(day_index, [])
        return "", []

    @staticmethod
    def get_items_for_day(day_index: int, kind: Optional[str] = None) -> List[Dict[str, Any]]:
        items = []

        if day_index not in SCHEDULE:
            return items

        for group_index, group in enumerate(SCHEDULE[day_index]):
            if kind and group[2].upper() != kind.upper():
                continue

            items.append(
                {
                    "day_index": day_index,
                    "group_index": group_index,
                    "group": group,
                }
            )

        return sorted(items, key=lambda x: x["group"][0])

    @staticmethod
    def get_items_for_week(kind: Optional[str] = None) -> List[Dict[str, Any]]:
        items = []

        for day_index in range(7):
            items.extend(ScheduleService.get_items_for_day(day_index, kind=kind))

        return items

    @staticmethod
    def get_by_type(groups: List[Tuple], kind: str):
        return [g for g in groups if g[2].upper() == kind.upper()]

    @staticmethod
    def get_by_metro(metro_query: str) -> List[Dict[str, Any]]:
        q = metro_query.lower().strip()
        result = []

        for day_index, groups in SCHEDULE.items():
            for group_index, group in enumerate(groups):
                if q in group[3].lower():
                    result.append(
                        {
                            "day_index": day_index,
                            "group_index": group_index,
                            "group": group,
                        }
                    )

        return result

    @staticmethod
    def get_all_metro_stations():
        stations = set()

        for groups in SCHEDULE.values():
            for group in groups:
                if group[3]:
                    stations.add(group[3])

        return sorted(stations)

    @staticmethod
    def get_nearest_groups(kind: Optional[str] = None, limit: int = NEAREST_LIMIT) -> List[Dict[str, Any]]:
        now = moscow_now()
        result = []

        for day_offset in range(0, 8):
            target_date = now.date() + timedelta(days=day_offset)
            day_index = target_date.weekday()
            groups = SCHEDULE.get(day_index, [])

            for group_index, group in enumerate(groups):
                time_str, _name, group_kind, _metro, _address = group

                if kind and group_kind.upper() != kind.upper():
                    continue

                hour, minute = map(int, time_str.split(":"))
                group_dt = datetime(
                    year=target_date.year,
                    month=target_date.month,
                    day=target_date.day,
                    hour=hour,
                    minute=minute,
                )

                if group_dt >= now:
                    result.append(
                        {
                            "datetime": group_dt,
                            "day_index": day_index,
                            "group_index": group_index,
                            "group": group,
                        }
                    )

        result.sort(key=lambda x: x["datetime"])
        return result[:limit]

    @staticmethod
    def get_week_title(kind: Optional[str] = None):
        if kind:
            return f"{TYPE_TITLES.get(kind, kind)} на неделю"
        return "📋 Полное расписание на неделю"


def build_daily_live_groups_message() -> str:
    day_index, day_name, groups = ScheduleService.get_today()

    if not groups:
        return f"Привет, живые группы сегодня ({escape_html(day_name)}) не найдены."

    lines = [f"Привет, живые группы сегодня ({escape_html(day_name)}):\n"]

    for group in sorted(groups, key=lambda x: x[0]):
        lines.append(format_group_for_daily(*group))

    return "\n\n".join(lines)


def format_nearest_groups(items: List[Dict[str, Any]], kind: Optional[str] = None) -> str:
    if kind:
        title = f"⏱ Ближайшие группы {TYPE_TITLES.get(kind, kind)}"
    else:
        title = "⏱ Ближайшие группы"

    if not items:
        return f"<b>{escape_html(title)}</b>

<i>Ближайших групп не найдено.</i>"

    return f"<b>{escape_html(title)}</b>

Выбери группу, чтобы открыть адрес и пояснения:"


async def send_nearest_groups_message(message: Message, kind: Optional[str] = None):
    items = ScheduleService.get_nearest_groups(kind=kind, limit=NEAREST_LIMIT)
    text = format_nearest_groups(items, kind=kind)

    if not items:
        await message.answer(text, parse_mode="HTML")
        return

    keyboard = build_group_choice_keyboard(items, nearest_mode=True)
    await message.answer(text, parse_mode="HTML", reply_markup=keyboard)


# ==================== АВТОРАССЫЛКА ====================
async def daily_notification_worker(bot: Bot):
    last_sent_date = None

    while True:
        now = moscow_now()
        today_key = now.strftime("%Y-%m-%d")

        if (
            now.hour == DAILY_NOTIFY_HOUR
            and now.minute == DAILY_NOTIFY_MINUTE
            and last_sent_date != today_key
        ):
            text = build_daily_live_groups_message()
            subscribers = load_subscribers()

            print(f"Запуск ежедневной рассылки: {today_key}, получателей: {len(subscribers)}")

            for chat_id in subscribers:
                try:
                    await send_long_message_to_chat(bot, chat_id, text, parse_mode="HTML")
                except Exception as e:
                    print(f"Не удалось отправить уведомление chat_id={chat_id}: {e}")

            last_sent_date = today_key

        await asyncio.sleep(20)


# ==================== КЛАВИАТУРЫ ====================
def get_menu_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text="📅 Сегодня"), KeyboardButton(text="⏱ Ближайшие"))
    builder.row(KeyboardButton(text="📋 Полное расписание"), KeyboardButton(text="📆 Выбрать день"))
    builder.row(KeyboardButton(text="🟠 ВДА сегодня"), KeyboardButton(text="🔵 CoDA сегодня"))
    builder.row(KeyboardButton(text="🟢 UAA сегодня"), KeyboardButton(text="🟡 АНЗ сегодня"))
    builder.row(KeyboardButton(text="🚇 Поиск по метро"), KeyboardButton(text="💫 Установка на день"))
    return builder.as_markup(resize_keyboard=True)


def get_days_keyboard():
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


def get_full_schedule_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📋 Вся неделя", callback_data="week_all"),
            ],
            [
                InlineKeyboardButton(text="🟠 ВДА на неделю", callback_data="week_type:ВДА"),
                InlineKeyboardButton(text="🔵 CoDA на неделю", callback_data="week_type:CoDA"),
            ],
            [
                InlineKeyboardButton(text="🟢 UAA на неделю", callback_data="week_type:UAA"),
                InlineKeyboardButton(text="🟡 АНЗ на неделю", callback_data="week_type:АНЗ"),
            ],
        ]
    )


def get_nearest_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="⏱ Все ближайшие", callback_data="nearest_all"),
            ],
            [
                InlineKeyboardButton(text="🟠 ВДА", callback_data="nearest_type:ВДА"),
                InlineKeyboardButton(text="🔵 CoDA", callback_data="nearest_type:CoDA"),
            ],
            [
                InlineKeyboardButton(text="🟢 UAA", callback_data="nearest_type:UAA"),
                InlineKeyboardButton(text="🟡 АНЗ", callback_data="nearest_type:АНЗ"),
            ],
        ]
    )


def get_metro_inline_keyboard():
    global metro_stations_cache

    stations = ScheduleService.get_all_metro_stations()
    metro_stations_cache = stations

    buttons = []

    for i in range(0, len(stations), 2):
        row = [InlineKeyboardButton(text=stations[i], callback_data=f"metro_{i}")]

        if i + 1 < len(stations):
            row.append(InlineKeyboardButton(text=stations[i + 1], callback_data=f"metro_{i + 1}"))

        buttons.append(row)

    return InlineKeyboardMarkup(inline_keyboard=buttons)


# ==================== ДИСПЕТЧЕР ====================
dp = Dispatcher()


@dp.message(Command("start"))
async def cmd_start(message: Message):
    add_subscriber(message.chat.id)

    await message.answer(
        "🕊 <b>Бот расписания живых групп</b>\n\n"
        "Здесь есть расписание групп ВДА, CoDA, UAA и АНЗ в Санкт-Петербурге.\n\n"
        "Каждый день бот автоматически отправляет живые группы на сегодня.\n\n"
        "<i>«Жизнь больше, чем просто выживание»</i>\n\n"
        "Выбери действие на клавиатуре:",
        parse_mode="HTML",
        reply_markup=get_menu_keyboard(),
    )

    await message.answer(
        "/today — группы на сегодня\n"
        "/nearest — ближайшие 5 групп\n"
        "/full — выбрать недельное расписание\n"
        "/metro — поиск по станции метро\n"
        "/slogan — установка на день\n"
        "/help — помощь"
    )


@dp.message(Command("today"))
async def cmd_today(message: Message):
    day_index, day_name, _groups = ScheduleService.get_today()
    items = ScheduleService.get_items_for_day(day_index)
    await send_group_list_message(message, items, f"📅 Группы на сегодня ({day_name}):")


@dp.message(Command("nearest"))
async def cmd_nearest(message: Message):
    await message.answer(
        "⏱ <b>Какие ближайшие группы показать?</b>",
        parse_mode="HTML",
        reply_markup=get_nearest_keyboard(),
    )


@dp.message(Command("full"))
async def cmd_full(message: Message):
    await message.answer(
        "📋 <b>Выбери расписание:</b>",
        parse_mode="HTML",
        reply_markup=get_full_schedule_keyboard(),
    )


@dp.message(Command("slogan"))
async def cmd_slogan(message: Message):
    slogan = random.choice(SLOGANS_AND_AFFIRMATIONS)

    await message.answer(
        f"💫 <b>Установка на день:</b>\n\n<i>«{escape_html(slogan)}»</i>",
        parse_mode="HTML",
    )


@dp.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "📖 <b>Справка:</b>\n\n"
        "/today — группы на сегодня\n"
        "/nearest — ближайшие 5 групп\n"
        "/full — выбрать недельное расписание\n"
        "/metro [станция] — поиск по метро\n"
        "/slogan — установка на день\n"
        "/vda, /coda, /uaa, /anz — фильтры по типам на сегодня\n\n"
        "Короткие списки показываются без длинных адресов. "
        "Чтобы открыть адрес и пояснения, нажми кнопку с нужной группой под списком.\n\n"
        "Кнопка «⏱ Ближайшие» показывает до 5 ближайших групп: все, ВДА, CoDA, UAA или АНЗ.\n\n"
        "Кнопка «📋 Полное расписание» открывает второй уровень выбора: "
        "вся неделя, ВДА на неделю, CoDA на неделю, UAA на неделю или АНЗ на неделю.\n\n"
        "Ежедневная рассылка включается автоматически после /start.",
        parse_mode="HTML",
        reply_markup=get_menu_keyboard(),
    )


# ==================== ФИЛЬТРЫ ПО ТИПАМ НА СЕГОДНЯ ====================
@dp.message(Command("vda"))
async def cmd_vda_today(message: Message):
    day_index, day_name, _groups = ScheduleService.get_today()
    items = ScheduleService.get_items_for_day(day_index, kind="ВДА")
    await send_group_list_message(message, items, f"🟠 Группы ВДА сегодня ({day_name}):")


@dp.message(Command("coda"))
async def cmd_coda_today(message: Message):
    day_index, day_name, _groups = ScheduleService.get_today()
    items = ScheduleService.get_items_for_day(day_index, kind="CoDA")
    await send_group_list_message(message, items, f"🔵 Группы CoDA сегодня ({day_name}):")


@dp.message(Command("uaa"))
async def cmd_uaa_today(message: Message):
    day_index, day_name, _groups = ScheduleService.get_today()
    items = ScheduleService.get_items_for_day(day_index, kind="UAA")
    await send_group_list_message(message, items, f"🟢 Группы UAA сегодня ({day_name}):")


@dp.message(Command("anz"))
async def cmd_anz_today(message: Message):
    day_index, day_name, _groups = ScheduleService.get_today()
    items = ScheduleService.get_items_for_day(day_index, kind="АНЗ")
    await send_group_list_message(message, items, f"🟡 Группы АНЗ сегодня ({day_name}):")


# ==================== ПОИСК ПО МЕТРО ====================
@dp.message(Command("metro"))
async def cmd_metro(message: Message):
    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        await message.answer(
            "🚇 Выберите станцию метро из списка или введите /metro <название> вручную:",
            reply_markup=get_metro_inline_keyboard(),
        )
        return

    station = args[1]
    await process_metro_search(message, station)


async def process_metro_search(message: Message, station: str):
    items = ScheduleService.get_by_metro(station)

    if not items:
        await message.answer(
            f"🚇 По запросу «{escape_html(station)}» групп не найдено.",
            parse_mode="HTML",
        )
        return

    await send_group_list_message(
        message,
        items,
        f"🚇 Группы рядом со станцией метро «{station}»:",
        show_day=True,
    )


@dp.message(F.text == "🚇 Поиск по метро")
async def btn_metro_start(message: Message):
    await message.answer(
        "🚇 Выберите станцию метро из списка:",
        reply_markup=get_metro_inline_keyboard(),
    )


@dp.callback_query(F.data.startswith("metro_"))
async def inline_metro_callback(callback: CallbackQuery):
    await callback.answer()

    idx_str = callback.data[len("metro_"):]

    if not idx_str.isdigit():
        await callback.message.answer("⚠️ Ошибка: станция не найдена.")
        return

    idx = int(idx_str)

    if idx < len(metro_stations_cache):
        station = metro_stations_cache[idx]
        await process_metro_search(callback.message, station)
    else:
        await callback.message.answer("⚠️ Ошибка: станция не найдена.")


# ==================== КНОПКИ МЕНЮ ====================
@dp.message(F.text == "📅 Сегодня")
async def btn_today(message: Message):
    await cmd_today(message)


@dp.message(F.text == "⏱ Ближайшие")
async def btn_nearest(message: Message):
    await cmd_nearest(message)


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
    await message.answer("📆 Выбери день недели:", reply_markup=get_days_keyboard())


# ==================== CALLBACK: ВЫБОР ДНЯ ====================
@dp.callback_query(F.data.startswith("day_"))
async def process_day_callback(callback: CallbackQuery):
    await callback.answer()

    day_index_str = callback.data.split("_", 1)[1]

    if not day_index_str.isdigit():
        await callback.message.answer("⚠️ Ошибка: день недели не найден.")
        return

    day_index = int(day_index_str)
    day_name, _groups = ScheduleService.get_by_day(day_index)
    items = ScheduleService.get_items_for_day(day_index)

    await send_group_list_message(callback.message, items, f"📅 {day_name}:")


# ==================== CALLBACK: НЕДЕЛЬНОЕ РАСПИСАНИЕ ====================
@dp.callback_query(F.data == "week_all")
async def process_week_all_callback(callback: CallbackQuery):
    await callback.answer()

    items = ScheduleService.get_items_for_week()
    await send_group_list_message(
        callback.message,
        items,
        ScheduleService.get_week_title(),
        show_day=True,
    )


@dp.callback_query(F.data.startswith("week_type:"))
async def process_week_type_callback(callback: CallbackQuery):
    await callback.answer()

    kind = callback.data.split(":", 1)[1]

    if kind not in TYPE_TITLES:
        await callback.message.answer("⚠️ Ошибка: тип групп не найден.")
        return

    items = ScheduleService.get_items_for_week(kind=kind)
    await send_group_list_message(
        callback.message,
        items,
        ScheduleService.get_week_title(kind),
        show_day=True,
    )


# ==================== CALLBACK: БЛИЖАЙШИЕ ГРУППЫ ====================
@dp.callback_query(F.data == "nearest_all")
async def process_nearest_all_callback(callback: CallbackQuery):
    await callback.answer()
    await send_nearest_groups_message(callback.message, kind=None)


@dp.callback_query(F.data.startswith("nearest_type:"))
async def process_nearest_type_callback(callback: CallbackQuery):
    await callback.answer()

    kind = callback.data.split(":", 1)[1]

    if kind not in TYPE_TITLES:
        await callback.message.answer("⚠️ Ошибка: тип групп не найден.")
        return

    await send_nearest_groups_message(callback.message, kind=kind)


# ==================== CALLBACK: ПОДРОБНОСТИ ГРУППЫ ====================
@dp.callback_query(F.data.startswith("detail:"))
async def process_group_detail_callback(callback: CallbackQuery):
    await callback.answer()

    group_key = callback.data.split(":", 1)[1]
    result = get_group_by_key(group_key)

    if not result:
        await callback.message.answer("⚠️ Ошибка: группа не найдена.")
        return

    day_index, group_index, group = result
    text = format_group_details(day_index, group_index, group)

    await callback.message.answer(text, parse_mode="HTML")


# ==================== ЗАПУСК ====================
async def main():
    if not BOT_TOKEN:
        print("❌ Ошибка: BOT_TOKEN не задан в переменных окружения")
        return

    bot = Bot(token=BOT_TOKEN)

    print("✅ Бот запущен")
    print(f"✅ Ежедневная рассылка: {DAILY_NOTIFY_HOUR:02d}:{DAILY_NOTIFY_MINUTE:02d} МСК")

    asyncio.create_task(daily_notification_worker(bot))

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
