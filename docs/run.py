#!/usr/bin/env python

'''
Rearrange content in sphinx-apidoc generated .rst files.

* Move "Module Contents" section to the top.
* Remove headers for "Module Contents", "Submodules" and "Subpackages",
  including their underlines and the following blank line.
'''


import argparse
import glob
import os
from functools import reduce

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def argument_parser():
    '''
    Define command line arguments.
    '''

    parser = argparse.ArgumentParser(
        description='''
        Rearrange content in sphinx-apidoc generated .rst files.
        '''
        )

    parser.add_argument(
        '-v', '--verbose',
        dest='verbose',
        default=False,
        action='store_true',
        help="""
            show more output.
            """
        )

    parser.add_argument(
        'input_file',
        metavar="INPUT_FILE",
        nargs='+',
        help="""
            file.
            """
        )

    return parser


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def main():
    '''
    Main program entry point.
    '''

    global args
    parser = argument_parser()
    args = parser.parse_args()

    filenames = [glob.glob(x) for x in args.input_file]
    if len(filenames) > 0:
        filenames = reduce(lambda x, y: x + y, filenames)

    for filename in set(filenames):

        # line_num was going to be for some consistency checks, never
        # implemented but left in place.
        found = {
            'Subpackages': {'contents': False, 'line_num': None},
            'Submodules': {'contents': False, 'line_num': None},
            'Module contents': {'contents': True, 'line_num': None},
            }

        in_module_contents = False
        line_num = 0
        reordered = []
        module_contents = []

        new_filename = '.'.join([filename, 'new'])
        new_filename = filename

        with open(filename, 'r') as fptr:

            for line in fptr:
                line = line.rstrip()
                discard = False

                line_num += 1

                if (
                    in_module_contents
                    and len(line) > 0
                    and line[0] not in ['.', '-', ' ']
                ):  # pylint: disable=bad-continuation
                    in_module_contents = False

                for sought in found:

                    if line.find(sought) == 0:

                        found[sought]['line_num'] = line_num
                        if found[sought]['contents']:
                            in_module_contents = True

                        discard = True
                        # discard the underlines and a blank line too
                        _ = fptr.readline()
                        _ = fptr.readline()

                if in_module_contents and not discard:
                    module_contents.append(line)

                elif not discard:
                    reordered.append(line)

                # print '{:<6}|{}'.format(len(line), line)

        with open(new_filename, 'w') as fptr:
            fptr.write('\n'.join(reordered[:3]))
            fptr.write('\n')
            if module_contents:
                fptr.write('\n'.join(module_contents))
                fptr.write('\n')
                if len(module_contents[-1]) > 0:
                    fptr.write('\n')
            if reordered[3:]:
                fptr.write('\n'.join(reordered[3:]))
                fptr.write('\n')

        if args.verbose:
            print(filename)


if __name__ == "__main__":
    main()
