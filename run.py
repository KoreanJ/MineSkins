import sys
import shutil
import os
import json
from etl import *

DATA_CONFIG = 'config/data-config.json'

def main(args):

    # check if args are correct
    is_correct = True
    usage_args = ['test-project', 'data', 'clean', 'train', 'visualize']
    for arg in args:
        if arg not in usage_args:
            is_correct = False
            bad = arg

    # show proper usage if args not correct
    barrier_len = 80
    if not is_correct:
        print('*'*barrier_len)
        print('Argument "{0}" is not recognized. Usage: '.format(bad))
        print('\tpython3 run.y [test-project] [data] [clean] [train] [visualize] ...')
        print('*'*barrier_len)

    # process command targets
    if 'clean' in args:
        if os.path.exists('out/'):
            shutil.rmtree('out/')
    if 'data' in args:
        with open(DATA_CONFIG) as f:
            cfg = json.load(f)
        get_data(**cfg)
    if 'test-project' in args:
        test_project()
    if 'train' in args:
        print('Training DCGAN')
    if 'visualize' in args:
        print('Visualizing')

if __name__ == '__main__':
    main(sys.argv[1:])