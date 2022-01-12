import hashlib
import json
import socket
import tkinter as tk
from tkinter import font as tk_font
from firebase_admin import db

from security_warning.config import config


class RoomPage(tk.LabelFrame):

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

        self.font = tk_font.Font(family='Times', size=16, weight="bold")
        room = json.loads(open(config.ROOM_ID).read())
        self.room_id = room["room"]

        # cred = credentials.Certificate(".\data\\firebase_key.json")
        # firebase_admin.initialize_app(cred)

        # add id
        self.lb_id = tk.Label(self, text="ID:", font=self.font)
        self.txt_id = tk.Entry(self, font=self.font, width=25)
        if len(self.room_id) > 0:
            self.txt_id.insert(0, self.room_id)

        # add password
        self.lb_pw = tk.Label(self, text="Password:", font=self.font)
        self.txt_pw = tk.Entry(self, show="*", font=self.font, width=25)

        # back
        self.btn_back = tk.Button(self, text='Back', font=self.font,
                                  width=15, command=lambda: controller.show_frame("HomePage"))

        # train
        self.btn_create = tk.Button(self, text='Save', font=self.font,
                                    width=15, command=lambda: self.save_room_info())

    def save_room_info(self):
        if not self.internet():
            self.ctrl.show_mesg('Please recheck the internet!')
            return
        room_id = self.txt_id.get()
        password = self.txt_pw.get()
        # pre-processing
        if room_id == "":
            self.ctrl.show_mesg('Please add group id!')
            return
        if password == "":
            self.ctrl.show_mesg('Please add password!')
            return
        if set('[~!@#$%^&*()_+{\}":;\']+$').intersection(room_id):
            self.ctrl.show_mesg('Id cannot contain special characters!')
            return
        hashpass = hashlib.md5(password.encode('utf8')).hexdigest()

        # request id and pw from firebase
        read_id = db.reference('/room/' + room_id + '/id', url='https://testjs-2b276.firebaseio.com/').get()
        read_pw = db.reference('/room/' + room_id + '/pw', url='https://testjs-2b276.firebaseio.com/').get()

        # id has not existed
        if read_id is None:
            # create new room
            self.create(room_id, hashpass)
            self.login(room_id)
            return
        # id has existed
        if read_id is not None:
            # login if input and pw is the same
            if hashpass == str(read_pw):
                self.login(room_id)
                return
            # input and pw are not the same
            if not hashpass == str(read_pw):
                # overwrite password if logged in
                if room_id == self.room_id:
                    self.overwrite_pw(room_id, hashpass)
                    self.login(room_id)
                    return
                # cannot overwrite pw the id of others
                if not room_id == self.room_id:
                    self.ctrl.show_mesg('This id has existed, but password was wrong!')
                    return
        self.ctrl.show_mesg('Something wrong!')

    @staticmethod
    def create(room_id, pw):
        data = {
            'id': room_id,
            'pw': pw,
            'notification': 'hello!'
        }
        ref = db.reference('/room/' + room_id, url='https://testjs-2b276.firebaseio.com/')
        ref.set(data)

    @staticmethod
    def overwrite_pw(room_id, pw):
        ref = db.reference('/room/' + room_id, url='https://testjs-2b276.firebaseio.com/')
        ref.update({'pw': pw})

    def login(self, room_id):
        data = {"room": room_id}
        roomPath = open(config.ROOM_ID, "w")
        roomPath.write(json.dumps(data))
        roomPath.close()
        self.txt_pw.delete(0, 'end')
        self.ctrl.show_mesg('Saved group information successfully!')

    def _resize_image(self, event):
        # self.image = self.img.resize((event.width, event.height))
        # self.background_image = ImageTk.PhotoImage(self.image)
        # self.img_label.configure(image=self.background_image)

        self.lb_id.place(x=event.width//2 - 150, y=105)
        self.txt_id.place(x=event.width//2 - 100, y=105)

        self.lb_pw.place(x=event.width // 2 - 213, y=155)
        self.txt_pw.place(x=event.width//2 - 100, y=155)

        self.btn_back.place(x=event.width - 405, y=event.height - 100)
        self.btn_create.place(x=event.width - 200, y=event.height - 100)

    def update(self):
        room = json.loads(open(config.ROOM_ID).read())
        self.room_id = room["room"]
        self.txt_id.delete(0, 'end')
        self.txt_pw.delete(0, 'end')
        if len(self.room_id) > 0:
            self.txt_id.insert(0, self.room_id)

    @staticmethod
    def internet(host="8.8.8.8", port=53, timeout=3):
        try:
            socket.setdefaulttimeout(timeout)
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
            return True
        except socket.error:
            return False
