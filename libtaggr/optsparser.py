#!/usr/bin/env python
# vim: ts=4 sw=4 et:

import os
from optparse import OptionParser


class OParser(OptionParser):
    def __init__(self, args):
        OptionParser.__init__(self)
        self.usage = ("%prog [options] filenames")
        self.epilog = '%s id3help: for help with id3 tags' % \
                      os.path.basename(args[0])
        self.add_option('-t', '--tag', dest='tag', action='append',
                        help="set a tag", metavar='tag=value')
        self.add_option('-a', '--add', dest='add', action='append',
                        help='set/add values to a tag, \
                        without removing any existing values',
                        metavar='tag=value')
        self.add_option('-p', '--pattern', dest='pattern', action='store',
                        help='substitution pattern from filename',
                        metavar="'%n %t.flac'")
        self.add_option('--fn2tag', dest='fn2tag', action='store',
                        help='same as -p | --pattern')
        self.add_option('-r', '--remove', dest='remove', action='append',
                        help='remove a tag value or entire tag',
                        metavar="'tag' or 'tag=value'")
        self.add_option('-j', '--justify', dest='justify', action='store_true',
                        help='zero-justify tracknumbers')
        self.add_option('--clear', dest='clear', action='store_true',
                        help='clear all tags')
        self.add_option('-n', '--noact', dest='noact', action='store_true',
                        help="just show what changes would be made")
        self.add_option('-c', '--confirm', dest='confirm', action='store_true',
                        help='show changes and prompt for confirmation \
                        to save')
        self.add_option('-f', '--files', dest='filenames', action='append',
                        help='one or more filenames/globs')
        self.add_option('-q', '--quiet', dest='quiet', action='store_true',
                        help='no output to stdout')
        self.add_option('--tag2fn', dest='tag2fn', action='store',
                        help='substitution pattern from tags',
                        metavar="'%n %t.flac'")
        self.add_option('--noconfirm', dest='noconfirm', action='store_true',
                        help='do not prompt for confirmation \
                        (only on rename/move)')
        self.add_option('-s', '--filter', dest='symbols', action='store',
                        help='one or more characters to filter from tags \
                        used to build filenames',
                        metavar="'!@$&*/?'")
        self.add_option('-m', '--map', dest='map', action='store',
                        help='replace all instances of a char with another \
                        char in conjunction with --tag2fn',
                        metavar="/ -")
        self.add_option('-i', '--index', dest='idx', action='store_true',
                        help='index files by filename order \
                        (persistent file order)')
        self.add_option('-v', '--verbose', dest='verbose', action='store_true',
                        help='extra output')
        self.add_option('-V', '--version', dest='vers', action='store_true',
                        help='show version')
