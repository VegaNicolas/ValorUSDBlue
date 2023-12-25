from datetime import timedelta, datetime

start: str = datetime.now().replace(hour=11, minute=55, second=0)


def update_dates() -> None:  # 19.01hs
    """ This updates the start variable at 19.01 (GMT-3) and sums 24hours in order to resume bot's functionality the next day 
    at 8.55 (GMT-3). In the future, this variable may be modified to 11.00 (GMT-3) to be more optimized."""
    global start
    start += timedelta(days=1)
    print(f"{'-'*36}\nFechas actualizadas\n{'-'*36}")
