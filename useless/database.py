import sqlite3
import os
import requests
import json


def createdb() -> None:
    connection = sqlite3.connect('Dollar.db')
    cursor = connection.cursor()

    cursor.execute(
        '''CREATE TABLE IF NOT EXISTS Rates(ID VARCHAR(30) UNIQUE PRIMARY KEY,
        Price DOUBLE, Last_Update VARCHAR(50), Variation VARCHAR(50), Last_Close DOUBLE)''')

    connection.commit()


def dolarblue() -> None:
    connection = sqlite3.connect('Dollar.db')
    cursor = connection.cursor()

    URL: str = os.getenv("URL")
    result: str = requests.get(URL).text
    data: list = json.loads(result)

    commit = ['Dólar Blue',
              data["venta"].replace(",", "."),
              data["fecha"],
              data["variacion"],
              data["valor_cierre_ant"].replace(",", ".")]

    cursor.execute('INSERT INTO Rates VALUES(?, ?, ?, ?, ?)', commit)
    connection.commit()

    # cursor.execute('UPDATE Rates SET ID = ?, Price = ?, Last_Update = ?, Variation = ?, Last_Close = ?', )


def get_data(query: str) -> any:
    connection = sqlite3.connect('Dollar.db')
    cursor = connection.cursor()
    cursor.execute(query)
    data = cursor.fetchone()
    return data


queries = ['SELECT Price FROM Rates WHERE ID = "Dólar Blue"', 'SELECT Last_Close FROM Rates WHERE ID = "Dólar Blue"',
           'SELECT Last_Update FROM Rates WHERE ID = "Dólar Blue"',
           'SELECT Variation FROM Rates WHERE ID = "Dólar Blue"']


def changeprice():
    connection = sqlite3.connect('Dollar.db')
    cursor = connection.cursor()
    cursor.execute('UPDATE Rates SET Price = 710 WHERE ID = "Dólar Blue"')
    connection.commit()


print(get_data(query='SELECT * FROM Rates'))

# changeprice()
