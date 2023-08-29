from db import DynamoDBClient


dc = DynamoDBClient()
atm_ = dc.get_data_from_table('atm')
print(atm_)
