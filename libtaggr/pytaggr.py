#!/usr/bin/env python
# vim: ts=4 sw=4 et:
'''
    cli implementations of many mutagen metadata functions,
    created for several compressed audio formats, with the
    intention of mainly being used to tag recordings of live
    concerts, & convert filepaths to tags or tags to filenames
'''

import re
import sys
# from importlib import import_module

from libtaggr.tageditor import TagEditors
from libtaggr.optsparser import OParser
parser = OParser(sys.argv)


def main():

    arglist = sys.argv
    if 'id3help' in arglist:
        from mutagen.easyid3 import EasyID3
        for key in EasyID3.valid_keys.keys():
            print(key,)
    tageditor = TagEditors()

    err = 0
    argstr = ' '.join(arglist)
    if len(arglist) < 2:
        parser.print_usage()
        print('-h|--help for help')
        sys.exit()

    p = '(-t|--tag|-a|--add|-p|--pattern|-r|--remove|-f|--files) +?-[^ ]*'
    mo = re.search(p, argstr)
    if mo:
        print('illegal option combination: ', mo.group())
        sys.exit(1)

        if err:
            print('Aborting...')

    tageditor.start()
    sys.exit(0)


if __name__ == '__main__':
    sys.exit(main())
