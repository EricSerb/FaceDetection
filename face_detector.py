import cv2
import numpy as np
from utils import grablog
import os

logger = grablog(os.path.basename(__file__))


class FaceDetection(object):

    def __init__(self, cascade_file, res, save_dir):
        self.cascade = cv2.CascadeClassifier(cascade_file)
        self.faces = None
        self.test_img = []
        self.test_gray = []
        self.test_im_names = []
        self.save_dir = save_dir
        self.test_path = os.path.join(res, "test_images")
        # need to read in all the randomly created test images
        # Need to make sure images are grayscale
        # Can take out gray list and have all the images be displayed in gray if we want
        for test in os.listdir(self.test_path):
            self.test_im_names.append(test)
            self.test_img.append(cv2.imread(os.path.join(self.test_path, test)))
            self.test_gray.append(cv2.imread(os.path.join(self.test_path, test), cv2.IMREAD_GRAYSCALE))

        assert len(self.test_img) == len(self.test_gray) == len(self.test_im_names), \
            "Error: length of test images must be the same as gray images and names"

    def detect_faces(self, img):
        self.faces = self.cascade.detectMultiScale(img, 1.3, 5)

    def alter_faces(self, img):
        for (x, y, w, h) in self.faces:
            cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)
            # region of interest: may need this for altering specific area of an image
            # just pass roi to the function that will alter the image and only that part of whole image altered
            # roi_gray = gray[y:y + h, x:x + w]
            # roi_color = img[y:y + h, x:x + w]

    @staticmethod
    def show(img, name):
        cv2.imshow(name, img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def save(self, img, name):
        cv2.imwrite(os.path.join(self.save_dir, name), img)
