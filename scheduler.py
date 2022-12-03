""" Created by Ashton Sawyer 10/31/22
This is a program to gather information about a project and schedule it in chunks in Google Calendar.
It will take the estimated time to complete the project and the end date (time of use assumed to be start)
and split it into chunks so that the number of total hours of work is reached by the end date
Events will be made in the calendar to schedule these chunks of work time
"""

from __future__ import print_function

from datetime import datetime
from datetime import timedelta
from datetime import timezone
import time

from random import *

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar.events']
TESTING = False
eventIDs = []  # to easily delete created events at the end


# stores all project information
class Project:
    # for converting input
    weekdays = {'Monday': 0, 'Tuesday': 1, 'Wednesday': 2, 'Thursday': 3, 'Friday': 4, 'Saturday': 5, 'Sunday': 6,
                'Mon': 0, 'Tue': 1, 'Wed': 2, 'Thur': 3, 'Fri': 4, 'Sat': 5, 'Sun': 6}

    # default init
    def __init__(self):
        self.startDateTime = datetime.today()
        self.name = ""
        self.hoursToComplete = -1
        self.maxHours = -1
        self.minHours = -1
        self.endDate = -1
        self.daysOff = []
        self.daysOffInt = []
        self.earliestTime = -1
        self.latestTime = -1
        self.buffer = -1

    # initialize from GUI
    def windowInit(self, name, hoursToComplete, maxHours, minHours, endDate, daysOff, earliestTime, latestTime, buffer):
        self.name = name
        self.hoursToComplete = hoursToComplete
        self.maxHours = maxHours
        self.minHours = minHours
        self.endDate = endDate
        self.daysOff = daysOff
        for day in range(len(self.daysOff)):
            self.daysOffInt += [self.weekdays[self.daysOff[day]]]
        self.earliestTime = earliestTime
        self.latestTime = latestTime
        self.buffer = buffer

    # initialize from terminal -- for testing
    # To Do: better error checking for weekdays
    def textInit(self):
        self.name = input("What is your project called: ")
        self.hoursToComplete = input("How many hours will it take to complete %s: " % self.name)

        # collect + error check maxHours
        self.maxHours = int(input("What is the longest (hours) you want to work in one stint (min:1): "))
        if self.maxHours < 1:
            self.maxHours = 1

        # collect + error check minHours
        while True:
            self.minHours = int(input("What is the shortest (hours) you want to work in one stint (min: 1): "))
            if self.minHours < 1:
                self.minHours = 1
            if self.minHours <= self.maxHours:
                break
            else:
                print("Error: minimum hours more than maximum hours")

        # collect and format end date
        while True:
            while True:
                self.endDate = input("When does %s need to be done by (mmddyy): " % self.name)
                if int(self.endDate[:2]) <= 12:
                    if int(self.endDate[2:4]) <= 31:
                        break
                    else:
                        print("Error: Invalid Day")
                else:
                    print("Error: Invalid Month")
            self.endDate = datetime.strptime(self.endDate, "%m%d%y").date()
            if self.endDate >= self.startDateTime.date():
                break
            else:
                print("Error: End Date before Start Date")

        # collect and format days off
        self.daysOff = input("Enter days you don't want to work on %s with a space in between: " % self.name)
        self.daysOff = self.daysOff.split()
        self.daysOffInt = []
        for day in range(len(self.daysOff)):
            self.daysOffInt += [self.weekdays[self.daysOff[day]]]

        # collect and format earliest time to work on project
        while True:
            self.earliestTime = input("What is the earliest you want to work on %s (hh:mm am/pm): " % self.name)
            if int(self.earliestTime[:2]) <= 12:
                if int(self.earliestTime[3:5]) <= 59:
                    break
                else:
                    print("Error: Invalid minutes")
            else:
                print("Error: Invalid hour")
        self.earliestTime = datetime.strptime(self.earliestTime, "%I:%M %p").time()

        # collect and format latest time to work on project
        while True:
            while True:
                self.latestTime = input("What is the latest you want to work on %s (hh:mm am/pm): " % self.name)
                if int(self.latestTime[:2]) <= 12:
                    if int(self.latestTime[3:5]) <= 59:
                        break
                    else:
                        print("Error: Invalid minutes")
                else:
                    print("Error: Invalid hour")
            self.latestTime = datetime.strptime(self.latestTime, "%I:%M %p").time()
            if self.latestTime > self.earliestTime:
                break
            else:
                print("Error: End time before start time")

        self.buffer = input("How many minutes do you want to buffer between events (default = 15): ")
        if self.buffer == "":
            self.buffer = "15"
        self.buffer = timedelta(minutes=int(self.buffer))

    # for testing
    def printInfo(self):
        print("Project Name: %s" % self.name)
        print("Hours to complete: %s" % self.hoursToComplete)
        print("Start DateTime: %s" % self.startDateTime)
        print("End Date: %s" % self.endDate)
        print("Days Off: %s" % self.daysOff)
        print("Days Off Ints: %s" % self.daysOffInt)
        print("Earliest work time: %s" % self.earliestTime)
        print("Latest work time: %s" % self.latestTime)
        print("Max hours: %d" % self.maxHours)
        print("Min hours: %d" % self.minHours)
        print("Buffer: %s" % self.buffer)
        print("\n")


# connects to Google Calendar and loads events between now() and endDateTime
def gatherUnavailTimes(service, project) -> list:
    # get current time in RFT3339 -> 'Z' stand-in for +00:00
    now = datetime.utcnow().isoformat() + 'Z'

    # get offset from UTC, set end as RFT3339 of end date and latest time for project
    offset = time.timezone if (time.localtime().tm_isdst == 0) else time.altzone
    tz = timezone(timedelta(seconds=(offset * -1)))  # -1 bc was returning +7:00 for PDT, might be problem other places
    end = datetime.combine(project.endDate, project.latestTime, tz).isoformat()

    # get events from primary calendar between now and end date
    unavailTimes_r = service.events().list(calendarId='primary', timeMin=now,
                                           timeMax=end, singleEvents=True,
                                           orderBy='startTime').execute()
    # turn into array of events + return
    unavailTimes = unavailTimes_r.get('items', [])
    return unavailTimes


# ignores all day events
# return list: each day is a list with events entered as [summary, startDateTime, endDateTime]
#   ex. [[["work", start, end], ["movie", start, end]], [], [["family dinner", start, end]]]
#       Day 1: work, then a movie
#       Day 2: Nothing
#       Day 3: family dinner
def split(unavailTimes, project) -> list:
    times = []
    i = 0

    if TESTING:
        for j in range(len(unavailTimes)):
            print(unavailTimes[j]['summary'])
            print(unavailTimes[j]['start'])

    # skip if all day event @ start
    while i < len(unavailTimes) and 'dateTime' not in unavailTimes[i]['start']:
        i += 1

    day = datetime.combine(project.startDateTime, project.latestTime)  # starting day
    endDateTime = datetime.combine(project.endDate, project.latestTime)
    while day <= endDateTime:
        dayTimes = []
        while i < len(unavailTimes) and day.date() == datetime.fromisoformat(
                unavailTimes[i]['start']['dateTime']).date():
            temp = [unavailTimes[i]['summary'], datetime.fromisoformat(unavailTimes[i]['start']['dateTime']),
                    datetime.fromisoformat(unavailTimes[i]['end']['dateTime'])]
            dayTimes += [temp]
            i += 1
            while i < len(unavailTimes) and 'dateTime' not in unavailTimes[i]['start']:
                i += 1
        times += [dayTimes]
        day += timedelta(days=1)

    if TESTING:
        print(times)
        print("\n")

    return times


# This is where the bulk of the work is done
# To Do: refactor -- split into multiple functions
# Returns : availTimes -> list of tuples to rep. start/end of available time chunk
#            split into sections of days
#            ex. -> [[], [[start, end], [start, end]], [[start, end]]]
#                   Day 1: no available times
#                   Day 2: two chunks of available time
#                   Day 3: one chunk of available time
def gatherAvailTimes(service, project) -> list:
    unavailTimes = gatherUnavailTimes(service, project)
    availTimes = []

    # print unavail times
    if TESTING:
        for i in range(len(unavailTimes)):
            if 'dateTime' in unavailTimes[i]['start']:
                eventTime = datetime.fromisoformat(unavailTimes[i]['start']['dateTime'])
            elif 'date' in unavailTimes[i]['start']:
                eventTime = datetime.fromisoformat(unavailTimes[i]['start']['date'])
            print("Event: %s at %s" % (unavailTimes[i]['summary'], eventTime))

    projectEndDateTime = datetime.combine(project.endDate, project.latestTime)
    days = projectEndDateTime - project.startDateTime

    if not unavailTimes:
        offset = time.timezone if (time.localtime().tm_isdst == 0) else time.altzone
        tz = timezone(timedelta(seconds=(offset * -1)))
        for day in range(days.days + 1):  # include end day as day to work
            dateDay = project.startDateTime.date() + timedelta(days=day)
            if project.startDateTime.time() >= project.latestTime:  # if it's too late to work today, skip
                dateDay += timedelta(days=1)

            startDate = dateDay
            if startDate.weekday() in project.daysOffInt:  # if curr day is a day off, skip
                continue
            startDateTime = datetime.combine(startDate, project.earliestTime, tz)
            endDateTime = datetime.combine(startDate, project.latestTime, tz)
            availTimes += [[startDateTime, endDateTime]]
    else:
        # get time zone info
        tz = -1
        for i in range(len(unavailTimes)):
            if 'dateTime' in unavailTimes[i]['start']:
                tz = datetime.fromisoformat(unavailTimes[i]['start']['dateTime']).tzinfo
        if tz == -1:
            offset = time.timezone if (time.localtime().tm_isdst == 0) else time.altzone
            tz = timezone(
                timedelta(seconds=(offset * -1)))  # -1 bc was returning +7:00 for PDT, might be problem other places

        # split unavail times into different days
        unavailTimes = split(unavailTimes, project)

        i = 0
        if project.startDateTime.time() >= project.latestTime:  # if it's too late to work today, skip
            i = 1
        for day in range(days.days + 1):  # include end day as day to work
            dateDay = project.startDateTime.date() + timedelta(days=day)
            if project.startDateTime.time() >= project.latestTime:  # if it's too late to work today, skip
                dateDay += timedelta(days=1)

            startDate = dateDay
            if startDate.weekday() in project.daysOffInt:  # if day isn't for working skip it
                i += 1
                continue

            # if there are not events during day
            if not unavailTimes[i]:
                startDateTime = datetime.combine(startDate, project.earliestTime, tz)
                if dateDay == project.startDateTime.date() and project.startDateTime.time() > project.earliestTime:
                    startDateTime = datetime.combine(startDate, project.startDateTime.time(), tz)
                endDateTime = datetime.combine(startDate, project.latestTime, tz)
                availTimes += [[startDateTime, endDateTime]]
            else:
                lastEvent = len(unavailTimes[i]) - 1
                for j in range(len(unavailTimes[i])):
                    currEvent = unavailTimes[i][j]
                    prevEvent = []
                    if j > 0:
                        prevEvent = unavailTimes[i][j - 1]

                    times = []
                    # if current event starts before earliest work time skip
                    if (currEvent[1] - project.buffer).time() < project.earliestTime and not j == lastEvent:
                        continue
                    # if current event starts after latest work time ignore start time
                    elif (currEvent[1] - project.buffer).time() > project.latestTime:
                        # if currEvent is first event of day
                        if j == 0:
                            startDateTime = datetime.combine(currEvent[1].date(), project.earliestTime, tz)
                            endDateTime = datetime.combine(currEvent[1].date(), project.latestTime, tz)
                            times = [startDateTime, endDateTime]
                        else:
                            if (datetime.combine(currEvent[1].date(), project.latestTime, tz) -
                                (prevEvent[2] + project.buffer)) >= timedelta(hours=project.minHours):
                                startDateTime = prevEvent[2] + project.buffer
                                endDateTime = datetime.combine(currEvent[1].date(), project.latestTime, tz)
                                times = [startDateTime, endDateTime]
                        if times:
                            availTimes += [times]
                        continue
                    # if currEvent starts within time constraints
                    else:
                        # if currEvent is first event of day
                        if j == 0:
                            if ((currEvent[1] - project.buffer) -
                                datetime.combine(currEvent[1].date(), project.earliestTime, tz)) >= \
                                    timedelta(hours=project.minHours):
                                startDateTime = datetime.combine(currEvent[1].date(), project.earliestTime, tz)
                                endDateTime = currEvent[1] - project.buffer
                                times = [startDateTime, endDateTime]
                        else:
                            if ((currEvent[1] - project.buffer) - (prevEvent[2] + project.buffer)) >= \
                                    timedelta(hours=project.minHours):
                                startDatetime = prevEvent[2] + project.buffer
                                endDateTime = currEvent[1] - project.buffer
                                times = [startDatetime, endDateTime]
                        if times:
                            availTimes += [times]

                    times = []  # reset for reuse if needed
                    if j == lastEvent:
                        # if last even ends after latest work time skip
                        if (currEvent[2] + project.buffer).time() > project.latestTime:
                            continue
                        # if last event ends before earliest work time ignore end time
                        elif (currEvent[2] + project.buffer).time() < project.earliestTime:
                            startDateTime = datetime.combine(currEvent[1].date(), project.earliestTime, tz)
                            endDateTime = datetime.combine(currEvent[1].date(), project.latestTime, tz)
                            times = [startDateTime, endDateTime]
                        else:
                            if (datetime.combine(currEvent[1].date(), project.latestTime, tz) -
                                (currEvent[2] + project.buffer)) >= timedelta(hours=project.minHours):
                                startDateTime = currEvent[2] + project.buffer
                                endDateTime = datetime.combine(currEvent[1].date(), project.latestTime, tz)
                                times = [startDateTime, endDateTime]
                        if times:
                            availTimes += [times]
            i += 1

    if TESTING:
        print("Available Times:")
        for i in range(len(availTimes)):
            print("%s" % availTimes[i])
        print("\n")

    return availTimes


# availTimes a list of Tuples -> (startDateTime, endDateTime) to represent sections of free time
# returns a list -> [hoursAssigned, [assignedStart, assignedEnd], [assignedStart, assignedEnd]...]
def randomAssign(availTimes, project) -> list:
    timeAssigned = 0
    assignedTimes = []
    assignedTimes += [0]

    while timeAssigned < int(project.hoursToComplete):
        timeLeft = int(project.hoursToComplete) - timeAssigned
        if timeLeft < int(project.hoursToComplete) and not availTimes:
            print("Error: not enough times available before deadline")
            break

        rand = randint(0, len(availTimes) - 1)
        hrsAvail = availTimes[rand][1] - availTimes[rand][0]

        if hrsAvail < timedelta(hours=project.minHours):  # if not enough time for minHours skip
            del availTimes[rand]
            continue
        elif hrsAvail >= timedelta(hours=timeLeft) and timeLeft <= project.maxHours:
            hrsAssigned = timeLeft
        elif hrsAvail > timedelta(hours=project.maxHours):  # if more time than max, set max hrsAssigned = maxHours
            hrsAssigned = project.maxHours
        else:  # if less/equal time avail than max, set max hrsAssigned = hrsAvail
            intHrsAvail = hrsAvail.seconds // 3600
            hrsAssigned = intHrsAvail

        assignedTime = [availTimes[rand][0], availTimes[rand][0] + timedelta(hours=hrsAssigned)]
        availTimes[rand][0] += timedelta(hours=hrsAssigned)
        availTimes[rand][0] += project.buffer
        timeAssigned += hrsAssigned
        assignedTimes[0] = timeAssigned
        assignedTimes += [assignedTime]

        if TESTING:
            print("Assigned Times:")
            for i in range(1, len(assignedTimes)):
                print("%s" % assignedTimes[i])
            print("timeAssigned: %d timeLeft: %d" % (timeAssigned, timeLeft))
            print("Avail times:")
            for i in range(len(availTimes)):
                print("%s" % availTimes[i])
            print("")
    if TESTING:
        print("\n")

    return assignedTimes


# creates Google Calendar event from times assigned to work on project
def inputEvents(assignedTimes, project, service):
    """ This section of code was adapted from Google Calendar API Events: Insert Documentation
    https://developers.google.com/calendar/api/v3/reference/events/insert#examples
    """
    for ev in range(1, len(assignedTimes)):
        if TESTING:
            print("Start Time: %s End Time: %s" % (assignedTimes[ev][0], assignedTimes[ev][1]))
        event = {
            'summary': project.name,
            'start': {
                'dateTime': assignedTimes[ev][0].isoformat(),
                'timeZone': 'America/Los_Angeles',
            },
            'end': {
                'dateTime': assignedTimes[ev][1].isoformat(),
                'timeZone': assignedTimes[ev][1].tzname(),
            },
            'reminders': {
                'useDefault': True,
            },
        }

        event = service.events().insert(calendarId='primary', body=event).execute()
        global eventIDs
        eventIDs += [event['id']]
        print("Event created: %s" % event.get('htmlLink'))


# deletes all created events -- for testing
def deleteEvents(service):
    for event in range(len(eventIDs)):
        service.events().delete(calendarId='primary', eventId=eventIDs[event]).execute()
        print("Event: %s deleted" % eventIDs[event])
