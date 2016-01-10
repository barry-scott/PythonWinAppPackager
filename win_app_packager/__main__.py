#!/usr/bin/python3
import sys
import importlib

#
#   Do the minimum imports to get a clean list
#   of all module names to process
#
def main( argv ):
    main_program = None
    for arg in argv[1:]:
        if arg.startswith( '--' ):
            continue
        main_program = arg
        break

    if main_program is not None:
        # load the program to be packaged
        importlib.import_module( main_program )

        all_module_names = list( sys.modules.keys() )

        print( all_module_names )

    # add the folder containing the app packager files
    import os
    sys.path.insert( 0, os.path.dirname( argv[0] ) )

    import app_package_builder
    app_package = app_package_builder.AppPackage( argv )

    if main_program is not None:
        return app_package.build( all_module_names )

    else:
        return app_package.usage()

    return 0        

sys.exit( main( sys.argv ) )
