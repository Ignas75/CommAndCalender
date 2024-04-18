import unittest
from events import *
from datetime import datetime, timedelta
import random

sampleInputs = ["Thursday 12:00 E1", "Friday 1pm E2", "2pm Monday E3", "3pm Monday E4 1 hour", "4pm Monday E5 1hour",
                "E6 5pm Monday 60 minutes", "Wed 75mins 9pm E7", "21/12 D1", "Tuesday D2", "22/12/2024 D3"]


def string_shuffle_and_join(event_values):
    random.shuffle(event_values)
    return " ".join(event_values)


class MyTestCase(unittest.TestCase):

    def valid_time_test(self, time):
        match = find_time(time)
        self.assertFalse("Error" in match)
        self.assertEqual(time, match["Match"])

    def test_accepted_valid_events(self):
        event_rejected = False
        successful_values = []
        failed_values = []

        for value in sampleInputs:
            if not process_event(value):
                event_rejected = True
                failed_values.append(value)
            else:
                successful_values.append(value)

        if event_rejected:
            print("\n\nprocess_event Failed on: ")
            for value in failed_values:
                print(value)

        self.assertEqual(event_rejected, False)

    def test_find_time(self):
        self.valid_time_test("24:00")

    def test_am_time(self):
        self.valid_time_test("9am")

    def test_am_time_with_minutes(self):
        self.valid_time_test("10:40am")

    def test_pm_time(self):
        self.valid_time_test("10:50pm")

    def test_accepts_weekdays(self):
        accepted_values = []
        rejected_values = []
        for day in days:
            sample_input = " " + day + " "
            found = find_day(sample_input)
            if "Error" in found:
                rejected_values.append(day)
                print("Test failed on value: " + day)
            else:
                accepted_values.append(day)
        self.assertTrue(len(rejected_values) == 0)

    def event_acceptation_test(self, name, date_string, time_string, hour, minutes=0,
                               duration=None, duration_units=None, date_format="%d/%m/%y"):
        duration_string = ""
        duration_minutes = ""
        if duration is not None:
            duration_string = str(duration) + " " + duration_units
            if duration_units.lower() in ["min", "mins", "minute", "minutes"]:
                duration_minutes = duration
            elif duration_units.lower() in ["hour", "hours", "hr", "hrs"]:
                duration_minutes = duration * 60
            elif duration_units.lower() in ["day", "days"]:
                duration_minutes = duration * 1440
            else:
                print("Missing/Invalid duration units passed to test function")
                duration_string = ""

        event_string_values = [name, date_string, time_string, duration_string]

        event_string = string_shuffle_and_join(event_string_values)

        event = process_event(event_string)
        self.assertTrue("Error" not in event)

        # if duration is unspecified, we test to see if it applies the default event duration correctly
        if duration is None:
            duration = default_duration_minutes
        else:
            # Setting duration after event processing to be in minutes
            duration = duration_minutes

        event_date = event["Start DateTime"].date()
        event_date_string = event_date.strftime(date_format)
        event_hour = event["Start DateTime"].hour
        event_minutes = event["Start DateTime"].minute
        # Bit lazy but, if the start date assertions pass, then it should be "safe" to base the expected end date on
        # the addition of the duration in minutes to the returned event datetime
        expected_end_date = event["Start DateTime"] + timedelta(minutes=duration)

        self.assertEqual(date_string, event_date_string)
        self.assertEqual(hour, event_hour)
        self.assertEqual(minutes, event_minutes)
        self.assertEqual(name, event["Name"])
        self.assertEqual(expected_end_date, event["End DateTime"])

    def event_acceptation_test_day(self, name, day, time_string, hour, minutes=0, duration=None, duration_units=None):

        current_date = datetime.now()
        current_weekday = current_date.weekday()
        current_hour = current_date.hour
        current_minutes = current_date.minute

        if (current_hour > hour or (minutes > current_minutes and hour == current_hour)) and current_weekday == day:
            days_to_add = 7
        else:
            days_to_add = 7 - current_weekday

        expected_date = (current_date + timedelta(days=days_to_add)).date()
        date_string = expected_date.strftime("%d/%m/%y")
        self.event_acceptation_test(name, date_string, time_string, hour, minutes, duration, duration_units)

    def test_accepts_event(self):
        name = "Bowling"
        time = "5pm"
        date = "Monday"
        hour = 17
        self.event_acceptation_test_day(name, date, time, hour)

    def test_accepts_am_event(self):
        name = "Programming 101"
        time = "9am"
        date = "Tuesday"
        hour = 9
        self.event_acceptation_test_day(name, date, time, hour)

    def test_accepts_24_hour_format_event(self):
        name = "Lexing"
        time = "13:00"
        date = "Wednesday"
        hour = 13
        self.event_acceptation_test_day(name, date, time, hour)

    def test_accepts_12am_event(self):
        name = "Rocket League with the boys"
        time = "12am"
        date = "Friday"
        hour = 0
        self.event_acceptation_test_day(name, date, time, hour)

    def test_accepts_12pm_event(self):
        name = "Lunch"
        time = "12pm"
        date = "Friday"
        hour = 12
        self.event_acceptation_test_day(name, date, time, hour)

    def test_accepts_am_time_with_minutes(self):
        name = "Dreaded Alarm"
        time = "6:30 am"
        date = "Saturday"
        hour = 6
        self.event_acceptation_test_day(name, date, time, hour, 30)

    def test_accepts_date_event(self):
        name = "Family Get-Together"
        time = "15:15"
        dt_now = datetime.now()
        day = 21
        month = (dt_now.month + 1) % 12
        hour = 15
        minutes = 15
        event_date = date_construction(month, day, hour)["Datetime"].strftime("%d/%m/%y")
        self.event_acceptation_test(name, event_date, time, hour, minutes)

    def test_accepts_date_long_year(self):
        name = "StarCraft III anniversary"
        time = "21:50"
        day = 3
        dt_now = datetime.now()
        month = (dt_now.month + 1) % 12
        hour = 21
        minutes = 50
        date_format = "%d/%m/%Y"
        event_date = date_construction(month, day, hour)["Datetime"].strftime(date_format)
        self.event_acceptation_test(name, event_date, time, hour, minutes, date_format=date_format)

    def test_accepts_date_next_year(self):
        name = "Pub Quiz"
        time = "8:03PM"
        day = 1
        month = 7
        hour = 20
        minutes = 3
        years_later = 1
        date_format = "%d/%m/%Y"
        event_date = date_construction(month, day, hour, minutes, years_later)["Datetime"].strftime(date_format)
        self.event_acceptation_test(name, event_date, time, hour, minutes, date_format=date_format)

    def test_accepts_hours_duration(self):
        name = "Ranked with the boys"
        time = "6:15Pm"
        date = "Friday"
        hour = 18
        minutes = 15
        duration = 4
        units = "hours"
        self.event_acceptation_test_day(name, date, time, hour, minutes, duration, units)

    def test_accepts_minute_duration(self):
        name = "One Piece Watch Party"
        time = "03:00"
        date = "Sunday"
        hour = 3
        minutes = 0
        duration = 25
        units = "minute"
        self.event_acceptation_test_day(name, date, time, hour, minutes, duration, units)

    def test_accepts_days_duration(self):
        name = "Streamathon"
        time = "20:45"
        date = "Wednesday"
        hour = 20
        minutes = 45
        duration = 2
        units = "days"
        self.event_acceptation_test_day(name, date, time, hour, minutes, duration, units)

    def test_accepts_date_no_year(self):
        name = "Company Drinks"
        time = "4PM"
        day = 28
        month = 11
        hour = 16
        minutes = 0
        date_format = "%d/%m"
        event_date = date_construction(month, day, hour, minutes)["Datetime"].strftime(date_format)
        self.event_acceptation_test(name, event_date, time, hour, minutes, date_format=date_format)

    def test_accepts_09_am(self):
        name = "Malevolent early morning lecture"
        time = "09am"
        date = "Monday"
        hour = 9
        minutes = 0
        self.event_acceptation_test_day(name, date, time, hour, minutes)

    def test_invalid_24_hour_format_hours(self):
        out = process_time("25:00")
        self.assertTrue("Error" in out)
        self.assertEqual("Too many hours", out["Error"])

    def test_invalid_24_hour_format_minutes(self):
        out = process_time("23:78")
        self.assertTrue("Error" in out)
        self.assertEqual("Too many minutes", out["Error"])

    def test_invalid_am_time_hours(self):
        out = process_time("13pm")
        self.assertTrue("Error" in out)
        self.assertEqual("Are you sure? pm time prefix only goes up to 12", out["Error"])

    def test_invalid_am_time_minutes(self):
        out = process_time("12:70am")
        self.assertTrue("Error" in out)
        self.assertEqual("Too many minutes", out["Error"])

    def test_invalid_time_colons(self):
        out = find_time("23:12:60")
        self.assertTrue("Error" in out)
        self.assertEqual("Time has too many colons", out["Error"])

    def test_invalid_am_time_colons(self):
        out = find_time("23:11:60am")
        self.assertTrue("Error" in out)
        self.assertEqual("Time has too many colons", out["Error"])

    def event_rejection_test(self, expected_error, name="", date="", time="", duration=None, units=None):
        event_details = [name, date, time]
        if duration is not None:
            duration_string = str(duration) + units
            event_details.append(duration_string)
        event_string = string_shuffle_and_join(event_details)
        result = process_event(event_string)
        self.assertTrue("Error" in result)
        self.assertEqual(expected_error, result["Error"])

    def test_too_many_days_feb(self):
        name = "Reading Berserk"
        date = "30/02"
        duration = 6
        units = "hours"
        time = "12pm"
        self.event_rejection_test("day is out of range for month February", name, date, time, duration, units)

    def test_missing_event_name(self):
        date = "Saturday"
        time = "12pm"
        expected_error = "Missing Event Name"
        self.event_rejection_test(expected_error, date=date, time=time)

    def test_missing_event_date(self):
        name = "Standup"
        time = "10am"
        expected_error = "No date nor day found"
        self.event_rejection_test(expected_error, name, time=time)

    def test_missing_event_time(self):
        name = "Listen to Rammstein"
        date = "01/01"
        expected_error = "No event start time found"
        self.event_rejection_test(expected_error, name, date)

    def test_too_many_days(self):
        name = "Warhammer 40k Lore Discussion"
        date = "32/08"
        time = "18:01"
        expected_error = "day is out of range for month August"
        self.event_rejection_test(expected_error, name, date, time)

    def test_too_many_hours(self):
        name = "Unlike Pluto Listening Party"
        date = "31/08"
        time = "25:30"
        expected_error = "Too many hours"
        self.event_rejection_test(expected_error, name, date, time)

    def test_reject_non_leap_year_feb_29(self):
        name = "Pigs fly"
        # guaranteeing that the date is not before today by adding 1
        next_year = datetime.now().year + 1
        if next_year % 4 == 0 and not (next_year % 100 == 0):
            year = next_year + 1
        else:
            year = next_year
        date = "29/02/" + str(year)
        time = "7am"
        expected_error = "You entered February 29th on a non-leap year"
        self.event_rejection_test(expected_error, name, date, time)

    def test_accept_leap_year_feb_29(self):
        name = "Eat chili with mushrooms"
        current_year = datetime.now().year
        year = current_year + 1 + (4 - ((current_year + 1) % 4))
        if year % 100 == 0 and year % 400 != 0:
            year = year + 4
        date = "29/02/" + str(year)
        time = "6:30pm"
        hour = 18
        minutes = 30
        self.event_acceptation_test(name, date, time, hour, minutes, date_format="%d/%m/%Y")

    def test_is_today_now(self):
        event = {"Start DateTime": datetime.now()}
        self.assertTrue(is_today(event))

    def test_is_today_lower_bound(self):
        dt_now = datetime.now()
        day = dt_now.day
        month = dt_now.month
        year = dt_now.year
        hour = 0
        minute = 0
        event_dt = datetime(year, month, day, hour, minute)
        event = {"Start DateTime": event_dt}
        self.assertTrue(is_today(event))

    def test_is_today_upper_bound(self):
        dt_now = datetime.now()
        day = dt_now.day
        month = dt_now.month
        year = dt_now.year
        hour = 23
        minute = 59
        event_dt = datetime(year, month, day, hour, minute)
        event = {"Start DateTime": event_dt}
        self.assertTrue(is_today(event))

    def test_is_today_not_yesterday(self):
        dt = datetime.now() - timedelta(days=1)
        event = {"Start DateTime": dt}
        self.assertFalse(is_today(event))

    def test_is_today_not_tomorrow(self):
        dt = datetime.now() + timedelta(days=1)
        event = {"Start DateTime": dt}
        self.assertFalse(is_today(event))

    def test_is_tomorrow_basic(self):
        dt = datetime.now() + timedelta(days=1)
        event = {"Start DateTime": dt}
        self.assertTrue(is_tomorrow(event))

    def test_is_tomorrow_lower_bound(self):
        dt_tomorrow = datetime.now() + timedelta(days=1)
        day = dt_tomorrow.day
        month = dt_tomorrow.month
        year = dt_tomorrow.year
        hour = 0
        minute = 0
        event_dt = datetime(year, month, day, hour, minute)
        event = {"Start DateTime": event_dt}
        self.assertTrue(is_tomorrow(event))

    def test_is_tomorrow_upper_bound(self):
        dt_tomorrow = datetime.now() + timedelta(days=1)
        day = dt_tomorrow.day
        month = dt_tomorrow.month
        year = dt_tomorrow.year
        hour = 23
        minute = 59
        event_dt = datetime(year, month, day, hour, minute)
        event = {"Start DateTime": event_dt}
        self.assertTrue(is_tomorrow(event))

    def test_is_tomorrow_not_today(self):
        dt = datetime.now()
        event = {"Start DateTime": dt}
        self.assertFalse(is_tomorrow(event))

    def test_is_tomorrow_not_overmorrow(self):
        dt = datetime.now() + timedelta(days=2)
        event = {"Start DateTime": dt}
        self.assertFalse(is_tomorrow(event))

    def test_is_this_week_today(self):
        dt = datetime.now()
        event = {"Start DateTime": dt}
        self.assertTrue(is_this_week(event))

    def test_is_this_week_lower_bound(self):
        dt_now = datetime.now()
        days_offset = dt_now.weekday()
        dt_monday = dt_now - timedelta(days=days_offset)
        year = dt_monday.year
        month = dt_monday.month
        day = dt_monday.day
        dt = datetime(year, month, day, 0, 0)
        event = {"Start DateTime": dt}
        self.assertTrue(is_this_week(event))

    def test_is_this_week_upper_bound(self):
        dt_now = datetime.now()
        days_offset = 7 - dt_now.weekday()
        dt_sunday = dt_now + timedelta(days=days_offset)
        year = dt_sunday.year
        month = dt_sunday.month
        day = dt_sunday.day
        dt = datetime(year, month, day, 0, 0, 0, 0) - timedelta(microseconds=1)
        event = {"Start DateTime": dt}
        self.assertTrue(is_this_week(event))

    def test_is_this_week_not_last_week(self):
        last_week_dt = datetime.now() - timedelta(days=7)
        event = {"Start DateTime": last_week_dt}
        self.assertFalse(is_this_week(event))

    def test_is_this_week_not_next_week(self):
        next_week_dt = datetime.now() + timedelta(days=7)
        event = {"Start DateTime": next_week_dt}
        self.assertFalse(is_this_week(event))

    def test_is_this_week_not_last_week_upper_bound(self):
        dt_now = datetime.now()
        days_offset = dt_now.weekday()
        dt_monday = dt_now - timedelta(days=days_offset)
        year = dt_monday.year
        month = dt_monday.month
        day = dt_monday.day
        dt = datetime(year, month, day, 0, 0) - timedelta(microseconds=1)
        event = {"Start DateTime": dt}
        self.assertFalse(is_this_week(event))

    def test_is_this_week_not_next_week_lower_bound(self):
        dt_now = datetime.now()
        days_offset = 7 - dt_now.weekday()
        dt_sunday = dt_now + timedelta(days=days_offset)
        year = dt_sunday.year
        month = dt_sunday.month
        day = dt_sunday.day
        dt = datetime(year, month, day, 0, 0, 0, 0)
        event = {"Start DateTime": dt}
        self.assertFalse(is_this_week(event))

    def test_is_next_week(self):
        dt_next_week = datetime.now() + timedelta(days=7)
        event = {"Start DateTime": dt_next_week}
        self.assertTrue(is_next_week(event))

    def test_is_next_week_lower_bound(self):
        dt_now = datetime.now()
        days_offset = 7 - dt_now.weekday()
        dt_sunday = dt_now + timedelta(days=days_offset)
        year = dt_sunday.year
        month = dt_sunday.month
        day = dt_sunday.day
        dt = datetime(year, month, day, 0, 0, 0, 0)
        event = {"Start DateTime": dt}
        self.assertTrue(is_next_week(event))

    def test_is_next_week_upper_bound(self):
        dt_now = datetime.now()
        days_offset = 14 - dt_now.weekday()
        dt_sunday = dt_now + timedelta(days=days_offset)
        year = dt_sunday.year
        month = dt_sunday.month
        day = dt_sunday.day
        dt = datetime(year, month, day, 0, 0, 0, 0) - timedelta(microseconds=1)
        event = {"Start DateTime": dt}
        self.assertTrue(is_next_week(event))

    def test_is_next_week_not_this_week(self):
        dt = datetime.now()
        event = {"Start DateTime": dt}
        self.assertFalse(is_next_week(event))

    def test_is_next_week_not_this_week_upper_bound(self):
        dt_now = datetime.now()
        days_offset = 7 - dt_now.weekday()
        dt_sunday = dt_now + timedelta(days=days_offset)
        year = dt_sunday.year
        month = dt_sunday.month
        day = dt_sunday.day
        dt = datetime(year, month, day, 0, 0, 0, 0) - timedelta(microseconds=1)
        event = {"Start DateTime": dt}
        self.assertFalse(is_next_week(event))

    def test_is_next_week_not_week_after_next_lower_bound(self):
        dt_now = datetime.now()
        days_offset = 14 - dt_now.weekday()
        dt_sunday = dt_now + timedelta(days=days_offset)
        year = dt_sunday.year
        month = dt_sunday.month
        day = dt_sunday.day
        dt = datetime(year, month, day, 0, 0, 0, 0)
        event = {"Start DateTime": dt}
        self.assertFalse(is_next_week(event))

    def test_is_this_month(self):
        dt = datetime.now()
        event = {"Start DateTime": dt}
        self.assertTrue(is_this_month(event))

    def test_is_this_month_lower_bound(self):
        dt_now = datetime.now()
        year = dt_now.year
        month = dt_now.month
        dt = datetime(year, month, 1, 0, 0, 0, 0)
        event = {"Start DateTime": dt}
        self.assertTrue(is_this_month(event))

    def test_is_this_month_upper_bound(self):
        dt_now = datetime.now()
        year = dt_now.year
        month = dt_now.month
        day = days_in_month(month, year)
        dt = datetime(year, month, day) + timedelta(days=1) - timedelta(microseconds=1)
        event = {"Start DateTime": dt}
        self.assertTrue(is_this_month(event))

    def test_is_this_month_not_last_month_upper_bound(self):
        dt_now = datetime.now()
        year = dt_now.year
        month = dt_now.month
        dt = datetime(year, month, 1, 0, 0, 0, 0) - timedelta(microseconds=1)
        event = {"Start DateTime": dt}
        self.assertFalse(is_this_month(event))

    def test_is_this_month_not_next_month_lower_bound(self):
        dt_now = datetime.now()
        year = dt_now.year
        month = dt_now.month + 1
        if month > 12:
            month = 1
            year = year + 1
        dt = datetime(year, month, 1, 0, 0)
        event = {"Start DateTime": dt}
        self.assertFalse(is_this_month(event))

    def test_is_next_month_lower_bound(self):
        dt_now = datetime.now()
        year = dt_now.year
        month = dt_now.month + 1
        if month > 12:
            month = 1
            year = year + 1
        dt = datetime(year, month, 1, 0, 0)
        event = {"Start DateTime": dt}
        self.assertTrue(is_next_month(event))

    def test_is_next_month_upper_bound(self):
        dt_now = datetime.now()
        year = dt_now.year
        month = dt_now.month + 1
        if month > 12:
            month = 1
            year = year + 1
        day = days_in_month(month, year)
        dt = datetime(year, month, day, 0, 0) + timedelta(days=1) - timedelta(microseconds=1)
        event = {"Start DateTime": dt}
        self.assertTrue(is_next_month(event))

    def test_is_next_month_not_now(self):
        dt = datetime.now()
        event = {"Start DateTime": dt}
        self.assertFalse(is_next_month(event))

    def test_is_next_month_not_this_month_upper_bound(self):
        dt_now = datetime.now()
        year = dt_now.year
        month = dt_now.month + 1
        if month > 12:
            month = 1
            year = year + 1
        dt = datetime(year, month, 1, 0, 0) - timedelta(microseconds=1)
        event = {"Start DateTime": dt}
        self.assertFalse(is_next_month(event))

    def test_is_next_month_not_month_after_next_lower_bound(self):
        dt_now = datetime.now()
        year = dt_now.year
        month = dt_now.month + 2
        if month > 12:
            month = 1
            year = year + 1
        dt = datetime(year, month, 1, 0, 0)
        event = {"Start DateTime": dt}
        self.assertFalse(is_next_month(event))

if __name__ == '__main__':
    unittest.main()
