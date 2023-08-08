from datetime import datetime, timedelta
import json
import os
import requests
from dotenv import load_dotenv
import telebot
import tweepy


load_dotenv()

# APIs' setup
# Telegram
TELEGRAM_TOKEN: str = os.getenv("TELEGRAM_TOKEN")

# Twitter
API_KEY_TW: str = os.getenv("API_KEY_TW")
API_KEY_SECRET_TW: str = os.getenv("API_KEY_SECRET_TW")
BEARER_TOKEN_TW: str = os.getenv("BEARER_TOKEN_TW")
CLIENT_ID_TW: str = os.getenv("CLIENT_ID_TW")
CLIENT_SECRET_TW: str = os.getenv("CLIENT_SECRET_TW")
ACCESS_TOKEN_TW: str = os.getenv("ACCESS_TOKEN_TW")
ACCESS_TOKEN_SECRET_TW: str = os.getenv("ACCESS_TOKEN_SECRET_TW")


# Global Variables
intervalo_blue: float = 0  # Precio del intervalo anterior
apertura_blue: float = 0
start: str = datetime.now().replace(hour=8, minute=55, second=0)


class Bot():

    def __init__(self):
        # Telegram
        self.channel_id: str = os.getenv("CHANNEL_ID")
        self.telegram_client: telebot.TeleBot = telebot.TeleBot(TELEGRAM_TOKEN)

        # Twitter
        self.twitter_client: tweepy.Client = tweepy.Client(
            consumer_key=API_KEY_TW,
            consumer_secret=API_KEY_SECRET_TW,
            bearer_token=BEARER_TOKEN_TW,
            access_token=ACCESS_TOKEN_TW,
            access_token_secret=ACCESS_TOKEN_SECRET_TW
        )

    def update_json(self):
        """ Takes an URL as a parameter (unable due to schedule library #TODO, so hardcoded) which leads
            to a json in Ámbito Financiero webpage (Argentinian news media that follows the informal ARS/USD rate)
            which is the source of the information used in every bot done by me."""

        URL: str = os.getenv("URL")
        result: str = requests.get(URL).text
        datos: list = json.loads(result)
        return datos

    def startup(self):
        """ QoL function which is called only when the service is restarted. It allows better
            testing results and even to commit changes in production on a weekday. The function settles
            the two main variables in the script (apertura_blue and intervalo_blue) which are not saved
            when the bot is down, so it 'restarts' automatically making an outage to not affect its normal
            output."""

        global apertura_blue
        global intervalo_blue
        data: list = self.update_json()
        apertura_blue = float(data["valor_cierre_ant"].replace(",", "."))
        intervalo_blue = float(data["venta"].replace(",", "."))

        now: str = datetime.now().strftime("%d/%m/%y - %H:%M:%S")
        print(f"{now} - Arranca la jornada. Dólar Blue abrió en ${int(apertura_blue)}.")

    '''def non_business_day(self):
        """ This function compares actual datetime with the one it is in the json file (updated rate)
            so the bot gives zero output during weekends and non-business days.
            *Note: this function may be deprecated in the future due to the json doesnt update in those days.
            It only affects cierre().
            # TODO Legacy method, deprecated in 8/8 due to api changes
        """

        data: list = self.update_json()
        fecha_feriado: str = data["fecha"]
        dia_update: list[str] = fecha_feriado.split(" ")

        return dia_update[0] != datetime.now().strftime("%d/%m/%Y")'''

    def opening(self):  # 11.05hs
        """ Internal function which updates the apertura_blue variable if been outaged during night.
        """

        global apertura_blue

        data: list = self.update_json()
        now_open: str = datetime.now().strftime("%d/%m/%y - %H:%M:%S")
        apertura_blue = float(data["valor_cierre_ant"].replace(",", "."))
        print(f"{now_open} - El dólar abre a ${apertura_blue}.")

    def update_dates(self):  # 19.01hs
        """ This updates the start variable at 19.01 (GMT-3) and sums 24hours in order to resume bot's functionality the next day 
            at 8.55 (GMT-3). In the future, this variable may be modified to 11.00 (GMT-3) to be more optimized.
        """

        global start

        start += timedelta(days=1)
        now_change: str = datetime.now().strftime("%d/%m/%y - %H:%M:%S")
        print(
            f"{'-'*36}\n{now_change} - Fechas actualizadas\n{'-'*36}")

    def core(self):
        """ Main output function. Every 5 minutes will update_json() so if it detects a new rate, 
            it will be the output of the bot. It isn't affected by the function arranque() because
            its only triggered when a change is made.
        """

        global intervalo_blue

        if datetime.now().strftime("%H:%M:%S") == "16:30:00":
            return

        # TODO maybe this function is called twice because of non_business_day() * no anymore
        data: list = self.update_json()

        venta_blue: float = float(data["venta"].replace(",", "."))
        now_change: str = datetime.now().strftime("%d/%m/%y - %H:%M:%S")

        if intervalo_blue > venta_blue:
            self.telegram_client.send_message(
                chat_id=self.channel_id, text=f"El Dólar Blue bajó ${int(intervalo_blue - venta_blue)} a ${int(venta_blue)}.")
            self.twitter_client.create_tweet(
                text=f"El Dólar Blue bajó ${int(intervalo_blue - venta_blue)} a ${int(venta_blue)}.")
            intervalo_blue = venta_blue
            print(f"{now_change} - Went down to ${int(intervalo_blue)} ARS/USD")

        elif intervalo_blue < venta_blue:
            self.telegram_client.send_message(
                chat_id=self.channel_id, text=f"El Dólar Blue subió ${int(venta_blue - intervalo_blue)} a ${int(venta_blue)}.")
            self.twitter_client.create_tweet(
                text=f"El Dólar Blue subió ${int(venta_blue - intervalo_blue)} a ${int(venta_blue)}.")
            intervalo_blue = venta_blue
            print(f"{now_change} - Raised to ${int(intervalo_blue)} ARS/USD")

    def closing(self):  # 16.30hs
        """ Output a closing rate exchange message at 16.30 (GMT-3), although the function core() is still running until
            19.00 (GMT-3), so sometimes cierre() might not be the last output of the day.
        """

        global apertura_blue

        data: list = self.update_json()
        variation: str = data["variacion"]
        now_open: str = datetime.now().strftime("%d/%m/%y - %H:%M:%S")
        cierre_blue: float = float(data["venta"].replace(",", "."))

        if cierre_blue > apertura_blue:
            self.telegram_client.send_message(
                chat_id=self.channel_id, text=f"El Dólar Blue cierra la jornada a ${int(cierre_blue)}. En el día subió ${int(cierre_blue - apertura_blue)}, lo que significa una variación de {variation}.")
            self.twitter_client.create_tweet(
                text=f"El Dólar Blue cierra la jornada a ${int(cierre_blue)}. En el día subió ${int(cierre_blue - apertura_blue)}, lo que significa una variación de {variation}.")
            print(f"{now_open} - Closed at {cierre_blue} ARS/USD")

        elif cierre_blue < apertura_blue:
            self.telegram_client.send_message(
                chat_id=self.channel_id, text=f"El Dólar Blue cierra la jornada a ${int(cierre_blue)}. En el día bajó ${int(apertura_blue - cierre_blue)}, lo que significa una variación de {variation}.")
            self.twitter_client.create_tweet(
                text=f"El Dólar Blue cierra la jornada a ${int(cierre_blue)}. En el día bajó ${int(apertura_blue - cierre_blue)}, lo que significa una variación de {variation}.")

            print(f"{now_open} - Closed at {cierre_blue} ARS/USD")

        else:
            self.telegram_client.send_message(
                chat_id=self.channel_id, text=f"El Dólar Blue cierra la jornada sin cambios a ${int(cierre_blue)}.")
            self.twitter_client.create_tweet(
                text=f"El Dólar Blue cierra la jornada sin cambios a ${int(cierre_blue)}.")
            print(f"{now_open} - Closed at {int(cierre_blue)} ARS/USD")
