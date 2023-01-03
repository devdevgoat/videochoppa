#%%

# import standard libraries
import sys, json, csv
if sys.version_info[0] < 3:
    import Tkinter as Tk
    from Tkinter import ttk
    from Tkinter.filedialog import askopenfilename
    from Tkinter.tkMessageBox import showerror
else:
    import tkinter as Tk
    from tkinter import ttk
    from tkinter import Toplevel
    from tkinter.filedialog import askopenfilename
    from tkinter.messagebox import showerror
from os.path import basename, expanduser, isfile, exists, join as joined

# Import custom library
import vlc
from vlc import Position, VideoMarqueeOption, str_to_bytes

# Import MY libraries
from simpletest import *
from popup import PopUp

class RussPlayer(Player):

    def __init__(self, parent, title=None, video=''):
        Player.__init__(self, parent)
        # Some marquee examples.  Marquee requires '--sub-source marq' in the
        # Instance() call above, see <http://www.videolan.org/doc/play-howto/en/ch04.html>
        self.player.video_set_marquee_int(VideoMarqueeOption.Enable, 1)
        self.player.video_set_marquee_int(VideoMarqueeOption.Size, 48)  # pixels

        # the _Enum type isn't being converted properly into int's during the ctypes casting
        # when you use ints natively, it works
        # Marquee position: 0=center, 1=left, 2=right, 4=top, 8=bottom, you can also use combinations of these values, eg 6 = top-right. default value: -1
        # self.player.video_set_marquee_int(4, 8)
        self.player.video_set_marquee_int(VideoMarqueeOption.Position, Position.top_left)
        self.player.video_set_marquee_int(VideoMarqueeOption.Timeout, 0)  # millisec, 0==forever
        self.player.video_set_marquee_int(VideoMarqueeOption.Refresh, 1000)  # millisec (or sec?)

        # need to detect when a video starts playing and get the log
        # .createOrGetLog()
    
    def createOrGetLog(self, event):
        log = False
        if self.player.get_media():
            media = self.player.get_media()
            filename = basename(vlc.bytes_to_str(media.get_mrl()))
            if self._isWindows:
                filebase = 'cliplogs\\'
            else:
                filebase = 'cliplogs/'
            print(f'Looking for log {filebase}{filename.split(".")[0]}.csv')
            self.logname = f"{filebase}{filename.split('.')[0]}.csv"
            #Create the log for this video
            if not exists(self.logname):
                logFile = open(self.logname,'w')
                logFile.write('id,startMs,endMs,desc,chars\n')
                logFile.close
        # Get the log for this video
        self.log = self.getLog(self.logname)
        self.maxId = self.getMaxId()
        # Display the clip manager
        self.clipManager = ClipManager(self) # inheriting the class has borked the clipmanager...
        self.clipManager.focus_force()
        print("Loaded Clip Manager")

    def getLog(self, logname):
        maxClip = 0
        logFile = open(logname,'r')
        log = list(csv.DictReader(logFile))
        print(log)
        logFile.close()
        return log
        
    def Skip(self, sec, *unused):
        if self.player:
            timeAdd = int(sec * 1e3)
            currentTime = int(self.timeVar.get() * 1e3)
            newTime = currentTime + timeAdd
            print(f"Changing time from {currentTime} to {newTime} by adding {timeAdd} ms")
            self.player.set_time(newTime) 
    
    def LogTime(self, *unused):
        if self.player:
            print(self.player.get_time() * 1e-3)

    def print_info(self):
        media = self.player.get_media()
        print('State: %s' % self.player.get_state())
        print('Media: %s' % vlc.bytes_to_str(media.get_mrl()))
        print('Track: %s/%s' % (self.player.video_get_track(), self.player.video_get_track_count()))
        print('Current time: %s/%s' % (self.player.get_time(), media.get_duration()))
        print('Position: %s' % self.player.get_position())
        print('FPS: %s (%d ms)' % (self.player.get_fps(), self.mspf()))
        print('Rate: %s' % self.player.get_rate())
        print('Video size: %s' % str(self.player.video_get_size(0)))  # num=0
        print('Scale: %s' % self.player.video_get_scale())
        print('Aspect ratio: %s' % self.player.video_get_aspect_ratio())

    def skip_sec(self,seconds=1):
        """Go backward one sec"""
        if self.player.get_media():
            if self.player.is_playing():
                self.player.set_time(self.player.get_time() + (seconds*1000))
            else:
                frameDir = 1 if seconds > 0 else -1
                self.skip_frame(frameDir)


    def skip_frame(self,frames=1):
        """Go backward one frame"""
        if self.player.get_media():
            if self.player.is_playing():
                self.OnPause()
            self.player.set_time(self.player.get_time() + (frames*self.mspf()))

    
    def startClip(self):
        if self.player.get_media():
            self.wip = {
                'logname':self.logname,
                'id': self.getMaxId()+1,
                'startMs':self.player.get_time()
            }
            self.player.video_set_marquee_string(VideoMarqueeOption.Text, \
                str_to_bytes(f'Pending Clip: \
                    {self.wip["startMs"]}:...'))


    def endClip(self):
        if self.player.get_media():
            if not self.wip["startMs"]:
                self.startClip()
            else:
                self.wip["endMs"] = self.player.get_time()
                self.player.video_set_marquee_string(VideoMarqueeOption.Text, \
                    str_to_bytes(f'Pending Clip: \
                        {self.wip["startMs"]}:{self.wip["endMs"]}'))
                # self.logClip()
                PopUp(self)
    
    def getMaxId(self):
        maxClip = 0
        for i in self.log:
            if int(i['id']) > maxClip:
                maxClip = int(i['id'])
        return maxClip

    def mspf():
        """Milliseconds per frame"""
        return int(1000 // (player.get_fps() or 25))


if __name__ == "__main__":

    _video = ''

    while len(sys.argv) > 1:
        arg = sys.argv.pop(1)
        if arg.lower() in ('-v', '--version'):
            # show all versions, sample output on macOS:
            # % python3 ./tkvlc.py -v
            # tkvlc.py: 2019.07.28 (tkinter 8.6 /Library/Frameworks/Python.framework/Versions/3.7/lib/libtk8.6.dylib)
            # vlc.py: 3.0.6109 (Sun Mar 31 20:14:16 2019 3.0.6)
            # LibVLC version: 3.0.6 Vetinari (0x3000600)
            # LibVLC compiler: clang: warning: argument unused during compilation: '-mmacosx-version-min=10.7' [-Wunused-command-line-argument]
            # Plugin path: /Applications/VLC3.0.6.app/Contents/MacOS/plugins
            # Python: 3.7.4 (64bit) macOS 10.13.6

            # Print version of this vlc.py and of the libvlc
            print('%s: %s (%s %s %s)' % (basename(__file__), __version__,
                                         Tk.__name__, Tk.TkVersion, libtk))
            try:
                vlc.print_version()
                vlc.print_python()
            except AttributeError:
                pass
            sys.exit(0)

        elif arg.startswith('-'):
            print('usage: %s  [-v | --version]  [<video_file_name>]' % (sys.argv[0],))
            sys.exit(1)

        elif arg:  # video file
            _video = expanduser(arg)
            if not isfile(_video):
                print('%s error: no such file: %r' % (sys.argv[0], arg))
                sys.exit(1)


    # Create a Tk.App() to handle the windowing event loop
    root = Tk.Tk()
    player = RussPlayer(root, video=_video)
    root.protocol("WM_DELETE_WINDOW", player.OnClose)  # XXX unnecessary (on macOS)
    
    
    root.bind('<Left>',lambda x: player.skip_sec(-10))
    root.bind('<Right>',lambda x: player.skip_sec(10))
    root.bind('<Shift-Left>',lambda x: player.skip_frame(-2))
    root.bind('<Shift-Right>',lambda x: player.skip_frame(2))
    root.bind('<Escape>',lambda x: player.quit())
    root.bind('<Up>',lambda x: player.startClip())
    root.bind('<Down>',lambda x: player.endClip())
    root.bind('<p>',lambda x: print(json.dumps(player.log, indent=4)))
    root.bind('<space>',lambda x: player.OnPause())
    root.bind('<r>',lambda x: player._Play('gurlag01.mkv'))
    # root.bind('<<OnPlay>>',lambda x: player.createOrGetLog())
    events = player.player.event_manager()
    events.event_attach(vlc.EventType.MediaPlayerOpening, player.createOrGetLog)
    
    root.focus_force()

    
    root.mainloop()