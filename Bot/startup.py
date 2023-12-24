from Bot.update_json import update_json
from Bot.global_variables import price


def startup() -> None:
    """ QoL function which is called only when the service is restarted. It allows better
        testing results and even to commit changes in production on a weekday. The function settles
        the two main variables in the script (apertura_blue and intervalo_blue) which are not saved
        when the bot is down, so it 'restarts' automatically making an outage to not affect its normal
        output."""
    data: dict = update_json()
    price.apertura_blue: int = float(
        data["valor_cierre_ant"].replace(",", "."))
    print(f"Rate opens at ${int(price.apertura_blue)}.")
