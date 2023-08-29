import os

import openai
from typing import List
from dotenv import load_dotenv
from const import Credit, ATM, Card, Deposit, \
    ExchangeRate, Insurance, MoneyTransferInfo, BankAccount


load_dotenv()


class ConnectionGPT:

    openai.api_key = os.getenv('OPENAI')

    def __init__(self,
                 credit: List[Credit],
                 atm_machine: List[ATM],
                 cards: List[Card],
                 deposits: List[Deposit],
                 ex_rate: List[ExchangeRate],
                 insurance: List[Insurance],
                 money_transfers: List[MoneyTransferInfo],
                 bank_account: List[BankAccount],
                 ):

        self.dict_of_prompts = {
            1: credit,
            2: atm_machine,
            3: cards,
            4: deposits,
            6: ex_rate,
            5: insurance,
            7: money_transfers,
            8: bank_account,
        }

    def get_bot_message(self, id_: int, user_message: str) -> str:
        if id_ == 1:
            return ConnectionGPT.to_credit(self.dict_of_prompts[id_], user_message)
        if id_ == 2:
            return ConnectionGPT.atm_machine(self.dict_of_prompts[id_], user_message)
        if id_ == 3:
            return ConnectionGPT.cards(self.dict_of_prompts[id_], user_message)
        if id_ == 4:
            return ConnectionGPT.deposits(self.dict_of_prompts[id_], user_message)
        if id_ == 6:
            return ConnectionGPT.ex_rate(self.dict_of_prompts[id_], user_message)
        if id_ == 5:
            return ConnectionGPT.insurance(self.dict_of_prompts[id_], user_message)
        if id_ == 7:
            return ConnectionGPT.money_transfers(self.dict_of_prompts[id_], user_message)
        if id_ == 8:
            return ConnectionGPT.bank_account(self.dict_of_prompts[id_], user_message)

    @staticmethod
    def to_credit(info: List[Credit], user_message: str) -> str:

        references = []
        text = ''

        for credit in info:
            references.append(credit.credit_info.link)
            text += f'название кредита: {credit.name} ' \
                    f' описание кредита: {credit.credit_info.terms}\n'

        return ConnectionGPT.send_to_gpt(text, user_message)

    @staticmethod
    def atm_machine(info: List[ATM], user_message: str) -> str:

        generated_text = ''
        steps = len(info) // 50
        atm = [atm.name for atm in info]
        for i in range(steps + 1):
            text = f"{''.join(atm[i * 50: (i + 1) * 50])}"
            generated_text += ConnectionGPT.send_to_gpt(text, user_message)

        return generated_text

    @staticmethod
    def cards(info: List[Card], user_message: str) -> str:

        info_ = {card.name: card.info for card in info}
        text1 = ''
        text2 = ''
        text3 = ''
        first = list(info_.items())[len(info_.items()) // 3:]
        second = list(info_.items())[len(info_.items()) // 3:2 * len(info_.items()) // 3]
        third = list(info_.items())[2 * len(info_.items()) // 3:]
        for name, value in first:
            text1 += f'название карты: {name}' + ' ' + value + '\n'
        for name, value in second:
            text2 += f'название карты: {name}' + ' ' + value + '\n'
        for name, value in third:
            text3 += f'название карты: {name}' + ' ' + value + '\n'
        listik = [text1, text2, text3]
        generated_text = ''

        for text in listik:
            generated_text += ConnectionGPT.send_to_gpt(text, user_message)

        return generated_text

    @staticmethod
    def deposits(info: List[Deposit], user_message: str) -> str:

        references = []
        text = ''

        for deposit in info:
            references.append(deposit.deposit_info.link)
            text += f'название вклада: {deposit.name} ' \
                    f'описание вклада: {deposit.deposit_info.terms}\n'

        return ConnectionGPT.send_to_gpt(text, user_message)

    @staticmethod
    def ex_rate(info: List[ExchangeRate], user_message: str) -> str:

        text = ''
        for currency in info:
            text += f'название валюты: {currency.name} курс: {currency.buy, currency.sell}' + '\n'

        return ConnectionGPT.send_to_gpt(text, user_message)

    @staticmethod
    def insurance(info: List[Insurance], user_message: str) -> str:

        references = []
        text = ''
        for item in info:
            references.append(item.insurance_info.link)
            text += f'название страховки: {item.name} ' \
                    f'описание страховки:  {item.insurance_info.terms}\n'
        return ConnectionGPT.send_to_gpt(text, user_message)

    @staticmethod
    def money_transfers(info: List[MoneyTransferInfo], user_message: str) -> str:

        references = []
        text = ''

        for item in info:
            references.append(item.link)
            text += f'название перевода: {item.name}\n'

        return ConnectionGPT.send_to_gpt(text, user_message)

    @staticmethod
    def bank_account(info: List[BankAccount], user_message: str) -> str:

        references = []
        text = ''

        for item in info:
            references.append(item.bank_account_info.link)
            text += f'название счета: {item.name} ' \
                    f'описание счета {item.bank_account_info.terms}\n'

        return ConnectionGPT.send_to_gpt(text, user_message)

    @staticmethod
    def send_to_gpt(text: str, user_message: str):
        prompt = f'ответь на сообщение: {user_message}, используя информацию:\n\n' + text

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful chat assistant in a bank."},
                {"role": "user", "content": prompt},

            ],
            temperature=0.2,
        )

        generated_text = response.choices[0].message['content']
        return generated_text
