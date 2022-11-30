import telegram.ext as tg
from dotenv import load_dotenv
import os

def start(update, context):
    update.message.reply_text("Hello you little climbing slut, missed a Brookes slot have we?")

if __name__ == "__main__":
    load_dotenv()
    token = os.getenv("TELEGRAM-API-KEY")
    updater = tg.Updater(token, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(tg.CommandHandler('start', start))
    updater.start_polling()
    updater.idle()