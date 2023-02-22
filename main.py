""" Created by Ashton Sawyer 10/31/22
These are the main functions for the project scheduler (see scheduler.py)
"""

from scheduler import *

import os.path


# for use with GUI
def winMain(project):
    """ Parts of this section of code from Google Calendar API quickstart documentation
    https://developers.google.com/calendar/api/quickstart/python
    """

    global TESTING
    #TESTING = True

    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('calendar', 'v3', credentials=creds)

        if TESTING:
            project.printInfo()

        availTimes = gatherAvailTimes(service, project)
        if not availTimes:
            print("Error: There are no times available to schedule during")
            print("Exiting...")
            return

        assignedTimes = randomAssign(availTimes, project)
        if assignedTimes[0] < int(project.hoursToComplete):
            print("We only assigned %d hours of work" % assignedTimes[0])
            makeEvents = input("Do you want to create the available events anyways [y/n]: ")
            if makeEvents == "n":
                print("Exiting...")
                return

        inputEvents(assignedTimes, project, service)

        if TESTING:
            wait = input("Press any key to continue...")
            deleteEvents(service)
        else:
            delete = input("Do you want to delete the created events [y/n]: ")
            if delete == "y":
                deleteEvents(service)

    except HttpError as error:
        print('An error occurred: %s' % error)


# terminal main -- for testing
def main():
    """ Parts of this section of code from Google Calendar API quickstart documentation
        https://developers.google.com/calendar/api/quickstart/python
        """

    global TESTING
    # TESTING = True

    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('calendar', 'v3', credentials=creds)

        project = Project()
        project.textInit()
        if TESTING:
            project.printInfo()

        availTimes = gatherAvailTimes(service, project)
        if not availTimes:
            print("Error: There are no times available to schedule during")
            print("Exiting...")
            return

        assignedTimes = randomAssign(availTimes, project)
        if assignedTimes[0] < int(project.hoursToComplete):
            print("We only assigned %d hours of work" % assignedTimes[0])
            makeEvents = input("Do you want to create the available events anyways [y/n]: ")
            if makeEvents == "n":
                print("Exiting...")
                return

        inputEvents(assignedTimes, project, service)

        if TESTING:
            wait = input("Press any key to continue...")
            deleteEvents(service)
        else:
            delete = input("Do you want to delete the created events [y/n]: ")
            if delete == "y":
                deleteEvents(service)

    except HttpError as error:
        print('An error occurred: %s' % error)


if __name__ == '__main__':
    main()
