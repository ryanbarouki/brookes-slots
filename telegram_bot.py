from datetime import datetime
from functools import reduce
from dotenv import load_dotenv
import telebot
import os
from scrape_brookes import BrookesScraper
from apscheduler.schedulers.background import BackgroundScheduler

load_dotenv()
API_KEY = os.getenv("TELEGRAM-API-KEY")
USER = os.getenv("BROOKES-USERNAME")
PASSWORD = os.getenv("BROOKES-PASSWORD")
bot = telebot.TeleBot(API_KEY)
jobs = {}
tracked_counts = {}

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Hello you little climbing slut, missed a Brookes slot have we?")

def slot_request(message):
    request = message.text.split()
    return len(request) >= 2 and request[1].lower() == "slots"

@bot.message_handler(func=slot_request)
def send_slots(message):
    input = message.text.split()[0]
    print(input)
    days_of_week = {'monday': 'mon' , 'tuesday': 'tue', 'wednesday': 'wed', 'thursday': 'thu', 'friday': 'fri', 'saturday': 'sat', 'sunday': 'sun'}
    if input.lower() not in days_of_week:
        bot.reply_to(message, "Please enter a day of the week. e.g. 'Thursday slots'")
        return
    day = days_of_week[input.lower()]
    scraper = BrookesScraper(USER, PASSWORD)
    slots = scraper.get_slots_for_day(day)
    if len(slots) == 0:
        bot.send_message(message.chat.id, "Couldn't find slots!")
        return
    slot_string = reduce(lambda a, b: f"{a}\n{b}", [f'{i+1}. {slots[i]["date"]} - {slots[i]["status"]} spaces' for i in range(len(slots))])
    slot_msg = bot.send_message(message.chat.id, slot_string)
    msg = bot.reply_to(slot_msg, "Which slot do you want to track?")
    bot.register_next_step_handler(msg, lambda message: process_slot_choice(message, slots))

def process_slot_choice(message, slots):
    reply = message.text
    try:
        slot_id = int(reply) - 1
        tracking_spaces_job(message, slots[slot_id])
    except ValueError:
        msg = bot.reply_to(message, "Not a valid slot choice, please input a number")
        bot.register_next_step_handler(msg, lambda message: process_slot_choice(message, slots))
    bot.reply_to(message, f"Tracking {slots[slot_id]['date']} slot")

    sched = BackgroundScheduler()
    sched.add_job(lambda: tracking_spaces_job(message, slots[slot_id]), 'interval', seconds=10)
    sched.start()
    jobs[slots[slot_id]['date']] = sched

def tracking_spaces_job(message, slot):
    scraper = BrookesScraper(USER, PASSWORD)
    space_count = scraper.get_space_count_for_slot(slot)

    slot_date = datetime.strptime(slot['date'], f"%a %d %b %Y, %H:%M")
    if slot_date < datetime.now() and slot['date'] in jobs:
        jobs[slot['date']].shutdown()
        del jobs[slot['date']]
        del tracked_counts[slot['date']]

    if slot['date'] not in tracked_counts:
        tracked_counts[slot['date']] = space_count
    if tracked_counts[slot['date']] != space_count:
        tracked_counts[slot['date']] = space_count
        bot.send_message(message.chat.id, f"Tracking {slot['date']} slot\nCurrently {space_count} spaces available")

bot.polling()

