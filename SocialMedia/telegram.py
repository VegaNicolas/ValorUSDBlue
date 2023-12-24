from datetime import datetime
import os
import telebot
from Bot.global_variables import price
from Bot.non_business_day import non_business_day
from Bot.update_json import update_json


class Telegram():

    def __init__(self):
        self.channel_id: str = os.environ.get("CHANNEL_ID")
        self.telegram_client: telebot.TeleBot = telebot.TeleBot(
            os.environ.get("TELEGRAM_TOKEN"))

    def core(self) -> None:
        """ Main output function. Every 5 minutes will update_json() so if it detects a new rate, 
            it will be the output of the bot. It isn't affected by the function arranque() because
            its only triggered when a change is made.
        """

        if datetime.now().strftime("%H:%M") == "16:30":
            return

        now_change: str = datetime.now().strftime("%d/%m/%y - %H:%M:%S")
        price.intervalo_blue = int(price.intervalo_blue)
        price.venta_blue = int(price.venta_blue)

        if price.intervalo_blue > price.venta_blue:
            self.telegram_client.send_message(
                chat_id=self.channel_id, text=f"El Dólar Blue bajó ${int(price.intervalo_blue - price.venta_blue)} a ${int(price.venta_blue)}.")

            print(f"{now_change} - Went down to ${int(price.venta_blue)} ARS/USD")

        elif price.intervalo_blue < price.venta_blue:
            self.telegram_client.send_message(
                chat_id=self.channel_id, text=f"El Dólar Blue subió ${int(price.venta_blue - price.intervalo_blue)} a ${int(price.venta_blue)}.")

            print(f"{now_change} - Raised to ${int(price.venta_blue)} ARS/USD")

    def closing(self) -> None:  # 16.30hs
        """ Output a closing rate exchange message at 16.30 (GMT-3), although the function core() is still running until
            19.00 (GMT-3), so sometimes cierre() might not be the last output of the day.
        """

        if non_business_day():
            return

        price.intervalo_blue = int(price.intervalo_blue)
        price.venta_blue = int(price.venta_blue)

        data: list = update_json()
        variation: str = data["variacion"]
        now_open: str = datetime.now().strftime("%d/%m/%y - %H:%M:%S")
        cierre_blue: float = float(data["venta"].replace(",", "."))

        if cierre_blue > price.apertura_blue:
            self.telegram_client.send_message(
                chat_id=self.channel_id, text=f"El Dólar Blue cierra la jornada a ${int(cierre_blue)}. En el día subió ${int(cierre_blue - price.apertura_blue)}, lo que significa una variación de {variation}.")

            print(f"{now_open} - Closed at {cierre_blue} ARS/USD")

        elif cierre_blue < price.apertura_blue:
            self.telegram_client.send_message(
                chat_id=self.channel_id, text=f"El Dólar Blue cierra la jornada a ${int(cierre_blue)}. En el día bajó ${int(price.apertura_blue - cierre_blue)}, lo que significa una variación de {variation}.")

            print(f"{now_open} - Closed at {cierre_blue} ARS/USD")

        else:
            self.telegram_client.send_message(
                chat_id=self.channel_id, text=f"El Dólar Blue cierra la jornada sin cambios a ${int(cierre_blue)}.")

            print(f"{now_open} - Closed at {int(cierre_blue)} ARS/USD")


telegram_client = Telegram()
