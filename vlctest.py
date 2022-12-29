#%%

import vlc
src = 'gurlag01.mkv'

media_player = vlc.MediaPlayer()
 
# media object
media = vlc.Media(src)
# setting media to the media player
media_player.set_media(media)
# making keyboard input enable
media_player.video_set_key_input(True)
# start playing video
media_player.play()