# Videochoppa

I needed a simple way to tag video files for clipping later, so I hacked up an example Python VLC/Tkinter file I found online! The goal of this project is to generate a file I can later use to generate clips from a video file. This is a laborous task in most video editors, but it fairly easy to do in python if you know the timestamps you want. This program lets me quickly save timestamps to a file for chopping later! 

Why do I want to do that? For makeing [AMVs](https://www.youtube.com/c/devdevgoat) of course!

![](img/choppa.png)


# Install

1. Install python 3.10.x
1. Install pipenv:

    ```sh
    pip install --user pipenv
    ```

1. Download this repo, and from the parent directory install the dependancies:

    ``` sh
    git clone https://github.com/devdevgoat/videochoppa.git
    cd videochoppa
    pipenv install 
    ```

1. run file

    ```bash
    pipenv shell 
    python playAndTag.py
    ```

1. Use the following short cut keys to generate a tag file. The general process is:
   1. Use left and right arrows to get to clip
   2. Hold Shift with left or right arrows to go frame by frame
   3. Hit UP arrow (or Down) to start the clip
   4. Hit DOWN arrow to end the clip
   5. Fill in description of clip (optional)
   6. Hit TAB, Space to close popup and commit to log
   7. Review log in /cliplogs folder, will be a CSV with the same name as the video

key | action
------------- | ------
Up Arrow | tag clip begining point
Down Arrow | end clip, triggers up arrow and popup description
Left Arrow | skip back 10 seconds
Right Arrow | skip forward 10 seconds
Shift Left Arrow | Pause and scrub back one frame
Shift Right Arrow | Pause and scrub forward one frame
Space Bar | Play/Pause
Escape | Close video
r | Open sample video

Tag files are stored in the cliplogs folder and have the following structure:

id|start_clip_ms|end_clip_ms|desc|characters
-|-|-|-|-
0|3492|5078|"some text"*|[goku,gohan,chichi]*

\* = pending 
  
# Pending features

- Video clipper that cuts all tagged clips and saves to folder
- Intro/Outro time code setter (getter via api?)
- Meta data grabber/api integration
- character buttons/shortcuts/profiles for tagging characters
- popup for title?, desc (DONE) of clip
- popup mode toggle for pausing, typing, and then resuming
- overlays
  - ms/timer
  - length of pending clip (DONE)
  - clip title?
- gui
  - clip log
  - click log entry to play?
  - clip generator button to cut video

## Short cuts
key | action
------------- | ------
T | Add details/notes to clip
C | Cut all clips

# Issues

VLC on mac, version 3.0.16 does not like set_time very much, and results in a second or two delay in audio resumption on m1 macs (ventura). Uinsg 3.0.18 fixes this, installed via: 

```bash
brew install vlc --cask
```

ffmpeg on mac appears broken for m1, importing moviepy = crash. You have to install the correct version of ffmpeg, and then install moviepy. [src](https://github.com/Zulko/moviepy/issues/1619#issuecomment-1369341762)

Position has an type error, have to update a block in the vlc version for now. [src](https://github.com/oaubert/python-vlc/issues/243)
```python
# Old mappings are in comment form to compare before/after

Position.bottom       = 8  #Position(6)
Position.bottom_left  = 9  #Position(7)
Position.bottom_right = 10 #Position(8)
Position.center       = 0  #Position(0)
Position.disable      = -1 #Position(-1)
Position.left         = 1  #Position(1)
Position.right        = 2  #Position(2)
Position.top          = 4  #Position(3)
Position.top_left     = 5  #Position(4)
Position.top_right    = 6  #Position(5)
```

# Notes/thoughts/ideas?

- Need to improve lip sync workflow, could had a lipflap tool that/feature?
  - maybe use L key to tag lip flap frames, then create 15s clips from each flap? 
  - B could be the base lipflap which gets 15sec, then all others get put to the beginning at 5 sec each?
  - eh, 15 is a yt short, but over kill I'm guessing... maybe everything gets 3 seconds? 
  - 3 frames is the defacto amount though, maybe BMO 3f3f3f? 
  - might be better to export clips to an ep level folder and use clip id's then in that folder have clip based sub folders that have 3frame videos of each lip flap? 1 frame? 