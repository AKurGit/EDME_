import os
import boto3
from typing import List, Dict, Union


class DynamoDBClient:
    def __init__(self):
        self.session = boto3.Session(
            aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
            aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY']
        )
        self.dynamodb_resource = self.session.resource('dynamodb', region_name='eu-west-2')
        
        

    def write_to_table(self, table_name: str, partition_key_name: str, data: Union[Dict[str, str], List[Dict[str, str]]]):
        try:
            table = self.dynamodb_resource.Table(table_name)
            with table.batch_writer() as batch:
                if isinstance(data, dict):
                    data = [data]  

                for item in data:
                    partition_key_value = item.get(partition_key_name)
                    if partition_key_value is not None:
                        item = {**item, partition_key_name: partition_key_value}
                        batch.put_item(Item=item)

            print("Data successfully written to DynamoDB table.")

        except Exception as e:
            print(f'Error writing data to DynamoDB: {str(e)}')
                  

    def get_data_from_table(self, table_name):
        try:
            table = self.dynamodb_resource.Table(table_name)
            response = table.scan()

            items = response['Items']

            while 'LastEvaluatedKey' in response:
                response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
                items.extend(response['Items'])

            return items

        except Exception as e:
            print(f'Error retrieving data from DynamoDB: {str(e)}')
            return None
