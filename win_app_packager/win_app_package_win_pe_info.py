#!/usr/bin/python3
import namedstruct
import pathlib

dos_magic = b'MZ'
struct_dos_header = namedstruct.namedstruct( 'DOS header', '<'
    '2s:dos_magic '
    'h:lastsize '
    'h:nblocks '
    'h:nreloc '
    'h:hdrsize '
    'h:minalloc '
    'h:maxalloc '
    'H:ss '
    'H:sp '
    'h:checksum '
    'H:ip '
    'H:cs '
    'h:relocpos '
    'h:noverlay '
    '4H:reserved1 '
    'h:oem_id '
    'h:oem_info '
    '10H:reserved2 '
    'L:pe_offset'
    )

pe_magic = b'PE\x00\x00'
struct_pe_header = namedstruct.namedstruct( 'PE Header', '<'
    '4s:pe_magic'
    )

struct_coff_header = namedstruct.namedstruct( 'COFF Header', '<'
    'H:Machine '
    'h:NumberOfSections '
    'l:TimeDateStamp '
    'l:PointerToSymbolTable '
    'l:NumberOfSymbols '
    'h:SizeOfOptionalHeader '
    'h:Characteristics '
    )

struct_pe_opt_signature = namedstruct.namedstruct( 'PE signature', '<'
    'H:signature '
    )
pe32_signature = 0x10b
pe64_signature = 0x20b

struct_pe32_opt_header = namedstruct.namedstruct( 'PE 32 Opt Header', '<'
    'H:signature '
    'B:MajorLinkerVersion '
    'B:MinorLinkerVersion '
    'L:SizeOfCode '
    'L:SizeOfInitializedData '
    'L:SizeOfUninitializedData '
    'L:AddressOfEntryPoint '
    'L:BaseOfCode '
    'L:BaseOfData '
    'L:ImageBase '
    'L:SectionAlignment '
    'L:FileAlignment '
    'H:MajorOSVersion '
    'H:MinorOSVersion '
    'H:MajorImageVersion '
    'H:MinorImageVersion '
    'H:MajorSubsystemVersion '
    'H:MinorSubsystemVersion '
    'L:Reserved '
    'L:SizeOfImage '
    'L:SizeOfHeaders '
    'L:Checksum '
    'H:Subsystem '
    'H:DLLCharacteristics '
    'L:SizeOfStackReserve '
    'L:SizeOfStackCommit '
    'L:SizeOfHeapReserve '
    'L:SizeOfHeapCommit '
    'L:LoaderFlags '
    'L:NumberOfRvaAndSizes'
    #data_directory DataDirectory[16];
    )

struct_pe64_opt_header = namedstruct.namedstruct( 'PE 64 Opt Header', '<'
    'H:signature '
    'B:MajorLinkerVersion '
    'B:MinorLinkerVersion '
    'L:SizeOfCode '
    'L:SizeOfInitializedData '
    'L:SizeOfUninitializedData '
    'L:AddressOfEntryPoint '
    'L:BaseOfCode '
    'Q:ImageBase '
    'L:SectionAlignment '
    'L:FileAlignment '
    'H:MajorOSVersion '
    'H:MinorOSVersion '
    'H:MajorImageVersion '
    'H:MinorImageVersion '
    'H:MajorSubsystemVersion '
    'H:MinorSubsystemVersion '
    'L:Reserved '
    'L:SizeOfImage '
    'L:SizeOfHeaders '
    'L:Checksum '
    'H:Subsystem '
    'H:DLLCharacteristics '
    'Q:SizeOfStackReserve '
    'Q:SizeOfStackCommit '
    'Q:SizeOfHeapReserve '
    'Q:SizeOfHeapCommit '
    'L:LoaderFlags '
    'L:NumberOfRvaAndSizes'
    #data_directory DataDirectory[16];
    )

IMAGE_DIRECTORY_ENTRY_IMPORT = 1
struct_pe_data_dir = namedstruct.namedstruct( 'PE Data directory', '<'
    'L:VirtualAddress '
    'L:Size'
    )

struct_coff_section = namedstruct.namedstruct( 'COFF Section', '<'
    '8s:Name '
    'L:VirtualSize '
    'L:VirtualAddress '
    'L:SizeOfRawData '
    'L:PointerToRawData '
    'L:PointerToRelocations '
    'L:PointerToLinenumbers '
    'H:NumberOfRelocations '
    'H:NumberOfLinenumbers '
    'L:Characteristics '
    )

struct_import_dirent = namedstruct.namedstruct( 'Import directory entry', '<'
    'L:ImportLookupTable '
    'L:TimeDateStamp '
    'L:ForwarderChain '
    'L:NameRVA '
    'L:ImportAddressTable'
    )


def getPeImportDlls( log, filename ):
    with filename.open( 'rb' ) as f:
        pe_image = f.read()

    dos_header = struct_dos_header.unpack( pe_image[0:len(struct_dos_header)] )
    log.debug( 'dos_header.dos_magic %r .pe_offset %r' % (dos_header.dos_magic, dos_header.pe_offset) )
    if dos_header.dos_magic != dos_magic:
        log.error( 'Not a PE image, bad dos magic %r in %s' % (dos_header.dos_magic, filename) )
        dos_header.dump( log.error )
        return set()

    pe_start = dos_header.pe_offset

    pe_header= struct_pe_header.unpack( pe_image[pe_start:pe_start+len(struct_pe_header)] )
    log.debug( 'pe_header.pe_magic %r' % (pe_header.pe_magic,) )
    if pe_header.pe_magic != pe_magic:
        log.error( 'Not a PE image, bad PE magic %r in %s' % (pe_header.pe_magic, filename) )
        log.error( 'DOS header' )
        dos_header.dump( log.error )
        log.error( 'PE header' )
        pe_header.dump( log.error )
        return set()

    coff_start = pe_start + len(struct_pe_header)

    coff_header = struct_coff_header.unpack( pe_image[coff_start:coff_start+len(struct_coff_header)] )
    log.debug( 'COFF header @ 0x%8.8x' % (coff_start,) )
    coff_header.dump( log.debug )

    pe_opt_start = coff_start + len(struct_coff_header)

    pe_opt_signature = struct_pe_opt_signature.unpack( pe_image[pe_opt_start:pe_opt_start+len(struct_pe_opt_signature)] )
    if pe_opt_signature.signature ==  pe32_signature:
        struct_pe_opt_header = struct_pe32_opt_header

    elif pe_opt_signature.signature == pe64_signature:
        struct_pe_opt_header = struct_pe64_opt_header

    else:
        log.error( 'Unknown PE optional header signature of 0x4.4x' % (pe_opt_signature.signature,) )
        return set()

    pe_opt_header = struct_pe_opt_header.unpack( pe_image[pe_opt_start:pe_opt_start+len(struct_pe_opt_header)] )

    log.debug( 'PE Opt header @ 0x%8.8x' % (pe_opt_start,) )
    pe_opt_header.dump( log.debug )

    # Decode the Data Directories
    data_dir_0_start = pe_opt_start + len(struct_pe_opt_header)

    all_data_dir = []

    for index in range( pe_opt_header.NumberOfRvaAndSizes ):
        data_dir_start = data_dir_0_start + len(struct_pe_data_dir)*index

        pe_data_dir= struct_pe_data_dir.unpack( pe_image[data_dir_start:data_dir_start+len(struct_pe_data_dir)] )

        log.debug( 'Data Dir %d @ 0x%8.8x' % (index, data_dir_start) )
        pe_data_dir.dump( log.debug )

        all_data_dir.append( pe_data_dir )

    # Decode the COFF Sections
    section_0_start = data_dir_0_start + pe_opt_header.NumberOfRvaAndSizes * len(struct_pe_data_dir)

    all_coff_sections = []
    for index in range( coff_header.NumberOfSections ):
        section_start = section_0_start + index * len(struct_coff_section)
        coff_section = struct_coff_section.unpack( pe_image[section_start:section_start+len(struct_coff_section)] )

        log.debug( 'Section %d @ 0x%8.8x' % (index, section_start) )
        coff_section.dump( log.debug )

        all_coff_sections.append( coff_section )

    # convert a RVA to the offset in the disk image
    def rvaToDisk( addr ):
        for section in all_coff_sections:
            if section.VirtualAddress <= addr < (section.VirtualAddress + section.VirtualSize):
                offset = addr - section.VirtualAddress
                return section.PointerToRawData + offset

        raise ValueError( 'RVA 0x%8.8x is not within any COFF section in file %s' % (addr, filename) )

    end = section_0_start + coff_header.NumberOfSections * len(struct_coff_section)

    log.debug( 'Decode @ 0x%8.8x' % (end,) )

    import_data_dir = all_data_dir[ IMAGE_DIRECTORY_ENTRY_IMPORT ]
    log.debug( 'import_data_dir %r' % (import_data_dir,) )
    import_data_dir.dump( log.debug )

    if import_data_dir.Size == 0:
        log.debug( 'Empty import list' )
        return set()

    start_import_data_dir = rvaToDisk( import_data_dir.VirtualAddress )

    log.debug( 'import data 0x%8.8x' % (start_import_data_dir,) )

    def unpackString( addr ):
        start = addr
        for i in range( 256 ):
            if pe_image[start+i] == 0:
                break

        return pe_image[start:start+i]

    all_dlls = set()

    while True:
        import_dirent = struct_import_dirent.unpack( pe_image[start_import_data_dir:start_import_data_dir+len(struct_import_dirent)] )
        log.debug( 'Import dirent @ 0x%8.8x' % (start_import_data_dir,) )
        import_dirent.dump( log.debug )
        if import_dirent.ImportLookupTable == 0:
            break

        start_name = rvaToDisk( import_dirent.NameRVA )
        name = unpackString( start_name )
        log.debug( 'Name @ 0x%8.8x %r' % (start_name, name) )

        all_dlls.add( pathlib.Path( name.decode('ASCII' ) ) )

        start_import_data_dir += len(struct_import_dirent)

    log.debug( 'OK for %s' % (filename,) )

    return all_dlls

if __name__ == '__main__':
    class log:
        def info( self, m ):
            print( 'Info: %s' % (m,) )

        def debug( self, m ):
            print( 'Debug: %s' % (m,) )

        def verbose( self, m ):
            print( 'Verbose: %s' % (m,) )

        def error( self, m ):
            print( 'Error: %s' % (m,) )

    print( getPeImportDlls( log(), pathlib.Path( r'C:\python36.win64\python3.dll' ) ) )
