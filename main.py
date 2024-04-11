from events import process_event
import os
from datetime import datetime
from icalendar import Calendar, Event

events = []
folder_name = "data"
absolute_path = os.path.dirname(__file__)
data_folder_path = os.path.join(absolute_path, folder_name)

data_file_path = "./data/events.txt"
datetime_display_format = "%d/%m/%Y %H:%M"


def event_has_started(event):
    return event["Start DateTime"] <= datetime.now()


def event_text(event):
    event_name = event["Name"]
    event_start_time = event["Start DateTime"].strftime(datetime_display_format)
    event_end_time = event["End DateTime"].strftime(datetime_display_format)
    return event_name + ":\n" + "Starting: " + event_start_time + "\nEnding: " + event_end_time + "\n\n"


def save_events():
    if not os.path.exists(data_folder_path):
        os.mkdir(data_folder_path)

    file = open(data_file_path, "w")
    for event in events:
        line_strs = [event["Name"], event["Start DateTime"].strftime(datetime_display_format),
                     event["End DateTime"].strftime(datetime_display_format)]
        file.write(",".join(line_strs) + "\n")
    file.close()


def delete_past_events():
    print("We would delete the following events:\n\n")
    events_to_delete_indices = []
    for i in range(0, len(events)):
        event = events[i]
        if event_has_started(event):
            events_to_delete_indices.append(i)
        else:
            print(event_text(event))

    prompt = "\nAre you sure you want to delete all of the above?"
    options = ["yes", "y", "no", "n"]
    choice = generic_menu(prompt, options)
    if choice in ["yes", "y"]:
        # deleting from the end to keep the process "clean" and not delete other events accidentally
        events_to_delete_indices.reverse()
        for i in events_to_delete_indices:
            events.pop(i)
        # making changes permanent
        save_events()


def convert_events_to_calendar(event_list, ignore_past_events=True):
    cal = Calendar()
    for event in event_list:
        if not (ignore_past_events and event_has_started(event)):
            cal_event = Event()
            cal_event.add('summary', event["Name"])
            cal_event.add('dtstart', event["Start DateTime"])
            cal_event.add('dtend', event["End DateTime"])
            cal.add_component(cal_event)
    return cal


def has_passed_event():
    for event in events:
        if event_has_started(event):
            return True
    return False


def has_upcoming_event():
    for event in events:
        if not event_has_started(event):
            return True
    return False


def generic_menu(prompt, options):
    valid_input = False
    choice = None
    prompt_with_options_text = prompt + "\nPlease enter one of (" + ",".join(options) + "): "
    while not valid_input:
        choice = input(prompt_with_options_text).lower()
        if choice in options:
            valid_input = True
        else:
            print("You entered: '" + choice + "', which is not one of : " + ",".join(options))

    return choice


def save_calendar(name):
    ignore_past_events = True
    if has_passed_event():
        prompt = "\nDo you want to export past events?"
        options = ["y", "yes", "no", "n"]
        choice = generic_menu(prompt, options)
        confirmations = ["y", "yes"]
        if choice in confirmations:
            ignore_past_events = False
        else:
            prompt = "\nDo you want to keep these past events?"
            choice = generic_menu(prompt, options)
            if choice not in confirmations:
                delete_past_events()

    calendar_folder_path = os.path.join(absolute_path, "calendars")
    if not os.path.exists(calendar_folder_path):
        os.mkdir(calendar_folder_path)
    calendar_file_name = name + ".ics"
    calendar_file_path = os.path.join(calendar_folder_path, calendar_file_name)
    calendar_relative_path = os.path.join("calendars", calendar_file_name)
    cal = convert_events_to_calendar(events, ignore_past_events)
    if len(events) == 0 or (ignore_past_events and not has_upcoming_event()):
        print("There are no events to save")
    else:
        print("Saving calendar to:")
        print(calendar_file_path)
        with open(calendar_relative_path, "wb") as f:
            f.write(cal.to_ical())


def save_calendar_menu():
    if len(events) == 0:
        print("There are no events to save, please create some first")
    else:
        file_name = input("Enter the file name you wish to use: ")
        if file_name == "":
            file_name = "events"
            print("File Name was left blank, using default file name of: " + file_name)
        save_calendar(file_name)


def load_events():
    if os.path.exists(data_folder_path):
        file = open(data_file_path, "r")
        for line in file:
            event = {}
            values = line.split(",")
            event["Name"] = values[0]
            event["Start DateTime"] = datetime.strptime(values[1], datetime_display_format)
            # removing the end space and or newline character to make this work? (don't fully get it)1
            event["End DateTime"] = datetime.strptime(values[2].strip(), datetime_display_format)
            events.append(event)
        file.close()


def view_events():
    if len(events) == 0:
        print("There are no events to show\n")
    else:
        for event in events:
            print(event_text(event))


def add_event_menu():
    add_more = True
    hint = "If you want to stop adding events, enter 'e' at any point, and you can enter 'h' to see this hint again"
    print(hint)
    while add_more:
        user_input = input("Enter event details: ")
        if user_input == "h":
            print(hint)
        elif user_input == "e":
            add_more = False
        else:
            event = process_event(user_input)
            if "Error" in event:
                print("There is a mistake in the event details:\n" + event["Error"])
            else:
                events.append(event)
    save_events()


description = """This is a commandline application intended for entering details of events one by one through quick copy paste.
Rather than through navigating menus in calendar apps to create events one by one. 
You will still need to find the file on your system and import the ics file, so you probably want to have at least 4-5 
events lined up for this program to be worthwhile."""


def menu():
    load_events()
    repeat_menu = True
    while repeat_menu:
        print("0: Add Events")
        print("1: View Events")
        print("2: Edit Events")
        print("3: Export to Calendar file\n")
        print("h: Help")
        print("e: Exit\n")
        choice = input("Enter your choice: ").strip()
        match choice:
            case "0":
                add_event_menu()
            case "1":
                view_events()
            case "2":
                print("WIP")
            case "3":
                save_calendar_menu()
            case "h":
                print(description)
                print("\nYou can choose what to do by entering a number between 0 and 3\n")
                print("Later on there will be options to press h in the other sub-menus to get more detailed hints")
            case "e":
                print("\nExiting...")
                repeat_menu = False

            case _:
                print("Please enter a valid choice\n")


menu()
