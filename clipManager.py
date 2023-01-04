import tkinter as Tk
from tkinter import ttk 
from subprocess import call
import os
from moviepy.editor import *

class ClipManager(Tk.Frame):
    def __init__(self, parent):   
        print('Loading clip manager...')   
        Tk.Frame.__init__(self, parent)
        self.root = parent
        self.geometry("400x345+504+20") #
        self.wm_title("Clips Manager")
        # self.log = getLog(parent.logname)
        self.exportButton = ttk.Button(self, text='Export All', command=self.exportAll)
        self.exportButton.pack(side=Tk.TOP)
        # self.buildList()

    def buildList(self):
        print('building list...')
        if 'listBox' in self.__dict__:
            print('killing the old one')
            self.listBox.destroy()
        self.listBox = Tk.Listbox(self, width=500, height=300)
        for i in self.root.cliplog.log:
            print(f'Adding entry {i["id"]} to lisbox..' )
            fromTo = f"{i['startMs']}:{i['endMs']}"
            self.listBox.insert(i['id'],f"{str(i['id']).zfill(4)} | {fromTo} | {i['desc']}")
        self.listBox.pack()
        self.bind('<<ListboxSelect>>', self.onselect)

    def addEntry(self,logEntry):
        print(logEntry)
        fromTo = f"{logEntry['startMs']}:{logEntry['endMs']}"
        self.listBox.insert(logEntry['id'],f"{str(logEntry['id']).zfill(4)} | {fromTo} | {logEntry['desc']}")

    def onselect(self,evt):
        # Note here that Tkinter passes an event object to onselect()
        w = evt.widget
        index = int(w.curselection()[0])
        value = w.get(index)
        print('You selected item %d: "%s"' % (index+1, value))
        self.root.player.set_time(int(self.root.log[index]["startMs"]))
        self.root.parent.focus_force()

    def exportAll(self):
        for i in self.root.log:
            self.exportClip(i)
        if not self.root._isWindows:
            call(["open", 'exports/'])

    def exportClip(self, logentry):
        print(f'Exporting {self.root.currentVideo}')
        video = self.root.currentVideo
        videoFileName = os.path.basename(self.root.currentVideo)
        startSec = float(logentry['startMs'])/1000
        endSec = float(logentry['endMs'])/1000
        outName = f'{videoFileName}_{logentry["id"]}_{startSec}-{endSec}'
        outName = f'exports/{outName}.mp4' if not self.root._isWindows else f'exports\\{outName}.mp4' 
        # ffmpeg_extract_subclip("full.mp4", start_seconds, end_seconds, targetname="cut.mp4")
        clip = VideoFileClip(video)
        # getting only first 5 seconds
        clip = clip.subclip(startSec,endSec)
        clip.write_videofile(outName, codec='libx264',
            audio_codec='aac', 
            temp_audiofile='temp-audio.m4a', 
            remove_temp=True)