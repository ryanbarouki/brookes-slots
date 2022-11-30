from functools import reduce
from dotenv import load_dotenv
import telebot
import os
from scrape_brookes import BrookesScraper

load_dotenv()
API_KEY = os.getenv("TELEGRAM-API-KEY")
USER = os.getenv("BROOKES-USERNAME")
PASSWORD = os.getenv("BROOKES-PASSWORD")
bot = telebot.TeleBot(API_KEY)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Hello you little climbing slut, missed a Brookes slot have we?")

def slot_request(message):
    request = message.text.split()
    return len(request) >= 2 and request[1].lower() == "slots"

@bot.message_handler(func=slot_request)
def send_slots(message):
    day = message.text.split()[0]
    scraper = BrookesScraper(USER, PASSWORD)
    slots = scraper.get_slots_for_day(day)
    if len(slots) == 0:
        bot.send_message(message.chat.id, "Couldn't find slots!")
        return
    slot_string = reduce(lambda a, b: f"{a}\n{b}", slots)
    bot.send_message(message.chat.id, slot_string)

bot.polling()

