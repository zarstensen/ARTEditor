import tkinter.filedialog
from tkinter import *
from src.Toolbar import Toolbar
from src.TextureEditor import TextureEditor, Modes
from tkinter import ttk
from Resources.ArtToCart import ArtToCart
from Resources.ArtToCart import CartToArt
from pathlib import Path
from src.ColorPicker import RGBA
from src.Palette import PaletteData


class ARTEditor(ttk.Frame):

    def __init__(self, root, *args, **kwargs):
        self.root = root

        super().__init__(root, *args, **kwargs)

        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        # setup toolbar
        self.toolbar = Toolbar(self)

        self.toolbar.onPaletteChange(self.__paletteChange)
        self.toolbar.onResizeChange(self.__onResize)
        self.toolbar.onBoxToggle(self.__onModeToggle)

        # setup texture editor
        self.texture_editor = TextureEditor(self, 10, 10)

        self.texture_editor.onCopy(self.__textureCopy)

        # setup top menu

        self.master.option_add('*tearOff', FALSE)

        self.menu = Menu(self)
        self.master.configure(menu=self.menu)
        self.file_menu = Menu(self.menu)

        self.menu.add_cascade(label='File', menu=self.file_menu)

        self.file_menu.add_command(label='Save')
        self.file_menu.add_command(label='Save as...')
        self.file_menu.add_command(label='Load')

        self.file_menu.add_separator()

        self.file_menu.add_command(label='Export texture', command=self.__exportTexture)
        self.file_menu.add_command(label='Import texture', command=self.__importTexture)

        self.file_menu.add_separator()

        self.file_menu.add_command(label='Export palette')
        self.file_menu.add_command(label='Import palette')

        self.file_menu.add_separator()

        self.file_menu.add_command(label='convert to .cart', command=self.__convertCart)
        self.file_menu.add_command(label='convert to .art', command=self.__convertArt)

        # layout
        self.toolbar.grid(column=0, row=0, sticky='nsew')
        self.texture_editor.grid(column=1, row=0, sticky='NSEW')


        self.__paletteChange(self.toolbar.getData())


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

    def __exportTexture(self):
        target_dir = tkinter.filedialog.asksaveasfilename(defaultextension=".art",
                                                   filetypes=(("Ascii Render texture file", "*.art"),
                                                              ("Compact Ascii Render texture file", "*.cart"),
                                                              ("All Files", "*.*")))
        if not target_dir:
            return

        path = Path(target_dir)

        # if suffix is .art write a Asciir Texture File
        if path.suffix == '.art':
            with open(target_dir, 'w', encoding='utf-8') as file:
                # write size
                file.write(f'// size\n{self.texture_editor.width} {self.texture_editor.height}\n\n')

                # write character data
                file.write('// symbols\n')

                for row in self.texture_editor.texture_data:
                    for col in row:
                        if col.character:
                            file.write(col.character + ' ')
                        else:
                            file.write('00')
                    file.write('\n')

                file.write('\n')

                # write foreground data
                file.write('// foreground color\n')

                for row in self.texture_editor.texture_data:
                    for col in row:
                        if col.background_color:
                            file.write(col.foreground_color.rgbaHex().replace('#', '') + ' ')
                        else:
                            file.write('00000000 ')
                    file.write('\n')

                file.write('\n')

                # write background data
                file.write('// background color\n')

                for row in self.texture_editor.texture_data:
                    for col in row:
                        if col.foreground_color:
                            file.write(col.background_color.rgbaHex().replace('#', '') + ' ')
                        else:
                            file.write('00000000 ')
                    file.write('\n')
        # if suffix is anything else (including .cart), write a Compact Asciir File.
        else:
            with open(target_dir, 'wb') as file:
                file.write(self.texture_editor.width.to_bytes(8, 'little'))
                file.write(self.texture_editor.height.to_bytes(8, 'little'))

                for row in self.texture_editor.texture_data:
                    for data in row:
                        if data.character:
                            file.write(data.character.encode('utf-8'))
                        else:
                            file.write(b'\00')

                        for color in (data.foreground_color, data.background_color):
                            if color:
                                for c_val in color.rgba():
                                    file.write(c_val.to_bytes(1, 'little'))
                            else:
                                file.write(b'\00\00\00\00')

    def __importTexture(self):
        target_dir = tkinter.filedialog.askopenfilename(defaultextension=".art",
                                                         filetypes=(("Ascii Render texture file", "*.art"),
                                                                    ("Compact Ascii Render texture file", "*.cart"),
                                                                    ("All Files", "*.*")))
        if not target_dir:
            return

        path = Path(target_dir)

        # if suffix is .art read a Asciir Texture File
        if path.suffix == '.art':
            data = ArtToCart.readData(path)

            if not data: return

            size_data, symbols_data, foreground_data, background_data = data

            self.texture_editor.resize(size_data[0], size_data[1])

            for i, row in enumerate(zip(symbols_data, foreground_data, background_data)):
                for j, data in enumerate(zip(row[0], row[1], row[2])):
                    self.texture_editor.texture_data[i][j] = PaletteData(data[0], RGBA(data[1]), RGBA(data[2]))

            self.texture_editor.rerender()

        # if suffix is anything else (including .cart), read as a Compact Asciir File.
        else:
            data = CartToArt.readData(path)

            if not data: return

            size_data, symbols_data, foreground_data, background_data = data

            self.texture_editor.resize(size_data[0], size_data[1])

            for i, row in enumerate(zip(symbols_data, foreground_data, background_data)):
                for j, data in enumerate(zip(row[0], row[1], row[2])):
                    self.texture_editor.texture_data[i][j] = PaletteData(data[0].decode('utf-8'), RGBA(data[1]), RGBA(data[2]))

            self.texture_editor.rerender()

    def __convertCart(self):
        target_dir = tkinter.filedialog.askopenfilename(defaultextension=".art",
                                                 filetypes=[("Ascii Render texture file", "*.art")])

        if not target_dir:
            return

        ArtToCart.convert([target_dir])

    def __convertArt(self):
        target_dir = tkinter.filedialog.askopenfilename(defaultextension=".cart",
                                                        filetypes=[("Compact Ascii Render texture file", "*.cart")])

        if not target_dir:
            return

        CartToArt.convert([target_dir])




root = Tk()
root.minsize(300, 300)

root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

editor = ARTEditor(root)
editor.grid(column=0, row=0, sticky='NSEW')


root.mainloop()