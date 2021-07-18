from tkinter import *
from src.Toolbar import Toolbar

root = Tk()
root.minsize(300, 300)

root.columnconfigure([0, 1], weight=1)
root.rowconfigure(0, weight=1)

toolbar = Toolbar(root)
toolbar.grid(column=0, row=0, sticky='nsew')

root.mainloop()
