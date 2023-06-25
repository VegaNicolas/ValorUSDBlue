from datetime import datetime, timedelta
import schedule
import time
import json
import os
import requests
from dotenv import load_dotenv
import telebot

# https://www.youtube.com/watch?v=TLtnXAWFUQg

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Global Variables
intervalo_blue: float = 0  # Precio del intervalo anterior
apertura_blue: float = 0
start: str = datetime.now().replace(hour=8, minute=55, second=0)

#TODO change before deployment
channel_id = os.getenv("CHANNEL_ID")


def update_json():

    """ Takes an URL as a parameter (unable due to schedule library #TODO, so hardcoded) which leads
        to a json in Ámbito Financiero webpage (Argentinian news media that follows the informal ARS/USD rate)
        which is the source of the information used in every bot done by me."""
        
    URL: str = "https://mercados.ambito.com//dolar/informal/variacion"
    result: str = requests.get(URL).text
    datos: list = json.loads(result)
    return datos


def arranque():

    """ QoL function which is called only when the service is restarted. It allows better
        testing results and even to commit changes in production on a weekday. The function settles
        the two main variables in the script (apertura_blue and intervalo_blue) which are not saved
        when the bot is down, so it 'restarts' automatically making an outage to not affect its normal
        output."""

    global apertura_blue
    global intervalo_blue
    data: list = update_json()
    apertura_blue = float(data["valor_cierre_ant"].replace(",","."))

    now: str = datetime.now().strftime("%d/%m/%y - %H:%M:%S")
    print(f"{now} - Arranca la jornada. Dólar Blue abrió en ${int(apertura_blue)}.")


def dia_no_habil():

    """ This function compares actual datetime with the one it is in the json file (updated rate)
        so the bot gives zero output during weekends and non-business days.
        *Note: this function may be deprecated in the future due to the json doesnt update in those days.
        It only affects cierre().
    """

    data: list = update_json()
    fecha_feriado: str = data["fecha"]
    dia_update: list[str] = fecha_feriado.split(" ")

    return dia_update[0] != datetime.now().strftime("%d/%m/%Y")


def apertura(): #11.05hs

    """ Internal function which updates the apertura_blue variable if been outaged during night.
    """

    global apertura_blue

    if dia_no_habil():
        return
    
    data: list = update_json()
    now_open: str = datetime.now().strftime("%d/%m/%y - %H:%M:%S")
    apertura_blue = float(data["valor_cierre_ant"].replace(",","."))
    print(f"{now_open} - El dólar abre a ${apertura_blue}.")


def core(): 
    
    """ Main output function. Every 5 minutes will update_json() so if it detects a new rate, 
        it will be the output of the bot. It isn't affected by the function arranque() because
        its only triggered when a change is made.
    """

    global intervalo_blue

    if datetime.now().strftime("%H:%M:%S") == "16:30:00": 
        return
    
    if dia_no_habil():
        return

    data: list = update_json() # TODO maybe this function is called twice because of dia_no_habil()

    venta_blue: float = float(data["venta"].replace(",","."))
    now_change: str = datetime.now().strftime("%d/%m/%y - %H:%M:%S")

    if intervalo_blue > venta_blue:
        bot.send_message(chat_id=channel_id, text=f"El Dólar Blue bajó ${int(intervalo_blue - venta_blue)} a ${int(venta_blue)}.")
        intervalo_blue = venta_blue
        print(f"{now_change} - Changed to ${int(intervalo_blue)} ARS/USD")
           
    elif intervalo_blue < venta_blue:
        bot.send_message(chat_id=channel_id, text=f"El Dólar Blue subió ${int(venta_blue - intervalo_blue)} a ${int(venta_blue)}.")
        intervalo_blue = venta_blue
        print(f"{now_change} - Changed to ${int(intervalo_blue)} ARS/USD")
    

def cierre(): # 16.30hs

    """ Output a closing rate exchange message at 16.30 (GMT-3), although the function core() is still running until
        19.00 (GMT-3), so sometimes cierre() might not be the last output of the day.
    """

    global apertura_blue
    if dia_no_habil():
        now_open: str = datetime.now().strftime("%d/%m/%y - %H:%M:%S")
        print(f"{now_open} - Feriado o finde, so no activity")
        return
    
    data: list = update_json()
    variation: str = data["variacion"]
    now_open: str = datetime.now().strftime("%d/%m/%y - %H:%M:%S")
    cierre_blue: float = float(data["venta"].replace(",","."))

    if cierre_blue > apertura_blue:
        bot.send_message(chat_id=channel_id, text=f"El Dólar Blue cierra la jornada a ${int(cierre_blue)}. En el día subió ${int(cierre_blue - apertura_blue)}, lo que significa una variación de {variation}.")
        print(f"{now_open} - Closed at {cierre_blue} ARS/USD")

    elif cierre_blue < apertura_blue:
        bot.send_message(chat_id=channel_id, text=f"El Dólar Blue cierra la jornada a ${int(cierre_blue)}. En el día bajó ${int(apertura_blue - cierre_blue)}, lo que significa una variación de {variation}.")
        print(f"{now_open} - Closed at {cierre_blue} ARS/USD")

    else:
        bot.send_message(chat_id=channel_id, text=f"El Dólar Blue cierra la jornada sin cambios a ${int(cierre_blue)}.")
        print(f"{now_open} - Closed at {cierre_blue} ARS/USD")


def update_dates(): #19.01hs

    """ This updates the start variable at 19.01 (GMT-3) and sums 24hours in order to resume bot's functionality the next day 
        at 8.55 (GMT-3). In the future, this variable may be modified to 11.00 (GMT-3) to be more optimized.
    """

    global start
    start += timedelta(days=1)
    now_change: str = datetime.now().strftime("%d/%m/%y - %H:%M:%S")
    print(f"------------------------------------\n{now_change} - Fechas actualizadas\n------------------------------------")


if __name__ == "__main__":
    print("Bot Ready!")

     # Schedule Setup
    arranque()

    # TODO test
    minutes = ["00","05", "10", "15", "20", "25", "30", "35", "40", "45", "50", "55"]

    for i in minutes:
        schedule.every().hour.at(f":{i}").do(core)
    
    
    schedule.every().day.at("11:05:00").do(apertura)
    schedule.every().day.at("16:30:00").do(cierre)
    schedule.every().day.at("19:01:00").do(update_dates)
    """schedule.every().hour.at(":00").do(core)
    schedule.every().hour.at(":05").do(core)
    schedule.every().hour.at(":10").do(core)
    schedule.every().hour.at(":15").do(core)
    schedule.every().hour.at(":20").do(core)
    schedule.every().hour.at(":25").do(core)
    schedule.every().hour.at(":30").do(core)
    schedule.every().hour.at(":35").do(core)
    schedule.every().hour.at(":40").do(core)
    schedule.every().hour.at(":45").do(core)
    schedule.every().hour.at(":50").do(core)
    schedule.every().hour.at(":55").do(core)"""
    
    
    while True:      
        if start < datetime.now():
            schedule.run_pending()
        else:
            schedule.idle_seconds()

        time.sleep(1)