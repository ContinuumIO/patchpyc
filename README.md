patchpyc
========

A python script that patches PYC files with new co_filename.

Test
====

Since it is very simple with just one functionality, the test is minimal:

```bash
python test.py
```

And manually verify that the path is set.  Then repeat for every Python version because PYC format may be different.

