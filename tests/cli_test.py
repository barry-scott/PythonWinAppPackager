#!/usr/bin/env python
import sys

import pathlib

def main( argv ):
    if sys.maxsize > (2**31):
        size_int_t = 64
    else:
        size_int_t = 32

    py_ver = '%d.%d-%d' % (sys.version_info.major, sys.version_info.minor, size_int_t)

    print( 'Info: CLI test program - home is %s' % (pathlib.Path.home(),) )
    print( 'Info: CLI test program - Python %s' % (py_ver,) )
    return 0

if __name__ == '__main__':
    sys.exit( main( sys.argv ) )
