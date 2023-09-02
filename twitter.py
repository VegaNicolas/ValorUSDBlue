from datetime import datetime
import os
from dotenv import load_dotenv
import tweepy
import bot

load_dotenv()

API_KEY_TW: str = os.getenv("API_KEY_TW")
API_KEY_SECRET_TW: str = os.getenv("API_KEY_SECRET_TW")
BEARER_TOKEN_TW: str = os.getenv("BEARER_TOKEN_TW")
CLIENT_ID_TW: str = os.getenv("CLIENT_ID_TW")
CLIENT_SECRET_TW: str = os.getenv("CLIENT_SECRET_TW")
ACCESS_TOKEN_TW: str = os.getenv("ACCESS_TOKEN_TW")
ACCESS_TOKEN_SECRET_TW: str = os.getenv("ACCESS_TOKEN_SECRET_TW")


class Twitter(bot.Bot):

    def __init__(self):

        # Twitter
        self.client: tweepy.Client = tweepy.Client(
            consumer_key=API_KEY_TW,
            consumer_secret=API_KEY_SECRET_TW,
            bearer_token=BEARER_TOKEN_TW,
            access_token=ACCESS_TOKEN_TW,
            access_token_secret=ACCESS_TOKEN_SECRET_TW
        )

        auth: tweepy.OAuth1UserHandler = tweepy.OAuth1UserHandler(
            API_KEY_TW,
            API_KEY_SECRET_TW,
            ACCESS_TOKEN_TW,
            ACCESS_TOKEN_SECRET_TW)

        api = tweepy.API(auth)

        try:
            api.verify_credentials()
            print("Twitter Authentication Successful")
        except:
            print("Twitter Authentication Error")

    def core(self) -> None:
        """ Main output function. Every 5 minutes will update_json() so if it detects a new rate, 
            it will be the output of the bot. It isn't affected by the function arranque() because
            its only triggered when a change is made.
        """

        if datetime.now().strftime("%H:%M:%S") == "16:30:00":
            return

        if self.non_business_day():
            return

        now_change: str = datetime.now().strftime("%d/%m/%y - %H:%M:%S")

        if bot.intervalo_blue > bot.venta_blue:
            self.client.create_tweet(
                text=f"El Dólar Blue bajó ${int(bot.intervalo_blue - bot.venta_blue)} a ${int(bot.venta_blue)}.")

            bot.intervalo_blue = bot.venta_blue
            print(f"{now_change} - Went down to ${int(bot.intervalo_blue)} ARS/USD")

        elif bot.intervalo_blue < bot.venta_blue:
            self.client.create_tweet(
                text=f"El Dólar Blue subió ${int(bot.venta_blue - bot.intervalo_blue)} a ${int(bot.venta_blue)}.")

            bot.intervalo_blue = bot.venta_blue
            print(f"{now_change} - Raised to ${int(bot.intervalo_blue)} ARS/USD")

    def closing(self) -> None:  # 16.30hs
        """ Output a closing rate exchange message at 16.30 (GMT-3), although the function core() is still running until
            19.00 (GMT-3), so sometimes cierre() might not be the last output of the day.
        """

        if self.non_business_day():
            return

        data: list = self.update_json()
        variation: str = data["variacion"]
        now_open: str = datetime.now().strftime("%d/%m/%y - %H:%M:%S")
        cierre_blue: float = float(data["venta"].replace(",", "."))

        if cierre_blue > bot.apertura_blue:
            self.client.create_tweet(
                text=f"El Dólar Blue cierra la jornada a ${int(cierre_blue)}. En el día subió ${int(cierre_blue - bot.apertura_blue)}, lo que significa una variación de {variation}.")

            print(f"{now_open} - Closed at {cierre_blue} ARS/USD")

        elif cierre_blue < bot.apertura_blue:
            self.client.create_tweet(
                text=f"El Dólar Blue cierra la jornada a ${int(cierre_blue)}. En el día bajó ${int(bot.apertura_blue - cierre_blue)}, lo que significa una variación de {variation}.")

            print(f"{now_open} - Closed at {cierre_blue} ARS/USD")

        else:
            self.client.create_tweet(
                text=f"El Dólar Blue cierra la jornada sin cambios a ${int(cierre_blue)}.")

            print(f"{now_open} - Closed at {int(cierre_blue)} ARS/USD")
