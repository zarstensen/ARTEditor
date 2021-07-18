from tkinter import *
from tkinter import ttk
import tkinter as tk
from src.ColorPicker import ColorPicker, RGBA


class Toolbar(ttk.Frame):
    """a widget containing the toolbar of the ARTEditor"""

    def __init__(self, root):
        super().__init__(root)

        self.root = root

        self.columnconfigure([1, 2, 3], weight=1)
        self.rowconfigure([1, 2, 3, 4, 5], weight=1)

        # setup color pickers
        self.foreground_picker = ColorPicker(self, "color", width=80, height=80)
        self.background_picker = ColorPicker(self, "background color")

        self.foreground_picker.grid(column=1, row=5)
        self.background_picker.grid(column=2, row=5)
