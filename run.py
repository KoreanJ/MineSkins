import sys

def main(args):

    # check if args are correct
    is_correct = True
    usage_args = ['test', 'data', 'clean']
    for arg in args:
        if arg not in usage_args:
            is_correct = False
            bad = arg

    # show proper usage if args not correct
    barrier_len = 80
    if not is_correct:
        print('*'*barrier_len)
        print('Argument "{0}" is not recognized. Usage: '.format(bad))
        print('\tpython3 run.y [test] [data] [clean] ...')
        print('*'*barrier_len)

if __name__ == '__main__':
    main(sys.argv[1:])