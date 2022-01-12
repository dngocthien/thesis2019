import datetime
import json
import os
import random
import socket
import time
from os import path
from threading import Thread

import cv2
import dlib
import numpy
import playsound
from imutils import paths
from keras.engine.saving import load_model
from keras_preprocessing.image import img_to_array
# from notify_run import Notify
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin.storage import storage
from preprocessing.meanpreprocessor import MeanPreprocessor
from security_warning.config import config


class Identifier:
    def __init__(self):
        if os.path.exists(config.MODEL_PATH) & os.path.exists(config.CLASS_NAMES_PATH):
            self.UNDEFINED = 'undefined'
            # self.detector = cv2.CascadeClassifier(config.CASCADE_PATH)
            self.detector = dlib.get_frontal_face_detector()
            room = json.loads(open(config.ROOM_ID).read())
            self.room_id = room["room"]

            if self.internet():
                cred = credentials.Certificate(".\data\\firebase_key.json")
                firebase_admin.initialize_app(cred)
                self.ref = db.reference('/room/' + self.room_id, url='https://testjs-2b276.firebaseio.com/')

                client = storage.Client.from_service_account_json('.\data\\firebase_key.json')
                self.bucket = client.get_bucket('testjs-2b276.appspot.com')
                self.blob = self.bucket.blob(self.room_id + '.png')

            means = json.loads(open(config.DATASET_MEAN).read())
            self.mp = MeanPreprocessor(means["R"], means["G"], means["B"])

            self.status_model = load_model(config.STATUS_MODEL)
            self.list_status = ['image', 'phone', 'real']

            self.model = load_model(config.MODEL_PATH)
            self.list_face = json.loads(open(config.CLASS_NAMES_PATH).read())
            self.i = 0
            self.k = 0
            # self.notify = Notify()
            self.timer = None
        else:
            self.model = None

    def trace(self, label, interest):
        dir = path.sep.join([config.UNKNOWN, label])
        if not os.path.exists(dir):
            os.mkdir(dir)
        destination = path.sep.join([dir, str(self.i) + ".jpg"])
        while os.path.exists(destination):
            self.i += 1
            destination = path.sep.join([dir, str(self.i) + ".jpg"])
            self.i += 1
        cv2.imwrite(destination, interest)
        return destination

    def identify(self, ctrl):
        if self.internet():
            room = json.loads(open(config.ROOM_ID).read())
            self.room_id = room["room"]
            self.ref = db.reference('/room/' + self.room_id, url='https://testjs-2b276.firebaseio.com/')
            self.blob = self.bucket.blob(self.room_id + '.png')

        if self.model is None:
            ctrl.show_mesg('Machine has not been trained')
            return

        camera = cv2.VideoCapture(0)
        closed = 0
        undefined_time = 0
        rand_max = 5

        while True:
            r = random.randint(1, rand_max)
            (grabbed, frame) = camera.read()
            full = frame.copy()
            gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

            # faces = self.detector.detectMultiScale(gray, scaleFactor=1.1,
            #                                        minNeighbors=12, flags=cv2.CASCADE_SCALE_IMAGE, minSize=(20, 20))
            faces = self.detector(gray, 1)
            for face in faces:
                # extract the ROI of the face from the grayscale image,
                # resize it to a fixed 28x28 pixels, and then prepare the
                # ROI for classification via the CNN
                # interest = frame[fY:fY + fH, fX:fX + fW]
                interest = frame[face.top():face.bottom(), face.left():face.right()]

                # predict real or fake
                roi1 = cv2.resize(interest.copy(), dsize=(32, 32), interpolation=cv2.INTER_AREA)
                roi1 = roi1.astype(float) / 255.0
                roi1 = img_to_array(roi1)
                roi1 = numpy.expand_dims(roi1, axis=0)
                statuses = self.status_model.predict(roi1)[0]
                m = max(statuses)
                index1 = [i for i, j in enumerate(statuses) if j == m][0]
                status = self.list_status.__getitem__(index1)
                if not status == 'real':
                    continue

                # predict class label
                roi = cv2.resize(interest.copy(), dsize=(config.IMAGE_SIZE, config.IMAGE_SIZE),
                                 interpolation=cv2.INTER_AREA)
                roi = self.mp.preprocess(roi)
                roi = roi.astype(float) / 255.0
                roi = img_to_array(roi)
                roi = numpy.expand_dims(roi, axis=0)
                class_values = self.model.predict(roi)[0]
                m = max(class_values)
                index = [i for i, j in enumerate(class_values) if j == m][0]
                label = self.list_face[index]	
                if m < 0.72:
                    label = self.UNDEFINED

                # random save image to update data
                if r == 1:
                    Thread(target=lambda: self.trace(label, interest)).start()
                    rand_max = len(list(paths.list_images(config.UNKNOWN)))*2 + 18

                # send to GUI
                if label == self.UNDEFINED:
                    text_color = (0, 0, 255)
                    undefined_time += 1
                    if self.timer is None:
                        self.timer = time.time() - 100
                    if (ctrl.var2.get()) and (time.time() - self.timer > 15):
                        self.timer = time.time()
                        undefined_time = 0
                        Thread(target=lambda: self.push(full, ctrl)).start()
                    if ctrl.var1.get() and undefined_time > 5:
                        Thread(target=lambda: playsound.playsound(config.ALARM)).start()
                        undefined_time = 0
                else:
                    text_color = (255, 100, 0)
                    undefined_time = 0
                # cv2.putText(frame, label + str(round(class_values[index], 2)), fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                #             fontScale=.8, color=text_color, thickness=2, org=(fX, fY - 10))
                # cv2.rectangle(frame, (fX, fY), (fX + fW, fY + fH), color=text_color, thickness=1)
                cv2.putText(frame, label + str(round(class_values[index], 2)), fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                            fontScale=.8, color=text_color, thickness=2, org=(face.left(), face.top() - 10))
                cv2.rectangle(frame, (face.left(), face.top()), (face.right(), face.bottom()), color=text_color, thickness=1)

            # exit options
            if cv2.waitKey(1) & 0xFF is ord("q"):
                break
            if cv2.getWindowProperty('Tracking', 1) == -1:
                if closed > 0:
                    break
                else:
                    closed += 1

            cv2.imshow("Tracking", frame)
        camera.release()
        cv2.destroyAllWindows()

    def push(self, interest, ctrl):
        if not self.internet():
            ctrl.show_mesg('Please recheck the internet!')
            return
        dest = self.notification(interest)
        img = open(dest, 'rb')
        self.blob.upload_from_file(img)
        encoded = self.blob.generate_signed_url(datetime.timedelta(seconds=420000), method='GET')
        encoded = self.encode(encoded)
        # encoded = encoded[::-1]
        self.ref.update({'notification': encoded})

    def notification(self, interest):
        dir = config.FULL
        if not os.path.exists(dir):
            os.mkdir(dir)
        destination = path.sep.join([dir, str(self.k) + ".jpg"])
        while os.path.exists(destination):
            self.k += 1
            destination = path.sep.join([dir, str(self.k) + ".jpg"])
            self.k += 1
        cv2.imwrite(destination, interest)
        return destination

    @staticmethod
    def encode(original, start=42):
        encoded = original[:start]

        origin = original[start:]
        for char in origin:
            if char == 'a':
                encoded += 'c'
            elif char == 'e':
                encoded += 'b'
            elif char == 'i':
                encoded += 'd'
            elif char == 'c':
                encoded += 'a'
            elif char == 'b':
                encoded += 'e'
            elif char == 'd':
                encoded += 'i'
            else:
                encoded += char
        return encoded

    @staticmethod
    def internet(host="8.8.8.8", port=53, timeout=3):
        try:
            socket.setdefaulttimeout(timeout)
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
            return True
        except socket.error:
            return False
