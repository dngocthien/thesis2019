import os
import shutil
import tkinter as tk
from os import path
import numpy
from imutils import paths
from tkinter import font as tk_font

from security_warning.config import config
from security_warning.camera_to_image import Photographer
from security_warning.train import FineTuner


class SettingPage(tk.LabelFrame):

    def __init__(self, parent, controller):
        tk.LabelFrame.__init__(self, parent)
        self.ctrl = controller
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        # background image
        # self.img = Image.open(".\data\sky.png")
        self.img_label = tk.Label(self)
        self.img_label.place(x=0, y=0, relwidth=1, relheight=1)
        # self.img_label.img = self.img  # PIL says we need to keep a ref so it doesn't get GCed
        self.img_label.bind('<Configure>', self._resize_image)
        parent.update()

        image_paths = list(paths.list_images(config.IMAGE))
        self.list_face = [p.split(os.path.sep)[-2] for p in image_paths]
        self.list_face = [str(x) for x in numpy.unique(self.list_face)]
        self.list_face.remove("undefined")

        self.om_variable = tk.StringVar(self)
        self.om_variable.set(self.list_face[0])
        self.om_variable.trace('w', self.option_select)

        self.font = tk_font.Font(family='Times', size=16, weight="bold")

        # add face
        self.e = tk.Entry(self, font=self.font, width=25)
        self.btn_add = tk.Button(self, text='Add Face', font=self.font,
                                 width=15, command=self.add_face)

        # remove face
        self.menu_face = tk.OptionMenu(self, self.om_variable, *self.list_face)
        self.menu_face.config(width=39)
        self.btn_remove = tk.Button(self, text='Remove Face', font=self.font,
                                    width=15, command=self.remove_face)

        # back
        self.btn_update = tk.Button(self, text='Update Data', font=self.font,
                                    width=15, command=self.page_update)

        # back
        self.btn_back = tk.Button(self, text='Back', font=self.font,
                                  width=15, command=lambda: controller.show_frame("HomePage"))

        # train
        self.btn_train = tk.Button(self, text='Train', font=self.font,
                                   width=15, command=self.train)

    def option_select(self, *args):
        self.ctrl.show_mesg(text=self.om_variable.get() + " is being selected")

    def add_face(self):
        name = self.e.get()
        if name == "":
            return
        if self.list_face.__contains__(name):
            self.ctrl.show_mesg('System has contained this name!')
            return
        output = path.sep.join([config.IMAGE, name])
        if not os.path.exists(output):
            os.mkdir(output)
        Photographer().take_photos(output, self.ctrl)

        self.list_face.append(name)
        self.ctrl.show_mesg(text=name + " was added")
        self.e.delete(0, 'end')

        menu = self.menu_face["menu"]
        menu.delete(0, "end")
        for string in self.list_face:
            menu.add_command(label=string, command=lambda value=string: self.om_variable.set(value))

    def remove_face(self):
        if self.list_face.__contains__(self.om_variable.get()):
            self.list_face.remove(self.om_variable.get())
            shutil.rmtree(path.sep.join([config.IMAGE, self.om_variable.get()]))
            self.ctrl.show_mesg(text=self.om_variable.get() + " was removed")
        else:
            self.ctrl.show_mesg(text='You have not select any face!')

        menu = self.menu_face["menu"]
        menu.delete(0, "end")
        for string in self.list_face:
            menu.add_command(label=string, command=lambda value=string: self.om_variable.set(value))

    def page_update(self):
        unknown_paths = list(paths.list_images(config.UNKNOWN))
        if 0 < len(unknown_paths):
            self.ctrl.show_frame("UpdateDataPage")
        else:
            self.ctrl.show_mesg('No new data to update!')

    def train(self):
        self.ctrl.show_mesg('training...0%')
        FineTuner().finetune(controller=self.ctrl)

    def _resize_image(self, event):
        # self.image = self.img.resize((event.width, event.height))
        # self.background_image = ImageTk.PhotoImage(self.image)
        # self.img_label.configure(image=self.background_image)

        self.e.place(x=event.width//2 - 250, y=105)
        self.btn_add.place(x=event.width//2 + 50, y=100)

        self.menu_face.place(x=event.width//2 - 250, y=155)
        self.btn_remove.place(x=event.width//2 + 50, y=150)

        self.btn_update.place(x=event.width//2 + 50, y=200)

        self.btn_back.place(x=event.width - 405, y=event.height - 100)
        self.btn_train.place(x=event.width - 200, y=event.height - 100)
