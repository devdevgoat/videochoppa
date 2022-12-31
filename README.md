# Videochoppa
 Need a simple way to tag video files for clipping later.

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

1. Use the following short cut keys to generate a tag file

key | action
------------- | ------
Up Arrow | tag clip begining point
Down Arrow | end clip
Left Arrow | skip back 10 seconds
Right Arrow | skip forward 10 seconds
Shift Left Arrow | Pause and scrub back one frame
Shift Right Arrow | Pause and scrub forward one frame
Space Bar | Play/Pause
Escape | Close video

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
- popup for title, desc of clip
- popup mode toggle for pausing, typing, and then resuming
- overlays
  - ms/timer
  - length of pending clip
  - clip title?
- gui
  - clip log
  - click log entry to play?


## Short cuts
key | action
------------- | ------
T | Add details/notes to clip
C | Cut all clips




