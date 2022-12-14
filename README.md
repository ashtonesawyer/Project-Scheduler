# Project Scheduler 
## Description
This program will take in information about a project, including the 
due date and an estimate of how many hours it will take to complete,
and automatically generate and schedule Google Calendar events for times to 
work on the given project.
### Elements
#### Project Scheduler
This is the main driver of the project. It manages all of the data
and interfaces with Google Calendar. There are currently relatively minor bugs with the scheduler, 
namely difficulty parsing free time when there are overlapping events already in the calendar. 
#### GUI 
This is still in progress. 
It takes user input, error checks as needed, and parses it for the project 
scheduler. 
## Use
Before running the code, the Google client library for python and the tkcalendar library must be downloaded. 
```bash
pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
pip install tkcalendar
```
In order to run with Google Calendar, you will have to have a Google Developer account and create Oath2.0 credentials. This process is described in detail in the [quickstart guide](https://developers.google.com/calendar/api/quickstart/python)
## Testing
Automated tests have not yet been created for this program


