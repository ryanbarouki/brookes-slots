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
PROCESSING_SLOT = False
bot = telebot.TeleBot(API_KEY)
tracked_counts_all_chats = {}

@bot.message_handler(commands=['help', 'start'])
def start(message):
    print(message.text)
    bot.send_message(message.chat.id, "Hello you little climbing slut, missed a Brookes slot have we?\nStart by listing the slots by clicking here:\n\
/monday\n/tuesday\n/wednesday\n/thursday\n/friday\n/saturday\n/sunday")


def slot_request(message):
    request = message.text.split()
    return len(request) >= 2 and request[1].lower() == "slots"

@bot.message_handler(commands=['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'])
def send_slots(message):
    global PROCESSING_SLOT
    if PROCESSING_SLOT:
        return
    PROCESSING_SLOT = True
    input = message.text[1:].split("@")[0]
    days_of_week = {'monday': 'mon' , 'tuesday': 'tue', 'wednesday': 'wed', 'thursday': 'thu', 'friday': 'fri', 'saturday': 'sat', 'sunday': 'sun'}
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
    global PROCESSING_SLOT
    reply = message.text
    try:
        slot_id = int(reply) - 1
        tracking_spaces_job(message, slots[slot_id])

        bot.reply_to(message, f"Tracking {slots[slot_id]['date']} slot")
        sched = BackgroundScheduler()
        slot_date = datetime.strptime(slots[slot_id]['date'], f"%a %d %b %Y, %H:%M")
        sched.add_job(lambda: tracking_spaces_job(message, slots[slot_id]), 'interval', seconds=10, end_date=slot_date)
        sched.start()
        PROCESSING_SLOT = False
    except ValueError:
        msg = bot.reply_to(message, "Not a valid slot choice, please input a number")
        bot.register_next_step_handler(msg, lambda message: process_slot_choice(message, slots))

def tracking_spaces_job(message, slot):
    scraper = BrookesScraper(USER, PASSWORD)
    try:
        space_count = scraper.get_space_count_for_slot(slot)
    except:
        bot.send_message(message.chat.id, f"One at a time please!")
        return

    tracked_counts = tracked_counts_all_chats[message.chat.id] if message.chat.id in tracked_counts_all_chats else {}

    slot_date = datetime.strptime(slot['date'], f"%a %d %b %Y, %H:%M")
    if slot_date < datetime.now() and slot['date'] in tracked_counts:
        try:
            del tracked_counts[slot['date']]
            bot.send_message(message.chat.id, f"Stopped tracking {slot['date']} slot")
            return
        except RuntimeError:
            bot.send_message(message.chat.id, f"Could not stop tracking process for {slot['date']}")

    if slot['date'] not in tracked_counts:
        tracked_counts[slot['date']] = space_count
    if tracked_counts[slot['date']] != space_count:
        tracked_counts[slot['date']] = space_count
        bot.send_message(message.chat.id, f"Tracking {slot['date']} slot\nCurrently {space_count} spaces available")
    tracked_counts_all_chats[message.chat.id] = tracked_counts

bot.polling()

