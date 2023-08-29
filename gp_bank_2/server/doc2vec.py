import ast
import pickle

import gensim
import tensorflow as tf
import chardet
import numpy as np
import pandas as pd
import pymorphy3
from gensim.models.doc2vec import Doc2Vec, TaggedDocument


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



data_path_text = "../../../gp_bank/gp_bank_2/topic_modeling/data/questions.txt"
df = read_dataframe_from_txt(data_path_text)
df = df.sample(frac=1, random_state=42)
question_lemmas = df['question'].apply(lambda x: normalize_text(x)).tolist()
documents = [TaggedDocument(q, [i]) for i, q in enumerate(question_lemmas)]

vectorizer = Doc2Vec(vector_size=120, min_count=1, epochs=200)
vectorizer.build_vocab(documents)
vectorizer.train(documents, total_examples=vectorizer.corpus_count, epochs=vectorizer.epochs)

with open('../../../gp_bank/gp_bank_2/topic_modeling/models/vectorizer_doc2vec.pkl', 'wb') as file:
    pickle.dump(vectorizer, file)

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

with open('../../../gp_bank/gp_bank_2/topic_modeling/models/classifier.pkl', 'wb') as file:
    pickle.dump(classifier, file)

test_path = "../../../gp_bank/gp_bank_2/topic_modeling/data/test_questions.txt"
test_data = read_dataframe_from_txt(test_path)
test_lemmas = test_data['question'].apply(lambda x: normalize_text(x)).tolist()
test_vectors = np.array([np.array(vectorizer.infer_vector(doc)) for doc in test_lemmas])
test_tags = []
for i, row in enumerate(test_data['tags']):
    nump = get_tags(row)
    test_tags.append(nump)
test_tags = list(map(lambda x: x.argmax(), test_tags))
test_preds = np.apply_along_axis(lambda x: x.argmax(), axis=1, arr=classifier.predict(test_vectors))
accuracy = 0
for tag, question, pred in zip(test_tags, test_data['question'], test_preds):
    print(f"{tag}/{pred}: {question}")
    if tag == pred:
        accuracy += 1
accuracy /= len(test_preds)
print(accuracy)



