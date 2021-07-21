from tkinter import *
from tkinter import ttk
import tkinter as tk
from src.ColorPicker import ColorPicker, RGBA
from src.Palette import Palette


class Toolbar(ttk.Frame):
    """a widget containing the toolbar of the ARTEditor"""

    def __init__(self, root):
        super().__init__(root)

        self.root = root

        self.rowconfigure([1, 2, 3, 4, 5], weight=1)

        # setup palettes
        self.palette = Palette(self, (11, 4))
        self.palette.grid(column=0, row=0, columnspan=5, rowspan=2, padx=5, pady=5, sticky='NW')

        self.palette.storeForegroundCallback(self.storeForeground)
        self.palette.storeBackgroundCallback(self.storeBackground)
        self.palette.loadCallback(self.loadData)

        # setup color pickers
        self.foreground_picker = ColorPicker(self, "Foreground", width=80, height=80)
        self.background_picker = ColorPicker(self, "Background", width=80, height=80)

        self.foreground_picker.grid(column=0, row=5)
        self.background_picker.grid(column=2, row=5)

    def storeForeground(self):
        return self.foreground_picker.color

    def storeBackground(self):
        return self.background_picker.color

    def loadData(self, palette_data):

        if palette_data.foreground_color is not None:
            self.foreground_picker.chagneColor(palette_data.foreground_color)

        if palette_data.background_color is not None:
            self.background_picker.chagneColor(palette_data.background_color)

