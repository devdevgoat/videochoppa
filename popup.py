import tkinter as Tk
# Description Popup
class PopUp(Tk.Tk):
    def __init__(self,parent):      
        Tk.Tk.__init__(self) 
        self.root = parent
        self.clipData = self.root.rb.wip
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
        print(self.mystring.get())
        self.clipData['desc'] = self.mystring.get()#.replace('"','\\"')
        self.clipData['chars']='[]'
        self.root.cliplog.addEntry(self.clipData)
        self.destroy()
        return