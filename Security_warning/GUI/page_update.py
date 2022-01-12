import os
import random
import tkinter as tk
from os import path

import numpy
from PIL import ImageTk, Image
from imutils import paths
from tkinter import font as tk_font

from security_warning.config import config


class UpdateDataPage(tk.LabelFrame):

    def __init__(self, parent, controller):
        self.pr = parent
        tk.LabelFrame.__init__(self, parent)
        self.ctrl = controller
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.i = 0

        # background image
        # self.img = Image.open(".\data\sky.png")
        self.img_label = tk.Label(self)
        self.img_label.place(x=0, y=0, relwidth=1, relheight=1)
        # self.img_label.image = self.img  # PIL says we need to keep a ref so it doesn't get GCed
        self.img_label.bind('<Configure>', self._resize_image)
        parent.update()

        image_paths = list(paths.list_images(config.IMAGE))
        self.list_face = [p.split(os.path.sep)[-2] for p in image_paths]
        self.list_face = [str(x) for x in numpy.unique(self.list_face)]

        self.om_variable = tk.StringVar(self)
        self.om_variable.set(self.list_face[0])
        self.om_variable.trace('w', self.option_select)

        self.font = tk_font.Font(family='Times', size=16, weight="bold")

        # show unknown face
        self.unknown_paths = list(paths.list_images(config.UNKNOWN))
        self.img_unknown = tk.Label(self.img_label)

        # remove face
        self.menu_face = tk.OptionMenu(self, self.om_variable, *self.list_face)
        self.menu_face.config(width=39)
        self.btn_update = tk.Button(self, text='Update Face', font=self.font,
                                    width=15, command=lambda: self.update_face())

        # back
        self.btn_back = tk.Button(self, text='Back', font=self.font,
                                  width=15, command=lambda: controller.show_frame("SettingPage"))

        # next face
        self.btn_next = tk.Button(self, text='Next', font=self.font, width=15,
                                  command=lambda: self.next_face())

    def option_select(self, *args):
        self.ctrl.show_mesg(text=self.om_variable.get() + " is being selected")

    def update_face(self):
        destination = path.sep.join([config.IMAGE, self.om_variable.get(), str(self.i) + ".jpg"])
        while os.path.exists(destination):
            self.i += 1
            destination = path.sep.join([config.IMAGE, self.om_variable.get(), str(self.i) + ".jpg"])
            self.i += 1
        os.rename(self.unknown_paths[0], destination)
        self.ctrl.show_mesg(text=self.om_variable.get() + " was updated")
        self.update()

    def next_face(self):
        os.remove(self.unknown_paths[0])
        self.update()

    def update(self):
        self.unknown_paths = list(paths.list_images(config.UNKNOWN))
        random.shuffle(self.unknown_paths)
        if 0 < len(self.unknown_paths):
            unknown = Image.open(self.unknown_paths[0])
            unknown = unknown.resize((128, 128), Image.ANTIALIAS)
            unknown_img = ImageTk.PhotoImage(unknown)
            self.img_unknown.config(image=unknown_img)
            self.img_unknown.image = unknown_img
            label = self.unknown_paths[0].split(os.path.sep)[-2]
            self.om_variable.set(label)
        else:
            self.ctrl.show_frame("SettingPage")
            self.ctrl.show_mesg('No new data to update!')
        self.pr.update()

    def _resize_image(self, event):
        # self.image = self.img.resize((event.width, event.height))
        # self.background_image = ImageTk.PhotoImage(self.image)
        # self.img_label.configure(image=self.background_image)

        self.menu_face.place(x=event.width//2 - 250, y=205)
        self.btn_update.place(x=event.width//2 + 50, y=200)

        self.img_unknown.place(x=event.width//2 - 50, y=20)

        self.btn_back.place(x=event.width - 405, y=event.height - 100)
        self.btn_next.place(x=event.width - 200, y=event.height - 100)
