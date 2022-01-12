from os import path

# hidden imports:
# 'sklearn.utils._cython_blas', 'PIL', 'cv2', 'keras', 'matplotlib', 'playsound', 'sklearn',
# 'tensorflow', 'imutils', 'keras_vggface', 'numpy', 'encodings'

# define the paths to the training and validation directories
IMAGE = ".\data\images"
UNKNOWN = ".\data\\unknown"
FULL = ".\data\\full"
OUTPUT_PATH = ".\data\output"
ALARM = ".\data\\alarm.wav"
NOTIFICATION_STATUS = ".\data\\notification_status.json"
ROOM_ID = ".\data\\room.json"
DATASET_MEAN = ".\data\mean.json"
STATUS_MODEL = ".\data\liveness32_p9.model"
PRETRAINED_VGG16 = ".\data\\rcmalli_vggface_tf_notop_vgg16.h5"

# since we do not have access to the testing data we need to
# take a number of images from the training data and use it instead

IMAGE_SIZE = 128
BATCH_SIZE = 16
EPOCH = 20

# define the path to the output directory used for storing plots,
# classification reports, etc.
CHECKPOINTS_PATH = path.sep.join([OUTPUT_PATH, "checkpoints"])
NAME = "identifier" + str(IMAGE_SIZE)
FIG_PATH = path.sep.join([OUTPUT_PATH, NAME + ".png"])
JSON_PATH = path.sep.join([OUTPUT_PATH, NAME + ".json"])
MODEL_PATH = path.sep.join([CHECKPOINTS_PATH, NAME + ".model"])
CLASS_NAMES_PATH = path.sep.join([OUTPUT_PATH, "list_face" + ".json"])
