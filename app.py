from flask import Flask
from threading import Thread
from Bot.global_variables import price

app = Flask('')

@app.route('/')

def home():
    return f"I'm alive - {price.intervalo_blue}"


def run():
  app.run(host='0.0.0.0', port=8000)


def keep_alive():  
    t = Thread(target=run)
    t.start()