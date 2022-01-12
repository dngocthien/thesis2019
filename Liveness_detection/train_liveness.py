from keras.applications import MobileNetV2
from keras.callbacks import ModelCheckpoint
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from keras.preprocessing.image import ImageDataGenerator
from keras.optimizers import RMSprop
from keras.engine.saving import load_model
from keras.utils import np_utils
from imutils import paths
import matplotlib.pyplot as plt
import numpy as np
import cv2
import os

from keras.layers.core import Flatten
from keras.layers.core import Dropout
from keras.layers.core import Dense
from keras import Model, Input

import matplotlib
matplotlib.use("Agg")

IMAGE_SIZE = 32
BS = 32
EPOCHS = 50
opt = RMSprop(lr=1e-4)
DATASET = "dataset_live_fake"
MODEL_PATH = "liveness32.model"

print("[INFO] loading images...")
data = []
labels = []
imagePaths = list(paths.list_images(DATASET))

for imagePath in imagePaths:
    # extract the class label from the filename, load the image and
    # resize it to be a fixed 32x32 pixels, ignoring aspect ratio
    image = cv2.imread(imagePath)
#     image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    image = cv2.resize(image, (IMAGE_SIZE, IMAGE_SIZE))
    data.append(image)
    # update the data and labels lists, respectively
    label = imagePath.split(os.path.sep)[-2]
    labels.append(label)

data = np.array(data, dtype="float") / 255.0

# one-hot encoding
le = LabelEncoder()
labels = le.fit_transform(labels)
labels = np_utils.to_categorical(labels, 3)

# partition the data into train set : val set : test set with ratio 50:25:25
(trainX, testX, trainY, testY) = train_test_split(data, labels, test_size=0.5, random_state=42)
(valX, testX, valY, testY) = train_test_split(testX, testY, test_size=0.5, random_state=42)

# construct the training image generator for data augmentation
aug = ImageDataGenerator(rotation_range=20, zoom_range=0.2, height_shift_range=0.1, width_shift_range=0.1,
                         horizontal_flip=True, fill_mode="nearest")

print("[INFO] compiling model...")
# model = build(width=IMAGE_SIZE, height=IMAGE_SIZE, depth=3, classes=len(le.classes_))
base_model = MobileNetV2(weights='imagenet', include_top=False, input_tensor=Input(shape=(32, 32, 3)))
x = base_model.output
x = Flatten()(x)
x = Dense(512, activation='relu')(x)
x = Dropout(0.5)(x)
x = Dense(3, activation='softmax')(x)

model = Model(inputs=base_model.input, outputs=x)

for layer in model.layers[:20]:
    layer.trainable = False

model.compile(loss="categorical_crossentropy", optimizer=opt, metrics=["accuracy"])
callbacks = [ModelCheckpoint(filepath=MODEL_PATH, monitor='val_loss', verbose=1, save_best_only=True,
                             save_weights_only=False, mode='auto', period=1)]

print("[INFO] training network for {} epochs...".format(EPOCHS))
H = model.fit_generator(aug.flow(trainX, trainY, batch_size=BS),
                        validation_data=(testX, testY), steps_per_epoch=len(trainX) // BS,
                        epochs=20, callbacks=callbacks)

for layer in model.layers[:20]:
    layer.trainable=True
    
model.compile(loss="categorical_crossentropy", optimizer=opt, metrics=["accuracy"])
callbacks = [ModelCheckpoint(filepath=MODEL_PATH, monitor='val_loss', verbose=1, save_best_only=True,
                             save_weights_only=False, mode='auto', period=1)]

print("[INFO] training network for {} epochs...".format(EPOCHS))
H = model.fit_generator(aug.flow(trainX, trainY, batch_size=BS),
                        validation_data=(valX, valY), steps_per_epoch=len(trainX) // BS,
                        epochs=EPOCHS, callbacks=callbacks)

print("[INFO] evaluating network...")
status_model = load_model(MODEL_PATH)
predictions = status_model.predict(testX, batch_size=BS)
print(classification_report(testY.argmax(axis=1), predictions.argmax(axis=1), target_names=le.classes_))

plt.style.use("ggplot")
plt.figure()
plt.plot(np.arange(0, EPOCHS), H.history["loss"], label="train_loss")
plt.plot(np.arange(0, EPOCHS), H.history["val_loss"], label="val_loss")
plt.plot(np.arange(0, EPOCHS), H.history["acc"], label="train_acc")
plt.plot(np.arange(0, EPOCHS), H.history["val_acc"], label="val_acc")
plt.title("Training Loss and Accuracy on Dataset")
plt.xlabel("Epoch #")
plt.ylabel("Loss/Accuracy")
plt.legend(loc="lower left")
plt.savefig("plot.png")
