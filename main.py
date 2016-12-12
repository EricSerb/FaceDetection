import argparse as ap
from utils import Dataset


def run():
    """
    Driver for the program
    :return: None
    """
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
                        # 'http://www.cs.fsu.edu/~liux/courses/cap5415-2014'
                        # '/assignments/lab3_info'
                        ],
            'help': 'specify url resource',
        }),
        'd': ('dir', {
            'default': 'res',
            'help': 'specify results directory',
        }),
    }

    for i in pargs:
        p.add_argument(
            '-{}'.format(i), '--{}'.format(pargs[i][0]), **pargs[i][1])

    # setup
    args = p.parse_args()
    dset = Dataset(args.src, args.dir, download=args.retrieve)
    print(len(dset.backs))


if __name__ == "__main__":
    run()
