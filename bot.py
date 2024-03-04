from main import get_rasp_day
import telebot
from telebot import types
token = '6834153158:AAHHK5f3Xn4XOQMy9jnjXSqizGIermGAhp0'
bot = telebot.TeleBot(token)


@bot.message_handler()
def start_message(message):
    print(message.text)
    if len(message.text.split()) == 2:
        bot.send_message(message.chat.id, get_rasp_day(message.text.split()[0], int(message.text.split()[1])))


bot.infinity_polling()
