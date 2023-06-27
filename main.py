from datetime import datetime
import schedule
import time
from dotenv import load_dotenv
import bot

load_dotenv()

# Global Variables
intervalo_blue: float = 0  # Precio del intervalo anterior
apertura_blue: float = 0
start: str = datetime.now().replace(hour=8, minute=55, second=0)


if __name__ == "__main__":
    print("Bot Ready!")

    client = bot.Bot()

     # Schedule Setup
    client.startup()

    minutes = ["00","05", "10", "15", "20", "25", "30", "35", "40", "45", "50", "55"]

    for i in minutes:
        schedule.every().hour.at(f":{i}").do(client.core)
    
    
    schedule.every().day.at("11:05:00").do(client.opening)
    schedule.every().day.at("16:30:00").do(client.closing)
    schedule.every().day.at("19:01:00").do(client.update_dates)
    
    
    while True:      
        if start < datetime.now():
            schedule.run_pending()
        else:
            schedule.idle_seconds()

        time.sleep(1)