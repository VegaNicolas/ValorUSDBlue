from datetime import datetime
import schedule
import time
from dotenv import load_dotenv
import bot
from telegram import Telegram
from twitter import Twitter

load_dotenv()

if __name__ == "__main__":
    print("Bot Ready!")

    client = bot.Bot()
    telegram = Telegram()
    twitter = Twitter()

    # Schedule Setup
    client.startup()

    minutes = ["00", "05", "10", "15", "20",
               "25", "30", "35", "40", "45", "50", "55"]

    schedule.every().day.at("16:30:00").do(telegram.closing)
    schedule.every().day.at("16:30:00").do(twitter.closing)

    for i in minutes:
        schedule.every().hour.at(f":{i}").do(client.update_price)
        schedule.every().hour.at(f":{i}").do(telegram.core)
        schedule.every().hour.at(f":{i}").do(twitter.core)
        schedule.every().hour.at(f":{i}").do(client.update_database)

    schedule.every().day.at("11:05:00").do(client.opening)
    schedule.every().day.at("19:01:00").do(client.update_dates)

    while True:
        if bot.start < datetime.now():
            schedule.run_pending()
        else:
            schedule.idle_seconds()

        time.sleep(1)
