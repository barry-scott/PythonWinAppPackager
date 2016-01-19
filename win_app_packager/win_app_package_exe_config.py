#!/usr/bin/python3
#
#   win_app_package_exe_config.py
#
import sys

import ctypes
import ctypes.wintypes

import struct
from namedstruct import namedstruct

# format of .ICO file on disk
struct_IconDirHeader = namedstruct( 'IconDirHeader', '<'
    'h:idReserved '
    'h:idType '
    'h:idCount'
    )
struct_IconDirEntry = namedstruct( 'IconDirEntry', '<'
    'b:bWidth '
    'b:bHeight '
    'b:bColorCount '
    'b:bReserved '
    'h:wPlanes '
    'h:wBitCount '
    'i:dwBytesInRes '
    'i:dwImageOffset'
    )

# Resource formats
struct_GrpIconDir = namedstruct( 'GrpIconDir', '<'
    'h:idReserved '
    'h:idType '
    'h:idCount'
    )
struct_GrpIconDirEntry = namedstruct( 'GrpIconDirEntry', '<'
    'b:bWidth '
    'b:bHeight '
    'b:bColorCount '
    'b:bReserved '
    'h:wPlanes '
    'h:wBitCount '
    'i:dwBytesInRes '
    'h:nID'
    )

# ctypes functions
BeginUpdateResource = ctypes.windll.kernel32.BeginUpdateResourceW
BeginUpdateResource.argtypes = (ctypes.wintypes.LPCWSTR
                               ,ctypes.wintypes.BOOL)
BeginUpdateResource.restype = ctypes.wintypes.HANDLE

UpdateResource = ctypes.windll.kernel32.UpdateResourceW
UpdateResource.argtypes = (ctypes.wintypes.HANDLE
                          ,ctypes.wintypes.ULARGE_INTEGER
                          ,ctypes.wintypes.ULARGE_INTEGER
                          ,ctypes.wintypes.WORD
                          ,ctypes.wintypes.LPVOID
                          ,ctypes.wintypes.DWORD)

EndUpdateResource = ctypes.windll.kernel32.EndUpdateResourceW
EndUpdateResource.argtypes = (ctypes.wintypes.HANDLE
                             ,ctypes.wintypes.BOOL)

RT_ICON =                   3
RT_GROUP_ICON =             14

RT_STRING =                 6        # STRINGTABLE

STRINGTABLE_BUNDLE_SIZE =   16

resource_ids = {
    'IDS_PYTHON_DLL':           64*STRINGTABLE_BUNDLE_SIZE + 0,
    'IDS_MAIN_PY_MODULE':       64*STRINGTABLE_BUNDLE_SIZE + 1,
    'IDS_INSTALL_FOLDER_KEY':   64*STRINGTABLE_BUNDLE_SIZE + 2,
    'IDS_INSTALL_FOLDER_VALUE': 64*STRINGTABLE_BUNDLE_SIZE + 3,

    'IDS_PY_VERBOSE':           65*STRINGTABLE_BUNDLE_SIZE + 0,
    }

# called when used standalone
def main( argv ):
    if argv[1:2] == ['bootstrap']:
        exe_filename = argv[2]

        python_dll = argv[3]
        main_py_module = agv[4]
        install_key  = argv[5]
        install_value  = argv[6]

        return configureAppExeBootStrap( exe_filename, python_dll, main_py_module, install_key, install_value )

    elif argv[1:2] == ['flags']:
        exe_filename = argv[2]

        py_verbose = argv[3]

        return configureAppExePyFlags( exe_filename, py_verbose )

    elif argv[1:2] == ['create']:
        return createResourceIdHeaderFile( argv[2] )

    elif argv[1:2] == ['icon']:
        return updateIconInExe( argv[3], argv[2] )

    else:
        print( 'Usage: %s bootstrap <exefile> <python_dll> <main_py_module> <install_key> <install_value>' % (argv[0],) )
        print( '       %s flags <exefile> <verbose>' % (argv[0],) )
        print( '       %s create <header-filename>' % (argv[0],) )
        return 1


# called when part of win_app_packager
def flagsCommand( argv ):
    if len(argv) != 4:
        return usage()

    exe_filename = argv[2]

    py_verbose = argv[3]

    return configureAppExePyFlags( exe_filename, py_verbose )

# called when part of win_app_packager
def usage():
################################################################################
    print(
'''python3 -m win_app_packager flags <exe-file> <verbose>'
  exe-file
    - the win_app_package create EXE file to modify
  verbose
    - either "0" or "1". The value to see the python verbose flag to.
''' )
    return 1

def createResourceIdHeaderFile( h_file ):
    with open( h_file, 'w' ) as f:
        for name in resource_ids:
           f.write( '#define %s %d\n' % (name, resource_ids[ name ]) )
    return 0

def configureAppExeBootStrap( exe_filename, python_dll, main_py_module, install_key, install_value ):
    all_strings = [
        python_dll,
        main_py_module,
        install_key,
        install_value,
        ]
    return updateStringBundleInExe( exe_filename, 'IDS_INSTALL_FOLDER_KEY', all_strings )

def configureAppExePyFlags( exe_filename, py_verbose ):
    all_strings = [
        py_verbose,
        ]
    return updateStringBundleInExe( exe_filename, 'IDS_PY_VERBOSE', all_strings )

def updateStringBundleInExe( exe_filename, stringtable_id_name, all_strings ):
    stringtable_id = resource_ids[ stringtable_id_name ]

    while len(all_strings) != STRINGTABLE_BUNDLE_SIZE:
        all_strings.append( '' )

    all_strtab_data = []
    for s in all_strings:
        count = struct.pack( '<H', len( s ) )
        all_strtab_data.append( count )
        if len(s) > 0:
            data = s.encode( 'utf-16' )[2:]
            all_strtab_data.append( data )

    strtab_data = b''.join( all_strtab_data )

    language = 0

    strtab_id = stringtable_id//STRINGTABLE_BUNDLE_SIZE + 1

    h = BeginUpdateResource( exe_filename, False )
    #print( h, ctypes.FormatError() )

    rc = UpdateResource( h, RT_STRING, strtab_id, language, strtab_data, len(strtab_data) )
    #print( rc, ctypes.FormatError() )

    rc = EndUpdateResource( h, False );
    #print( rc, ctypes.FormatError() )

    return 0

def updateIconInExe( exe_filename, icon_filename ):
    with open( icon_filename, 'rb' ) as f:
        all_entries = []
        all_images = []

        header = struct_IconDirHeader.unpack( f.read( len(struct_IconDirHeader) ) )

        for i in range( header.idCount ):
            all_entries.append(
                 struct_IconDirEntry.unpack(
                    f.read( len(struct_IconDirEntry) ) ) )

        for entry in all_entries:
            f.seek( entry.dwImageOffset, 0 )
            all_images.append( f.read( entry.dwBytesInRes ) )

    h = BeginUpdateResource( exe_filename, False )
    #print( h, ctypes.FormatError() )

    grp_header = struct_GrpIconDir.packer()
    grp_header.idReserved = 0
    grp_header.idType = header.idType
    grp_header.idCount = header.idCount

    all_data = [grp_header.pack()]
    entry_id = 1
    for entry in all_entries:
        grp_entry = struct_GrpIconDirEntry.packer()
        grp_entry.bWidth = entry.bWidth
        grp_entry.bHeight = entry.bHeight
        grp_entry.bColorCount = entry.bColorCount
        grp_entry.bReserved = entry.bReserved
        grp_entry.wPlanes = entry.wPlanes
        grp_entry.wBitCount = entry.wBitCount
        grp_entry.dwBytesInRes = entry.dwBytesInRes
        grp_entry.nID = entry_id
        all_data.append( grp_entry.pack() )
        entry_id += 1

    language = 0
    data = b''.join( all_data )
    rc = UpdateResource( h, RT_GROUP_ICON, 1, language, data, len(data) )
    #print( rc, ctypes.FormatError() )

    entry_id = 1
    for image in all_images:
        rc = UpdateResource( h, RT_ICON, entry_id, language, image, len(image) )
        #print( rc, ctypes.FormatError() )
        entry_id += 1

    rc = EndUpdateResource( h, False );
    #print( rc, ctypes.FormatError() )
    return 0

if __name__ == '__main__':
    sys.exit( main( sys.argv ) )
