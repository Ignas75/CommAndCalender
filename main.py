from events import process_event
import os
from datetime import datetime

events = []
folder_name = "data"
absolute_path = os.path.dirname(__file__)
data_folder_path = os.path.join(absolute_path, folder_name)

data_file_path = "./data/events.txt"
datetime_display_format = "%d/%m/%Y %H:%M"


def save_events():
    headers = ["Name", "Start DateTime", "End DateTime"]

    if not os.path.exists(data_folder_path):
        os.mkdir(data_folder_path)

    file = open(data_file_path, "w")
    for event in events:
        line_strs = [event["Name"], event["Start DateTime"].strftime(datetime_display_format),
                     event["End DateTime"].strftime(datetime_display_format)]
        file.write(",".join(line_strs) + "\n")
    file.close()


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
            event_name = event["Name"]
            event_start_time = event["Start DateTime"].strftime(datetime_display_format)
            event_end_time = event["End DateTime"].strftime(datetime_display_format)
            print(event_name + ":\n" + "Starting: " + event_start_time + "\nEnding: " + event_end_time + "\n\n")


def add_event_menu():
    add_more = True
    hint = "If you want to stop adding events, enter 'r' at any point, and you can enter 'h' to see this hint again"
    print(hint)
    while add_more:
        user_input = input("Enter event details: ")
        if user_input == "h":
            print(hint)
        elif user_input == "r":
            add_more = False
        else:
            event = process_event(user_input)
            if "Error" in event:
                print("There is a mistake in the event details:\n" + event["Error"])
            else:
                events.append(event)
    save_events()


def menu():
    load_events()
    repeat_menu = True
    while repeat_menu:
        print("0: Add Events")
        print("1: View Events")
        print("2: Edit Events")
        print("3: Help")
        print("4: Exit\n")
        choice = input("Enter your choice: ").strip()
        match choice:
            case "0":
                add_event_menu()
            case "1":
                view_events()
            case "2":
                print("WIP")
            case "3":
                print("Currently only exiting works (:\n")
            case "4":
                print("\nExiting...")
                repeat_menu = False

            case _:
                print("Please enter a valid choice\n")


menu()
