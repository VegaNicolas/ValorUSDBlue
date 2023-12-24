import sqlite3
from Bot.update_json import update_json
from Bot.global_variables import price


def database_price():
    connection = sqlite3.connect('Dollar.db')
    cursor = connection.cursor()
    cursor.execute('SELECT Price FROM Rates')
    data = cursor.fetchone()
    return data[0]


def update_database():
    connection = sqlite3.connect('Dollar.db')
    cursor = connection.cursor()
    data = update_json()
    variation: str = data["variacion"]
    date = data["fecha"]

    commit = [data["venta"].replace(",", "."),
              date,
              variation,
              data["valor_cierre_ant"].replace(",", ".")]

    cursor.execute(
        'UPDATE Rates SET Price = ?, Last_Update = ?, Variation = ?, Last_Close = ?', commit)
    connection.commit()


def update_price():
    data = update_json()

    price.intervalo_blue = database_price()
    price.venta_blue = float(data["venta"].replace(",", "."))
