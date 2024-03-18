import json
import os
import requests
from dotenv import load_dotenv

load_dotenv()


def update_json() -> dict:
    """ Takes an URL as a parameter (unable due to schedule library #TODO, so hardcoded) which leads
        to a json in Ámbito Financiero webpage (Argentinian news media that follows the informal ARS/USD rate)
        which is the source of the information used in every bot done by me."""

    URL: str = os.environ.get("URL")
    result: str = requests.get(URL).text
    datos: list = json.loads(result)
    return datos


def update_ccl() -> dict:
    '''Same function as update_json with the difference it uses CCL link because of a typo in
        the main link's date'''

    URL: str = 'https://mercados.ambito.com//dolarrava/cl/variacion'
    result: str = requests.get(URL).text
    datos: list = json.loads(result)
    return datos
