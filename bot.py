import asyncio
import logging
from aiogram import Bot, Dispatcher, types
import requests


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


logging.basicConfig(level=logging.INFO)
bot = Bot(token="6834153158:AAHHK5f3Xn4XOQMy9jnjXSqizGIermGAhp0")
dp = Dispatcher()


@dp.message()
async def cmd_start(message: types.Message):
    if len(message.text.split()) == 2:
        await bot.send_message(message.chat.id, get_rasp_day(message.text.split()[0], message.text.split()[1]))


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
