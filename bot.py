from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

import asyncio
import json

from rasp import get_rasp_week, get_group_id

TOKEN = "YOUR_TOKEN"
bot = Bot(token=TOKEN)
dp = Dispatcher()

USERS_FILE = "users.json"

def load_users():
    #Загрузка пользователей из файла
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_users(users):
    #Сохранение пользователей в файл
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=4)

users = load_users()

async def send_main_menu(message: types.Message):
    #Отправляет главное меню
    kb = [
        [KeyboardButton(text="Получить расписание")],
        [KeyboardButton(text="Изменить группу")],
    ]
    markup = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.answer("📋 Главное меню", reply_markup=markup)

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    user_id = str(message.from_user.id)
    if user_id in users:
        await message.answer(f"✅ Ваша группа: {users[user_id]}")
        await send_main_menu(message)
    else:
        await message.answer("Введите назвение вашей группы:")

@dp.message(lambda message: message.text == "Изменить группу")
async def change_group(message: types.Message):
    await message.answer("Введите новый номер группы:")

@dp.message(lambda message: message.text.isdigit())
async def set_group(message: types.Message):
    user_id = str(message.from_user.id)
    group_id = get_group_id(message.text)

    if group_id:
        users[user_id] = message.text
        save_users(users)
        await message.answer(f"✅ Группа {message.text} сохранена!")
        await send_main_menu(message)
    else:
        await message.answer("❌ Группа не найдена, попробуйте снова.")

@dp.message(lambda message: message.text == "Получить расписание")
async def send_schedule(message: types.Message):
    user_id = str(message.from_user.id)
    if user_id not in users:
        await message.answer("⚠️ Сначала выберите группу!")
        return

    group_name = users[user_id]
    schedule = get_rasp_week(group_name)

    if not schedule:
        await message.answer("❌ Расписание не найдено.")
        return

    for day, data in schedule.items():
        text = f"📅 {day} ({data['date']}):\n" + "\n".join(data["lessons"])
        await message.answer(text)

#Запуск бота
async def main():
    print("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
