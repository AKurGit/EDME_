import os

import telebot
import requests
from dotenv import load_dotenv


load_dotenv()
# BRAIN_URL = os.environ['BRAIN_URL']
# BRAIN_PORT = os.environ['BRAIN_PORT']
TELEGRAM_BOT = os.getenv('TELEGRAM_BOT')
# url = f'http://{BRAIN_URL}:{BRAIN_PORT}/'
bot = telebot.TeleBot(TELEGRAM_BOT)
url = 'http://127.0.0.1:8000/'


@bot.message_handler(commands=['start'])
def start(message):
    text = f'Здравствуйте, {message.from_user.first_name.capitalize()} {message.from_user.last_name.capitalize()}!'\
            ' Напишите вопрос, который хотели бы задать'
    bot.send_message(message.chat.id, text)


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    response = requests.post(url=f'{url}get_data_gpt', json={'text': message.text})
    res = response.json()
    for value in res.values():
        bot.send_message(message.chat.id, value)


bot.polling(none_stop=True)
