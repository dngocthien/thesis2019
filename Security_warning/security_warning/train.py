import json
import os

import cv2
import numpy as np
from imutils import paths
from keras import Input, Model
from keras.callbacks import ModelCheckpoint, EarlyStopping
from keras.optimizers import RMSprop
from keras_preprocessing.image import ImageDataGenerator
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelBinarizer

from callbacks.training_monitor import TrainingMonitor
from security_warning.config import config
from preprocessing.meanpreprocessor import MeanPreprocessor
from networks.VGG16 import base, head


class FineTuner:
    def __init__(self):
        pass

    @staticmethod
    def finetune(controller=None):
        # initialize the image preprocessors

        (R, G, B) = ([], [], [])
        for imagePath in paths.list_images(config.IMAGE):
            image = cv2.imread(imagePath)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image = cv2.resize(image, (config.IMAGE_SIZE, config.IMAGE_SIZE), interpolation=cv2.INTER_AREA)

            (b, g, r) = cv2.mean(image)[:3]
            R.append(r)
            G.append(g)
            B.append(b)
        (R, G, B) = (np.mean(R), np.mean(G), np.mean(B))
        D = {"R": R, "G": G, "B": B}
        meanPath = open(config.DATASET_MEAN, "w")
        meanPath.write(json.dumps(D))
        meanPath.close()
        mp = MeanPreprocessor(R, G, B)

        data = []
        labels = []

        for imagePath in paths.list_images(config.IMAGE):
            image = cv2.imread(imagePath)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image = cv2.resize(image, (config.IMAGE_SIZE, config.IMAGE_SIZE), interpolation=cv2.INTER_AREA)
            image = mp.preprocess(image)
            data.append(image)
            label = imagePath.split(os.path.sep)[-2]
            labels.append(label)

        list_face = [str(x) for x in np.unique(labels)]
        num_classes = len(list_face)
        if num_classes < 2:
            controller.show_mesg('You have not add any face!')
            return

        f = open(config.CLASS_NAMES_PATH, "w")
        f.write(json.dumps(list_face))
        f.close()

        # scale the raw pixel intensities to the range [0, 1]
        data = np.array(data, dtype="float") / 255.0
        labels = np.array(labels)

        # partition train set : test set with ratio 75:25
        (trainX, testX, trainY, testY) = train_test_split(data, labels, test_size=0.25, stratify=labels, random_state=42)

        # convert the labels from integers to vectors
        lb = LabelBinarizer().fit(trainY)
        trainY = lb.transform(trainY)
        testY = lb.transform(testY)

        # prepare augmentation
        aug = ImageDataGenerator(rotation_range=12, zoom_range=0.3, width_shift_range=0.2, height_shift_range=0.2,
                                 shear_range=0.2, horizontal_flip=True, fill_mode="nearest")

        callbacks = [
            TrainingMonitor(fig_path=config.FIG_PATH, json_path=config.JSON_PATH, start_at=1, controller=controller),
            ModelCheckpoint(filepath=config.MODEL_PATH, monitor='val_loss', verbose=1, save_best_only=True,
                            save_weights_only=False, mode='auto', period=1),
            EarlyStopping(monitor='val_loss', mode='auto', min_delta=1e-4, patience=5, verbose=1, baseline=0.01)
        ]

        # baseModel = VGGFace(weights="vggface", include_top=False, input_tensor=Input(shape=(
        #     config.IMAGE_SIZE, config.IMAGE_SIZE, 3)))
        # headModel = self.build_head(baseModel.output, num_classes, 128)
        # model = Model(inputs=baseModel.input, outputs=headModel)

        baseModel = base(input_tensor=Input(shape=(config.IMAGE_SIZE, config.IMAGE_SIZE, 3)))
        headModel = head(baseModel.output, num_classes, 128)
        baseModel.load_weights(config.PRETRAINED_VGG16)
        model = Model(inputs=baseModel.input, outputs=headModel)

        # freeze layers
        for (i, layer) in enumerate(baseModel.layers):
            layer.trainable = False

        print("[INFO] compiling model...")
        opt = RMSprop(lr=1e-3)
        if num_classes > 2:
            model.compile(loss="categorical_crossentropy", optimizer=opt, metrics=["accuracy"])
        else:
            model.compile(loss="sparse_categorical_crossentropy", optimizer=opt, metrics=["accuracy"])

        print("[INFO] training head...")
        model.fit_generator(aug.flow(trainX, trainY, batch_size=config.BATCH_SIZE), validation_data=(testX, testY),
                            epochs=config.EPOCH, steps_per_epoch=len(trainX) // config.BATCH_SIZE, validation_steps=8,
                            callbacks=callbacks)

        # evaluate the network
        print("[INFO] evaluating network...")
        predictions = model.predict(testX, batch_size=16)
        print(classification_report(testY.argmax(axis=1), predictions.argmax(axis=1), target_names=lb.classes_))
