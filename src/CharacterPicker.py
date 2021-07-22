from tkinter import *
from tkinter import ttk
from src.Palette import PaletteElem

class CharacterPicker(ttk.Frame):
    """a widget for storing and letting the user modify a character"""

    def __init__(self, root, name="Character", font_width=20, height=20, **kwargs):
        super().__init__(root, **kwargs)

        self.root = root

        self.font_width = font_width
        self.height = height

        # setup name
        self.name = StringVar(root, name)
        self.name_label = ttk.Label(self, textvariable=self.name, style='TLabel')

        # setup data visualization
        self.char_vis = PaletteElem(self, font_width=font_width, height=height)
        self.char_vis['style'] = 'PalettePressed.TFrame'

        # setup user input
        self.char_code = StringVar(root)
        self.character_entry = ttk.Entry(self, textvariable=self.char_code, width=9)
        self.character_entry.bind('<Return>', self.__acceptInput)

        # organize layout
        self.rowconfigure(0, weight=1)

        self.name_label.grid(column=0, row=0, sticky='SW')
        self.char_vis.grid(column=0, row=1, sticky='NSEW')
        self.character_entry.grid(column=0, row=2, sticky='NSEW')

    def changeForeground(self, foreground):
        self.char_vis.data.foreground_color = foreground
        self.char_vis.updateVis()

    def getChar(self):
        return self.char_vis.data.character

    def setChar(self, char):
        self.char_vis.data.character = char
        self.char_vis.updateVis()

    def __acceptInput(self, event):
        """
        Accepts input as either a character, a positive integer, or a hex-value.
        A hex value must start with an [#] or else it will be detected as invalid input or an integer input
        """

        if len(self.char_code.get()) > 0:
            # detect character input
            if len(self.char_code.get()) == 1:
                self.char_vis.data.character = self.char_code.get()
                self.char_vis.updateVis()
                return

            # detect integer input
            try:
                code = int(self.char_code.get())
                self.char_vis.data.character = chr(code)
                self.char_vis.updateVis()
                return
            except (ValueError, OverflowError):
                pass

            # detect hex input
            if self.char_code.get()[0] == '#':
                try:
                    code = int(self.char_code.get()[1:], 16)
                    self.char_vis.data.character = chr(code)
                    self.char_vis.updateVis()
                    return
                except (ValueError, OverflowError):
                    pass

            print(f'Invalid input [{self.char_code.get()}]')
        




if __name__ == "__main__":
    root = Tk()
    root.minsize(300, 300)

    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    c = CharacterPicker(root)
    c.grid(column=0, row=0, sticky='NSEW')

    root.mainloop()

