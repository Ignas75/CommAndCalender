import re
from datetime import datetime, timedelta

default_duration = "1 hour"


def store_event(date_and_time, name):
    return {"date_and_time": date_and_time, "name": name}


def process_event(user_input):
    time_found = find_time(user_input)
    processed_time = process_time(time_found.group())
    if "Error" in processed_time:
        return processed_time["Error"]

    day = find_day(user_input)

    if user_input is not None:
        return {"date_and_time": datetime.now(), "name": "Bowling", "duration": default_duration}
    return None


def find_duration(user_input):
    pattern = r"[1-6]?[0-9] (min|mins|minutes|hours?|day)"
    return re.search(pattern, user_input)


def find_day(user_input):
    days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
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
        hours = int(time)

    if (am_time or pm_time) and hours > 12:
        return {"Error": "Are you sure? am and pm time only goes up to 12 as a prefix"}

    if hours > 24:
        return {"Error": "Too many hours"}

    if minutes > 59:
        return {"Error": "Too many minutes"}

    return {"hours": hours, "minutes": minutes}


def find_time(user_input):
    if not re.search(":[0-9]*:[0-9]*(am|pm)?", user_input) is None:
        return {"Error": "Time has too many colons"}

    am_pm_time_pattern = r"[0-1]?[0-9]?:?[0-5]?[0-9]\s*(am|pm)"
    out = re.search(am_pm_time_pattern, user_input)
    if not (out is None):
        return out

    twenty_four_hour_time_pattern = r"[0-2]?[0-9]:[0-5][0-9]"
    out = re.search(twenty_four_hour_time_pattern, user_input)
    return out
