import cv2
from imutils import paths
import dlib

input = "video\\a.mp4"
output = "dataset2"
detector = dlib.get_frontal_face_detector()
SKIP = 10

vs = cv2.VideoCapture("videos/d.mp4")

read = 0
saved = 0

while True:
    # grab the frame from the file
    (grabbed, frame) = vs.read()

    # if the frame was not grabbed, then we have reached the end
    # of the stream
    if not grabbed:
        break

    # increment the total number of frames read thus far
    read += 1

    if read % SKIP != 0:
        continue

    frame = cv2.resize(frame, dsize=(600, 300))
    rows, cols = frame.shape[:2]
    M = cv2.getRotationMatrix2D((cols / 2, rows / 2), -90, 1)
    frame = cv2.warpAffine(frame, M, (cols, rows))

    faces = detector(gray, 1)

    for face in rects:
        roi = frame[face.top():face.bottom(), face.left():face.right()]
        file_name = output + "\\n_" + str(face.top()) + ".jpg"
        cv2.imwrite(file_name, roi)
        cv2.rectangle(frame, (face.left(), face.top()), (face.right(), face.bottom()), color=(0, 0, 200), thickness=1)
    cv2.imshow("Scanning", frame)
    num_image = len(list(paths.list_images(output)))
    if cv2.waitKey(1) & 0xFF is ord("q"):
        break
    if cv2.getWindowProperty('Scanning', 1) == -1:
        break

cv2.destroyAllWindows()
