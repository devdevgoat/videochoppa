#%%
#! /usr/bin/python
# -*- coding: utf-8 -*-

# tkinter example for VLC Python bindings
# Copyright (C) 2015 the VideoLAN team
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston MA 02110-1301, USA.
#
"""A simple example for VLC python bindings using tkinter.
Requires Python 3.4 or later.
Author: Patrick Fay
Date: 23-09-2015

Modder: Devdevgoat
Date: 30-12-2022
Adding some features to support amv creation:
    *=pending
    - Time Skipping
        - left move back 10 sec
        - right move fwd 10 sec
        - hold? shift to scrub?*
    - Clip Logger for clip tagging
        - Up arrow to start clip tag*
        - down arrow to end clip tag*
            - write the following to clip log:
                -start
                -end
                -filename
"""

# Tested with Python 3.7.4, tkinter/Tk 8.6.9 on macOS 10.13.6 only.
__version__ = '20.05.04'  # mrJean1 at Gmail

# import external libraries
import vlc
from vlc import Position, VideoMarqueeOption, str_to_bytes

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
from pathlib import Path
import time

#import custom libs
from clipManager import ClipManager

_isMacOS   = sys.platform.startswith('darwin')
_isWindows = sys.platform.startswith('win')
_isLinux   = sys.platform.startswith('linux')

if _isMacOS:
    from ctypes import c_void_p, cdll
    # libtk = cdll.LoadLibrary(ctypes.util.find_library('tk'))
    # returns the tk library /usr/lib/libtk.dylib from macOS,
    # but we need the tkX.Y library bundled with Python 3+,
    # to match the version number of tkinter, _tkinter, etc.
    try:
        libtk = 'libtk%s.dylib' % (Tk.TkVersion,)
        prefix = getattr(sys, 'base_prefix', sys.prefix)
        libtk = joined(prefix, 'lib', libtk)
        dylib = cdll.LoadLibrary(libtk)
        # getNSView = dylib.TkMacOSXDrawableView is the
        # proper function to call, but that is non-public
        # (in Tk source file macosx/TkMacOSXSubwindows.c)
        # and dylib.TkMacOSXGetRootControl happens to call
        # dylib.TkMacOSXDrawableView and return the NSView
        _GetNSView = dylib.TkMacOSXGetRootControl
        # C signature: void *_GetNSView(void *drawable) to get
        # the Cocoa/Obj-C NSWindow.contentView attribute, the
        # drawable NSView object of the (drawable) NSWindow
        _GetNSView.restype = c_void_p
        _GetNSView.argtypes = c_void_p,
        del dylib

    except (NameError, OSError):  # image or symbol not found
        def _GetNSView(unused):
            return None
        libtk = "N/A"

    C_Key = "Command-"  # shortcut key modifier

else:  # *nix, Xwindows and Windows, UNTESTED

    libtk = "N/A"
    C_Key = "Control-"  # shortcut key modifier


class _Tk_Menu(Tk.Menu):
    '''Tk.Menu extended with .add_shortcut method.
       Note, this is a kludge just to get Command-key shortcuts to
       work on macOS.  Other modifiers like Ctrl-, Shift- and Option-
       are not handled in this code.
    '''
    _shortcuts_entries = {}
    _shortcuts_widget  = None

    def add_shortcut(self, label='', key='', command=None, **kwds):
        '''Like Tk.menu.add_command extended with shortcut key.
           If needed use modifiers like Shift- and Alt_ or Option-
           as before the shortcut key character.  Do not include
           the Command- or Control- modifier nor the <...> brackets
           since those are handled here, depending on platform and
           as needed for the binding.
        '''
        # <https://TkDocs.com/tutorial/menus.html>
        if not key:
            self.add_command(label=label, command=command, **kwds)

        elif _isMacOS:
            # keys show as upper-case, always
            self.add_command(label=label, accelerator='Command-' + key,
                                          command=command, **kwds)
            self.bind_shortcut(key, command, label)

        else:  # XXX not tested, not tested, not tested
            self.add_command(label=label, underline=label.lower().index(key),
                                          command=command, **kwds)
            self.bind_shortcut(key, command, label)

    def bind_shortcut(self, key, command, label=None):
        """Bind shortcut key, default modifier Command/Control.
        """
        # The accelerator modifiers on macOS are Command-,
        # Ctrl-, Option- and Shift-, but for .bind[_all] use
        # <Command-..>, <Ctrl-..>, <Option_..> and <Shift-..>,
        # <https://www.Tcl.Tk/man/tcl8.6/TkCmd/bind.htm#M6>
        if self._shortcuts_widget:
            if C_Key.lower() not in key.lower():
                key = "<%s%s>" % (C_Key, key.lstrip('<').rstrip('>'))
            self._shortcuts_widget.bind(key, command)
            # remember the shortcut key for this menu item
            if label is not None:
                item = self.index(label)
                self._shortcuts_entries[item] = key
        # The Tk modifier for macOS' Command key is called
        # Meta, but there is only Meta_L[eft], no Meta_R[ight]
        # and both keyboard command keys generate Meta_L events.
        # Similarly for macOS' Option key, the modifier name is
        # Alt and there's only Alt_L[eft], no Alt_R[ight] and
        # both keyboard option keys generate Alt_L events.  See:
        # <https://StackOverflow.com/questions/6378556/multiple-
        # key-event-bindings-in-tkinter-control-e-command-apple-e-etc>

    def bind_shortcuts_to(self, widget):
        '''Set the widget for the shortcut keys, usually root.
        '''
        self._shortcuts_widget = widget

    def entryconfig(self, item, **kwds):
        """Update shortcut key binding if menu entry changed.
        """
        Tk.Menu.entryconfig(self, item, **kwds)
        # adjust the shortcut key binding also
        if self._shortcuts_widget:
            key = self._shortcuts_entries.get(item, None)
            if key is not None and "command" in kwds:
                self._shortcuts_widget.bind(key, kwds["command"])


class Player(Tk.Frame):
    """The main window has to deal with events.
    """
    _geometry = ''
    _stopped  = None

    def __init__(self, parent, title=None, video=''):
        Tk.Frame.__init__(self, parent)

        self.parent = parent  # == root
        self.parent.title(title or "tkVLCplayer")
        self.video = expanduser(video)
        self._isWindows = _isWindows
        # Menu Bar
        #   File Menu
        menubar = Tk.Menu(self.parent)
        self.parent.config(menu=menubar)

        fileMenu = _Tk_Menu(menubar)
        fileMenu.bind_shortcuts_to(parent)  # XXX must be root?

        fileMenu.add_shortcut("Open...", 'o', self.OnOpen)
        fileMenu.add_separator()
        fileMenu.add_shortcut("Play", 'p', self.OnPlay)  # Play/Pause
        fileMenu.add_command(label="Stop", command=self.OnStop)
        fileMenu.add_separator()
        fileMenu.add_shortcut("Mute", 'm', self.OnMute)
        fileMenu.add_separator()
        fileMenu.add_shortcut("Up", 'u', self.LogTime)
        fileMenu.add_separator()
        fileMenu.add_shortcut("Close", 'w' if _isMacOS else 's', self.OnClose)
        if _isMacOS:  # intended for and tested on macOS
            fileMenu.add_separator()
            fileMenu.add_shortcut("Full Screen", 'f', self.OnFullScreen)
        menubar.add_cascade(label="File", menu=fileMenu)
        self.fileMenu = fileMenu
        self.playIndex = fileMenu.index("Play")
        self.muteIndex = fileMenu.index("Mute")

        # first, top panel shows video

        self.videopanel = ttk.Frame(self.parent)
        self.canvas = Tk.Canvas(self.videopanel)
        self.canvas.pack(fill=Tk.BOTH, expand=1)
        self.videopanel.pack(fill=Tk.BOTH, expand=1)

         # rl: lets try adding some stats
        self.statsLable = Tk.Label(self.parent, text='Stats:')
        self.statsLable.pack()
        self.statsLable.config(font=("Courier", 44))
        self.statsLable.config(fg="#0000FF")
        self.statsLable.config(bg="yellow")
       
        # my attempt at a clips pannel

        # self.clipspanel = Tk.Toplevel(self.parent)
        # self.buttons_panel.title("Clip Log")

        # panel to hold buttons
        self.buttons_panel = Tk.Toplevel(self.parent)
        self.buttons_panel.title("")
        self.is_buttons_panel_anchor_active = False

        buttons = ttk.Frame(self.buttons_panel)
        self.playButton = ttk.Button(buttons, text="Play", command=self.OnPlay)
        stop            = ttk.Button(buttons, text="Stop", command=self.OnStop)
        self.muteButton = ttk.Button(buttons, text="Mute", command=self.OnMute)
        self.playButton.pack(side=Tk.LEFT)
        stop.pack(side=Tk.LEFT)
        self.muteButton.pack(side=Tk.LEFT)

        self.volMuted = False
        self.volVar = Tk.IntVar()
        self.volSlider = Tk.Scale(buttons, variable=self.volVar, command=self.OnVolume,
                                  from_=0, to=100, orient=Tk.HORIZONTAL, length=200,
                                  showvalue=0, label='Volume')
        self.volSlider.pack(side=Tk.RIGHT)
        buttons.pack(side=Tk.BOTTOM, fill=Tk.X)


        # panel to hold player time slider
        timers = ttk.Frame(self.buttons_panel)
        self.timeVar = Tk.DoubleVar()
        self.timeSliderLast = 0
        self.timeSlider = Tk.Scale(timers, variable=self.timeVar, command=self.OnTime,
                                   from_=0, to=1000, orient=Tk.HORIZONTAL, length=500,
                                   showvalue=0)  # label='Time',
        self.timeSlider.pack(side=Tk.BOTTOM, fill=Tk.X, expand=1)
        self.timeSliderUpdate = time.time()
        timers.pack(side=Tk.BOTTOM, fill=Tk.X)


        # VLC player
        args = ["--sub-source=marq"]
        if _isLinux:
            args.append('--no-xlib')
        self.Instance = vlc.Instance(args)
        self.player = self.Instance.media_player_new()

        self.parent.bind("<Configure>", self.OnConfigure)  # catch window resize, etc.
        self.parent.update()

        # After parent.update() otherwise panel is ignored.
        self.buttons_panel.overrideredirect(True)

        # Estetic, to keep our video panel at least as wide as our buttons panel.
        self.parent.minsize(width=502, height=0)

        if _isMacOS:
            # Only tested on MacOS so far. Enable for other OS after verified tests.
            self.is_buttons_panel_anchor_active = True

            # Detect dragging of the buttons panel.
            self.buttons_panel.bind("<Button-1>", lambda event: setattr(self, "has_clicked_on_buttons_panel", event.y < 0))
            self.buttons_panel.bind("<B1-Motion>", self._DetectButtonsPanelDragging)
            self.buttons_panel.bind("<ButtonRelease-1>", lambda _: setattr(self, "has_clicked_on_buttons_panel", False))
            self.has_clicked_on_buttons_panel = False
        else:
            self.is_buttons_panel_anchor_active = False

        self._AnchorButtonsPanel()

        self.OnTick()  # set the timer up
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
        
        self.currentClipId = 0

    def createOrGetLog(self):
        log = False
        if self.player.get_media():
            media = self.player.get_media()
            filename = basename(self.bytes_to_str(media.get_mrl()))
            if _isWindows:
                filebase = 'cliplogs\\'
            else:
                filebase = 'cliplogs/'
            self.logname = f"{filebase}{filename.split('.')[0]}.csv"
            #Create the log for this video
            if not exists(self.logname):
                logFile = open(self.logname,'w')
                logFile.write('id,startMs,endMs,desc,chars\n')
                logFile.close
        # Get the log for this video
        self.log = getLog(self.logname)
        self.maxId = self.getMaxId()
        # Display the clip manager
        self.clipManager = ClipManager(self)
        self.clipManager.lower()

    def OnClose(self, *unused):
        """Closes the window and quit.
        """
        # print("_quit: bye")
        self.parent.quit()  # stops mainloop
        self.parent.destroy()  # this is necessary on Windows to avoid
        # ... Fatal Python Error: PyEval_RestoreThread: NULL tstate

    def _DetectButtonsPanelDragging(self, _):
        """If our last click was on the boarder
           we disable the anchor.
        """
        if self.has_clicked_on_buttons_panel:
            self.is_buttons_panel_anchor_active = False
            self.buttons_panel.unbind("<Button-1>")
            self.buttons_panel.unbind("<B1-Motion>")
            self.buttons_panel.unbind("<ButtonRelease-1>")

    def _AnchorButtonsPanel(self):
        video_height = self.parent.winfo_height()
        panel_x = self.parent.winfo_x()
        panel_y = self.parent.winfo_y() + video_height + 23 # 23 seems to put the panel just below our video.
        panel_height = self.buttons_panel.winfo_height()
        panel_width = self.parent.winfo_width()
        self.buttons_panel.geometry("%sx%s+%s+%s" % (panel_width, panel_height, panel_x, panel_y))

    def OnConfigure(self, *unused):
        """Some widget configuration changed.
        """
        # <https://www.Tcl.Tk/man/tcl8.6/TkCmd/bind.htm#M12>
        self._geometry = ''  # force .OnResize in .OnTick, recursive?

        if self.is_buttons_panel_anchor_active:
            self._AnchorButtonsPanel()

    def OnFullScreen(self, *unused):
        """Toggle full screen, macOS only.
        """
        # <https://www.Tcl.Tk/man/tcl8.6/TkCmd/wm.htm#M10>
        f = not self.parent.attributes("-fullscreen")  # or .wm_attributes
        if f:
            self._previouscreen = self.parent.geometry()
            self.parent.attributes("-fullscreen", f)  # or .wm_attributes
            self.parent.bind("<Escape>", self.OnFullScreen)
        else:
            self.parent.attributes("-fullscreen", f)  # or .wm_attributes
            self.parent.geometry(self._previouscreen)
            self.parent.unbind("<Escape>")

    def OnMute(self, *unused):
        """Mute/Unmute audio.
        """
        # audio un/mute may be unreliable, see vlc.py docs.
        self.volMuted = m = not self.volMuted  # self.player.audio_get_mute()
        self.player.audio_set_mute(m)
        u = "Unmute" if m else "Mute"
        self.fileMenu.entryconfig(self.muteIndex, label=u)
        self.muteButton.config(text=u)
        # update the volume slider text
        self.OnVolume()


    def OnOpen(self, *unused):
        """Pop up a new dialow window to choose a file, then play the selected file.
        """
        # if a file is already running, then stop it.
        self.OnStop()
        # Create a file dialog opened in the current home directory, where
        # you can display all kind of files, having as title "Choose a video".
        video = askopenfilename(initialdir = Path(expanduser("~")),
                                title = "Choose a video",
                                filetypes = (("all files", "*.*"),
                                             ("mp4 files", "*.mp4"),
                                             ("mkv files", "*.mkv"),
                                             ("mov files", "*.mov")))
        self._Play(video)

    def _Pause_Play(self, playing):
        # re-label menu item and button, adjust callbacks
        p = 'Pause' if playing else 'Play'
        c = self.OnPlay if playing is None else self.OnPause
        self.fileMenu.entryconfig(self.playIndex, label=p, command=c)
        # self.fileMenu.bind_shortcut('p', c)  # XXX handled
        self.playButton.config(text=p, command=c)
        self._stopped = False

    def _Play(self, video):
        # helper for OnOpen and OnPlay
        if isfile(video):  # Creation
            m = self.Instance.media_new(str(video))  # Path, unicode
            self.player.set_media(m)
            self.parent.title("Clip Logger - %s" % (basename(video),))
            self.createOrGetLog()
            # set the window id where to render VLC's video output
            h = self.videopanel.winfo_id()  # .winfo_visualid()?
            if _isWindows:
                self.player.set_hwnd(h)
            elif _isMacOS:
                # XXX 1) using the videopanel.winfo_id() handle
                # causes the video to play in the entire panel on
                # macOS, covering the buttons, sliders, etc.
                # XXX 2) .winfo_id() to return NSView on macOS?
                v = _GetNSView(h)
                if v:
                    self.player.set_nsobject(v)
                else:
                    self.player.set_xwindow(h)  # plays audio, no video
            else:
                self.player.set_xwindow(h)  # fails on Windows
            self.currentVideo = str(video)
            # FIXME: this should be made cross-platform
            self.OnPlay()

    def OnPause(self, *unused):
        """Toggle between Pause and Play.
        """
        if self.player.get_media():
            self._Pause_Play(not self.player.is_playing())
            self.player.pause()  # toggles

    def get_stats(self):
        if self.player.get_media():
            return str(self.player.get_fps())

    def OnPlay(self, *unused):
        """Play video, if none is loaded, open the dialog window.
        """
        # if there's no video to play or playing,
        # open a Tk.FileDialog to select a file
        if not self.player.get_media():
            if self.video:
                self._Play(expanduser(self.video))
                self.video = ''
            else:
                self.OnOpen()
        # Try to play, if this fails display an error message
        elif self.player.play():  # == -1
            self.showError("Unable to play the video.")
        else:
            self._Pause_Play(True)
            # set volume slider to audio level
            vol = self.player.audio_get_volume()
            if vol > 0:
                self.volVar.set(vol)
                self.volSlider.set(vol)
            #rl disable subtitles!
            print('Disabling subtitles...')
            self.player.video_set_spu(-1)

    def OnResize(self, *unused):
        """Adjust the window/frame to the video aspect ratio.
        """
        g = self.parent.geometry()
        if g != self._geometry and self.player:
            u, v = self.player.video_get_size()  # often (0, 0)
            if v > 0 and u > 0:
                # get window size and position
                g, x, y = g.split('+')
                w, h = g.split('x')
                # alternatively, use .winfo_...
                # w = self.parent.winfo_width()
                # h = self.parent.winfo_height()
                # x = self.parent.winfo_x()
                # y = self.parent.winfo_y()
                # use the video aspect ratio ...
                if u > v:  # ... for landscape
                    # adjust the window height
                    h = round(float(w) * v / u)
                else:  # ... for portrait
                    # adjust the window width
                    w = round(float(h) * u / v)
                self.parent.geometry("%sx%s+%s+%s" % (w, h, x, y))
                self._geometry = self.parent.geometry()  # actual

    def OnStop(self, *unused):
        """Stop the player, resets media.
        """
        if self.player:
            self.player.stop()
            self._Pause_Play(None)
            # reset the time slider
            self.timeSlider.set(0)
            self._stopped = True
        # XXX on macOS libVLC prints these error messages:
        # [h264 @ 0x7f84fb061200] get_buffer() failed
        # [h264 @ 0x7f84fb061200] thread_get_buffer() failed
        # [h264 @ 0x7f84fb061200] decode_slice_header error
        # [h264 @ 0x7f84fb061200] no frame!

    def OnTick(self):
        """Timer tick, update the time slider to the video time.
        """
        if self.player:
            # since the self.player.get_length may change while
            # playing, re-set the timeSlider to the correct range
            t = self.player.get_length() * 1e-3  # to seconds
            if t > 0:
                self.timeSlider.config(to=t)

                t = self.player.get_time() * 1e-3  # to seconds
                # don't change slider while user is messing with it
                if t > 0 and time.time() > (self.timeSliderUpdate + 2):
                    self.timeSlider.set(t)
                    self.timeSliderLast = int(self.timeVar.get())
        # start the 1 second timer again
        self.parent.after(100, self.OnTick)
        # adjust window to video aspect ratio, done periodically
        # on purpose since the player.video_get_size() only
        # returns non-zero sizes after playing for a while
        if not self._geometry:
            self.OnResize()

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
        
    def OnTime(self, *unused):
        if self.player:
            t = self.timeVar.get()
            if self.timeSliderLast != int(t):
                # this is a hack. The timer updates the time slider.
                # This change causes this rtn (the 'slider has changed' rtn)
                # to be invoked.  I can't tell the difference between when
                # the user has manually moved the slider and when the timer
                # changed the slider.  But when the user moves the slider
                # tkinter only notifies this rtn about once per second and
                # when the slider has quit moving.
                # Also, the tkinter notification value has no fractional
                # seconds.  The timer update rtn saves off the last update
                # value (rounded to integer seconds) in timeSliderLast if
                # the notification time (sval) is the same as the last saved
                # time timeSliderLast then we know that this notification is
                # due to the timer changing the slider.  Otherwise the
                # notification is due to the user changing the slider.  If
                # the user is changing the slider then I have the timer
                # routine wait for at least 2 seconds before it starts
                # updating the slider again (so the timer doesn't start
                # fighting with the user).
                self.player.set_time(int(t * 1e3))  # milliseconds
                self.timeSliderUpdate = time.time()

    def OnVolume(self, *unused):
        """Volume slider changed, adjust the audio volume.
        """
        vol = min(self.volVar.get(), 100)
        v_M = "%d%s" % (vol, " (Muted)" if self.volMuted else '')
        self.volSlider.config(label="Volume " + v_M)
        if self.player and not self._stopped:
            # .audio_set_volume returns 0 if success, -1 otherwise,
            # e.g. if the player is stopped or doesn't have media
            if self.player.audio_set_volume(vol):  # and self.player.get_media():
                self.showError("Failed to set the volume: %s." % (v_M,))

    def showError(self, message):
        """Display a simple error dialog.
        """
        self.OnStop()
        showerror(self.parent.title(), message)
    
    def bytes_to_str(self,b):
        """Translate bytes to string.
        """
        if isinstance(b, bytes):
            return b.decode(DEFAULT_ENCODING)
        else:
            return b

    ## Stolen from the bottom of vlc.py
    def mspf(self):
            """Milliseconds per frame"""
            return int(1000 // (self.player.get_fps() or 25))

    def print_info(self):
        media = self.player.get_media()
        print('State: %s' % self.player.get_state())
        print('Media: %s' % self.bytes_to_str(media.get_mrl()))
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

    def getOutputPath(self):
        videoFileName = basename(self.currentVideo).split(".")[0]
        Path(videoFileName).mkdir(parents=True, exist_ok=True)
        return f"exports/{videoFileName}"
    
    def captureStillByType(self, type):
        if not self.player.is_playing():
            currentFrame = int(self.player.get_time() / self.mspf())
            outputPath = f"{self.getOutputPath()}/stills"
            Path(outputPath).mkdir(parents=True, exist_ok=True)
            outputFile = f"{outputPath}/{currentFrame}_{type}.png"
            self.player.video_take_snapshot(0,outputFile,0,0)

    def printCurrentFrame(self):
        print(self.player.get_time())
        print(self.mspf())
        print( int(self.player.get_time() / self.mspf()))

# Description Popup
class PopUp(Tk.Tk):
    def __init__(self,parent):      
        Tk.Tk.__init__(self) 
        self.parent = parent
        self.clipData = parent.wip
        # self.popup = Tk.Toplevel(parent)
        self.wm_title("Clip # Description")
        self.tkraise(self)
        Tk.Label(self, text="Describe this clip").pack(side="left", fill="x", pady=10, padx=10)
        self.mystring = Tk.StringVar(self)
        self.entry = Tk.Entry(self,textvariable = self.mystring, bd=1, width=20)
        self.entry.pack(side="left", fill="x")
        self.button = Tk.Button(self, text="Save", command=self.on_button)
        self.button.pack()
        self.entry.focus_set()      

    def on_button(self):
        # print(self.mystring.get())
        self.destroy()
        print(self.mystring.get())
        self.clipData['desc'] = self.mystring.get()#.replace('"','\\"')
        self.clipData['chars']='[]'
        #3 logs... uhg
        logClip(self.clipData)
        self.parent.clipManager.addEntry(self.clipData)
        self.parent.log.append(self.clipData)
        return 



def open_popup():
    return PopUp()

# Clip storage:
# Currently updating in 3 places... would rather these be event driven updates...
def logClip(logLine):
    with open(logLine['logname'],'a') as f:
        out = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        out.writerow([logLine['id'],logLine['startMs'],logLine['endMs'],logLine['desc'],logLine['chars']])
    jsonOut = {logLine['id']:[logLine['startMs'], logLine['endMs'],f"{logLine['desc']}",logLine['chars']]}
    return jsonOut

def getLog(logname):
    maxClip = 0
    logFile = open(logname,'r')
    log = list(csv.DictReader(logFile))
    logFile.close()
    return log




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
    player = Player(root, video=_video)
    root.protocol("WM_DELETE_WINDOW", player.OnClose)  # XXX unnecessary (on macOS)
    
    
    root.bind('<Left>',lambda x: player.skip_sec(-10))
    root.bind('<Right>',lambda x: player.skip_sec(10))
    root.bind('<Shift-Left>',lambda x: player.skip_frame(-2))
    root.bind('<Shift-Right>',lambda x: player.skip_frame(2))
    root.bind('<Escape>',lambda x: player.quit())
    root.bind('<Up>',lambda x: player.startClip())
    root.bind('<Down>',lambda x: player.endClip())
    root.bind('<p>',lambda x: player.printCurrentFrame())
    root.bind('<space>',lambda x: player.OnPause())
    root.bind('<r>',lambda x: player._Play('gurlag01.mkv'))

    # bindings for capturing stills
    root.bind('<o>',lambda x: player.captureStillByType('open'))
    root.bind('<m>',lambda x: player.captureStillByType('mid'))
    root.bind('<c>',lambda x: player.captureStillByType('closed'))
    

    
    root.focus_force()

    
    root.mainloop()