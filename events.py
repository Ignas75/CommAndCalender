import re
from datetime import datetime, timedelta
from enum import Enum


class DateFormat(Enum):
    LONG_YEAR = 1
    SHORT_YEAR = 2
    DAY_MONTH = 3
    DAY_OF_WEEK = 4


default_duration = "1 hour"

events = []
# can't include the 3 letter versions because sat and sun could be used in the title, and we wouldn't want to match
# on that
days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]


def store_event(start_dt, end_dt, name):
    events.append({"start_dt": start_dt, "end_dt": end_dt, "name": name})


def find_duration(user_input):
    pattern = r"[1-6]?[0-9] (min|mins|minutes|hours?|day)"
    return re.search(pattern, user_input)


def find_day(user_input):
    no_year_date_format = r"[0-3]?[0-9]/[0-1][0-9]"
    short_year_date_format = r"[0-3]?[0-9]/[0-1][0-9]/[0-9]{2}"
    long_year_date_format = r"[0-3]?[0-9]/[0-1][0-9]/20[0-9]{2}"
    lower_str = user_input.lower()

    match = re.search(long_year_date_format, lower_str)
    if match is not None:
        return {"Date": match.group(), "Format": "long year"}

    match = re.search(short_year_date_format, lower_str)
    if match is not None:
        return {"Date": match.group(), "Format": "short year"}

    match = re.search(no_year_date_format, lower_str)
    if match is not None:
        return {"Date": match.group(), "Format": "day month"}

    for day in days:
        if day in lower_str:
            return {"Day": day}

    return {"Error": "No date nor day found"}


def find_time(user_input):
    if not re.search(":[0-9]*:[0-9]*(am|pm)?", user_input) is None:
        return {"Error": "Time has too many colons"}

    am_pm_time_pattern = r"[0-1]?[0-9]?:?[0-5]?[0-9]\s*(am|pm)"
    out = re.search(am_pm_time_pattern, user_input)
    if not (out is None):
        return {"Match:": out.group()}

    twenty_four_hour_time_pattern = r"[0-2]?[0-9]:[0-5][0-9]"
    out = re.search(twenty_four_hour_time_pattern, user_input)
    if out is None:
        return {"Error": "no time found"}
    return {"Match": out.group()}


def process_time(time):
    hours = 0
    minutes = 0
    am_time = False
    pm_time = False

    if "am" in time:
        am_time = True
        time = time.replace("am", "")

    elif "pm" in time:
        pm_time = True
        hours = 12
        time = time.replace("pm", "")

    if ":" in time:
        time_components = time.split(":")
        hour_component = time_components[0]
        if am_time and hour_component == 12:
            hours = 0
        elif not (hour_component == 12 and pm_time):
            hours += int(time_components[0])
            if hours == 24:
                hours = 0

        minutes = int(time_components[1])
    else:
        # adding in case it's pm time
        hours = hours + int(time)

    if am_time and hours > 11:
        return {"Error": "Are you sure? am time prefix only goes up to 12"}
    elif pm_time and hours > 23:
        return {"Error": "Are you sure? pm time prefix only goes up to 12"}

    if hours > 24:
        return {"Error": "Too many hours"}

    if minutes > 59:
        return {"Error": "Too many minutes"}

    return {"Hours": hours, "Minutes": minutes}


def process_event(user_input):
    time_found = find_time(user_input)
    if "Error" in time_found:
        return time_found["Error"]

    processed_time = process_time(time_found.group())
    if "Error" in processed_time:
        return processed_time["Error"]
    hours = processed_time["hours"]
    minutes = processed_time["minutes"]

    day = find_day(user_input)
    if "Error" in day:
        return day["Error"]
    elif "Day" in day:
        days_offset = 0
        day_int = days.index(day["Day"])
        current_weekday_int = datetime.now().date().weekday()
        if day_int == current_weekday_int:
            if hours > datetime.now().hour or (hours == datetime.now().hour and minutes >= datetime.now().minute):
                days_offset = 7
        else:
            days_offset = (day_int - current_weekday_int) % 7
        current_date = datetime.now()
        event_date = current_date + timedelta(days=days_offset)
        event_day = event_date.day
        event_month = event_date.month
        event_year = event_date.year
        event_date = datetime(year=event_year, month=event_month, day=event_day, hour=hours, minute=minutes)
        match day["Format"]:
            case "short year":
                print("TEMP")
    print(day)
    print(processed_time)
    duration = find_duration(user_input)
    if duration is None:
        duration = 60

    if user_input is not None:
        event = {"date_and_time": datetime.now(), "name": "Bowling", "duration": default_duration}
        return event
    return None
