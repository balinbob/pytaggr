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
import os
from os.path import sep
from optparse import OptionParser
from mutagen import File
from mutagen.mp3 import EasyMP3 as MP3
from mutagen.mp3 import HeaderNotFoundError
from libtaggr.taggr import Subster
from libtaggr import __version__

'''
class Confirmer():
    def __init__(self, optt):
        self.opt = optt
        if any([self.opt.tag, self.opt.add, self.opt.remove, self.opt.clear,
                self.opt.fn2tag, self.opt.tag2fn]):
            self.use = True
        else:
            self.use = False
        self._all = False

    def confirm(self):
        if self.use:
            if self.opt.noact:
                return False
            if self._all:
                return True
            if not self.opt.confirm:
                return True
            resp = input('confirm changes? [y]/n/a ')
            if resp == '':
                resp = 'y'
            if resp[0].lower() == 'y':
                return True
            if resp[0].lower() == 'a':
                self._all = True
                return True
        return False
'''


class Speaker():
    ''' wrapper to simplify printing user messages '''
    def __init__(self, quiet, verbose):
        self.x = 0
        self.quiet = quiet
        self.verbose = verbose

    def speak(self, strng):
        ''' print formatted messages '''
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

    def say(self, tabs, strng, error=False, verbose=False):
        tab = '\t' * tabs
        if error:
            print('%s%s' % (tab, strng))
            sys.exit(1)
        self.quiet = self.quiet and not verbose
        if not self.quiet:
            print('%s%s' % (tab, strng))


class Helpers():
    def __init__(self, opt, fnames=[]):
        self.opt = opt
        self.fnames = fnames
        self.spkr = Speaker(opt.quiet, opt.verbose)

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

    def confirm(self):
        ''' honor certain options regarding actual file-writing,
            and input of y or n to proceed with file-writing.
        '''

        if any([self.opt.tag, self.opt.add, self.opt.remove, self.opt.clear,
                self.opt.fn2tag, self.opt.tag2fn]):
            _use = True
        else:
            _use = False
        _all = False

        if _use:
            if self.opt.noact:
                return False
            if _all:
                return True
            if not self.opt.confirm:
                return True
            resp = input('confirm changes? [y]/n/a ')
            if resp == '':
                resp = 'y'
            if resp[0].lower() == 'y':
                return True
            if resp[0].lower() == 'a':
                _all = True
                return True
        return False

    def subs(self, mf):
        opt = self.opt
        '''
            func = str, fn2tag or tag2fn
            fname = str
            vals = dict - full existing tag
            opt = instantiation of class OP
        '''
        spkr = Speaker(opt.quiet, opt.verbose)
        if opt.fn2tag:
            pat = opt.fn2tag
            subster = Subster(pat, 'fn2tag')
            d = subster.getdict(mf.filename)
            for k in d:
                li = d.get(k, [])
                mf[k] = li

                spkr.say(2, 'from filename: %s=%s' % (k, li[0]))
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


def main():
    arglist = sys.argv
    if 'id3help' in arglist:
        from mutagen.easyid3 import EasyID3
        for key in EasyID3.valid_keys.keys():
            print(key,)
    sys.path.append('.')
    parser = OParser(arglist)
    tagger(parser, arglist)


def tagger(parser, args):
    err = 0
    argstr = ' '.join(args)

    if len(args) < 2:
        parser.print_usage()
        print('-h|--help for help')
        sys.exit()

    p = '(-t|--tag|-a|--add|-p|--pattern|-r|--remove|-f|--files) +?-[^ ]*'
    mo = re.search(p, argstr)
    if mo:
        print('illegal option combination: ', mo.group())
        sys.exit(1)

    (opt, fnames) = parser.parse_args()
    h = Helpers(opt, fnames)
    if opt.pattern:
        opt.fn2tag = opt.pattern
    if opt.vers:
        print('%s %s' % (parser.get_prog_name(), __version__))
    if opt.filenames:
        fnames += opt.filenames

    for fname in fnames:
        if not os.path.exists(fname):
            print('%s: no such file' % fname)
            err += 1
    if err:
        sys.exit(err)

    fnum = 0
#    idx = 0
    modded = any([opt.clear, opt.remove, opt.add, opt.tag, opt.fn2tag,
                  opt.tag2fn, opt.justify, opt.idx])
    spkr = Speaker(opt.quiet, opt.verbose)
    top_length = 0

    for fname in fnames:
        bfname = os.path.basename(fname)
        top_length = len(bfname) if len(bfname) > top_length else top_length

    for fname in fnames:
        fnum += 1
        vals = {}
#        keys = []
        origfn = fname
        k = None

        mf = h.mf_open(fname)
        print(os.path.basename(fname))

        if opt.clear:
            mf.clear()
            spkr.say(1, 'all tags cleared')

        if opt.idx:
            trn = mf.get('tracknumber', None)
            mf['idx'] = str(fnum)
            if trn:
                mf['idx'] += trn
            mf.save()
            print(' indexed')

        for action in opt.remove or []:
            k, v = (action.split('=', 1)+[''])[:2]
            if k in mf:
                li = mf.pop(k) or []
                if v and v in li:
                    li.remove(v)
                elif v:
                    spkr.say(2, '%s=%s not present' % (k, v))
                    continue
                else:
                    li = []
                mf.update({k: li})
                if mf.get(k, None):
                    spkr.say(2, 'removed %s from %s' % (v, k))
                else:
                    spkr.say(2, 'removed %s' % k)

        for action in opt.tag or []:
            k, v = h.splitarg(action)
            if v in [None, '', []]:
                spkr.say(2, 'cannot set empty tag, use -r to remove',
                         error=True)
            if isinstance(v, list):
                mf[k] = v[0]
                spkr.say(2, 'tag set: %s=%s' % (k, v[0]))
                for val in v[1:]:
                    mf[k] += val
                    spkr.say(2, 'tag value added: %s=%s' % (k, val))
            else:
                mf[k] = [v]
                spkr.say(2, 'tag set: %s=%s' % (k, v))

        for action in opt.add or []:
            (k, v) = h.splitarg(action)
            if not k and v:
                return
            if mf.get(k, []):
                if isinstance(v, list):
                    mf[k] += v
                else:
                    mf[k] += [v]
            else:
                mf[k] = [v]
            spkr.say(2, 'tag value added: %s=%s' % (k, v), False, opt.verbose)

        if opt.fn2tag:
            mf = h.subs(mf)
        if opt.tag2fn:
            fname = h.subs(mf)

        if opt.justify:
            try:
                vals.update({'tracknumber': mf['tracknumber']})
            except KeyError:
                vals['tracknumber'] = [fnum]
            width = len(str(len(fnames)))
            if width == 1:
                width = 2
            n = width - len(str(vals['tracknumber'][0]))
            vals['tracknumber'] = ['0' * n + str(vals['tracknumber'][0])]

        if not any([modded, opt.quiet]):
            print(mf.pprint())
            continue

        if opt.noact or opt.confirm:
            for k in vals:
                print(k+'='+str(vals[k]))
        if opt.noact:
            continue
        if opt.confirm and not h.confirm():
            continue
        if opt.tag2fn:
            if opt.map:
                a, b = opt.map.split()
                fname = re.sub(a, b, fname)
                print('opt.map seems to be set')
        try:
            mf.save()
        except Exception as e:
            spkr.say(2, e)
            raise IOError

        if opt.tag2fn:
            if sep in opt.tag2fn or sep in fname:
                origfn = os.path.normpath(origfn)
                fname = os.path.normpath(fname)
                n = origfn.count(sep)
                m = opt.tag2fn.strip(sep).count(sep)
                pthlist = origfn.split(sep)
                pthname = os.path.join(sep.join(pthlist[:n-m]), fname)
            else:
                pthname = os.path.join(os.path.dirname(origfn), fname)
            spkr.say(1, ' <-- %s' % origfn)
            spkr.say(1, ' --> %s' % pthname)
            if not opt.noconfirm:
                opt.confirm = True
                if not h.confirm():
                    continue
            try:
                os.renames(origfn, pthname)
            except Exception as e:
                spkr.say(2, e)
                raise Exception
