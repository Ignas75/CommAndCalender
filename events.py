import re
from datetime import datetime, timedelta
from enum import Enum


class DateFormat(Enum):
    LONG_YEAR = 1
    SHORT_YEAR = 2
    DAY_MONTH = 3
    DAY_OF_WEEK = 4


default_duration_minutes = 60

events = []
# can't include the 3 letter versions because sat and sun could be used in the title, and we wouldn't want to match
# on that
days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]


def store_event(start_dt, end_dt, name):
    events.append({"start_dt": start_dt, "end_dt": end_dt, "name": name})


def find_duration(user_input):
    pattern = r"[1-6]?[0-9]/s*(mins?|minutes?|hours?|day)"
    match = re.search(pattern, user_input)
    if match is None:
        return None
    return match.group()


def find_day(user_input):
    no_year_date_format = r"[0-3]?[0-9]/[0-1][0-9]"
    short_year_date_format = r"[0-3]?[0-9]/[0-1][0-9]/[0-9]{2}"
    long_year_date_format = r"[0-3]?[0-9]/[0-1][0-9]/20[0-9]{2}"
    lower_str = user_input.lower()

    match = re.search(long_year_date_format, lower_str)
    if match is not None:
        return {"Date": match.group(), "Format": DateFormat.LONG_YEAR}

    match = re.search(short_year_date_format, lower_str)
    if match is not None:
        return {"Date": match.group(), "Format": DateFormat.SHORT_YEAR}

    match = re.search(no_year_date_format, lower_str)
    if match is not None:
        return {"Date": match.group(), "Format": DateFormat.DAY_MONTH}

    for day in days:
        if day in lower_str:
            return {"Day": day, "Format": DateFormat.DAY_OF_WEEK, "Substring Index": lower_str.index(day)}

    return {"Error": "No date nor day found"}


def find_time(user_input):
    if not re.search(":[0-9]*:[0-9]*(am|pm)?", user_input) is None:
        return {"Error": "Time has too many colons"}

    am_pm_time_pattern = r"[0-1]?[0-9]?:?[0-5]?[0-9]\s*([aApP][mM])"
    out = re.search(am_pm_time_pattern, user_input)
    if not (out is None):
        return {"Match": out.group()}

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

    time = time.lower()
    if "am" in time:
        am_time = True
        time = time.replace("am", "")

    elif "pm" in time:
        pm_time = True
        hours = 12
        time = time.replace("pm", "")

    if ":" in time:
        time_components = (time.strip()).split(":")
        hour_component = time_components[0]
        if am_time and hour_component == 12:
            hours = 0
        elif pm_time and not hour_component == 12:
            hours += int(time_components[0])
        else:
            hours = int(hour_component)
        minutes = int(time_components[1])

    if am_time and hours > 11:
        return {"Error": "Are you sure? am time prefix only goes up to 12"}
    elif pm_time and hours > 23:
        return {"Error": "Are you sure? pm time prefix only goes up to 12"}

    if hours > 24:
        return {"Error": "Too many hours"}

    if minutes > 59:
        return {"Error": "Too many minutes"}

    return {"Hours": hours, "Minutes": minutes}


def remove_substring(string, remove):
    return string.replace(remove, "").strip()


# used for figuring out a valid date based on given time parameters
def date_construction(month, day, hour=0, minute=0, extra_years=0):
    current_datetime = datetime.now()
    current_date = current_datetime.date()
    year = current_date.year + extra_years
    if extra_years != 0:
        if month < current_date.month:
            year = year + 1
        elif month == current_date.month:
            if day < current_date.day:
                year = year + 1
            elif day == current_date.day:
                if hour < current_datetime.hour:
                    year += 1
                elif hour == current_datetime.hour and minute <= current_datetime.minute:
                    year += 1
    return datetime(year=year, month=month, day=day, hour=hour, minute=minute)


def process_event(user_input):
    event_datetime = None
    time_found = find_time(user_input)
    if "Error" in time_found:
        return time_found["Error"]
    processed_time = process_time(time_found["Match"])
    user_input = remove_substring(user_input, time_found["Match"])

    if "Error" in processed_time:
        return processed_time["Error"]
    hours = processed_time["Hours"]
    minutes = processed_time["Minutes"]

    day = find_day(user_input)
    if "Error" in day:
        return day["Error"]
    if day["Format"] != DateFormat.DAY_OF_WEEK:
        user_input = remove_substring(user_input, day["Date"])
    else:
        substring_length = len(day["Day"])
        index_of_substring = day["Substring Index"]
        user_input = (user_input[0: index_of_substring] +
                      user_input[(index_of_substring + substring_length): len(user_input)])
    event_duration = find_duration(user_input)

    event_name = user_input.strip()

    match day["Format"]:
        case DateFormat.DAY_OF_WEEK:
            days_offset = 0
            day_int = days.index(day["Day"])
            current_weekday_int = datetime.now().date().weekday()
            if day_int == current_weekday_int:
                if hours > datetime.now().hour or (hours == datetime.now().hour and minutes >= datetime.now().minute):
                    days_offset = 7
            else:
                days_offset = (day_int - current_weekday_int) % 7
            current_date = datetime.now()
            datetime_of_event = current_date + timedelta(days=days_offset)
            event_day = datetime_of_event.day
            event_month = datetime_of_event.month
            event_year = datetime_of_event.year

        case DateFormat.LONG_YEAR:
            date_components = day["Date"].split("/")
            event_day = int(date_components[0])
            event_month = int(date_components[1])
            event_year = int(date_components[2])

        case DateFormat.SHORT_YEAR:
            date_components = day["Date"].split("/")
            event_day = int(date_components[0])
            event_month = int(date_components[1])
            event_year = int("20" + date_components[2])

        case DateFormat.DAY_MONTH:
            date_components = day["Date"].split("/")
            event_day = int(date_components[0])
            event_month = int(date_components[1])

    if event_datetime is None:
        event_datetime = datetime(year=event_year, month=event_month, day=event_day, hour=hours, minute=minutes)
    if event_duration is None:
        event_duration = default_duration_minutes
    event_end_datetime = event_datetime + timedelta(minutes=event_duration)

    return {"Start DateTime": event_datetime, "End DateTime": event_end_datetime, "Name": event_name}
