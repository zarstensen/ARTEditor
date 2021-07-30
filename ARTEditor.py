from tkinter import *
from src.Toolbar import Toolbar
from src.TextureEditor import TextureEditor, Modes
from tkinter import ttk

class ARTEditor(ttk.Frame):

    def __init__(self, root, *args, **kwargs):
        self.root = root

        super().__init__(root, *args, **kwargs)

        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        self.toolbar = Toolbar(self)
        self.texture_editor = TextureEditor(self, 10, 10)

        self.toolbar.grid(column=0, row=0, sticky='nsew')
        self.texture_editor.grid(column=1, row=0, sticky='NSEW')

        self.toolbar.onPaletteChange(self.__paletteChange)
        self.toolbar.onResizeChange(self.__onResize)
        self.toolbar.onBoxToggle(self.__onModeToggle)

        self.__paletteChange(self.toolbar.getData())

        self.texture_editor.onCopy(self.__textureCopy)

    def __paletteChange(self, data):
        self.texture_editor.draw_data = data

    def __onResize(self, width, height):
        if width == '':
            width = 1

        if height == '':
            height = 1

        self.texture_editor.resize(int(width), int(height))

    def __onModeToggle(self, mode):

        if mode:
            self.texture_editor.mode = Modes.BOX
        else:
            self.texture_editor.mode = Modes.PEN

    def __textureCopy(self, data):
        self.toolbar.loadData(data)


root = Tk()
root.minsize(300, 300)

root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

editor = ARTEditor(root)
editor.grid(column=0, row=0, sticky='NSEW')


root.mainloop()