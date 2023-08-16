import datetime
import json
import random
import boto3
import time

# STREAM_NAME = "order"
STREAM_NAME = "etl-kinesisStream-order"


def get_data():
    provisionary_products = [
        'Organic Quinoa',
        'Wild Alaskan Salmon',
        'Free Range Chicken',
        'Artisanal Sourdough Bread',
        'Locally Sourced Honey',
        'Small Batch Craft Beer',
        'Farm Fresh Eggs',
        'Homemade Jam',
        'Handcrafted Pasta',
        'Artisanal Cheese Selection',
        'Premium Olive Oil',
        'Farm to Table Vegetables',
        'Freshly Roasted Coffee Beans',
        'Artisanal Chocolate Truffles',
        'Locally Sourced Grass-Fed Beef',
        'Organic Leafy Greens',
        'All-Natural Granola',
        'Freshly Baked Croissants',
        'Handcrafted Beer Battered Fish',
        'Farm Fresh Raw Milk'
    ]
    
    return {
        'order_id': random.randint(1, 30),
        'customer_id': random.randint(1, 10),
        'product_name': random.choice(provisionary_products),
        'quantity': random.randint(1, 10),
        'price': round(random.uniform(1.0, 50.0), 2)
    }


def generate(stream_name, kinesis_client):
    while True:
        data = get_data()
        print(data)
        kinesis_client.put_record(
            StreamName=stream_name,
            Data=json.dumps(data),
            PartitionKey=str(data['customer_id']))
        time.sleep(1)


if __name__ == '__main__':
    generate(STREAM_NAME, boto3.client('kinesis', region_name='us-east-1'))

