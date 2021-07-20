import tkinter
from tkinter import *
from tkinter import ttk
from ColorPicker import RGBA
import time


class PaletteElem(ttk.Frame):
    """
    stores a character and its back and foreground color.
    a callback with the current values stored is called when it is clicked on.
    """

    def __init__(self, root, character=' ', foreground=RGBA('0c0c0c'), background=RGBA('ffffff'), width=None, height=None, *args, **kwargs):
        self.root = root

        super().__init__(root, *args, **kwargs)

        self.character = character
        self.foreground_color = foreground
        self.background_color = background
        self.clickCallback = None

        # configure border
        self.s = ttk.Style()
        self.s.configure("PaletteElem.TFrame", relief="raised",
                         borderwidth=3)

        # apply width and height
        self.configure(style='PaletteElem.TFrame')
        self.grid_configure(ipadx=width, ipady=height)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # setup palette visualization font and size
        self.palette_vis = Label(self, font=("TkFixedFont", width))
        self.palette_vis.grid(column=0, row=0)

        self.updateVis()

    @staticmethod
    def emptyPalette(root, width=None, height=None, *args, **kwargs):
        return PaletteElem(root, None, None, None, width, height, *args, **kwargs)

    def onClick(self, func):
        self.clickCallback = lambda event: func(self.character, self.foreground_color, self.background_color, event)
        self.bind('<1>', self.clickCallback)
        self.palette_vis.bind('<1>', self.clickCallback)

    def updateVis(self):
        """
        updates the labels text and color with the currently stored text and color.
        if the character is None, it will be replaced by a whitespace character.
        if the foreground color is None, the foreground color will be set to its default color (often black).
        if the background color is None, it will be set to the background color of the widget.
        """
        character = self.character
        fg = self.foreground_color
        bg = self.background_color

        if character is None:
            self.palette_vis.configure(text=' ')
        else:
            self.palette_vis.configure(text=character)

        if fg is not None:
            self.palette_vis.configure(fg=self.foreground_color.rgbHex())
        else:
            self.palette_vis.configure(fg=None)

        if bg is not None:
            self.palette_vis.configure(bg=self.background_color.rgbHex())
        else:
            self.palette_vis.configure(bg=self.s.lookup('PaletteElem.TFrame', 'background'))


