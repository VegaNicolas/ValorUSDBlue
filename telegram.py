from datetime import datetime
import os
from dotenv import load_dotenv
import telebot
import bot

load_dotenv()


class Telegram(bot.Bot):

    def __init__(self):
        self.channel_id: str = os.getenv("CHANNEL_ID")
        self.telegram_client: telebot.TeleBot = telebot.TeleBot(
            os.getenv("TELEGRAM_TOKEN"))

    def core(self) -> None:
        """ Main output function. Every 5 minutes will update_json() so if it detects a new rate, 
            it will be the output of the bot. It isn't affected by the function arranque() because
            its only triggered when a change is made.
        """

        if datetime.now().strftime("%H:%M:%S") == "16:30:00":
            return

        if self.non_business_day():
            print('non-business-day')
            return

        # now_change: str = datetime.now().strftime("%d/%m/%y - %H:%M:%S")

        if bot.intervalo_blue > bot.venta_blue:
            self.telegram_client.send_message(
                chat_id=self.channel_id, text=f"El Dólar Blue bajó ${int(bot.intervalo_blue - bot.venta_blue)} a ${int(bot.venta_blue)}.")

            # print(f"{now_change} - Went down to ${int(bot.intervalo_blue)} ARS/USD")

        elif bot.intervalo_blue < bot.venta_blue:
            self.telegram_client.send_message(
                chat_id=self.channel_id, text=f"El Dólar Blue subió ${int(bot.venta_blue - bot.intervalo_blue)} a ${int(bot.venta_blue)}.")

            # print(f"{now_change} - Raised to ${int(bot.intervalo_blue)} ARS/USD")

    def closing(self) -> None:  # 16.30hs
        """ Output a closing rate exchange message at 16.30 (GMT-3), although the function core() is still running until
            19.00 (GMT-3), so sometimes cierre() might not be the last output of the day.
        """

        if self.non_business_day():
            return

        data: list = self.update_json()
        variation: str = data["variacion"]
        # now_open: str = datetime.now().strftime("%d/%m/%y - %H:%M:%S")
        cierre_blue: float = float(data["venta"].replace(",", "."))

        if cierre_blue > bot.apertura_blue:
            self.telegram_client.send_message(
                chat_id=self.channel_id, text=f"El Dólar Blue cierra la jornada a ${int(cierre_blue)}. En el día subió ${int(cierre_blue - bot.apertura_blue)}, lo que significa una variación de {variation}.")

            # print(f"{now_open} - Closed at {cierre_blue} ARS/USD")

        elif cierre_blue < bot.apertura_blue:
            self.telegram_client.send_message(
                chat_id=self.channel_id, text=f"El Dólar Blue cierra la jornada a ${int(cierre_blue)}. En el día bajó ${int(bot.apertura_blue - cierre_blue)}, lo que significa una variación de {variation}.")

            # print(f"{now_open} - Closed at {cierre_blue} ARS/USD")

        else:
            self.telegram_client.send_message(
                chat_id=self.channel_id, text=f"El Dólar Blue cierra la jornada sin cambios a ${int(cierre_blue)}.")

            # print(f"{now_open} - Closed at {int(cierre_blue)} ARS/USD")
