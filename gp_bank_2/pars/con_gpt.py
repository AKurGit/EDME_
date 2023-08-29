import openai
from typing import List, Dict, Tuple


class ConnectionGPT:

    openai.api_key = "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"

    func_dict = {
        '1': credits,
    }

    def __init__(self,
                 credits: Dict[str, Tuple[str, str]],
                 atm_machine: List[str],
                 cards: Dict[str, Tuple[str, str]],
                 deposits: Dict[str, Tuple[str, str]],
                 ex_rate: Dict[str, str],
                 insurance: Dict[str, Tuple[str, str]],
                 money_transfers: List[Tuple[str, str]],
                 bank_account: Dict[str, Tuple[str, str]]):

        self.dict_of_prompts = {
            1: credits,
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
            return ConnectionGPT.credits(self.dict_of_prompts[id_], user_message)
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
    def credits(info: Dict[str, Tuple[str, str]], user_message: str) -> str:

        references = [value[0] for value in info.values()]
        # print(references)
        text = ''
        for name, value in info.items():
            text += f'название кредита: {name}' + ' ' + value[1] + '\n'

        # print(text)
        return ConnectionGPT.send_to_gpt(text, user_message)

    @staticmethod
    def atm_machine(info: List[str], user_message: str) -> str:

        generated_text = ''
        steps = len(info) // 50
        # print(steps)
        for i in range(steps + 1):
            text = f"{''.join(info[i * 50: (i + 1) * 50])}"
            generated_text += ConnectionGPT.send_to_gpt(text, user_message)

        return generated_text

    @staticmethod
    def cards(info: Dict[str, Tuple[str, str]], user_message: str) -> str:

        references = [value[0] for value in info.values()]
        inff = {name: value[1] for name, value in info.items()}
        text1 = ''
        text2 = ''
        text3 = ''
        first = list(inff.items())[len(inff.items()) // 3:]
        second = list(inff.items())[len(inff.items()) // 3:2 * len(inff.items()) // 3]
        third = list(inff.items())[2 * len(inff.items()) // 3:]
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
    def deposits(info: Dict[str, Tuple[str, str]], user_message: str) -> str:

        references = [value[0] for value in info.values()]
        text = ''
        for name, value in info.items():
            text += f'название вклада: {name}' + ' ' + value[1] + '\n'

        # print(text)
        return ConnectionGPT.send_to_gpt(text, user_message)

    @staticmethod
    def ex_rate(info: Dict[str, str], user_message: str) -> str:

        text = ''
        for name, value in info.items():
            text += name + ' ' + value + '\n'

        # print(text)
        return ConnectionGPT.send_to_gpt(text, user_message)

    @staticmethod
    def insurance(info: Dict[str, Tuple[str, str]], user_message: str) -> str:

        references = [value[0] for value in info.values()]
        text = ''
        for name, value in info.items():
            text += f'название страховки: {name}' + ' ' + value[1] + '\n'

        # print(text)
        return ConnectionGPT.send_to_gpt(text, user_message)

    @staticmethod
    def money_transfers(info: List[Tuple[str, str]], user_message: str) -> str:

        references = [value[1] for value in info]
        text = ''
        for value in info:
            text += f'название перевода: {value[0]}\n'

        # print(text)
        return ConnectionGPT.send_to_gpt(text, user_message)

    @staticmethod
    def bank_account(info: Dict[str, Tuple[str, str]], user_message: str) -> str:

        references = [value[0] for value in info.values()]
        text = ''
        for name, value in info.items():
            text += f'название счета: {name}' + ' ' + value[1] + '\n'

        # print(text)

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
