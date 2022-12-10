import json
from scrape_brookes import BrookesScraper
import boto3
from botocore.exceptions import ClientError
import telebot
import os

API_KEY = os.getenv("TELEGRAM_API_KEY")
USER = os.getenv("BROOKES_USERNAME")
PASSWORD = os.getenv("BROOKES_PASSWORD")

bot = telebot.Telebot(API_KEY)

db_client = boto3.client('dynamodb')

def create_table(table_name):
    try:
        db_client.create_table(
            TableName=table_name,
            KeySchema=[
                {'AttributeName': 'date', 'KeyType': 'HASH'},
            ],
            AttributeDefinitions=[
                {'AttributeName': 'date', 'AttributeType': 'S'},
            ],
            ProvisionedThroughput={'ReadCapacityUnits': 10, 'WriteCapacityUnits': 10}
        )
    except ClientError as err:
        print(f"Couldn't create table {table_name}. Here's why: {err.response['Error']['Code']}: {err.response['Error']['Message']}")
    
def put_item(table_name, date, count):
    db_client.put_item(
        TableName=table_name,
        Item={'date': {'S': date}, 'count': {'N': f"{count}"}}
    )
    
def get_count(table_name, date):
    response = db_client.get_item(
        TableName=table_name,
        Key={'date': {'S': date}}
    )
    return int(response['Item']['count']['N'])

def track_spaces(chat_id, slot):

    scraper = BrookesScraper(USER, PASSWORD)
    try:
        space_count = scraper.get_space_count_for_slot(slot)
    except:
        bot.send_message(chat_id, f"Ahhh too much going on at once!")
        return

    # grabbing counts from db
    table_name = f"{chat_id}"
    create_table(table_name)
    # tracked_counts = tracked_counts_all_chats[message.chat.id] if message.chat.id in tracked_counts_all_chats else {}

    # slot_date = datetime.strptime(slot['date'], f"%a %d %b %Y, %H:%M")
    # if slot_date < datetime.now() and slot['date'] in tracked_counts:
    #     try:
    #         del tracked_counts[slot['date']]
    #         bot.send_message(message.chat.id, f"Stopped tracking {slot['date']} slot")
    #         return
    #     except RuntimeError:
    #         bot.send_message(message.chat.id, f"Could not stop tracking process for {slot['date']}")

    try:
        count = get_count(table_name, slot['date'])
        if count != space_count:
            put_item(table_name, slot['date'], space_count)
            bot.send_message(chat_id, f"Tracking {slot['date']} slot\nCurrently {space_count} spaces available")
    except ClientError:
        put_item(table_name, slot['date'], space_count)
    
def lambda_handler(event, context):
        chat_id = event["chat_id"]
        slot = event["slot"]
    
        track_spaces(chat_id, slot)
        
        return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda! TEST TEST')
    }