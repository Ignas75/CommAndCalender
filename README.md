# CommAndCalender

A project intended to create a program which:

- takes a list of events
- converts them into events
- which can be output into the commandline as a schedule
- or exported into a calendar ics file for easy bulk import into your chosen calendar app

The intended use case is for when you are given a lot of events in a text format, and you want to quickly grab
each one to export into a calendar of your choice with less menu navigation. 
(Might want at least 4-5 before it becomes worthwhile?)

## TO DO

- [x] Add commandline menu loop
- [x] Create basic event storage format
- [x] Add pattern recognition for command-line input, for creating events (regex)
- [x] Make menu option for displaying stored schedule work
- [x] Adjust event format to match google calendar's events
- [x] Add exporting events via iCalendar format
  - [x] Add confirmation for also exporting events that have already started or passed
  - [x] If rejected, could also give an option to delete said events as they are no longer necessary
- [ ] Add a more "dynamic" viewing of the events in the View events option
  - Like providing time ranges
  - Or viewing x amount of events 
  - Or viewing "past"/"future" events only
- [ ] Allow for selecting and editing of event details 
    - Either by selecting what details to edit or sending a new event string 
    - The latter option would not be available for events which have already "started"
- [ ] Enable bulk deleting for events based on criteria (how far in the past/future)
    - Preview what is going to be deleted first
- [ ] Add timezone detection and settings
- [ ] Adjust README and menu to explain calendar export functionality
- [ ] Consider setting up defaults (and settings) for
  - [ ] Event durations
  - [ ] Deleting events which have already passed from the saves
    - This would remove viewing, editing, and exporting of past event functionality. 
      - Might need a global variable to track this? 
  - Might want to store these defaults in a file in case they are changed in settings? 
- [ ] Add instructions for using and running the app in a commandline

## Extensions/Idea Dump

- GUI for app
- Inviting others
- Recurring events
- Add security or at least warnings about storing sensitive information in txt/ics files locally