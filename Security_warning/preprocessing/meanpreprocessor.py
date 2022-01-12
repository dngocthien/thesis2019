import cv2
from keras_preprocessing.image import img_to_array


class MeanPreprocessor:
    def __init__(self, rMean, gMean, bMean):
        self.rMean = rMean
        self.gMean = gMean
        self.bMean = bMean

    def preprocess(self, image):

        (B, G, R) = cv2.split(image.astype("float32"))
        R -= self.rMean
        G -= self.gMean
        B -= self.bMean

        image = cv2.merge([B, G, R])
        return img_to_array(image)
