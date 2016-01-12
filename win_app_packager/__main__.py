#!/usr/bin/python3
import sys
import importlib

#
#   Do the minimum imports to get a clean list
#   of all module names to process
#
def main( argv ):
    all_args = []

    for arg in argv[1:]:
        if arg.startswith( '--' ):
            continue

        all_args.append( arg )

    if len(all_args) == 3 and all_args[0] == 'build':
        # load the program to be packaged
        main_module = all_args[1]
        if main_module.endswith( '.py' ):
            main_module = main_module[:-len('.py')]

        importlib.import_module( main_module )

        # save the list of modules imported
        all_module_names = list( sys.modules.keys() )

    import win_app_packager.win_app_package_builder
    win_app_package = win_app_packager.win_app_package_builder.AppPackage( argv )

    if len(all_args) > 1 and all_args[0] == 'build':
        return win_app_package.build( all_module_names )

    elif len(all_args) > 1 and all_args[0] == 'flags':
        import win_app_packager.win_app_package_exe_config
        return win_app_packager.win_app_package_exe_config.configureAppExePyFlags( all_args[1], all_args[2] )

    else:
        return win_app_package.usage()

    return 0        

sys.exit( main( sys.argv ) )
