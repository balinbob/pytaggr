#!/usr/bin/env python
# vim: ts=4 sw=4 et:

import os
from os.path import sep
from . cfg import opt, fnames, spkr, Helpers
from glob import glob


class TagEditors(object):
    fnum = 0

    def __init__(self):
        self.vals = {}

        self.modded = any([opt.clear, opt.remove, opt.add, opt.tag, opt.fn2tag,
                          opt.tag2fn, opt.justify, opt.idx])
        self.opt = opt
        self.fnames = fnames
        if opt.pattern:
            self.fn2tag = opt.pattern

        self.hlpr = Helpers()

    def glob_parse(self, fpaths):
        fnames = []
        for fpath in fpaths:
            if isinstance(fpath, str):
                fnames.extend(glob(fpath))
            else:
                fnames.extend(fpath)
        return fnames

    def start(self):
        self.fnames = self.glob_parse(self.fnames)

        self.chkfiles()
        # self.fnames = fnames
        for fname in self.fnames:
            self.fnum += 1
            origfn = fname
            mf = self.hlpr.mf_open(fname)

            if opt.clear:
                mf.clear()
                spkr.say(2, '%s: clearing all tags')

            if opt.idx:
                self.index(mf)
            if opt.remove:
                mf = self.remove(spkr, opt, mf)

            if opt.tag:
                mf = self.tag(spkr, opt, mf)
            if opt.add:
                mf = self.add(spkr, opt, mf)

            if opt.fn2tag:
                mf = self.hlpr.subs(mf)
            if opt.tag2fn:
                fname = self.hlpr.subs(mf)

            if opt.justify:
                mf = self.justify(opt, mf)
            if not any([self.modded, opt.quiet]):
                print(mf.pprint())
                continue

            self.write(spkr, fname, mf)

            if opt.tag2fn:
                self.tag2fn(origfn, fname)

    def write(self, spkr, fname, mf):
        spkr.say(0, '%s' % fname)
        if opt.noact or opt.confirm:
            for key in self.vals:
                spkr.say(1, key + '=' + str(self.vals[key]))

            if opt.noact:
                return
        if any([opt.clear, opt.remove, opt.add, opt.tag,
               opt.justify, opt.idx, opt.fn2tag]):
            if opt.confirm:
                if self.hlpr.confirm():
                    mf.save()
                    spkr.say(3, 'Tag saved!')
            else:
                mf.save()
                spkr.say(3, 'Tag saved!')

    def chkfiles(self):
        err = 0
        for fname in self.fnames:
            if not os.path.exists(fname):
                spkr.say(0, '%s: no such file' % fname)
                err += 1
        if err:
            spkr.say(0, 'aborting...')

    def tag2fn(self, origfn, fname):
        if sep in opt.tag2fn or sep in fname:
            origfn = os.path.normpath(origfn)
            fname = os.path.normpath(fname)
            n = origfn.count(sep)
            m = opt.tag2fn.strip(sep).count(sep)
            pthlist = origfn.split(sep)
            pthname = os.path.join(sep.join(pthlist[:(n - m)]), fname)
        else:
            pthname = os.path.join(os.path.dirname(origfn), fname)
        spkr.say(1, ' <-- %s' % origfn)
        spkr.say(1, ' --> %s' % pthname)
        if not opt.noconfirm:
            if not self.hlpr.confirm():
                return

        try:
            os.renames(origfn, pthname)
            spkr.say(3, 'Renamed!')
        except Exception as e:
            spkr.say(2, e)
            raise Exception

    def index(self, say, mf):
        trn = mf.get('tracknumber', None)
        mf['idx0'] = str(self.fnum)
        indexed = 'filenumber'
        if trn:
            mf['idx1'] = trn
            indexed += ' & tracknumber'
        say(2, 'indexing by %s' % indexed)

    def remove(self, spkr, opt, mf):
        for action in opt.remove:
            key, val = (action.split('=', 1) + [''])[:2]
            li = []
            if key in mf:
                li = mf.pop(key) or []
            if not li:
                return mf
            if val and val in li:
                li.remove(val)
            elif val:
                spkr.say(1, '%s=%s not present' % (key, val))
                continue
            else:
                li = []
            mf.update({key: li})
            if mf.get(key):
                spkr.say(2, 'removing %s from %s' % (val, key))
            else:
                spkr.say(2, 'removing %s' % key)
            return mf

    def tag(self, spkr, opt, mf):
        for action in opt.tag or []:
            key, val = self.hlpr.splitarg(action)
            if val in (None, '', []):
                spkr.say(1, 'cannot set empty tag, use -r to remove',
                         error=True)
            if isinstance(val, list):
                mf[key] = val[0]
                spkr.say(2, 'setting tag value: %s=%s' % (key, val[0]))
                for val in val[1:]:
                    mf[key] += val
                    spkr.say(2, 'setting tag value: %s=%s' % (key, val))
            else:
                mf[key] = [val]
                spkr.say(2, 'setting tag value: %s=%s' % (key, val))
        return mf

    def add(self, spkr, opt, mf):
        for action in opt.add or []:
            (key, val) = self.hlpr.splitarg(action)
            if not key and val:
                return mf
            if mf.get(key, []):
                if isinstance(val, list):
                    mf[key] += val
                else:
                    mf[key] += [val]
            else:
                mf[key] = [val]
            spkr.say(2, 'adding tag value: %s=%s' % (key, val),
                     False,
                     opt.verbose)

            return mf

    def justify(self, opt, mf):
        try:
            self.vals.update({'tracknumber': mf['tracknumber']})
        except KeyError:
            self.vals['tracknumber'] = [self.fnum]
        width = len(str(len(self.fnames)))
        width = 2 if width == 1 else 2
        n = width - len(str(self.vals['tracknumber'][0]))
        self.vals['tracknumber'] = \
            ['0' * n + str(self.vals['tracknumber'][0])]
