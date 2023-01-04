import vlc, json, tkinter as Tk
from clipManager import ClipManager
from rp import RussPlayer
from popup import PopUp
from os.path import basename, expanduser, isfile, exists, join as joined
from cliplog import ClipLog

class MainApp(Tk.Tk):
    def __init__(self):
        Tk.Tk.__init__(self)
        self.rp = RussPlayer(self, video="")
        self.clipmanager = ClipManager(self)
        self.cliplog = None

        # init bindings
        self.protocol("WM_DELETE_WINDOW", self.rp.OnClose)  # XXX unnecessary (on macOS)
        self.bind('<Left>',lambda x: self.rp.skip_sec(-10))
        self.bind('<Right>',lambda x: self.rp.skip_sec(10))
        self.bind('<Shift-Left>',lambda x: self.rp.skip_frame(-2))
        self.bind('<Shift-Right>',lambda x: self.rp.skip_frame(2))
        self.bind('<Escape>',lambda x: self.rp.quit())
        self.bind('<Up>',lambda x: self.rp.startClip())
        self.bind('<Down>',lambda x: self.rp.endClip())
        self.bind('<p>',lambda x: print(json.dumps(self.rp.log, indent=4)))
        self.bind('<space>',lambda x: self.rp.OnPause())
        self.bind('<r>',lambda x: self.rp._Play('gurlag01.mkv'))

        # Subscribe to events
        self.em = self.rp.player.event_manager()
        self.em.event_attach(vlc.EventType.MediaPlayerOpening, self.getPlaying)

    def promptForDesc(self):
        PopUp(self)
    
    def getPlaying(self,event):
        print('Callback')
        media = self.rp.player.get_media()
        self.current_video = basename(vlc.bytes_to_str(media.get_mrl()))
        print(f'Playing {self.current_video}')
        self.cliplog = ClipLog(self, self.current_video)
        print('CaLLIG build list')
        self.clipmanager.buildList()


if __name__ == "__main__":

    # Create a Tk.App() to handle the windowing event loop
    root = MainApp()

    root.focus_force()

    root.mainloop()