import schedule
import time
import json
from datetime import datetime
from dotenv import load_dotenv
from Bot.startup import startup
from Bot.update_dates import update_dates, start
from Database.database import update_database, update_price
from SocialMedia.telegram import telegram_client
from SocialMedia.twitter import twitter_client

load_dotenv()

def main():
    print("Bot Ready!")

    # Schedule Setup
    startup()

    minutes = ["00", "05", "10", "15", "20",
               "25", "30", "35", "40", "45", "50", "55"]

    schedule.every().day.at("16:30:00").do(telegram_client.closing)  # 16.30
    schedule.every().day.at("16:30:00").do(twitter_client.closing)

    for i in minutes:
        schedule.every().hour.at(f":{i}").do(update_price)
        schedule.every().hour.at(f":{i}").do(telegram_client.core)
        schedule.every().hour.at(f":{i}").do(twitter_client.core)
        schedule.every().hour.at(f":{i}").do(update_database)

    schedule.every().day.at("11:05:00").do(startup)  # 11.05
    schedule.every().day.at("19:01:00").do(update_dates)  # 19.01

    while True:
        try:
            if start < datetime.now():
                schedule.run_pending()
            else:
                schedule.idle_seconds()

        except json.decoder.JSONDecodeError:
            print('JSON Error')

        time.sleep(1)



if __name__ == '__main__':
    main()
  