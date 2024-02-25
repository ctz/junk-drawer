import datetime
from os import path
import time

import alphaess


def date(day, y):
    return datetime.datetime.strptime("%d-%03d" % (y, day), "%Y-%j").date()


def days_in_year(y):
    for day in range(1, 367):
        d = date(day, y)

        if d.year == y:
            yield d


for d in days_in_year(2023):
    o = type("Object", (), dict(date=d, format="json"))()

    filename = "output/%d/%d-%02d-%02d.json" % (d.year, d.year, d.month, d.day)

    if path.exists(filename):
        print("Already have", d)
        continue

    with open(filename, "w") as f:
        print("Fetching", d)
        alphaess.get_daily_power_histogram(o, output=f)
        time.sleep(2)
