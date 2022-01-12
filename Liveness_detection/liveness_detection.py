import numpy

import cv2
from keras.engine.saving import load_model
from keras_preprocessing.image import img_to_array
import dlib

detector = dlib.get_frontal_face_detector()

status_model = load_model("liveness32_a4.model")
IMAGE_SIZE = 32

list_status = ['image', 'phone', 'real']
camera = cv2.VideoCapture(0)
closed = 0

while True:
    (grabbed, frame) = camera.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

    faces = detector(gray, 1)
    for face in faces:
        # extract the ROI of the face from the grayscale image,
        # resize it to a fixed 28x28 pixels, and then prepare the
        # ROI for classification via the CNN
        interest = frame[face.top():face.bottom(), face.left():face.right()]

        # predict real or fake
        roi1 = cv2.resize(interest.copy(), dsize=(IMAGE_SIZE, IMAGE_SIZE), interpolation=cv2.INTER_AREA)
      
        roi1 = roi1.astype(float) / 255.0
        roi1 = img_to_array(roi1)
        roi1 = numpy.expand_dims(roi1, axis=0)
        statuses = status_model.predict(roi1)[0]
        m = max(statuses)
        index1 = [i for i, j in enumerate(statuses) if j == m][0]
        status = list_status[index1]

        text_color = (50, 255, 0)
        if status == "image":
            text_color = (50, 0, 255)
        if status == "phone":
            text_color = (255, 0, 255)

        cv2.putText(frame, status + str(round(statuses[index1], 2)), fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                    fontScale=.8, color=text_color, thickness=2, org=(face.left(), face.top() - 10))
        cv2.rectangle(frame, (face.left(), face.top()), (face.right(), face.bottom()), color=text_color, thickness=1)

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
