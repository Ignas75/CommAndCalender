from events import *
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
    choice = get_user_choice(prompt, options)
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


def get_user_choice(prompt, options):
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


def generic_menu(menu_items, help_text=None):
    valid_choice = False
    user_choice = None
    while not valid_choice:
        for i in range(0, len(menu_items)):
            print(str(i) + ": " + menu_items[i])

        if help_text:
            print("\nh: " + help_text)

        print("e: exit")
        user_choice = input("Please enter your choice here")
        if user_choice.isdigit():
            int_choice = int(user_choice)
            if 0 <= int_choice < len(menu_items):
                valid_choice = True
            elif help_text and user_choice == "h":
                print(help_text)
        elif user_choice == "e":
            valid_choice = True
        else:
            print("You entered: '" + user_choice + "', please try again")
    return user_choice


def save_calendar(name):
    ignore_past_events = True
    if has_passed_event():
        prompt = "\nDo you want to export past events?"
        options = ["y", "yes", "no", "n"]
        choice = get_user_choice(prompt, options)
        confirmations = ["y", "yes"]
        if choice in confirmations:
            ignore_past_events = False
        else:
            prompt = "\nDo you want to keep these past events?"
            choice = get_user_choice(prompt, options)
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
            # removing the end space and or newline character to make this work? (don't fully get it)
            event["End DateTime"] = datetime.strptime(values[2].strip(), datetime_display_format)
            events.append(event)
        file.close()


def indexes_of_list_elem_matching_criteria(event_list, criteria):
    indexes = []
    for i in range(0, len(event_list)):
        if criteria(event_list[i]):
            indexes.append(i)
    return indexes


def print_events_by_index(indexes, event_list):
    for i in indexes:
        print(event_text(event_list[i]) + "\n")


def view_events():
    event_count = len(events)
    if event_count == 0:
        print("There are no events to show\n")
        return 0
    elif event_count <= 5:
        for event in events:
            print(event_text(event))
        return 1
    today_events_indexes = indexes_of_list_elem_matching_criteria(events, is_today)
    tomorrow_events_indexes = indexes_of_list_elem_matching_criteria(events, is_tomorrow)
    this_weeks_events_indexes = indexes_of_list_elem_matching_criteria(events, is_this_week)
    next_weeks_events_indexes = indexes_of_list_elem_matching_criteria(events, is_next_week)
    this_months_events_indexes = indexes_of_list_elem_matching_criteria(events, is_this_month)
    next_months_events_indexes = indexes_of_list_elem_matching_criteria(events, is_next_month)
    show_help = True
    valid_choice = False
    while not valid_choice:
        if show_help:
            print(f"You have ({event_count}) events stored, you can either view them all or apply one of these filters")
            print(f"\ntd: Today({len(today_events_indexes)})   nd: Tomorrow({len(tomorrow_events_indexes)})")
            print(f"tw: This Week({len(this_weeks_events_indexes)})   nw: Next Week({len(next_weeks_events_indexes)})")
            print(f"tm: This Month({len(this_months_events_indexes)})   nm: Next Month({len(next_months_events_indexes)})")
            print("\nOr only press enter to view all")
            show_help = False

        choice = input("\nPlease enter your choice: ").lower()
        match choice:
            case "td":
                print_events_by_index(today_events_indexes, events)
                valid_choice = True
            case "nd":
                print_events_by_index(tomorrow_events_indexes, events)
                valid_choice = True
            case "tw":
                print_events_by_index(this_weeks_events_indexes, events)
                valid_choice = True
            case "nw":
                print_events_by_index(next_weeks_events_indexes, events)
                valid_choice = True
            case "tm":
                print_events_by_index(this_months_events_indexes, events)
                valid_choice = True
            case "nm":
                print_events_by_index(next_months_events_indexes, events)
                valid_choice = True
            case "h":
                show_help = True
            case "e":
                valid_choice = True
            case "":
                for event in events:
                    print(event_text(event))
                valid_choice = True
            case _:
                print(f"You entered '{choice}', you can enter 'h' to repeat the help text, or 'e' to return to the menu")
    delay = input("Press enter to return to the main menu")


def start_dt(event):
    return event["Start DateTime"]


def order_events_by_start_date():
    events.sort(key=start_dt)


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
    order_events_by_start_date()
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
