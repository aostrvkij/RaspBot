import asyncio
import json
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardRemove
from rasp import get_week_schedule, get_group_id

API_TOKEN = "YOUR_API_TOKEN"  # Замените на ваш токен

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Загрузка пользователей
def load_users():
    try:
        with open("users.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

# Сохранение пользователей
def save_users(data):
    with open("users.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

users = load_users()

# Клавиатура
main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📅 Получить расписание")],
        [KeyboardButton(text="🔁 Изменить группу")]
    ],
    resize_keyboard=True
)

# Словарь дней недели
WEEKDAYS = {
    1: "Понедельник",
    2: "Вторник",
    3: "Среда",
    4: "Четверг",
    5: "Пятница",
    6: "Суббота",
    7: "Воскресенье"
}

# Форматирование расписания
def format_day_schedule(day, lessons):
    date = lessons[0]['дата']
    text = f"📅 {WEEKDAYS[day]} — {date}\n\n"  # ← пустая строка

    for lesson in lessons:
        start = lesson['начало']
        end = lesson['конец']
        room = lesson['аудитория']
        subject = lesson['дисциплина']
        teacher = lesson['преподаватель']
        text += f"🕒 {start}–{end} (ауд: {room})\n📚 {subject}\n👤 {teacher}\n\n"
    return text.strip()

# Обработка /start
@dp.message(CommandStart())
async def cmd_start(message: Message):
    user_id = str(message.from_user.id)

    if user_id not in users:
        await message.answer("Привет! Введи название своей группы:")
    else:
        await message.answer("Добро пожаловать обратно!", reply_markup=main_kb)

# Обработка ввода номера группы
@dp.message(F.text.regexp(r"^[\w\-]+$"))
async def group_input(message: Message):
    user_id = str(message.from_user.id)
    group_name = message.text.strip()

    if not get_group_id(group_name):
        await message.answer("❌ Группа не найдена. Попробуй ещё раз.")
        return

    users[user_id] = group_name
    save_users(users)

    await message.answer(f"✅ Группа сохранена: {group_name}", reply_markup=main_kb)

# Кнопка изменить группу
@dp.message(F.text == "🔁 Изменить группу")
async def change_group(message: Message):
    await message.answer("Введи новое название группы:", reply_markup=ReplyKeyboardRemove())

# Получить расписание
@dp.message(F.text == "📅 Получить расписание")
async def get_schedule(message: Message):
    user_id = str(message.from_user.id)

    if user_id not in users:
        await message.answer("Сначала введи название своей группы.")
        return

    group = users[user_id]
    data = get_week_schedule(group)

    if data is None:
        await message.answer("⚠️ Проблемы с сервером. Попробуйте позже.")
        return

    # Оставляем только дни, где есть пары
    non_empty_days = {day: lessons for day, lessons in data.items() if lessons}

    if not non_empty_days:
        await message.answer("⛔ Расписание на эту неделю не найдено.")
        return

    await message.answer("Вот расписание на ближайшую учебную неделю 📚:")

    for day, lessons in non_empty_days.items():
        msg = format_day_schedule(day, lessons)
        await message.answer(msg)

# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
