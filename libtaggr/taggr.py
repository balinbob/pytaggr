# vim: ts=4 sw=4 et:

from __future__ import absolute_import
import re
from os.path import sep

from libtaggr import __version__


class Subster():
    '''
        s = Subster(pattern, mode)
        or
        s = Subster('%a/%l/%n - %t.flac', mode='fn2tag')
    '''
    keydict = {'a': 'artist',
               'l': 'album',
               'n': 'tracknumber',
               't': 'title',
               'd': 'date',
               'g': 'genre',
               'c': 'composer',
               'j': 'junk',
               'i': 'discnumber',
               'v': 'venue'}

    keystr = ''.join(list(keydict.keys()))
    keypat = '%[' + keystr + ']'
#    print (keypat)
    keypat = re.compile(keypat)
    fname = ''

    def __init__(self, pattern='', mode='fn2tag'):
        self.pattern = pattern or ''
        if mode == 'tag2fn':
            self.tag2fn = pattern or ''
        elif mode == 'fn2tag':
            self.fn2tag = pattern or ''
        self.mode = mode

        self.keys = [mp[1] for mp in re.findall(self.keypat, self.pattern)]
        self.lits = re.split(self.keypat, self.pattern)
        self.keyiter = iter(self.keys)
        self.literals = iter(self.lits)

    def pathstrip(self, ptn, pth):
        n = len(ptn.strip(sep).split(sep))
        pthlist = pth.strip(sep).split(sep)[-n:]
        return sep.join(pthlist)

    def _get_regex(self, reg, lit):
        if reg == 'n':
            return '[0-9]+?'+lit
        return '.+?'+lit

    def init(self):
        literal = next(self.literals)
        self.fname = self.fname[len(literal):]

    def nextpair(self):
        try:
            key = next(self.keyiter)
            keyname = self.keydict[key]
        except StopIteration:
            raise StopIteration
        try:
            lit = next(self.literals)
        except StopIteration:
            lit = ''
        except ValueError:
            # in case the first part of the pattern is a lit
            lit = lit.strip()
            return {keyname: [lit]}
        matchpat = self._get_regex(key, lit)
        mo = re.match(matchpat, self.fname)
        if mo:
            val = mo.group()[:-len(lit)]
            self.fname = self.fname[len(lit+val):]
            return {keyname: [val]}
        lit = lit.strip()
        return {keyname: [lit]}

    def getdict(self, fname):
        gdict = {}
        fname.replace(str(sep + sep), sep)
        self.fname = self.pathstrip(self.pattern, fname)
        self.init()
        while True:
            try:
                gdict.update(self.nextpair())
            except ValueError:
                pass
            except StopIteration:
                break
        return gdict

    def getfnlist(self):
        fnlist = []
        self.keyiter = iter(self.keys)
        self.literals = iter(self.lits)
        while True:
            try:
                fnlist.append(next(self.literals))
                fnlist.append(self.keydict[next(self.keyiter)].lower())
            except StopIteration:
                break
        return fnlist
