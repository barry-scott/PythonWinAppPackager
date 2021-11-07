#!/usr/bin/env python
import sys
import pathlib
import datetime
import tzlocal
import tzdata
import zoneinfo

def main( argv ):
    if sys.maxsize > (2**31):
        size_int_t = 64
    else:
        size_int_t = 32

    py_ver = '%d.%d-%d' % (sys.version_info.major, sys.version_info.minor, size_int_t)

    print( 'Info: CLI pytz test program - home is %s' % (pathlib.Path.home(),) )
    print( 'Info: CLI pytz test program - Python %s' % (py_ver,) )

    local_timezone_name = tzlocal.get_localzone_name()
    print( 'Info: CLI pytz timezone name %r' % (local_timezone_name,) )

    local_timezone = zoneinfo.ZoneInfo( local_timezone_name )

    print( 'Info: CLI pytz timezone %r' % (local_timezone,) )

    return 0

if __name__ == '__main__':
    sys.exit( main( sys.argv ) )
