import cv2
import numpy as np
from utils import grablog
import os

logger = grablog()


class FaceDetection(object):

    def __init__(self, cascade_file):
        cascade = cv2.CascadeClassifier(cascade_file)
        faces = None
        test_img = []
        # need to read in all the randomly created test images
        logger.info("Reading in test images")
        for test in os.listdir("res/test_images"):
            test_img.append(cv2.imread(test))
