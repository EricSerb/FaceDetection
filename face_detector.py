import cv2
import numpy as np
from utils import grablog
import os

logger = grablog(os.path.basename(__file__))


class FaceDetection(object):

    def __init__(self, cascade_file, test_path, save_dir):
        self.cascade = cv2.CascadeClassifier(cascade_file)
        self.prof_cascade = cv2.CascadeClassifier("open_cv_face_classifier/"
                                                  "haarcascade_profileface.xml")
        self.faces = None
        self.prof_faces = None
        self.test_img = []
        self.test_gray = []
        self.test_im_names = []
        self.save_dir = save_dir
        if not os.path.exists(self.save_dir):
            os.mkdir(self.save_dir)
        self.test_path = os.path.realpath(test_path)
        # need to read in all the randomly created test images
        # Need to make sure images are grayscale
        # Can take out gray list and have all the images be displayed in gray
        # if we want
        logger.info("Retrieving images from {}".format(self.test_path))
        for test in os.listdir(self.test_path):
            logger.info("Retrieving test image: {}".format(test))
            self.test_im_names.append(test)
            self.test_img.append(cv2.imread(os.path.join(self.test_path, test)))
            # self.test_gray.append(cv2.imread(os.path.join(self.test_path, test),
            #                                  cv2.IMREAD_GRAYSCALE))
            self.test_gray.append(cv2.cvtColor(self.test_img[-1],
                                               cv2.COLOR_BGR2GRAY))
        logger.info("Test images length: {}".format(len(self.test_img)))
        logger.info("Test gray images length: {}".format(len(self.test_gray)))

        assert len(self.test_img) == len(self.test_gray) == \
            len(self.test_im_names), "Error: length of test images must " \
                                     "be the same as gray images and names"

    def detect_faces(self, img):
        # Since Liu's code uses the pgm face image that is tiny we need to
        # look for a small area in the image and make sure we don't use any
        # areas that are too large!
        self.faces = self.cascade.detectMultiScale(img, 1.05, 0,
                                                   minSize=(15, 15),
                                                   maxSize=(40, 40))
        # self.faces = []
        # for x, y, w, h in faces:
        #     if x+w > 120 or y+h > 150:
        #         continue
        #     self.faces.append([x,y,w,h])

    def alter_faces(self, img):
        for (x, y, w, h) in self.faces:
            cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)
        return img
        # region of interest: may need this for altering specific area of
        # an image just pass roi to the function that will alter the image
        # and only that part of whole image altered
        # roi_gray = gray[y:y + h, x:x + w]
        # roi_color = img[y:y + h, x:x + w]

    def detect_prof_faces(self, img):
        self.prof_faces = self.prof_cascade.detectMultiScale(img, 1.05, 3,
                                                             minSize=(15, 15),
                                                             maxSize=(40, 40))

    def alter_prof_faces(self, img):
        for (x, y, w, h) in self.prof_faces:
            cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)
        return img
        # region of interest: may need this for altering specific area of
        # an image just pass roi to the function that will alter the image
        # and only that part of whole image altered
        # roi_gray = gray[y:y + h, x:x + w]
        # roi_color = img[y:y + h, x:x + w]

    @staticmethod
    def show(img, name):
        cv2.imshow(name, img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def save(self, img, name):
        cv2.imwrite(os.path.join(self.save_dir, name), img)
