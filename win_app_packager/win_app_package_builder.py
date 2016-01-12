#/usr/bin/python3
#
#   win_app_package_builder.py
#
import sys
import os
import pathlib
import uuid
import ctypes
import ctypes.wintypes

import win_app_packager.win_app_package_win_pe_info
import win_app_packager.win_app_package_exe_config

class AppPackageError(Exception):
    pass

class AppPackage:
    APP_TYPE_CLI = 1
    APP_TYPE_GUI = 2

    resource_folder = pathlib.Path( 'PyWinAppRes' )
    library_folder = resource_folder / 'lib'

    def __init__( self, argv ):
        self.argv = argv

        # options
        self.enable_debug = False
        self.enable_verbose = False
        self.enable_merge = False

        self.enable_bootstrap_debug = False

        self.app_type = self.APP_TYPE_CLI
        self.app_name = None
        self.app_install_key = ''
        self.app_install_value = ''

        self.main_program = None
        self.package_folder = None

        # package contents
        self.__all_library_files = set()
        self.__all_dlls = set()

        # how to find app packager resources
        self.win_app_packager_folder = pathlib.Path( sys.argv[0] ).parent

    def debug( self, msg ):
        if self.enable_debug:
            print( 'Debug: %s' % (msg,) )

    def info( self, msg ):
        print( 'Info: %s' % (msg,) )

    def verbose( self, msg ):
        if self.enable_verbose:
            print( 'Info: %s' % (msg,) )

    def error( self, msg ):
        print( 'Error: %s' % (msg,) )

    def usage( self ):
        print( 'app-packager.py <main-script> [<options>...]' )
        return 1

    def parseArgs( self ):
        print( self.argv )
        all_positional_args = []
        index = 1
        while index < len( self.argv ):
            arg = self.argv[index]
            if arg.startswith( '--' ):
                if arg == '--debug':
                    self.enable_debug = True

                elif arg == '--bootstrap-debug':
                    self.enable_bootstrap_debug = True

                elif arg == '--verbose':
                    self.enable_verbose = True

                elif arg in ('--console', '--cli'):
                    self.app_type = self.APP_TYPE_CLI

                elif arg == '--gui':
                    self.app_type = self.APP_TYPE_GUI

                elif arg == '--name' and (index+1) < len( self.argv ):
                    self.app_name = self.argv[index+1]
                    index += 1

                elif arg == '--install-key' and (index+1) < len( self.argv ):
                    self.app_install_key = sys.argv[index+1]
                    index += 1

                elif arg == '--install-value' and (index+1) < len( self.argv ):
                    self.app_install_value = sys.argv[index+1]
                    index += 1

                elif arg == '--merge':
                    self.enable_merge = True

                else:
                    raise AppPackageError( 'Unknown option %r' % (arg,) )

            else:
                all_positional_args.append( arg )

            index += 1

        print( all_positional_args )

        if( len( all_positional_args ) < 1
        or all_positional_args[0] != 'build' ):
            raise AppPackageError( 'Expecting command name "build"' )

        self.main_program = all_positional_args[1]
        if self.main_program.endswith( '.py' ):
            self.main_program = self.main_program[:-len('.py')]

        self.package_folder = pathlib.Path( all_positional_args[2] )

        if self.app_name is None:
            self.app_name = self.main_program

        if self.app_install_key != '' and self.app_install_value == '':
            raise AppPackageError( 'require --install-value with --install-key' )

    def build( self, all_module_names ):
        try:
            self.info( 'App Packager' )
            self.parseArgs()

            if self.app_type == self.APP_TYPE_CLI:
                self.info( 'Building CLI App %s into package folder %s' % (self.app_name, self.package_folder) )

            elif self.app_type == self.APP_TYPE_GUI:
                self.info( 'Building GUI App %s into package folder %s' % (self.app_name, self.package_folder) )

            else:
                raise AppPackageError( 'Unknown app_type %r' % (self.app_type,) )

            self.debug( 'All module names: %r' % (all_module_names,) )

            # find the python DLL
            self.addWinPeFileDependenciesToPackage( pathlib.Path( sys.executable ) )

            for name in sorted( all_module_names ):
                self.processModule( name )

            if not self.enable_merge:
                self.cleanAppPackage()

            self.createAppPackage()

            self.info( 'Completed sucessfully' )

            return 0

        except AppPackageError as e:
            self.error( str(e) )

    def processModule( self, name ):
        self.verbose( 'Checking module %s' % (name,) )
        module = sys.modules[ name ]
        if not hasattr( module, '__file__' ):
            self.verbose( '%s is builtin - ignoring' % (name,) )
            return

        if name == '__main__':
            self.verbose( '%s is app-packager module - ignoring' % (name,) )
            return

        filename = pathlib.Path( module.__file__ )
        self.debug( 'module type %s filename %s' % (filename.suffix, filename) )

        # is this file part of the python installation?
        for path in [sys.prefix]+sys.path:
            try:
                path = pathlib.Path( path ).resolve()

            except FileNotFoundError:
                continue

            try:
                library_filename_suffix = filename.relative_to( path )

            except ValueError:
                continue

            if filename.match( '*.py' ):
                self.addPyFileToPackage( filename, library_filename_suffix )

            elif( filename.match( '*.pyd' )
            or    filename.match( '*.dll' ) ):
                self.addWinPeFileToPackage( filename, library_filename_suffix )

            else:
                raise AppPackageError( 'No handler for files of type %s' % (ext,) )

            return

        raise AppPackageError( 'Dropped file %s' % (filename,) )

    def addPyFileToPackage( self, filename, library_filename_suffix ):
        self.verbose( 'Adding source file %s from %s' % (library_filename_suffix, filename) )
        self.__all_library_files.add( PackageFile( filename, library_filename_suffix ) )

    def addWinPeFileToPackage( self, filename, library_filename_suffix ):
        pf = PackageFile( filename, library_filename_suffix )
        if pf not in self.__all_dlls:
            self.verbose( 'Adding DLL %s from %s' % (library_filename_suffix, filename) )
            self.__all_dlls.add( pf )

            self.addWinPeFileDependenciesToPackage( filename )

    def addWinPeFileDependenciesToPackage( self, filename ):
        all_dlls = win_app_packager.win_app_package_win_pe_info.getPeImportDlls( self, filename )
        self.verbose( 'Dependancies of DLL %s:' % (filename,) )
        for dll in sorted( all_dlls ):
            self.verbose( '   %s' % (dll,) )

        all_dll_to_be_scanned = []

        for dll in sorted( all_dlls ):
            dll_path = self.findDll( dll, filename.parent )
            if self.isStandardDll( dll_path ):
                self.verbose( 'No need to package standard DLL %s' % (dll_path,) )
                continue

            all_dll_to_be_scanned.append( (dll_path, self.findLibraryLocationForDll( dll_path )) )

        for dll_path, library_filename_suffix in all_dll_to_be_scanned:
            self.addWinPeFileToPackage( dll_path, library_filename_suffix )

    def findLibraryLocationForDll( self, dll_path ):
        for path in [sys.prefix]+sys.path:
            try:
                path = pathlib.Path( path ).resolve()

            except FileNotFoundError:
                continue

            try:
                return dll_path.relative_to( path )

            except ValueError:
                continue

        raise AppPackageError( 'Dropped DLL %s' % (dll_path,) )


    def findDll( self, dll_name, prefered_location ):
        # look for the DLL in an ordered set of locations
        # starting with the 'prefered_location'
        # and then working along the 'PATH'

        for folder in [prefered_location,'']+os.environ['PATH'].split( os.pathsep ):
            try:
                folder = pathlib.Path( folder ).resolve()

            except FileNotFoundError:
                continue

            dll_path = folder / dll_name
            if dll_path.exists():
                return dll_path

        return dll_name

    def isStandardDll( self, dll ):
        dll = pathlib.Path( dll )

        if dll.match( 'api-ms-win-*.dll' ):
            return True

        if dll.parent == windowsGetSystemDirectory():
            return True

        return False

    def cleanAppPackage( self ):
        #
        # Clean up the package_folder, but only if
        # the special PyWinAppLib folder is within it.
        #
        # This is to defend against removing files
        # unintended locations like c:\windows
        #
        if not self.package_folder.exists():
            return

        if not self.package_folder.is_dir():
            raise AppPackageError( '%s is not a directory' )

        all_filenames = list( self.package_folder.iterdir() )
        if len(all_filenames) == 0:
            return

        if (self.package_folder / self.resource_folder) not in all_filenames:
            raise AppPackageError( '%s is not an existing packager folder - refusing to clean up' % (self.package_folder,) )

        self.info( 'Cleaning up %s' % (self.package_folder,) )
        for dirpath, all_dirnames, all_filenames in os.walk( str( self.package_folder ), topdown=False ):
            for filename in all_filenames:
                (pathlib.Path( dirpath ) / filename).unlink()

            for dirname in all_dirnames:
                (pathlib.Path( dirpath ) / dirname).rmdir()

    def createAppPackage( self ):
        #
        #   create the following structure on disk
        #
        #   <package-folder>\<main-program>.exe
        #   <package-folder>\PyWinAppLib\<library-file>
        #

        self.info( 'Creating App Package in %s' % (self.package_folder,) )

        path_library_folder = pathlib.Path( self.package_folder ) / self.library_folder
        path_resource_folder = pathlib.Path( self.package_folder ) / self.resource_folder

        # copy the programs python source code
        for lib_file in sorted( self.__all_library_files ):
            self.verbose( 'Copying Library file: %s' % (lib_file.source_file,) )
            lib_file.copy( path_resource_folder )

        # copy the programs DLL dependencies
        for dll_file in sorted( self.__all_dlls ):
            self.verbose( 'Copying DLL: %s' % (dll_file.source_file,) )
            dll_file.copy( path_resource_folder )

            if self.enable_bootstrap_debug:
                # include PDB file need to support debugging
                dll_file.copyPdb( path_resource_folder )

        # copy the right boot strap
        if self.app_type == self.APP_TYPE_CLI:
            bootstrap_filename = self.win_app_packager_folder / 'BootStrap' / 'obj' / 'bootstrap-cli.exe'

        elif self.app_type == self.APP_TYPE_GUI:
            bootstrap_filename = self.win_app_packager_folder / 'BootStrap' / 'obj' / 'bootstrap-gui.exe'

        bootstrap_exe = pathlib.Path( '%s.exe' % (self.app_name,) )
        p = PackageFile( bootstrap_filename, bootstrap_exe )
        p.copy( self.package_folder )

        if self.enable_bootstrap_debug:
            # include PDB file need to support debugging
            p.copyPdb( self.package_folder )

            #
            # create the Microsoft Visual Studio 14.0 solution file
            # need to run the boot strap  code under the debugger
            #
            sln_vars = {
                'UUID1':                uuid.uuid4(),
                'UUID2':                uuid.uuid4(),
                'name':                 self.app_name,
                'exefile':              bootstrap_exe,
                'Executable':           self.package_folder.resolve() / bootstrap_exe,
                'StartingDirectory':    self.package_folder.resolve(),
                }
            sln_file = (self.package_folder / bootstrap_exe ).with_suffix( '.sln' )
            sln_file.write_text( self.vc_14_solution_file_template % sln_vars )

        win_app_packager.win_app_package_exe_config.configureAppExeBootStrap( 
            str( self.package_folder / bootstrap_exe ),
            'python%d%d.dll' % (sys.version_info.major, sys.version_info.minor),
            self.main_program,
            self.app_install_key, 
            self.app_install_value, 
            )

    vc_14_solution_file_template = '''Microsoft Visual Studio Solution File, Format Version 12.00
# Visual Studio 14
VisualStudioVersion = 14.0.23107.0
MinimumVisualStudioVersion = 10.0.40219.1
Project("{%(UUID1)s}") = "%(name)s", "%(exefile)s", "{%(UUID2)s}"
	ProjectSection(DebuggerProjectSystem) = preProject
		PortSupplier = 00000000-0000-0000-0000-000000000000
		Executable = %(Executable)s
		RemoteMachine = BLACKSTAR
		StartingDirectory = %(StartingDirectory)s
		Environment = Default
		LaunchingEngine = 00000000-0000-0000-0000-000000000000
		UseLegacyDebugEngines = No
		LaunchSQLEngine = No
		AttachLaunchAction = No
	EndProjectSection
EndProject
Global
	GlobalSection(SolutionConfigurationPlatforms) = preSolution
		Release|x64 = Release|x64
	EndGlobalSection
	GlobalSection(ProjectConfigurationPlatforms) = postSolution
		{%(UUID2)s}.Release|x64.ActiveCfg = Release|x64
	EndGlobalSection
	GlobalSection(SolutionProperties) = preSolution
		HideSolutionNode = FALSE
	EndGlobalSection
EndGlobal
'''

class PackageFile:
    def __init__( self, source_file, package_file ):
        self.source_file = source_file
        self.package_file = package_file

    def copy( self, to_folder ):
        dest_file = to_folder / self.package_file
        dest_file.parent.mkdir( parents=True, exist_ok=True )

        self.__copy( self.source_file, dest_file )

    def copyPdb( self, to_folder ):
        # if there is a .pdb file copy it
        source_pdb = self.source_file.with_suffix( '.pdb' )
        if not source_pdb.exists():
            return

        dest_pdb = (to_folder / self.package_file).with_suffix( '.pdb' )

        self.__copy( source_pdb, dest_pdb )

    def __copy( self, src, dst ):
        #print( '__copy( %s, %s )' % (src, dst) )

        with src.open( 'rb' ) as f_in, dst.open( 'wb' ) as f_out:
            while True:
                buf = f_in.read( 128 * 1024 )
                if len(buf) == 0:
                    break

                f_out.write( buf )

    def __repr__( self ):
        return '<PackageFile src=%s, pkg=%s>' % (self.source_file, self.package_file)

    # make sortable
    def __eq__( self, other ):
        if isinstance( other, PackageFile ):
            return self.source_file == other.source_file

        return self.source_file == other

    def __lt__( self, other ):
        if isinstance( other, PackageFile ):
            return self.source_file < other.source_file

        return self.source_file < other

    # make containable
    def __hash__( self ):
        return hash( self.source_file )

def windowsGetSystemDirectory():
    GetSystemDirectory = ctypes.windll.kernel32.GetSystemDirectoryW
    GetSystemDirectory.argtypes = (ctypes.wintypes.LPWSTR
                                  ,ctypes.wintypes.DWORD)

    GetSystemDirectory.restype = ctypes.wintypes.UINT

    size = 1024
    folder = ctypes.create_unicode_buffer( size )

    rc = GetSystemDirectory( folder, size )
    assert rc > 0

    return pathlib.Path( folder.value )
