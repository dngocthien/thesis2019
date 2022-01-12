import glob
import os


def rename(dir, pattern, titlePattern):
    for i, pathAndFilename in enumerate(glob.iglob(os.path.join(dir, pattern))):
        title, ext = os.path.splitext(os.path.basename(pathAndFilename))
        os.rename(pathAndFilename, os.path.join(dir, titlePattern + str(i) + ".jpg"))


rename(r'.\liveness_detection\dataset_live_fake\\real',
       r'*.jpg', r'n_')
