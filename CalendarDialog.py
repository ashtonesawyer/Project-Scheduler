""" Adapted from @moshekaplan's tkinter_components
https://github.com/moshekaplan/tkinter_components/tree/master/CalendarDialog
"""

from tkinter import Frame, StringVar, Entry, Button, LEFT
from tkinter import simpledialog
import tkcalendar


class CalendarDialog(simpledialog.Dialog):
    """Dialog box that displays a calendar and returns the selected date"""
    def body(self, master):
        self.calendar = tkcalendar.Calendar(master)
        self.calendar.pack()

    def apply(self):
        self.result = self.calendar.get_date()


class CalendarFrame(Frame):
    def __init__(self, master):
        Frame.__init__(self, master)

        def getdate():
            cd = CalendarDialog(self)
            self.selected_date.set(cd.result)

        self.selected_date = StringVar()

        Entry(self, textvariable=self.selected_date).pack(side=LEFT)
        Button(self, text="Choose a date", command=getdate).pack(side=LEFT)

