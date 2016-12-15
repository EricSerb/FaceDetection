import sys
from getpass import getpass
from cv2 import imread
import requests
import platform
from operator import itemgetter
import logging
from subprocess import call, Popen, PIPE
from os import \
    makedirs as f_mkdir, \
    listdir as f_list, \
    getcwd as f_cwd, \
    chdir as f_cd, \
    rename as f_rename, \
    remove as f_rm, \
    system as f_sys

from os.path import \
    exists as f_exists, \
    join as f_join, \
    basename as f_base, \
    splitext as f_splitext, \
    dirname as f_dir, \
    realpath as f_rpath, \
    isfile as f_file

if platform.system() == 'Linux':
    from HTMLParser import HTMLParser as hp
elif platform.system() == 'Windows':
    from html.parser import HTMLParser as hp
else:
    print('OS not currently supported')
    sys.exit(-1)

h_links = []


def grablog(name):
    """
    Call this function from anywhere in the project (assuming it is imported).
    It will return the single logger instance used to record errors to the
    console stream, and general information to a file located in the project
    directory called fdmain.log.
    :return: The configured logger with the module name
    """
    # grab named logger from this directory
    logpath = f_join(f_dir(f_rpath(__file__)), 'fdmain.log')
    log = logging.getLogger(name)
    log.setLevel(logging.INFO)

    # logger stream handler setup
    fh = logging.FileHandler(logpath)
    ch = logging.StreamHandler()

    # set levels of what to log for stream and file
    fh.setLevel(logging.INFO)
    ch.setLevel(logging.ERROR)

    # create formatter for handler and add to logger
    fmt = logging.Formatter('%(asctime)s  %(name)-16s %(levelname)-8s: '
                            '%(message)s', datefmt='%y-%m-%d %H:%M.%S')
    fh.setFormatter(fmt)
    ch.setFormatter(fmt)

    # attach the handlers to the logger
    log.addHandler(fh)
    log.addHandler(ch)

    return log


logger = grablog(f_base(__file__))


class Dataset(object):
    """
    Encapsualtion of our dataset operations.
    """

    def __init__(self, src, dest):
        self.src = src
        self.dest = dest
        self.sub_dirs = ['s{}'.format(i) for i in range(1, 41)]
        # Will load faces by category as list in dict
        self.faces = {i: [] for i in self.sub_dirs}
        self.backs = []
        self.back_files = []
        self.auth = (getpass('user: '), getpass('pswd: '))

        if not f_exists(self.dest):
            f_mkdir(self.dest)

        for url in src:
            logger.info("Downloading from {}".format(url))
            if isinstance(url, (bytes, str)) and \
                    (f_base(url) == 'background' or
                     f_base(url) == 'lab3_info'):
                self.download(url)

            elif isinstance(url, (bytes, str)) and f_base(
                    url) == 'orldataset':
                # we have multiple dirs in faces folder need to get all
                # face_names contains res_dir/sub/filename for each file and
                #  sub dir
                self.face_names = self.download_faces(url)

        self.back_f_path = f_join(self.dest, 'background')
        logger.info('Backgrounds: {}'.format(self.back_f_path))

        self.face_f_path = f_join(self.dest, 'orldataset')
        logger.info('Faces: {}'.format(self.face_f_path))

        '''
        # This is the code for loading the original images in, but we need
        # to use the c program to create test images and then load those in.
        # C program will load in images from directories directly to the c
        # program
        # TODO take this code out since we don't actually need to load
        # these files in....
        self.load()
        for key in self.faces:
            assert self.faces[key] != []
        assert self.backs != []
        '''

    def download_faces(self, url):
        names = []
        for sub in self.sub_dirs:
            dir_link = '/'.join((url, sub))
            names = self._download_all(dir_link, dest=f_join(self.dest,
                                                             f_base(url), sub))
        return names

    def download(self, url):
        sub_dir = f_base(url)
        cur_dld_dir = f_join(self.dest, sub_dir)
        if not f_exists(cur_dld_dir):
            f_mkdir(cur_dld_dir)
        self._download_all(url, dest=cur_dld_dir)

    def load(self):
        logger.info('Loading images...')
        try:
            # This needs a seperate loop for the backgrounds and for faces
            # and Haar features if we end up using them.

            # Reading in backgrounds
            files = f_list(self.back_f_path)
            sfiles = sorted([int(f[f.rfind('_') + 1:]) for f in
                             map(itemgetter(0), map(f_splitext, files))])
            self.back_files = tuple('{}{}.png'.format('jan-12-2005-wh107_', i)
                                    for i in sfiles)

            for f in self.back_files:
                p = f_join(f_cwd(), f_join(self.back_f_path, f))

                self.backs.append(imread(p))

                # putting everything in memory here
                # self.imgs.setdefault(c, []).append((f, imread(p)))

            # Reading in Faces
            # May need to fix this to sort them be we will see
            for f in self.face_names:
                p = f_join(f_cwd(), f)
                sub_name = f_base(f_dir(f))
                self.faces[sub_name].append(imread(p))

        except (OSError, IOError) as e:
            logger.error('Did you forget to download the data with \'-r\'?')
            logger.error('Or maybe check your permissions?')
            logger.error(e)
            raise e

    def __iter__(self):
        """
        Generator to walk over this data set in an ordered fashion.
        """
        assert self.back_files
        for f in self.back_files:
            yield f

    class _HrefParser(hp):
        def handle_starttag(self, tag, attrs):
            try:
                href = dict(attrs)['href']
                # Adding .c, .o, .h to get the files for the random image
                # generator that we may need later on
                # There is also .lis files if we need those at all
                if href.endswith('.jpg') or href.endswith('.pgm') or \
                        href.endswith('.c') or href.endswith('.h') or \
                        href.endswith('.o') or href.endswith('.lis') or \
                        href.endswith('makefile'):
                    h_links.append(href)
            except (KeyError, TypeError):
                pass

    def _download_all(self, url, dest=None):
        if dest is None:
            dest = self.dest
        h_links[:] = []
        href = self._HrefParser()
        href.feed(str(requests.get(url, auth=self.auth).content))
        _names = []
        for link in h_links:
            _names.append(
                self._download('/'.join((url, link)), dest=dest))
        return _names

    def _download(self, url, dest):
        if not f_exists(dest):
            f_mkdir(dest)
        url_base = f_base(url)
        name = f_join(dest, url_base)
        if f_splitext(url_base)[1] in ['.c', '.o', '.h', '.lis'] \
                or url_base == 'makefile':
            name = f_join(self.dest, url_base)
        with open(name, 'wb') as out:
            out.write(requests.get(url, auth=self.auth).content)
        return name


def clean_compile(res_dir):
    """
    This function is used to clean and compile the testimage program that is
    needed later
    :return: None
    """
    try:
        path = f_join('.', res_dir)
        logger.info("Moving to {} from {}".format(path, f_base(f_cwd())))
        f_cd(path)
    except OSError as e:
        logger.error("{} could not found or could not be accessed".format(path))
        logger.error(e)
        raise e
    try:
        # Must first move to res dir so that in the same place as the make file
        logger.info("Cleaning and compiling testimage...")
        call(["make", "clean"])
        call(["make"])
    except OSError as e:
        logger.error("Make clean or make failed")
        logger.error(e)
        raise e
    logger.info("Successful clean and compile")
    f_cd('..')


def _gather_tests(test_im_dir):
    if not f_exists(test_im_dir):
        f_mkdir(test_im_dir)
    files = [f for f in map(f_rpath, f_list(f_cwd())) if f_file(f) and
             "background" in f_splitext(f_base(f))[0] and
             ".lis" != f_splitext(f_base(f))[1]]
    for f in files:
        f_rename(f, f_join(f_dir(f), test_im_dir, f_base(f)))


def _rm_old_tests(test_im_dir):
    if f_exists(test_im_dir):
        files = [f for f in map(f_rpath, f_list(test_im_dir)) if f_file(f) and
                 "background" in f_splitext(f_base(f))[0]]
        for f in files:
            f_rm(f)


def create_test_imgs(res_dir, exe="./testimage", num_test=10,
                     test_im_dir="test_images"):
    """
    This function will be called to create test images using the c code
    provided by Dr. Liu
    Args that can be passed to testimage:
    -m: 0 = slow pixel by pixel matching, 1 = Fast tempalte matching,
        2 = Real-time based on Haar features
    -t: number of test images. Max is 100 default is 10
    -f: path to facelist
    -b: path to background list
    -v: verbose
    -o: occlusion. Takes height and width to be occluded on each positive image
        window
    -s: seed
    :param res_dir: The results directory where the executable file is stored
    :param exe: The name of the executable file
    :param num_test: The number of test images requested
    :return: This will create images for testing
    """
    # May want to delete previous images before running this each time so no
    # old images are left from previous runs
    # This will probably need to be changed for windows

    logger.info("Creating test images")
    try:
        f_cd(res_dir)
        test_im_dir = f_join(f_cwd(), test_im_dir)
        _rm_old_tests(test_im_dir)
        # f_sys(" ".join((exe, "-m", "2", "-t", str(num_test))))
        p = Popen([exe, "-m", "2", "-t", str(num_test)], stdout=PIPE)
        logger.info("Output of {}:".format(exe))
        logger.info("\n{}".format(p.stdout.read()))
        p.wait()
        if p.returncode < 0:
            logger.error("Failed to fully run {}".format(exe))
            raise OSError
        _gather_tests(test_im_dir)
        f_cd('..')
    except OSError as e:
        logger.error("Cannot find/execute {}".format(exe))
        logger.error(e)
        raise e
    logger.info("Finished creating test images")
