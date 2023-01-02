import tkinter as Tk
from tkinter import ttk
from tkinter import Toplevel
import csv

class ClipManager(Tk.Tk):
    def __init__(self, logName):      
        Tk.Tk.__init__(self)
        self.geometry("250x500")
        self.wm_title("Clips Manager")
        self.tkraise(self)
        self.log = getLog(logName)
        # self.button = Tk.Button(self, text="Reload", command=self.buildList)
        # self.button.pack()
        self.buildList()

    def buildList(self):
        print('building list...')
        if 'listBox' in self.__dict__:
            print('killing the old one')
            self.listBox.destroy()
        self.listBox = Tk.Listbox(self, width=500)
        ii = 1
        for i in self.log:
            fromTo = f"{i['startMs']}:{i['endMs']}"
            self.listBox.insert(ii,f"{i['id'].rjust(4,' ')} | {fromTo} | {i['desc']}")
            ii+=1
        self.listBox.pack()

def open_popup():
    return PopUp()

def getLog(logname):
    maxClip = 0
    logFile = open(logname,'r')
    log = list(csv.DictReader(logFile))
    logFile.close()
    return log

# app.mainloop()

app = ClipManager('clipLogs/gurlag01.csv')
app.mainloop()