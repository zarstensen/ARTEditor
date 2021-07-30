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

        self.s = ttk.Style()

        self.change_callback = None

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
        self.foreground_picker = ColorPicker(self, "Foreground")
        self.background_picker = ColorPicker(self, "Background")

        self.foreground_picker.onColorChange(self.__onForegroundChange)

        # setup mode and size inputs

        self.s.configure('EditorOp.TFrame', relief='sunken', borderwidth=3)

        self.editor_frame = ttk.Frame(self)
        self.editor_frame.columnconfigure(0, weight=1)
        self.editor_frame.rowconfigure(1, weight=1)

        self.editor_label = ttk.Label(self.editor_frame, text='Editor Options')

        self.editor_options = ttk.Frame(self.editor_frame, style='EditorOp.TFrame')

        self.box_toggle = BooleanVar()
        self.toggle_box = Checkbutton(self.editor_options, text='▦', variable=self.box_toggle, indicatoron=False, font='TkDefault 30')

        def validate(val):
            if val == '':
                return True

            try:
                return int(val) > 0
            except ValueError:
                return False

        self.width_label = ttk.Label(self.editor_options, text='Width ')
        self.width_value = StringVar()
        self.width_input = ttk.Entry(self.editor_options, width=3, textvariable=self.width_value,
                                     validate='key', validatecommand=(self.register(validate), '%P'))

        self.height_label = ttk.Label(self.editor_options, text='Height ')
        self.height_value = StringVar()
        self.height_input = ttk.Entry(self.editor_options, width=3, textvariable=self.height_value,
                                      validate='key', validatecommand=(self.register(validate), '%P'))

        # organize layout

        self.palette.grid(column=0, row=0, columnspan=5, rowspan=2, padx=5, pady=5, sticky='NW')

        self.character_picker.grid(column=0, row=3, sticky='NSEW')

        self.foreground_picker.grid(column=0, row=5, ipady=60, sticky='NSEW')
        self.background_picker.grid(column=2, row=5, ipady=60, sticky='NSEW')

        self.editor_frame.grid(column=2, row=3, sticky='NSEW')
        self.editor_label.grid(column=0, row=0, sticky='NSW')
        self.editor_options.grid(column=0, row=1, sticky='NSEW')
        self.editor_options.columnconfigure([1, 2], weight=1)
        self.editor_options.rowconfigure([0, 1], weight=1)

        self.toggle_box.grid(column=0, row=0, rowspan=2)

        self.width_label.grid(column=1, row=0, sticky='E')
        self.width_input.grid(column=2, row=0, sticky='EW')

        self.height_label.grid(column=1, row=1, sticky='E')
        self.height_input.grid(column=2, row=1, sticky='EW')

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

    def onPaletteChange(self, func):
        """
        Calls [func] when the active colors or character is changed.
        [func] should accept a PaletteData object containing the new values.
        """

        self.character_picker.onCharacterChanged(lambda c: func(PaletteData(c, self.foreground_picker.color, self.background_picker.color)))
        self.background_picker.onColorChange(lambda c: func(PaletteData(self.character_picker.getChar(), self.foreground_picker.color, c)))
        self.change_callback = func

    def loadData(self, palette_data):

        if palette_data.foreground_color is not None:
            self.foreground_picker.chagneColor(palette_data.foreground_color)

        if palette_data.background_color is not None:
            self.background_picker.chagneColor(palette_data.background_color)

        if palette_data.character is not None:
            self.character_picker.setChar(palette_data.character)

        if self.change_callback is not None:
            self.change_callback(self.getData())

    def getData(self):
        return PaletteData(self.character_picker.getChar(), self.foreground_picker.color, self.background_picker.color)

    def onResizeChange(self, func):
        """
        calls [func] when either the width or height entry has had a [Return] callback.
        [func] should accept the new width and height.
        """

        if func is not None:
            self.width_input.bind('<Return>', lambda e: func(self.width_input.get(), self.height_input.get()))
            self.height_input.bind('<Return>', lambda e: func(self.width_input.get(), self.height_input.get()))
        else:
            self.width_input.unbind('<Return>')
            self.height_input.unbind('<Return>')

    def onBoxToggle(self, func):
        """
        calls [func] when the box mode checkbox has changed.
        [func] should accept a boolean value representing whether box mode is on.
        """

        if func is not None:
            self.toggle_box.bind('<1>', lambda e: func(not self.box_toggle.get()))
        else:
            self.toggle_box.unbind('<1>')

    def __onForegroundChange(self, color):
        self.character_picker.changeForeground(color)

        if self.change_callback is not None:
            self.change_callback(PaletteData(self.character_picker.getChar(), self.foreground_picker, color))


