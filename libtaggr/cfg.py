#!/usr/bin/env python
# vim: ts=4 sw=4 et:

# import importlib
from . speaker import Speaker
from . optsparser import OParser
from . helpers import Helpers
from sys import argv as arglist

parser = OParser(arglist)
(opt, fnames) = parser.parse_args()
if opt.filenames:
    fnames += opt.filenames
spkr = Speaker(opt.quiet, opt.verbose)
hlpr = Helpers()
