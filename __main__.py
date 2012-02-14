#!/usr/bin/env python
"""
Copyright (c) 2012, Kevin Han
All rights reserved.

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

    Redistributions of source code must retain the above copyright notice, this
    list of conditions and the following disclaimer.

    Redistributions in binary form must reproduce the above copyright notice,
    this list of conditions and the following disclaimer in the documentation
    and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

import os
import re
import fnmatch
from datetime import datetime
import argparse

LICENSES = ('freebsd', 'bsdnew', 'bsdold', 'mit', 'apachev2', 'gplv3', 'wtfpl')

def printV(*s):
    if args.verbose > 0:
        print ' '.join(str(a) for a in s)

def fillTemplate(template, args, reEscaped=False):
    """
    Fill in template with values in args. Pass reEscaped=True if template is
    regex-escaped.
    """
    op = re.escape if reEscaped else lambda x: x
    for var in 'progName year owner organization'.split():
        val = vars(args)[var]
        template = (template
                .replace(op('<%s>' % var), val)
                .replace(op('<%s_upper>' % var), val.upper())
                )
    return template

def getComment(ext, header):
    """Adds appropriate comment wrappers around header, given file extension."""
    cmt = extToComment[ext]
    if len(cmt) == 1:
        return '\n'.join(cmt[0] + ' ' + line for line in header.strip().split('\n')) + '\n\n'
    else:
        return '%s\n%s%s\n\n' % (cmt[0], header, cmt[1])

def rmTemplate(code, ext, template):
    """Return code with the header template removed, or None if not found."""
    class _Generic:
        pass
    dummyArgs = _Generic()
    dummyArgs.progName = r'[^\n]+?'
    dummyArgs.year = r'[^\n]+?'
    dummyArgs.owner = r'[^\n]+?'
    dummyArgs.organization = r'[^\n]+?'
    cmtRegex = fillTemplate(
        re.escape(getComment(ext, template)),
        dummyArgs,
        reEscaped=True
        )
##    print 'REGEX', cmtRegex
##    print 'CODE', code
    newCode = re.sub(cmtRegex, '', code, count=1)
    if code == newCode:
        return None
    return newCode

def hasHeader(code):
    """
    Return True if code contains a copyright header. Must be more conservative
    (return more positives) than rmTemplate.
    """
    return any('copyright' in line.lower() for line in code.splitlines()[:40])

THIS_DIR = os.path.abspath(os.path.dirname(__file__))

# map file extension to comment style, 1-tuple for single line, 2-tuple for
# multi line
extToComment = dict(
        py=('"""', '"""'),
        jsp=('<%--', '--%>'),
        rb=('=begin', '=end'),
        vb=("'",),
        hs=('{-', '-}'),
        ada=('--',),
        lua=('--[[', '--]]',),
        erl=('%',),
        ml=('(*', '*)'),
        )
# Common comment styles
for ext in 'c h cpp hpp js java php cs sql hla as m d scala go'.split():
    extToComment[ext] = ('/*', '*/')
for ext in 'asm lisp scm lsp cloj'.split():
    extToComment[ext] = (';',)
for ext in 'pas pp lpr dpr p'.split():
    extToComment[ext] = ('{', '}')
for ext in 'pl sh tcl'.split():
    extToComment[ext] = ('#',)
for ext in 'f for f90 f95'.split():
    extToComment[ext] = ('!',)
for ext in 'forth 4th'.split():
    extToComment[ext] = ('\\',)

# map license name to (header template, license template)
nameToData = dict(
        (license, (
            open(os.path.join(THIS_DIR, 'headers', license)).read(),
            open(os.path.join(THIS_DIR, 'licenses', license)).read()
            ))
        for license in LICENSES
        )

class _ArgHolder:
    verbose = True
    includeFiles = ['*.' + ext for ext in extToComment]
    excludeFiles = ()
    excludeDirs = ()
    organization = ''
    year = str(datetime.now().year)
    includeHidden = False

    # This class namespace is a way to specify default values of arguments that
    # are only needed for the add subcommand, but since the execution is almost
    # the same for rm it's easier to fill everything in with dummy values.
    progName = ''
    owner = ''
    license = 'gplv3'

args = _ArgHolder

desc = '''
Add a software license to a source directory, and prepend the associated header
to all source files.

Remove added licenses using the "rm" subcommand.
'''

parser = argparse.ArgumentParser(description=desc.strip())
subparsers = parser.add_subparsers(
        title='commands',
        help='type "add -h" or "rm -h" for specific help',
        dest='cmd'
        )

addParser = subparsers.add_parser('add', help='add a license to a project')
rmParser = subparsers.add_parser('rm', help='remove a previously added license')

for p in (addParser, rmParser):
    # These are actually general arguments, but if you include them as such,
    # they won't show up in the help dialog of add or rm. :(
    p.add_argument(
            'srcDir',
            help='directory containing source files',
            metavar='src_dir'
            )

    p.add_argument(
            '-q',
            '--quiet',
            dest='verbose',
            action='store_false',
            help="don't print what it's doing"
            )
    p.add_argument(
            '-x',
            '--exclude-files',
            dest='excludeFiles',
            metavar='PATTERN',
            help='file wildcards to ignore, eg. -x *.c *.h',
            nargs='+'
            )
    p.add_argument(
            '-X',
            '--exclude-dirs',
            dest='excludeDirs',
            help='directories to ignore, eg. -X lib/ temp/',
            metavar='DIR',
            nargs='+'
            )
    p.add_argument(
            '-i',
            '--include-hidden',
            dest='includeHidden',
            help='include files and directories starting with ".", ignored by default',
            action='store_true'
            )

# positional args for add
addParser.add_argument('progName', help='program name', metavar='prog_name')
addParser.add_argument('owner', help='copyright owner')
addParser.add_argument(
        'license',
        choices=LICENSES,
        help='which license to use'
        )

# options for add
addParser.add_argument(
        '-o',
        '--organization',
        help='organization of the owner, required for bsdnew and bsdold'
        )
addParser.add_argument(
        '-y',
        '--year',
        help='copyright year; default: current year'
        )
addParser.add_argument(
        '-f',
        '--files',
        help='file wildcards to add headers to, eg. -f *.c *.h; recognizes most source file extensions by default, so this option is not usually needed',
        nargs='+',
        dest='includeFiles',
        metavar='PATTERN'
        )

parser.parse_args(namespace=args)

if not args.organization and args.license in ('bsdold', 'bsdnew'):
    parser.error('organization required for: bsdold, bsdnew')

args.excludeDirs = [os.path.abspath(d) for d in args.excludeDirs]
args.srcDir = os.path.abspath(args.srcDir)

header, license = (fillTemplate(s, args) for s in nameToData[args.license])

for curDir, dirs, files in os.walk(args.srcDir):
    printV('searching ' + curDir)

    if not args.includeHidden:
        for testDir in list(dirs):
            if testDir.startswith('.'):
                dirs.remove(testDir)
                printV('skipped ' + os.path.join(curDir, testDir))

    for xDir in args.excludeDirs:
        for testDir in dirs:
            absTest = os.path.join(curDir, testDir)
            if absTest == xDir:
                dirs.remove(testDir)
                printV('skipped ' + absTest)
                break

    for f in files:
        if not args.includeHidden and f.startswith('.'):
            continue

        absF = os.path.join(curDir, f)
        fText = open(absF).read()

        if any(fnmatch.fnmatch(f, wc) for wc in args.excludeFiles):
            printV('skipped ' + absF)
            continue

        for wc in args.includeFiles:
            if fnmatch.fnmatch(f, wc):
                ext = f.rsplit('.', 1)[-1]
                break
        else:
            continue

        if hasHeader(fText) and args.cmd == 'add':
            printV('header already found in ' + absF)
            continue

        for headerTempl, _ in nameToData.values():
            newCode = rmTemplate(fText, ext, headerTempl)
            if newCode is not None and args.cmd == 'rm':
                open(absF, 'w').write(newCode)
                printV('removed header from ' + absF)
                break
        else:
            if args.cmd == 'add':
                # preserve shebangs
                if fText.strip().startswith('#!'):
                    i = fText.find('\n', fText.find('#!') + 2) + 1
                else:
                    i = 0
                open(absF, 'w').write(fText[:i] + getComment(ext, header) + fText[i:])
                printV('added header to ' + absF)

for f in os.listdir(args.srcDir):
    if f.lower() in ('copying', 'license'):
        path = os.path.join(args.srcDir, f)
        if args.cmd == 'add':
            printV('license file already exists: ' + path)
        elif args.cmd == 'rm':
            os.unlink(path)
            printV('removed license file: ' + path)
        break
else:
    if args.cmd == 'add':
        path = os.path.join(args.srcDir, 'COPYING')
        open(path, 'w').write(license)
        printV('added license text to ' + path)
    elif args.cmd == 'rm':
        printV('no license file found in ' + args.srcDir)
