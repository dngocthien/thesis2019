import cv2
from imutils import paths
import dlib

output = "stream"
detector = detector = dlib.get_frontal_face_detector()
SKIP = 2

vs = cv2.VideoCapture(0)

read = 0

while True:
    # grab the frame from the file
    (grabbed, frame) = vs.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

    read += 1

    if read % SKIP != 0:
        continue

    rects = detector(gray, 1)

    for face in rects:
        roi = frame[face.top():face.bottom(), face.left():face.right()]
        file_name = output + "\\gt_" + str(read) + ".jpg"
        cv2.imwrite(file_name, roi)
        cv2.rectangle(frame, (face.left(), face.top()), (face.right(), face.bottom()), color=(0, 0, 200), thickness=1)
    cv2.imshow("Scanning", frame)
    num_image = len(list(paths.list_images(output)))
    if cv2.waitKey(1) & 0xFF is ord("q"):
        break
    if cv2.getWindowProperty('Scanning', 1) == -1:
        break

cv2.destroyAllWindows()
