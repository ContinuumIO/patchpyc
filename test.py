from __future__ import print_function
import sys
import os
import py_compile
import subprocess

import patchpyc


# Prepare
os.mkdir("isolate")
py_compile.compile("udt.py", "isolate/udt.pyc")
pwd = os.path.abspath(os.curdir)
print('pwd =', pwd)
os.chdir("isolate")
print('cd', os.path.abspath(os.curdir))

# Test

print("Before".center(80, '='))
subprocess.call("{python} -c 'import udt;udt.foo()'".format(
    python=sys.executable), shell=True)

print("Patch".center(80, '='))
patchpyc.patchpyc("udt.pyc", "udt.pyc",
                  "/somewhere/that/is/new/udt.py")

print("After".center(80, '='))
subprocess.call("{python} -c 'import udt;udt.foo()'".format(
    python=sys.executable), shell=True)


# Cleanup
os.chdir(pwd)
os.unlink("isolate/udt.pyc")
os.rmdir("isolate")
