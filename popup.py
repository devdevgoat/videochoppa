import tkinter as Tk

# Description Popup
class PopUp(Tk.Tk):
    def __init__(self,parent):      
        Tk.Tk.__init__(self) 
        self.parent = parent
        self.clipData = parent.wip
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
        # logClip(self.clipData)
        self.parent.clipManager.addEntry(self.clipData)
        self.parent.log.append(self.clipData)
        return self.clipData