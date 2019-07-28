#!/usr/bin/env python
import sys

import pathlib

def main( argv ):
    py_ver = '%d.%d' % (sys.version_info.major, sys.version_info.minor)

    print( 'Info: CLI test program - home is %s' % (pathlib.Path.home(),) )
    print( 'Info: CLI test program - Python %s' % (py_ver,) )
    return 0

if __name__ == '__main__':
    sys.exit( main( sys.argv ) )
