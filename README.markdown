**Choosing a software license sucks, and figuring out how to apply it correctly is
a pain. Here's the solution.**

This is a simple Python script to automatically license a project under one of
many popular open source licenses. Simply provide the source directory, the
project name and owner, and the license name, and it adds the license text into
a COPYING file and prepends the right copyright headers to all source files,
correctly escaped with relevant comment syntax for the language.

It also comes with options for further configurability, such as excluding
filetypes or specific directories.

Example usage:

        python licenser/ add my_project/ "Project Name" "Owner Name" freebsd

To exclude directories (note: it ignores all files/directories starting with "."
by default):

        python licenser/ add my_project/ "Project Name" "Owner Name" freebsd -X my_project/temp/ my_project/Lib

To remove headers/licenses added with this tool:

        python licenser/ rm my_project/

Requires the argparse module, which is included by default in Python 2.7 and
3.2+. Older versions can install it separately - see [here](http://code.google.com/p/argparse/).

---

Side note: don't know which license to choose? Neither did I, until I read this
[excellent blog post by Jeff Atwood](http://www.codinghorror.com/blog/2007/04/pick-a-license-any-license.html).

If you just want attribution but no other restrictions (as I suspect most people
do), the BSD or MIT licenses seem to be the way to go.
