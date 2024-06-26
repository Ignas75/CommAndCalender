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


def find_duration(user_input):
    pattern = r"[1-6]?[0-9]\s*(minutes?|mins?|hrs?|hours?|days?)"
    match = re.search(pattern, user_input)
    if match is None:
        return None
    return match.group()


def process_duration(duration_string):
    minute_multiplier = 0
    unit_string = ""

    for spelling in ["minutes", "minute", "mins", "min"]:
        if spelling in duration_string:
            minute_multiplier = 1
            unit_string = spelling
            break

    if unit_string == "":
        for spelling in ["hours", "hour", "hrs", "hr"]:
            if spelling in duration_string:
                minute_multiplier = 60
                unit_string = spelling
                break

    if unit_string == "":
        for spelling in ["days", "day"]:
            if spelling in duration_string:
                minute_multiplier = 1440
                unit_string = spelling
                break
    duration_amount_string = duration_string.replace(unit_string, "").strip()
    duration_amount = int(duration_amount_string)
    return duration_amount * minute_multiplier


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
        return {"Error": "No event start time found"}
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
        hour_component = int(time_components[0])
        if not (hour_component == 12 and (am_time or pm_time)):
            hours = hours + hour_component
        minutes = int(time_components[1])
    else:
        if int(time) != 12:
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


def remove_substring(string, remove):
    return string.replace(remove, "").strip()


def date_validation_and_construction(year, month, day, hour=0, minute=0):
    current_datetime = datetime.now()
    current_date = current_datetime.date()
    if year < current_date.year:
        return {"Error": "Cannot create an event for a year that has already passed"}
    elif year == current_date.year:
        if month < current_date.month:
            return {"Error": "Cannot create an event for a month that has already passed"}
        elif month == current_date.month:
            if day < current_date.day:
                return {"Error": "Cannot create and event for day that has already passed"}

    if day == 29 and month == 2:
        if year % 4 != 0 and not (year % 100 == 0 and year % 400 != 0):
            return {"Error": "You entered February 29th on a non-leap year"}
    try:
        event_datetime = datetime(year=year, month=month, day=day, hour=hour, minute=minute)
    except ValueError as v:
        if v.__str__() == "day is out of range for month":
            month_name = datetime(year=year, month=month, day=1).strftime("%B")
            return {"Error": v.__str__() + " " + month_name}
        else:
            return {"Error": v}
    return {"Datetime": event_datetime}


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
    try:
        event_datetime = datetime(year=year, month=month, day=day, hour=hour, minute=minute)
    except ValueError as v:
        if v.__str__() == "day is out of range for month":
            month_name = datetime(year=year, month=month, day=1).strftime("%B")
            return {"Error": v.__str__() + " " + month_name}
        else:
            return {"Error": v}
    return {"Datetime": event_datetime}


def process_event(user_input):
    event_datetime = None
    time_found = find_time(user_input)
    if "Error" in time_found:
        # time_found is already a dict containing an error at this point, can pass along the error upwards
        return time_found
    processed_time = process_time(time_found["Match"])
    user_input = remove_substring(user_input, time_found["Match"])

    if "Error" in processed_time:
        # processed_time is already a dictionary containing error, can just pass along
        return processed_time
    hours = processed_time["Hours"]
    minutes = processed_time["Minutes"]

    day = find_day(user_input)
    if "Error" in day:
        # day is already a dict containing an error at this point, can pass the error upwards
        return day
    if day["Format"] != DateFormat.DAY_OF_WEEK:
        user_input = remove_substring(user_input, day["Date"])
    else:
        substring_length = len(day["Day"])
        index_of_substring = day["Substring Index"]
        user_input = (user_input[0: index_of_substring] +
                      user_input[(index_of_substring + substring_length): len(user_input)])
    event_duration_string = find_duration(user_input)
    if event_duration_string is not None:
        user_input = user_input.replace(event_duration_string, "").strip()
        event_duration_minutes = process_duration(event_duration_string)

    event_name = user_input.strip()
    if event_name == "":
        return {"Error": "Missing Event Name"}

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
            date = date_construction(event_month, event_day, hours, minutes)
            if "Error" in date:
                # date already contains an error, can just pass it along
                return date
            else:
                event_year = date["Datetime"].year
    if event_datetime is None:
        potential_date = date_validation_and_construction(event_year, event_month, event_day, hours, minutes)
        if "Error" in potential_date:
            return potential_date
        else:
            event_datetime = potential_date["Datetime"]
    if event_duration_string is None:
        event_duration_minutes = default_duration_minutes
    event_end_datetime = event_datetime + timedelta(minutes=event_duration_minutes)
    return {"Start DateTime": event_datetime, "End DateTime": event_end_datetime, "Name": event_name}


def detect_timezone():
    return datetime.now().astimezone().tzinfo
