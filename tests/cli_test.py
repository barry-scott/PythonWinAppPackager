#!/usr/bin/env python
import sys

import pathlib

def main( argv ):
    print( 'CLI test program - home is %s' % (pathlib.Path.home(),) )
    return 0

if __name__ == '__main__':
    sys.exit( main( sys.argv ) )
