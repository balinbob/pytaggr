#!/usr/bin/env python
# vim: ts=4 sw=4 et:

import sys


class Speaker():
    ''' wrapper to simplify printing user messages '''
    def __init__(self, quiet, verbose):
        self.x = 0
        self.quiet = quiet
        self.verbose = verbose

    def say(self, tabs, strng, error=False, verbose=False, end='\n'):
        tab = '\t' * tabs
        if error:
            print('%s%s' % (tab, strng))
            sys.exit(1)
        self.quiet = self.quiet and not verbose
        if not self.quiet:
            print('%s%s' % (tab, strng), end=end)
            pass


'''
    def speak(self, strng):
        if not self.quiet:
            if strng[:2] == '\n\t':
                print(' ' * 48, strng[2:],)
                self.x += len(strng)
            elif strng[:1] == '\t':
                strng += ' '*120
                strng = strng[self.x:]
                print(strng[1:],)
            else:
                print(strng,)
'''
