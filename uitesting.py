import tkinter as Tk
from tkinter import ttk

root = Tk.Tk()

root.geometry("900x600")
videopanel = Tk.Frame(root)
canvas = Tk.Canvas(videopanel,highlightbackground='black',highlightthickness=2)
canvas.grid(row=0,column=0,columnspan=2)
# clipmanager = ttk.Frame(root).grid(row=0,column=7,columnspan=3)
clipmanager = Tk.Canvas(root,highlightbackground='red',highlightthickness=2)
clipmanager.grid(row=0,column=7,columnspan=3)

exportButton = ttk.Button(clipmanager, text='Export All')
# exportButton.pack(side=Tk.TOP)
listBox = Tk.Listbox(clipmanager, width=500, height=300)
listBox.insert(0,f"00001 | 100:200000000 | Some text! ")
# listBox.pack()

# canvas.pack(fill=Tk.BOTH, expand=1)
# videopanel.pack(fill=Tk.BOTH, expand=1)


root.mainloop()