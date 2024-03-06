import asyncio
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart


def get_group_id(name):
    url_id = 'https://xn--h1amj9b.xn--80aaiac8g.xn--p1ai/api/raspGrouplist?year=2023-2024'
    resp = requests.get(url_id).json()['data']
    for i in resp:
        if i['name'] == str(name):
            return i['id']
    return 'Not found'


def get_rasp_day(group_name, day):
    if get_group_id(group_name) != 'Not found':
        url = f'https://xn--h1amj9b.xn--80aaiac8g.xn--p1ai/api/Rasp?idGroup={get_group_id(group_name)}&sdate=2024-03-04'
    else:
        return 'Группа не найдена'
    resp = requests.get(url).json()
    text = ''
    for i in resp['data']['rasp']:
        if i['деньНедели'] == int(day):
            text += i['дисциплина'] + '\n'
    if text:
        return text
    return 'Расписание не найдено'


TOKEN = '6834153158:AAHHK5f3Xn4XOQMy9jnjXSqizGIermGAhp0'

bot = Bot(TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def start(message: types.Message):
    await message.answer('Введите номер группы и номер дня недели(1-5) через пробел.' + '\n' + 'Пример: 417 1')


@dp.message()
async def rasp(message: types.Message):
    await message.answer(get_rasp_day(message.text.split()[0], message.text.split()[1]))


async def main():
    await dp.start_polling(bot)


asyncio.run(main())
