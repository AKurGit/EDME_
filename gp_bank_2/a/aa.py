from pars.db import DynamoDBClient


dc = DynamoDBClient()

cards = dc.get_data_from_table('bank_cards')
cards = {i['card_name']: ('', i['card_info']) for i in cards}
print(cards)
