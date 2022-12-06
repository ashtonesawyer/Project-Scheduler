""" Created by Ashton Sawyer 11/18/22
This is the GUI for the project scheduler -- unfinished
Takes user input, parses, and passes to scheduler
Displays error messages for incorrect input
To Do:
    - Improve error checking
    - Improve layout of screen
    - Improve color and design
    - Improve time input -> give menu/buttons to ensure correct input
    - Connect to be able to display diagnostic messages from scheduler to user through GUI
    - Refactor code structure -> classes, variable names
"""

from main import *

from tkinter import *
from tkinter import ttk
from CalendarDialog import *
from datetime import datetime
import re


# for showing additional menus for days off
def addOffMenu():
    global count, offDrops
    count += 1
    if count < 6:
        offDrops[count].grid(row=count+1)


# for error output to screen
def displayText(text):
    outputLabel.configure(text=text, fg='red')


# parse info from screen for project init
# To Do: improve error checking 
#   + endTime - startTime > 0
#   + endDate - startDate > 0 
#   + endDateTime - startDateTime >= hoursToComplete
def parseInfo():
    displayText("")

    form1 = re.compile('\d{2}:\d{2}.{2}')
    form2 = re.compile('\d:\d{2}.{2}')

    project = Project()
    name = nameEntry.get()
    hours = hoursEntry.get()
    if not hours.isdigit():
        displayText("Error: Hours to complete needs to be a positive integer")
        return
    maxHours = maxEntry.get()
    if not maxHours.isdigit():
        displayText("Error: Max hours needs to be a positive integer")
        return
    maxHours = int(maxHours)
    minHours = minEntry.get()
    if not minHours.isdigit():
        displayText("Error: Min hours needs to be a positive integer")
        return
    minHours = int(minHours)
    endDate = datetime.strptime(endCalendar.selected_date, "%m/%d/%y").date()
    daysOff = []
    for index in range(6):
        if menus[index].get() != "--Select--":
            daysOff += [menus[index].get()]
    hold = earliestEntry.get()
    hold += timeMenus[0].get()
    print(hold)
    if not form1.match(hold) and not form2.match(hold):
        displayText("Error: Earliest time invalid format")
        return
    if hold[:2].isdigit() and int(hold[:2]) > 12:
        displayText("Error: 12 hour time required for earliest time")
        return
    earliestTime = datetime.strptime(hold, "%I:%M%p").time()
    hold = latestEntry.get()
    hold += timeMenus[1].get()
    if not form1.match(hold) and not form2.match(hold):
        displayText("Error: Latest time invalid format")
        return
    if hold[:2].isdigit() and int(hold[:2]) > 12:
        displayText("Error: 12 hour time required for latest time")
        return
    latestTime = datetime.strptime(hold, "%I:%M%p").time()
    buffer = bufferEntry.get()
    if not buffer.isdigit():
        displayText("Error: Buffer needs to be a positive integer")
        return
    buffer = timedelta(minutes=int(buffer))
    project.windowInit(name, hours, maxHours, minHours, endDate, daysOff, earliestTime, latestTime, buffer)
    winMain(project)


# setup window
win = Tk()
win.minsize(850, 440)
win.title("Project Scheduler")
win.grid_rowconfigure(0, weight=1)
win.grid_columnconfigure(0, weight=1)

# create + config frames
projNameFrm = ttk.Labelframe(win, padding=10)
dueDateFrm = ttk.Labelframe(win, padding=10)
dataFrm = ttk.Labelframe(win, padding=10)
genButtonFrm = ttk.Labelframe(win, padding=10)

projNameFrm.grid_rowconfigure(0, weight=1)
dueDateFrm.grid_rowconfigure(0, weight=1)
dataFrm.grid_rowconfigure(0, weight=1)
genButtonFrm.grid_rowconfigure(0, weight=1)

projNameFrm.grid_columnconfigure(0, weight=1)
dueDateFrm.grid_columnconfigure(0, weight=1)
dataFrm.grid_columnconfigure(0, weight=1)
genButtonFrm.grid_columnconfigure(0, weight=1)

data_leftFrm = ttk.Frame(dataFrm, padding=10)
data_rightFrm = ttk.Frame(dataFrm, padding=10)

"""frm1 = ttk.Labelframe(win, text="Project Name: ", padding=10)
frm2 = ttk.Labelframe(win, text="Number of hours to complete the project: ", padding=10)
frm3 = ttk.Labelframe(win, text="Time (hours) to spend on project in one sitting: ", padding=10)
frm4 = ttk.Labelframe(win, text="Date the project is due: ", padding=10)
frm5 = ttk.Labelframe(win, text="Days of the week to take off: ", padding=10)
frm6 = ttk.Labelframe(win, text="Limit working times: ", padding=10)
frm7 = ttk.Labelframe(win, text="Time between events (mins): ", padding=10)
frm8 = ttk.Frame(win, padding=10)   # for init button
frm9 = ttk.Labelframe(win, text="Output: ", padding=10)
"""
# layout frames
projNameFrm.grid(row=0, sticky="new")
dueDateFrm.grid(row=1, sticky="nsew")
dataFrm.grid(row=2, sticky="nsew")
genButtonFrm.grid(row=3, sticky="sew")

data_leftFrm.grid(row=0, column=0)
data_rightFrm.grid(row=0, column=1)

# project name widgets
nameFrm = ttk.Frame(projNameFrm)
nameFrm.grid(row=0)
nameLabel = Label(nameFrm, text="Project Name:  ")
nameEntry = Entry(nameFrm, width=40)
nameLabel.grid(row=0, column=0)
nameEntry.grid(row=0, column=1)

# due date widgets
dateFrm = ttk.Frame(dueDateFrm)
dateFrm.grid(row=0)
dateLabel = Label(dateFrm, text="Due Date: ")
endCalendar = CalendarFrame(dateFrm)
dateLabel.grid(row=0, column=0)
endCalendar.grid(row=0, column=1)

# data_left widgets
#    hours
hoursFrm = ttk.Frame(data_leftFrm, padding=5)
hoursFrm.grid(row=0)

hoursLabel = Label(hoursFrm, text="Hours to complete: ")
hoursEntry = Entry(hoursFrm, width=40)
hoursLabel.grid(row=0, column=0)
hoursEntry.grid(row=0, column=1)

#    time to work in one sitting
sittingFrm = ttk.Frame(data_leftFrm, padding=5)
sittingFrm.grid(row=1)

sittingLabel = Label(sittingFrm, text="Hours to work in one sitting")
maxLabel = Label(sittingFrm, text="Max: ")
minLabel = Label(sittingFrm, text="Min: ")
maxEntry = Entry(sittingFrm, width=35)
minEntry = Entry(sittingFrm, width=35)
sittingLabel.grid(row=1, column=0)
maxLabel.grid(row=2, column=0)
maxEntry.grid(row=2, column=1)
minLabel.grid(row=3, column=0)
minEntry.grid(row=3, column=1)

#    days off
daysOffFrm = ttk.Frame(data_leftFrm, padding=5)
daysOffFrm.grid(row=3)

daysLabel = Label(daysOffFrm, text="Days off")
dayOptions = ["--Select--", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
menus = []             # list of menu options for offDrops
offDrops = []          # list of OptionMenus
count = 0              # how many days off are there
for i in range(6):        # init menus
    tmp = StringVar()
    menus += [tmp]
    menus[i].set("--Select--")
for i in range(6):        # init options
    tmp = OptionMenu(daysOffFrm, menus[i], *dayOptions)
    offDrops += [tmp]
addButton = Button(daysOffFrm, text="+", command=addOffMenu)

daysLabel.grid(row=0)
offDrops[0].grid(row=1)
addButton.grid(row=7)

# data_right widgets
#    work times
timesFrm = ttk.Frame(data_rightFrm, padding=5)
timesFrm.grid(row=0)

timesLabel = Label(timesFrm, text="Work time restrictions")
earliestLabel = Label(timesFrm, text="Earliest: ")
latestLabel = Label(timesFrm, text="Latest: ")
earliestEntry = Entry(timesFrm, width=20)
latestEntry = Entry(timesFrm, width=20)
timeMenus = []
timeOptions = ["AM", "PM"]
for i in range(2):
    tmp = StringVar()
    timeMenus += [tmp]
    timeMenus[i].set("AM")
earlyDrop = OptionMenu(timesFrm, timeMenus[0], *timeOptions)
lateDrop = OptionMenu(timesFrm, timeMenus[1], *timeOptions)
timesLabel.grid(row=0)
earliestLabel.grid(row=1, column=0)
latestLabel.grid(row=2, column=0)
earliestEntry.grid(row=1, column=1)
latestEntry.grid(row=2, column=1)
earlyDrop.grid(row=1, column=3)
lateDrop.grid(row=2, column=3)

#    buffer
buffFrm = ttk.Frame(data_rightFrm, padding=5)
buffFrm.grid(row=1)

bufferLabel = Label(buffFrm, text="Buffer between events (mins): ")
bufferEntry = Entry(buffFrm, width=40)
bufferLabel.grid(row=0, column=0)
bufferEntry.grid(row=0, column=1)

# generate widget
genButton = Button(genButtonFrm, text="Generate Events", command=parseInfo)
genButton.grid(row=0, column=0, sticky="")

"""# name
frm1.grid()
#nameEntry = Entry(frm1, width=40)
nameEntry.grid()

# hoursToComplete
frm2.grid()
hoursEntry = Entry(frm2, width=40)
hoursEntry.grid()

# maxHours + minHours
frm3.grid()
maxLabel = Label(frm3, text="Max: ").grid(column=0, row=0)
maxEntry = Entry(frm3, width=40)
maxEntry.grid(column=1, row=0)
minLabel = Label(frm3, text="Min: ").grid(column=0, row=1)
minEntry = Entry(frm3, width=40)
minEntry.grid(column=1, row=1)

# endDate
now = datetime.today()
frm4.grid()
endCalendar = Calendar(frm4, selectmode='day', year=now.year, month=now.month, day=now.day)
endCalendar.grid()


# daysOff 
# To Do: create button to add drop downs as needed rather than giving all at once
frm5.grid()
dayOptions = ["--Select--", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
menus = []
offDrops = []
for i in range(6):
    tmp = StringVar()
    menus += [tmp]
    menus[i].set("--Select--")
for i in range(6):
    tmp = OptionMenu(frm5, menus[i], *dayOptions)
    offDrops += [tmp]
    offDrops[i].grid()

# earliestTime + latestTime - not the best format, but works for now
frm6.grid()
earliestLabel = Label(frm6, text="Earliest time to work: ").grid(column=0, row=0)
earliestEntry = Entry(frm6, width=20)
earliestEntry.grid(column=1, row=0)
latestLabel = Label(frm6, text="Latest time to work: ").grid(column=0, row=1)
latestEntry = Entry(frm6, width=20)
latestEntry.grid(column=1, row=1)
timeMenus = []
timeOptions = ["AM", "PM"]
for i in range(2):
    tmp = StringVar()
    timeMenus += [tmp]
    timeMenus[i].set("AM")
earlyDrop = OptionMenu(frm6, timeMenus[0], *timeOptions)
earlyDrop.grid(column=2, row=0)
lateDrop = OptionMenu(frm6, timeMenus[1], *timeOptions)
lateDrop.grid(column=2, row=1)

# buffer
frm7.grid()
bufferEntry = Entry(frm7, width=20)
bufferEntry.grid()

# go button
frm8.grid()
button = Button(frm8, text="Generate Events", width=20, command=parseInfo)
button.grid()

# output
frm9.grid(column=1, row=3)
outputLabel = Label(frm9, text="")
outputLabel.grid()"""

win.mainloop()

