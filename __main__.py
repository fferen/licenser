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
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.'
"""

import os
import fnmatch
import urllib2
from datetime import datetime
import argparse

LICENSES = ('freebsd', 'bsdnew', 'bsdold', 'mit', 'apachev2', 'gplv3', 'wtfpl')

def printV(*s):
    if args.verbose > 0:
        print ' '.join(str(a) for a in s)

def fillTemplate(template):
    """Fill in template with values in args."""
    # hah this almost looks like lisp code
    return (template
            .replace('<PROG_NAME>', args.progName)
            .replace('<YEAR>', args.year)
            .replace('<OWNER>', args.owner)
            .replace('<ORGANIZATION>', args.organization))

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

desc = '''
Add a software license to a source directory, and prepend the associated header
to all source files.
'''

parser = argparse.ArgumentParser(description=desc.strip())

# positional args
parser.add_argument(
        'srcDir',
        help='directory containing source files',
        metavar='src_dir'
        )
parser.add_argument('progName', help='program name', metavar='prog_name')
parser.add_argument('owner', help='copyright owner')
parser.add_argument(
        'license',
        choices=LICENSES,
        help='which license to use'
        )

# optional args
parser.add_argument(
        '-q',
        '--quiet',
        dest='verbose',
        action='store_false',
        default='true',
        help="don't print what it's doing"
        )
parser.add_argument(
        '-o',
        '--organization',
        help='organization of the owner, required for bsdnew and bsdold',
        default=''
        )
parser.add_argument(
        '-y',
        '--year',
        help='copyright year; default: current year',
        default=str(datetime.now().year)
        )
parser.add_argument(
        '-f',
        '--files',
        help='file wildcards to add headers to, eg. -f *.c *.h; recognizes most source file extensions by default, so this option is not usually needed',
        nargs='*',
        dest='includeFiles',
        metavar='PATTERN',
        default=['*.' + ext for ext in extToComment]
        )
parser.add_argument(
        '-x',
        '--exclude-files',
        dest='excludeFiles',
        metavar='PATTERN',
        help='file wildcards to skip adding headers to, eg. -x *.c *.h',
        nargs='*',
        default=()
        )
parser.add_argument(
        '-X',
        '--exclude-dirs',
        dest='excludeDirs',
        help='directories to ignore, eg. -X lib/ temp/',
        metavar='DIR',
        nargs='*',
        default=()
        )

args = parser.parse_args()

if not args.organization and args.license in ('bsdold', 'bsdnew'):
    parser.error('organization required for: bsdold, bsdnew')

args.excludeDirs = [os.path.abspath(d) for d in args.excludeDirs]
args.srcDir = os.path.abspath(args.srcDir)

header, license = (fillTemplate(s) for s in nameToData[args.license])

for curDir, dirs, files in os.walk(args.srcDir):
    if curDir in args.excludeDirs:
        continue

    printV('searching ' + curDir)
    for f in files:
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

        if any(fillTemplate(header) in fText \
                for header, license in nameToData.values()):
            printV('header already found in ' + absF)
            continue

        cmt = extToComment[ext]
        if len(cmt) == 1:
            # single line comment syntax
            open(absF, 'w').write('\n'.join(cmt[0] + ' ' + line for line in header.split('\n')) + '\n' + fText)
        else:
            open(absF, 'w').write('%s\n%s%s\n\n' % (cmt[0], header, cmt[1]) + fText)
        printV('added header to ' + absF)

for f in ('COPYING', 'LICENSE'):
    if f in [s.upper() for s in os.listdir(args.srcDir)]:
        printV('license file already detected: ' + os.path.join(args.srcDir, f))
        break
else:
    open(os.path.join(args.srcDir, 'COPYING'), 'w').write(license)
    printV('added license text to ' + os.path.join(args.srcDir, 'COPYING'))
