import argparse as ap
from utils import Dataset, grablog, create_test_imgs, clean_compile
from face_detector import FaceDetection
import os
from time import clock
from platform import system

# res directory folders to check and ensure they exists and contain files
dirs = ["orldataset", "background"]


def run():
    """
    Driver for the program
    :return: None
    """
    logger = grablog(os.path.basename(__file__))
    logger.info("\n\n Running Face Detection")
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
        'm': ('module', {
            'help': 'choose a module to run',
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
                        # This is the Haar features... Not sure if needed yet
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
            # this will be changed to 'haar_cascade/cascade.xml'
            # once finished creating
            'default': 'lbp_classifier/cascade.xml',
            'help': 'specify cascade.xml file to use for detection',
        }),
        't': ('test_imgs', {
            'default': 'test_images',
            'help': 'directory where test images can be found in res directory',
        }),
    }

    for i in pargs:
        p.add_argument(
            '-{}'.format(i), '--{}'.format(pargs[i][0]), **pargs[i][1])

    # setup
    args = p.parse_args()
    if args.retrieve:
        # This probably does not need to be a class now but it is for the time
        # being
        # Refactor later
        logger.info("Starting downloads...")
        Dataset(args.src, args.dir)
        logger.info("Finished downloads")

    # This is to ensure we have files for the c program to use to create test
    # images
    try:
        for d in dirs:
            files = os.listdir(os.path.join(args.dir, d))
            assert files != []
    except (AssertionError, OSError) as e:
        logger.error("Directory does not exist or contains no files."
                     "Rerun with download flag -r")
        logger.error(e)
        raise e

    clean_compile(args.dir)
    create_test_imgs(args.dir, test_im_dir=args.test_imgs)

    logger.info("Retrieving test images...")
    face_dtec = FaceDetection(args.cascade,
                              os.path.join(args.dir, args.test_imgs),
                              os.path.join(args.dir, "found_faces"))
    logger.info("Finished retrieving test images")

    # All images have been downloaded, converted, and loaded in
    # Start of actual testing
    times = []

    if system() == 'Linux':
        logger.info("Starting testing phase on Linux....")
        for norm, gray, name in zip(face_dtec.test_img, face_dtec.test_gray,
                                    face_dtec.test_im_names):
            start = clock()
            face_dtec.detect_faces(gray)
            norm = face_dtec.alter_faces(norm)
            times.append(clock() - start)
            # face_dtec.show(norm, name)
            face_dtec.save(norm, name)

    elif system() == 'Windows':
        logger.info("Starting testing phase on Windows....")
        for norm, gray, name in zip(face_dtec.test_img, face_dtec.test_gray,
                                    face_dtec.test_im_names):
            clock()
            face_dtec.detect_faces(gray)
            face_dtec.alter_faces(norm)
            times.append(clock())
            face_dtec.show(norm, name)
            face_dtec.save(norm, name)
    logger.info("Testing complete")
    logger.info("It took {0:0.8f} seconds to detect and alter {1:d} "
                "images".format(sum(times), len(face_dtec.test_img)))


if __name__ == "__main__":
    run()
