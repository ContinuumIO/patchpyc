from __future__ import print_function
import sys


def foo():
    class A:
        def bar(self):
            print(sys.version)
            print(sys.executable)
            print(self.bar)
            raise NotImplementedError("hahaha")

    A().bar()


if __name__ == '__main__':
    foo()
