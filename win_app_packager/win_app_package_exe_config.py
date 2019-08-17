#!/usr/bin/python3
#
#   win_app_package_exe_config.py
#
import sys

import ctypes
import ctypes.wintypes

import struct
from namedstruct import namedstruct

is_64bit = (ctypes.sizeof( ctypes.c_voidp ) * 8) == 64

# DumpRange used for debug
struct_DumpRange = namedstruct( 'DumpRange', '<'
    '8h:row1 '
    '8h:row2 '
    '8h:row3 '
    '8h:row4 '
    )

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

# VS_VERSIONINFO
struct_VersionInfoHeader = namedstruct( 'VersionInfo', '<'
    'h:wLength '    # sizeof( struct_VersionInfoHeader ) + sizeof( struct_VersionInfoFixedFileInfo )
    'h:wValueLength '
    'h:wType '
    '16h:szKey '    # room for "VS_VERSION_INFO\0" in utf-16
    'h:Padding1 '
    )

# VS_FIXEDFILEINFO
struct_VersionInfoFixedFileInfo = namedstruct( 'VersionInfoFixedFileInfo', '<'
    'I:dwSignature '        # magic value 0xFEEF04BD
    'h:dwStrucVersion1 '     # ???
    'h:dwStrucVersion0 '     # ???
    'h:dwFileVersion1 '
    'h:dwFileVersion0 '
    'h:dwFileVersion3 '
    'h:dwFileVersion2 '
    'h:dwProductVersion1 '
    'h:dwProductVersion0 '
    'h:dwProductVersion3 '
    'h:dwProductVersion2 '
    'i:dwFileFlagsMask '
    'i:dwFileFlags '
    'i:dwFileOS '
    'i:dwFileType '
    'i:dwFileSubtype '
    'i:dwFileDateMS '
    'i:dwFileDateLS '
    )
# dwSignature value
VER_SIGNATURE_MAGIC = 0xFEEF04BD
# dwFileOS value
VOS_NT_WINDOWS32    = 0x00040004
# dwFileType
VFT_APP             = 0x00000001
# dwFileSubtype
VFT2_UNKNOWN        = 0x00000000

# Child of VS_VERSION_INFO Header
struct_ChildOfVersionInfoHeader = namedstruct( 'ChildOfVersionInfoHeader', '<'
    'h:wLength '
    'h:wValueLength '
    'h:wType '
    )

# StringFileInfo
struct_StringFileInfo = namedstruct( 'StringFileInfo', '<'
    'h:wLength '
    'h:wValueLength '
    'h:wType '
    '15h:szKey '      # "StringFileInfo".
    )

# VarFileInfo
struct_VarFileInfo = namedstruct( 'VarFileInfo', '<'
    'h:wLength '
    'h:wValueLength '
    'h:wType '
    '12h:szKey '      # "VarFileInfo".
    'h:padding'
    )

struct_Var = namedstruct( 'Var', '<'
    'h:wLength '
    'h:wValueLength '
    'h:wType '
    '11h:szKey '      # "Translation".
    'h:Padding '
    # list of VarValue
    )

struct_VarValue = namedstruct( 'VarValue', '<'
    'I:value '
    )

# StringTable
struct_StringTable = namedstruct( 'StringTable', '<'
    'h:wLength '
    'h:wValueLength '
    'h:wType '
    '15h:szKey '
    'h:Padding '
    # n of String
    )

# String
struct_StringHeader = namedstruct( 'StringHeader', '<'
    'h:wLength '
    'h:wValueLength '
    'h:wType '
    # 0 terminated wchar string
    # pad to 32 bit
    # 0 terminated wchar string
    )


# ctypes functions
BeginUpdateResource = ctypes.windll.kernel32.BeginUpdateResourceW
BeginUpdateResource.argtypes = (ctypes.wintypes.LPCWSTR
                               ,ctypes.wintypes.BOOL)
BeginUpdateResource.restype = ctypes.wintypes.HANDLE

UpdateResource = ctypes.windll.kernel32.UpdateResourceW
if is_64bit:
    UpdateResource.argtypes = (ctypes.wintypes.HANDLE
                              ,ctypes.wintypes.ULARGE_INTEGER
                              ,ctypes.wintypes.ULARGE_INTEGER
                              ,ctypes.wintypes.WORD
                              ,ctypes.wintypes.LPVOID
                              ,ctypes.wintypes.DWORD)
else:
    UpdateResource.argtypes = (ctypes.wintypes.HANDLE
                              ,ctypes.wintypes.DWORD
                              ,ctypes.wintypes.DWORD
                              ,ctypes.wintypes.WORD
                              ,ctypes.wintypes.LPVOID
                              ,ctypes.wintypes.DWORD)

EndUpdateResource = ctypes.windll.kernel32.EndUpdateResourceW
EndUpdateResource.argtypes = (ctypes.wintypes.HANDLE
                             ,ctypes.wintypes.BOOL)

LoadLibraryEx = ctypes.windll.kernel32.LoadLibraryExW
LoadLibraryEx.argtypes =    (ctypes.wintypes.LPCWSTR
                            ,ctypes.wintypes.HANDLE
                            ,ctypes.wintypes.DWORD)
LoadLibraryEx.restype =     ctypes.wintypes.HANDLE

LOAD_LIBRARY_AS_DATAFILE_EXCLUSIVE = 0x00000040

FreeLibrary = ctypes.windll.kernel32.FreeLibrary
FreeLibrary.argtypes = (ctypes.wintypes.HANDLE,)

FindResource = ctypes.windll.kernel32.FindResourceW
FindResource.argtypes =     (ctypes.wintypes.HANDLE
                            ,ctypes.wintypes.ULARGE_INTEGER
                            ,ctypes.wintypes.ULARGE_INTEGER)
FindResource.restype =      ctypes.wintypes.HANDLE

LoadResource = ctypes.windll.kernel32.LoadResource
LoadResource.argtypes =     (ctypes.wintypes.HANDLE
                            ,ctypes.wintypes.HANDLE)
LoadResource.restype =      ctypes.wintypes.HANDLE

SizeofResource = ctypes.windll.kernel32.SizeofResource
SizeofResource.argtypes =   (ctypes.wintypes.HANDLE
                            ,ctypes.wintypes.HANDLE)
SizeofResource.restype =    ctypes.wintypes.DWORD

LockResource = ctypes.windll.kernel32.LockResource
LockResource.argtypes =     (ctypes.wintypes.HANDLE,)
LockResource.restype =      ctypes.c_void_p

RT_ICON =                   3
RT_GROUP_ICON =             14
RT_VERSION =                16
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

    elif argv[1:2] == ['show-version-info']:
        return showVersionInfoInExe( argv[2] )

    elif argv[1:2] == ['set-version-info']:
        return setVersionInfoInExe( argv[2], argv[3:] )

    else:
        print( 'Usage: %s bootstrap <exefile> <python_dll> <main_py_module> <install_key> <install_value>' % (argv[0],) )
        print( '       %s flags <exefile> <verbose>' % (argv[0],) )
        print( '       %s create <header-filename>' % (argv[0],) )
        print( '       %s show-version-info <exefile>' % (argv[0],) )
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

def dprint( msg ):
    #print( '|', msg )
    pass

def showVersionInfoInExe( exe_filename ):
    vir = VersionInfoResource( exe_filename )

    print( '     dwStrucVersion: %d.%d' % (vir.fixed.dwStrucVersion0, vir.fixed.dwStrucVersion1) )
    print( '        FileVersion: %d.%d.%d.%d' % (vir.fixed.dwFileVersion0, vir.fixed.dwFileVersion1, vir.fixed.dwFileVersion2, vir.fixed.dwFileVersion3) )
    print( '     ProductVersion: %d.%d.%d.%d' % (vir.fixed.dwProductVersion0, vir.fixed.dwProductVersion1, vir.fixed.dwProductVersion2, vir.fixed.dwProductVersion3) )

    print( '           encoding: %s' % (vir.encoding,) )
    for key in sorted( vir.all_properties ):
        print( ' %18s: "%s"' % (key, vir.all_properties[ key ]) )

    print( '  translation value: 0x%8.8x' % (vir.translation.value,) )

def setVersionInfoInExe( exe_filename, argv ):
    vir = VersionInfoResource( exe_filename )

    args = iter(argv)

    for name in args:
        value = next(args)

        if name.lower() == 'version':
            vir.setVersion( value )

        else:
            vir.setProperty( name, value )

    vir.updateWithChanges()

class VersionInfoResource:
    def __init__( self, exe_filename ):
        self.exe_filename = exe_filename
        self.__loadVersionInfo()

        self.pack_header = struct_VersionInfoHeader.packer( self.header )
        self.pack_fixed = struct_VersionInfoFixedFileInfo.packer( self.fixed )
        self.pack_child = struct_ChildOfVersionInfoHeader.packer( self.child )
        self.pack_string_file_info = struct_StringFileInfo.packer( self.string_file_info )

    def setProperty( self, name, value ):
        self.all_properties[ name ] = value

    def setVersion( self, str_version ):
        int_version = tuple( int(n) for n in str_version.split('.') )
        assert len(int_version) == 4, 'bad version %r' % (str_version,)

        self.all_properties[ 'ProductVersion' ] = str_version
        self.pack_fixed.dwProductVersion0 = int_version[0]
        self.pack_fixed.dwProductVersion1 = int_version[1]
        self.pack_fixed.dwProductVersion2 = int_version[2]
        self.pack_fixed.dwProductVersion3 = int_version[3]

        self.all_properties[ 'FileVersion' ] = str_version
        self.pack_fixed.dwFileVersion0 = int_version[0]
        self.pack_fixed.dwFileVersion1 = int_version[1]
        self.pack_fixed.dwFileVersion2 = int_version[2]
        self.pack_fixed.dwFileVersion3 = int_version[3]

    def updateWithChanges( self ):
        version_resource = self.__encodeVersionInfo()
        self.__decodeVersionInfo( version_resource )

        h = BeginUpdateResource( self.exe_filename, False )
        dprint( 'BeginUpdateResource() -> 0x%x - %s' % (h, ctypes.FormatError()) )

        language = 0
        version_id = 1
        rc = UpdateResource( h, RT_VERSION, version_id, language, version_resource, len(version_resource) )
        dprint( 'UpdateResource() -> 0x%x - %s' % (rc, ctypes.FormatError()) )

        rc = EndUpdateResource( h, False );
        dprint( 'EndUpdateResource() => 0x%x' % (rc,) )

        return 0

    def __encodeVersionInfo( self ):
        # pack in reverse order so that sizes are available

        # the tail is copied as is

        # string properties block
        all_string_properties = []

        for name, value in self.all_properties.items():
            sz_name = packSzChar( name )
            if value == '':
                sz_value = b''

            else:
                sz_value = packSzChar( value )

            offset = len(struct_StringHeader) + len(sz_name)

            dprint( 'zzz name %r value %r offset %d' % (name, value, offset) )

            if offset%4 != 0:
                offset += 2
                sz_name += b'\0\0'

            offset += len(sz_value)

            string_header = struct_StringHeader.packer()
            string_header.wLength = offset # qaq
            string_header.wValueLength = len(sz_value)//2
            string_header.wType = 1

            dprint( 'zzz name %r value %r size %d' % (name, value, offset) )

            if offset%4 != 0:
                offset += 2
                sz_value += b'\0\0'

            buf_property = string_header.pack() + sz_name + sz_value
            all_string_properties.append( buf_property )

        buf_all_string_properties = b''.join( all_string_properties )

        # Prefix with an encoding stringheader
        buf_sz_encoding = packSzChar( self.encoding )
        encoding_header = struct_StringHeader.packer()
        encoding_header.wLength = len(encoding_header) + len(buf_all_string_properties) + len(buf_sz_encoding)
        encoding_header.wValueLength = 0
        encoding_header.wType = 1

        buf_properties = encoding_header.pack() + buf_sz_encoding + buf_all_string_properties

        self.pack_string_file_info.wLength = len(self.pack_string_file_info) + len(buf_properties)
        buf_string_properties = self.pack_string_file_info.pack() + buf_properties

        buf_fixed = self.pack_fixed.pack()

        buf_version_info = buf_fixed + buf_string_properties + self.packed_tail

        # VersionInfoHeader
        header = struct_VersionInfoHeader.packer( self.header )
        header.wLength = len(header) + len(buf_version_info)
        buf_header = header.pack()

        version_resource = buf_header + buf_version_info
        return version_resource

    def __loadVersionInfo( self ):
        hmodule = LoadLibraryEx( self.exe_filename, None, LOAD_LIBRARY_AS_DATAFILE_EXCLUSIVE )
        dprint( 'hmodule 0x%x' % (hmodule,) )

        hrsrc = FindResource( hmodule, 1, RT_VERSION )
        dprint( '  hrsrc 0x%x' % (hrsrc,) )

        hglobal = LoadResource( hmodule, hrsrc )
        dprint( 'hglobal 0x%x' % (hglobal,) )

        self.res_size = SizeofResource( hmodule, hrsrc )
        dprint( 'res_size %d' % (self.res_size,) )

        data_p = LockResource( hglobal )
        dprint( ' data_p 0x%x' % (data_p,) )

        buf = ctypes.create_string_buffer( self.res_size )
        ctypes.memmove( buf, data_p, self.res_size )
        data = buf.raw

        # Free handle
        rc = FreeLibrary( hmodule )
        assert rc, 'RC 0x%x' % (rc,)

        self.__decodeVersionInfo( data )

    def __decodeVersionInfo( self, data ):
        dprint( 'VersionInfoResource.__decodeVersionInfo()' )
        hexDump( data, dprint )

        offset = 0
        size = len(struct_VersionInfoHeader)
        assert offset%4 == 0
        self.header = struct_VersionInfoHeader.unpack( data[offset:offset+size] )
        self.header.dump( dprint, 'at offset 0x%x' % (offset,) )

        offset += size
        size = len(struct_VersionInfoFixedFileInfo)
        assert offset%4 == 0
        self.fixed = struct_VersionInfoFixedFileInfo.unpack( data[offset:offset+size] )
        self.fixed.dump( dprint, 'at offset 0x%x' % (offset,) )

        assert offset%4 == 0

        offset += size
        size = len(struct_ChildOfVersionInfoHeader)
        assert offset%4 == 0
        self.child = struct_ChildOfVersionInfoHeader.unpack( data[offset:offset+size] )
        self.child.dump( dprint, 'at offset 0x%x' % (offset,) )

        self.all_properties = {}

        if self.child.wType == 1:
            size = len(struct_StringFileInfo)
            assert offset%4 == 0
            self.string_file_info = struct_StringFileInfo.unpack( data[offset:offset+size] )
            self.string_file_info.dump( dprint, 'at offset 0x%x' % (offset,) )
            dprint( 'szKey %d "%s"' % extractSzChar( data, offset+6 ) )

            end = offset + self.string_file_info.wLength

            offset += size
            assert offset%4 == 0

            size = len(struct_StringHeader)
            assert offset%4 == 0
            string_encoding_header = struct_StringHeader.unpack( data[offset:offset+size] )
            dprint( 'qqq' )
            string_encoding_header.dump( dprint, 'at offset 0x%x' % (offset,) )

            offset += size
            offset, self.encoding = extractSzChar( data, offset )

            while offset < end:
                if offset%4 != 0:
                    offset += 2

                size = len(struct_StringHeader)
                assert offset%4 == 0
                string_header = struct_StringHeader.unpack( data[offset:offset+size] )
                string_header.dump( dprint, 'at offset 0x%x' % (offset,) )

                offset += size
                offset, key = extractSzChar( data, offset )
                if offset%4 != 0:
                    offset += 2

                if string_header.wValueLength == 0:
                    # There is not a string to extract
                    value = ''

                else:
                    offset, value = extractSzChar( data, offset )

                self.all_properties[ key ] = value
                dprint( 'key %d:%r value %d:%r' % (len(key), key, len(value), value) )

            dprint( 'At end: end=%d offset=%d' % (end, offset) )

            if offset%4 != 0:
                offset += 2

            if offset < len(data):
                size = len(struct_ChildOfVersionInfoHeader)
                assert offset%4 == 0
                child = struct_ChildOfVersionInfoHeader.unpack( data[offset:offset+size] )
                child.dump( dprint, 'at offset 0x%x' % (offset,) )

        # the tail bytes stay as is when updating the version resource
        self.packed_tail = data[offset:]

        if( offset < len(data)
        and child.wType == 1 ):
            size = len(struct_VarFileInfo)
            assert offset%4 == 0
            var_file_info = struct_VarFileInfo.unpack( data[offset:offset+size] )
            var_file_info.dump( dprint, 'at offset 0x%x' % (offset,) )

            end = offset + var_file_info.wLength

            offset += size
            assert offset%4 == 0

            while offset < end:
                if offset%4 != 0:
                    offset += 2

                size = len(struct_Var)
                assert offset%4 == 0
                var = struct_Var.unpack( data[offset:offset+size] )
                var.dump( dprint, 'at offset 0x%x' % (offset,) )

                var_end = offset + var.wLength
                offset += size
                if offset % 4 != 0:
                    offset += 2

                while offset < var_end:
                    size = len(struct_VarValue)
                    self.translation = struct_VarValue.unpack( data[offset:offset+size] )
                    self.translation.dump( dprint, 'at offset 0x%x' % (offset,) )
                    offset += size

def hexDump( buffer, write ):
    all_parts = []
    all_chars = []
    for index, byte in enumerate( buffer ):
        if index%16 == 0:
            all_parts.append( '%8.8x' % (index,) )
        all_parts.append( '%2.2x' % (byte, ) )
        if ord(' ') <= byte < 0x7f:
            all_chars.append( chr(byte) )
        else:
            all_chars.append( '.' )

        if index%16 == 15:
            all_parts.reverse()
            all_parts.append( ' %s' % (''.join( all_chars),) )
            write( ' '.join( all_parts ) )
            all_parts = []
            all_chars = []

    if index%16 != 15:
        while index%16 != 15:
            all_parts.append( '  ' )
            index += 1

        all_parts.reverse()
        all_parts.append( ' %s' % (''.join( all_chars),) )
        write( ' '.join( all_parts ) )

def extractSzChar( data, offset ):
    all_chars = []
    while True:
        low = data[offset]
        hi = data[offset+1]
        wchar = (hi<<8) + low
        offset += 2
        if wchar == 0:
            break
        all_chars.append( chr(wchar) )

    return offset, ''.join( all_chars )

def packSzChar( chars ):
    all_bytes = []
    for ch in chars:
        ch = ord(ch)
        lo = ch & 0xff
        hi = (ch>>8) & 0xff

        all_bytes.append( lo )
        all_bytes.append( hi )

    all_bytes.append( 0 )
    all_bytes.append( 0 )

    return bytes( all_bytes )

def updateVersionInfoInExe( exe_filename, version, description ):
    h = BeginUpdateResource( exe_filename, False )
    language = 0

    rc = UpdateResource( h, RT_VERSION, 1, language, data, len(data) )
    print( rc, ctypes.FormatError() )

    rc = EndUpdateResource( h, False );
    print( rc, ctypes.FormatError() )
    return 0

if __name__ == '__main__':
    sys.exit( main( sys.argv ) )
