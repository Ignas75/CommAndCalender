from events import process_event

events = []


def view_events():
    if len(events) == 0:
        print("There are no events to show\n")
    else:
        for event in events:
            event_name = event["Name"]
            event_start_time = event["Start DateTime"].strftime("%d/%m/%Y %H:%M")
            event_end_time = event["End DateTime"].strftime("%d/%m/%Y %H:%M")
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


def menu():
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
