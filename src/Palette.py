from tkinter import *
from tkinter import ttk


class PaletteData:
    def __init__(self, character=None, foreground=None, background=None):
        self.character = character
        self.foreground_color = foreground
        self.background_color = background

        self.char = self.character
        self.fg = self.foreground_color
        self.bg = self.background_color

    def __eq__(self, other):
        return other.character == self.character and \
               other.foreground_color == self.foreground_color and \
               other.background_color == self.background_color


class PaletteElem(ttk.Frame):
    """
    stores a character and its back and foreground color.
    a callback with the current values stored is called when it is clicked on.
    """

    def __init__(self, root, character=None, foreground=None, background=None, font_width=None,
                 height=None, *args, **kwargs):
        self.root = root

        self.width = font_width
        self.height = height

        super().__init__(root, *args, **kwargs)

        self.data = PaletteData(character, foreground, background)
        self.clickCallback = None

        # configure border
        self.s = ttk.Style()

        self.s.configure("PaletteReleased.TFrame", relief="raised",
                         borderwidth=3)
        self.s.configure("PalettePressed.TFrame", relief="sunken",
                         borderwidth=3)

        self['style'] = 'PaletteReleased.TFrame'

        # setup palette visualization font and size
        self.palette_vis = Label(self, font=("TkFixedFont", self.width), width=1)
        self.palette_vis.grid(column=0, row=0)

        self.updateVis()

        # setup event callbacks

        self.bind('<1>', self.__pressCallback)
        self.palette_vis.bind('<1>', self.__pressCallback)

    def onClick(self, func):

        """function should accept a PaletteElem, PaletteData and a ButtonPress event as arguments"""

        if func is not None:
            self.clickCallback = lambda e: func(self, self.data, e)
        else:
            self.clickCallback = None

    def __pressCallback(self, e):
        if self.clickCallback is not None:
            self.clickCallback(e)

    def updateVis(self):
        character = self.data.character
        fg = self.data.foreground_color
        bg = self.data.background_color

        if character is None:
            self.palette_vis.configure(text=' ')
        else:
            self.palette_vis.configure(text=character)

        if fg is not None:
            self.palette_vis.configure(fg=self.data.foreground_color.rgbHex())
        else:
            self.palette_vis.configure(fg=None)

        if bg is not None:
            self.palette_vis.configure(bg=self.data.background_color.rgbHex())
        else:
            self.palette_vis.configure(bg=self.s.lookup('PaletteElem.TFrame', 'background'))

        self.grid_configure(ipadx=self.width, ipady=self.height)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.update()




class Palette(ttk.Frame):
    """
    A widget interface for interacting with multiple PaletteElem's.
    """

    def __init__(self, root, palette_grid=(12, 5), *args, **kwargs):
        self.root = root

        super().__init__(root, *args, **kwargs)

        # configure style
        self.s = ttk.Style()

        self.s.configure('Palette.TFrame', relief="sunken",
                         borderwidth=1, background='gray75')

        self.s.configure('PaletteSelector.TFrame',
                         background='gray75')

        self.s.configure('Options.TFrame',
                         relief='groove', borderwidth=1, background='gray75')

        self['style'] = 'Palette.TFrame'

        # configure stretching
        # self.columnconfigure(0, weight=1)
        # self.rowconfigure(0, weight=1)
        # self.rowconfigure(1, minsize=20)

        # setup palette frame

        self.palette_grid = list(palette_grid)

        self.palette_frame = ttk.Frame(self, style='PaletteSelector.TFrame')
        self.palette_frame.grid(column=0, row=0, sticky='NW')

        self.palette_elems = [[
            PaletteElem(self.palette_frame, font_width=9, height=9) for _ in range(self.palette_grid[0])
        ] for _ in range(self.palette_grid[1])]

        self.palette_data = []
        self.selected_palettes = []

        for y, row in enumerate(self.palette_elems):
            for x, p_elem in enumerate(row):
                p_elem.grid(column=x, row=y, sticky='NSEW')
                p_elem.onClick(self.__paletteClickCallback)

        # setup options
        self.option_frame = ttk.Frame(self, style='Options.TFrame')

        self.option_frame.columnconfigure(6, weight=1)

        self.current_preset = 1
        self.preset_count = 0
        self.current_preset_text = StringVar()

        self.s.configure('PLabel.TLabel',
                         background=self.s.lookup('Options.TFrame', 'background'))

        self.current_preset_text.set(f"{self.current_preset}/{self.preset_count}")
        self.current_preset_label = ttk.Label(self.option_frame, textvariable=self.current_preset_text,
                                              style='PLabel.TLabel')

        self.__extendPreset()

        # buttons
        self.s.configure('PButton.TButton', width=0, height=0)

        self.load_button = ttk.Button(self.option_frame, text='↓', style='PButton.TButton')

        self.store_all_button = ttk.Button(self.option_frame, text='↑', style='PButton.TButton')

        self.store_character_button = ttk.Button(self.option_frame, text='ch ↑', style='PButton.TButton')
        self.store_background_button = ttk.Button(self.option_frame, text='bg ↑', style='PButton.TButton')
        self.store_foreground_button = ttk.Button(self.option_frame, text='fg ↑', style='PButton.TButton')

        self.left_button = ttk.Button(self.option_frame, text='<', style='PButton.TButton', command=self.__lbClick)
        self.right_button = ttk.Button(self.option_frame, text='>', style='PButton.TButton', command=self.__rbClick)

        self.extend_button = ttk.Button(self.option_frame, text='+', style='PButton.TButton',
                                        command=self.__extendPreset)
        self.shrink_button = ttk.Button(self.option_frame, text='-', style='PButton.TButton',
                                        command=self.__shrinkPreset)
        self.clear_button = ttk.Button(self.option_frame, text='cl', style='PButton.TButton',
                                       command=self.__clearPreset)

        # layout

        self.option_frame.grid(column=0, row=1, sticky='NSEW')
        self.option_frame.columnconfigure(2, minsize=25)

        self.left_button.grid(column=0, row=0, sticky='W', padx=(5, 1))
        self.right_button.grid(column=1, row=0, sticky='W', padx=(1, 5))

        self.current_preset_label.grid(column=2, row=0, sticky='WE')

        self.extend_button.grid(column=3, row=0, sticky='w', padx=(10, 1))
        self.shrink_button.grid(column=4, row=0, sticky='w', padx=(1, 0))

        self.clear_button.grid(column=5, row=0, sticky='W', padx=5)

        self.store_background_button.grid(column=7, row=0, sticky='E', pady=5, padx=5)
        self.store_foreground_button.grid(column=8, row=0, sticky='E', pady=5, padx=5)
        self.store_character_button.grid(column=9, row=0, sticky='E', pady=5, padx=5)
        self.store_all_button.grid(column=10, row=0, sticky='E', pady=5, padx=(5, 15))
        self.load_button.grid(column=11, row=0, sticky='E', pady=5, padx=5)

        self.__updatePalettes()

    def loadCallback(self, func):
        """
        Function passed should accept a PaletteData argument.
        The function will be called when the [LOAD] button is pressed and the active palette will be passed
        """

        if func is not None:
            self.load_button['command'] = lambda: func(self.selected_palettes[self.current_preset - 1].data)
        else:
            self.load_button['command'] = None

    def storeAllCallback(self, func):
        """
        Function passed should return a PaletteData element to be stored.
        Does not take any arguments.
        """

        if func is not None:
            def l_callback():
                pos = self.posFromPalette(self.selected_palettes[self.current_preset - 1])
                self.palette_data[self.current_preset - 1][pos[0]][pos[1]] = func()
                self.__updatePalettes()

            self.store_all_button['command'] = l_callback
        else:
            self.store_all_button['command'] = None

    def storeBackgroundCallback(self, func):
        """
        Function passed should return a background color to be stored.
        Does not take any arguments.
        """

        if func is not None:
            def l_callback():
                pos = self.posFromPalette(self.selected_palettes[self.current_preset - 1])
                self.palette_data[self.current_preset - 1][pos[0]][pos[1]].background_color = func()
                self.__updatePalettes()

            self.store_background_button['command'] = l_callback
        else:
            self.store_background_button['command'] = None

    def storeForegroundCallback(self, func):
        """
        Function passed should return a foreground color to be stored.
        Does not take any arguments.
        """

        if func is not None:
            def l_callback():
                pos = self.posFromPalette(self.selected_palettes[self.current_preset - 1])
                self.palette_data[self.current_preset - 1][pos[0]][pos[1]].foreground_color = func()
                self.__updatePalettes()

            self.store_foreground_button['command'] = l_callback
        else:
            self.store_foreground_button['command'] = None

    def storeCharacterCallback(self, func):
        """
        Function passed should return a character to be stored.
        Does not take any arguments.
        """

        if func is not None:
            def l_callback():
                pos = self.posFromPalette(self.selected_palettes[self.current_preset - 1])
                self.palette_data[self.current_preset - 1][pos[0]][pos[1]].character = func()
                self.__updatePalettes()

            self.store_character_button['command'] = l_callback
        else:
            self.store_character_button['command'] = None

    def posFromPalette(self, p_elem):
        for y, row in enumerate(self.palette_elems):
            for x, elem in enumerate(row):
                if elem is p_elem:
                    return [y, x]

        return None

    def __extendPreset(self):
        self.palette_data.insert(self.current_preset, [[
            PaletteData() for x in range(self.palette_grid[0])
        ] for y in range(self.palette_grid[1])])

        self.selected_palettes.insert(self.current_preset, self.palette_elems[0][0])

        self.preset_count += 1

        self.__updatePalettes()

    def __shrinkPreset(self):
        if self.preset_count != 1:
            del self.palette_data[self.current_preset - 1]
            del self.selected_palettes[self.current_preset - 1]

            if self.current_preset == self.preset_count:
                self.current_preset -= 1

            self.preset_count -= 1

            self.__updatePalettes()

    def __clearPreset(self):
        for y in range(len(self.palette_data[self.current_preset - 1])):
            for x in range(len(self.palette_data[self.current_preset - 1][y])):
                self.palette_data[self.current_preset - 1][y][x] = PaletteData()

        self.__updatePalettes()

    def __updatePalettes(self):
        self.current_preset_text.set(f"{self.current_preset}/{self.preset_count}")

        for row_data, row_elem in zip(self.palette_data[self.current_preset - 1], self.palette_elems):
            for col_data, col_elem in zip(row_data, row_elem):
                col_elem.data = col_data
                col_elem.updateVis()

                if self.selected_palettes[self.current_preset - 1] is col_elem:
                    col_elem['style'] = 'PalettePressed.TFrame'
                else:
                    col_elem['style'] = 'PaletteReleased.TFrame'

    def __paletteClickCallback(self, palette, data, event):
        self.selected_palettes[self.current_preset - 1] = palette

        self.__updatePalettes()

    def __lbClick(self):
        self.current_preset -= 1
        self.current_preset = max(1, self.current_preset)

        self.__updatePalettes()

    def __rbClick(self):
        self.current_preset += 1
        self.current_preset = min(self.preset_count, self.current_preset)

        self.__updatePalettes()


if __name__ == "__main__":
    root = Tk()
    root.minsize(300, 300)

    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    p = Palette(root)
    p.grid(column=0, row=0, sticky='NSEW')

    root.mainloop()
