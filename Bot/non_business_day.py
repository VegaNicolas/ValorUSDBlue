from Bot.update_json import update_ccl
from datetime import datetime


def non_business_day() -> bool:
    """ This function compares actual datetime with the one it is in the json file (updated rate)
        so the bot gives zero output during weekends and non-business days.
        *Note: this function may be deprecated in the future due to the json doesnt update in those days."""

    data: list = update_ccl()
    fecha_feriado: str = data["fecha"]
    dia_update: list[str] = fecha_feriado.split(" ")

    return dia_update[0] != datetime.now().strftime("%d/%m/%Y")
