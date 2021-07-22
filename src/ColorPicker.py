from tkinter import *
from tkinter import ttk
from tkcolorpicker import askcolor
from PIL import Image, ImageTk
import cv2
import numpy as np
from math import ceil


class RGBA:
    """class for storing rgba colors and converting them to different representations"""

    def __init__(self, c_val=(0, 0, 0, 255)):
        """color values should be in range 0-255 and should be passed as lists or a string with hex values.
        if only three values are passed, a fourth alpha value will be appended with the value 255"""
        if type(c_val) is tuple:
            c_val = list(c_val)

        if type(c_val) is list or type(c_val) is tuple:
            if len(c_val) == 3 or len(c_val) == 4:
                if len(c_val) == 3:
                    c_val.append(255)
                self.__init_rgba(c_val)
            else:
                raise ValueError("Invalid number of channels passed to constructor")
        elif type(c_val) is str:
            if c_val[0] == '#':
                c_val = c_val[1:]

            if len(c_val) == 6:
                self.__init_hex(c_val + 'ff')
            elif len(c_val) == 8:
                self.__init_hex(c_val)
            else:
                raise ValueError("Invalid number of channels passed to constructor")
        else:
            raise TypeError("Invalid type passed to constructor ", type(c_val))

    def __init_rgba(self, rgba: list):
        self.red = rgba[0]
        self.green = rgba[1]
        self.blue = rgba[2]
        self.alpha = rgba[3]

    def __init_hex(self, hex_val: str):
        self.red = int(hex_val[0:2], 16)
        self.green = int(hex_val[2:4], 16)
        self.blue = int(hex_val[4:6], 16)
        self.alpha = int(hex_val[6:8], 16)

    def rgba(self):
        return self.red, self.green, self.blue, self.alpha

    def rgbaHex(self):
        return f"#{''.join([format(val, 'x').zfill(2) for val in self.rgba()])}"

    def rgb(self):
        return self.red, self.green, self.blue

    def rgbHex(self):
        return f"#{''.join([format(val, 'x').zfill(2) for val in self.rgb()])}"

    def genImg(self, dimensions, block_size=10):
        background = self.__generatePngBackground(dimensions, block_size)
        width, height = dimensions

        # create img with rgb values from self.color to overlay onto background
        overlay = np.zeros((height, width, 3), dtype=np.uint8)
        overlay[:] = self.rgb()

        background = cv2.addWeighted(background, 1 - self.alpha / 255, overlay, self.alpha / 255, 0)

        # convert np array to tkinter photoimage
        img = Image.fromarray(background)
        imgTk = ImageTk.PhotoImage(image=img)

        return imgTk

    def __str__(self):
        return f"{self.red} {self.green} {self.blue} {self.alpha}"

    # generates the background the color is added on top of
    def __generatePngBackground(self, dimensions, block_size, colors=None):

        if colors is None:
            colors = (type(self)((154, 154, 154, 255)), type(self)((100, 100, 100, 255)))

        width, height = dimensions

        # generate tiles from current size
        png_back = np.zeros((height, width, 3), dtype=np.uint8)

        for x in range(ceil(width / block_size)):
            for y in range(ceil(height / block_size)):
                cv2.rectangle(png_back, (block_size * x, block_size * y),
                              (block_size * (x + 1), block_size * (y + 1)),
                              colors[(y + x) % 2].rgb(), -1)

        return png_back


class ColorPicker(ttk.Frame):
    """a widget for storing and letting the user modify an rgba value"""

    def __init__(self, root, name="Color", width=20, height=20, **kwargs):
        super().__init__(root, **kwargs)

        self.root = root

        self.width = width
        self.height = height

        self.color = RGBA()
        self.name = StringVar(root, name)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=4)

        self.color_label = ttk.Label(self, textvariable=self.name)

        self.color_label.grid(column=0, row=0, sticky="NW")

        self.color_preview = Label(self, relief="sunken", borderwidth=3, bg="#000000", width=width, height=height)

        self.color_preview.grid(column=0, row=1, sticky="SW", ipadx=0, ipady=0)

        self.color_change_callback = None

        self.color_preview.bind('<Configure>', self.__prevConfCallback)
        self.color_preview.bind('<1>', self.chooseColor)

    def chooseColor(self, *args):
        result = askcolor(self.color.rgbaHex(), alpha=True)
        if None not in result:
            self.color = RGBA(result[0])

            if self.color_change_callback is not None:
                self.color_change_callback(self.color)

            # update preview color
            self.root.after_idle(self.__setColorAsBackground)

    def getColPrevSize(self):
        # return the size of the image in the frame
        return self.color_preview.winfo_width() - (
                    int(str(self.color_preview['borderwidth'])) + int(str(self.grid_info()['ipadx']))) * 2, \
               self.color_preview.winfo_height() - (
                           int(str(self.color_preview['borderwidth'])) + int(str(self.grid_info()['ipady']))) * 2

    def changeSize(self, width, height):
        self.width = width
        self.height = height

        self.color_preview.configure(width=self.width, height=self.height)

    def chagneColor(self, color: RGBA):
        self.color = color

        if self.color_change_callback is not None:
            self.color_change_callback(self.color)

        self.__setColorAsBackground()

    def onColorChange(self, callback):
        """
        calls [callback] when the color value is changed.
        [callback] should accept an RGBA argument
        """

        self.color_change_callback = callback

    def __setColorAsBackground(self):

        # prevent preview image from being freed from memory
        self.b_img = self.color.genImg(self.getColPrevSize())

        self.color_preview.configure(image=self.b_img)

    def __prevConfCallback(self, event):
        # only call __prevResize if size has changed
        if (event.width, event.height) != (self.color_preview.winfo_width(), self.color_preview.winfo_height):
            self.root.after_idle(lambda: self.__prevResize())

    def __prevResize(self):
        # if preview frame was resized, a new preview image must be generated
        self.__setColorAsBackground()
