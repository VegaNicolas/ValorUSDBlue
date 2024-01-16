import schedule
import time
from datetime import datetime
from Bot.startup import startup
from Bot.update_dates import update_dates, start
from Database.database import update_database, update_price
from SocialMedia.telegram import telegram_client
from SocialMedia.twitter import twitter_client


def main():
    print("Bot Ready!")

    # Schedule Setup
    startup()
    update_database()
    print('Database Updated')

    minutes = ["00", "05", "10", "15", "20",
               "25", "30", "35", "40", "45", "50", "55"]

    schedule.every().day.at("16:30:00").do(
        telegram_client.closing)  # 16.30 -> 19.30 UTC
    schedule.every().day.at("16:30:00").do(twitter_client.closing)

    for i in minutes:
        schedule.every().hour.at(f":{i}").do(update_price)
        schedule.every().hour.at(f":{i}").do(telegram_client.core)
        schedule.every().hour.at(f":{i}").do(twitter_client.core)
        schedule.every().hour.at(f":{i}").do(update_database)

    schedule.every().day.at("11:05:00").do(startup)  # 11.05 -> 14.05 UTC
    schedule.every().day.at("21:01:00").do(update_dates)  # 19.01 -> 22.01 UTC

    while True:
        if start < datetime.now():
            schedule.run_pending()
        else:
            schedule.idle_seconds()

        time.sleep(1)


main()
