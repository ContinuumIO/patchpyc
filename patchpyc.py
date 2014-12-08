"""
Reference:
http://nedbatchelder.com/blog/200804/the_structure_of_pyc_files.html
"""

from __future__ import print_function

import sys
import marshal
import types


if sys.version_info[0:2] >= (3, 4):
    from importlib.util import MAGIC_NUMBER
else:
    import imp

    MAGIC_NUMBER = imp.get_magic()


def read_pyc(path):
    with open(path, 'rb') as fin:
        header = []
        # First four bytes of PYC is the magic number
        magic = fin.read(4)
        if magic != MAGIC_NUMBER:
            raise RuntimeError("Magic number in {file} does not match "
                               "interpreter's magic number".format(file=path))
        header.append(magic)
        # The next four bytes are the modification date
        moddate = fin.read(4)
        header.append(moddate)
        # In python 3.3+, the size of the source code is in the next 4 bytes
        if sys.version_info[0:2] >= (3, 3):
            srcsize = fin.read(4)
            header.append(srcsize)
        # The rest is a marshalled code object
        code = marshal.load(fin)

    return header, code


def write_pyc(path, header, code):
    with open(path, 'wb') as fout:
        # Write out all the headers
        for metadata in header:
            fout.write(metadata)
        # Dump the code object
        marshal.dump(code, fout)


def recode(oldcode, newfilename):
    constlist = []

    # More code object can live as constants.  Rewrite them also
    for const in oldcode.co_consts:
        if isinstance(const, types.CodeType):
            constlist.append(recode(const, newfilename))
        else:
            constlist.append(const)

    # Base python 2 argument list
    args = [oldcode.co_argcount,
            oldcode.co_nlocals,
            oldcode.co_stacksize,
            oldcode.co_flags,
            oldcode.co_code,
            tuple(constlist),
            oldcode.co_names,
            oldcode.co_varnames,
            newfilename,
            oldcode.co_name,
            oldcode.co_firstlineno,
            oldcode.co_lnotab,
            oldcode.co_freevars,
            oldcode.co_cellvars]

    # Add python 3 argument
    if sys.version_info[0] >= 3:
        args.insert(1, oldcode.co_kwonlyargcount)

    # Generate new code object
    code = types.CodeType(*args)
    return code


def patchpyc(oldpyc, newpyc, newpath):
    """Read `oldpyc` and replace all co_filename in its code object with
    `newpath` then write the output to `newpyc`.

    Args
    ----
    oldpyc : str
        Old PYC file path to be read.
    newpyc : str
        New PYC file path to be written. Can be the same as Initoldpyc.
    newpath
        New co_filename for the new PYC file.
    """
    header, code = read_pyc(oldpyc)
    code = recode(code, newpath)
    write_pyc(newpyc, header, code)


def main():
    try:
        oldpyc, newpyc, newpath = sys.argv[1:]
    except ValueError:
        print(("{prog} <oldpyc> <newpyc> <newpath>\n\n"
               "Rewrite all filename in code objects of the .pyc file"
              ).format(prog=sys.argv[0]))
        sys.exit(1)
    else:
        patchpyc(oldpyc, newpyc, newpath)


if __name__ == '__main__':
    main()
