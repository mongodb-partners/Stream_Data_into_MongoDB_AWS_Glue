import datetime
import json
import random
import boto3
import time

# STREAM_NAME = "customer"
STREAM_NAME = "etl-kinesisStream-customer"

# Set to keep track of generated customer IDs
generated_customer_ids = set()

def get_unique_customer_id():
    while True:
        customer_id = random.randint(1, 500)
        if customer_id not in generated_customer_ids:
            generated_customer_ids.add(customer_id)
            return customer_id

def get_data():
    customer_id = get_unique_customer_id()
    customer_name = str('CUSTOMER') + '_' + str(customer_id)
    email_id = customer_name.lower() + "@gmail.com"
    country_id = customer_id
    return {
        'customer_id': customer_id,
        'customer_name': customer_name,
        'email_id': email_id,
        'country_id': country_id
    }

def generate(stream_name, kinesis_client, max_records=500):
    record_count = 0
    while record_count < max_records:
        data = get_data()
        print(data)
        record = kinesis_client.put_record(
            StreamName=stream_name,
            Data=json.dumps(data),
            PartitionKey=str(data['customer_id']))
        print(record)
        record_count += 1
        print('record_count for customer:===>', record_count)
        time.sleep(1)

if __name__ == '__main__':
    generate(STREAM_NAME, boto3.client('kinesis', region_name='us-east-1'))




## 'boto3' is client library in Pythin to interact with AWS services.

