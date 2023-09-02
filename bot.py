from datetime import datetime, timedelta
import json
import os
import requests
from dotenv import load_dotenv
import sqlite3

load_dotenv()

# Global Variables
intervalo_blue: float = 0  # Precio del intervalo anterior
apertura_blue: float = 0
venta_blue: float = 0
start: str = datetime.now().replace(hour=8, minute=55, second=0)


class Bot():

    def update_json(self) -> dict:
        """ Takes an URL as a parameter (unable due to schedule library #TODO, so hardcoded) which leads
            to a json in Ámbito Financiero webpage (Argentinian news media that follows the informal ARS/USD rate)
            which is the source of the information used in every bot done by me."""

        URL: str = os.getenv("URL")
        result: str = requests.get(URL).text
        datos: list = json.loads(result)
        return datos

    def database_price(self):

        def get_data(query: str) -> any:
            connection = sqlite3.connect('Dollar.db')
            cursor = connection.cursor()
            cursor.execute(query)
            data = cursor.fetchone()
            return data[0]

        dbprice = float(get_data(
            query='SELECT Price FROM Rates'))

        return dbprice

    def update_database(self):
        connection = sqlite3.connect('Dollar.db')
        cursor = connection.cursor()

        data = self.update_json()
        commit = [data["venta"].replace(",", "."),
                  data["fecha"],
                  data["variacion"],
                  data["valor_cierre_ant"].replace(",", ".")]

        cursor.execute(
            'UPDATE Rates SET Price = ?, Last_Update = ?, Variation = ?, Last_Close = ?', commit)
        connection.commit()

    def update_price(self):
        global intervalo_blue
        global venta_blue

        intervalo_blue = self.database_price()
        venta_blue = self.get_sell_price()

    def startup(self) -> None:
        """ QoL function which is called only when the service is restarted. It allows better
            testing results and even to commit changes in production on a weekday. The function settles
            the two main variables in the script (apertura_blue and intervalo_blue) which are not saved
            when the bot is down, so it 'restarts' automatically making an outage to not affect its normal
            output."""
        global apertura_blue

        apertura_blue = self.get_opening_price()
        now: str = datetime.now().strftime("%d/%m/%y - %H:%M:%S")
        print(f"{now} - Arranca la jornada. Dólar Blue abrió en ${int(apertura_blue)}.")

    def non_business_day(self) -> bool:
        """ This function compares actual datetime with the one it is in the json file (updated rate)
            so the bot gives zero output during weekends and non-business days.
            *Note: this function may be deprecated in the future due to the json doesnt update in those days."""

        data: list = self.update_json()
        fecha_feriado: str = data["fecha"]
        dia_update: list[str] = fecha_feriado.split(" ")

        return dia_update[0] != datetime.now().strftime("%d/%m/%Y")

    def opening(self) -> None:  # 11.05hs
        """ Internal function which updates the apertura_blue variable if been outaged during night.
        """
        now_open: str = datetime.now().strftime("%d/%m/%y - %H:%M:%S")
        apertura_blue = self.get_opening_price()
        print(f"{now_open} - El dólar abre a ${apertura_blue}.")

    def get_sell_price(self) -> float:
        ''' Updates the price for intervalo_blue'''
        data: list = self.update_json()
        return float(data["venta"].replace(",", "."))

    def get_opening_price(self) -> float:
        '''Updates the price for apertura_blue'''
        data: list = self.update_json()
        return float(data["valor_cierre_ant"].replace(",", "."))

    def update_dates(self) -> None:  # 19.01hs
        """ This updates the start variable at 19.01 (GMT-3) and sums 24hours in order to resume bot's functionality the next day 
        at 8.55 (GMT-3). In the future, this variable may be modified to 11.00 (GMT-3) to be more optimized."""
        global start

        start += timedelta(days=1)
        now_change: str = datetime.now().strftime("%d/%m/%y - %H:%M:%S")
        print(f"{'-'*36}\n{now_change} - Fechas actualizadas\n{'-'*36}")
