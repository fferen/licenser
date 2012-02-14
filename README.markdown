**Choosing a software license sucks, and figuring out how to apply it correctly is
a pain. Here's the solution.**

This is a simple Python script to automatically license a project under one of
many popular open source licenses. Simply provide the source directory, the
project name and owner, and the license name, and it adds the license text into
a COPYING file and prepends the right copyright headers to all source files,
correctly escaped with relevant comment syntax.

It also comes with options for further configurability, such as excluding
filetypes or specific directories.

Example usage:

        python licenser/ add my_project/ "Project Name" "Owner Name" freebsd

To remove headers/licenses added with this tool:

        python licenser/ rm my_project/

Features:

*   Supported source file extensions: .4th .ada .as .asm .c .cloj .cpp .cs .d .dpr .erl .f .f90 .f95 .for .forth .go .h .hla .hpp .hs .java .js .jsp .lisp .lpr .lsp .lua .m .ml .p .pas .php .pl .pp .py .rb .scala .scm .sh .sql .tcl .vb
*   Supported licenses: FreeBSD, BSD Old, BSD New, MIT, GPLv3, Apache v2, [WTFPL](http://sam.zoy.org/wtfpl/)
*   Will not override existing licenses or headers.
*   Detects shebang and appends header after it.
*   Exclude specific files or directories with the -x or -X options, respectively.

Requires the argparse module, which is included by default in Python 2.7 and
3.2+. Older versions can install it separately - see [here](http://code.google.com/p/argparse/).

---

Side note: don't know which license to choose? Neither did I, until I read this
[excellent blog post by Jeff Atwood](http://www.codinghorror.com/blog/2007/04/pick-a-license-any-license.html).

If you just want attribution but no other restrictions (as I suspect most people
do), the BSD or MIT licenses seem to be the way to go.
