# Import custom library
import vlc
from vlc import Position, VideoMarqueeOption, str_to_bytes

# Import MY libraries
from player import *
from popup import PopUp
from cliplog import ClipLog

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
                self.root.promptForDesc()
    
    def mspf(self):
        """Milliseconds per frame"""
        return int(1000 // (self.player.get_fps() or 25))

