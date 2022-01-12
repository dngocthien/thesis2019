import json
import tkinter as tk
from tkinter import font as tk_font

from security_warning.config import config
from security_warning.identify_face import Identifier


class HomePage(tk.LabelFrame):

    def __init__(self, parent, controller):
        tk.LabelFrame.__init__(self, parent)
        self.parent = parent
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

        #
        notifies = json.loads(open(config.NOTIFICATION_STATUS).read())
        device = notifies["device"]
        phone = notifies["phone"]

        self.font = tk_font.Font(family='Times', size=16, weight="bold")

        # start
        self.btn_start = tk.Button(self, text='Start', font=self.font, width=15, command=lambda: self.start())

        # setting
        self.btn_setting = tk.Button(self, text='Setting', font=self.font,
                                     width=15, command=lambda: controller.show_frame("SettingPage"))

        # notify
        self.device_notify = tk.Checkbutton(self, text='Alarm this device', font=self.font,
                                            variable=self.ctrl.var1,
                                            command=lambda: self.save_notify_status())
        self.phone_notify = tk.Checkbutton(self, text='Notify me by phone', font=self.font,
                                           variable=self.ctrl.var2,
                                           command=lambda: self.save_notify_status())
        self.btn_create_room = tk.Button(self, text='Group', font=self.font,
                                         command=lambda: controller.show_frame("RoomPage"))
        if device == 1:
            self.device_notify.select()
        if phone == 1:
            self.phone_notify.select()

        self.identifier = Identifier()

    def start(self):
        self.identifier.identify(self.ctrl)
        pass

    def save_notify_status(self):
        var1 = 1 if self.ctrl.var1.get() else 0
        var2 = 1 if self.ctrl.var2.get() else 0
        D = {"device": var1, "phone": var2}
        meanPath = open(config.NOTIFICATION_STATUS, "w")
        meanPath.write(json.dumps(D))
        meanPath.close()

    def _resize_image(self, event):
        # self.image = self.img.resize((event.width, event.height))
        # self.background_image = ImageTk.PhotoImage(self.image)
        # self.img_label.configure(image=self.background_image)

        self.btn_start.place(x=event.width - 200, y=100)
        self.btn_setting.place(x=event.width - 200, y=150)

        self.device_notify.place(x=50, y=event.height - 150)
        self.phone_notify.place(x=50, y=event.height - 100)
        self.btn_create_room.place(x=260, y=event.height - 102)
