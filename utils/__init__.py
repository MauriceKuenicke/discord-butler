import datetime
import google_doc
import utils.embeds


def get_next_weekday_date(d, weekday):
    """weekday : 0 = Monday, 1=Tuesday, 2=Wednesday...   """
    days_ahead = weekday - d.weekday()
    if days_ahead < 0:  # Target day already happened this week
        days_ahead += 7
    elif days_ahead == 0:
        days_ahead = 0
    return d + datetime.timedelta(days_ahead)


def calculate_timedelta(weekday, hour, minute):
    time_now = datetime.datetime.now()
    next_date = get_next_weekday_date(time_now.date(), weekday)
    time_goal = datetime.datetime(
        next_date.year, next_date.month, next_date.day, hour, minute, 0, 0)
    delta = time_goal - time_now
    return delta.total_seconds()
