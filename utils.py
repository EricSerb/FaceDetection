import sys
from getpass import getpass
from requests import get as wget
from requests.exceptions import RequestException
from cv2 import imread
import requests
import platform
from operator import itemgetter

if platform.system() == 'Linux':
    from HTMLParser import HTMLParser as hp
elif platform.system() == 'Windows':
    from html.parser import HTMLParser as hp
else:
    print('OS not currently supported')
    sys.exit(-1)

from os import \
    makedirs as f_mkdir, \
    listdir as f_list, \
    getcwd as f_cwd

from os.path import \
    exists as f_exists, \
    join as f_join, \
    basename as f_base, \
    splitext as f_splitext, \
    dirname as f_dir

h_links = []


class Dataset(object):
    """
    Encapsualtion of our dataset operations.
    """

    def __init__(self, src, dest, download=False):

        self.src = src
        self.dest = dest
        self.sub_dirs = ['s{}'.format(i) for i in range(1, 41)]
        # Will load faces by category as list in dict
        self.faces = {i: [] for i in self.sub_dirs}
        self.backs = []
        #self.h_links = []
        if download:
            self.auth = (getpass('user: '), getpass('pswd: '))

        if not f_exists(self.dest):
            f_mkdir(self.dest)

        for url in src:
            # TODO need a statement to take care of the Haar features if we
            # use them
            if isinstance(url, (bytes, str)) and download and (f_base(
                    url).strip() == 'background' or f_base(url).strip() ==
                    'lab3_info'):
                self.download(url)

            elif isinstance(url, (bytes, str)) and download and f_base(
                    url).strip() == 'orldataset':
                # we have multiple dirs in faces folder need to get all
                # face_names contains res_dir/sub/filename for each file and
                #  sub dir
                self.face_names = self.download_faces(url)

        self.back_f_path = f_join(self.dest, 'background')
        print('Backgrounds: {}'.format(self.back_f_path))

        self.face_f_path = f_join(self.dest, 'orldataset')
        print('Faces: {}'.format(self.face_f_path))

        # self.files = []
        self.back_files = []
        # self.imgs = {}
        self.load()
        assert self.faces
        assert self.backs

        # self.testcases = None
        # if type(cases) in (int, float):
        #     self.settests(int(cases))
        # else:
        #     self.testcases = list(flatten(cases)) \
        #         if cases is not None else []

    def download_faces(self, url):
        print('Downloading: {}'.format(f_base(url)))
        names = []
        for sub in self.sub_dirs:
            dir_link = '/'.join((url, sub))
            names = self._download_all(dir_link, dest=f_join(self.dest, sub))
        return names

    def download(self, url):
        sub_dir = f_base(url)
        cur_dld_dir = f_join(self.dest, sub_dir)
        print('Downloading: {}'.format(sub_dir))
        if not f_exists(cur_dld_dir):
            f_mkdir(cur_dld_dir)
        self._download_all(url, dest=cur_dld_dir)

    def load(self):
        print('Loading images...')
        try:
            # This needs a seperate loop for the backgrounds and for faces
            # and Haar features if we end up using them.

            # Reading in backgrounds
            files = f_list(self.back_f_path)
            sfiles = sorted([int(f[f.rfind('_') + 1:]) for f in map(itemgetter(0), map(f_splitext, files))])
            self.back_files = tuple('{}{}.jpg'.format('jan-12-2005-wh107_', i) for i in sfiles)

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
            print('Did you forget to download the data with \'-r\'?')
            print('Or maybe check your permissions?')
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
                if href.endswith('.jpg') or href.endswith('.pgm'):
                    h_links.append(href)
            except (KeyError, TypeError):
                pass

    def _download_all(self, url, dest=None):
        if dest is None:
            dest = self.dest
        h_links[:] = []
        href = self._HrefParser()
        print(url)
        href.feed(str(requests.get(url, auth=self.auth).content))
        _names = []
        for link in h_links:
            _names.append(
                self._download('/'.join((url, link)), dest=dest))
        return _names

    def _download(self, url, dest):
        if not f_exists(dest):
            f_mkdir(dest)
        name = f_join(dest, f_base(url))
        with open(name, 'wb') as out:
            out.write(requests.get(url, auth=self.auth).content)
        return name
