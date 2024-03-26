import unittest
from events import *
from datetime import datetime, timedelta


sampleInputs = ["Thursday 12:00 E1", "Friday 1pm E2", "2pm Monday E3", "3pm Monday E4 1 hour", "4pm Monday E5 1hour",
                "E6 5pm Monday 60 minutes", "Wed 75mins 9pm E7", "21/12 D1", "Tuesday D2", "22/12/2024 D3"]


class MyTestCase(unittest.TestCase):

    def valid_time_test(self, time):
        match = find_time(time)
        self.assertFalse("Error" in match)
        self.assertEqual(time, match["Match"])

    # TODO: fix
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
        self.assertEqual("Are you sure? am and pm time only goes up to 12 as a prefix", out["Error"])

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

    def event_acceptation_test_template(self, event_string, name, date, hour, minutes, duration):
        event = process_event(event_string)
        self.assertIsNotNone(event)

        # Setting empty duration after processing the event, for testing. To see if the default duration is correctly
        # applied
        if duration.strip() == "":
            duration = default_duration
        event_date = event["date_and_time"].date()
        event_date_string = event_date.strftime("%d/%m/%y")
        event_hour = event["date_and_time"].hour
        event_minutes = event["date_and_time"].minute
        self.assertEqual(date, event_date_string)
        self.assertEqual(hour, event_hour)
        self.assertEqual(minutes, event_minutes)
        self.assertEqual(name, event["name"])
        self.assertEqual(duration, event["duration"])

    def event_acceptation_date(self, name, time_string, date, hour, minutes=0, duration=""):
        event_string = name + " " + time_string + " " + date + " " + duration
        self.event_acceptation_test_template(event_string, name, date, hour, minutes, duration)

    def event_acceptation_day(self, name, time_string, day, hour, minutes=0, duration=""):
        event_string = name + " " + time_string + " " + day + " " + duration

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
        self.event_acceptation_test_template(name, event_string, date_string, hour, minutes, duration)

    def test_accepts_event(self):
        name = "Bowling"
        time = "5pm"
        date = "Monday"
        hour = 17
        self.event_acceptation_day(name, time, date, hour)

    def test_missing_event_name(self):
        self.assertEqual(process_event("Saturday 12pm"), "Missing Event Name")

    def test_missing_event_date(self):
        self.assertEqual(process_event("Standup 10am"), "Missing Event Day")


if __name__ == '__main__':
    unittest.main()
