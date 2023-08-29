import telebot
import requests
from telebot import types


bot = telebot.TeleBot('6370758294:AAHJHs0gRGEDKE7EPGn_WzvM2sYdRjTxbLQ')
url = 'http://127.0.0.1:8000/'


@bot.message_handler(commands=['start'])
def start(message):
    text = f'Здравствуйте, {message.from_user.first_name.capitalize()} {message.from_user.last_name.capitalize()}!'\
    ' Напишите вопрос, который хотели бы задать'
    bot.send_message(message.chat.id, text)


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    # bot.send_message(message.chat.id, 'Это может занять какое-то время')
    response = requests.post(url=f'{url}get_data_gpt', json={'text': message.text})
    res = response.json()
    # bot.send_message(message.chat.id, f'{res["message"]}')
    for value in res.values():
        if value[0] == 'D':
            bot.send_animation(message.chat.id, animation=open(f'{value}', 'rb'))
        else:
            bot.send_message(message.chat.id, value)


bot.polling(none_stop=True)
