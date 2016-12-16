import argparse as ap
from utils import Dataset, grablog, create_test_imgs, clean_compile
from face_detector import FaceDetection
import os
from time import clock
from platform import system
import cProfile, pstats

# res directory folders to check and ensure they exists and contain files
dirs = ["orldataset", "background"]


def run():
    """
    Driver for the program
    :return: None
    """
    logger = grablog(os.path.basename(__file__))
    p = ap.ArgumentParser(
        prog='vis_proj',
        formatter_class=ap.ArgumentDefaultsHelpFormatter,
        description='cli')

    pargs = {
        #
        # Add arg in this format:
        #
        #   'short' : ('long', { *args }),
        #
        # where { *args } is a dictionary of
        # keyword arguments used by p.parse_args
        #
        'v': ('video', {
            'default': False,
            'action': 'store_true',
            'help': 'Run local image face detection if False, '
                    'otherwise run webcam face detection',
        }),
        'g': ('debug', {
            'default': False,
            'action': 'store_true',
            'help': 'run in debug mode',
        }),
        'r': ('retrieve', {
            'default': False,
            'action': 'store_true',
            'help': 'retrieve web resources',
        }),
        's': ('src', {
            'default': ['http://www.cs.fsu.edu/~liux/courses/cap5415-2016'
                        '/assignments/lab3_info/orldataset',
                        'http://www.cs.fsu.edu/~liux/courses/cap5415-2016'
                        '/assignments/lab3_info/background',
                        'http://www.cs.fsu.edu/~liux/courses/cap5415-2014'
                        '/assignments/lab3_info'
                        ],
            'help': 'specify url resource',
        }),
        'd': ('dir', {
            'default': 'res',
            'help': 'specify results directory',
        }),
        'c': ('cascade', {
            # 'default': 'lbp_classifier/cascade.xml',
            # 'default': 'haar_classifiers/'
            #            'haarcascade_frontalface_default.xml',
            'default': 'haar_classifiers/'
                       'haarcascade_frontalface_alt2.xml',
            'help': 'specify cascade.xml file to use for detection',
        }),
        't': ('test_imgs', {
            'default': 'test_images',
            'help': 'directory where test images can be found in res directory',
        }),
        'n': ('num_tests', {
            'default': '10',
            'help': 'number of test images to be created',
        }),
        'o': ('occlusion', {
            'default': False,
            'action': 'store_true',
            'help': 'Will occlude the faces in the test images with 3x4 patch',
        }),
    }

    for i in pargs:
        p.add_argument(
            '-{}'.format(i), '--{}'.format(pargs[i][0]), **pargs[i][1])

    # setup
    args = p.parse_args()
    logger.info("\n\n Running Face Detection")

    if not args.video:
        if args.retrieve:
            # This probably does not need to be a class now but it is for
            # the time being
            # Refactor later
            logger.info("Starting downloads...")
            Dataset(args.src, args.dir)
            logger.info("Finished downloads")

        # This is to ensure we have files for the c program to use to
        # create test images
        try:
            for d in dirs:
                files = os.listdir(os.path.join(args.dir, d))
                assert files != []
        except (AssertionError, OSError) as e:
            logger.error("Directory does not exist or contains no files."
                         "Rerun with download flag -r")
            logger.error(e)
            raise e

        if system() == "Linux":
            clean_compile(args.dir)
            create_test_imgs(args.dir, test_im_dir=args.test_imgs,
                             num_test=args.num_tests, occl=args.occlusion)

        logger.info("Retrieving test images...")
        face_dtec = FaceDetection(args.cascade,
                                  os.path.join(args.dir, args.test_imgs),
                                  os.path.join(args.dir, "found_faces"))
        logger.info("Finished retrieving test images")

        # All images have been downloaded, converted, and loaded in
        # Start of actual testing
        times = []
        found = []
        pr = cProfile.Profile()
        pr.enable()

        if system() == 'Linux':
            logger.info("Starting testing phase on Linux....")
            for norm, gray, name in zip(face_dtec.test_img, face_dtec.test_gray,
                                        face_dtec.test_im_names):
                face_dtec.detect_faces(gray, args.occlusion)
                norm = face_dtec.alter_faces(norm)
                face_dtec.save(norm, name)

                if len(face_dtec.faces) > 0:
                    found.append(True)
                else:
                    found.append(False)

                    # face_dtec.show(norm, name)

        elif system() == 'Windows':
            logger.info("Starting testing phase on Windows....")
            for norm, gray, name in zip(face_dtec.test_img, face_dtec.test_gray,
                                        face_dtec.test_im_names):
                start = clock()
                face_dtec.detect_faces(gray, args.occlusion)
                norm = face_dtec.alter_faces(norm)
                # face_dtec.show(norm, name)
                face_dtec.save(norm, name)
                times.append(clock()-start)

                if len(face_dtec.faces) > 0:
                    found.append(True)
                else:
                    found.append(False)

        logger.info("Testing complete")
        logger.info("{} frames were processed in {} seconds. This comes to {}"
                    " frames/sec being detected and manipulated.".format(
                    len(face_dtec.test_im_names), sum(times),
                    len(face_dtec.test_im_names) / sum(times)))
        pr.disable()
        sortby = 'cumulative'
        s = open("fdmain.log", "a")
        ps = pstats.Stats(pr, stream=s).strip_dirs().sort_stats(sortby)
        ps.print_stats()
        s.close()
        # for im_time, im_name in zip(times, face_dtec.test_im_names):
        #     logger.info("It took {0:0.8f} seconds to detect and alter {1}"
        #                 "".format(im_time, im_name))
        # logger.info("It took {0:0.8f} seconds to detect and alter {1:d} "
        #             "images".format(sum(times), len(face_dtec.test_img)))
        for f in zip(found, face_dtec.test_im_names):
            logger.info("Images idenftied correctly {}".format(f))

    else:
        # Implementing the webcam code here
        import cv2
        cascPath = args.cascade
        faceCascade = cv2.CascadeClassifier(cascPath)
        blend_im = cv2.imread("Xiuwen_liu_Large.jpg")

        video_capture = cv2.VideoCapture(0)
        num_frames = 0
        times = []
        pr = cProfile.Profile()
        pr.enable()

        while True:
            # Capture frame-by-frame
            ret, frame = video_capture.read()

            start = clock()

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            faces = faceCascade.detectMultiScale(
                gray,
                scaleFactor=1.21,
                minNeighbors=5,
                minSize=(30, 30),
            )

            # Draw a rectangle around the faces
            for x, y, w, h in faces:
                roi_color = frame[y: y + h, x: x + w]
                '''
                This function can take a number of arguments in place of
                cv2.MORPH_x
                Options in place of x:
                OPEN, CLOSE, GRADIENT, TOPHAT, BLACKHAT'''
                roi_color[:, :, :] = cv2.morphologyEx(
                    roi_color, cv2.MORPH_CLOSE, cv2.getStructuringElement(
                     cv2.MORPH_RECT, (20, 20)))[:,:,:]
                '''
                This line plus line 182 will allow you to look like Dr. Liu
                '''
                # roi_color[:,:,:] = cv2.resize(blend_im, (w, h))[:,:,:]

            times.append(clock() - start)

            # Display the resulting frame
            cv2.imshow('Face Detection', frame)
            num_frames += 1

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        logger.info("{} frames were processed in {} seconds. This comes to {}"
                    " frames/sec being detected and manipulated.".format(
                    num_frames, sum(times), num_frames/sum(times)))
        pr.disable()
        sortby = 'cumulative'
        s = open("fdmain.log", "a")
        ps = pstats.Stats(pr, stream=s).strip_dirs().sort_stats(sortby)
        ps.print_stats()
        s.close()

        # When everything is done, release the capture
        video_capture.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    run()
