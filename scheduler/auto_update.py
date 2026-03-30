import schedule
import time
from data_collector import collect_year
from config import init_gee
init_gee()


def job():
    collect_year(2024)

schedule.every().day.do(job)

while True:
    schedule.run_pending()
    time.sleep(60)
