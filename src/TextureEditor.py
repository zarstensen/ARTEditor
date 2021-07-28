from tkinter import *
from tkinter import ttk

from PIL import Image, ImageFont, ImageDraw, ImageTk

from src.Palette import PaletteData
from src.ColorPicker import RGBA
import enum
import numpy as np
import sys
from math import floor
import cv2
from copy import deepcopy


class Modes(enum.Enum):
    PEN = 0
    BOX = 1


class TextureEditor(ttk.Frame):
    def __init__(self, root, width=20, height=20, zoom=20, undo_length=128, *args, **kwargs):
        self.root = root
        super().__init__(root, *args, **kwargs)

        self.s = ttk.Style()
        self.s.configure('Editor.TFrame', background='#ffffff')

        # define data storage variables

        self.width = width
        self.height = height

        self.zoom = zoom

        # defines the maximum length of the undo and redo list
        self.undo_length = undo_length

        self.mode = Modes.PEN

        self.draw_data = PaletteData()

        self.texture_data = [[
            PaletteData() for x in range(self.width)
        ] for y in range(self.height)]

        # holds older versions of [texture_data] to be restored if necessary
        self.undo_data = []
        self.redo_data = []

        # setup canvas and image for holding the texture display data
        self.canvas = Canvas(self, width=500, height=500)

        self.canvas.grid(column=0, row=0, sticky='NW')

        self.font = self.__getFont(self.zoom)

        self.texture = self.__generateImage()
        self.draw = ImageDraw.Draw(self.texture)

        self.__drawData()

        self.img = ImageTk.PhotoImage(self.texture)

        self.img_id = self.canvas.create_image(0, 0, image=self.img, anchor='nw')

        self.__drawImage()

        # setup canvas event bindings

        self.bind_all('<Control-z>', lambda e: self.undo())
        self.bind_all('<Control-y>', lambda e: self.redo())

        self.canvas.bind('<B2-Motion>', self.__move)
        self.canvas.bind('<2>', self.__moveStart)
        self.canvas.bind('<ButtonRelease-2>', self.__moveEnd)

        self.canvas.bind('<MouseWheel>', lambda e: self.__zoom(1, e))
        self.canvas.bind('<Control-MouseWheel>', lambda e: self.__zoom(10, e))

        self.bind_all('<B1-Motion>', self.__draw)
        self.bind_all('<ButtonPress-1>', self.__drawStart)
        self.bind_all('<ButtonRelease-1>', self.__drawEnd)

        self.bind_all('<B3-Motion>', self.__erase)
        self.bind_all('<ButtonPress-3>', self.__eraseStart)
        self.bind_all('<ButtonRelease-3>', self.__eraseEnd)

        self.last_move = (0, 0)
        self.moving = False

    def undo(self):
        if self.undo_data:
            self.redo_data.append(deepcopy(self.texture_data))
            self.texture_data = self.undo_data.pop(-1)

            self.__drawData()
            self.__drawImage()

    def redo(self):
        if self.redo_data:
            self.undo_data.append(self.texture_data)
            self.texture_data = self.redo_data.pop(-1)

            self.__drawData()
            self.__drawImage()

    def drawText(self, text):
        """draws [text] onto the texture"""

        x = y = 0

        for line in text.split('\n'):
            for char in line:
                self.drawChar((x, y), char, (0, 255, 0, 155), (255, x * 10, 255, 55))
                x += 1
            x = 0
            y += 1

    def drawChar(self, pos, char, foreground, background):
        """draws [char] with the color of [foregound] onto the texture using ImageDraw. A box with the color of [background] is drawn around the character"""

        char_width, char_height = self.__charDimensions()

        self.draw.rectangle((pos[0] * char_width, pos[1] * char_height,
               (pos[0] + 1) * char_width, (pos[1] + 1) * char_height), fill=background)

        self.draw.text((pos[0] * char_width, pos[1] * char_height), char, font=self.font, fill=foreground)

    def __getFont(self, size):
        self.zoom = size
        return ImageFont.truetype('../Resources/SourceCodePro/SourceCodePro-Regular.ttf', size)

    def __generateImage(self):
        char_width, char_height = self.__charDimensions()

        background = self.__backgroundColor()

        return Image.fromarray(np.full((self.height * char_height, self.width * char_width, 4), background, dtype=np.uint8))

    def __charDimensions(self):
        ascent, descent = self.font.getmetrics()
        char_width = self.font.getsize(' ')[0]
        char_height = ascent + descent

        return char_width, char_height

    def __drawData(self):
        """draws [texture_data] to the [texture_img]"""

        for y, row in enumerate(self.texture_data):
            for x, col in enumerate(row):
                self.drawChar((x, y),
                                col.character if col.character is not None else ' ',
                                col.foreground_color.rgba() if col.foreground_color is not None else None,
                                col.background_color.rgba() if col.background_color is not None else self.__backgroundColor())

    def __drawImage(self):
        """creates a image from [texture_img] on the canvas"""

        self.img = ImageTk.PhotoImage(self.texture)

        self.canvas.itemconfigure(self.img_id, image=self.img)

    def __backgroundColor(self):
        # get rgb_value of frame background color and map it from 0-65536 to 0-255, also darken it to create a border
        return *[round(c_val / 65536 * 255 * 9 / 10) for c_val in self.canvas.winfo_rgb(self.canvas['background'])], 255

    def __zoom(self, step, event):
        if not self.moving:
            if event.delta > 0:
                self.zoom += step
            else:
                self.zoom -= step
                self.zoom = max(1, self.zoom)

            self.font = self.__getFont(self.zoom)

        # image size changed so a new image must be generated
        self.texture = self.__generateImage()
        self.draw = ImageDraw.Draw(self.texture)
        self.img = ImageTk.PhotoImage(self.texture)

        self.__drawData()
        self.__drawImage()

    def __moveStart(self, event):
        self.moving = True
        self.last_move = (event.x, event.y)

    def __move(self, event):
        # self.canvas.delete(self.win_id)
        # self.win_id = self.canvas.create_window((event.x, event.y), window=self.frame)
        delta_x = event.x - self.last_move[0]
        delta_y = event.y - self.last_move[1]

        self.last_move = (event.x, event.y)
        self.canvas.move(self.img_id, delta_x, delta_y)

    def __moveEnd(self, event):
        self.moving = False

    def __drawStart(self, event):
        self.redo_data = []

        if not self.undo_data or self.texture_data != self.undo_data[-1]:
            if len(self.undo_data) >= self.undo_length:
                self.undo_data.pop(0)

            self.undo_data.append(deepcopy(self.texture_data))

        self.__draw(event)

    def __drawEnd(self, event):
        if self.undo_data[-1] == self.texture_data:
            self.undo_data.pop()

    def __draw(self, event):
        if self.canvas.coords(self.img_id)[0] < event.x < self.canvas.coords(self.img_id)[0] + self.img.width() and \
                self.canvas.coords(self.img_id)[1] < event.y < self.canvas.coords(self.img_id)[1] + self.img.height():

            pos_x = floor((event.x - self.canvas.coords(self.img_id)[0]) / self.__charDimensions()[0])
            pos_y = floor((event.y - self.canvas.coords(self.img_id)[1]) / self.__charDimensions()[1])

            if self.mode == Modes.PEN:
                if self.draw_data.character is not None:
                    self.texture_data[pos_y][pos_x].character = self.draw_data.character

                if self.draw_data.foreground_color is not None:
                    self.texture_data[pos_y][pos_x].foreground_color = self.draw_data.foreground_color

                if self.draw_data.background_color is not None:
                    self.texture_data[pos_y][pos_x].background_color = self.draw_data.background_color
            elif self.mode == Modes.BOX:
                print(event)

            self.__drawData()
            self.__drawImage()

    def __eraseStart(self, event):
        self.redo_data = []

        if self.texture_data != self.undo_data[-1]:
            if len(self.undo_data) >= self.undo_length:
                self.undo_data.pop(0)

            self.undo_data.append(deepcopy(self.texture_data))

        self.__erase(event)

    def __eraseEnd(self, event):
        if self.undo_data[-1] == self.texture_data:
            self.undo_data.pop()

    def __erase(self, event):
        if self.canvas.coords(self.img_id)[0] < event.x < self.canvas.coords(self.img_id)[0] + self.img.width() and \
                self.canvas.coords(self.img_id)[1] < event.y < self.canvas.coords(self.img_id)[1] + self.img.height():

            pos_x = floor((event.x - self.canvas.coords(self.img_id)[0]) / self.__charDimensions()[0])
            pos_y = floor((event.y - self.canvas.coords(self.img_id)[1]) / self.__charDimensions()[1])

            if self.mode == Modes.PEN:
                self.texture_data[pos_y][pos_x] = PaletteData()

            self.__drawData()
            self.__drawImage()


if __name__ == '__main__':
    root = Tk()
    root.minsize(300, 300)

    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    t = TextureEditor(root, 40, 40, 40)
    t.grid(column=0, row=0, sticky='NW')

    t.draw_data = PaletteData('a', RGBA((255, 0, 0)), RGBA((0, 255, 0)))

    root.mainloop()
