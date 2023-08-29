import ast
import pickle

import chardet
import numpy as np
import pandas as pd
import pymorphy3
from fastapi import FastAPI
from gensim.models import Doc2Vec
import tensorflow as tf
from gensim.models.doc2vec import TaggedDocument

from con_gpt import ConnectionGPT
from greetings import is_greeting_or_farewell, get_greeting, get_farewell
from db import DynamoDBClient
import uvicorn
from const import Credit, ATM, Card, Deposit, ExchangeRate, \
    Insurance, MoneyTransferInfo, BankAccount

stop_words_list = ['а', 'бы', 'ведь', 'во', 'вот', 'впрочем', 'все', 'всегда', 'всего', 'всё', 'всю', 'вы', 'где', 'да',
                   'даже', 'два', 'для', 'до', 'другой', 'его', 'ее', 'ей',
                   'ему', 'если', 'есть', 'еще', 'ж', 'же', 'за', 'зачем', 'и', 'из', 'или', 'им', 'иногда',
                   'их', 'к', 'как', 'когда', 'конечно', 'ли', 'много', 'может', 'можно', 'мой', 'моя', 'мы', 'на',
                   'над', 'надо',
                   'наконец', 'нас', 'не', 'него', 'нее', 'ней', 'нельзя', 'нет', 'ни', 'нибудь', 'никогда', 'ним',
                   'них', 'ничего', 'но', 'ну', 'о', 'об', 'один', 'он', 'она', 'они', 'опять', 'от', 'перед', 'по',
                   'под', 'после', 'потом', 'потому', 'почти', 'при', 'про', 'раз', 'разве', 'с', 'сам', 'свою',
                   'себе', 'себя', 'со', 'совсем', 'так', 'такой', 'там',
                   'тебя', 'тем', 'теперь', 'то', 'тогда', 'того', 'тоже', 'только', 'том', 'тот', 'три', 'тут', 'ты',
                   'у', 'уж', 'уже', 'хоть', 'чего', 'чем', 'через', 'что', 'чтоб', 'чтобы', 'чуть',
                   'эти', 'этого', 'этой', 'этом', 'этот', 'эту', 'я', '?', ',', '!', ':', 'здравствуйте', 'добрый',
                   'день','утро', 'вечер', 'где', 'как', 'почему', 'привет', 'какой', 'можно', 'сколько', 'хотеть',
                   'узнать', 'мочь', 'уточнить', 'подсказать']


def normalize_text(text):
    text = text.replace(",", " ")
    text = text.replace("?", " ")
    text = text.replace("!", " ")
    text = text.replace(":", " ")
    text = text.replace(".", " ")
    text = text.replace(";", " ")
    text = text.replace("\t", " ")
    text = text.replace("(", " ")
    text = text.replace(")", " ")
    text = text.replace("%", " ")
    text = text.replace("$", " ")
    tokens = text.split()
    stop_words = set(stop_words_list)
    filtered_tokens = [word.lower() for word in tokens if word.lower() not in stop_words]
    morph = pymorphy3.MorphAnalyzer()
    lemmas = []
    for token in filtered_tokens:
        parsed = morph.parse(token)[0]
        lemma = parsed.normal_form
        lemmas.append(lemma)
    return lemmas


def read_dataframe_from_txt(path, columns=['tags', 'question']):
    with open(path, 'rb') as f:
        result = chardet.detect(f.read())
    encoding = result['encoding']
    if encoding is None:
        encoding = 'cp1251'
    with open(path, 'r', encoding=encoding, errors='ignore') as file:
        text = file.read()
    text = text.encode(encoding, errors='ignore').decode('utf8', errors='ignore')
    df = pd.DataFrame([x.split("|")[0:2] for x in text.split("\n")], columns=columns)
    return df


def get_tags(str):
    str_list = str.split(',')
    nump = np.zeros(12)
    for el in str_list:
        el = ast.literal_eval(el)
        nump[el] = 1
    nump = nump.reshape(12)
    return nump


def get_topics(question, vectorizer: Doc2Vec, classifier: tf.keras.models.Sequential):
    word_list = normalize_text(question)
    vector = vectorizer.infer_vector(word_list)
    tags = classifier.predict(np.array([vector]))
    topic = tags.argmax()
    return topic


def get_models(data_path_text):
    df = read_dataframe_from_txt(data_path_text)
    df = df.sample(frac=1, random_state=42)
    question_lemmas = df['question'].apply(lambda x: normalize_text(x)).tolist()
    documents = [TaggedDocument(q, [i]) for i, q in enumerate(question_lemmas)]

    vectorizer = Doc2Vec(vector_size=120, min_count=1, epochs=200)
    vectorizer.build_vocab(documents)
    vectorizer.train(documents, total_examples=vectorizer.corpus_count, epochs=vectorizer.epochs)

    vectors = np.array([np.array(vectorizer.docvecs[i]) for i, doc in enumerate(question_lemmas)])
    tags = []
    for i, row in enumerate(df['tags']):
        nump = get_tags(row)
        tags.append(nump)
    tags = np.array(tags)

    classifier = tf.keras.models.Sequential([
        tf.keras.layers.Dense(64, activation='linear'),
        tf.keras.layers.Dense(12, activation='softmax')
    ])
    classifier.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    classifier.fit(vectors, tags, epochs=120, batch_size=4)

    return vectorizer, classifier



app = FastAPI()
dc = DynamoDBClient()

atm_ = dc.get_data_from_table('atm')
atm = [ATM(**i) for i in atm_]

credit = dc.get_data_from_table('bank_credit')
credit = [Credit(**item) for item in credit]

cards = dc.get_data_from_table('bank_cards')
cards = [Card(**card) for card in cards]

deposits = dc.get_data_from_table('bank_deposit')
deposits = [Deposit(**item) for item in deposits]

ex_rate = dc.get_data_from_table('bank_exchange')
ex_rate = [ExchangeRate(**currency) for currency in ex_rate]

insurance = dc.get_data_from_table('bank_insurance')
insurance = [Insurance(**item) for item in insurance]

money_transfers = dc.get_data_from_table('money_transfers')
money_transfers = [MoneyTransferInfo(**item) for item in money_transfers]

bank_accounts = dc.get_data_from_table('bank_accounts')
bank_accounts = [BankAccount(**item) for item in bank_accounts]

object_of_gpt = ConnectionGPT(credit, atm, cards, deposits, ex_rate, insurance, money_transfers, bank_accounts)

vectorizer, classifier = get_models("data/questions.txt")


@app.post('/get_data_gpt')
def get_data_gpt(data: dict):
    user_message = data['text']
    res = is_greeting_or_farewell(user_message)
    print(res)
    if res:
        return {'message': get_greeting()}
    elif res is None:
        global object_of_gpt, vectorizer, classifier
        id_ = get_topics(user_message, vectorizer, classifier)
        print(f"topic: {id_}", type(id_))
        generated_text = object_of_gpt.get_bot_message(user_message=user_message, id_=id_)
        if len(generated_text) > 1500:
            return {'message': generated_text[:len(generated_text) // 2],
                    'message1': generated_text[len(generated_text) // 2:]}
        else:
            return {'message': generated_text}
    else:
        return {'message': get_farewell()}


if __name__ == '__main__':
    uvicorn.run(app='server:app', host='0.0.0.0', port=1276,  reload=True)
