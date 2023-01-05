import tkinter as Tk
from tkinter import ttk 
from subprocess import call
import os, glob
from pathlib import Path
from moviepy.editor import *

class ClipManager(Tk.Tk):
    def __init__(self, parent):      
        Tk.Tk.__init__(self)
        self.parent = parent
        self.geometry("400x345+504+20")
        self.wm_title("Clips Manager")
        # self.log = getLog(parent.logname)
        self.exportButton = ttk.Button(self, text='Export All', command=self.exportAll)
        self.exportButton.pack(side=Tk.TOP)
        self.buildList()

    def buildList(self):
        print('building list...')
        if 'listBox' in self.__dict__:
            print('killing the old one')
            self.listBox.destroy()
        self.listBox = Tk.Listbox(self, width=500, height=300)
        for i in self.parent.log:
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
        self.parent.player.set_time(int(self.parent.log[index]["startMs"]))
        self.parent.parent.focus_force()

    def exportAll(self):
        for i in self.parent.log:
            self.exportClip(i)
        call(["open", 'exports/'])

    def exportStillsAsSingleClip(self):
        stillsPath = f"{self.parent.getOutputPath()}/stills"
        file_list = glob.glob(f'{stillsPath}/*.png')  # Get all the pngs in the current directory
        clips = [ImageClip(m).set_duration(2)
                for m in file_list]
        concat_clip = concatenate_videoclips(clips.sort(), method="compose")
        concat_clip.write_videofile(f"{self.parent.getOutputPath()}/stills.mp4", fps=1)

    def exportClip(self, logentry):
        print(f'Exporting {self.parent.currentVideo}')
        outputPath = self.parent.getOutputPath()
        Path(outputPath).mkdir(parents=True, exist_ok=True)
        startSec = float(logentry['startMs'])/1000
        endSec = float(logentry['endMs'])/1000
        outName = f'{logentry["id"]}_{startSec}-{endSec}'
        outName = f'{outputPath}/{outName}.mp4' if not self.parent._isWindows else f'exports\\{outName}.mp4' 
        # ffmpeg_extract_subclip("full.mp4", start_seconds, end_seconds, targetname="cut.mp4")
        clip = VideoFileClip(self.parent.currentVideo)
        # getting only first 5 seconds
        clip = clip.subclip(startSec,endSec)
        clip.write_videofile(outName, codec='libx264',
            audio_codec='aac', 
            temp_audiofile='temp-audio.m4a', 
            remove_temp=True)

        print("Generating stills video...")
        self.exportStillsAsSingleClip()

        #media_player.video_take_snapshot