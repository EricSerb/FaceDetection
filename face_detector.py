import cv2
import numpy as np
from utils import grablog
import os
import shutil

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
        if os.path.exists(save_dir):
            shutil.rmtree(save_dir)
        self.blend_im = cv2.imread("Xiuwen_liu_Large.jpg")
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

    def detect_faces(self, img, occl):
        # Since Liu's code uses the pgm face image that is tiny we need to
        # look for a small area in the image and make sure we don't use any
        # areas that are too large!
        '''These are the perfect settings without occlusion'''
        if not occl:
            self.faces = self.cascade.detectMultiScale(img, 1.08, 2,
                                                   minSize=(10, 10),
                                                   maxSize=(40, 40))

        else:
            '''100% detection with up to 3x4 occlusion'''
            self.faces = self.cascade.detectMultiScale(img, 1.045, 2,
                                                   minSize=(10, 10),
                                                   maxSize=(40, 40))

    def alter_faces(self, img):
        for x, y, w, h in self.faces:
            '''Code to produce rectangle around found faces'''
            # cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)

            roi_color = img[y: y+h, x: x+w]
            '''Blur out images. options explained in main'''
            # roi_color[:, :, :] = cv2.morphologyEx(
            #     roi_color, cv2.MORPH_BLACKHAT, cv2.getStructuringElement(
            #         cv2.MORPH_RECT, (20, 20)))[:, :, :]
            '''Uncomment below to have Dr. Liu appear'''
            roi_color[:,:,:] = cv2.resize(self.blend_im, (w, h))[:,:,:]
        return img

    @staticmethod
    def show(img, name):
        cv2.imshow(name, img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def save(self, img, name):
        cv2.imwrite(os.path.join(self.save_dir, name), img)
