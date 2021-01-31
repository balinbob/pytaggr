#!/usr/bin/env python
# vim: ts=4 sw=4 et:


import sys
import os
import re
from mutagen import File
from mutagen.mp3 import EasyMP3 as MP3
from mutagen.mp3 import HeaderNotFoundError
from libtaggr import cfg
from libtaggr.taggr import Subster


sep = os.path.sep


class Helpers():
    def __init__(self):
        self.opt = cfg.opt
        self.spkr = cfg.spkr     # Speaker(opt.quiet, opt.verbose)
        self._all = False

    def str2list(self, s):
        li = []

        try:
            if not s.startswith('['):
                s = '[' + s
            if not s.endswith(']'):
                s = s + ']'
        except ValueError:
            return False
        li = eval(s)
        if not isinstance(li, list):
            return False
        for val in s:
            li.append(str(val))
        return li

    def splitarg(self, arg):
        ''' return key and value pairs;  accept
            either a string or list as the value
        '''
        k = ''
        v = []
        values = []
        try:
            k, v = arg.split('=', 1)
        except ValueError:
            if not k:
                self.spkr.say(2, 'Missing argument', True, True)
            if len(v) < 1:
                self.spkr.say(2, 'Missing value', True, True)
        try:
            li = v.split(',')
        except NameError as e:
            print(e)

        for val in li:
            values.append(str(val))
        if not values:
            values = li
        return (k, values)

    def mf_open(self, fname):
        mf = None
        if os.path.splitext(fname)[1] == '.mp3':
            try:
                mf = MP3(fname)
            except HeaderNotFoundError:
                try:
                    mf = File(fname)
                except Exception as e:
                    print(e)
                    self.spkr.say(1,
                                  'cannot find metadata header:  %s' % fname)
        else:
            try:
                mf = File(fname)
            except IOError as e:
                print(e)
        return mf

    def get_response(self, _use):
        resp = 'x'
        if _use:
            # if self.opt.noact:
            # return False
            if self._all:
                return True
            if not any([self.opt.confirm, self.opt.fn2tag, self.opt.tag2fn]):
                if not any([self.opt.tag, self.opt.add,
                            self.opt.remove, self.opt.clear]):
                    return True
            while resp not in 'ynaq':
                try:
                    resp = input('confirm changes? [y]/n/a/q ')
                except KeyboardInterrupt:
                    print('Quitting')
                    sys.exit(4)
            if resp == '':
                resp = 'y'
            if resp[0].lower() == 'q':
                print('Quitting')
                sys.exit(0)
            if resp[0].lower() == 'y':
                return True
            if resp[0].lower() == 'a':
                self._all = True
                return True
        return False

    def confirm(self):
        # print()
        ''' honor certain options regarding actual file-writing,
            and input of y or n to proceed with file-writing.
        '''
        if self.opt.noact:
            return False
        if self.opt.noconfirm:
            return True

        if any([self.opt.tag, self.opt.add, self.opt.remove, self.opt.clear,
                self.opt.fn2tag, self.opt.tag2fn]):
            _use = True
        else:
            _use = False
        # self._all = False
        return self.get_response(_use)

    def subs(self, mf):
        opt = self.opt
        '''
            func = str, fn2tag or tag2fn
            fname = str
            vals = dict - full existing tag
            opt = instantiation of class OP
        '''
        if opt.fn2tag:
            pat = opt.fn2tag
            subster = Subster(pat, 'fn2tag')
            d = subster.getdict(mf.filename)
            for k in d:
                li = d.get(k, [])
                mf[k] = li

                self.spkr.say(2, 'from filename: %s=%s' % (k, li[0]))
            return mf

        if opt.tag2fn:
            pat = opt.tag2fn.strip(sep)
            fname = ''
            subster = Subster(pat, 'tag2fn')
            fnlist = subster.getfnlist()
            if 'tracknumber' in fnlist:
                tn = 1
            else:
                tn = 0
            lit = True
            for item in fnlist:
                lit = not lit
                if lit:
                    if not tn and item == 'tracknumber':
                        item = 'track'
                    if tn and item == 'track':
                        item = 'tracknumber'
                    if item.startswith('track') and opt.justify:
                        subst = mf[item][0].rjust(2, '0')
                    else:
                        subst = mf[item][0]
                    if opt.symbols:
                        pat = '['+opt.symbols+']'
                        subst = re.sub(pat, '', subst)
                        subst = subst.strip()
                    fname += subst
                else:
                    fname += item
            return fname
