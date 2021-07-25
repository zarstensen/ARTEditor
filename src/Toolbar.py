from tkinter import *
from tkinter import ttk
import tkinter as tk
from src.ColorPicker import ColorPicker
from src.Palette import Palette, PaletteData
from src.CharacterPicker import CharacterPicker


class Toolbar(ttk.Frame):
    """a widget containing the toolbar of the ARTEditor"""

    def __init__(self, root):
        super().__init__(root)

        self.root = root

        self.rowconfigure(2, weight=1)

        # setup palettes
        self.palette = Palette(self, (11, 4))

        self.palette.storeAllCallback(self.storeAll)

        self.palette.storeForegroundCallback(self.storeForeground)
        self.palette.storeBackgroundCallback(self.storeBackground)
        self.palette.storeCharacterCallback(self.storeCharacter)

        self.palette.loadCallback(self.loadData)

        # setup character picker
        self.character_picker = CharacterPicker(self, "Character", font_width=28, height=5)

        # setup color pickers
        self.foreground_picker = ColorPicker(self, "Foreground", width=80, height=80)
        self.background_picker = ColorPicker(self, "Background", width=80, height=80)

        self.foreground_picker.onColorChange(self.__onForegroundChange)

        # organize layout

        self.palette.grid(column=0, row=0, columnspan=5, rowspan=2, padx=5, pady=5, sticky='NW')

        self.character_picker.grid(column=0, row=3, sticky='NW')

        self.foreground_picker.grid(column=0, row=5, sticky='NW')
        self.background_picker.grid(column=2, row=5, sticky='NW')

    def storeForeground(self):
        return self.foreground_picker.color

    def storeBackground(self):
        return self.background_picker.color

    def storeCharacter(self):
        return self.character_picker.getChar()

    def storeAll(self):
        return PaletteData(character=self.storeCharacter(),
                           foreground=self.storeForeground(),
                           background=self.storeBackground())

    def loadData(self, palette_data):

        if palette_data.foreground_color is not None:
            self.foreground_picker.chagneColor(palette_data.foreground_color)

        if palette_data.background_color is not None:
            self.background_picker.chagneColor(palette_data.background_color)

        if palette_data.character is not None:
            self.character_picker.setChar(palette_data.character)

    def __onForegroundChange(self, color):
        self.character_picker.changeForeground(color)
