def menu():
    repeat_menu = False
    while not repeat_menu:
        print("0: Add Events")
        print("1: View Events")
        print("2: Edit Events")
        print("3: Exit\n")
        print("4: Help")
        choice = input("Enter your choice: ").strip()
        match choice:
            case "0":
                print("WIP")
            case "1":
                print("WIP")
            case "2":
                print("WIP")
            case "3":
                print("\nExiting...")
                repeat_menu = True
            case "4":
                print("Currently only exiting works (:\n")
            case _:
                print("Please enter a valid choice\n")


menu()
