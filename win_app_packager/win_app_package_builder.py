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
import modulefinder
import importlib

from . import win_app_package_win_pe_info
from . import win_app_package_exe_config

class AppPackageError(Exception):
    pass

class AppPackage:
    APP_TYPE_CLI = 1
    APP_TYPE_GUI = 2

    resource_folder = pathlib.Path( 'PyWinAppRes' )
    library_folder = resource_folder / 'lib'

    all_modules_allowed_to_be_missing = set( [
        '_dummy_threading',
        '_frozen_importlib',
        '_frozen_importlib_external',
        '_posixsubprocess',
        '_scproxy',
        '_winreg',
        'ce',
        'grp',
        'java.lang',
        'org.python.core',
        'os.path',
        'posix',
        'pwd',
        'readline',
        'termios',
        'vms_lib',
        ] )

    all_imported_modules_to_exclude = set( [
        'ctypes',
        'ctypes._endian',
        'ctypes.util',
        'ctypes.wintypes',
        'importlib',
        'importlib._bootstrap',
        'importlib._bootstrap_external',
        'importlib.abc',
        'importlib.machinery',
        'importlib.util',
        'modulefinder',
        'pathlib',
        'uuid',
        'win_app_packager',
        'win_app_packager.win_app_package_builder',
        'win_app_packager.win_app_package_exe_config',
        'win_app_packager.win_app_package_win_pe_info',
        ] )

    def __init__( self ):
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

    def warning( self, msg ):
        print( 'Warn: %s' % (msg,) )

    def usage( self ):
################################################################################
        print(
'''python3 -m win_app_packager build <main-script> <package-folder> [<options>...]
  main-script
    - python main module
  package-folder
    - folder to create package into

  Where <options> are:
    --console
    --cli
        build a windows console progam (the default).
    --gui
        build a windows gui program.
    --name
        name the program (defaults to the <main-script> name).
    --install-key <key>  --install-value <value>
        The install path of the package can be read
        from the windows registry from key HKLM:<key> value <value>
        otherwise the install path is assumed to be the same folder
        that the .EXE files is in.
    --merge
        Do not clean out the <package-folder> before building the package.
        Useful for putting multiple programs into one package.
    --verbose
        Output extra information about the build process.
    --debug
        Developer option. Output lots of details about the build process.
    --bootstrap-debug
        Developer option. Copy PDF files and setup a Microsoft Visual 
        Studio solution (.sln) file suitable for running the bootstrap
        under the debugger.
'''
)
        return 1

    def parseArgs( self, argv ):
        all_positional_args = []
        index = 1
        while index < len( argv ):
            arg = argv[index]
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

                elif arg == '--name' and (index+1) < len( argv ):
                    self.app_name = argv[index+1]
                    index += 1

                elif arg == '--install-key' and (index+1) < len( argv ):
                    self.app_install_key = sys.argv[index+1]
                    index += 1

                elif arg == '--install-value' and (index+1) < len( argv ):
                    self.app_install_value = sys.argv[index+1]
                    index += 1

                elif arg == '--merge':
                    self.enable_merge = True

                else:
                    raise AppPackageError( 'Unknown option %r' % (arg,) )

            else:
                all_positional_args.append( arg )

            index += 1

        if( len( all_positional_args ) < 1
        or all_positional_args[0] != 'build' ):
            raise AppPackageError( 'Expecting command name "build"' )

        self.main_program = all_positional_args[1]
        self.package_folder = pathlib.Path( all_positional_args[2] )

        if self.app_name is None:
            self.app_name = self.main_program[:-len('.py')]

        if self.app_install_key != '' and self.app_install_value == '':
            raise AppPackageError( 'require --install-value with --install-key' )

    def buildCommand( self, argv ):
        try:
            self.info( 'App Package Builder' )
            self.parseArgs( argv )

            if self.app_type == self.APP_TYPE_CLI:
                self.info( 'Building CLI App %s into package folder %s' % (self.app_name, self.package_folder) )

            elif self.app_type == self.APP_TYPE_GUI:
                self.info( 'Building GUI App %s into package folder %s' % (self.app_name, self.package_folder) )

            else:
                raise AppPackageError( 'Unknown app_type %r' % (self.app_type,) )


            #
            #   Look for modules using two methods
            #   1. Import the main program and see what ends up in sys.modules
            #   2. Use modulefinder to locate imports done at runtime
            #

            # 1. import main program
            main_module = self.main_program
            if main_module.endswith( '.py' ):
                main_module = main_module[:-len('.py')]

            importlib.import_module( main_module )

            # save the list of modules imported
            all_imported_module_names = list( sys.modules.keys() )

            # 2. what can modulefinder locate
            mf = modulefinder.ModuleFinder()
            mf.run_script( self.main_program )
            for name, mod in sorted( mf.modules.items() ):
                self.verbose( 'Module %s: %r' % (name, mod) )

            missing, maybe = mf.any_missing_maybe()
            all_missing = set( missing )
            all_missing_but_needed = all_missing - self.all_modules_allowed_to_be_missing

            for x in all_missing_but_needed:
                self.error( 'module %s is missing but is required' % (x,) )

            for x in maybe:
                self.warning( 'module %s maybe missing' % (x,) )

            if len(all_missing_but_needed) > 0:
                return 1

            # find the python DLL
            self.addWinPeFileDependenciesToPackage( pathlib.Path( sys.executable ) )

            for name, mod in sorted( mf.modules.items() ):
                self.processModule( name, mod )

            for name in sorted( all_imported_module_names ):
                if name in self.all_imported_modules_to_exclude:
                    continue

                self.processModule( name, sys.modules[ name ] )

            if not self.enable_merge:
                self.cleanAppPackage()

            self.createAppPackage()

            self.info( 'Completed sucessfully' )

            return 0

        except AppPackageError as e:
            self.error( str(e) )

    def processModule( self, name, module ):
        self.verbose( 'Checking module %s' % (name,) )
        if not hasattr( module, '__file__' ) or module.__file__ is None:
            self.verbose( '%s is builtin - ignoring' % (name,) )
            return

        filename = pathlib.Path( module.__file__ ).resolve()
        self.debug( 'module type %s filename %s' % (filename.suffix, filename) )

        # is this file part of the python installation?
        for path in [sys.prefix]+sys.path:
            try:
                path = pathlib.Path( path )
                path = path.resolve()

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
        all_dlls = win_app_package_win_pe_info.getPeImportDlls( self, filename )
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

        p = PackageFile(
                self.win_app_packager_folder / 'run_win_app.py',
                self.library_folder / 'run_win_app.py' )
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

        win_app_package_exe_config.configureAppExeBootStrap( 
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