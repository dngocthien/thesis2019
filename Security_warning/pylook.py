from tkinter import W, E, N, S
import tkinter as tk
from tkinter import font as tk_font

from GUI.page_home import HomePage
from GUI.page_setting import SettingPage
from GUI.page_update import UpdateDataPage
from GUI.page_room import RoomPage


class PyLook:

    def __init__(self, r):
        self.root = r
        self.root.title("PyLook")
        self.root.minsize(600, 400)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)
        self.var1 = tk.IntVar()
        self.var2 = tk.IntVar()

        # the container is where we'll stack a bunch of frames
        # on top of each other, then the one we want visible
        # will be raised above the others
        container = tk.Frame(self.root)
        container.grid(row=1, column=0, padx=10, pady=10, sticky=E+W+N+S)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.font = tk_font.Font(family='Times', size=16, weight="bold")

        # info
        self.mesg = tk.Label(self.root, text="Welcome!", font=self.font)
        self.mesg.place(x=0, y=0)

        self.frames = {}
        for F in (HomePage, SettingPage, UpdateDataPage, RoomPage):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, sticky=W+E+N+S)

        self.show_frame("HomePage")

    def show_frame(self, page_name):
        self.show_mesg('')
        frame = self.frames[page_name]
        frame.update()
        frame.tkraise()

    def show_mesg(self, text):
        self.mesg.config(text=text)
        self.root.update()


window = tk.Tk()
app = PyLook(r=window)
window.mainloop()
