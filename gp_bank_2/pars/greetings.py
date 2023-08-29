from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from random import choice
# from spellchecker import Spellchecker
#
#
# def fix_word(word):
#     spell = Spellchecker(language='ru')
#     return spell.correction(word)


greetings = [
    "Привет!",
    "Здравствуйте!",
    "Добрый день!",
    "Приветствую!",
    "Здорово!",
    "Приветствую Вас!",
    "Доброе утро!",
    "Всем привет!",
    "Доброго времени суток!",
    "Здравствуй, добрый человек!",
    "Приветик!",
    "Доброго дня!",
    "Здравствуйте, друзья!",
    "Добро пожаловать!",
    "Приветствую всех присутствующих!",
    "Здравствуйте, дорогие гости!",
    "Добро пожаловать в нашу команду!",
    "Приветствую тебя, путник!",
    "Добро пожаловать на нашу вечеринку!",
    "Приветствую всех с наступающим Новым годом!"
]

farewells = [
    "До свидания!",
    "Прощай!",
    "Всего доброго!",
    "Удачи!",
    "Пока!",
    "До скорого!",
    "До встречи!",
    "Покедова!",
    "Бывай!",
    "До завтра!",
    "Счастливо!",
    "Прощайте!",
    "До новых встреч!",
    "До свидания, друзья!",
    "Удачи вам во всем!",
    "До следующего раза!",
    "Всем пока!",
    "До скорой встречи!",
    "До встречи, мои хорошие!",
    "Счастливо оставаться!"
]


def get_greeting():
    greet = [
        "Привет!",
        "Здравствуйте!",
        "Добрый день!",
        "Приветствую!",
    ]
    return choice(greet)


def get_farewell():
    fare = [
        "До свидания!",
        "Прощай!",
        "Всего доброго!",
        "Удачи!",
        "Пока!",
        "До скорого!",
        "До встречи!",
    ]
    return choice(fare)


vectorizer = CountVectorizer().fit(greetings + farewells)
greetings_matrix = vectorizer.transform(greetings)
farewell_matrix = vectorizer.transform(farewells)


def is_greeting_or_farewell(message):
    if len(message.split()) > 4:
        return None
    message_vector = vectorizer.transform([message])
    greeting_similarity = cosine_similarity(message_vector, greetings_matrix)
    farewell_similarity = cosine_similarity(message_vector, farewell_matrix)

    if greeting_similarity.max() > 0.75:
        return 1
    elif farewell_similarity.max() > 0.75:
        return 0
    else:
        return None
