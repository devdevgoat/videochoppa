#%%
# Import everything needed to edit video clips
from moviepy.editor import *
from tkinter import *
from tkVideoPlayer import TkinterVideo

  
src = 'gurlag01.mkv'
file = 'gurlag01.txt'

def func(timeInSec):
    file1 = open(file, "a")  # append modexxx
    file1.write(f"{timeInSec}\n")
    file1.close()

def back(timeInSec):
    videoplayer.seek(int(timeInSec)-5)
def fwd(timeInSec):
    tgt = int(timeInSec)+10
    print(f"{timeInSec}>{tgt}")
    videoplayer.seek(tgt)

root = Tk()
root.title("Editor")
root.config(bg="#232323")
root.bind('<Up>',lambda x: func(videoplayer.current_duration()))
root.bind('<Left>',lambda x: back(videoplayer.current_duration()))
root.bind('<Right>',lambda x: fwd(videoplayer.current_duration()))
videoplayer = TkinterVideo(master=root, scaled=True)
videoplayer.load(src)
videoplayer.pack(expand=True, fill="both")
videoplayer.play()
root.focus_force()
root.mainloop()
