from tkinter import *
from tkinter import ttk
from src.Palette import PaletteData
import enum
from math import floor


class Modes(enum.Enum):
    ERASE = 0
    DRAW = 1

    ERASE_BOX = 2
    DRAW_BOX = 3


class TextureEditor(ttk.Frame):
    def __init__(self, root, width=20, height=20, *args, **kwargs):
        self.root = root
        super().__init__(root, *args, **kwargs)

        # define data storage variables

        self.width = width
        self.height = height

        self.mode = Modes.DRAW

        self.zoom = 10

        self.draw_data = PaletteData()

        self.texture_data = [[
            PaletteData() for _ in range(self.width)
        ] for _ in range(self.height)]

        # setup canvas and frame for holding the text widget
        self.canvas = Canvas(self, width=500, height=500)

        self.canvas.grid(column=0, row=0, sticky='NW')

        self.frame = ttk.Frame(self.canvas)



        # setup text widget
        self.text = Text(self.frame, width=self.width, height=self.height, wrap=CHAR, borderwidth=0,
                         font=('Consolas', self.zoom), cursor='target')

        self.text.insert(INSERT, ('a' * self.width + '\n') * self.height)

        for y in range(self.height):
            for x in range(self.width):
                self.text.tag_add(f'{x}|{y}', f'{y + 1}.{x}')

        self.text.grid(column=0, row=0, sticky='NSEW')
        self.win_id = self.canvas.create_window((100, 100), window=self.frame)
        self.canvas.itemconfigure(self.win_id, )



        self.lockEditor()

        # bind events
        self.text.bind('<Alt-MouseWheel>', lambda e: self.__zoom(1, e))
        self.text.bind('<Alt-Control-MouseWheel>', lambda e: self.__zoom(10, e))
        self.text.bind('<MouseWheel>', lambda e: 'break')
        self.text.bind('<B2-Motion>', self.__move)
        self.text.bind('<2>', self.__moveStart)
        self.text.bind('<B2-ButtonRelease>', self.__moveEnd)

        self.text.bind('<B1-Motion>', self.__draw)
        self.text.bind('<1>', self.__draw)

        self.last_move = (0, 0)
        self.moving = False




    def lockEditor(self):
        self.text['state'] = 'disabled'

    def unlockEditor(self):
        self.text['state'] = 'normal'

    # returns the width and height of a character in pixels.
    def charDimensions(self):
        #print(self.text.configure())
        return floor(self.text.winfo_width() / self.text['width']),\
               floor(self.text.winfo_height() / self.text['height'])

    def __zoom(self, step, event):
        if not self.moving:
            if event.delta > 0:
                self.zoom += step
            else:
                self.zoom -= step
                self.zoom = max(1, self.zoom)

            self.text['font'] = ('Consolas', self.zoom)
            self.text.configure(width=self.width, height=self.height)

        return 'break'

    def __moveStart(self, event):
        self.moving = True
        self.last_move = (event.x, event.y)

    def __move(self, event):
        # self.canvas.delete(self.win_id)
        # self.win_id = self.canvas.create_window((event.x, event.y), window=self.frame)
        delta_x = event.x - self.last_move[0]
        delta_y = event.y - self.last_move[1]

        self.last_move = (event.x - delta_x, event.y - delta_y)
        self.canvas.move(self.win_id, delta_x, delta_y)

        return 'break'

    def __moveEnd(self, event):
        self.moving = False

    def __draw(self, event):

        if self.frame.bbox('all')[0] < event.x < self.frame.bbox('all')[2] and \
            self.frame.bbox('all')[1] < event.y < self.frame.bbox('all')[3]:

            pos_x = floor((event.x - self.frame.bbox('all')[0]) / self.charDimensions()[0])
            pos_y = floor((event.y - self.frame.bbox('all')[1]) / self.charDimensions()[1])

            if self.mode == Modes.DRAW:
                if self.text.get(f'{pos_y + 1}.{pos_x}') != '\n':
                    self.texture_data[pos_y][pos_x] = self.draw_data

                    if self.draw_data.foreground_color is not None:
                        self.text.tag_configure(f'{pos_x}|{pos_y}',
                                                foreground=self.draw_data.foreground_color.rgbHex())
                    if self.draw_data.background_color is not None:
                        self.text.tag_configure(f'{pos_x}|{pos_y}',
                                                background=self.draw_data.background_color.rgbHex())

                    if self.draw_data.character is not None:
                        self.text.delete(f'{pos_y + 1}.{pos_x}')
                        self.text.insert(f'{pos_y + 1}.{pos_x}', self.draw_data.character)

            elif self.mode == Modes.ERASE:
                self.text.tag_configure(f'{pos_x}|{pos_y}', foreground=None, background=None)
                self.unlockEditor()
                if self.text.get(f'{pos_y+1}.{pos_x}') != '\n':
                    self.text.delete(f'{pos_y+1}.{pos_x}')
                    self.text.insert(f'{pos_y+1}.{pos_x}', ' ')

        return 'break'


if __name__ == '__main__':
    root = Tk()
    root.minsize(300, 300)

    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    e = TextureEditor(root, width=10, height=10)
    e.mode = Modes.DRAW
    e.grid(column=0, row=0, sticky='NSEW')

    root.mainloop()
