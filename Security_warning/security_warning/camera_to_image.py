import os

import cv2
from imutils import paths
from os import path
import dlib


class Photographer:
    def __init__(self):
        # self.detector = cv2.CascadeClassifier(config.CASCADE_PATH)
        self.detector = dlib.get_frontal_face_detector()
        self.i = 1

    def take_photos(self, output, controller):
        camera = cv2.VideoCapture(0)

        while True:
            (rval, frame) = camera.read()
            # frame = cv2.flip(frame, 1, 0)

            # rects = self.detector.detectMultiScale(frame.copy(), scaleFactor=1.1, minNeighbors=12,
            #                                        flags=cv2.CASCADE_SCALE_IMAGE, minSize=(64, 64))
            rects = self.detector(frame, 1)
            for face in rects:
                # extract the ROI of the face from the grayscale image,
                # resize it to a fixed 28x28 pixels, and then prepare the
                # ROI for classification via the CNN
                roi = frame[face.top():face.bottom(), face.left():face.right()]
                file_name = output + "\\n_" + str(self.i) + ".jpg"
                while os.path.exists(file_name):
                    self.i += 1
                    file_name = output + "\\n_" + str(self.i) + ".jpg"
                    self.i += 1
                cv2.imwrite(file_name, roi)
                cv2.rectangle(frame, (face.left(), face.top()), (face.right(), face.bottom()), color=(0, 0, 200), thickness=1)
            cv2.imshow("Scanning", frame)
            num_image = len(list(paths.list_images(output)))
            if cv2.waitKey(1) & 0xFF is ord("q"):
                break
            if num_image > 99:
                break
            if cv2.getWindowProperty('Scanning', 1) == -1:
                break
            controller.show_mesg('scanning...' + str(num_image) + '%')
        camera.release()
        cv2.destroyAllWindows()
