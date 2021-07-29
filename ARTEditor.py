from tkinter import *
from src.Toolbar import Toolbar
from src.TextureEditor import TextureEditor

root = Tk()
root.minsize(300, 300)

root.columnconfigure(1, weight=1)
root.rowconfigure(0, weight=1)

toolbar = Toolbar(root)
texture_editor = TextureEditor()

toolbar.grid(column=0, row=0, sticky='nsew')

root.mainloop()
