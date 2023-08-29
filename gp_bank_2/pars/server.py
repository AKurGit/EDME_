import pickle

from fastapi import FastAPI
from con_gpt import ConnectionGPT
from greetings import is_greeting_or_farewell, get_greeting, get_farewell
from doc2vec import get_topics
from db import DynamoDBClient


app = FastAPI()
dc = DynamoDBClient()
atm_ = dc.get_data_from_table('atm')
atm = []
for i in atm_:
    atm.append(i['name'])
credits = dc.get_data_from_table('bank_credit')
credits = {i['credit_name']: (i['credit_info']['link'], i['credit_info']['terms']) for i in credits}
cards = dc.get_data_from_table('bank_cards')
cards = {i['card_name']: ('', i['card_info']) for i in cards}
deposits = dc.get_data_from_table('bank_deposit')
deposits = {i['deposit_name']: (i['deposit_info']['link'], i['deposit_info']['deposit_terms']) for i in deposits}
ex_rate = dc.get_data_from_table('bank_exchange')
ex_rate = [((f'{i["currency_name"]}_sell', i["sell"]), ((f'{i["currency_name"]}_buy', i["buy"]))) for i in ex_rate]
ex_rate = [i[0] + i[1] for i in ex_rate]
ex_rate = dict({i[0]: i[1] for i in ex_rate}, **{i[2]: i[3] for i in ex_rate})
insurance = dc.get_data_from_table('bank_insurance')
insurance = {i['insurance_name']: (i['insurance_info']['link'], i['insurance_info']['terms']) for i in insurance}
money_transfers = dc.get_data_from_table('money_transfers')
money_transfers = [tuple(i.values()) for i in money_transfers]
bank_accounts = dc.get_data_from_table('bank_accounts')
bank_accounts = {i['name']: (i['info']['link'], i['info']['terms']) for i in bank_accounts}
b = ConnectionGPT(credits, atm, cards, deposits, ex_rate, insurance, money_transfers, bank_accounts)
with open('2.pkl', 'rb') as file:
    vectorizer = pickle.load(file)
with open('1.pkl', 'rb') as file:
    classifier = pickle.load(file)


@app.post('/get_data_gpt')
def get_data_gpt(data: dict):

    user_message = data['text']
    res = is_greeting_or_farewell(user_message)
    print(res)
    if res:
        # return {'message': get_greeting()}
        return {'message': get_greeting(), 'path_to_gif': r'D:\gifs\hi.gif'}
    elif res is None:
        global b, vectorizer, classifier
        id_ = get_topics(user_message, vectorizer, classifier)
        print(f"topic: {id_}", type(id_))
        # return {'message': f'вот твое id: {id_}'}
        generated_text = b.get_bot_message(user_message=user_message, id_=id_)
        if len(generated_text) > 1500:
            return {'message': generated_text[:len(generated_text) // 2],
                    'message1': generated_text[len(generated_text) // 2:]}
        else:
            return {'message': generated_text}
    else:
        # return {'message': get_farewell()}
        return {'message': get_farewell(), 'path_to_gif': r'D:\gifs\hola-adios.gif'}
