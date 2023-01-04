#%%
from mainapp import MainApp


# def OnVideoLoaded(root):
#     media = root.rp.player.get_media()
#     filename = basename(vlc.bytes_to_str(media.get_mrl()))
#     print(f'Playing {filename}')
#     # clipman.buildList(filename.split('.')[0])

if __name__ == "__main__":

    # Create a Tk.App() to handle the windowing event loop
    root = MainApp()

    root.focus_force()

    root.mainloop()