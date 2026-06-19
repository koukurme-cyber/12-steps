import asyncio
import json
import os
import random
import re
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


def moscow_now():
    return datetime.utcnow() + timedelta(hours=3)


VIEW_CONTEXTS: Dict[str, Dict[str, Any]] = {}
VIEW_COUNTER = 0


# ==================== РАСПИСАНИЕ (время, название, тип, метро, адрес) ====================
SCHEDULE = {
    0: [  # Понедельник
        ('15:00', 'Выход', 'ВДА', 'м. Технологический институт', 'ул. Егорова, 11, цокольный этаж, вход с улицы, помещение «Хаски». Время: 15:00–16:00. +7 911 995-25-35, Евгения. t.me/+sQ0gunx02...'),
        ('18:30', 'ЮТА', 'UAA', '', 'адрес уточняйте на uaarus.ru'),
        ('18:45', 'Небо на Тореза', 'CoDA', 'м. Площадь Мужества', 'пр. Тореза, 32, Библиотека им. Д. С. Лихачёва. +7 911 952-70-73. https://t.me/nebo_coda'),
        ('18:45', 'Путь к себе', 'CoDA', 'м. Сенная/Садовая/Спасская', 'Б. Подъяческая, 34, РБОО «АЗАРИЯ». +7 911 928-67-10. Рабочее собрание — первый четверг месяца 20:05. День рождения группы — 9 августа 1999 года.'),
        ('19:00', 'Небо на Обводном', 'CoDA', 'м. Балтийская', 'наб. Обводного канала, 116, храм Воскресения Христова, здание воскресной школы — отдельное 3-этажное кирпичное здание на улице. +7 911 952-70-73. https://t.me/nebo_coda'),
        ('19:00', 'Подруги', 'ВДА', 'м. Владимирская/Достоевская', 'Щербаков пер., 12, ДЦ Владимирский. Женская группа. Время: 19:00–20:00. vk.com/spb_aca_girls, t.me/spb_aca_girls'),
        ('19:00', 'Феникс', 'ВДА', 'м. Василеостровская/Спортивная', '2-я линия В.О., 3, «Информационный кабинет», лестница вниз. +7 965 787-05-74. t.me/+MqZjzIhuK...'),
        ('20:15', 'Замысел', 'UAA', 'м. Сенная/Садовая/Спасская', 'ул. Ефимова, 6'),
        ('20:20', 'Невская', 'ВДА', 'м. Ломоносовская', 'пер. Челиева, 10Б, на территории Подворья Свято-Троицкого Александра Свирского мужского монастыря. +7 911 964-73-58. t.me/+dWXgfntIf...'),
    ],
    1: [  # Вторник
        ('16:00', 'Чёрная речка', 'ВДА', 'м. Чёрная речка', 'Сестрорецкая ул., 2. Вход с Сестрорецкой улицы через магазин «Рыбалка». Время: 16:00–17:00. Чат группы: t.me/+la-lJbgvZ...'),
        ('17:30', 'Лотос', 'ВДА', 'м. Ленинский проспект', 'Трамвайный пр., 12к2, 5 этаж, комната 33. +7 921 904-49-86. vk.com/club188163037'),
        ('18:45', 'Вместе', 'ВДА', 'м. Технологический институт', '1-я Красноармейская ул., 11, Собор Успения Пресвятой Девы Марии, цокольный этаж: через главный зал, направо вниз по лестнице, затем направо по коридору, по указателям. Время: 18:45–20:00. +7 921 633-43-32, Алёна. t.me/+3LbXeWKvr...'),
        ('18:45', 'Черта', 'ВДА', 'м. Площадь Ленина/Площадь Мужества/Новочеркасская', 'Пискарёвский пр., 25, вход между Fitness House и «Евразией», на лифте 4 этаж, помещение 5. t.me/+pktT8AlhN..., chat.whatsapp.com/IVIZxQ9HsG...'),
        ('19:00', 'Единство CoDA online', 'CoDA', '', 'Онлайн-группа в Telegram. Возможны спонтанные собрания — следите за анонсами в чате группы: https://t.me/edinstvoCoDA'),
        ('19:00', 'Небо на Обводном', 'CoDA', 'м. Балтийская', 'наб. Обводного канала, 116, храм Воскресения Христова, здание воскресной школы — отдельное 3-этажное кирпичное здание на улице. +7 911 952-70-73. https://t.me/nebo_coda'),
        ('19:00', 'Единство Невский проспект', 'UAA', 'м. Невский пр.', 'ул. Садовая, 11, 3 эт., зал 11, код #3239'),
        ('19:00', 'Петрополис', 'АНЗ', 'м. Чкаловская', 'ул. Колпинская, 27, Малый зал'),
        ('19:00', 'Взрослые девочки', 'ВДА', 'м. Василеостровская', '13-я линия В.О., 2, кв. 46, синяя дверь во дворе. Женская группа. +7 911 156-54-77, Наталья. vk.com/aca_girls_spb'),
        ('19:10', 'Путь к себе', 'CoDA', 'м. Сенная/Садовая/Спасская', 'Б. Подъяческая, 34, РБОО «АЗАРИЯ». +7 911 928-67-10. Рабочее собрание — первый четверг месяца 20:05. День рождения группы — 9 августа 1999 года.'),
        ('20:15', 'Замысел', 'UAA', 'м. Сенная/Садовая/Спасская', 'ул. Ефимова, 6'),
        ('20:20', 'Тепло (Азария)', 'ВДА', 'м. Садовая/Технологический институт', 'ул. Большая Подъяческая, 34, вход со двора'),
    ],
    2: [  # Среда
        ('17:00', '13 линия', 'ВДА', 'м. Василеостровская', '13-я линия В.О., 2, кв. 46, синяя дверь во дворе. vk.com/club117132895'),
        ('17:30', 'Участие на Юго-Западе', 'CoDA', 'м. Автово', 'ул. Маршала Захарова, 13, 3 подъезд, цокольный этаж. Домофон 222. +7 981 945-54-37. https://t.me/codaSPbsw'),
        ('18:00', 'Солнечная сторона', 'ВДА', 'м. Чернышевская', 'ул. Радищева, 30, пространство «Просвет», зал «Просвещение». Время: 18:00–19:00. t.me/+qFRjoIzA_...'),
        ('18:45', 'Небо на Тореза', 'CoDA', 'м. Площадь Мужества', 'пр. Тореза, 32, Библиотека им. Д. С. Лихачёва. +7 911 952-70-73. https://t.me/nebo_coda'),
        ('19:00', 'Здравствуй, Я!', 'ВДА', 'м. Балтийская/Фрунзенская', 'наб. Обводного канала, 116, ауд. 121, возле Варшавского вокзала. На территории Храма Воскресения Христова, в кирпичном домике, где туалеты, 1 этаж, прямо до конца коридора, направо. Время: 19:00–20:30. +7 906 246-56-93, Марина. t.me/+leT0VsACS..., vk.ru/club236966318'),
        ('19:00', 'Петроградка', 'ВДА', 'м. Петроградская', 'Большой пр. П. С., 77. Деревянная дверь выходит на остановку, код домофона 3, третий этаж, белая дверь напротив входа. +7 911 022-95-07. t.me/vdapetrogr...'),
        ('19:00', 'Прометей', 'ВДА', 'м. Московская/Проспект Славы', 'пр. Славы, 4, после арки направо, вывеска «Автошкола», 2 этаж, последняя дверь налево. Время: 19:00–20:00. +7 911 277-49-11, Анастасия. vk.ru/vda_prometei'),
        ('19:00', 'Феникс', 'ВДА', 'м. Василеостровская/Спортивная', '2-я линия В.О., 3, «Информационный кабинет», лестница вниз. +7 965 787-05-74. t.me/+MqZjzIhuK...'),
        ('19:10', 'Путь к себе', 'CoDA', 'м. Сенная/Садовая/Спасская', 'Б. Подъяческая, 34, РБОО «АЗАРИЯ». +7 911 928-67-10. Рабочее собрание — первый четверг месяца 20:05. День рождения группы — 9 августа 1999 года.'),
        ('19:15', 'Ручей', 'ВДА', 'м. Чкаловская', 'ул. Колпинская, 27, пространство выздоровления «Ручей». Рабочее собрание — последняя среда месяца 20:15–21:15'),
        ('20:15', 'Замысел', 'UAA', 'м. Сенная/Садовая/Спасская', 'ул. Ефимова, 6'),
        ('20:20', 'Небо на В.О.', 'CoDA', 'м. Василеостровская', 'наб. Лейтенанта Шмидта, 39, церковь святых Анастасии, Феодора, Давида и Константина. +7 911 952-70-73. https://t.me/nebo_coda'),
        ('20:20', 'Тепло (Азария)', 'ВДА', 'м. Садовая/Технологический институт', 'ул. Большая Подъяческая, 34, вход со двора'),
        ('21:30', 'Путь к себе online', 'CoDA', '', 'Онлайн-группа в Skype. Группа возобновила работу. Ссылка для подключения в исходных данных не указана.'),
    ],
    3: [  # Четверг
        ('10:00', 'Единство CoDA online', 'CoDA', '', 'Онлайн-группа в Telegram. Возможны спонтанные собрания — следите за анонсами в чате группы: https://t.me/edinstvoCoDA'),
        ('18:00', 'Свобода смысла', 'ВДА', 'м. Сенная/Садовая/Спасская', 'ул. Ефимова, 6. К арке, звонок справа от домофона, код 220222#, парадная напротив арки, домофон 57, 2 этаж. t.me/+b14S_QR3Q..., vk.ru/club237107598. Группа ориентирована на агностиков и атеистов'),
        ('18:45', 'Вместе', 'ВДА', 'м. Технологический институт', '1-я Красноармейская ул., 11, Собор Успения Пресвятой Девы Марии, цокольный этаж: через главный зал, направо вниз по лестнице, затем направо по коридору, по указателям. Время: 18:45–20:00. +7 921 633-43-32, Алёна. t.me/+3LbXeWKvr...'),
        ('18:45', 'Черта', 'ВДА', 'м. Площадь Ленина/Площадь Мужества/Новочеркасская', 'Пискарёвский пр., 25, вход между Fitness House и «Евразией», на лифте 4 этаж, помещение 5. t.me/+pktT8AlhN..., chat.whatsapp.com/IVIZxQ9HsG...'),
        ('19:00', 'PRO ЖИЗНЬ', 'CoDA', 'м. Сенная/Садовая/Спасская', 'ул. Казанская, 52, церковь «Краеугольный камень». +7 911 928-67-10. Контактное лицо: Юля, +7 904 642-98-03'),
        ('19:00', 'Небо на Обводном', 'CoDA', 'м. Балтийская', 'наб. Обводного канала, 116, храм Воскресения Христова, здание воскресной школы — отдельное 3-этажное кирпичное здание на улице. +7 911 952-70-73. https://t.me/nebo_coda'),
        ('19:00', 'Эфир', 'ВДА', 'м. Московская', 'ул. Варшавская, 122, каб. 10, цокольный этаж, домофон «6». Время: 19:00–20:00. +7 999 037-13-05, Наталья. t.me/+KPUbhUb_2...'),
        ('19:20', 'Небо на В.О.', 'CoDA', 'м. Василеостровская', 'наб. Лейтенанта Шмидта, 39, церковь святых Анастасии, Феодора, Давида и Константина. +7 911 952-70-73. https://t.me/nebo_coda'),
        ('20:15', 'Замысел', 'UAA', 'м. Сенная/Садовая/Спасская', 'ул. Ефимова, 6'),
    ],
    4: [  # Пятница
        ('18:10', 'Ручей', 'ВДА', 'м. Чкаловская', 'ул. Колпинская, 27, пространство выздоровления «Ручей»'),
        ('18:30', 'ЮТА', 'UAA', '', 'адрес уточняйте на uaarus.ru'),
        ('19:00', 'Небо на Обводном', 'CoDA', 'м. Балтийская', 'наб. Обводного канала, 116, храм Воскресения Христова, здание воскресной школы — отдельное 3-этажное кирпичное здание на улице. +7 911 952-70-73. https://t.me/nebo_coda'),
        ('19:00', 'Сознание Пушкин', 'CoDA', 'Пушкин', 'г. Пушкин, ул. Магазейная, 22/30, полуподвал. +7 911 711-80-81'),
        ('19:00', 'Солнечная', 'CoDA', 'м. Гостиный Двор/Невский Проспект', 'ул. Садовая, 7–9–11, пространство «Ступени», 3 этаж, офис 38, кабинет 7. День рождения группы — 4 июня 2007 года'),
        ('19:00', 'Любящий родитель', 'ВДА', 'м. Балтийская', 'Практика применения пособия «Любящий родитель». Наб. Обводного канала, 116, помещение «Лекционка» в храме, центральный вход. Напротив поста охраны налево, коричневая дверь, подняться наверх за хоры. Время: 19:00–20:30. Важно не опаздывать: в 19:30 храм закрывают под группу. Валерия, +7 952 236-77-44'),
        ('19:00', 'Петроградка', 'ВДА', 'м. Петроградская', 'Большой пр. П. С., 77. Деревянная дверь выходит на остановку, код домофона 3, третий этаж, белая дверь напротив входа. +7 911 022-95-07. t.me/vdapetrogr...'),
        ('19:00', 'Тепло (Азария)', 'ВДА', 'м. Садовая/Технологический институт', 'ул. Большая Подъяческая, 34, вход со двора'),
        ('19:00', 'Феникс', 'ВДА', 'м. Василеостровская/Спортивная', '2-я линия В.О., 3, «Информационный кабинет», лестница вниз. +7 965 787-05-74. t.me/+MqZjzIhuK...'),
        ('20:15', 'Замысел', 'UAA', 'м. Сенная/Садовая/Спасская', 'ул. Ефимова, 6'),
        ('20:20', 'Путь к себе', 'CoDA', 'м. Сенная/Садовая/Спасская', 'Б. Подъяческая, 34, РБОО «АЗАРИЯ». +7 911 928-67-10. Рабочее собрание — первый четверг месяца 20:05. День рождения группы — 9 августа 1999 года.'),
    ],
    5: [  # Суббота
        ('11:00', 'Взрослые девочки — интенсив 10 шага', 'ВДА', 'м. Василеостровская', '13-я линия В.О., 2, кв. 46, синяя дверь во дворе. Открытый интенсив для женщин по 10 шагу ВДА по БКК и ЖТ. Приглашаются все желающие, которые прошли 9 шагов'),
        ('13:00', 'Петрополис', 'АНЗ', 'м. Чкаловская', 'ул. Колпинская, 27, Малый зал'),
        ('13:00', '13 линия', 'ВДА', 'м. Василеостровская', '13-я линия В.О., 2, кв. 46, синяя дверь во дворе. vk.com/club117132895'),
        ('14:00', 'Небо online', 'CoDA', '', 'Онлайн-собрание группы «Небо». https://t.me/nebo_coda'),
        ('14:30', 'Участие на Юго-Западе', 'CoDA', 'м. Автово', 'ул. Маршала Захарова, 13, 3 подъезд, цокольный этаж. Домофон 222. +7 981 945-54-37. https://t.me/codaSPbsw'),
        ('16:00', 'Говори, доверяй, чувствуй', 'ВДА', 'м. Проспект Просвещения', 'пр. Энгельса, 132, подвальное помещение во внутреннем дворе у магазина «Бристоль». +7 905 274-55-50, Алёна'),
        ('16:00', 'Свобода смысла', 'ВДА', 'м. Сенная/Садовая/Спасская', 'ул. Ефимова, 6. К арке, звонок справа от домофона, код 220222#, парадная напротив арки, домофон 57, 2 этаж. t.me/+b14S_QR3Q..., vk.ru/club237107598. Группа ориентирована на агностиков и атеистов'),
        ('17:00', 'Парнас', 'ВДА', 'м. Парнас', '6-й Верхний пер., 12Б, 5 этаж, офис №2. Центральный вход, на лифте до 4 этажа, затем по лестнице до 5-го и налево по коридору. +7 921 434-05-66, Александра'),
        ('17:00', 'Петроградка', 'ВДА', 'м. Петроградская', 'Большой пр. П. С., 77. Деревянная дверь выходит на остановку, код домофона 3, третий этаж, белая дверь напротив входа. +7 911 022-95-07. t.me/vdapetrogr...'),
        ('18:30', 'ЮТА', 'UAA', '', 'адрес уточняйте на uaarus.ru'),
        ('19:00', 'Солнечная сторона', 'ВДА', 'м. Чернышевская', 'ул. Радищева, 30, пространство «Просвет», зал «Просвещение». Время: 19:00–20:00. t.me/+qFRjoIzA_...'),
        ('19:00', 'Феникс', 'ВДА', 'м. Василеостровская/Спортивная', '2-я линия В.О., 3, «Информационный кабинет», лестница вниз. +7 965 787-05-74. t.me/+MqZjzIhuK...'),
        ('20:15', 'Замысел', 'UAA', 'м. Сенная/Садовая/Спасская', 'ул. Ефимова, 6'),
    ],
    6: [  # Воскресенье
        ('11:00', 'Взрослые девочки', 'ВДА', 'м. Василеостровская', '13-я линия В.О., 2, кв. 46, синяя дверь во дворе. Женская группа. +7 911 156-54-77, Наталья. vk.com/aca_girls_spb'),
        ('12:00', 'Мост', 'CoDA', 'Красное Село', 'Красное Село, ул. Массальского, 3. Алла, +7 952 236-39-81'),
        ('13:00', 'Черта', 'ВДА', 'м. Площадь Ленина/Площадь Мужества/Новочеркасская', 'Пискарёвский пр., 25, вход между Fitness House и «Евразией», на лифте 4 этаж, помещение 5. t.me/+pktT8AlhN..., chat.whatsapp.com/IVIZxQ9HsG...'),
        ('14:30', 'Любящий родитель (практика)', 'ВДА', 'м. Площадь Ленина/Площадь Мужества/Новочеркасская', 'Практика по восстановлению связи с Любящим родителем проходит каждое воскресенье 14:30–15:00 в рамках группы «Черта». Пискарёвский пр., 25'),
        ('15:00', 'Воскресенье', 'ВДА', 'м. Автово', 'ул. Маршала Захарова, 13, подъезд 3, цокольный этаж. Домофон 222. Время: 15:00–16:30. +7 918 351-04-44, Елена. t.me/voskresenj...'),
        ('15:10', 'Феникс', 'ВДА', 'м. Василеостровская/Спортивная', '2-я линия В.О., 3, «Информационный кабинет», лестница вниз. +7 965 787-05-74. t.me/+MqZjzIhuK...'),
        ('16:30', 'Все свободны', 'ВДА', 'м. Чернышевская', 'ул. Таврическая, 5, как пройти — в закрепах чата. t.me/vsefree_vda. Встречи открыты для всех членов 12-шаговых сообществ с правом высказывания'),
        ('17:00', 'Небо на В.О.', 'CoDA', 'м. Василеостровская', 'наб. Лейтенанта Шмидта, 39, церковь святых Анастасии, Феодора, Давида и Константина. +7 911 952-70-73. https://t.me/nebo_coda'),
        ('17:00', 'проСВЕТ', 'ВДА', 'м. Проспект Просвещения', 'Выборгское ш., 15, вход через ТЦ «Авеню» со стороны Выборгского шоссе во внутренний двор, 3 этаж на лифте или по лестнице, по диагонали через двор налево первая дверь, первая комната налево. Перед приходом уточнить проведение собрания. Екатерина +7 999 202-91-71, Александр +7 964 388-52-23'),
        ('18:00', 'Прометей', 'ВДА', 'м. Московская/Проспект Славы', 'пр. Славы, 4, после арки направо, вывеска «Автошкола», 2 этаж, последняя дверь налево. Время: 18:00–19:30. +7 911 277-49-11, Анастасия. vk.ru/vda_prometei'),
        ('18:30', 'Путь к себе', 'CoDA', 'м. Сенная/Садовая/Спасская', 'Б. Подъяческая, 34, РБОО «АЗАРИЯ». +7 911 928-67-10. Рабочее собрание — первый четверг месяца 20:05. День рождения группы — 9 августа 1999 года.'),
        ('19:00', 'Единство Невский проспект', 'UAA', 'м. Невский пр.', 'ул. Садовая, 11, 3 эт., зал 11, код #3239'),
        ('19:30', 'PRO ЖИЗНЬ', 'CoDA', 'м. Сенная/Садовая/Спасская', 'ул. Казанская, 52, церковь «Краеугольный камень». +7 911 928-67-10. Контактное лицо: Юля, +7 904 642-98-03'),
        ('20:15', 'Замысел', 'UAA', 'м. Сенная/Садовая/Спасская', 'ул. Ефимова, 6'),
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
    "ВДА": "",
    "CoDA": "",
    "UAA": "",
    "АНЗ": "",
}

TYPE_TITLES = {
    "ВДА": "ВДА",
    "CoDA": "CoDA",
    "UAA": "UAA",
    "АНЗ": "АНЗ",
}


def type_prefix(kind: str) -> str:
    prefix = TYPE_EMOJI.get(kind, "")
    return f"{prefix} " if prefix else ""


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


def create_view_context(
    items: List[Dict[str, Any]],
    title: str,
    show_day: bool = False,
) -> str:
    global VIEW_COUNTER

    VIEW_COUNTER += 1
    view_id = str(VIEW_COUNTER)

    VIEW_CONTEXTS[view_id] = {
        "items": items,
        "title": title,
        "show_day": show_day,
        "created_at": datetime.utcnow().isoformat(),
    }

    # Простая защита от бесконечного роста памяти.
    if len(VIEW_CONTEXTS) > 200:
        oldest_keys = list(VIEW_CONTEXTS.keys())[:100]
        for key in oldest_keys:
            VIEW_CONTEXTS.pop(key, None)

    return view_id


def get_view_context(view_id: str) -> Optional[Dict[str, Any]]:
    return VIEW_CONTEXTS.get(view_id)


def get_group_by_key(group_key: str) -> Optional[Tuple[int, int, Tuple]]:
    parsed = parse_group_key(group_key)

    if not parsed:
        return None

    day_index, group_index = parsed
    return day_index, group_index, SCHEDULE[day_index][group_index]



def clean_schedule_address(metro: str, address: str) -> str:
    """Оставляет для вывода только адресную часть без времени, тем, контактов и примечаний."""
    metro = str(metro or "").strip()
    address = str(address or "").strip()

    if metro and address:
        text = f"{metro}. {address}"
    else:
        text = address or metro

    text = re.sub(r"\s+", " ", text).strip()

    # Время, контакты, ссылки и служебные пояснения не выводим в списке расписания.
    stop_patterns = [
        r"\bВремя\s*:",
        r"\bТелефон\b",
        r"\bКонтакты?\b",
        r"\bКонт\.\s*номер\b",
        r"\+\s*7\b",
        r"\b8\s*\(?\d{3}\)?",
        r"https?://",
        r"\bt\.me/",
        r"\bvk\.(?:com|ru)/",
        r"chat\.whatsapp\.com/",
        r"\bРабочее собрание\b",
        r"\bДень рождения\b",
        r"\bЖенская группа\b",
        r"\bОткрытый интенсив\b",
        r"\bПриглашаются\b",
        r"\bВажно\b",
        r"\bПеред приходом\b",
        r"\bВстречи открыты\b",
        r"\bГруппа ориентирована\b",
        r"\bкак пройти\b",
        r"\bВозможны спонтанные собрания\b",
        r"\bСсылка для подключения\b",
    ]

    cut_positions = []
    for pattern in stop_patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            cut_positions.append(match.start())

    if cut_positions:
        text = text[:min(cut_positions)]

    text = re.sub(r"\s+", " ", text).strip(" .;,—-")
    return text or "адрес уточняется"


def format_schedule_item(day_index: int, group: Tuple, show_day: bool = False) -> str:
    time_str, name, kind, metro, address = group
    day_part = f"{DAYS[day_index]}, " if show_day else ""
    clean_address = clean_schedule_address(metro, address)
    return (
        f"• <b>{escape_html(day_part + time_str)}</b> — "
        f"{escape_html(name)} [{escape_html(kind)}]\n"
        f"  {escape_html(clean_address)}"
    )


def format_group_short(day_index: int, group_index: int, group: Tuple, show_day: bool = False) -> str:
    return format_schedule_item(day_index, group, show_day=show_day)


def format_schedule_list(items: List[Dict[str, Any]], title: str, show_day: bool = False) -> str:
    if not items:
        return f"<b>{escape_html(title)}</b>\n\n<i>Групп не найдено.</i>"

    lines = [f"<b>{escape_html(title)}</b>"]
    for item in sorted(items, key=lambda x: (x["day_index"], x["group"][0], x["group"][1])):
        lines.append(format_schedule_item(item["day_index"], item["group"], show_day=show_day))
    return "\n\n".join(lines)


def format_week_schedule(items: List[Dict[str, Any]], title: str) -> str:
    if not items:
        return f"<b>{escape_html(title)}</b>\n\n<i>Групп не найдено.</i>"

    by_day: Dict[int, List[Dict[str, Any]]] = {}

    for item in items:
        day_index = item["day_index"]
        by_day.setdefault(day_index, []).append(item)

    parts = [f"<b>{escape_html(title)}</b>"]

    for day_index in range(7):
        day_items = by_day.get(day_index, [])

        if not day_items:
            continue

        parts.append(f"\n<b>{escape_html(DAYS[day_index])}</b>")

        for item in sorted(day_items, key=lambda x: (x["group"][0], x["group"][1])):
            parts.append(format_schedule_item(day_index, item["group"]))

    return "\n".join(parts)


async def send_week_schedule_message(message: Message, items: List[Dict[str, Any]], title: str):
    await send_long_message(message, format_week_schedule(items, title))


def format_group_details(day_index: int, group_index: int, group: Tuple) -> str:
    return format_schedule_item(day_index, group)


def format_group_for_daily(time: str, name: str, kind: str, metro: str, address: str) -> str:
    clean_address = clean_schedule_address(metro, address)
    return (
        f"• <b>{escape_html(time)}</b> — {escape_html(name)} [{escape_html(kind)}]\n"
        f"  {escape_html(clean_address)}"
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


def build_group_choice_keyboard(
    items: List[Dict[str, Any]],
    view_id: str,
    show_day: bool = False,
) -> InlineKeyboardMarkup:
    rows = []

    for item in items:
        day_index = item["day_index"]
        group_index = item["group_index"]
        group = item["group"]
        time_str, name, kind, metro, _address = group
        if show_day:
            prefix = f"{DAYS[day_index][:2]}, {time_str}"
        else:
            prefix = time_str

        metro_part = f" · {metro.replace('м. ', '')}" if metro else ""
        button_text = f"{prefix} · {name} [{kind}]{metro_part}"

        if len(button_text) > 64:
            button_text = button_text[:61] + "..."

        rows.append(
            [
                InlineKeyboardButton(
                    text=button_text,
                    callback_data=f"detail:{view_id}:{get_group_key(day_index, group_index)}",
                )
            ]
        )

    return InlineKeyboardMarkup(inline_keyboard=rows)


def build_back_to_list_keyboard(view_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="← Назад к списку",
                    callback_data=f"back:{view_id}",
                )
            ]
        ]
    )


async def send_long_message(message: Message, text: str, parse_mode: str = "HTML"):
    for part in split_long_message(text):
        await message.answer(part, parse_mode=parse_mode)


async def send_long_message_to_chat(bot: Bot, chat_id: int, text: str, parse_mode: str = "HTML"):
    for part in split_long_message(text):
        await bot.send_message(chat_id, part, parse_mode=parse_mode)
        await asyncio.sleep(0.05)


def render_group_list_text(title: str) -> str:
    return f"<b>{escape_html(title)}</b>"


async def send_group_list_message(
    message: Message,
    items: List[Dict[str, Any]],
    title: str,
    show_day: bool = False,
):
    await send_long_message(
        message,
        format_schedule_list(items, title, show_day=show_day),
        parse_mode="HTML",
    )


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
    def get_week_title(kind: Optional[str] = None):
        if kind:
            return f"{TYPE_TITLES.get(kind, kind)} на неделю"
        return "Полное расписание на неделю"


def build_daily_live_groups_message() -> str:
    day_index, day_name, groups = ScheduleService.get_today()

    if not groups:
        return f"Привет, живые группы сегодня ({escape_html(day_name)}) не найдены."

    lines = [f"Привет, живые группы сегодня ({escape_html(day_name)}):\n"]

    for group in sorted(groups, key=lambda x: x[0]):
        lines.append(format_group_for_daily(*group))

    return "\n\n".join(lines)


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
    builder.row(KeyboardButton(text="Сегодня"), KeyboardButton(text="Выбрать день"))
    builder.row(KeyboardButton(text="Полное расписание"))
    builder.row(KeyboardButton(text="ВДА сегодня"), KeyboardButton(text="CoDA сегодня"))
    builder.row(KeyboardButton(text="UAA сегодня"), KeyboardButton(text="АНЗ сегодня"))
    builder.row(KeyboardButton(text="Установка на день"))
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
                InlineKeyboardButton(text="Вся неделя", callback_data="week_all"),
            ],
            [
                InlineKeyboardButton(text="ВДА на неделю", callback_data="week_type:ВДА"),
                InlineKeyboardButton(text="CoDA на неделю", callback_data="week_type:CoDA"),
            ],
            [
                InlineKeyboardButton(text="UAA на неделю", callback_data="week_type:UAA"),
                InlineKeyboardButton(text="АНЗ на неделю", callback_data="week_type:АНЗ"),
            ],
        ]
    )


# ==================== ДИСПЕТЧЕР ====================
dp = Dispatcher()


@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "🕊 <b>Бот расписания живых групп</b>\n\n"
        "Здесь есть расписание групп ВДА, CoDA, UAA и АНЗ в Санкт-Петербурге.\n\n"
        "<i>«Жизнь больше, чем просто выживание»</i>\n\n"
        "Выбери действие на клавиатуре:",
        parse_mode="HTML",
        reply_markup=get_menu_keyboard(),
    )


@dp.message(Command("today"))
async def cmd_today(message: Message):
    day_index, day_name, _groups = ScheduleService.get_today()
    items = ScheduleService.get_items_for_day(day_index)
    await send_group_list_message(message, items, f"Группы на сегодня ({day_name}):")



@dp.message(Command("full"))
async def cmd_full(message: Message):
    await message.answer(
        "<b>Выбери расписание:</b>",
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
        "<b>Справка</b>\n\n"
        "Используй кнопки меню: сегодня, выбор дня, полное расписание, "
        "фильтры по сообществам и установка на день.\n\n"
        "Короткие списки показываются без длинных адресов. "
        "Чтобы открыть адрес и пояснения, нажми кнопку с нужной группой под списком.",
        parse_mode="HTML",
        reply_markup=get_menu_keyboard(),
    )


# ==================== ФИЛЬТРЫ ПО ТИПАМ НА СЕГОДНЯ ====================
@dp.message(Command("vda"))
async def cmd_vda_today(message: Message):
    day_index, day_name, _groups = ScheduleService.get_today()
    items = ScheduleService.get_items_for_day(day_index, kind="ВДА")
    await send_group_list_message(message, items, f"Группы ВДА сегодня ({day_name}):")


@dp.message(Command("coda"))
async def cmd_coda_today(message: Message):
    day_index, day_name, _groups = ScheduleService.get_today()
    items = ScheduleService.get_items_for_day(day_index, kind="CoDA")
    await send_group_list_message(message, items, f"Группы CoDA сегодня ({day_name}):")


@dp.message(Command("uaa"))
async def cmd_uaa_today(message: Message):
    day_index, day_name, _groups = ScheduleService.get_today()
    items = ScheduleService.get_items_for_day(day_index, kind="UAA")
    await send_group_list_message(message, items, f"Группы UAA сегодня ({day_name}):")


@dp.message(Command("anz"))
async def cmd_anz_today(message: Message):
    day_index, day_name, _groups = ScheduleService.get_today()
    items = ScheduleService.get_items_for_day(day_index, kind="АНЗ")
    await send_group_list_message(message, items, f"Группы АНЗ сегодня ({day_name}):")


# ==================== КНОПКИ МЕНЮ ====================
@dp.message(F.text == "Сегодня")
async def btn_today(message: Message):
    await cmd_today(message)



@dp.message(F.text == "Полное расписание")
async def btn_full(message: Message):
    await cmd_full(message)


@dp.message(F.text == "ВДА сегодня")
async def btn_vda(message: Message):
    await cmd_vda_today(message)


@dp.message(F.text == "CoDA сегодня")
async def btn_coda(message: Message):
    await cmd_coda_today(message)


@dp.message(F.text == "UAA сегодня")
async def btn_uaa(message: Message):
    await cmd_uaa_today(message)


@dp.message(F.text == "АНЗ сегодня")
async def btn_anz(message: Message):
    await cmd_anz_today(message)


@dp.message(F.text == "Установка на день")
async def btn_slogan(message: Message):
    await cmd_slogan(message)


@dp.message(F.text == "Выбрать день")
async def btn_choose_day(message: Message):
    await message.answer("Выбери день недели:", reply_markup=get_days_keyboard())


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

    await send_group_list_message(callback.message, items, f"{day_name}:")


# ==================== CALLBACK: НЕДЕЛЬНОЕ РАСПИСАНИЕ ====================
@dp.callback_query(F.data == "week_all")
async def process_week_all_callback(callback: CallbackQuery):
    await callback.answer()

    items = ScheduleService.get_items_for_week()
    await send_week_schedule_message(
        callback.message,
        items,
        ScheduleService.get_week_title(),
    )


@dp.callback_query(F.data.startswith("week_type:"))
async def process_week_type_callback(callback: CallbackQuery):
    await callback.answer()

    kind = callback.data.split(":", 1)[1]

    if kind not in TYPE_TITLES:
        await callback.message.answer("⚠️ Ошибка: тип групп не найден.")
        return

    items = ScheduleService.get_items_for_week(kind=kind)
    await send_week_schedule_message(
        callback.message,
        items,
        ScheduleService.get_week_title(kind),
    )


# ==================== CALLBACK: ПОДРОБНОСТИ ГРУППЫ ====================
@dp.callback_query(F.data.startswith("detail:"))
async def process_group_detail_callback(callback: CallbackQuery):
    await callback.answer()

    parts = callback.data.split(":", 3)

    if len(parts) != 4:
        await callback.message.answer("⚠️ Ошибка: группа не найдена.")
        return

    _prefix, view_id, day_index_str, group_index_str = parts
    group_key = f"{day_index_str}:{group_index_str}"
    result = get_group_by_key(group_key)

    if not result:
        await callback.message.answer("⚠️ Ошибка: группа не найдена.")
        return

    day_index, group_index, group = result
    text = format_group_details(day_index, group_index, group)

    try:
        await callback.message.edit_text(
            text,
            parse_mode="HTML",
            reply_markup=build_back_to_list_keyboard(view_id),
        )
    except Exception:
        await callback.message.answer(
            text,
            parse_mode="HTML",
            reply_markup=build_back_to_list_keyboard(view_id),
        )


@dp.callback_query(F.data.startswith("back:"))
async def process_back_to_list_callback(callback: CallbackQuery):
    await callback.answer()

    view_id = callback.data.split(":", 1)[1]
    context = get_view_context(view_id)

    if not context:
        await callback.message.answer("⚠️ Список устарел. Открой его заново.")
        return

    items = context["items"]
    title = context["title"]
    show_day = context["show_day"]
    try:
        await callback.message.edit_text(
            render_group_list_text(title),
            parse_mode="HTML",
            reply_markup=build_group_choice_keyboard(
                items,
                view_id=view_id,
                show_day=show_day,
            ),
        )
    except Exception:
        await callback.message.answer(
            render_group_list_text(title),
            parse_mode="HTML",
            reply_markup=build_group_choice_keyboard(
                items,
                view_id=view_id,
                show_day=show_day,
            ),
        )


# ==================== ЗАПУСК ====================
async def main():
    if not BOT_TOKEN:
        print("❌ Ошибка: BOT_TOKEN не задан в переменных окружения")
        return

    bot = Bot(token=BOT_TOKEN)

    print("✅ Бот запущен")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
